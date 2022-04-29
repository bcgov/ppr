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


# Error messages
ERR_REGISTRATION_NOT_FOUND = '{code}: no registration found for MHR number {mhr_number}.'
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
    street = legacy_address[0:38].strip()
    street2 = None
    city = legacy_address[39:].strip()
    if len(legacy_address) > 80:
        city = legacy_address[79:].strip()
        street2 = legacy_address[39:78].strip()
    address = {
        'city': city,
        'street': street,
        'region': 'BC',
        'country': 'CA',
        'postalCode': postal_code
    }
    if street2:
        address['streetAdditional'] = street2
    return address


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
