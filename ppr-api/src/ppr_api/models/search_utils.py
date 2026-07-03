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
from ppr_api.models import utils as model_utils

# flake8: noqa Q000,E122,E131
# Disable Q000: Allow query strings to be in double quotation marks that contain single quotation marks.
# Disable E122: allow query strings to be more human readable.
# Disable E131: allow query strings to be more human readable.

GET_DETAIL_DAYS_LIMIT = 7  # Number of days in the past a get details request is allowed.
# Maximum number of days in the past to filter when fetching account search history: set to <= 0 to disable.
GET_HISTORY_DAYS_LIMIT = 14

# Account search history max result set size.
ACCOUNT_SEARCH_HISTORY_MAX_SIZE = 1000
# Maximum number or results returned by search.
SEARCH_RESULTS_MAX_SIZE = 5000

# Result set size limit clause
RESULTS_SIZE_LIMIT_CLAUSE = "FETCH FIRST :max_results_size ROWS ONLY"

# Accoun search filtering, soriting request parameters
FROM_UI_PARAM = "fromUI"
FROM_UI_PARAM2 = "from_ui"
PAGE_NUM_PARAM = "pageNumber"
SORT_DIRECTION_PARAM = "sortDirection"
SORT_CRITERIA_PARAM = "sortCriteriaName"
START_TS_PARAM = "startDateTime"
END_TS_PARAM = "endDateTime"
CLIENT_REF_PARAM = "clientReferenceId"
SEARCH_TS_PARAM = "searchDateTime"
SEARCH_TYPE_PARAM = "type"
SEARCH_CRITERIA_PARAM = "criteria"
USERNAME_PARAM = "username"
SORT_ASCENDING = "ascending"
SORT_DESCENDING = "descending"
ACCOUNT_SORT_DESCENDING = " DESC"
ACCOUNT_SORT_ASCENDING = " ASC"

TO_FILTER_SEARCH_TYPE = {
    "AIRCRAFT_DOT": "AC",
    "BUSINESS_DEBTOR": "BS",
    "INDIVIDUAL_DEBTOR": "IS",
    "MHR_NUMBER": "MH",
    "REGISTRATION_NUMBER": "RG",
    "SERIAL_NUMBER": "SS",
    "MHR_OWNER_NAME": "MI",
    "MHR_ORGANIZATION_NAME": "MO",
    "MHR_MHR_NUMBER": "MM",
    "MHR_SERIAL_NUMBER": "MS",
    "PPR": "PPR",
    "MHR": "MHR",
}
FILTER_SEARCH_TYPE_PPR = "PPR"
FILTER_SEARCH_TYPE_MHR = "MHR"

SEARCH_ORDER_BY_DATE = " ORDER BY search_ts"
SEARCH_ORDER_BY_CLIENT_REF = " ORDER BY client_reference_id"
SEARCH_ORDER_BY_USERNAME = " ORDER BY username"
SEARCH_ORDER_BY_SEARCH_TYPE = " ORDER BY search_type"
SEARCH_ORDER_BY_SEARCH_CRITERIA = " ORDER BY search_criteria"
SEARCH_ORDER_BY_DEFAULT = " ORDER BY search_ts DESC"
SEARCH_FILTER_CLIENT_REF = "  AND position(:query_client_ref in UPPER(client_reference_id)) > 0"
SEARCH_FILTER_USERNAME = " WHERE position(:query_username in UPPER(username)) > 0"
SEARCH_FILTER_DATE = " AND search_ts BETWEEN :query_start AND :query_end"
SEARCH_FILTER_TYPE = " AND search_type = :query_type"
SEARCH_FILTER_TYPE_PPR = " AND search_type NOT IN ('MI', 'MO', 'MM', 'MS')"
SEARCH_FILTER_TYPE_MHR = " AND search_type IN ('MI', 'MO', 'MM', 'MS')"
SEARCH_FILTER_CRITERIA_DEFAULT = " AND position(:query_criteria in search_value) > 0"
QUERY_ACCOUNT_ORDER_BY = {
    SEARCH_TS_PARAM: SEARCH_ORDER_BY_DATE,
    SEARCH_TYPE_PARAM: SEARCH_ORDER_BY_SEARCH_TYPE,
    CLIENT_REF_PARAM: SEARCH_ORDER_BY_CLIENT_REF,
    USERNAME_PARAM: SEARCH_ORDER_BY_USERNAME,
    SEARCH_CRITERIA_PARAM: SEARCH_ORDER_BY_SEARCH_CRITERIA,
}
QUERY_ACCOUNT_FILTER_BY = {
    CLIENT_REF_PARAM: SEARCH_FILTER_CLIENT_REF,
    USERNAME_PARAM: SEARCH_FILTER_USERNAME,
    START_TS_PARAM: SEARCH_FILTER_DATE,
    SEARCH_TYPE_PARAM: SEARCH_FILTER_TYPE,
    SEARCH_CRITERIA_PARAM: SEARCH_FILTER_CRITERIA_DEFAULT,
}


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
MHR_NUM_QUERY = (
    SERIAL_SEARCH_BASE
    + """
   AND sc.serial_type = 'MH' 
   AND sc.mhr_number = (SELECT searchkey_mhr(:query_value)) 
ORDER BY match_type, sc.serial_number ASC, sc.year ASC, r.registration_ts ASC
"""
)

# Equivalent logic as DB view search_by_serial_num_vw, but API determines the where clause.
SERIAL_NUM_QUERY = (
    SERIAL_SEARCH_BASE
    + """
   AND sc.serial_type NOT IN ('AC', 'AF', 'AP')
   AND sc.srch_vin = (SELECT searchkey_vehicle(:query_value)) 
ORDER BY match_type, sc.serial_number ASC, sc.year ASC, r.registration_ts ASC
"""
)

# Equivalent logic as DB view search_by_aircraft_dot_vw, but API determines the where clause.
AIRCRAFT_DOT_QUERY = (
    SERIAL_SEARCH_BASE
    + """
   AND sc.serial_type IN ('AC', 'AF', 'AP')
   AND sc.srch_vin = (SELECT searchkey_aircraft(:query_value)) 
ORDER BY match_type, sc.serial_number ASC, sc.year ASC, r.registration_ts ASC
"""
)

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

MHR_NUM_TOTAL_COUNT = (
    SERIAL_SEARCH_COUNT_BASE + " AND sc.serial_type = 'MH' " + "AND sc.mhr_number = searchkey_mhr(:query_value)"
)

SERIAL_NUM_TOTAL_COUNT = (
    SERIAL_SEARCH_COUNT_BASE
    + " AND sc.serial_type NOT IN ('AC', 'AF') "
    + "AND sc.srch_vin = searchkey_vehicle(:query_value)"
)

AIRCRAFT_DOT_TOTAL_COUNT = (
    SERIAL_SEARCH_COUNT_BASE
    + " AND sc.serial_type IN ('AC', 'AF') "
    + "AND sc.srch_vin = searchkey_aircraft(:query_value)"
)

COUNT_QUERY_FROM_SEARCH_TYPE = {
    "AC": AIRCRAFT_DOT_TOTAL_COUNT,
    "BS": BUSINESS_NAME_TOTAL_COUNT,
    "IS": INDIVIDUAL_NAME_TOTAL_COUNT,
    "MH": MHR_NUM_TOTAL_COUNT,
    "SS": SERIAL_NUM_TOTAL_COUNT,
}

QUERY_ACCOUNT_HISTORY_TOTAL = f"""
SELECT COUNT(sc.id)
FROM search_requests sc, search_results sr
WHERE sc.id = sr.search_id
  AND sc.account_id = :query_account
  AND sc.search_ts > ((now() at time zone 'utc') - interval '{str(GET_HISTORY_DAYS_LIMIT)} days')
  AND NOT EXISTS (SELECT sc2.id
                    FROM search_requests sc2
                   WHERE sc2.id = sc.id
                     AND sc2.search_type IN ('MM', 'MI', 'MO', 'MS')
                     AND sc2.pay_path IS NULL)
"""

ACCOUNT_SEARCH_HISTORY_BASE = f"""
SELECT sc.id, sc.search_ts, sc.api_criteria, sc.total_results_size, sc.returned_results_size,
  (SELECT CASE WHEN sc.search_type IN ('MM', 'MI', 'MO', 'MS') THEN -1
               WHEN sc.updated_selection IS NULL THEN
                    (SELECT COUNT(*) 
                       FROM json_array_elements(sr.api_result) sr2
                      WHERE sr2 ->> 'matchType' = 'EXACT')
               ELSE (SELECT COUNT(*) 
                       FROM json_array_elements(sc.updated_selection) sc2
                      WHERE sc2 ->> 'matchType' = 'EXACT') END) AS exact_match_count,
  sr.similar_match_count, sr.callback_url, sr.doc_storage_url,
  json_array_length(sr.api_result) as selected_match_count,
  (SELECT CASE WHEN sc.user_id IS NULL THEN ''
     ELSE (SELECT CASE WHEN u.lastname IS NOT NULL AND u.firstname IS NOT NULL THEN u.firstname || ' ' || u.lastname 
                       WHEN u.lastname IS NULL AND u.firstname IS NOT NULL THEN u.firstname
                       WHEN u.lastname IS NOT NULL AND u.firstname IS NULL THEN u.lastname
                       ELSE '' END
             FROM users u WHERE u.username = sc.user_id FETCH FIRST 1 ROWS ONLY)
      END) AS username,
  sr.api_result, sc.user_id, sr.score, sc.pay_invoice_id,
  sc.search_type, sc.client_reference_id,
  CASE WHEN sc.search_type = 'BS' THEN UPPER(api_criteria -> 'criteria' -> 'debtorName' ->> 'business')
       WHEN sc.search_type = 'IS' THEN concat(UPPER(api_criteria -> 'criteria' -> 'debtorName' ->> 'last'),
                                              ' ',
                                              UPPER(api_criteria -> 'criteria' -> 'debtorName' ->> 'first'))
       WHEN sc.search_type = 'MI' THEN concat(UPPER(api_criteria -> 'criteria' -> 'ownerName' ->> 'last'),
                                              ' ',
                                              UPPER(api_criteria -> 'criteria' -> 'ownerName' ->> 'first'))
       ELSE UPPER(api_criteria -> 'criteria' ->> 'value') END as search_criteria
FROM search_requests sc, search_results sr
WHERE sc.id = sr.search_id
  AND sc.account_id = :query_account
  AND sc.search_ts > ((now() at time zone 'utc') - interval '{str(GET_HISTORY_DAYS_LIMIT)} days')
  AND NOT EXISTS (SELECT sc2.id
                    FROM search_requests sc2
                   WHERE sc2.id = sc.id
                     AND sc2.search_type IN ('MM', 'MI', 'MO', 'MS')
                     AND sc2.pay_path IS NULL)
"""

ACCOUNT_SEARCH_HISTORY_DATE_QUERY = (
    ACCOUNT_SEARCH_HISTORY_BASE
    + f""" AND sc.search_ts > ((now() at time zone 'utc') - interval '{str(GET_HISTORY_DAYS_LIMIT)} days')
 ORDER BY sc.search_ts DESC 
"""
)

ACCOUNT_SEARCH_HISTORY_QUERY = ACCOUNT_SEARCH_HISTORY_BASE + " ORDER BY sc.search_ts DESC "

ACCOUNT_SEARCH_HISTORY_DATE_QUERY_NEW = ACCOUNT_SEARCH_HISTORY_DATE_QUERY

ACCOUNT_SEARCH_HISTORY_QUERY_NEW = ACCOUNT_SEARCH_HISTORY_QUERY

QUERY_ACCOUNT_HISTORY_LIMIT = " LIMIT :page_size OFFSET :page_offset"


def format_mhr_number(request_json):
    """Trim and pad with zeroes search query mhr number query."""
    mhr_num: str = request_json["criteria"]["value"]
    mhr_num = mhr_num.strip().rjust(6, "0")
    request_json["criteria"]["value"] = mhr_num


class AccountSearchParams:
    """Contains parameter values to use when querying account summary search history information."""

    account_id: str
    sbc_staff: bool = False
    from_ui: bool = False
    sort_direction: str = SORT_DESCENDING
    page_number: int = 1
    sort_criteria: str = None
    filter_search_criteria: str = None
    filter_search_type: str = None
    filter_client_reference_id: str = None
    filter_username: str = None
    filter_start_date: str = None
    filter_end_date: str = None
    filter_last_name: str = None
    filter_first_name: str = None

    def __init__(self, account_id, sbc_staff: bool = False):
        """Set common base initialization."""
        self.account_id = account_id
        self.sbc_staff = sbc_staff

    def has_sort(self) -> bool:
        """Check if sort criteria provided."""
        if self.sort_criteria:
            if self.sort_criteria in (
                SEARCH_TS_PARAM,
                SEARCH_TYPE_PARAM,
                SEARCH_CRITERIA_PARAM,
                USERNAME_PARAM,
                CLIENT_REF_PARAM,
            ):
                return True
        return False

    def has_filter(self) -> bool:
        """Check if filter criteria provided."""
        return (
            self.filter_client_reference_id
            or self.filter_search_criteria
            or self.filter_search_type
            or self.filter_start_date
            or self.filter_username
        )

    def get_filter_values(self):  # pylint: disable=too-many-return-statements
        """Provide optional filter name and value if available."""
        if self.filter_search_type:
            return SEARCH_TYPE_PARAM, self.filter_search_type
        if self.filter_start_date:
            return START_TS_PARAM, self.filter_start_date
        if self.filter_search_criteria:
            return SEARCH_CRITERIA_PARAM, self.filter_search_criteria
        if self.filter_client_reference_id:
            return CLIENT_REF_PARAM, self.filter_client_reference_id
        if self.filter_username:
            return USERNAME_PARAM, self.filter_username
        return None, None

    def get_page_size(self) -> int:
        """Provide account registrations query page size."""
        return ACCOUNT_SEARCH_HISTORY_MAX_SIZE

    def get_page_offset(self) -> int:
        """Provide account registrations query page offset."""
        page_offset: int = self.page_number
        if page_offset <= 1:
            return 0
        return (page_offset - 1) * self.get_page_size()


def get_multiple_filters(params: AccountSearchParams) -> dict:
    """Build the list of all applied filters as a key/value dictionary."""
    filters = []
    if params.filter_search_type:
        filters.append(("type", params.filter_search_type))
    if params.filter_start_date and params.filter_end_date:
        filters.append(("startDateTime", params.filter_start_date))
    if params.filter_search_criteria:
        filters.append(("criteria", params.filter_search_criteria))
    if params.filter_client_reference_id:
        filters.append(("clientReferenceId", params.filter_client_reference_id))
    if params.filter_username:
        filters.append(("username", params.filter_username))
    if filters:
        return filters
    return None


def build_account_query_filter(query_text: str, params: AccountSearchParams) -> str:
    """Build the account search history summary query filter clause."""
    if not params.has_filter():
        return query_text
    filter_clause: str = ""
    # Get all selected filters and loop through, applying them
    filters = get_multiple_filters(params)
    for query_filter in filters:
        filter_type = query_filter[0]
        filter_value = query_filter[1]
        if filter_type and filter_value:
            if filter_type == SEARCH_TYPE_PARAM:
                if filter_value == FILTER_SEARCH_TYPE_MHR:
                    filter_clause = SEARCH_FILTER_TYPE_MHR
                elif filter_value == FILTER_SEARCH_TYPE_PPR:
                    filter_clause = SEARCH_FILTER_TYPE_PPR
                else:
                    filter_clause = QUERY_ACCOUNT_FILTER_BY.get(filter_type)
            elif filter_type != "username":
                filter_clause = QUERY_ACCOUNT_FILTER_BY.get(filter_type)
            if filter_clause:
                query_text += filter_clause
    base_query: str = f"SELECT * FROM ({query_text}) AS q "
    if params.filter_username:
        base_query += SEARCH_FILTER_USERNAME
    return base_query


def get_account_query_order(params: AccountSearchParams) -> str:
    """Build the account search history summary query order by clause."""
    order_clause: str = ""
    if params.has_sort():
        order_clause = QUERY_ACCOUNT_ORDER_BY.get(params.sort_criteria)
        if params.sort_direction and params.sort_direction == SORT_ASCENDING:
            order_clause += ACCOUNT_SORT_ASCENDING
        else:
            order_clause += ACCOUNT_SORT_DESCENDING
    else:  # Default sort order if filter but no sorting specified.
        order_clause += SEARCH_ORDER_BY_DEFAULT
    return order_clause


def build_search_history_query(params: AccountSearchParams) -> str:
    """Build the account search history query based on the request parameters."""
    if not params.has_filter() and not params.has_sort():
        query: str = ACCOUNT_SEARCH_HISTORY_DATE_QUERY_NEW
        if GET_HISTORY_DAYS_LIMIT <= 0:
            query = ACCOUNT_SEARCH_HISTORY_QUERY_NEW
        query += QUERY_ACCOUNT_HISTORY_LIMIT
        return query
    query_text: str = ACCOUNT_SEARCH_HISTORY_BASE
    if params.has_filter():
        query_text = build_account_query_filter(query_text, params)
    query_text += get_account_query_order(params)
    return query_text + QUERY_ACCOUNT_HISTORY_LIMIT


def build_account_query_params(
    params: AccountSearchParams,
) -> dict:
    """Build the account query runtime parameter set from the provided parameters."""
    page_offset: int = params.page_number
    page_size: int = params.get_page_size()
    if page_offset <= 1:
        page_offset = 0
    else:
        page_offset = (page_offset - 1) * page_size
    query_params = {"query_account": params.account_id, "page_size": page_size, "page_offset": page_offset}
    if params.has_filter():
        if params.filter_start_date and params.filter_end_date:
            start_ts = model_utils.search_ts(params.filter_start_date, True)
            end_ts = model_utils.search_ts(params.filter_end_date, False)
            # logger.info(f'start_ts={start_ts} end_ts={end_ts}')
            query_params["query_start"] = start_ts
            query_params["query_end"] = end_ts
        if params.filter_search_type and params.filter_search_type not in (
            FILTER_SEARCH_TYPE_PPR,
            FILTER_SEARCH_TYPE_MHR,
        ):
            query_params["query_type"] = params.filter_search_type
        if params.filter_username:
            query_params["query_username"] = params.filter_username
        if params.filter_client_reference_id:
            query_params["query_client_ref"] = params.filter_client_reference_id
        if params.filter_search_criteria:
            query_params["query_criteria"] = params.filter_search_criteria
    return query_params
