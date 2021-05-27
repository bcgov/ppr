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

from flask import current_app

from ppr_api.exceptions import BusinessException
from ppr_api.models import utils as model_utils

from .db import db
from .financing_statement import FinancingStatement
from .search_utils import GET_DETAIL_DAYS_LIMIT


class SearchResult(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains search results detail (search step 2) information."""

    __tablename__ = 'search_results'

    search_id = db.Column('search_id', db.Integer, db.ForeignKey('search_clients.id'),
                          primary_key=True, nullable=False)
    search_select = db.Column('api_result', db.JSON, nullable=True)
    search_response = db.Column('registrations', db.JSON, nullable=False)
    score = db.Column('score', db.Integer, nullable=True)
    exact_match_count = db.Column('exact_match_count', db.Integer, nullable=True)
    similar_match_count = db.Column('similar_match_count', db.Integer, nullable=True)

    # parent keys

    # Relationships - Search
    search = db.relationship('SearchClient', foreign_keys=[search_id],
                             back_populates='search_result', cascade='all, delete', uselist=False)

    @property
    def json(self) -> dict:
        """Return the search query results as a json object."""
        result = None
        if self.search_response:
            result = self.search_response
            if self.search_select:
                result['selected'] = self.search_select
        return result

    def save(self):
        """Render a search results detail information to the local cache."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:  # noqa: B902; just logging
            current_app.logger.error('DB search_result save exception: ' + repr(db_exception))
            raise BusinessException(
                error='Database search_result save failed: ' + repr(db_exception),
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR
            )

    def update_selection(self, search_select):
        """Update the set of search details from the search query selection.

        Remove any original similar match financing statements that are not in the current search query selection.
        """
        # Nothing to do if search had no results.
        if self.search.total_results_size < 1:
            return

        # Build default summary information
        detail_response = {
            'searchDateTime': model_utils.format_ts(self.search.search_ts),
            'exactResultsSize': self.exact_match_count,
            'similarResultsSize': self.similar_match_count,
            'searchQuery': self.search.search_criteria,
            'details': []
        }
        if self.search.pay_invoice_id and self.search.pay_path:
            payment = {
                'invoiceId': str(self.search.pay_invoice_id),
                'receipt': self.search.pay_path
            }
            detail_response['payment'] = payment

        results = self.search_response
        new_results = []
        exact_count = 0
        similar_count = 0
        for result in results:
            # Always include exact matches.
            if result['matchType'] == model_utils.SEARCH_MATCH_EXACT:
                new_results.append(result)
                exact_count += 1
            else:
                found = False
                reg_num = result['financingStatement']['baseRegistrationNumber']
                for select in search_select:
                    if select['baseRegistrationNumber'] == reg_num and \
                       ('selected' not in select or select['selected']):
                        found = True
                        similar_count += 1
                if found:
                    new_results.append(result)

        # current_app.logger.debug('exact_count=' + str(exact_count) + ' similar_count=' + str(similar_count))
        self.search_select = search_select
        self.exact_match_count = exact_count
        self.similar_match_count = similar_count
        # current_app.logger.debug('saving updates')
        # Update summary information and save.
        detail_response['exactResultsSize'] = self.exact_match_count
        detail_response['similarResultsSize'] = self.similar_match_count
        detail_response['totalResultsSize'] = (self.exact_match_count + self.similar_match_count)
        detail_response['details'] = new_results
        self.search_response = detail_response
        self.save()

    @classmethod
    def find_by_search_id(cls, search_id: int, limit_by_date: bool = False):
        """Return the search detail record matching the search_id."""
        search_detail = None
        error_msg = ''
        if search_id and not limit_by_date:
            search_detail = db.session.query(SearchResult).filter(SearchResult.search_id == search_id).one_or_none()
        elif search_id and limit_by_date:
            min_allowed_date = model_utils.today_ts_offset(GET_DETAIL_DAYS_LIMIT, False)
            search_detail = db.session.query(SearchResult).filter(SearchResult.search_id == search_id).one_or_none()
            if search_detail and search_detail.search and \
                    search_detail.search.search_ts.timestamp() < min_allowed_date.timestamp():
                min_ts = model_utils.format_ts(min_allowed_date)
                error_msg = f'Search get details search ID {search_id} timestamp too old: must be after {min_ts}.'

        if error_msg != '':
            raise BusinessException(
                error=error_msg,
                status_code=HTTPStatus.BAD_REQUEST
            )

        return search_detail

    @staticmethod
    def create_from_search_query_no_results(search_query):
        """Create a search detail object from the inital search query which retured no results."""
        search_result = SearchResult(search_id=search_query.id, exact_match_count=0, similar_match_count=0)
        detail_response = {
            'searchDateTime': model_utils.format_ts(search_query.search_ts),
            'exactResultsSize': search_result.exact_match_count,
            'similarResultsSize': search_result.similar_match_count,
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
    def create_from_search_query(search_query, mark_added: bool = True):
        """Create a search detail object from the initial search query with no search selection criteria."""
        if search_query.total_results_size == 0:  # A search query with no results: build minimal details.
            return SearchResult.create_from_search_query_no_results(search_query)

        search_result = SearchResult(search_id=search_query.id, exact_match_count=0, similar_match_count=0)
        query_results = search_query.search_response
        detail_results = []
        for result in query_results:
            reg_num = result['baseRegistrationNumber']
            match_type = result['matchType']
            found = False
            if detail_results:  # Check for duplicates.
                for statement in detail_results:
                    if statement['financingStatement']['baseRegistrationNumber'] == reg_num:
                        found = True
            if not found:  # No duplicates.
                financing = FinancingStatement.find_by_registration_number(reg_num, staff=False, allow_historical=True)
                financing.mark_update_json = mark_added  # Added for PDF, indicate if party or collateral was added.
                # Special business rule: if search is by serial number, only include
                # serial_collateral records where the serial number is an exact match.
                # Do not include general_collateral records.
                financing_json = {
                    'matchType': match_type,
                    'financingStatement': financing.json
                }
                # Build an array of changes
                changes = []
                if financing.registration:
                    for reg in reversed(financing.registration):
                        if reg.registration_type_cl not in ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN'):
                            statement_json = reg.json
                            statement_json['statementType'] = \
                                model_utils.REG_CLASS_TO_STATEMENT_TYPE[reg.registration_type_cl]
                            changes.append(statement_json)
                if changes:
                    financing_json['financingStatement']['changes'] = changes
                detail_results.append(financing_json)
                if match_type == model_utils.SEARCH_MATCH_EXACT:
                    search_result.exact_match_count += 1
                else:
                    search_result.similar_match_count += 1

        search_result.search_response = detail_results
        return search_result

    @staticmethod
    def create_from_json(search_json, search_id: int):
        """Create a search detail object from dict/json specifying the search selection."""
        search = SearchResult()
        search.search_id = search_id
        search.search_select = search_json
        detail_results = []
        for result in search_json:
            reg_num = result['baseRegistrationNumber']
            financing = FinancingStatement.find_by_registration_number(reg_num, staff=False, allow_historical=True)
            # Special business rule: if search is by serial number, only include
            # serial_collateral records where the serial number is an exact match.
            # Do not include general_collateral records.
            financing_json = {
                'financingStatement': financing.json
            }
            # Build an array of changes
            changes = []
            if financing.registration:
                for reg in financing.registration:
                    if reg.registration_num != financing.registration_num:
                        statement_json = reg.json
                        statement_json['statementType'] = \
                            model_utils.REG_CLASS_TO_STATEMENT_TYPE[reg.registration_type_cl]
                        changes.append(statement_json)
            if changes:
                financing_json['financingStatement']['changes'] = changes
            detail_results.append(financing_json)
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

        search_result = SearchResult.find_by_search_id(search_id)
        if not search_result:
            error_msg = f'Search select results failed: invalid search ID {search_id}.'
        elif search_result.search_select:
            # Search detail request already submitted.
            error_msg = f'Search select results failed: results already provided for search ID {search_id}.'

        if error_msg != '':
            raise BusinessException(
                error=error_msg,
                status_code=HTTPStatus.BAD_REQUEST
            )

        return search_result
