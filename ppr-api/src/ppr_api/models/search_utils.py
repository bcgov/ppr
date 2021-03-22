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

GET_DETAIL_DAYS_LIMIT = 7 # Number of days in the past a get details request is allowed.
# Maximum number of days in the past to filter when fetching account search history: set to <= 0 to disable.
GET_HISTORY_DAYS_LIMIT = 7

# Account search history max result set size.
ACCOUNT_SEARCH_HISTORY_MAX_SIZE = 500
# Maximum number or results returned by search.
SEARCH_RESULTS_MAX_SIZE = 1000

# Result set size limit clause
RESULTS_SIZE_LIMIT_CLAUSE = 'FETCH FIRST ' + str(SEARCH_RESULTS_MAX_SIZE) + ' ROWS ONLY'

# Serial number search base where clause
SERIAL_SEARCH_BASE = """
SELECT r.registration_type_cd,r.registration_ts AS base_registration_ts,
        sc.serial_type_cd,sc.serial_number,sc.year,sc.make,sc.model,
        r.registration_number AS base_registration_num,
        DECODE(serial_number, '?', 'EXACT', 'SIMILAR') AS match_type,
        fs.expire_date,fs.state_type_cd,sc.serial_id AS vehicle_id, sc.mhr_number
  FROM registration r, financing_statement fs, serial_collateral sc 
 WHERE r.financing_id = fs.financing_id
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN')
   AND r.base_reg_number IS NULL
   AND (fs.expire_date IS NULL OR fs.expire_date > ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30))
   AND NOT EXISTS (SELECT r3.registration_id 
                     FROM registration r3
                    WHERE r3.financing_id = fs.financing_id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30))
   AND sc.financing_id = fs.financing_id
   AND sc.registration_id_end IS NULL
"""

# Equivalent logic as DB view search_by_reg_num_vw, but API determines the where clause.
REG_NUM_QUERY = """
SELECT r.registration_type_cd,r.registration_ts AS base_registration_ts,
        r.registration_number AS base_registration_num,
        'EXACT' AS match_type,fs.state_type_cd, fs.expire_date
  FROM registration r, financing_statement fs, registration r2
 WHERE r2.financing_id = r.financing_id
   AND r.financing_id = fs.financing_id
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN')
   AND r.base_reg_number IS NULL
   AND (fs.expire_date IS NULL OR fs.expire_date > ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30))
   AND NOT EXISTS (SELECT r3.registration_id
                     FROM registration r3
                    WHERE r3.financing_id = fs.financing_id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30))
   AND r2.registration_number = '?'
"""

# Equivalent logic as DB view search_by_mhr_num_vw, but API determines the where clause.
MHR_NUM_QUERY = SERIAL_SEARCH_BASE + \
    " AND sc.serial_type_cd = 'MH' " + \
     "AND sc.srch_vin = search_key_pkg.mhr('?') " + \
"ORDER BY match_type, r.registration_ts ASC " + RESULTS_SIZE_LIMIT_CLAUSE

# Equivalent logic as DB view search_by_serial_num_vw, but API determines the where clause.
SERIAL_NUM_QUERY = SERIAL_SEARCH_BASE + \
    " AND sc.serial_type_cd NOT IN ('AC', 'AF', 'AP') " + \
     "AND sc.srch_vin = search_key_pkg.vehicle('?') " + \
"ORDER BY match_type, sc.serial_number " + RESULTS_SIZE_LIMIT_CLAUSE

# Equivalent logic as DB view search_by_aircraft_dot_vw, but API determines the where clause.
AIRCRAFT_DOT_QUERY = SERIAL_SEARCH_BASE + \
    " AND sc.serial_type_cd IN ('AC', 'AF', 'AP') " + \
     "AND sc.srch_vin = search_key_pkg.aircraft('?') " + \
"ORDER BY match_type, sc.serial_number " + RESULTS_SIZE_LIMIT_CLAUSE

BUSINESS_NAME_QUERY = """
SELECT r.registration_type_cd,r.registration_ts AS base_registration_ts,
       p.business_name,
       r.registration_number AS base_registration_num,
       DECODE(p.business_name, '?', 'EXACT', 'SIMILAR') AS match_type,
       fs.expire_date,fs.state_type_cd,p.party_id
  FROM registration r, financing_statement fs, party p
 WHERE r.financing_id = fs.financing_id
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN')
   AND r.base_reg_number IS NULL
   AND (fs.expire_date IS NULL OR fs.expire_date > ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30))
   AND NOT EXISTS (SELECT r3.registration_id
                     FROM registration r3
                    WHERE r3.financing_id = fs.financing_id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30))
   AND p.financing_id = fs.financing_id
   AND p.registration_id_end IS NULL
   AND p.party_type_cd = 'DB'
   AND UTL_MATCH.JARO_WINKLER_SIMILARITY(p.business_srch_key, SEARCH_KEY_PKG.businame('?')) >=
       NVL((SELECT MAX(JARO_VALUE)
              FROM THESAURUS A, JARO  B
             WHERE REGEXP_LIKE(SEARCH_KEY_PKG.businame('?'),WORD,'i')
               AND A.WORD_ID = B.WORD_ID), 85) 
ORDER BY match_type, p.business_name 
"""  + RESULTS_SIZE_LIMIT_CLAUSE

INDIVIDUAL_NAME_QUERY = """
SELECT r.registration_type_cd,r.registration_ts AS base_registration_ts,
       p.last_name,p.first_name,p.middle_name,p.party_id,
       r.registration_number AS base_registration_num,
       DECODE(p.last_name, 'LNAME?',
              DECODE(p.first_name, 'FNAME?', 'EXACT', 'SIMILAR'), 'SIMILAR') AS match_type,
       fs.expire_date,fs.state_type_cd
  FROM registration r, financing_statement fs, party p
 WHERE r.financing_id = fs.financing_id
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN')
   AND r.base_reg_number IS NULL
   AND (fs.expire_date IS NULL OR fs.expire_date > ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30))
   AND NOT EXISTS (SELECT r3.registration_id
                     FROM registration r3
                    WHERE r3.financing_id = fs.financing_id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30))
   AND p.financing_id = fs.financing_id
   AND p.registration_id_end IS NULL
   AND p.party_type_cd = 'DI'
   AND p.party_id IN (SELECT * FROM match_individual_name('LNAME?', 'FNAME?')) 
ORDER BY match_type, p.last_name, p.first_name 
"""  + RESULTS_SIZE_LIMIT_CLAUSE

# Total result count queries for serial number, debtor name searches:
BUSINESS_NAME_TOTAL_COUNT = """
SELECT COUNT(r.registration_id)
  FROM registration r, financing_statement fs, party p
 WHERE r.financing_id = fs.financing_id
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN')
   AND r.base_reg_number IS NULL
   AND (fs.expire_date IS NULL OR fs.expire_date > ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30))
   AND NOT EXISTS (SELECT r3.registration_id
                     FROM registration r3
                    WHERE r3.financing_id = fs.financing_id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30))
   AND p.financing_id = fs.financing_id
   AND p.registration_id_end IS NULL
   AND p.party_type_cd = 'DB'
   AND UTL_MATCH.JARO_WINKLER_SIMILARITY(p.business_srch_key, SEARCH_KEY_PKG.businame('?')) >=
       NVL((SELECT MAX(JARO_VALUE)
              FROM THESAURUS A, JARO  B
             WHERE REGEXP_LIKE(SEARCH_KEY_PKG.businame('?'),WORD,'i')
               AND A.WORD_ID = B.WORD_ID), 85) 
"""

INDIVIDUAL_NAME_TOTAL_COUNT = """
SELECT COUNT(r.registration_id)
  FROM registration r, financing_statement fs, party p
 WHERE r.financing_id = fs.financing_id
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN')
   AND r.base_reg_number IS NULL
   AND (fs.expire_date IS NULL OR fs.expire_date > ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30))
   AND NOT EXISTS (SELECT r3.registration_id
                     FROM registration r3
                    WHERE r3.financing_id = fs.financing_id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30))
   AND p.financing_id = fs.financing_id
   AND p.registration_id_end IS NULL
   AND p.party_type_cd = 'DI'
   AND p.party_id IN (SELECT * FROM match_individual_name('LNAME?', 'FNAME?'))
"""

SERIAL_SEARCH_COUNT_BASE = """
SELECT COUNT(r.registration_id)
  FROM registration r, financing_statement fs, serial_collateral sc
  WHERE r.financing_id = fs.financing_id
    AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN')
    AND r.base_reg_number IS NULL
    AND (fs.expire_date IS NULL OR fs.expire_date > ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30))
    AND NOT EXISTS (SELECT r3.registration_id
                      FROM registration r3
                     WHERE r3.financing_id = fs.financing_id
                       AND r3.registration_type_cl = 'DISCHARGE'
                       AND r3.registration_ts < ((SYSTIMESTAMP AT TIME ZONE 'UTC') - 30))
    AND sc.financing_id = fs.financing_id
    AND sc.registration_id_end IS NULL 
"""

MHR_NUM_TOTAL_COUNT = SERIAL_SEARCH_COUNT_BASE + \
  " AND sc.serial_type_cd = 'MH' " + \
   "AND sc.srch_vin = search_key_pkg.mhr('?')"

SERIAL_NUM_TOTAL_COUNT = SERIAL_SEARCH_COUNT_BASE + \
  " AND sc.serial_type_cd NOT IN ('AC', 'AF') " + \
   "AND sc.srch_vin = search_key_pkg.vehicle('?')"

AIRCRAFT_DOT_TOTAL_COUNT = SERIAL_SEARCH_COUNT_BASE + \
  " AND sc.serial_type_cd IN ('AC', 'AF') " + \
   "AND sc.srch_vin = search_key_pkg.aircraft('?')"

COUNT_QUERY_FROM_SEARCH_TYPE = {
    'AC': AIRCRAFT_DOT_TOTAL_COUNT,
    'BS': BUSINESS_NAME_TOTAL_COUNT,
    'IS': INDIVIDUAL_NAME_TOTAL_COUNT,
    'MH': MHR_NUM_TOTAL_COUNT,
    'SS': SERIAL_NUM_TOTAL_COUNT
}

ACCOUNT_SEARCH_HISTORY_DATE_QUERY = \
'SELECT sc.search_id, sc.search_ts, sc.api_criteria, sc.total_results_size, sc.returned_results_size,' + \
       'sr.exact_match_count, sr.similar_match_count ' + \
  'FROM search_client sc, search_result sr ' + \
 'WHERE sc.search_id = sr.search_id ' + \
   "AND sc.account_id = '?' " + \
   "AND sc.search_ts > ((SYSTIMESTAMP AT TIME ZONE 'UTC') - " + str(GET_HISTORY_DAYS_LIMIT) + ') ' + \
'ORDER BY sc.search_ts DESC ' + \
'FETCH FIRST ' + str(ACCOUNT_SEARCH_HISTORY_MAX_SIZE) + ' ROWS ONLY'

ACCOUNT_SEARCH_HISTORY_QUERY = \
'SELECT sc.search_id, sc.search_ts, sc.api_criteria, sc.total_results_size, sc.returned_results_size,' + \
       'sr.exact_match_count, sr.similar_match_count ' + \
  'FROM search_client sc, search_result sr ' + \
 'WHERE sc.search_id = sr.search_id ' + \
   "AND sc.account_id = '?' " + \
'ORDER BY sc.search_ts DESC ' + \
'FETCH FIRST ' + str(ACCOUNT_SEARCH_HISTORY_MAX_SIZE) + ' ROWS ONLY'
