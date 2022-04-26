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
