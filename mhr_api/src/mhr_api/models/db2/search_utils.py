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
from mhr_api.models.db2 import utils as db2_utils


GET_DETAIL_DAYS_LIMIT = 7 # Number of days in the past a get details request is allowed.
# Maximum number of days in the past to filter when fetching account search history: set to <= 0 to disable.
GET_HISTORY_DAYS_LIMIT = -1

# Account search history max result set size.
ACCOUNT_SEARCH_HISTORY_MAX_SIZE = 1000
# Maximum number or results returned by search.
SEARCH_RESULTS_MAX_SIZE = 5000

# Result set size limit clause
RESULTS_SIZE_LIMIT_CLAUSE = 'FETCH FIRST :max_results_size ROWS ONLY'

MHR_NUM_QUERY = """
SELECT mh.mhregnum, mh.mhstatus, mh.exemptfl, d.regidate, l.towncity, de.sernumb1, de.yearmade,
       de.makemodl, mh.manhomid,
       (SELECT o.ownrtype || og.status || o.ownrname
          FROM owner o, owngroup og
         WHERE mh.manhomid = o.manhomid
           AND mh.manhomid = og.manhomid
           AND o.owngrpid = og.owngrpid
           AND og.status IN ('3', '4')
           FETCH FIRST 1 ROWS ONLY) AS owner_info
  FROM manuhome mh, document d, location l, descript de
 WHERE mh.mhregnum = :query_value
   AND mh.mhstatus != 'D'
   AND mh.mhregnum = d.mhregnum
   AND mh.regdocid = d.documtid
   AND mh.manhomid = l.manhomid
   AND l.status = 'A'
   AND mh.manhomid = de.manhomid
   AND de.status = 'A'
"""

# Example if changing to include all owner names.
#       (SELECT LISTAGG(o2.ownrname, ',')
#          FROM owner o2
#        WHERE o2.manhomid = mh.manhomid) as owner_names, 
SERIAL_NUM_QUERY = """
SELECT mh.mhregnum, mh.mhstatus, mh.exemptfl, d.regidate,
       (SELECT o.ownrtype || og.status || o.ownrname
          FROM owner o, owngroup og
         WHERE mh.manhomid = o.manhomid
           AND mh.manhomid = og.manhomid
           AND o.owngrpid = og.owngrpid
           AND og.status IN ('3', '4')
           FETCH FIRST 1 ROWS ONLY) AS owner_info,
       l.towncity, TRIM(de.sernumb1) AS serial_num, de.yearmade,
       TRIM(de.makemodl) AS make_model, mh.manhomid,
       TRIM(de.sernumb2) AS serial_num2, TRIM(de.sernumb3) AS serial_num3, TRIM(de.sernumb4) AS serial_num4
  FROM manuhome mh, document d, location l, descript de
 WHERE mh.mhregnum = d.mhregnum
   AND mh.mhstatus != 'D'
   AND mh.regdocid = d.documtid
   AND mh.manhomid = l.manhomid
   AND l.status = 'A'
   AND mh.manhomid = de.manhomid
   AND de.status = 'A'
   AND EXISTS (SELECT c.manhomid
                 FROM cmpserno c
                WHERE mh.manhomid = c.manhomid
                  AND HEX(c.serialno) = :query_value)
"""

OWNER_NAME_QUERY = """
SELECT mh.mhregnum, mh.mhstatus, mh.exemptfl, d.regidate, o.ownrtype, o.ownrname, l.towncity, de.sernumb1,
       de.yearmade, de.makemodl, mh.manhomid, og.status, og.owngrpid
  FROM manuhome mh, document d, owner o, location l, descript de, owngroup og
 WHERE mh.mhregnum = d.mhregnum
   AND mh.mhstatus != 'D'
   AND mh.regdocid = d.documtid
   AND mh.manhomid = l.manhomid
   AND l.status = 'A'
   AND mh.manhomid = de.manhomid
   AND de.status = 'A'
   AND mh.manhomid = o.manhomid
   AND o.ownrtype = 'I'
   AND o.compname LIKE :query_value || '%'
   AND o.manhomid = og.manhomid
   AND o.owngrpid = og.owngrpid
   AND og.status IN ('3', '4', '5')
ORDER BY o.ownrname ASC, og.status ASC, mh.mhstatus ASC, mh.mhregnum DESC
"""

ORG_NAME_QUERY = """
SELECT mh.mhregnum, mh.mhstatus, mh.exemptfl, d.regidate, o.ownrtype, o.ownrname, l.towncity, de.sernumb1,
       de.yearmade, de.makemodl, mh.manhomid, og.status, og.owngrpid
  FROM manuhome mh, document d, owner o, location l, descript de, owngroup og
 WHERE mh.mhregnum = d.mhregnum
   AND mh.mhstatus != 'D'
   AND mh.regdocid = d.documtid
   AND mh.manhomid = l.manhomid
   AND l.status = 'A'
   AND mh.manhomid = de.manhomid
   AND de.status = 'A'
   AND mh.manhomid = o.manhomid
   AND o.ownrtype = 'B'
   AND o.compname LIKE :query_value || '%'
   AND o.manhomid = og.manhomid
   AND o.owngrpid = og.owngrpid
   AND og.status IN ('3', '4', '5')
ORDER BY o.ownrname ASC, og.status ASC, mh.mhstatus ASC, mh.mhregnum DESC
"""

LEGACY_TO_OWNER_STATUS = {
    '3': 'ACTIVE',
    '4': 'EXEMPT',
    '5': 'PREVIOUS'
}
LEGACY_TO_REGISTRATION_STATUS = {
    'R': 'ACTIVE',
    'E': 'EXEMPT',
    'C': 'HISTORICAL'
}
LEGACY_REGISTRATION_ACTIVE = 'R'


def search_by_mhr_number(current_app, db, request_json):
     """Execute a DB2 search by mhr number query."""
     mhr_num = request_json['criteria']['value']
     current_app.logger.info(f'DB2 search_by_mhr_number search value={mhr_num}.')
     try:
          query = text(MHR_NUM_QUERY)
          result = db.get_engine(current_app, 'db2').execute(query, {'query_value': mhr_num.strip()})
          return result
     except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('DB2 search_by_mhr_number exception: ' + str(db_exception))
        raise DatabaseException(db_exception)

def search_by_organization_name(current_app, db, request_json):
     """Execute a DB2 search by organization name query."""
     value = request_json['criteria']['value']
     key = model_utils.get_compressed_key(value)
     current_app.logger.info(f'DB2 search_by_organization_name search value={value}, key={key}.')
     try:
          query = text(ORG_NAME_QUERY)
          result = db.get_engine(current_app, 'db2').execute(query, {'query_value': key})
          return result
     except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('DB2 search_by_organization_name exception: ' + str(db_exception))
        raise DatabaseException(db_exception)

def search_by_owner_name(current_app, db, request_json):
     """Execute a DB2 search by owner name query."""
     try:
          owner_name = request_json['criteria']['ownerName']
          name: str = owner_name.get('last')
          if owner_name.get('first'):
               name += ' ' + owner_name.get('first')
          if owner_name.get('middle'):
               name += ' ' + owner_name.get('middle').upper()
          key = model_utils.get_compressed_key(name)
          current_app.logger.info(f'DB2 search_by_owner_name search value={name}, key={key}.')
          query = text(OWNER_NAME_QUERY)
          result = db.get_engine(current_app, 'db2').execute(query, {'query_value': key})
          return result
     except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('DB2 search_by_owner_name exception: ' + str(db_exception))
        raise DatabaseException(db_exception)

def search_by_serial_number(current_app, db, request_json):
    """Execute a DB2 search by serial number query."""
    serial_num:str = request_json['criteria']['value']
    serial_key = get_search_serial_number_key_hex(serial_num)
    current_app.logger.debug(f'DB2 search_by_serial_number search value={serial_num}, key={serial_key}.')
    try:
        query = text(SERIAL_NUM_QUERY)
        result = db.get_engine(current_app, 'db2').execute(query, {'query_value': serial_key})
        return result
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('DB2 search_by_serial_number exception: ' + str(db_exception))
        raise DatabaseException(db_exception)

def get_search_serial_number_key(serial_num: str) -> str:
    """Get the search serial number key for the MH serial number."""
    if not serial_num:
        return ''
    key: str = '000000' + serial_num.strip().upper()
    # Replace alphas with the corresponding integers:
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
    start_pos: int = len(key) - 6
    return key[start_pos:]

def get_search_serial_number_key_hex(serial_num: str) -> str:
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
    # 6. Convert it to bytes and return the last 3.
    key_bytes: bytes = int(key).to_bytes(3, 'big')
    key_hex = key_bytes.hex().upper()
    current_app.logger.debug(f'key={key} last 3 bytes={key_bytes} hex={key_hex}')
    return key_hex

def build_search_result_owner(row):
    """Build a single search by owner summary json from a DB row."""
    mh_status = str(row[1])
    status = LEGACY_TO_REGISTRATION_STATUS[mh_status]
    # current_app.logger.info('Mapping timestamp')
    timestamp = row[3]
    # current_app.logger.info('Timestamp mapped')
    value: str = str(row[8])
    year = int(value) if value.isnumeric() else 0
    result_json = {
        'mhrNumber': str(row[0]),
        'status': status,
        'createDateTime': model_utils.format_local_ts(timestamp),
        'homeLocation': str(row[6]).strip(),
        'serialNumber': str(row[7]).strip(),
        'baseInformation': {
            'year': year,
            'make': str(row[9]).strip(),
            'model': ''
        },
        'activeCount': 0,
        'exemptCount': 0,
        'historicalCount': 0,
        'mhId': int(row[10])
    }
    # current_app.logger.info(result_json)
    owner_type = str(row[4])
    owner_name = str(row[5]).strip()
    if owner_type != 'I':
        result_json['organizationName'] = owner_name
    else:
        result_json['ownerName'] = model_utils.get_ind_name_from_db2(owner_name)
    owner_status: str = str(row[11])
    result_json['ownerStatus'] = LEGACY_TO_OWNER_STATUS[owner_status]
    if owner_status == '3':
        result_json['activeCount'] = 1
    elif owner_status == '4':
        result_json['exemptCount'] = 1
    elif owner_status == '5':
        result_json['historicalCount'] = 1
    return result_json

def build_search_result_mhr(row):
    """Build a single search summary json from a DB row for a mhr number search."""
    mh_status = str(row[1])
    status = LEGACY_TO_REGISTRATION_STATUS[mh_status]
    # current_app.logger.info('Mapping timestamp')
    timestamp = row[3]
    # current_app.logger.info('Timestamp mapped')
    value: str = str(row[6])
    year = int(value) if value.isnumeric() else 0
    result_json = {
        'mhrNumber': str(row[0]),
        'status': status,
        'createDateTime': model_utils.format_local_ts(timestamp),
        'homeLocation': str(row[4]).strip(),
        'serialNumber': str(row[5]).strip(),
        'baseInformation': {
            'year': year,
            'make': str(row[7]).strip(),
            'model': ''
        },
        'activeCount': 0,
        'exemptCount': 0,
        'historicalCount': 0,
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
    if owner_status == '3':
        result_json['activeCount'] = 1
    elif owner_status == '4':
        result_json['exemptCount'] = 1
    elif owner_status == '5':
        result_json['historicalCount'] = 1
    # current_app.logger.info(result_json)
    return result_json

def build_search_result_serial(row, request_json: dict):
    """Build a single search summary json from a DB row for a serial number search."""
    mh_status = str(row[1])
    status = LEGACY_TO_REGISTRATION_STATUS[mh_status]
    # current_app.logger.info('Mapping timestamp')
    timestamp = row[3]
    # current_app.logger.info('Timestamp mapped')
    value: str = str(row[7])
    year = int(value) if value.isnumeric() else 0
    result_json = {
        'mhrNumber': str(row[0]),
        'status': status,
        'createDateTime': model_utils.format_local_ts(timestamp),
        'homeLocation': str(row[5]).strip(),
        'baseInformation': {
            'year': year,
            'make': str(row[8]).strip(),
            'model': ''
        },
        'serialNumber': str(row[6]).strip(),
        'activeCount': 1,
        'exemptCount': 0,
        'historicalCount': 0,
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
    return get_matching_serial_numbers(row, request_json, result_json)

def get_matching_serial_numbers(row, request_json: dict, result_json: dict) -> dict:
    """Get matching serial number(s) for an individual searcy by serial number result."""
    serial2: str = str(row[10]) if row[10] else ''
    serial3: str = str(row[11]) if row[11] else ''
    serial4: str = str(row[12]) if row[12] else ''
    if not serial2 and not serial3 and not serial4:
        return result_json
    search_val:str = request_json['criteria']['value']
    search_key = get_search_serial_number_key_hex(search_val)
    serial_match: str = result_json.get('serialNumber')
    match_count: int = 0
    if search_key != get_search_serial_number_key_hex(serial_match):
        serial_match = ''
    else:
        match_count = 1
    if serial2 and search_key == get_search_serial_number_key_hex(serial2):
        match_count += 1
        if serial_match == '' or serial_match.find(serial2) == -1:
            serial_match += ', ' + serial2 if serial_match != '' else serial2
    if serial3 and search_key == get_search_serial_number_key_hex(serial3):
        match_count += 1
        if serial_match == '' or serial_match.find(serial3) == -1:
            serial_match += ', ' + serial3 if serial_match != '' else serial3
    if serial4 and search_key == get_search_serial_number_key_hex(serial4):
        match_count += 1
        if serial_match == '' or serial_match.find(serial4) == -1:
            serial_match += ', ' + serial4 if serial_match != '' else serial4
    result_json['serialNumber'] = serial_match
    result_json['activeCount'] = match_count
    return result_json
