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
"""This module holds model data and database operations for search queries."""
# flake8: noqa Q000,E122,E131
# Disable Q000: Allow query strings to be in double quotation marks that contain single quotation marks.
# Disable E122: allow query strings to be more human readable.
# Disable E131: allow query strings to be more human readable.
from __future__ import annotations

from enum import Enum
from http import HTTPStatus

from flask import current_app

from ppr_api.exceptions import BusinessException, DatabaseException
from ppr_api.models import utils as model_utils
from ppr_api.models import search_utils

from .db import db


# Async search report status pending.
REPORT_STATUS_PENDING = 'PENDING'


class SearchRequest(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains search query (search step 1) information."""

    class SearchTypes(Enum):

        """Render an Enum of the search types."""
        AIRCRAFT_AIRFRAME_DOT = 'AC'
        BUSINESS_DEBTOR = 'BS'
        INDIVIDUAL_DEBTOR = 'IS'
        REGISTRATION_NUM = 'RG'
        SERIAL_NUM = 'SS'
        MANUFACTURED_HOME_NUM = 'MH'

    __tablename__ = 'search_requests'


    id = db.Column('id', db.Integer, db.Sequence('search_id_seq'), primary_key=True)
    search_ts = db.Column('search_ts', db.DateTime, nullable=False, index=True)
    search_type = db.Column('search_type', db.String(2),
                            db.ForeignKey('search_types.search_type'), nullable=False)
    search_criteria = db.Column('api_criteria', db.JSON, nullable=False)
    search_response = db.Column('search_response', db.JSON, nullable=True)
    account_id = db.Column('account_id', db.String(20), nullable=True, index=True)
    client_reference_id = db.Column('client_reference_id', db.String(50), nullable=True)
    total_results_size = db.Column('total_results_size', db.Integer, nullable=True)
    returned_results_size = db.Column('returned_results_size', db.Integer, nullable=True)
    user_id = db.Column('user_id', db.String(1000), nullable=True)
    updated_selection = db.Column('updated_selection', db.JSON, nullable=True)

    pay_invoice_id = db.Column('pay_invoice_id', db.Integer, nullable=True)
    pay_path = db.Column('pay_path', db.String(256), nullable=True)

    # parent keys

    # Relationships - SearchResult
    search_result = db.relationship('SearchResult', back_populates='search', uselist=False)
    # Relationships - SearchType
    search_request_type = db.relationship('SearchType', foreign_keys=[search_type],
                                          back_populates='search_request', cascade='all, delete', uselist=False)

    request_json = {}

    @property
    def json(self) -> dict:
        """Return the search query results as a json object."""
        result = {
            'searchId': str(self.id),
            'searchDateTime': model_utils.format_ts(self.search_ts),
            'totalResultsSize': self.total_results_size,
            'returnedResultsSize': self.returned_results_size,
            'maxResultsSize': search_utils.SEARCH_RESULTS_MAX_SIZE,
            'searchQuery': self.search_criteria
        }
        if self.updated_selection:
            result['results'] = self.updated_selection
        elif self.search_response:
            result['results'] = self.search_response

        if self.pay_invoice_id and self.pay_path:
            payment = {
                'invoiceId': str(self.pay_invoice_id),
                'receipt': self.pay_path
            }
            result['payment'] = payment

        return result

    def save(self):
        """Render a search query to the local cache."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:
            current_app.logger.error('DB search_client save exception: ' + repr(db_exception))
            raise DatabaseException(db_exception)

    def update_search_selection(self, search_json):
        """Support UI search selection autosave: replace search response."""
        # Audit requirement: save original search summary results (before consumer selects registrations to include).
        # API consumers could remove results.
        self.updated_selection = search_json
        self.save()

    def search_by_registration_number(self):
        """Execute a search by registration number query."""
        reg_num = self.request_json['criteria']['value']
        row = None
        try:
            result = db.session.execute(search_utils.REG_NUM_QUERY, {'query_value': reg_num.strip().upper()})
            row = result.first()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB search_by_registration_number exception: ' + repr(db_exception))
            raise DatabaseException(db_exception)

        if row is not None:
            mapping = row._mapping  # pylint: disable=protected-access; follows documentation
            registration_type = str(mapping['registration_type'])
            # Remove state check for now - let the DB view take care of it.
            timestamp = mapping['base_registration_ts']
            result_json = [{
                'baseRegistrationNumber': str(mapping['base_registration_num']),
                'matchType': str(mapping['match_type']),
                'createDateTime': model_utils.format_ts(timestamp),
                'registrationType': registration_type
            }]
            if reg_num != str(mapping['base_registration_num']):
                result_json[0]['registrationNumber'] = reg_num

            self.returned_results_size = 1
            self.total_results_size = 1
            self.search_response = result_json
        else:
            self.returned_results_size = 0
            self.total_results_size = 0

    def search_by_serial_type(self):
        """Execute a search query for either an aircraft DOT, MHR number, or serial number search type."""
        search_value = self.request_json['criteria']['value']
        query = search_utils.SERIAL_NUM_QUERY
        if self.search_type == 'MH':
            query = search_utils.MHR_NUM_QUERY
            query = query.replace('CASE WHEN serial_number', 'CASE WHEN mhr_number')
        elif self.search_type == 'AC':
            query = search_utils.AIRCRAFT_DOT_QUERY
        rows = None
        try:
            result = db.session.execute(query, {'query_value': search_value.strip().upper()})
            rows = result.fetchall()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB search_by_serial_type exception: ' + repr(db_exception))
            raise DatabaseException(db_exception)
        if rows is not None:
            results_json = []
            for row in rows:
                mapping = row._mapping  # pylint: disable=protected-access; follows documentation
                registration_type = str(mapping['registration_type'])
                timestamp = mapping['base_registration_ts']
                collateral = {
                    'type': str(mapping['serial_type']),
                    'serialNumber': str(mapping['serial_number'])
                }
                value = mapping['year']
                if value is not None:
                    collateral['year'] = int(value)
                value = mapping['make']
                if value is not None:
                    collateral['make'] = str(value)
                value = mapping['model']
                if value is not None:
                    collateral['model'] = str(value)
                match_type = str(mapping['match_type'])
                if self.search_type == 'MH':
                    collateral['manufacturedHomeRegistrationNumber'] = str(mapping['mhr_number'])
                result_json = {
                    'baseRegistrationNumber': str(mapping['base_registration_num']),
                    'matchType': match_type,
                    'createDateTime': model_utils.format_ts(timestamp),
                    'registrationType': registration_type,
                    'vehicleCollateral': collateral
                }
                results_json.append(result_json)

            self.returned_results_size = len(results_json)
            self.total_results_size = self.returned_results_size
            if self.returned_results_size > 0:
                self.search_response = results_json
        else:
            self.returned_results_size = 0
            self.total_results_size = 0

    def search_by_business_name(self):
        """Execute a debtor business name search query."""
        search_value = self.request_json['criteria']['debtorName']['business']
        rows = None
        try:
            result = db.session.execute(search_utils.BUSINESS_NAME_QUERY,
                                        {'query_bus_name': search_value.strip().upper(),
                                         'query_bus_quotient':
                                         current_app.config.get('SIMILARITY_QUOTIENT_BUSINESS_NAME')})
            rows = result.fetchall()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB search_by_business_name exception: ' + repr(db_exception))
            raise DatabaseException(db_exception)
        if rows is not None:
            results_json = []
            for row in rows:
                mapping = row._mapping  # pylint: disable=protected-access; follows documentation
                registration_type = str(mapping['registration_type'])
                timestamp = mapping['base_registration_ts']
                debtor = {
                    'businessName': str(mapping['business_name']),
                    'partyId': int(mapping['id'])
                }
                result_json = {
                    'baseRegistrationNumber': str(mapping['base_registration_num']),
                    'matchType': str(mapping['match_type']),
                    'createDateTime': model_utils.format_ts(timestamp),
                    'registrationType': registration_type,
                    'debtor': debtor
                }
                results_json.append(result_json)

            self.returned_results_size = len(results_json)
            self.total_results_size = self.returned_results_size
            if self.returned_results_size > 0:
                self.search_response = results_json
        else:
            self.returned_results_size = 0
            self.total_results_size = 0

    def search_by_individual_name(self):  # pylint: disable=too-many-locals; easier to follow
        """Execute a debtor individual name search query."""
        result = None
        middle_name = None
        last_name = self.request_json['criteria']['debtorName']['last']
        first_name = self.request_json['criteria']['debtorName']['first']
        quotient_first = current_app.config.get('SIMILARITY_QUOTIENT_FIRST_NAME')
        quotient_last = current_app.config.get('SIMILARITY_QUOTIENT_LAST_NAME')
        quotient_default = current_app.config.get('SIMILARITY_QUOTIENT_DEFAULT')
        if 'second' in self.request_json['criteria']['debtorName']:
            middle_name = self.request_json['criteria']['debtorName']['second']
        rows = None
        try:
            if middle_name is not None and middle_name.strip() != '' and middle_name.strip().upper() != 'NONE':
                result = db.session.execute(search_utils.INDIVIDUAL_NAME_MIDDLE_QUERY,
                                            {'query_last': last_name.strip().upper(),
                                             'query_first': first_name.strip().upper(),
                                             'query_middle': middle_name.strip().upper(),
                                             'query_last_quotient': quotient_last,
                                             'query_first_quotient': quotient_first,
                                             'query_default_quotient': quotient_default})
            else:
                result = db.session.execute(search_utils.INDIVIDUAL_NAME_QUERY,
                                            {'query_last': last_name.strip().upper(),
                                             'query_first': first_name.strip().upper(),
                                             'query_last_quotient': quotient_last,
                                             'query_first_quotient': quotient_first,
                                             'query_default_quotient': quotient_default})
            rows = result.fetchall()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB search_by_individual_name exception: ' + repr(db_exception))
            raise DatabaseException(db_exception)
        if rows is not None:
            results_json = []
            for row in rows:
                mapping = row._mapping  # pylint: disable=protected-access; follows documentation
                registration_type = str(mapping['registration_type'])
                timestamp = mapping['base_registration_ts']
                person = {
                    'last': str(mapping['last_name']),
                    'first': str(mapping['first_name'])
                }
                middle = str(mapping['middle_initial'])
                if middle and middle != '' and middle.upper() != 'NONE':
                    person['middle'] = middle
                debtor = {
                    'personName': person,
                    'partyId': int(mapping['id'])
                }
                if mapping['birth_date']:
                    debtor['birthDate'] = model_utils.format_ts(mapping['birth_date'])
                result_json = {
                    'baseRegistrationNumber': str(mapping['base_registration_num']),
                    'matchType': str(mapping['match_type']),
                    'createDateTime': model_utils.format_ts(timestamp),
                    'registrationType': registration_type,
                    'debtor': debtor
                }
                results_json.append(result_json)

            self.returned_results_size = len(results_json)
            self.total_results_size = self.returned_results_size
            if self.returned_results_size > 0:
                self.search_response = results_json
        else:
            self.returned_results_size = 0
            self.total_results_size = 0

    def get_total_count(self):
        """Execute a search to get the total match count for the search criteria. Only call if limit reached."""
        count_query = search_utils.COUNT_QUERY_FROM_SEARCH_TYPE[self.search_type]
        if count_query:
            result = None
            if self.search_type == self.SearchTypes.BUSINESS_DEBTOR.value:
                search_value = self.request_json['criteria']['debtorName']['business']
                quotient = current_app.config.get('SIMILARITY_QUOTIENT_BUSINESS_NAME')
                result = db.session.execute(count_query,
                                            {'query_bus_name': search_value, 'query_bus_quotient': quotient})
            elif self.search_type == self.SearchTypes.INDIVIDUAL_DEBTOR.value:
                last_name = self.request_json['criteria']['debtorName']['last']
                first_name = self.request_json['criteria']['debtorName']['first']
                quotient_first = current_app.config.get('SIMILARITY_QUOTIENT_FIRST_NAME')
                quotient_last = current_app.config.get('SIMILARITY_QUOTIENT_LAST_NAME')
                quotient_default = current_app.config.get('SIMILARITY_QUOTIENT_DEFAULT')
                result = db.session.execute(count_query, {'query_last': last_name.strip().upper(),
                                                          'query_first': first_name.strip().upper(),
                                                          'query_first_quotient': quotient_first,
                                                          'query_last_quotient': quotient_last,
                                                          'query_default_quotient': quotient_default})
            else:
                search_value = self.request_json['criteria']['value']
                result = db.session.execute(count_query, {'query_value': search_value})

            if result:
                row = result.first()
                self.total_results_size = int(row._mapping['query_count'])  # pylint: disable=protected-access

    def search(self):
        """Execute a search with the previously set search type and criteria."""
        if self.search_type == self.SearchTypes.REGISTRATION_NUM.value:
            self.search_by_registration_number()
        elif self.search_type in (self.SearchTypes.SERIAL_NUM.value,
                                  self.SearchTypes.MANUFACTURED_HOME_NUM.value,
                                  self.SearchTypes.AIRCRAFT_AIRFRAME_DOT.value):
            self.search_by_serial_type()
        elif self.search_type == self.SearchTypes.BUSINESS_DEBTOR.value:
            self.search_by_business_name()
        else:
            self.search_by_individual_name()
        self.save()

    @classmethod
    def find_by_id(cls, search_id: int):
        """Return the search query matching the id."""
        search = None
        if search_id:
            search = db.session.query(SearchRequest).filter(SearchRequest.id == search_id).one_or_none()
        return search

    @classmethod
    def find_all_by_account_id(cls, account_id: str = None):
        """Return a search history summary list of searches executed by an account."""
        history_list = []
        if account_id:
            query = search_utils.ACCOUNT_SEARCH_HISTORY_DATE_QUERY.replace('?', account_id)
            if search_utils.GET_HISTORY_DAYS_LIMIT <= 0:
                query = search_utils.ACCOUNT_SEARCH_HISTORY_QUERY.replace('?', account_id)
            rows = None
            try:
                result = db.session.execute(query)
                rows = result.fetchall()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB find_all_by_account_id exception: ' + repr(db_exception))
                raise DatabaseException(db_exception)
            if rows is not None:
                for row in rows:
                    mapping = row._mapping  # pylint: disable=protected-access; follows documentation
                    search_id = str(mapping['id'])
                    # Set to pending if async report is not yet available.
                    callback_url = str(mapping['callback_url'])
                    doc_storage_url = str(mapping['doc_storage_url'])
                    if callback_url is not None and callback_url.lower() != 'none' and \
                            (doc_storage_url is None or doc_storage_url.lower() == 'none'):
                        search_id = REPORT_STATUS_PENDING
                    search = {
                        'searchId': search_id,
                        'searchDateTime': model_utils.format_ts(mapping['search_ts']),
                        'searchQuery': mapping['api_criteria'],
                        'totalResultsSize': int(mapping['total_results_size']),
                        'returnedResultsSize': int(mapping['returned_results_size']),
                        'username': str(mapping['username'])
                    }
                    exact_value = mapping['exact_match_count']
                    if exact_value is not None:
                        search['exactResultsSize'] = int(exact_value)
                    else:
                        search['exactResultsSize'] = 0
                    selected_value = mapping['selected_match_count']
                    if selected_value is not None:
                        search['selectedResultsSize'] = int(selected_value)
                    else:
                        search['selectedResultsSize'] = 0
                    history_list.append(search)

        return history_list

    @staticmethod
    def create_from_json(search_json,
                         account_id: str = None,
                         user_id: str = None):
        """Create a search object from dict/json."""
        new_search = SearchRequest()
        new_search.request_json = search_json
        search_type = search_json['type']
        new_search.search_type = model_utils.TO_DB_SEARCH_TYPE[search_type]
        new_search.search_criteria = search_json
        new_search.search_ts = model_utils.now_ts()
        if account_id:
            new_search.account_id = account_id
        if 'clientReferenceId' in search_json and search_json['clientReferenceId'].strip() != '':
            new_search.client_reference_id = search_json['clientReferenceId']
        new_search.user_id = user_id
        return new_search

    @staticmethod
    def validate_query(json_data):
        """Perform any extra data validation here, either because it is too complicated for the schema.

        Or because it requires existing data.
        """
        error_msg = ''

        # validate search type - criteria combinations
        search_type = json_data['type']
        if search_type not in ('INDIVIDUAL_DEBTOR', 'BUSINESS_DEBTOR'):
            if 'value' not in json_data['criteria']:
                error_msg += f'Search criteria value is required for search type {search_type}. '
        else:
            if 'debtorName' not in json_data['criteria']:
                error_msg += f'Search criteria debtorName is required for search type {search_type}. '
            elif search_type == 'INDIVIDUAL_DEBTOR' and 'last' not in json_data['criteria']['debtorName']:
                error_msg += f'Search criteria debtorName last is required for search type {search_type}. '
            elif search_type == 'BUSINESS_DEBTOR' and 'business' not in json_data['criteria']['debtorName']:
                error_msg += f'Search criteria debtorName businessName is required for search type {search_type}. '

        # Verify the start and end dates.
        if 'startDateTime' in json_data or 'startDateTime' in json_data:
            now = model_utils.now_ts()
            ts_start = None
            ts_end = None
            if 'startDateTime' in json_data:
                ts_start = model_utils.ts_from_iso_format(json_data['startDateTime'])
                if ts_start > now:
                    error_msg = error_msg + 'Search startDateTime invalid: it cannot be in the future. '
            if 'endDateTime' in json_data:
                ts_end = model_utils.ts_from_iso_format(json_data['endDateTime'])
                if ts_end > now:
                    error_msg = error_msg + 'Search endDateTime invalid: it cannot be in the future. '

            if ts_start and ts_end and ts_start > ts_end:
                error_msg = error_msg + 'Search date range invalid: startDateTime cannot be after endDateTime. '

        if error_msg != '':
            raise BusinessException(
                error=error_msg,
                status_code=HTTPStatus.BAD_REQUEST
            )
