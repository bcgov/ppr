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
"""Model helper utilities for processing requests.

Common constants used across models and utilities for mapping type codes
between the API and the database in both directions.
"""
from datetime import date  # noqa: F401 pylint: disable=unused-import
from datetime import datetime as _datetime
from datetime import time, timedelta, timezone

import pytz
from datedelta import datedelta
from flask import current_app


# Local timzone
LOCAL_TZ = pytz.timezone('America/Los_Angeles')

# API draft types
DRAFT_TYPE_AMENDMENT = 'AMENDMENT_STATEMENT'
DRAFT_TYPE_CHANGE = 'CHANGE_STATEMENT'
DRAFT_TYPE_FINANCING = 'FINANCING_STATEMENT'

# DB party types
PARTY_DEBTOR_BUS = 'DB'
PARTY_DEBTOR_IND = 'DI'
PARTY_REGISTERING = 'RG'
PARTY_SECURED = 'SP'

# DB registration class types
REG_CLASS_AMEND = 'AMENDMENT'
REG_CLASS_AMEND_COURT = 'COURTORDER'
REG_CLASS_CHANGE = 'CHANGE'
REG_CLASS_CROWN = 'CROWNLIEN'
REG_CLASS_DISCHARGE = 'DISCHARGE'
REG_CLASS_FINANCING = 'PPSALIEN'
REG_CLASS_MISC = 'MISCLIEN'
REG_CLASS_PPSA = 'PPSALIEN'
REG_CLASS_RENEWAL = 'RENEWAL'

# DB registration types
REG_TYPE_AMEND = 'AM'
REG_TYPE_AMEND_COURT = 'CO'
REG_TYPE_DISCHARGE = 'DC'
REG_TYPE_RENEWAL = 'RE'
REG_TYPE_REPAIRER_LIEN = 'RL'
REG_TYPE_MARRIAGE_SEPARATION = 'FR'
REG_TYPE_LAND_TAX_MH = 'LT'
REG_TYPE_TAX_MH = 'MH'
REG_TYPE_OTHER = 'OT'
REG_TYPE_SECURITY_AGREEMENT = 'SA'
# New amendment change types
REG_TYPE_AMEND_ADDITION_COLLATERAL = 'AA'
REG_TYPE_AMEND_DEBTOR_RELEASE = 'AR'
REG_TYPE_AMEND_DEBTOR_TRANSFER = 'AD'
REG_TYPE_AMEND_PARIAL_DISCHARGE = 'AP'
REG_TYPE_AMEND_SP_TRANSFER = 'AS'
REG_TYPE_AMEND_SUBSTITUTION_COLLATERAL = 'AU'

SEARCH_MATCH_EXACT = 'EXACT'
SEARCH_MATCH_SIMILAR = 'SIMILAR'

# DB state types
STATE_DISCHARGED = 'HDC'
STATE_ACTIVE = 'ACT'
STATE_EXPIRED = 'HEX'

# Financing statement, registraiton constants
LIFE_INFINITE = 99
REPAIRER_LIEN_DAYS = 180
REPAIRER_LIEN_YEARS = 0
MAX_ACCOUNT_REGISTRATIONS_DEFAULT = 1000  # Use when not paging.

# Legacy registration types not allowed with new financing statements.
REG_TYPE_NEW_FINANCING_EXCLUDED = {
    'SS': 'SS',
    'MR': 'MR',
    'CC': 'CC',
    'DP': 'DP',
    'HR': 'HR',
    'MI': 'MI',
}

# Mapping from API draft type to DB registration class
DRAFT_TYPE_TO_REG_CLASS = {
    'AMENDMENT_STATEMENT': 'AMENDMENT',
    'CHANGE_STATEMENT': 'CHANGE',
    'FINANCING_STATEMENT': 'PPSALIEN'
}

# Mapping from DB registration class to API draft type
REG_CLASS_TO_DRAFT_TYPE = {
    'AMENDMENT': 'AMENDMENT_STATEMENT',
    'COURTORDER': 'AMENDMENT_STATEMENT',
    'CHANGE': 'CHANGE_STATEMENT',
    'CROWNIEN': 'FINANCING_STATEMENT',
    'MISCLIEN': 'FINANCING_STATEMENT',
    'PPSALIEN': 'FINANCING_STATEMENT'
}

# Mapping from DB registration class to API statement type
REG_CLASS_TO_STATEMENT_TYPE = {
    'AMENDMENT': 'AMENDMENT_STATEMENT',
    'COURTORDER': 'AMENDMENT_STATEMENT',
    'CROWNLIEN': 'FINANCING_STATEMENT',
    'CHANGE': 'CHANGE_STATEMENT',
    'RENEWAL': 'RENEWAL_STATEMENT',
    'DISCHARGE': 'DISCHARGE_STATEMENT',
    'MISCLIEN': 'FINANCING_STATEMENT',
    'PPSALIEN': 'FINANCING_STATEMENT'
}

# Default mapping from registration class to registration type
REG_CLASS_TO_REG_TYPE = {
    'AMENDMENT': 'AM',
    'COURTORDER': 'CO',
    'DISCHARGE': 'DC',
    'RENEWAL': 'RE'
}

# Mapping from registration type to registration class
REG_TYPE_TO_REG_CLASS = {
    'AM': 'AMENDMENT',
    'AA': 'AMENDMENT',
    'AR': 'AMENDMENT',
    'AD': 'AMENDMENT',
    'AP': 'AMENDMENT',
    'AS': 'AMENDMENT',
    'AU': 'AMENDMENT',
    'CO': 'COURTORDER',
    'AC': 'CHANGE',
    'DR': 'CHANGE',
    'DT': 'CHANGE',
    'PD': 'CHANGE',
    'ST': 'CHANGE',
    'SU': 'CHANGE',
    'CC': 'CROWNLIEN',
    'CT': 'CROWNLIEN',
    'DP': 'CROWNLIEN',
    'ET': 'CROWNLIEN',
    'FO': 'CROWNLIEN',
    'FT': 'CROWNLIEN',
    'HR': 'CROWNLIEN',
    'IP': 'CROWNLIEN',
    'IT': 'CROWNLIEN',
    'LO': 'CROWNLIEN',
    'MD': 'CROWNLIEN',
    'MI': 'CROWNLIEN',
    'MR': 'CROWNLIEN',
    'OT': 'CROWNLIEN',
    'PG': 'CROWNLIEN',
    'PS': 'CROWNLIEN',
    'PT': 'CROWNLIEN',
    'RA': 'CROWNLIEN',
    'SC': 'CROWNLIEN',
    'SS': 'CROWNLIEN',
    'TL': 'CROWNLIEN',
    'DC': 'DISCHARGE',
    'HN': 'MISCLIEN',
    'ML': 'MISCLIEN',
    'MN': 'MISCLIEN',
    'PN': 'MISCLIEN',
    'WL': 'MISCLIEN',
    'FA': 'PPSALIEN',
    'FL': 'PPSALIEN',
    'FR': 'PPSALIEN',
    'FS': 'PPSALIEN',
    'LT': 'PPSALIEN',
    'MH': 'PPSALIEN',
    'RL': 'PPSALIEN',
    'SA': 'PPSALIEN',
    'SG': 'PPSALIEN',
    'TA': 'PPSALIEN',
    'TF': 'PPSALIEN',
    'TG': 'PPSALIEN',
    'TM': 'PPSALIEN',
    'RE': 'RENEWAL'
}

# Map from API search type to DB search type
TO_DB_SEARCH_TYPE = {
    'AIRCRAFT_DOT': 'AC',
    'BUSINESS_DEBTOR': 'BS',
    'INDIVIDUAL_DEBTOR': 'IS',
    'MHR_NUMBER': 'MH',
    'REGISTRATION_NUMBER': 'RG',
    'SERIAL_NUMBER': 'SS'
}

# Account financing statement/registration list queries.
QUERY_ACCOUNT_FINANCING_STATEMENTS = """
SELECT r.id, r.registration_number, r.registration_ts, r.registration_type, r.registration_type_cl,
       rt.registration_desc, r.base_reg_number, fs.state_type AS state,
       CASE WHEN fs.life = 99 THEN -99
            ELSE CAST(EXTRACT(day from (fs.expire_date - (now() at time zone 'utc'))) AS INT) END expire_days,
       (SELECT MAX(r2.registration_ts)
          FROM registrations r2
         WHERE r2.financing_id = r.financing_id) AS last_update_ts,
       (SELECT CASE WHEN p.business_name IS NOT NULL THEN p.business_name
                    WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)
                    ELSE p.first_name || ' ' || p.last_name END
          FROM parties p
         WHERE p.registration_id = r.id
           AND p.party_type = 'RG') AS registering_party,
       (SELECT string_agg((CASE WHEN p.business_name IS NOT NULL THEN p.business_name
                                WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)
                                ELSE p.first_name || ' ' || p.last_name END), ', ')
          FROM parties p
         WHERE p.financing_id = fs.id
           AND p.registration_id_end IS NULL
           AND p.party_type = 'SP') AS secured_party,
       r.client_reference_id,
       (SELECT CASE WHEN r.user_id IS NULL THEN ''
                    ELSE (SELECT u.firstname || ' ' || u.lastname
                            FROM users u
                           WHERE u.username = r.user_id) END) AS registering_name
  FROM registrations r, registration_types rt, financing_statements fs
 WHERE r.registration_type = rt.registration_type
   AND fs.id = r.financing_id
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN')
   AND (r.account_id = :query_account OR r.id IN (SELECT r2.id
                                                    FROM user_extra_registrations uer, registrations r2
                                                   WHERE uer.registration_number = r2.registration_number
                                                     AND uer.account_id = :query_account))
   AND (fs.expire_date IS NULL OR fs.expire_date > ((now() at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
ORDER BY r.registration_ts DESC
FETCH FIRST :max_results_size ROWS ONLY
"""

QUERY_ACCOUNT_REGISTRATIONS = """
WITH q AS (
  SELECT (TO_TIMESTAMP(TO_CHAR(current_date, 'YYYY-MM-DD') || ' 23:59:59', 'YYYY-MM-DD HH24:MI:SS') at time zone 'utc')
      AS current_expire_ts
)
SELECT r.registration_number, r.registration_ts, r.registration_type, r.registration_type_cl, r.account_id,
       rt.registration_desc, r.base_reg_number, fs.state_type AS state,
       CASE WHEN fs.life = 99 THEN -99
            ELSE CAST(EXTRACT(day from ((fs.expire_date at time zone 'utc') - current_expire_ts)) AS INT)
            END expire_days,
       (SELECT MAX(r2.registration_ts)
          FROM registrations r2
         WHERE r2.financing_id = r.financing_id) AS last_update_ts,
       (SELECT CASE WHEN p.business_name IS NOT NULL THEN p.business_name
                    WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)
                    ELSE p.first_name || ' ' || p.last_name END
          FROM parties p
         WHERE p.registration_id = r.id
           AND p.party_type = 'RG') AS registering_party,
       (SELECT string_agg((CASE WHEN p.business_name IS NOT NULL THEN p.business_name
                                WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)
                                ELSE p.first_name || ' ' || p.last_name END), ', ')
          FROM parties p
         WHERE p.financing_id = fs.id
           AND p.registration_id_end IS NULL
           AND p.party_type = 'SP') AS secured_party,
       r.client_reference_id,
       (SELECT CASE WHEN r.user_id IS NULL THEN ''
                    ELSE (SELECT u.firstname || ' ' || u.lastname
                            FROM users u
                           WHERE u.username = r.user_id) END) AS registering_name,
      (SELECT COUNT(id)
         FROM user_extra_registrations uer
        WHERE uer.registration_number = r.registration_number
          AND uer.account_id = r.account_id
          AND uer.removed_ind = 'Y') AS removed_count
  FROM registrations r, registration_types rt, financing_statements fs, q
 WHERE r.registration_type = rt.registration_type
   AND fs.id = r.financing_id
   AND fs.id IN (SELECT fs2.id
                   FROM financing_statements fs2, registrations r2
                  WHERE fs2.id = r2.financing_id
                    AND r2.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')
                    AND r2.account_id = :query_account)
   AND (fs.expire_date IS NULL OR fs.expire_date > ((now() at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
  AND NOT EXISTS (SELECT r2.financing_id
                    FROM user_extra_registrations uer, registrations r2
                   WHERE uer.account_id = :query_account
                     AND uer.registration_number = r2.registration_number
                     AND r2.financing_id = r.financing_id
                     AND uer.removed_ind = 'Y')
UNION (
SELECT r.registration_number, r.registration_ts, r.registration_type, r.registration_type_cl, r.account_id,
       rt.registration_desc, r.base_reg_number, fs.state_type AS state,
       CASE WHEN fs.life = 99 THEN -99
            ELSE CAST(EXTRACT(day from ((fs.expire_date at time zone 'utc') - current_expire_ts)) AS INT)
            END expire_days,
       (SELECT MAX(r2.registration_ts)
          FROM registrations r2
         WHERE r2.financing_id = r.financing_id) AS last_update_ts,
       (SELECT CASE WHEN p.business_name IS NOT NULL THEN p.business_name
                    WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)
                    ELSE p.first_name || ' ' || p.last_name END
          FROM parties p
         WHERE p.registration_id = r.id
           AND p.party_type = 'RG') AS registering_party,
       (SELECT string_agg((CASE WHEN p.business_name IS NOT NULL THEN p.business_name
                                WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)
                                ELSE p.first_name || ' ' || p.last_name END), ', ')
          FROM parties p
         WHERE p.financing_id = fs.id
           AND p.registration_id_end IS NULL
           AND p.party_type = 'SP') AS secured_party,
       r.client_reference_id,
       (SELECT CASE WHEN r.user_id IS NULL THEN ''
                    ELSE (SELECT u.firstname || ' ' || u.lastname
                            FROM users u
                           WHERE u.username = r.user_id) END) AS registering_name,
       0 AS removed_count
  FROM registrations r, registration_types rt, financing_statements fs, q
 WHERE r.registration_type = rt.registration_type
   AND fs.id = r.financing_id
   AND fs.id IN (SELECT fs2.id
                   FROM financing_statements fs2, registrations r2
                  WHERE fs2.id = r2.financing_id
                    AND r2.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')
                    AND r2.registration_number IN (SELECT uer.registration_number
                                                      FROM user_extra_registrations uer
                                                     WHERE uer.account_id = :query_account
                                                       AND uer.removed_ind IS NULL))
   AND (fs.expire_date IS NULL OR fs.expire_date > ((now() at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
)
ORDER BY registration_ts DESC
FETCH FIRST :max_results_size ROWS ONLY
"""

QUERY_ACCOUNT_ADD_REGISTRATION = """
SELECT r.registration_number, r.registration_ts, r.registration_type, r.registration_type_cl,
       rt.registration_desc, r.base_reg_number, fs.state_type AS state,
       CASE WHEN fs.life = 99 THEN -99
            ELSE CAST(EXTRACT(day from (fs.expire_date - (now() at time zone 'utc'))) AS INT) END expire_days,
       (SELECT MAX(r2.registration_ts)
          FROM registrations r2
         WHERE r2.financing_id = r.financing_id) AS last_update_ts,
       (SELECT CASE WHEN p.business_name IS NOT NULL THEN p.business_name
                    WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)
                    ELSE p.first_name || ' ' || p.last_name END
          FROM parties p
         WHERE p.registration_id = r.id
           AND p.party_type = 'RG') AS registering_party,
       (SELECT string_agg((CASE WHEN p.business_name IS NOT NULL THEN p.business_name
                                WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)
                                ELSE p.first_name || ' ' || p.last_name END), ', ')
          FROM parties p
         WHERE p.financing_id = fs.id
           AND p.registration_id_end IS NULL
           AND p.party_type = 'SP') AS secured_party,
       r.client_reference_id,
       (SELECT CASE WHEN r.user_id IS NULL THEN ''
                    ELSE (SELECT u.firstname || ' ' || u.lastname
                            FROM users u
                           WHERE u.username = r.user_id) END) AS registering_name,
       r.account_id,
       (SELECT COUNT(uer.id)
          FROM user_extra_registrations uer
         WHERE uer.account_id = :query_account
           AND (uer.registration_number = :query_reg_num OR
                uer.registration_number = r.registration_number)) AS exists_count
  FROM registrations r, registration_types rt, financing_statements fs
 WHERE r.registration_type = rt.registration_type
   AND fs.id = r.financing_id
   AND fs.id IN (SELECT fs2.id
                   FROM financing_statements fs2, registrations r2
                  WHERE fs2.id = r2.financing_id
                    AND r2.registration_number = :query_reg_num)
   AND (fs.expire_date IS NULL OR fs.expire_date > ((now() at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
ORDER BY r.registration_ts DESC
"""

QUERY_ACCOUNT_DRAFTS_LIMIT = " FETCH FIRST :max_results_size ROWS ONLY"
QUERY_ACCOUNT_DRAFTS_DEFAULT_ORDER = " ORDER BY create_ts DESC"
QUERY_ACCOUNT_DRAFTS_DOC_NUM_CLAUSE = " AND document_number LIKE :doc_num || '%'"
QUERY_ACCOUNT_DRAFTS_CLIENT_REF_CLAUSE = " AND client_reference_id LIKE :client_reference_id || '%'"
QUERY_ACCOUNT_DRAFTS_REG_NAME_CLAUSE = " AND registering_name LIKE :registering_name || '%'"
QUERY_ACCOUNT_DRAFTS_REG_TYPE_CLAUSE = ' AND registration_type = :registration_type'
QUERY_ACCOUNT_DRAFTS_DATE_CLAUSE = """
 AND create_ts BETWEEN (TO_TIMESTAMP(:start_date_time, 'YYYY-MM-DD HH24:MI:SS') at time zone 'utc') AND
                       (TO_TIMESTAMP(:end_date_time, 'YYYY-MM-DD HH24:MI:SS') at time zone 'utc')
 """

QUERY_ACCOUNT_DRAFTS_BASE = """
SELECT d.document_number, d.create_ts, d.registration_type, d.registration_type_cl, rt.registration_desc,
       CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') THEN ''
            ELSE d.registration_number END base_reg_num,
       d.draft ->> 'type' AS draft_type,
       CASE WHEN d.update_ts IS NOT NULL THEN d.update_ts ELSE d.create_ts END last_update_ts,
       CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') THEN
                 d.draft -> 'financingStatement' ->> 'clientReferenceId'
            WHEN d.registration_type_cl = 'AMENDMENT' THEN d.draft -> 'amendmentStatement' ->> 'clientReferenceId'
            WHEN d.registration_type_cl = 'CHANGE' THEN d.draft -> 'changeStatement' ->> 'clientReferenceId'
            ELSE '' END client_reference_id,
       CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') AND
                 d.draft -> 'financingStatement' -> 'registeringParty' IS NOT NULL THEN
                 CASE WHEN d.draft -> 'financingStatement' -> 'registeringParty' -> 'businessName' IS NOT NULL THEN
                           d.draft -> 'financingStatement' -> 'registeringParty' ->> 'businessName'
                      WHEN d.draft -> 'financingStatement' -> 'registeringParty' ->> 'personName' IS NOT NULL THEN
                      concat(d.draft -> 'financingStatement' -> 'registeringParty' -> 'personName' ->> 'first', ' ',
                             d.draft -> 'financingStatement' -> 'registeringParty' -> 'personName' ->> 'last')
                 END
            WHEN d.registration_type_cl = 'AMENDMENT' AND
                 (d.draft -> 'amendmentStatement' -> 'registeringParty') IS NOT NULL THEN
                 CASE WHEN d.draft -> 'amendmentStatement' -> 'registeringParty' -> 'businessName' IS NOT NULL THEN
                           d.draft -> 'amendmentStatement' -> 'registeringParty' ->> 'businessName'
                      WHEN d.draft -> 'amendmentStatement' -> 'registeringParty' -> 'personName' IS NOT NULL THEN
                        concat(d.draft -> 'amendmentStatement' -> 'registeringParty' -> 'personName' ->> 'first', ' ',
                               d.draft -> 'amendmentStatement' -> 'registeringParty' -> 'personName' ->> 'last')
                 END
            ELSE '' END registering_party,
      CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') AND
                 d.draft -> 'financingStatement' -> 'securedParties' IS NOT NULL THEN
                (SELECT string_agg((CASE WHEN (sp -> 'businessName') IS NOT NULL THEN
                                             (sp ->> 'businessName')
                                         WHEN sp -> 'personName' IS NOT NULL THEN
                                            concat((sp -> 'personName' ->> 'first'), ' ',
                                                   (sp -> 'personName' ->> 'last'))
                                         END),
                                   ',')
                   FROM json_array_elements(d.draft -> 'financingStatement' -> 'securedParties') sp)
          WHEN d.registration_type_cl = 'AMENDMENT' AND
                 d.draft -> 'amendmentStatement' -> 'securedParties' IS NOT NULL THEN
                (SELECT string_agg((CASE WHEN (sp2 -> 'businessName') IS NOT NULL THEN
                                             (sp2 ->> 'businessName')
                                         WHEN sp2 -> 'personName' IS NOT NULL THEN
                                            concat((sp2 -> 'personName' ->> 'first'), ' ',
                                                   (sp2 -> 'personName' ->> 'last'))
                                         END),
                                   ',')
                   FROM json_array_elements(d.draft -> 'amendmentStatement' -> 'securedParties') sp2)
            ELSE ' ' END secured_party,
       (SELECT CASE WHEN d.user_id IS NULL THEN ''
                    ELSE (SELECT u.firstname || ' ' || u.lastname
                            FROM users u
                           WHERE u.username = d.user_id) END) AS registering_name, d.account_id
  FROM drafts d, registration_types rt
 WHERE d.account_id = :query_account
   AND d.registration_type = rt.registration_type
   AND NOT EXISTS (SELECT r.draft_id FROM registrations r WHERE r.draft_id = d.id)
   AND NOT EXISTS (SELECT uer.id
                     FROM user_extra_registrations uer
                    WHERE uer.registration_number = d.registration_number
                      AND uer.account_id = d.account_id
                      AND uer.removed_ind = 'Y')
"""

QUERY_ACCOUNT_DRAFTS_FILTER = 'SELECT * FROM (' + QUERY_ACCOUNT_DRAFTS_BASE + ') AS q WHERE account_id = :query_account'
QUERY_ACCOUNT_DRAFTS = QUERY_ACCOUNT_DRAFTS_BASE + QUERY_ACCOUNT_DRAFTS_DEFAULT_ORDER + QUERY_ACCOUNT_DRAFTS_LIMIT

QUERY_ACCOUNT_REG_TOTAL = """
SELECT COUNT(registration_id) AS reg_count
  FROM account_registration_vw
 WHERE account_id = :query_account
   AND registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')
"""

QUERY_ACCOUNT_BASE_REG_BASE = """
SELECT registration_number, registration_ts, registration_type, registration_type_cl, account_id,
       registration_desc, base_reg_number, state, expire_days, last_update_ts, registering_party,
       secured_party, client_reference_id, registering_name, orig_account_id, pending_count, vehicle_count
  FROM account_registration_vw arv
 WHERE arv.account_id = :query_account
   AND arv.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')
"""

QUERY_ACCOUNT_BASE_REG_SUBQUERY = """
SELECT arv.financing_id
  FROM account_registration_vw arv
 WHERE (arv.account_id = :query_account OR arv.base_account_id = :query_account)
"""

QUERY_ACCOUNT_BASE_REG_FILTER = """
SELECT * FROM (
SELECT registration_number, registration_ts, registration_type, registration_type_cl, account_id,
       registration_desc, base_reg_number, state, expire_days, last_update_ts, registering_party,
       secured_party, client_reference_id, registering_name, orig_account_id, pending_count, vehicle_count
  FROM account_registration_vw arv1
 WHERE arv1.account_id = :query_account
   AND arv1.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')
   AND arv1.financing_id IN
    (
        QUERY_ACCOUNT_BASE_REG_SUBQUERY
    )
 ) AS q
"""

QUERY_ACCOUNT_CHANGE_REG_BASE = """
SELECT arv2.financing_id
  FROM account_registration_vw arv2
 WHERE arv2.account_id = :query_account
"""

QUERY_ACCOUNT_CHANGE_REG = """
SELECT registration_number, registration_ts, registration_type, registration_type_cl, account_id,
       registration_desc, base_reg_number, state, expire_days, last_update_ts, registering_party,
       secured_party, client_reference_id, registering_name, orig_account_id, pending_count, vehicle_count
  FROM account_registration_vw
 WHERE registration_type_cl NOT IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')
   AND (account_id = :query_account OR base_account_id = :query_account)
   AND financing_id IN (QUERY_ACCOUNT_CHANGE_REG_BASE)
ORDER BY registration_ts DESC
"""

QUERY_ACCOUNT_CHANGE_REG_FILTER = """
SELECT registration_number, registration_ts, registration_type, registration_type_cl, account_id,
       registration_desc, base_reg_number, state, expire_days, last_update_ts, registering_party,
       secured_party, client_reference_id, registering_name, orig_account_id, pending_count, vehicle_count
  FROM account_registration_vw
 WHERE registration_type_cl NOT IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')
   AND (account_id = :query_account OR base_account_id = :query_account)
   AND base_reg_number IN (BASE_REG_LIST)
ORDER BY registration_ts DESC
"""

# Error messages
ERR_FINANCING_NOT_FOUND = '{code}: no Financing Statement found for registration number {registration_num}.'
ERR_REGISTRATION_NOT_FOUND = '{code}: no registration found for registration number {registration_num}.'
ERR_FINANCING_HISTORICAL = \
    '{code}: the Financing Statement for registration number {registration_num} has expired or been discharged.'
ERR_REGISTRATION_ACCOUNT = '{code}: the account ID {account_id} does not match registration number {registration_num}.'
ERR_REGISTRATION_MISMATCH = \
    '{code}: the registration {registration_num} does not match the Financing Statement registration {base_reg_num}.'
ERR_DRAFT_NOT_FOUND = '{code}: no Draft Statement found for Document ID {document_number}.'
ERR_DRAFT_USED = '{code}: Draft Statement for Document ID {document_number} has been used.'
ERR_SEARCH_TOO_OLD = '{code}: search get details search ID {search_id} timestamp too old: must be after {min_ts}.'
ERR_SEARCH_COMPLETE = '{code}: search select results failed: results already provided for search ID {search_id}.'
ERR_SEARCH_NOT_FOUND = '{code}: search select results failed: invalid search ID {search_id}.'

SEARCH_RESULTS_DOC_NAME = 'search-results-report-{search_id}.pdf'


def get_max_registrations_size():
    """Get the configurable results maximum size for account registrations."""
    return int(current_app.config.get('ACCOUNT_REGISTRATIONS_MAX_RESULTS'))


def format_ts(time_stamp):
    """Build a UTC ISO 8601 date and time string with no microseconds."""
    formatted_ts = None
    if time_stamp:
        formatted_ts = time_stamp.replace(tzinfo=timezone.utc).replace(microsecond=0).isoformat()

    return formatted_ts


def now_ts():
    """Create a timestamp representing the current date and time in the UTC time zone."""
    return _datetime.now(timezone.utc)


def now_ts_offset(offset_days: int = 1, add: bool = False):
    """Create a timestamp representing the current date and time adjusted by offset number of days."""
    now = now_ts()
    if add:
        return now + timedelta(days=offset_days)

    return now - timedelta(days=offset_days)


def today_ts_offset(offset_days: int = 1, add: bool = False):
    """Create a timestamp representing the current date at 00:00:00 adjusted by offset number of days."""
    today = date.today()
    day_time = time(0, 0, 0, tzinfo=timezone.utc)
    today_ts = _datetime.combine(today, day_time)
    if add:
        return today_ts + timedelta(days=offset_days)

    return today_ts - timedelta(days=offset_days)


def expiry_dt_from_years(life_years: int, iso_date: str = None):
    """Create a date representing the date at 23:59:59 local time as UTC.

    Adjusted by the life_years number of years in the future. Current date if no iso_date
    """
    # Naive date
    today = None
    if iso_date:
        today = date.fromisoformat(iso_date[:10])
    else:
        today = now_ts().astimezone(LOCAL_TZ)
    # Add years
    future_date = date((today.year + life_years), today.month, today.day)
    # Naive time
    expiry_time = time(23, 59, 59, tzinfo=None)
    # Explicitly set to local timezone which will adjust for daylight savings.
    local_ts = LOCAL_TZ.localize(_datetime.combine(future_date, expiry_time))
    # Return as UTC
    return _datetime.utcfromtimestamp(local_ts.timestamp()).replace(tzinfo=timezone.utc)


def expiry_dt_repairer_lien(expiry_ts: _datetime = None):
    """Create a date representing the date at 23:59:59 local time as UTC from the current expiry date."""
    if not expiry_ts:
        # Naive date
        today = now_ts().astimezone(LOCAL_TZ)
        # base_date = date.today()
        base_date = date(today.year, today.month, today.day)
        # Naive time
        expiry_time = time(23, 59, 59, tzinfo=None)
        future_ts = _datetime.combine(base_date, expiry_time) + timedelta(days=REPAIRER_LIEN_DAYS)
        # Explicitly set to local timezone which will adjust for daylight savings.
        local_ts = LOCAL_TZ.localize(future_ts)
        # Return as UTC
        return _datetime.utcfromtimestamp(local_ts.timestamp()).replace(tzinfo=timezone.utc)

    # Simplify: existing registration current expiry is always 1 day ahead in utc.
    base_ts = expiry_ts - timedelta(days=1)
    base_date = date(base_ts.year, base_ts.month, base_ts.day)
    # Naive time
    expiry_time = time(23, 59, 59, tzinfo=None)
    future_ts = _datetime.combine(base_date, expiry_time) + timedelta(days=REPAIRER_LIEN_DAYS)
    # Explicitly set to local timezone which will adjust for daylight savings.
    local_ts = LOCAL_TZ.localize(future_ts)
    # Return as UTC
    return _datetime.utcfromtimestamp(local_ts.timestamp()).replace(tzinfo=timezone.utc)


def expiry_dt_from_registration_rl(expiry_ts: _datetime = None):
    """Create a date representing the date at 23:59:59 local time as UTC from the registration timestamp."""
    base_time = expiry_ts.timestamp()
    offset = _datetime.fromtimestamp(base_time) - _datetime.utcfromtimestamp(base_time)
    base_ts = expiry_ts + offset
    base_date = date(base_ts.year, base_ts.month, base_ts.day)
    # Naive time
    expiry_time = time(23, 59, 59, tzinfo=None)
    future_ts = _datetime.combine(base_date, expiry_time) + timedelta(days=REPAIRER_LIEN_DAYS)
    # Explicitly set to local timezone which will adjust for daylight savings.
    local_ts = LOCAL_TZ.localize(future_ts)
    # Return as UTC
    return _datetime.utcfromtimestamp(local_ts.timestamp()).replace(tzinfo=timezone.utc)


def expiry_dt_from_registration(registration_ts, life_years: int):
    """Create a date representing the expiry date for a registration.

    Adjust the registration timestamp by the life_years number of years in the future.
    """
    reg_local_ts = registration_ts.astimezone(LOCAL_TZ)
    base_time = reg_local_ts.timestamp()
    offset = _datetime.fromtimestamp(base_time) - _datetime.utcfromtimestamp(base_time)
    base_ts = reg_local_ts + offset
    current_app.logger.info(f'Adjusted local expiry Date: {base_ts.year}-{base_ts.month}-{base_ts.day} ')
    base_date = date(base_ts.year, base_ts.month, base_ts.day)
    # Naive time
    expiry_time = time(23, 59, 59, tzinfo=None)
    future_ts: _datetime = _datetime.combine(base_date, expiry_time)
    future_ts = future_ts + datedelta(years=life_years)
    # Explicitly set to local timezone which will adjust for daylight savings.
    local_ts = LOCAL_TZ.localize(future_ts)
    current_app.logger.info('Local expiry timestamp: ' + local_ts.isoformat())
    # Return as UTC before formatting
    return _datetime.utcfromtimestamp(local_ts.timestamp()).replace(tzinfo=timezone.utc)


def expiry_dt_add_years(current_expiry, add_years: int):
    """For renewals add years to the existing expiry timestamp."""
    if current_expiry and add_years and add_years > 0:
        return current_expiry + datedelta(years=add_years)
    return current_expiry


def ts_from_iso_format(timestamp_iso: str):
    """Create a datetime object from a timestamp string in the ISO format."""
    time_stamp = _datetime.fromisoformat(timestamp_iso).timestamp()
    return _datetime.utcfromtimestamp(time_stamp).replace(tzinfo=timezone.utc)


def expiry_ts_from_iso_format(timestamp_iso: str):
    """Create a datetime object from a timestamp string in the ISO format.

    For expiry timestamps, the time is set to 23:59:59.
    """
    expiry_ts = ts_from_iso_format(timestamp_iso)
    return expiry_ts.replace(hour=23, minute=59, second=59)


def ts_from_date_iso_format(date_iso: str):
    """Create a UTC datetime object from a date string in the ISO format.

    Use the current UTC time.
    """
    return ts_from_iso_format(date_iso)


def to_local_timestamp(utc_ts):
    """Create a timestamp adjusted from UTC to the local timezone."""
    return utc_ts.astimezone(LOCAL_TZ)


def today_local():
    """Return today in the local timezone."""
    return now_ts().astimezone(LOCAL_TZ)


def get_doc_storage_name(registration):
    """Get a document storage name from the registration in the format YYYY/MM/DD/reg_class-reg_id-reg_num.pdf."""
    name = registration.registration_ts.isoformat()[:10]
    name = name.replace('-', '/') + '/' + registration.registration_type_cl.lower()
    name += '-' + str(registration.id) + '-' + registration.registration_num + '.pdf'
    return name


def get_search_doc_storage_name(search_request):
    """Get a search document storage name in the format YYYY/MM/DD/search-results-report-search_id.pdf."""
    name = search_request.search_ts.isoformat()[:10]
    name = name.replace('-', '/') + '/' + SEARCH_RESULTS_DOC_NAME.format(search_id=search_request.id)
    return name


def is_historical(financing_statement, create: bool):
    """Check if a financing statement is in a historical, non-viewable state."""
    if financing_statement.state_type == STATE_ACTIVE and financing_statement.expire_date and \
            financing_statement.expire_date < _datetime.utcnow():
        financing_statement.state_type = STATE_EXPIRED
    if financing_statement.state_type == STATE_ACTIVE:
        return False
    # Creating a registration is not allowed immediately after the financing statement has expired or been discharged.
    if create:
        return True
    # Offset matches account registrations/search window: need to check to be consistent.
    historical_ts = now_ts_offset(30).timestamp()
    if financing_statement.state_type == STATE_DISCHARGED and financing_statement.registration:
        for reg in reversed(financing_statement.registration):
            if reg.registration_type_cl == REG_CLASS_DISCHARGE and reg.registration_ts.timestamp() < historical_ts:
                return True
    if financing_statement.state_type == STATE_EXPIRED and \
       financing_statement.expire_date and \
       financing_statement.expire_date.timestamp() < historical_ts:
        return True

    return False


def is_financing(registration_class):
    """Check if the registration is a financing registration for some conditions."""
    return registration_class and registration_class in (REG_CLASS_CROWN, REG_CLASS_MISC, REG_CLASS_PPSA)


def is_change(registration_class):
    """Check if the registration is a change or amendment for some conditions."""
    return registration_class and registration_class in (REG_CLASS_AMEND, REG_CLASS_AMEND_COURT, REG_CLASS_CHANGE)


def cleanup_amendment(json_data):
    """Delete empty amendment add/remove arrays."""
    if 'addVehicleCollateral' in json_data and not json_data['addVehicleCollateral']:
        del json_data['addVehicleCollateral']
    if 'deleteVehicleCollateral' in json_data and not json_data['deleteVehicleCollateral']:
        del json_data['deleteVehicleCollateral']
    if 'addGeneralCollateral' in json_data and not json_data['addGeneralCollateral']:
        del json_data['addGeneralCollateral']
    if 'deleteGeneralCollateral' in json_data and not json_data['deleteGeneralCollateral']:
        del json_data['deleteGeneralCollateral']
    if 'addSecuredParties' in json_data and not json_data['addSecuredParties']:
        del json_data['addSecuredParties']
    if 'deleteSecuredParties' in json_data and not json_data['deleteSecuredParties']:
        del json_data['deleteSecuredParties']
    if 'addDebtors' in json_data and not json_data['addDebtors']:
        del json_data['addDebtors']
    if 'deleteDebtors' in json_data and not json_data['deleteDebtors']:
        del json_data['deleteDebtors']
    return json_data


def amendment_change_type(json_data):
    # pylint: disable=too-many-boolean-expressions
    """Try to assign a more specific amendment change type based on the request data."""
    if 'courtOrderInformation' in json_data:
        return REG_TYPE_AMEND_COURT
    if 'addTrustIndenture' in json_data or 'removeTrustIndenture' in json_data:
        return REG_TYPE_AMEND
    change_type = json_data['changeType']
    if 'addVehicleCollateral' not in json_data and 'deleteVehicleCollateral' not in json_data and \
            'addGeneralCollateral' not in json_data and 'deleteGeneralCollateral' not in json_data:
        if 'addDebtors' not in json_data and 'deleteDebtors' not in json_data and \
                'addSecuredParties' in json_data and 'deleteSecuredParties' in json_data and \
                len(json_data['addSecuredParties']) == 1 and len(json_data['deleteSecuredParties']) == 1:
            change_type = REG_TYPE_AMEND_SP_TRANSFER
        if 'addSecuredParties' not in json_data and 'deleteSecuredParties' not in json_data and \
                'addDebtors' in json_data and 'deleteDebtors' in json_data and \
                len(json_data['addDebtors']) == 1 and len(json_data['deleteDebtors']) == 1:
            change_type = REG_TYPE_AMEND_DEBTOR_TRANSFER
        if 'addSecuredParties' not in json_data and 'deleteSecuredParties' not in json_data and \
                'addDebtors' not in json_data and 'deleteDebtors' in json_data and \
                len(json_data['deleteDebtors']) == 1:
            change_type = REG_TYPE_AMEND_DEBTOR_RELEASE
    if 'addSecuredParties' not in json_data and 'deleteSecuredParties' not in json_data and \
       'addDebtors' not in json_data and 'deleteDebtors' not in json_data:
        if 'addVehicleCollateral' not in json_data and 'addGeneralCollateral' not in json_data and \
                ('deleteVehicleCollateral' in json_data or 'deleteGeneralCollateral' in json_data):
            change_type = REG_TYPE_AMEND_PARIAL_DISCHARGE
        if ('addVehicleCollateral' in json_data or 'addGeneralCollateral' in json_data) and \
                'deleteVehicleCollateral' not in json_data and 'deleteGeneralCollateral' not in json_data:
            change_type = REG_TYPE_AMEND_ADDITION_COLLATERAL
        if 'addVehicleCollateral' in json_data and 'deleteVehicleCollateral' in json_data and \
                len(json_data['addVehicleCollateral']) == 1 and len(json_data['deleteVehicleCollateral']) == 1 and \
                'addGeneralCollateral' not in json_data and 'deleteGeneralCollateral' not in json_data:
            change_type = REG_TYPE_AMEND_SUBSTITUTION_COLLATERAL
        if 'addGeneralCollateral' in json_data and 'deleteGeneralCollateral' in json_data and \
                len(json_data['addGeneralCollateral']) == 1 and len(json_data['deleteGeneralCollateral']) == 1 and \
                'addVehicleCollateral' not in json_data and 'deleteVehicleCollateral' not in json_data:
            change_type = REG_TYPE_AMEND_SUBSTITUTION_COLLATERAL

    return change_type


def valid_court_order_date(financing_ts, order_ts: str):
    """Verify requuest court order date is between the financing statement date and the current date."""
    if not financing_ts or not order_ts:
        return False
    financing_date = date(financing_ts.year, financing_ts.month, financing_ts.day)
    order_date = date.fromisoformat(order_ts[:10])
    # Naive date
    now = now_ts()
    today_date = date(now.year, now.month, now.day)
    return financing_date <= order_date <= today_date
