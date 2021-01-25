# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Date time utilities."""
# from datetime import datetime, timezone
import time as _time
from datetime import date, datetime as _datetime, timezone, timedelta  # pylint: disable=unused-import # noqa: F401, I001


class datetime(_datetime):  # pylint: disable=invalid-name; # noqa: N801; ha datetime is invalid??
    """Alternative to the built-in datetime that has a timezone on the UTC call."""

    @classmethod
    def utcnow(cls):
        """Construct a UTC non-naive datetime, meaning it includes timezone from time.time()."""
        time_stamp = _time.time()
        return super().utcfromtimestamp(time_stamp).replace(tzinfo=timezone.utc)


def format_ts(time_stamp):
    """Build a UTC ISO 8601 date and time string with no microseconds."""
    formatted_ts = None
    if time_stamp:
#        formatted_ts = time_stamp.replace(microsecond=0).isoformat()
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

def expiry_dt_from_years(life_years: int):
    """Create a date representing the current date adjusted by the life_years number of years in the future."""
    today = date.today()
    year = today.year + life_years
    month = today.month
    day = today.day

#    add_days = 365 * life_years
#    return today + timedelta(days=add_days) 
    return date(year, month, day)

def ts_from_iso_format(timestamp_iso: str):
    """Create a datetime object from a timestamp string in the ISO format."""
    return _datetime.fromisoformat(timestamp_iso) #.replace(tzinfo=timezone.utc)
