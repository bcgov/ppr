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

import re
import pytz
from datedelta import datedelta
from flask import current_app


# Local timzone
LOCAL_TZ = pytz.timezone('America/Los_Angeles')

# Map from API search type to DB search type
TO_DB_SEARCH_TYPE = {
    'OWNER_NAME': 'MI',
    'ORGANIZATION_NAME': 'MO',
    'MHR_NUMBER': 'MM',
    'SERIAL_NUMBER': 'MS'
}
KEY_ALLOWED_CHARS: str = '&#ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'

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

# MHR Error messages
ERR_REGISTRATION_NOT_FOUND = '{code}: no registration found for MHR number {mhr_number}.'
ERR_SEARCH_TOO_OLD = '{code}: search get details search ID {search_id} timestamp too old: must be after {min_ts}.'
ERR_SEARCH_COMPLETE = '{code}: search select results failed: results already provided for search ID {search_id}.'
ERR_SEARCH_NOT_FOUND = '{code}: search select results failed: invalid search ID {search_id}.'

# PPR Error messages
ERR_FINANCING_NOT_FOUND = '{code}: no Financing Statement found for registration number {registration_num}.'
ERR_REGISTRATION_NOT_FOUND = '{code}: no registration found for registration number {registration_num}.'
ERR_FINANCING_HISTORICAL = \
    '{code}: the Financing Statement for registration number {registration_num} has expired or been discharged.'


SEARCH_RESULTS_DOC_NAME = 'search-results-report-{search_id}.pdf'
DB2_REMOVE_ADRRESS = [', BC', ',BC', 'BC', ', B.C.', ',B.C.', 'B.C.', 'BRITISH COLUMBIA', 'CANADA',
                      ', AB', ',AB', ' AB', ', ALBERTA', 'ALBERTA', ', SK', ',SK', ' SK', ', SASKATCHEWAN',
                      'SASKATCHEWAN', ', ON', ',ON', ' ON', ', ONTARIO', 'ONTARIO']
DB2_PROVINCE_MAPPING = {
    'AB': 'AB',
    ' AB': 'AB',
    ', AB': 'AB',
    'ALBERTA': 'AB',
    'SK': 'SK',
    ' SK': 'SK',
    ', SK': 'SK',
    'SASKATCHEWAN': 'SK',
    'ON': 'ON',
    ' ON': 'ON',
    ', ON': 'ON',
    'ONTARIO': 'ON'
}


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


def ts_from_iso_format(timestamp_iso: str):
    """Create a datetime object from a timestamp string in the ISO format."""
    time_stamp = _datetime.fromisoformat(timestamp_iso).timestamp()
    return _datetime.utcfromtimestamp(time_stamp).replace(tzinfo=timezone.utc)


def ts_from_date_iso_format(date_iso: str):
    """Create a UTC datetime object from a date string in the ISO format.

    Use the current UTC time.
    """
    return ts_from_iso_format(date_iso)


def date_from_iso_format(date_iso: str):
    """Create a date object from a date string in the ISO format."""
    return date.fromisoformat(date_iso)


def time_from_iso_format(time_iso: str):
    """Create a time object from a time string in the ISO format."""
    return time.fromisoformat(time_iso)


def to_local_timestamp(utc_ts):
    """Create a timestamp adjusted from UTC to the local timezone."""
    return utc_ts.astimezone(LOCAL_TZ)


def to_local_expiry_report(expiry_date_time: str):
    """Create an expiry timestamp adjusted from UTC to the local timezone."""
    utc_ts: _datetime = ts_from_iso_format(expiry_date_time)
    offset: int = 7 if utc_ts.hour == 6 else 8
    # current_app.logger.info('UTC ts: ' + utc_ts.isoformat() + ' offset=' + str(offset))
    local_ts = utc_ts - timedelta(hours=offset)
    current_app.logger.info('Local expiry timestamp: ' + local_ts.isoformat())
    return local_ts


def today_local():
    """Return today in the local timezone."""
    return now_ts().astimezone(LOCAL_TZ)


def expiry_dt_from_years(life_years: int, iso_date: str = None):
    """Create a date representing the date at 23:59:59 local time as UTC.

    Adjusted by the life_years number of years in the future. Use current date if no iso_date.
    PYTZ has a DST issue (not working after 2037), so set the time before adding years.
    """
    # Naive date
    today = None
    if iso_date:
        today = date.fromisoformat(iso_date[:10])
    else:
        today = now_ts().astimezone(LOCAL_TZ)
    # Naive time
    expiry_time = time(23, 59, 59, tzinfo=None)
    expiry_now = _datetime.combine(date(today.year, today.month, today.day), expiry_time)
    # Explicitly set to local timezone which will adjust for daylight savings.
    local_ts = LOCAL_TZ.localize(expiry_now)
    # Add years
    future_ts = local_ts + datedelta(years=life_years)
    # Return as UTC
    return _datetime.utcfromtimestamp(future_ts.timestamp()).replace(tzinfo=timezone.utc)


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


def expiry_dt_from_registration(registration_ts, life_years: int):
    """Create a date representing the expiry date for a registration.

    Adjust the registration timestamp by the life_years number of years in the future.
    PYTZ has a DST issue (not working after 2037), so set the time before adding years.
    """
    reg_local_ts = registration_ts.astimezone(LOCAL_TZ)
    base_time = reg_local_ts.timestamp()
    offset = _datetime.fromtimestamp(base_time) - _datetime.utcfromtimestamp(base_time)
    base_ts = reg_local_ts + offset
    base_date = date(base_ts.year, base_ts.month, base_ts.day)
    current_app.logger.info('Adjusted local reg Date: ' + base_date.isoformat())
    # Naive time
    expiry_time = time(23, 59, 59, tzinfo=None)
    expiry_reg = _datetime.combine(base_date, expiry_time)
    if life_years:
        # Explicitly set to local timezone which will adjust for daylight savings.
        local_ts = LOCAL_TZ.localize(expiry_reg)
        # Add years
        future_ts = local_ts + datedelta(years=life_years)
        current_app.logger.info('Local expiry timestamp: ' + future_ts.isoformat())
        # Return as UTC
        return _datetime.utcfromtimestamp(future_ts.timestamp()).replace(tzinfo=timezone.utc)

    # is RL
    future_ts = expiry_reg + timedelta(days=REPAIRER_LIEN_DAYS)
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


def get_compressed_key(name: str) -> str:
    """Get the compressed search key for the organization or combined owner name."""
    key: str = ''
    if not name:
        return key
    key = name.upper()
    # 1 Remove the first character of the string if it’s not in the accepted alphanumeric characters.
    #   Accepted characters: &#ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890
    if KEY_ALLOWED_CHARS.find(key[0:1]) < 0:
        key = key[1:]
    # 2 Remove 'THE ' from the beginning of the string.
    if key.startswith('THE '):
        key = key[4:]
    # 3 Remove any non-alphanumeric characters.
    #   Accepted characters: &#ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890
    key = re.sub('[^0-9A-Z&#]+', '', key)
    # 4 If the remaining string starts with 'BRITISHCOLUMBIA ', replace it with ‘BC’.
    if key.startswith('BRITISHCOLUMBIA'):
        key = 'BC' + key[15:]
    # 5 Replace ‘#’ with ‘NUMBER’.
    key = key.replace('#', 'NUMBER')
    # 6 Replace ‘&’ with ‘AND’;
    key = key.replace('&', 'AND')

    # 7 Replace all numbers with matching words (0 with ZERO)
    key = key.replace('0', 'ZERO')
    key = key.replace('1', 'ONE')
    key = key.replace('2', 'TWO')
    key = key.replace('3', 'THREE')
    key = key.replace('4', 'FOUR')
    key = key.replace('5', 'FIVE')
    key = key.replace('6', 'SIX')
    key = key.replace('7', 'SEVEN')
    key = key.replace('8', 'EIGHT')
    key = key.replace('9', 'NINE')
    if len(key) > 30:
        return key[0:30]
    return key


def get_serial_number_key(serial_num: str) -> str:
    """Get the compressed search serial number key for the MH serial number."""
    key: str = ''
    if not serial_num:
        return key
    key = serial_num.strip().upper()
    if len(key) > 20:
        return key[0:20]
    return key


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


def get_ind_name_from_db2(db2_name: str):
    """Get an individual name json from a DB2 legacy name."""
    last = db2_name[0:24].strip()
    first = db2_name[25:].strip()
    middle = None
    if len(db2_name) > 40:
        first = db2_name[25:38].strip()
        middle = db2_name[39:].strip()
    name = {
        'first': first,
        'last': last
    }
    if middle:
        name['middle'] = middle
    return name


def get_address_from_db2(legacy_address: str, postal_code: str = ''):
    """Get an address json from a DB2 legacy address."""
    if len(legacy_address) > 120:
        return get_long_address_from_db2(legacy_address, postal_code)

    street = legacy_address[0:38].strip()
    street2 = None
    city = None
    province = None
    if len(legacy_address) > 80:
        value: str = legacy_address[79:].strip()
        province = get_province_db2(value, None)
        for text in DB2_REMOVE_ADRRESS:
            if value.endswith(text):
                value = value.replace(text, '')
                break
        value = value.strip()
        if value:
            city = value
            street2 = legacy_address[39:78].strip()
    if not city:
        city = legacy_address[39:78].strip()
        province = get_province_db2(city, None)
        for text in DB2_REMOVE_ADRRESS:
            if city.endswith(text):
                city = city.replace(text, '')
                break
        city = city.strip()
    if not province:
        province = 'BC'
    address = {
        'city': city,
        'street': street,
        'region': province,
        'country': 'CA',
        'postalCode': postal_code
    }
    if street2:
        address['streetAdditional'] = street2
    return address


def get_long_address_from_db2(legacy_address: str, postal_code: str = ''):
    """Get an address json from a DB2 legacy address."""
    value: str = legacy_address[119:].strip()
    street = legacy_address[0:38].strip()
    street2 = None
    city = legacy_address[79:118].strip()
    province = get_province_db2(value, None)
    for text in DB2_REMOVE_ADRRESS:
        if value.endswith(text):
            value = value.replace(text, '')
            break
    value = value.strip()
    # current_app.logger.debug(f'2. value={value}')
    if value:
        city = value
        street2 = legacy_address[39:118].strip()
        # current_app.logger.debug(f'3. street2={street2}, city={city}')
    else:
        province = get_province_db2(city, None)
        for text in DB2_REMOVE_ADRRESS:
            if city.endswith(text):
                city = city.replace(text, '')
                break
        city = city.strip()
        if city == '':
            city = legacy_address[39:78].strip()
        else:
            street2 = legacy_address[39:78].strip()
        # current_app.logger.debug(f'4. street2={street2}, city={city}')
    if not province:
        province = 'BC'
    address = {
        'city': city,
        'street': street,
        'region': province,
        'country': 'CA',
        'postalCode': postal_code
    }
    if street2:
        address['streetAdditional'] = street2
    return address


def get_province_db2(legacy_value: str, default: str):
    """Get a province code from DB2 legacy address text."""
    for text in DB2_REMOVE_ADRRESS:
        if legacy_value.endswith(text) and DB2_PROVINCE_MAPPING.get(text):
            if len(legacy_value) == 2 or len(text) > 2:
                return DB2_PROVINCE_MAPPING[text]
    return default
