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

# Equivalent logic as DB view search_by_reg_num_vw, but API determines the where clause.
REG_NUM_QUERY = """
SELECT r2.registration_type, r2.registration_ts AS base_registration_ts, 
       r2.registration_number AS base_registration_num,
       'EXACT' AS match_type, fs.state_type, fs.expire_date
  FROM registrations r, financing_statements fs, registrations r2
 WHERE r.financing_id = fs.id
   AND r2.financing_id = fs.id
   AND r2.registration_type_cl IN ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN')
   AND r.registration_number = :query_value
   AND (fs.expire_date IS NULL OR fs.expire_date > ((now() at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
"""

# Equivalent logic as DB view search_by_mhr_num_vw, but API determines the where clause.
MHR_NUM_QUERY = SERIAL_SEARCH_BASE + """
   AND sc.serial_type = 'MH' 
   AND sc.mhr_number = (SELECT searchkey_mhr(:query_value)) 
ORDER BY match_type, sc.serial_number ASC, sc.year ASC, r.registration_ts ASC
"""

# Equivalent logic as DB view search_by_serial_num_vw, but API determines the where clause.
SERIAL_NUM_QUERY = SERIAL_SEARCH_BASE + """
   AND sc.serial_type NOT IN ('AC', 'AF', 'AP')
   AND sc.srch_vin = (SELECT searchkey_vehicle(:query_value)) 
ORDER BY match_type, sc.serial_number ASC, sc.year ASC, r.registration_ts ASC
"""

# Equivalent logic as DB view search_by_aircraft_dot_vw, but API determines the where clause.
AIRCRAFT_DOT_QUERY = SERIAL_SEARCH_BASE + """
   AND sc.serial_type IN ('AC', 'AF', 'AP')
   AND sc.srch_vin = (SELECT searchkey_aircraft(:query_value)) 
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

# Total result count queries for serial number, debtor name searches:
BUSINESS_NAME_TOTAL_COUNT = """
WITH q AS (
   SELECT searchkey_business_name(:query_bus_name) AS search_key
)
SELECT COUNT(r.id) AS query_count
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
   AND SUBSTR(search_key,1,1) = SUBSTR(p.business_name,1,1)
   AND (SIMILARITY(search_key, p.business_srch_key) >= :query_bus_quotient OR p.business_srch_key = search_key)
"""

INDIVIDUAL_NAME_TOTAL_COUNT = """
SELECT COUNT(r.id) AS query_count
  FROM registrations r, financing_statements fs, parties p
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
"""

SERIAL_SEARCH_COUNT_BASE = """
SELECT COUNT(r.id) AS query_count
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

MHR_NUM_TOTAL_COUNT = SERIAL_SEARCH_COUNT_BASE + \
  " AND sc.serial_type = 'MH' " + \
   "AND sc.mhr_number = searchkey_mhr(:query_value)"

SERIAL_NUM_TOTAL_COUNT = SERIAL_SEARCH_COUNT_BASE + \
  " AND sc.serial_type NOT IN ('AC', 'AF') " + \
   "AND sc.srch_vin = searchkey_vehicle(:query_value)"

AIRCRAFT_DOT_TOTAL_COUNT = SERIAL_SEARCH_COUNT_BASE + \
  " AND sc.serial_type IN ('AC', 'AF') " + \
   "AND sc.srch_vin = searchkey_aircraft(:query_value)"

COUNT_QUERY_FROM_SEARCH_TYPE = {
    'AC': AIRCRAFT_DOT_TOTAL_COUNT,
    'BS': BUSINESS_NAME_TOTAL_COUNT,
    'IS': INDIVIDUAL_NAME_TOTAL_COUNT,
    'MH': MHR_NUM_TOTAL_COUNT,
    'SS': SERIAL_NUM_TOTAL_COUNT
}

ACCOUNT_SEARCH_HISTORY_DATE_QUERY = \
'SELECT sc.id, sc.search_ts, sc.api_criteria, sc.total_results_size, sc.returned_results_size,' + \
       '(SELECT CASE WHEN sr.api_result IS NULL THEN 0 ' + \
                    'ELSE (SELECT COUNT(*) ' + \
                            'FROM json_array_elements(sr.api_result) sr2 ' + \
                           "WHERE sr2 ->> 'matchType' = 'EXACT') END) AS exact_match_count, " + \
       'sr.similar_match_count, sr.callback_url, sr.doc_storage_url, ' + \
       'json_array_length(sr.api_result) as selected_match_count, ' + \
       "(SELECT CASE WHEN sc.user_id IS NULL THEN '' " + \
                    "ELSE (SELECT u.firstname || ' ' || u.lastname " + \
                            'FROM users u ' + \
                           'WHERE u.username = sc.user_id) END) AS username ' + \
  'FROM search_requests sc, search_results sr ' + \
 'WHERE sc.id = sr.search_id ' + \
   "AND sc.account_id = '?' " + \
   "AND sc.search_ts > ((now() at time zone 'utc') - interval '" + str(GET_HISTORY_DAYS_LIMIT) + " days') " + \
'ORDER BY sc.search_ts DESC ' + \
'FETCH FIRST ' + str(ACCOUNT_SEARCH_HISTORY_MAX_SIZE) + ' ROWS ONLY'

ACCOUNT_SEARCH_HISTORY_QUERY = \
'SELECT sc.id, sc.search_ts, sc.api_criteria, sc.total_results_size, sc.returned_results_size,' + \
       '(SELECT CASE WHEN sr.api_result IS NULL THEN 0 ' + \
                    'ELSE (SELECT COUNT(*) ' + \
                            'FROM json_array_elements(sr.api_result) sr2 ' + \
                           "WHERE sr2 ->> 'matchType' = 'EXACT') END) AS exact_match_count, " + \
       'sr.similar_match_count, sr.callback_url, sr.doc_storage_url, ' + \
       'json_array_length(sr.api_result) as selected_match_count, ' + \
       "(SELECT CASE WHEN sc.user_id IS NULL THEN '' " + \
                    "ELSE (SELECT u.firstname || ' ' || u.lastname " + \
                            'FROM users u ' + \
                           'WHERE u.username = sc.user_id) END) AS username ' + \
  'FROM search_requests sc, search_results sr ' + \
 'WHERE sc.id = sr.search_id ' + \
   "AND sc.account_id = '?' " + \
'ORDER BY sc.search_ts DESC ' + \
'FETCH FIRST ' + str(ACCOUNT_SEARCH_HISTORY_MAX_SIZE) + ' ROWS ONLY'
