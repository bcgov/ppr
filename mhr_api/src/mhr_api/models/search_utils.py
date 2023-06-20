# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Model helper utilities for processing search query and search detail requests.

Search constants and helper functions.
"""
# flake8: noqa Q000,E122,E131
# Disable Q000: Allow query strings to be in double quotation marks that contain single quotation marks.
# Disable E122: allow query strings to be more human readable.
# Disable E131: allow query strings to be more human readable.
import re
from flask import current_app
from sqlalchemy.sql import text

from mhr_api.exceptions import DatabaseException
from mhr_api.models import utils as model_utils
from mhr_api.models.type_tables import MhrOwnerStatusTypes

from .db import db


GET_DETAIL_DAYS_LIMIT = 7 # Number of days in the past a get details request is allowed.
# Maximum number of days in the past to filter when fetching account search history: set to <= 0 to disable.
GET_HISTORY_DAYS_LIMIT = 14

# Account search history max result set size.
ACCOUNT_SEARCH_HISTORY_MAX_SIZE = 1000
# Maximum number or results returned by search.
SEARCH_RESULTS_MAX_SIZE = 5000

# Result set size limit clause
RESULTS_SIZE_LIMIT_CLAUSE = 'FETCH FIRST :max_results_size ROWS ONLY'

ACCOUNT_SEARCH_HISTORY_DATE_QUERY = f"""
SELECT sc.id, sc.search_ts, sc.api_criteria, sc.total_results_size, sc.returned_results_size,
       sr.callback_url, sr.doc_storage_url,
       json_array_length(sr.api_result) as selected_match_count,
       (SELECT CASE WHEN sc.user_id IS NULL THEN ''
         ELSE (SELECT u.firstname || ' ' || u.lastname FROM users u WHERE u.username = sc.user_id
               FETCH FIRST 1 ROWS ONLY)
         END) AS username
FROM search_requests sc, search_results sr
WHERE sc.id = sr.search_id
  AND sc.account_id = '?'
  AND sc.search_ts > ((now() at time zone 'utc') - interval '{str(GET_HISTORY_DAYS_LIMIT)} days')
  AND sc.search_type IN ('MI', 'MO', 'MS', 'MM')
ORDER BY sc.search_ts DESC
FETCH FIRST {str(ACCOUNT_SEARCH_HISTORY_MAX_SIZE)} ROWS ONLY
"""

ACCOUNT_SEARCH_HISTORY_QUERY = f"""
SELECT sc.id, sc.search_ts, sc.api_criteria, sc.total_results_size, sc.returned_results_size,
       sr.callback_url, sr.doc_storage_url,
       json_array_length(sr.api_result) as selected_match_count,
       (SELECT CASE WHEN sc.user_id IS NULL THEN ''
         ELSE (SELECT u.firstname || ' ' || u.lastname FROM users u WHERE u.username = sc.user_id
               FETCH FIRST 1 ROWS ONLY)
         END) AS username
FROM search_requests sc, search_results sr
WHERE sc.id = sr.search_id
  AND sc.account_id = '?'
  AND sc.search_type IN ('MI', 'MO', 'MS', 'MM')
ORDER BY sc.search_ts DESC
FETCH FIRST {str(ACCOUNT_SEARCH_HISTORY_MAX_SIZE)} ROWS ONLY
"""

ACCOUNT_SEARCH_HISTORY_DATE_QUERY_NEW = f"""
SELECT sc.id, sc.search_ts, sc.api_criteria, sc.total_results_size, sc.returned_results_size, sc.user_id,
       sr.callback_url, sr.doc_storage_url, sr.api_result,
       json_array_length(sr.api_result) as selected_match_count,
       (SELECT CASE WHEN sc.user_id IS NULL THEN ''
         ELSE (SELECT u.firstname || ' ' || u.lastname FROM users u WHERE u.username = sc.user_id
               FETCH FIRST 1 ROWS ONLY)
         END) AS username
FROM search_requests sc, search_results sr
WHERE sc.id = sr.search_id
  AND sc.account_id = '?'
  AND sc.search_type IN ('MI', 'MO', 'MS', 'MM')
  AND sc.search_ts > ((now() at time zone 'utc') - interval '{str(GET_HISTORY_DAYS_LIMIT)} days')
ORDER BY sc.search_ts DESC
FETCH FIRST {str(ACCOUNT_SEARCH_HISTORY_MAX_SIZE)} ROWS ONLY
"""

ACCOUNT_SEARCH_HISTORY_QUERY_NEW = f"""
SELECT sc.id, sc.search_ts, sc.api_criteria, sc.total_results_size, sc.returned_results_size, sc.user_id,
       sr.callback_url, sr.doc_storage_url, sr.api_result,
       json_array_length(sr.api_result) as selected_match_count,
       (SELECT CASE WHEN sc.user_id IS NULL THEN ''
         ELSE (SELECT u.firstname || ' ' || u.lastname FROM users u WHERE u.username = sc.user_id
               FETCH FIRST 1 ROWS ONLY)
         END) AS username
FROM search_requests sc, search_results sr
WHERE sc.id = sr.search_id
  AND sc.account_id = '?'
  AND sc.search_type IN ('MI', 'MO', 'MS', 'MM')
ORDER BY sc.search_ts DESC
FETCH FIRST {str(ACCOUNT_SEARCH_HISTORY_MAX_SIZE)} ROWS ONLY
"""

PPR_MHR_NUMBER_QUERY = """
SELECT DISTINCT fs.id
  FROM registrations r, financing_statements fs, serial_collateral sc 
 WHERE r.financing_id = fs.id
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN')
   AND r.base_reg_number IS NULL
   AND (fs.expire_date IS NULL OR fs.expire_date > ((now() at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id 
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
   AND sc.financing_id = fs.id
   AND sc.registration_id_end IS NULL
   AND sc.serial_type = 'MH'
   AND sc.mhr_number = (SELECT searchkey_mhr(:query_value))
ORDER BY fs.id ASC
"""
SEARCH_MHR_NUMBER_QUERY = """
SELECT mhr_number, status_type, registration_ts, city, serial_number, year_made, make, model, id, owner_info
  FROM mhr_search_mhr_number_vw
 WHERE mhr_number = :query_value
"""
SEARCH_SERIAL_QUERY = """
SELECT mhr_number, status_type, registration_ts, city, serial_number, year_made, make, model, id, owner_info
  FROM mhr_search_serial_vw
 WHERE compressed_key = mhr_serial_compressed_key(:query_value)
"""
SEARCH_OWNER_BUS_QUERY = """
SELECT DISTINCT mhr_number, status_type, registration_ts, city, serial_number, year_made, make, model, id,
       business_name, owner_status_type
  FROM mhr_search_owner_bus_vw
 WHERE compressed_name LIKE mhr_name_compressed_key(:query_value) || '%'
"""
SEARCH_OWNER_IND_QUERY = """
SELECT mhr_number, status_type, registration_ts, city, serial_number, year_made, make, model, id,
       owner_status_type, last_name, first_name, middle_name
  FROM mhr_search_owner_ind_vw
 WHERE compressed_name LIKE mhr_name_compressed_key(:query_value) || '%'
"""


def format_mhr_number(request_json):
    """Trim and pad with zeroes search query mhr number query."""
    mhr_num: str = request_json['criteria']['value']
    mhr_num = mhr_num.strip().rjust(6, '0')
    request_json['criteria']['value'] = mhr_num


def search_by_mhr_number(request_json):
    """Execute a search by mhr number query."""
    mhr_num: str = request_json['criteria']['value']
    current_app.logger.info(f'search_by_mhr_number search value={mhr_num}.')
    try:
        query = text(SEARCH_MHR_NUMBER_QUERY)
        result = db.session.execute(query, {'query_value': mhr_num.strip()})
        return result
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('Search_by_mhr_number exception: ' + str(db_exception))
        raise DatabaseException(db_exception)


def search_by_serial_number(request_json):
    """Execute a search by serial number query."""
    serial_num: str = request_json['criteria']['value']
    current_app.logger.info(f'search_by_serial_number search value={serial_num}.')
    try:
        query = text(SEARCH_SERIAL_QUERY)
        result = db.session.execute(query, {'query_value': serial_num.strip()})
        return result
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('Search_by_serial_number exception: ' + str(db_exception))
        raise DatabaseException(db_exception)


def search_by_owner_business(request_json):
    """Execute a search by owner business name query."""
    bus_name: str = request_json['criteria']['value']
    current_app.logger.info(f'search_by_owner_business search value={bus_name}.')
    try:
        query = text(SEARCH_OWNER_BUS_QUERY)
        result = db.session.execute(query, {'query_value': bus_name.strip()})
        return result
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('Search_by_owner_business exception: ' + str(db_exception))
        raise DatabaseException(db_exception)


def search_by_owner_individual(request_json):
    """Execute a search by owner individual name query."""
    owner_name = request_json['criteria']['ownerName']
    name: str = owner_name.get('last')
    if owner_name.get('first'):
        name += ' ' + owner_name.get('first')
    if owner_name.get('middle'):
        name += ' ' + owner_name.get('middle').upper()
    current_app.logger.info(f'search_by_owner_individual search value={name}.')
    try:
        query = text(SEARCH_OWNER_IND_QUERY)
        result = db.session.execute(query, {'query_value': name.strip()})
        return result
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('Search_by_owner_individual exception: ' + str(db_exception))
        raise DatabaseException(db_exception)


def build_search_result_mhr(row):
    """Build a single search summary json from a DB row for a mhr number search."""
    timestamp = row[2]
    year: int = int(row[5]) if row[5] is not None else 0
    result_json = {
        'mhrNumber': str(row[0]),
        'status': str(row[1]),
        'createDateTime': model_utils.format_local_ts(timestamp),
        'homeLocation': str(row[3]).strip(),
        'serialNumber': str(row[4]).strip(),
        'baseInformation': {
            'year': year,
            'make': str(row[6]).strip() if row[6] is not None else '',
            'model': str(row[7]).strip() if row[7] is not None else ''
        },
        'activeCount': 0,
        'exemptCount': 0,
        'historicalCount': 0,
        'mhId': int(row[8])
    }
    return set_owner_info(result_json, row)


def build_search_result_serial(row):
    """Build a single search summary json from a DB row for a serial number search."""
    timestamp = row[2]
    year: int = int(row[5]) if row[5] is not None else 0
    result_json = {
        'mhrNumber': str(row[0]),
        'status': str(row[1]),
        'createDateTime': model_utils.format_local_ts(timestamp),
        'homeLocation': str(row[3]).strip(),
        'serialNumber': str(row[4]).strip(),
        'baseInformation': {
            'year': year,
            'make': str(row[6]).strip() if row[6] is not None else '',
            'model': str(row[7]).strip() if row[7] is not None else ''
        },
        'activeCount': 0,
        'exemptCount': 0,
        'historicalCount': 0,
        'mhId': int(row[8])
    }
    return set_owner_info(result_json, row)


def build_search_result_owner_bus(row):
    """Build a single search summary json from a DB row for a owner business name search."""
    timestamp = row[2]
    year: int = int(row[5]) if row[5] is not None else 0
    result_json = {
        'mhrNumber': str(row[0]),
        'status': str(row[1]),
        'createDateTime': model_utils.format_local_ts(timestamp),
        'homeLocation': str(row[3]).strip(),
        'serialNumber': str(row[4]).strip(),
        'baseInformation': {
            'year': year,
            'make': str(row[6]).strip() if row[6] is not None else '',
            'model': str(row[7]).strip() if row[7] is not None else ''
        },
        'activeCount': 0,
        'exemptCount': 0,
        'historicalCount': 0,
        'mhId': int(row[8]),
        'organizationName': str(row[9])
    }
    owner_status: str = str(row[10])
    return set_owner_status(result_json, owner_status)


def build_search_result_owner_ind(row):
    """Build a single search summary json from a DB row for a owner individual name search."""
    timestamp = row[2]
    year: int = int(row[5]) if row[5] is not None else 0
    result_json = {
        'mhrNumber': str(row[0]),
        'status': str(row[1]),
        'createDateTime': model_utils.format_local_ts(timestamp),
        'homeLocation': str(row[3]).strip(),
        'serialNumber': str(row[4]).strip(),
        'baseInformation': {
            'year': year,
            'make': str(row[6]).strip() if row[6] is not None else '',
            'model': str(row[7]).strip() if row[7] is not None else ''
        },
        'activeCount': 0,
        'exemptCount': 0,
        'historicalCount': 0,
        'mhId': int(row[8])
    }
    owner_status: str = str(row[9])
    owner_name = {
        'last': str(row[10]),
        'first': str(row[11])
    }
    if row[12] is not None:
        owner_name['middle'] = str(row[12])
    result_json['ownerName'] = owner_name
    return set_owner_status(result_json, owner_status)


def set_owner_info(result_json: dict, row) -> dict:
    """ Set the conditional owner status count and name for the result."""
    owner_info = str(row[9]).split('|') if row[9] is not None else []
    owner_status: str = owner_info[0] if owner_info else ''
    if owner_info:
        if len(owner_info) == 2:
            result_json['organizationName'] = owner_info[1]
        else:
            name = {
                'first': owner_info[1]
            }
            if len(owner_info) == 3:
                name['last'] = owner_info[2]
            else:
                name['middle'] = owner_info[2]
                name['last'] = owner_info[3]
            result_json['ownerName'] = name
    else:
        result_json['organizationName'] = ''
    return set_owner_status(result_json, owner_status)


def set_owner_status(result_json: dict, owner_status: str) -> dict:
    """ Set the conditional owner status count."""
    if owner_status == MhrOwnerStatusTypes.ACTIVE:
        result_json['activeCount'] = 1
    elif owner_status == MhrOwnerStatusTypes.EXEMPT:
        result_json['exemptCount'] = 1
    elif owner_status == MhrOwnerStatusTypes.PREVIOUS:
        result_json['historicalCount'] = 1
    return result_json


def get_serial_number_key(serial_num: str) -> str:
    """Get the compressed search serial number key for the MH serial number."""
    key: str = ''

    if not serial_num:
        return key
    key = serial_num.strip().upper()
    # 1. Remove all non-alphanumberic characters.
    key = re.sub('[^0-9A-Z]+', '', key)
    # current_app.logger.debug(f'1: key={key}')
    # 2. Add 6 zeroes to the start of the serial number.
    key = '000000' + key
    # current_app.logger.debug(f'2: key={key}')
    # 3. Determine the value of I as last position in the serial number that contains a numeric value.
    last_pos: int = 0
    for index, char in enumerate(key):
        if char.isdigit():
            last_pos = index
    # current_app.logger.debug(f'3: last_pos={last_pos}')
    # 4. Replace alphas with the corresponding integers:
    # 08600064100100000050000042  where A=0, B=8, C=6…Z=2
    key = key.replace('B', '8')
    key = key.replace('C', '6')
    key = key.replace('G', '6')
    key = key.replace('H', '4')
    key = key.replace('I', '1')
    key = key.replace('L', '1')
    key = key.replace('S', '5')
    key = key.replace('Y', '4')
    key = key.replace('Z', '2')
    key = re.sub('[A-Z]', '0', key)
    # current_app.logger.debug(f'4: key={key}')
    # 5. Take 6 characters of the string beginning at position I – 5 and ending with the position determined by I
    # in step 3.
    start_pos = last_pos - 5
    key = key[start_pos:(last_pos + 1)]
    # current_app.logger.debug(f'5: key={key}')
    return key
