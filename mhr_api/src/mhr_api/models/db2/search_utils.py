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


GET_DETAIL_DAYS_LIMIT = 7 # Number of days in the past a get details request is allowed.
# Maximum number of days in the past to filter when fetching account search history: set to <= 0 to disable.
GET_HISTORY_DAYS_LIMIT = -1

# Account search history max result set size.
ACCOUNT_SEARCH_HISTORY_MAX_SIZE = 1000
# Maximum number or results returned by search.
SEARCH_RESULTS_MAX_SIZE = 5000

# Result set size limit clause
RESULTS_SIZE_LIMIT_CLAUSE = 'FETCH FIRST :max_results_size ROWS ONLY'

# Serial number search base where clause
SERIAL_SEARCH_BASE = """
SELECT r.registration_type,r.registration_ts AS base_registration_ts,
        sc.serial_type,sc.serial_number,sc.year,sc.make,sc.model,
        r.registration_number AS base_registration_num,
        CASE WHEN serial_number = :query_value THEN 'EXACT' ELSE 'SIMILAR' END match_type,
        fs.expire_date,fs.state_type,sc.id AS vehicle_id, sc.mhr_number
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
"""

MHR_NUM_QUERY = """
SELECT mh.mhregnum, mh.mhstatus, mh.exemptfl, d.regidate, o.ownrtype, o.ownrname, l.towncity, de.sernumb1, de.yearmade,
       de.makemodl
  FROM manuhome mh, document d, owner o, location l, descript de
 WHERE mh.mhregnum = :query_value
   AND mh.mhregnum = d.mhregnum
   AND mh.regdocid = d.documtid
   AND mh.manhomid = o.manhomid
   AND o.owngrpid = 1
   AND o.ownerid = 1
   AND mh.manhomid = l.manhomid
   AND l.status = 'A'
   AND mh.manhomid = de.manhomid
   AND de.status = 'A'
"""

# Equivalent logic as DB view search_by_serial_num_vw, but API determines the where clause.
SERIAL_NUM_QUERY = SERIAL_SEARCH_BASE + """
   AND sc.serial_type NOT IN ('AC', 'AF', 'AP')
   AND sc.srch_vin = (SELECT searchkey_vehicle(:query_value)) 
ORDER BY match_type, sc.serial_number ASC, sc.year ASC, r.registration_ts ASC
"""


BUSINESS_NAME_QUERY = """
WITH q AS (
   SELECT(SELECT searchkey_business_name(:query_bus_name)) AS search_key,
   SUBSTR((SELECT searchkey_business_name(:query_bus_name)),1,1) AS search_key_char1,
   (SELECT business_name_strip_designation(:query_bus_name)) AS search_name_base,
   (SELECT array_length(string_to_array(trim(regexp_replace(:query_bus_name,'^THE','','gi')),' '),1)) AS word_length)
SELECT r.registration_type,r.registration_ts AS base_registration_ts,
       p.business_name,
       r.registration_number AS base_registration_num,
       CASE WHEN p.bus_name_base = search_name_base THEN 'EXACT'
            ELSE 'SIMILAR' END match_type,
       fs.expire_date,fs.state_type,p.id
  FROM registrations r, financing_statements fs, parties p, q
WHERE r.financing_id = fs.id
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN')
   AND r.base_reg_number IS NULL
   AND (fs.expire_date IS NULL OR fs.expire_date > ((now() at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
   AND p.financing_id = fs.id
   AND p.registration_id_end IS NULL
   AND p.party_type = 'DB'
   AND p.bus_name_key_char1 = search_key_char1
   AND ((search_key <% p.business_srch_key AND
          SIMILARITY(search_key, p.business_srch_key) >= :query_bus_quotient)
          OR p.business_srch_key = search_key
          OR word_length=1 and search_key = split_part(business_name,' ',1)
          OR (LENGTH(search_key) >= 3 AND LEVENSHTEIN(search_key, p.business_srch_key) <= 1) AND 
              p.bus_name_key_char1 = search_key_char1
    )
ORDER BY match_type, p.business_name ASC, r.registration_ts ASC
"""

INDIVIDUAL_NAME_QUERY = """
WITH q AS (SELECT(searchkey_last_name(:query_last)) AS search_last_key)
SELECT r.registration_type,r.registration_ts AS base_registration_ts,
       p.last_name,p.first_name,p.middle_initial,p.id,
       r.registration_number AS base_registration_num,
       CASE WHEN search_last_key = p.last_name_key AND p.first_name = :query_first THEN 'EXACT'
            WHEN search_last_key = p.last_name_key AND LENGTH(:query_first) = 1 AND
                 :query_first = p.first_name_char1 THEN 'EXACT'
            WHEN search_last_key = p.last_name_key AND LENGTH(p.first_name) = 1 AND
                 p.first_name = LEFT(:query_first, 1) THEN 'EXACT'
            WHEN search_last_key = p.last_name_key AND p.first_name_char2 IS NOT NULL AND p.first_name_char2 = '-' AND
                 p.first_name_char1 = LEFT(:query_first, 1) THEN 'EXACT'
            WHEN search_last_key = p.last_name_key AND LENGTH(:query_first) > 1 AND SUBSTR(:query_first, 2, 1) = '-'
                 AND p.first_name_char1 = LEFT(:query_first, 1) THEN 'EXACT'
            ELSE 'SIMILAR' END match_type,
       fs.expire_date,fs.state_type, p.birth_date
  FROM registrations r, financing_statements fs, parties p, q
WHERE r.financing_id = fs.id
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN')
   AND r.base_reg_number IS NULL
   AND (fs.expire_date IS NULL OR fs.expire_date > ((now() at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
   AND p.financing_id = fs.id
   AND p.registration_id_end IS NULL
   AND p.party_type = 'DI'
   AND p.id IN (SELECT * FROM unnest(match_individual_name(:query_last, :query_first, :query_last_quotient,
                                                           :query_first_quotient, :query_default_quotient))) 
ORDER BY match_type, p.last_name ASC, p.first_name ASC, p.middle_initial ASC, p.birth_date ASC,  r.registration_ts ASC
"""

INDIVIDUAL_NAME_MIDDLE_QUERY = """
WITH q AS (SELECT(searchkey_last_name(:query_last)) AS search_last_key)
SELECT r.registration_type,r.registration_ts AS base_registration_ts,
       p.last_name,p.first_name,p.middle_initial,p.id,
       r.registration_number AS base_registration_num,
       CASE WHEN search_last_key = p.last_name_key AND p.first_name = :query_first AND
               (p.middle_initial is NULL OR LEFT(p.middle_initial, 1) = LEFT(:query_middle, 1)) THEN 'EXACT'
            WHEN search_last_key = p.last_name_key AND LENGTH(:query_first) = 1 AND
                 :query_first = p.first_name_char1 AND
                 (p.middle_initial is NULL OR LEFT(p.middle_initial, 1) = LEFT(:query_middle, 1)) THEN 'EXACT'
            WHEN search_last_key = p.last_name_key AND LENGTH(p.first_name) = 1 AND
                 p.first_name = LEFT(:query_first, 1) AND
                 (p.middle_initial is NULL OR LEFT(p.middle_initial, 1) = LEFT(:query_middle, 1)) THEN 'EXACT'
            WHEN search_last_key = p.last_name_key AND p.first_name_char2 IS NOT NULL AND p.first_name_char2 = '-' AND
                 p.first_name_char1 = LEFT(:query_first, 1) AND
                 (p.middle_initial is NULL OR LEFT(p.middle_initial, 1) = LEFT(:query_middle, 1)) THEN 'EXACT'
            WHEN search_last_key = p.last_name_key AND LENGTH(:query_first) > 1 AND SUBSTR(:query_first, 2, 1) = '-'
                 AND p.first_name_char1 = LEFT(:query_first, 1) AND
                 (p.middle_initial is NULL OR LEFT(p.middle_initial, 1) = LEFT(:query_middle, 1)) THEN 'EXACT'
            ELSE 'SIMILAR' END match_type,
       fs.expire_date,fs.state_type, p.birth_date
  FROM registrations r, financing_statements fs, parties p, q
WHERE r.financing_id = fs.id
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN')
   AND r.base_reg_number IS NULL
   AND (fs.expire_date IS NULL OR fs.expire_date > ((now() at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
   AND p.financing_id = fs.id
   AND p.registration_id_end IS NULL
   AND p.party_type = 'DI'
   AND p.id IN (SELECT * FROM unnest(match_individual_name(:query_last, :query_first, :query_last_quotient,
                                                           :query_first_quotient, :query_default_quotient))) 
ORDER BY match_type, p.last_name ASC, p.first_name ASC, p.middle_initial ASC, p.birth_date ASC,  r.registration_ts ASC
"""


def search_by_mhr_number(current_app, db, request_json):
     """Execute a DB2 search by mhr number query."""
     mhr_num = request_json['criteria']['value']
     try:
          query = text(MHR_NUM_QUERY)
          result = db.get_engine(current_app, 'db2').execute(query, {'query_value': mhr_num.strip()})
          return result
     except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('DB2 search_by_mhr_number exception: ' + repr(db_exception))
        raise DatabaseException(db_exception)
