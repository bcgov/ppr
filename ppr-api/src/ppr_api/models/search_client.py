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
from __future__ import annotations

from enum import Enum
from http import HTTPStatus
import json
import copy

#from sqlalchemy import event

from registry_schemas.example_data.ppr import SEARCH_QUERY_RESULT
from ppr_api.exceptions import BusinessException
from ppr_api.models import utils as model_utils

from .db import db

# Serial number search base where clause
SERIAL_SEARCH_BASE = \
    "SELECT r.registration_type_cd,r.registration_ts AS base_registration_ts," + \
            "sc.serial_type_cd,sc.serial_number,sc.year,sc.make,sc.model," + \
            "r.registration_number AS base_registration_num," + \
            "DECODE(serial_number, '?', 'EXACT', 'SIMILAR') AS match_type," + \
            "fs.expire_date,fs.state_type_cd,sc.serial_id AS vehicle_id  " + \
      "FROM registration r, financing_statement fs, serial_collateral sc " + \
     "WHERE r.financing_id = fs.financing_id " + \
       "AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN') " + \
       "AND r.base_reg_number IS NULL " + \
       "AND (fs.expire_date IS NULL OR fs.expire_date > ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30)) " + \
       "AND NOT EXISTS (SELECT r3.registration_id " + \
                         "FROM registration r3 " + \
                        "WHERE r3.financing_id = fs.financing_id " + \
                          "AND r3.registration_type_cl = 'DISCHARGE' " + \
                          "AND r3.registration_ts < ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30)) " + \
      "AND sc.financing_id = fs.financing_id " + \
      "AND sc.registration_id_end IS NULL "

# Equivalent logic as DB view search_by_reg_num_vw, but API determines the where clause.
REG_NUM_QUERY = \
    "SELECT r.registration_type_cd,r.registration_ts AS base_registration_ts," + \
            "r.registration_number AS base_registration_num," + \
            "'EXACT' AS match_type,fs.state_type_cd, fs.expire_date " + \
      "FROM registration r, financing_statement fs, registration r2 " + \
     "WHERE r2.financing_id = r.financing_id " + \
       "AND r.financing_id = fs.financing_id " + \
       "AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN') " + \
       "AND r.base_reg_number IS NULL " + \
       "AND (fs.expire_date IS NULL OR fs.expire_date > ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30)) " + \
       "AND NOT EXISTS (SELECT r3.registration_id " + \
                         "FROM registration r3 " + \
                        "WHERE r3.financing_id = fs.financing_id " + \
                          "AND r3.registration_type_cl = 'DISCHARGE' " + \
                          "AND r3.registration_ts < ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30)) " + \
      "AND r2.registration_number = '?'"

# Equivalent logic as DB view search_by_mhr_num_vw, but API determines the where clause.
MHR_NUM_QUERY = SERIAL_SEARCH_BASE + \
                 "AND sc.serial_type_cd = 'MH' " + \
                 "AND sc.mhr_number = '?' " + \
            "ORDER BY r.registration_ts ASC"

# Equivalent logic as DB view search_by_serial_num_vw, but API determines the where clause.
SERIAL_NUM_QUERY = SERIAL_SEARCH_BASE + \
                     "AND sc.serial_type_cd NOT IN ('AC', 'AF') " + \
                     "AND sc.srch_vin = search_key_pkg.vehicle('?') " + \
                "ORDER BY match_type, sc.serial_number"

# Equivalent logic as DB view search_by_aircraft_dot_vw, but API determines the where clause.
#                    "AND UPPER(REGEXP_REPLACE(sc.serial_number,'\s|-','')) = UPPER(REGEXP_REPLACE('?','\s|-','')) " + \
# pylint: disable=anomalous-backslash-in-string
AIRCRAFT_DOT_QUERY = SERIAL_SEARCH_BASE + \
                    "AND sc.serial_type_cd IN ('AC', 'AF') " + \
                    "AND sc.srch_vin = search_key_pkg.aircraft('?') " + \
               "ORDER BY match_type, sc.serial_number"


class SearchClient(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains search query (search step 1) information."""

    class SearchTypes(Enum):
        """Render an Enum of the search types."""
        AIRCRAFT_AIRFRAME_DOT = 'AC'
        BUSINESS_DEBTOR = 'BS'
        INDIVISUAL_DEBTOR = 'ID'
        REGISTRATION_NUM = 'RG'
        SERIAL_NUM = 'SS'
        MANUFACTURED_HOME_NUM = 'MH'

    __versioned__ = {}
    __tablename__ = 'search_client'


#    search_id = db.Column('search_id', db.Integer, primary_key=True, server_default=db.FetchedValue())
    search_id = db.Column('search_id', db.Integer, db.Sequence('search_id_seq'), primary_key=True)
    search_ts = db.Column('search_ts', db.DateTime, nullable=False)
    search_type_cd = db.Column('search_type_cd', db.String(2), nullable=False)
                                #, db.ForeignKey('search_type.search_type_cd'))
    search_criteria = db.Column('api_criteria', db.String(1000), nullable=False)
    search_response = db.Column('search_response', db.Text, nullable=True)
    account_id = db.Column('account_id', db.String(20), nullable=True)
    client_reference_id = db.Column('client_reference_id', db.String(20), nullable=True)
    total_results_size = db.Column('total_results_size', db.Integer, nullable=True)
    returned_results_size = db.Column('returned_results_size', db.Integer, nullable=True)

    pay_invoice_id = db.Column('pay_invoice_id', db.Integer, nullable=True)
    pay_path = db.Column('pay_path', db.String(256), nullable=True)

    # parent keys

    # Relationships - SearchResult
    search_result = db.relationship("SearchResult", back_populates="search", uselist=False)

    request_json = {}


    @property
    def json(self) -> dict:
        """Return the search query results as a json object."""
        result = {
            'searchId': str(self.search_id),
            'searchDateTime': model_utils.format_ts(self.search_ts),
            'totalResultsSize': self.total_results_size,
            'returnedResultsSize': self.returned_results_size,
            'maxResultsSize': 1000,
            'searchQuery': json.loads(self.search_criteria)
        }
        if self.search_response:
            result['results'] = json.loads(self.search_response)

        return result


    def save(self):
        """Render a search query to the local cache."""

        db.session.add(self)
        db.session.commit()


    def search_by_registration_number(self):
        """Execute a search by registration number query."""

        reg_num = self.request_json['criteria']['value']
        query = REG_NUM_QUERY.replace('?', reg_num)
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
            self.search_response = json.dumps(result_json)
        else:
            self.returned_results_size = 0
            self.total_results_size = 0


    def search_by_serial_type(self):
        """Execute a search query for either an aircraft DOT, MHR number, or
           serial number search type."""

        search_value = self.request_json['criteria']['value']
        query = SERIAL_NUM_QUERY
        if self.search_type_cd == 'MH':
            query = MHR_NUM_QUERY
        elif self.search_type_cd == 'AC':
            query = AIRCRAFT_DOT_QUERY

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
                if self.search_type_cd == 'MH':
                    collateral['manufacturedHomeRegistrationNumber'] = search_value
                    match_type = 'EXACT'
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
                self.search_response = json.dumps(results_json)
        else:
            self.returned_results_size = 0
            self.total_results_size = 0


    def search(self):
        """Execute a search by the previously set search type."""

        if self.search_type_cd == 'RG':
            self.search_by_registration_number()
        elif self.search_type_cd in ('SS', 'MH', 'AC'):
            self.search_by_serial_type()
        # temporary until debtor search implemented
        else:
            self.search_response = json.dumps(copy.deepcopy(SEARCH_QUERY_RESULT))
            self.returned_results_size = 1
            self.total_results_size = 1

        self.save()


    @classmethod
    def find_by_id(cls, search_id: int):
        """Return the search query matching the id."""
        search = None
        if search_id:
            search = cls.query.get(search_id)
        return search


    @staticmethod
    def create_from_json(search_json,
                         account_id: str = None):
        """Create a search object from dict/json."""

        new_search = SearchClient()
        new_search.request_json = search_json
        search_type = search_json['type']
        new_search.search_type_cd = model_utils.TO_DB_SEARCH_TYPE[search_type]
        new_search.search_criteria = json.dumps(search_json)
        new_search.search_ts = model_utils.now_ts()
        if account_id:
            new_search.account_id = account_id
        if 'clientReferenceId' in search_json:
            new_search.client_reference_id = search_json['clientReferenceId']

        return new_search


    @staticmethod
    def validate_query(json_data):
        """Perform any extra data validation here, either because it is too

        complicated for the schema, or because it requires existing data.
        """
        error_msg = ''

        # validate search type - criteria combinations
        search_type = json_data['type']
        if search_type not in ('INDIVIDUAL_DEBTOR', 'BUSINESS_DEBTOR'):
            if 'value' not in json_data['criteria']:
                error_msg = error_msg + f'Search criteria value is required for search type {search_type}. '
        else:
            if 'debtorName' not in json_data['criteria']:
                error_msg = error_msg + f'Search criteria debtorName is required for search type {search_type}. '
            elif search_type == 'INDIVIDUAL_DEBTOR' and 'last' not in json_data['criteria']['debtorName']:
                error_msg = error_msg + f'Search criteria debtorName last is required for search type {search_type}. '
            elif search_type == 'BUSINESS_DEBTOR' and 'businessName' not in json_data['criteria']['debtorName']:
                error_msg = error_msg + f'Search criteria debtorName businessName is required for search type {search_type}. '

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
