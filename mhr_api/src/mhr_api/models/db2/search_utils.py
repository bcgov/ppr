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
SELECT mh.mhregnum, mh.mhstatus, mh.exemptfl, d.regidate, o.ownrtype, o.ownrname, l.towncity, de.sernumb1, de.yearmade,
       de.makemodl, mh.manhomid, '3'
  FROM manuhome mh, document d, owner o, location l, descript de
 WHERE mh.mhregnum = :query_value
   AND mh.mhregnum = d.mhregnum
   AND mh.regdocid = d.documtid
   AND mh.manhomid = l.manhomid
   AND l.status = 'A'
   AND mh.manhomid = de.manhomid
   AND de.status = 'A'
   AND mh.manhomid = o.manhomid
   AND o.ownerid = 1
   AND o.owngrpid IN (SELECT MIN(og2.owngrpid)
                        FROM owngroup og2
                       WHERE mh.manhomid = og2.manhomid
                         AND og2.status IN ('3', '4'))
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
       de.makemodl, mh.manhomid, c.cmpserid, de.sernumb2, de.sernumb3, de.sernumb4
  FROM manuhome mh, document d, location l, descript de, cmpserno c
 WHERE mh.mhregnum = d.mhregnum
   AND mh.regdocid = d.documtid
   AND mh.manhomid = l.manhomid
   AND l.status = 'A'
   AND mh.manhomid = de.manhomid
   AND de.status = 'A'
   AND mh.manhomid = c.manhomid
   AND HEX(c.serialno) = :query_value
ORDER BY d.regidate ASC
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
ORDER BY o.ownrname ASC, d.regidate ASC
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
ORDER BY o.ownrname ASC, d.regidate ASC
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
     serial_key = model_utils.get_serial_number_key_hex(serial_num)  # serial_num.upper().strip()
     current_app.logger.debug(f'DB2 search_by_serial_number search value={serial_num}, key={serial_key}.')
     try:
          query = text(SERIAL_NUM_QUERY)
          result = db.get_engine(current_app, 'db2').execute(query, {'query_value': serial_key})
          return result
     except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('DB2 search_by_serial_number exception: ' + str(db_exception))
        raise DatabaseException(db_exception)
