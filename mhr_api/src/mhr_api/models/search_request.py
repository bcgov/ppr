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

from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.models import utils as model_utils
from mhr_api.models import search_utils
from mhr_api.models.db2 import search_utils as db2_search_utils

from .db import db


# Async search report status pending.
REPORT_STATUS_PENDING = 'PENDING'
CHARACTER_SET_UNSUPPORTED = 'The search name {} charcter set is not supported.\n'

LEGACY_TO_OWNER_STATUS = {
    '3': 'ACTIVE',
    '4': 'EXEMPT',
    '5': 'PREVIOUS'
}


class SearchRequest(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains search query (search step 1) information."""

    class SearchTypes(str, Enum):

        """Render an Enum of the distinct MHR search types."""
        OWNER_NAME = 'MI'
        ORGANIZATION_NAME = 'MO'
        SERIAL_NUM = 'MS'
        MANUFACTURED_HOME_NUM = 'MM'

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
            current_app.logger.debug('DB search_request.save completed')
        except Exception as db_exception:
            current_app.logger.error('DB search_request save exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    def update_search_selection(self, search_json):
        """Support UI search selection autosave: replace search response."""
        # Audit requirement: save original search summary results (before consumer selects registrations to include).
        # API consumers could remove results.
        self.updated_selection = search_json
        self.save()

    @classmethod
    def __build_search_result(cls, row):
        """Build a single search summary json from a DB row."""
        status = 'ACTIVE'
        mh_status = str(row[1])
        exempt = str(row[2])
        if mh_status != 'R':
            if exempt and exempt != 'N':
                status = 'EXEMPT'
            else:
                status = 'HISTORIC'
        # current_app.logger.info('Mapping timestamp')
        timestamp = row[3]
        # current_app.logger.info('Timestamp mapped')
        value: str = str(row[8])
        year = int(value) if value.isnumeric() else 0
        result_json = {
            'mhrNumber': str(row[0]),
            'status': status,
            'createDateTime': model_utils.format_ts(timestamp),
            'homeLocation': str(row[6]).strip(),
            'serialNumber': str(row[7]).strip(),
            'baseInformation': {
                'year': year,
                'make': str(row[9]).strip(),
                'model': ''
            },
            'mhId': int(row[10])
        }
        # current_app.logger.info(result_json)
        owner_type = str(row[4])
        owner_name = str(row[5]).strip()
        if owner_type != 'I':
            result_json['organizationName'] = owner_name
        else:
            result_json['ownerName'] = model_utils.get_ind_name_from_db2(owner_name)
        result_json['ownerStatus'] = LEGACY_TO_OWNER_STATUS[str(row[11])]
        return result_json

    @classmethod
    def __build_search_result_mhr(cls, row):
        """Build a single search summary json from a DB row for an mhr number search."""
        status = 'ACTIVE'
        mh_status = str(row[1])
        exempt = str(row[2])
        if mh_status != 'R':
            if exempt and exempt != 'N':
                status = 'EXEMPT'
            else:
                status = 'HISTORIC'
        # current_app.logger.info('Mapping timestamp')
        timestamp = row[3]
        # current_app.logger.info('Timestamp mapped')
        value: str = str(row[6])
        year = int(value) if value.isnumeric() else 0
        result_json = {
            'mhrNumber': str(row[0]),
            'status': status,
            'createDateTime': model_utils.format_ts(timestamp),
            'homeLocation': str(row[4]).strip(),
            'serialNumber': str(row[5]).strip(),
            'baseInformation': {
                'year': year,
                'make': str(row[7]).strip(),
                'model': ''
            },
            'mhId': int(row[8])
        }
        owner_info = str(row[9])
        owner_type = owner_info[0:1]
        owner_status = owner_info[1:2]
        owner_name = owner_info[2:].strip()
        if owner_type != 'I':
            result_json['organizationName'] = owner_name
        else:
            result_json['ownerName'] = model_utils.get_ind_name_from_db2(owner_name)
        result_json['ownerStatus'] = LEGACY_TO_OWNER_STATUS[owner_status]
        # current_app.logger.info(result_json)
        return result_json

    @classmethod
    def __build_search_result_serial(cls, row):
        """Build a single search summary json from a DB row for a serial number search."""
        status = 'ACTIVE'
        mh_status = str(row[1])
        exempt = str(row[2])
        if mh_status != 'R':
            if exempt and exempt != 'N':
                status = 'EXEMPT'
            else:
                status = 'HISTORIC'
        # current_app.logger.info('Mapping timestamp')
        timestamp = row[3]
        # current_app.logger.info('Timestamp mapped')
        value: str = str(row[7])
        year = int(value) if value.isnumeric() else 0
        result_json = {
            'mhrNumber': str(row[0]),
            'status': status,
            'createDateTime': model_utils.format_ts(timestamp),
            'homeLocation': str(row[5]).strip(),
            'serialNumber': str(row[6]).strip(),
            'baseInformation': {
                'year': year,
                'make': str(row[8]).strip(),
                'model': ''
            },
            'mhId': int(row[9])
        }
        # current_app.logger.info(result_json)
        owner_info = str(row[4])
        owner_type = owner_info[0:1]
        owner_status = owner_info[1:2]
        owner_name = owner_info[2:].strip()
        if owner_type != 'I':
            result_json['organizationName'] = owner_name
        else:
            result_json['ownerName'] = model_utils.get_ind_name_from_db2(owner_name)
        result_json['ownerStatus'] = LEGACY_TO_OWNER_STATUS[owner_status]
        serial_index = int(row[10])
        if serial_index == 2:
            result_json['serialNumber'] = str(row[11]).strip()
        elif serial_index == 3:
            result_json['serialNumber'] = str(row[12]).strip()
        elif serial_index == 4:
            result_json['serialNumber'] = str(row[13]).strip()
        return result_json

    def search_by_mhr_number_db2(self):
        """Execute a search by mhr number query."""
        result = db2_search_utils.search_by_mhr_number(current_app, db, self.request_json)
        row = None
        try:
            row = result.first()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB search_by_mhr_number exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

        result_json = []
        if row is not None:
            result_json.append(SearchRequest.__build_search_result_mhr(row))
            self.returned_results_size = 1
            self.total_results_size = 1
            self.search_response = result_json
        else:
            self.returned_results_size = 0
            self.total_results_size = 0

    def search_by_organization_name_db2(self):
        """Execute a search by organization name query."""
        result = db2_search_utils.search_by_organization_name(current_app, db, self.request_json)
        rows = None
        try:
            rows = result.fetchall()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB search_by_organization_name_db2 exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

        if rows is not None:
            results_json = []
            for row in rows:
                results_json.append(SearchRequest.__build_search_result(row))
            self.returned_results_size = len(results_json)
            self.total_results_size = self.returned_results_size
            self.search_response = results_json
        else:
            self.returned_results_size = 0
            self.total_results_size = 0

    def search_by_owner_name_db2(self):
        """Execute a search by owner name query."""
        result = db2_search_utils.search_by_owner_name(current_app, db, self.request_json)
        rows = None
        try:
            rows = result.fetchall()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB search_by_owner_name_db2 exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

        if rows is not None:
            results_json = []
            for row in rows:
                results_json.append(SearchRequest.__build_search_result(row))
            self.returned_results_size = len(results_json)
            self.total_results_size = self.returned_results_size
            self.search_response = results_json
        else:
            self.returned_results_size = 0
            self.total_results_size = 0

    def search_by_serial_number_db2(self):
        """Execute a search by serial number query."""
        result = db2_search_utils.search_by_serial_number(current_app, db, self.request_json)
        rows = None
        try:
            rows = result.fetchall()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB search_by_serial_number_db2 exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

        if rows is not None:
            results_json = []
            for row in rows:
                # result = SearchRequest.__build_search_result(row)
                # current_app.logger.debug(result)
                results_json.append(SearchRequest.__build_search_result_serial(row))
            self.returned_results_size = len(results_json)
            self.total_results_size = self.returned_results_size
            self.search_response = results_json
        else:
            self.returned_results_size = 0
            self.total_results_size = 0

    def search_by_serial_number(self):
        """Execute a search query for either a serial number search type."""
        #search_value = self.request_json['criteria']['value']
        self.returned_results_size = 0
        self.total_results_size = 0
        self.search_response = None

    def search_by_organization_name(self):
        """Execute a owner organization/business name search query."""
        # search_value = self.request_json['criteria']['organizationName']
        self.returned_results_size = 0
        self.total_results_size = 0
        self.search_response = None

    def search_by_owner_name(self):  # pylint: disable=too-many-locals; easier to follow
        """Execute a owner individual name search query."""
        #result = None
        #middle_name = None
        #last_name = self.request_json['criteria']['individualName']['last']
        #first_name = self.request_json['criteria']['individualName']['first']
        #if 'middle' in self.request_json['criteria']['individualName']:
        #    middle_name = self.request_json['criteria']['individualName']['middle']
        self.returned_results_size = 0
        self.total_results_size = 0
        self.search_response = None

    def search(self):
        """Execute a search with the previously set search type and criteria."""
        use_legacy_db: bool = current_app.config.get('USE_LEGACY_DB', True)
        if self.search_type == self.SearchTypes.MANUFACTURED_HOME_NUM:
            # Format before searching
            search_utils.format_mhr_number(self.request_json)

        if use_legacy_db:
            self.search_db2()
        else:
            raise DatabaseException('SearchRequest.search PosgreSQL not yet implemented.')

    def search_db2(self):
        """Execute a search with the previously set search type and criteria."""
        if self.search_type == self.SearchTypes.MANUFACTURED_HOME_NUM:
            self.search_by_mhr_number_db2()
        elif self.search_type == self.SearchTypes.SERIAL_NUM:
            self.search_by_serial_number_db2()
        elif self.search_type == self.SearchTypes.ORGANIZATION_NAME:
            self.search_by_organization_name_db2()
        else:
            self.search_by_owner_name_db2()
        self.save()

    @classmethod
    def find_by_id(cls, search_id: int):
        """Return the search query matching the id."""
        search = None
        if search_id:
            search = db.session.query(SearchRequest).filter(SearchRequest.id == search_id).one_or_none()
        return search

    @classmethod
    def find_all_by_account_id(cls, account_id: str = None, from_ui: bool = False): # pylint: disable=too-many-branches, too-many-locals
        """Return a search history summary list of searches executed by an account."""
        history_list = []
        if account_id:
            query = search_utils.ACCOUNT_SEARCH_HISTORY_DATE_QUERY.replace('?', account_id)
            if from_ui:
                query = search_utils.ACCOUNT_SEARCH_HISTORY_DATE_QUERY_NEW.replace('?', account_id)
            if search_utils.GET_HISTORY_DAYS_LIMIT <= 0:
                query = search_utils.ACCOUNT_SEARCH_HISTORY_QUERY.replace('?', account_id)
                if from_ui:
                    query = search_utils.ACCOUNT_SEARCH_HISTORY_QUERY_NEW.replace('?', account_id)
            rows = None
            try:
                result = db.session.execute(query)
                rows = result.fetchall()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB find_all_by_account_id exception: ' + str(db_exception))
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
                    history_list.append(search)
                    if from_ui:
                        # if api_result is null then the selections have not been finished
                        search['inProgress'] = not mapping['api_result'] and \
                            mapping['api_result'] != [] and search['totalResultsSize'] > 0
                        search['userId'] = str(mapping['user_id'])

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
    def validate_query(json_data):  # pylint: disable=too-many-branches
        """Perform any extra data validation here, either because it is too complicated for the schema.

        Or because it requires existing data.
        """
        error_msg = ''
        # validate search type - criteria combinations
        search_type: str = json_data['type']
        if len(search_type) != 2:
            search_type = model_utils.TO_DB_SEARCH_TYPE[search_type]
        if search_type == SearchRequest.SearchTypes.OWNER_NAME:
            if 'ownerName' not in json_data['criteria']:
                error_msg += f'Search criteria ownerName is required for search type {search_type}. '
            elif 'last' not in json_data['criteria']['ownerName']:
                error_msg += f'Search criteria ownerName last is required for search type {search_type}. '
            elif 'first' not in json_data['criteria']['ownerName']:
                error_msg += f'Search criteria ownerName first is required for search type {search_type}. '
        elif 'value' not in json_data['criteria']:
            error_msg += f'Search criteria value is required for search type {search_type}. '

        if error_msg != '':
            raise BusinessException(
                error=error_msg,
                status_code=HTTPStatus.BAD_REQUEST
            )
