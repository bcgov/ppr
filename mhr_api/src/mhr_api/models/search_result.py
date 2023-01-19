# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This module holds model data and database operations for search results detail requests."""

from __future__ import annotations

from http import HTTPStatus
import json

from flask import current_app
from sqlalchemy.sql import text

from mhr_api.exceptions import BusinessException, DatabaseException, ResourceErrorCodes
from mhr_api.models import MhrRegistration, FinancingStatement, utils as model_utils, search_utils

from .db import db
# from .financing_statement import FinancingStatement
from .search_request import SearchRequest
from .search_utils import GET_HISTORY_DAYS_LIMIT


# PPR UI search detail report callbackURL parameter: skip notification if request originates from UI.
UI_CALLBACK_URL = 'PPR_UI'


class SearchResult(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains search results detail (search step 2) information."""

    __tablename__ = 'search_results'

    search_id = db.Column('search_id', db.Integer, db.ForeignKey('search_requests.id'),
                          primary_key=True, nullable=False)
    search_select = db.Column('api_result', db.JSON, nullable=True)
    search_response = db.Column('registrations', db.JSON, nullable=False)
    score = db.Column('score', db.Integer, nullable=True)
    exact_match_count = db.Column('exact_match_count', db.Integer, nullable=True)
    similar_match_count = db.Column('similar_match_count', db.Integer, nullable=True)
    # large async report requests capture callbackURL
    callback_url = db.Column('callback_url', db.String(1000), nullable=True)
    # large async report requests event listener updates when pdf generated and saved to document storage.
    doc_storage_url = db.Column('doc_storage_url', db.String(1000), nullable=True)
    # Need this for async reports (extracted from token).
    account_name = db.Column('account_name', db.String(1000), nullable=True)

    # parent keys

    # Relationships - Search
    search = db.relationship('SearchRequest', foreign_keys=[search_id],
                             back_populates='search_result', cascade='all, delete', uselist=False)

    @property
    def json(self) -> dict:
        """Return the search query results as a json object."""
        result = None
        if self.search_response:
            result = self.search_response
            # Distinguish a search with matches where none are selected from no results found.
            if not self.search_select and self.search.total_results_size > 0:
                result['selected'] = self.search_select
            elif self.search_select:
                result['selected'] = self.search_select
        return result

    def save(self):
        """Render a search results detail information to the local cache."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:  # noqa: B902; just logging
            current_app.logger.error('DB search_result save exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    def update_selection(self,  # pylint: disable=too-many-arguments
                         search_select,
                         account_name: str = None,
                         callback_url: str = None,
                         certified: bool = False,
                         staff: bool = False):
        """Update the set of search details from the search query selection.

        Remove any original matches that are not in the current search query selection.
        """
        # Build default summary information. Add certified for report setup.
        detail_response = {
            'searchDateTime': model_utils.format_ts(self.search.search_ts),
            'searchQuery': self.search.search_criteria,
            'certified': certified
        }
        client_ref: str = '' if not self.search.client_reference_id else self.search.client_reference_id
        detail_response['searchQuery']['clientReferenceId'] = client_ref
        if self.search.pay_invoice_id and self.search.pay_path:
            payment = {
                'invoiceId': str(self.search.pay_invoice_id),
                'receipt': self.search.pay_path
            }
            detail_response['payment'] = payment
        # Nothing else to do if search had no results.
        if self.search.total_results_size < 1:
            detail_response['totalResultsSize'] = self.search.total_results_size
            self.search_response = detail_response
            self.save()
            return

        self.set_search_selection(search_select)
        detail_response['details'] = self.build_details(staff)
        # current_app.logger.debug('saving updates')
        # Update summary information and save.
        select_count = len(detail_response['details'])
        self.exact_match_count = select_count
        detail_response['totalResultsSize'] = select_count
        self.search_response = detail_response
        if account_name:
            self.account_name = account_name
        if callback_url:
            self.callback_url = callback_url
        else:
            results_length = len(json.dumps(detail_response['details']))
            current_app.logger.debug(f'Search id= {self.search_id} results size={results_length}.')
            if results_length > current_app.config.get('MAX_SIZE_SEARCH_RT'):
                current_app.logger.info(f'Search id={self.search_id} size exceeds RT max, setting up async report.')
                self.callback_url = current_app.config.get('UI_SEARCH_CALLBACK_URL')
        self.save()

    def build_details(self, staff: bool = False):
        """Generate the search selection details."""
        new_results = []
        use_legacy_db: bool = current_app.config.get('USE_LEGACY_DB', True)
        for select in self.search_select:
            if 'selected' not in select or select['selected']:
                mhr_num = select['mhrNumber']
                found = False
                if new_results:  # Check for duplicates.
                    for match in new_results:
                        if match['mhrNumber'] == mhr_num:
                            found = True
                if not found:  # No duplicates.
                    # Load registration details here.
                    mh_id = select.get('mhId', None)
                    current_app.logger.debug(f'find_by_id for mhr num {mhr_num} start id={mh_id}')
                    record = MhrRegistration.find_by_id(mh_id, use_legacy_db, True)
                    current_app.logger.debug(f'find_by_id for mhr num {mhr_num} end')
                    record.staff = staff
                    result = record.registration_json
                    if select.get('includeLienInfo', False):
                        current_app.logger.info(f'Searching PPR for MHR num {mhr_num}.')
                        ppr_registrations = SearchResult.search_ppr_by_mhr_number(mhr_num)
                        result['pprRegistrations'] = ppr_registrations
                    new_results.append(result)
        return new_results

    def set_search_selection(self, update_select):
        """Sort the selection for the report TOC."""
        original_results = self.search.search_response
        final_selection = []
        for result in original_results:
            for match in update_select:
                if result['mhrNumber'] == match['mhrNumber']:
                    if match.get('includeLienInfo', False):
                        result['includeLienInfo'] = match.get('includeLienInfo')
                    final_selection.append(result)
                    break

        # Now sort by search type.
        if self.search.search_type == SearchRequest.SearchTypes.OWNER_NAME:
            self.search_select = SearchResult.__sort_owner_ind(final_selection)
        if self.search.search_type == SearchRequest.SearchTypes.ORGANIZATION_NAME:
            self.search_select = SearchResult.__sort_owner_org(final_selection)
        if self.search.search_type == SearchRequest.SearchTypes.SERIAL_NUM:
            self.search_select = SearchResult.__sort_serial_num(final_selection)
        else:
            self.search_select = final_selection

    @classmethod
    def __sort_serial_num(cls, update_select):
        """Sort selected serial numbers."""
        update_select.sort(key=SearchResult.__select_sort_year)
        update_select.sort(key=SearchResult.__select_sort_serial_num)
        update_select.sort(key=SearchResult.__select_sort_mhr_num, reverse=True)
        return update_select

    @classmethod
    def __sort_owner_ind(cls, update_select):
        """Sort selected individual owner names."""
        update_select.sort(key=SearchResult.__select_sort_year)
        update_select.sort(key=SearchResult.__select_sort_owner_middle_name)
        update_select.sort(key=SearchResult.__select_sort_owner_first_name)
        update_select.sort(key=SearchResult.__select_sort_owner_last_name)
        update_select.sort(key=SearchResult.__select_sort_mhr_num, reverse=True)
        return update_select

    @classmethod
    def __sort_owner_org(cls, update_select):
        """Sort selected organization/business owner names."""
        update_select.sort(key=SearchResult.__select_sort_year)
        update_select.sort(key=SearchResult.__select_sort_owner_org_name)
        update_select.sort(key=SearchResult.__select_sort_mhr_num, reverse=True)
        return update_select

    @classmethod
    def __select_sort_mhr_num(cls, item):
        """Sort the match list by MHR number."""
        return item['mhrNumber']

    @classmethod
    def __select_sort_owner_middle_name(cls, item):
        """Sort the match list by individual owner middle name."""
        return item['ownerName'].get('middle', '')

    @classmethod
    def __select_sort_owner_first_name(cls, item):
        """Sort the match list by individual owner first name."""
        return item['ownerName']['first']

    @classmethod
    def __select_sort_owner_last_name(cls, item):
        """Sort the match list by individual owner last name."""
        return item['ownerName']['last']

    @classmethod
    def __select_sort_owner_org_name(cls, item):
        """Sort the match list by owner organization/business name."""
        return item['organizationName']

    @classmethod
    def __select_sort_year(cls, item):
        """Sort the match list by MH year."""
        return item['baseInformation'].get('year', 0)

    @classmethod
    def __select_sort_serial_num(cls, item):
        """Sort the match list by serial number."""
        return item['serialNumber']

    @classmethod
    def find_by_search_id(cls, search_id: int, limit_by_date: bool = False):
        """Return the search detail record matching the search_id."""
        search_detail = None
        error_msg = ''
        if search_id and not limit_by_date:
            try:
                search_detail = db.session.query(SearchResult).filter(SearchResult.search_id == search_id).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB find_by_search_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        elif search_id and limit_by_date:
            min_allowed_date = model_utils.today_ts_offset(GET_HISTORY_DAYS_LIMIT, False)
            try:
                search_detail = db.session.query(SearchResult).filter(SearchResult.search_id == search_id).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB find_by_search_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
            if search_detail and search_detail.search and \
                    search_detail.search.search_ts.timestamp() < min_allowed_date.timestamp():
                min_ts = model_utils.format_ts(min_allowed_date)
                error_msg = model_utils.ERR_SEARCH_TOO_OLD.format(code=ResourceErrorCodes.TOO_OLD_ERR,
                                                                  search_id=search_id,
                                                                  min_ts=min_ts)

        if error_msg != '':
            raise BusinessException(error=error_msg, status_code=HTTPStatus.BAD_REQUEST)

        return search_detail

    def is_ui_callback(self):
        """Return whether an async search report request originated from the UI."""
        return self.callback_url and self.callback_url == UI_CALLBACK_URL

    @staticmethod
    def create_from_search_query_no_results(search_query):
        """Create a search detail object from the inital search query which retured no results."""
        search_result = SearchResult(search_id=search_query.id, exact_match_count=0, similar_match_count=0)
        detail_response = {
            'searchDateTime': model_utils.format_ts(search_query.search_ts),
            'totalResultsSize': 0,
            'searchQuery': search_query.search_criteria
        }
        if search_query.pay_invoice_id and search_query.pay_path:
            payment = {
                'invoiceId': str(search_query.pay_invoice_id),
                'receipt': search_query.pay_path
            }
            detail_response['payment'] = payment
        search_result.search_response = detail_response
        return search_result

    @staticmethod
    def create_from_search_query(search_query):
        """Create a search detail object from the initial search query with no search selection criteria."""
        if search_query.total_results_size == 0:  # A search query with no results: build minimal details.
            return SearchResult.create_from_search_query_no_results(search_query)

        search_result = SearchResult(search_id=search_query.id, exact_match_count=0, similar_match_count=0)
        # query_results = search_query.search_response
        detail_results = []
        search_result.search_response = detail_results
        return search_result

    @staticmethod
    def create_from_json(search_json, search_id: int):
        """Create a search detail object from dict/json specifying the search selection."""
        search = SearchResult()
        search.search_id = search_id
        search.search_select = search_json
        detail_results = []
        search.search_response = detail_results
        return search

    @staticmethod
    def validate_search_select(select_json, search_id: int):  # pylint: disable=unused-argument
        """Perform any extra data validation here.

        Either because it is too complicated for the schema, or because it requires existing data.
        Also fetch the existing search_detail record and verify a previous search detail request on
        the same search ID has not been submitted.
        """
        error_msg = ''
        status_code = HTTPStatus.BAD_REQUEST
        search_result = SearchResult.find_by_search_id(search_id)
        if not search_result:
            error_msg = model_utils.ERR_SEARCH_NOT_FOUND.format(code=ResourceErrorCodes.NOT_FOUND_ERR,
                                                                search_id=search_id)
            status_code = HTTPStatus.NOT_FOUND
        elif search_result.search_select:
            # Search detail request already submitted.
            error_msg = model_utils.ERR_SEARCH_COMPLETE.format(code=ResourceErrorCodes.DUPLICATE_ERR,
                                                               search_id=search_id)

        if error_msg != '':
            raise BusinessException(error=error_msg, status_code=status_code)

        return search_result

    @staticmethod
    def search_ppr_by_mhr_number(mhr_number):
        """Execute a PPR MHR Number search query."""
        current_app.logger.info(f'Search_ppr_by_mhr_number search value={mhr_number}.')
        rows = None
        try:
            query = text(search_utils.PPR_MHR_NUMBER_QUERY)
            result = db.session.execute(query, {'query_value': mhr_number})
            rows = result.fetchall()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('Search_ppr_by_mhr_number query exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

        results_json = []
        if rows is None:
            return results_json
        try:
            for row in rows:
                financing_id: int = int(row[0])
                current_app.logger.info(f'Found financing id={financing_id}.')
                financing: FinancingStatement = FinancingStatement.find_by_id(financing_id)
                financing.mark_update_json = True  # Added for PDF, indicate if party or collateral was added.
                # Set to true to include change history.
                financing.include_changes_json = True
                financing_json = {
                    'matchType': 'EXACT',
                    'financingStatement': financing.json
                }
                results_json.append(financing_json)
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('Search_ppr_by_mhr_number build results error: ' + str(db_exception))
            raise DatabaseException(db_exception)

        current_app.logger.info('Search_ppr_by_mhr_number results length=' + str(len(results_json)))
        return results_json
