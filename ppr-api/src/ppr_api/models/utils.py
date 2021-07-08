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

from datetime import date, datetime as _datetime, timezone, timedelta
from datetime import time  # noqa: F401 pylint: disable=unused-import


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
REG_CLASS_DISCHARGE = 'DISCHARGE'
REG_CLASS_FINANCING = 'PPSALIEN'
REG_CLASS_MISC = 'MISCLIEN'
REG_CLASS_RENEWAL = 'RENEWAL'

# DB registration types
REG_TYPE_AMEND = 'AM'
REG_TYPE_AMEND_COURT = 'CO'
REG_TYPE_DISCHARGE = 'DC'
REG_TYPE_RENEWAL = 'RE'
REG_TYPE_REPAIRER_LIEN = 'RL'

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
    'MISCLIEN': 'FINANCING_STATEMENT',
    'PPSALIEN': 'FINANCING_STATEMENT'
}

# Mapping from DB registration class to API statement type
REG_CLASS_TO_STATEMENT_TYPE = {
    'AMENDMENT': 'AMENDMENT_STATEMENT',
    'COURTORDER': 'AMENDMENT_STATEMENT',
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
    'CO': 'COURTORDER',
    'AC': 'CHANGE',
    'DR': 'CHANGE',
    'DT': 'CHANGE',
    'PD': 'CHANGE',
    'ST': 'CHANGE',
    'SU': 'CHANGE',
    'DC': 'DISCHARGE',
    'MR': 'MISCLIEN',
    'SA': 'PPSALIEN',
    'SG': 'PPSALIEN',
    'RL': 'PPSALIEN',
    'FR': 'PPSALIEN',
    'LT': 'PPSALIEN',
    'MH': 'PPSALIEN',
    'FL': 'PPSALIEN',
    'FA': 'PPSALIEN',
    'FS': 'PPSALIEN',
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
                    ELSE p.last_name || ', ' || p.first_name END
          FROM parties p
         WHERE p.registration_id = r.id
           AND p.party_type = 'RG') AS registering_party,
       (SELECT CASE WHEN p.business_name IS NOT NULL THEN p.business_name
                    WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)
                    ELSE p.last_name || ', ' || p.first_name END
          FROM parties p
         WHERE p.financing_id = fs.id
           AND p.registration_id_end IS NULL
           AND p.party_type = 'SP'
      ORDER BY p.id desc LIMIT 1) AS secured_party,
      r.client_reference_id
  FROM registrations r, registration_types rt, financing_statements fs
 WHERE r.registration_type = rt.registration_type
   AND fs.id = r.financing_id
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN')
   AND r.account_id = '?'
   AND (fs.expire_date IS NULL OR fs.expire_date > ((now() at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
ORDER BY r.registration_ts DESC
FETCH FIRST 1000 ROWS ONLY
"""

QUERY_ACCOUNT_REGISTRATIONS = """
SELECT r.id, r.registration_number, r.registration_ts, r.registration_type, r.registration_type_cl,
       rt.registration_desc, r.base_reg_number, fs.state_type AS state,
       CASE WHEN fs.life = 99 THEN -99
            ELSE CAST(EXTRACT(day from (fs.expire_date - (now() at time zone 'utc'))) AS INT) END expire_days,
       (SELECT MAX(r2.registration_ts)
          FROM registrations r2
         WHERE r2.financing_id = r.financing_id) AS last_update_ts,
       (SELECT CASE WHEN p.business_name IS NOT NULL THEN p.business_name
                    WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)
                    ELSE p.last_name || ', ' || p.first_name END
          FROM parties p
         WHERE p.registration_id = r.id
           AND p.party_type = 'RG') AS registering_party,
       (SELECT CASE WHEN p.business_name IS NOT NULL THEN p.business_name
                    WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)
                    ELSE p.last_name || ', ' || p.first_name END
          FROM parties p
         WHERE p.financing_id = fs.id
           AND p.registration_id_end IS NULL
           AND p.party_type = 'SP'
      ORDER BY p.id desc LIMIT 1) AS secured_party,
      r.client_reference_id
  FROM registrations r, registration_types rt, financing_statements fs
 WHERE r.registration_type = rt.registration_type
   AND fs.id = r.financing_id
   AND r.account_id = '?'
   AND (fs.expire_date IS NULL OR fs.expire_date > ((now() at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
ORDER BY r.registration_ts DESC
FETCH FIRST 1000 ROWS ONLY
"""

QUERY_ACCOUNT_DRAFTS = """
SELECT d.document_number, d.create_ts, d.registration_type, d.registration_type_cl, rt.registration_desc,
       CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') THEN ''
            ELSE d.registration_number END base_reg_num,
       d.draft ->> 'type' AS draft_type,
       CASE WHEN d.update_ts IS NOT NULL THEN d.update_ts ELSE d.create_ts END last_update_ts,
       CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') THEN
                 d.draft -> 'financingStatement' ->> 'clientReferenceId'
            WHEN d.registration_type_cl = 'AMENDMENT' THEN d.draft -> 'amendmentStatement' ->> 'clientReferenceId'
            WHEN d.registration_type_cl = 'CHANGE' THEN d.draft -> 'changeStatement' ->> 'clientReferenceId'
            ELSE '' END client_reference_id
  FROM drafts d, registration_types rt
 WHERE d.account_id = '?'
   AND d.registration_type = rt.registration_type
   AND NOT EXISTS (SELECT r.draft_id FROM registrations r WHERE r.draft_id = d.id)
ORDER BY d.create_ts DESC
FETCH FIRST 1000 ROWS ONLY
"""

# Error messages
ERR_FINANCING_NOT_FOUND = 'No Financing Statement found for registration number {registration_num}.'
ERR_REGISTRATION_NOT_FOUND = 'No registration found for registration number {registration_num}.'
ERR_FINANCING_HISTORICAL = \
    'The Financing Statement for registration number {registration_num} has expired or been discharged.'
ERR_REGISTRATION_ACCOUNT = 'The account ID {account_id} does not match registration number {registration_num}.'
ERR_REGISTRATION_MISMATCH = \
    'The registration {registration_num} does not match the Financing Statement registration {base_reg_num}.'


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


def expiry_dt_from_years(life_years: int):
    """Create a date representing the current UTC date at 23:59:59.

    Adjusted by the life_years number of years in the future.
    """
    today = now_ts()
    year = today.year + life_years
    month = today.month
    day = today.day
    future_date = date(year, month, day)
    expiry_time = time(23, 59, 59, tzinfo=timezone.utc)
    return _datetime.combine(future_date, expiry_time)


def expiry_dt_add_years(current_expiry, add_years: int):
    """For renewals add years to the existing expiry timestamp."""
    if current_expiry and add_years and add_years > 0:
        return current_expiry.replace(year=current_expiry.year + add_years)

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


def is_historical(financing_statement):
    """Check if a financing statement is in a historical, non-viewable state."""
    if financing_statement.state_type == STATE_ACTIVE:
        return False

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
