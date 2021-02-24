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
"""Test Suite to ensure the datetime utility functions are working as expected.

"""
from datetime import timedelta as _timedelta
from ppr_api.utils import datetime

def test_expiry_dt_from_years():
    """Assert that generating an expiry date from life years is performing as expected."""
    expiry_ts = datetime.expiry_dt_from_years(5)
    now_ts = datetime.now_ts()
    print('Expiry timestamp: ' + datetime.format_ts(expiry_ts))
    print('Now timestamp: ' + datetime.format_ts(now_ts))
    assert (expiry_ts.year - now_ts.year) == 5
    assert expiry_ts.hour == 23
    assert expiry_ts.minute == 59
    assert expiry_ts.second == 59
    assert expiry_ts.day == now_ts.day
    assert expiry_ts.month in (now_ts.month, (now_ts.month + 1))

def test_ts_from_iso_format():
    """Assert that creating a UTC datetime object from an ISO date-time
       formatted string is performing as expected."""
    test_ts = datetime.ts_from_iso_format('2021-02-16T23:00:00-08:00')
    print('Test timestamp: ' + datetime.format_ts(test_ts))
    assert test_ts.day == 17
    assert test_ts.month == 2
    assert test_ts.year == 2021
    assert test_ts.hour == 7
    assert test_ts.minute == 0
    assert test_ts.second == 0

    test_ts = datetime.ts_from_iso_format('2021-02-16T23:00:00+00:00')
    print('Test timestamp: ' + datetime.format_ts(test_ts))
    assert test_ts.day == 16
    assert test_ts.hour == 23

    test_ts = datetime.ts_from_iso_format('2021-02-16T13:00:00-08:00')
    print('Test timestamp: ' + datetime.format_ts(test_ts))
    assert test_ts.day == 16
    assert test_ts.hour == 21

    test_ts = datetime.ts_from_iso_format('2021-03-31T23:00:00-08:00')
    print('Test timestamp: ' + datetime.format_ts(test_ts))
    assert test_ts.month == 4
    assert test_ts.day == 1
    assert test_ts.hour == 7

def test_ts_from_date_iso_format():
    """Assert that creating a UTC datetime object from an ISO date-time
       formatted string is performing as expected."""
    test_ts = datetime.ts_from_date_iso_format('2021-02-16')
    print('Test timestamp: ' + datetime.format_ts(test_ts))
    assert test_ts.day in (16, 17)
    assert test_ts.month == 2
    assert test_ts.year == 2021
    if test_ts.day == 16:
        assert test_ts.hour >= 8
    else:
        assert test_ts.hour <= 7


def test_now_ts_offset():
    """Assert that adjusting UTC now by a number of days is performing as expected."""
    now_ts = datetime.now_ts() + _timedelta(days=60)
    test_ts = datetime.now_ts_offset(60, True)
    print('Now timestamp + 60 days: ' + datetime.format_ts(test_ts))
    assert test_ts.day == now_ts.day
    assert test_ts.month == now_ts.month
    assert test_ts.year == now_ts.year

    now_ts = datetime.now_ts() - _timedelta(days=60)
    test_ts = datetime.now_ts_offset(60, False)
    print('Now timestamp - 60 days: ' + datetime.format_ts(test_ts))
    assert test_ts.day == now_ts.day
    assert test_ts.month == now_ts.month
    assert test_ts.year == now_ts.year
