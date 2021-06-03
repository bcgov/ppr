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

from ppr_api.exceptions import BusinessException
from ppr_api.models import utils as model_utils
from ppr_api.models import search_utils

from .db import db


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
    client_reference_id = db.Column('client_reference_id', db.String(20), nullable=True)
    total_results_size = db.Column('total_results_size', db.Integer, nullable=True)
    returned_results_size = db.Column('returned_results_size', db.Integer, nullable=True)

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
        if self.search_response:
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
            raise BusinessException(
                error='Database search_client save failed: ' + repr(db_exception),
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR
            )

    def update_search_selection(self, search_json):
        """Support UI search selection autosave: replace search response."""
        self.search_response = search_json
        self.save()

    def search_by_registration_number(self):
        """Execute a search by registration number query."""
        reg_num = self.request_json['criteria']['value']
        query = search_utils.REG_NUM_QUERY.replace('?', reg_num)
        result = db.session.execute(query)
        row = result.first()
        if row is not None:
            values = row.values()
            registration_type = str(values[0])
            # Remove state check for now - let the DB view take care of it.
            timestamp = values[1]
            result_json = [{
                'baseRegistrationNumber': str(values[2]),
                'matchType': str(values[3]),
                'createDateTime': model_utils.format_ts(timestamp),
                'registrationType': registration_type
            }]
            if reg_num != str(values[2]):
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

        query = query.replace('?', search_value)
        result = db.session.execute(query)
        rows = result.fetchall()
        if rows is not None:
            results_json = []
            for row in rows:
                values = row.values()
                registration_type = str(values[0])
                timestamp = values[1]
                collateral = {
                    'type': str(values[2]),
                    'serialNumber': str(values[3])
                }
                value = values[4]
                if value is not None:
                    collateral['year'] = int(value)
                value = values[5]
                if value is not None:
                    collateral['make'] = str(value)
                value = values[6]
                if value is not None:
                    collateral['model'] = str(value)
                match_type = str(values[8])
                if self.search_type == 'MH':
                    collateral['manufacturedHomeRegistrationNumber'] = str(values[12])
                result_json = {
                    'baseRegistrationNumber': str(values[7]),
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
        """Execute a search query debtor business_name search type."""
        search_value = self.request_json['criteria']['debtorName']['business']
        query = search_utils.BUSINESS_NAME_QUERY.replace('?', search_value.strip().upper())
        result = db.session.execute(query)
        rows = result.fetchall()
        if rows is not None:
            results_json = []
            for row in rows:
                values = row.values()
                registration_type = str(values[0])
                timestamp = values[1]
                debtor = {
                    'businessName': str(values[2]),
                    'partyId': int(values[7])
                }
                result_json = {
                    'baseRegistrationNumber': str(values[3]),
                    'matchType': str(values[4]),
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

    def search_by_individual_name(self):
        """Execute a search query debtor individual name search type."""
        last_name = self.request_json['criteria']['debtorName']['last']
        first_name = self.request_json['criteria']['debtorName']['first']
        query = search_utils.INDIVIDUAL_NAME_QUERY.replace('LNAME?', last_name.strip().upper())
        query = query.replace('FNAME?', first_name.strip().upper())
        result = db.session.execute(query)
        rows = result.fetchall()
        if rows is not None:
            results_json = []
            for row in rows:
                values = row.values()
                registration_type = str(values[0])
                timestamp = values[1]
                person = {
                    'last': str(values[2]),
                    'first': str(values[3])
                }
                middle = str(values[4])
                if middle:
                    person['middle'] = middle
                debtor = {
                    'personName': person,
                    'partyId': int(values[5])
                }
                result_json = {
                    'baseRegistrationNumber': str(values[6]),
                    'matchType': str(values[7]),
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
            if self.search_type == self.SearchTypes.BUSINESS_DEBTOR.value:
                search_value = self.request_json['criteria']['debtorName']['business']
                count_query = count_query.replace('?', search_value.strip().upper())
            elif self.search_type == self.SearchTypes.INDIVIDUAL_DEBTOR.value:
                last_name = self.request_json['criteria']['debtorName']['last']
                first_name = self.request_json['criteria']['debtorName']['first']
                count_query = count_query.replace('LNAME?', last_name.strip().upper())
                count_query = count_query.replace('FNAME?', first_name.strip().upper())
            else:
                count_query = count_query.replace('?', self.request_json['criteria']['value'])

            result = db.session.execute(count_query)
            row = result.first()
            values = row.values()
            self.total_results_size = int(values[0])

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

        if self.returned_results_size == search_utils.SEARCH_RESULTS_MAX_SIZE:
            # Actual result size exceeds limit: need to get total match count
            self.get_total_count()

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

            result = db.session.execute(query)
            rows = result.fetchall()
            if rows is not None:
                for row in rows:
                    values = row.values()
                    search = {
                        'searchId': str(values[0]),
                        'searchDateTime': model_utils.format_ts(values[1]),
                        'searchQuery': values[2],
                        'totalResultsSize': int(values[3]),
                        'returnedResultsSize': int(values[4])
                    }
                    exact_value = values[5]
                    if exact_value is not None:
                        search['exactResultsSize'] = int(exact_value)
                    similar_value = values[6]
                    if similar_value is not None:
                        search['selectedResultsSize'] = (int(similar_value) + int(exact_value))
                    else:
                        search['selectedResultsSize'] = int(exact_value)
                    history_list.append(search)

        # if not history_list:
        #   raise BusinessException(
        #       error=f'No search history found for Account ID {account_id}.',
        #       status_code=HTTPStatus.NOT_FOUND
        #    )

        return history_list

    @staticmethod
    def create_from_json(search_json,
                         account_id: str = None):
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
