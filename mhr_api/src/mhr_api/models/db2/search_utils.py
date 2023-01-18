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
from sqlalchemy.sql import text

from mhr_api.exceptions import DatabaseException
from mhr_api.models import utils as model_utils


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
SELECT DISTINCT mh.mhregnum, mh.mhstatus, mh.exemptfl, d.regidate,
       (SELECT o.ownrtype || og.status || o.ownrname
          FROM owner o, owngroup og
         WHERE mh.manhomid = o.manhomid
           AND mh.manhomid = og.manhomid
           AND o.owngrpid = og.owngrpid
           AND og.status IN ('3', '4')
           FETCH FIRST 1 ROWS ONLY) AS owner_info,
       l.towncity, de.sernumb1, de.yearmade,
       de.makemodl, mh.manhomid, TRIM(de.sernumb2), TRIM(de.sernumb3), TRIM(de.sernumb4)
  FROM manuhome mh, document d, location l, descript de
 WHERE mh.mhregnum = d.mhregnum
   AND mh.regdocid = d.documtid
   AND mh.manhomid = l.manhomid
   AND l.status = 'A'
   AND mh.manhomid = de.manhomid
   AND de.status = 'A'
   AND (RIGHT(('000000' || TRANSLATE(TRIM(de.sernumb1), '08600064100100000050000042', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')),
              6) = :query_value OR
        RIGHT(('000000' || TRANSLATE(TRIM(de.sernumb2), '08600064100100000050000042', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')),
              6) = :query_value OR
        RIGHT(('000000' || TRANSLATE(TRIM(de.sernumb3), '08600064100100000050000042', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')),
              6) = :query_value OR
        RIGHT(('000000' || TRANSLATE(TRIM(de.sernumb4), '08600064100100000050000042', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')),
              6) = :query_value)
ORDER BY de.sernumb1 ASC, mh.mhstatus ASC, mh.mhregnum DESC
"""

OWNER_NAME_QUERY = """
SELECT DISTINCT mh.mhregnum, mh.mhstatus, mh.exemptfl, d.regidate, o.ownrtype, o.ownrname, l.towncity, de.sernumb1,
       de.yearmade, de.makemodl, mh.manhomid, og.status, og.owngrpid
  FROM manuhome mh, document d, owner o, location l, descript de, owngroup og
 WHERE mh.mhregnum = d.mhregnum
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
SELECT DISTINCT mh.mhregnum, mh.mhstatus, mh.exemptfl, d.regidate, o.ownrtype, o.ownrname, l.towncity, de.sernumb1,
       de.yearmade, de.makemodl, mh.manhomid, og.status, og.owngrpid
  FROM manuhome mh, document d, owner o, location l, descript de, owngroup og
 WHERE mh.mhregnum = d.mhregnum
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
    serial_key = get_search_serial_number_key(serial_num)
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
