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
"""Test Suite to ensure the datetime utility functions are working as expected."""
from datetime import timedelta as _timedelta

import pytest

from ppr_api.models import utils as model_utils


# testdata pattern is ({registration_ts}, {years}, {expiry_ts})
TEST_DATA_EXPIRY = [
    ('2021-08-31T00:00:01-07:00', 1, '2022-09-01T06:59:59+00:00'),
    ('2021-08-31T01:00:00-07:00', 1, '2022-09-01T06:59:59+00:00'),
    ('2021-08-31T04:00:00-07:00', 1, '2022-09-01T06:59:59+00:00'),
    ('2021-08-31T08:00:00-07:00', 1, '2022-09-01T06:59:59+00:00'),
    ('2021-08-31T12:00:00-07:00', 1, '2022-09-01T06:59:59+00:00'),
    ('2021-08-31T16:00:00-07:00', 1, '2022-09-01T06:59:59+00:00'),
    ('2021-08-31T16:01:00-07:00', 1, '2022-09-01T06:59:59+00:00'),
    ('2021-08-31T17:00:00-07:00', 1, '2022-09-01T06:59:59+00:00'),
    ('2021-08-31T17:01:00-07:00', 1, '2022-09-01T06:59:59+00:00'),
    ('2021-08-31T18:00:00-07:00', 1, '2022-09-01T06:59:59+00:00'),
    ('2021-08-31T19:00:00-07:00', 1, '2022-09-01T06:59:59+00:00'),
    ('2021-08-31T20:00:00-07:00', 1, '2022-09-01T06:59:59+00:00'),
    ('2021-08-31T21:00:00-07:00', 1, '2022-09-01T06:59:59+00:00'),
    ('2021-08-31T22:00:00-07:00', 1, '2022-09-01T06:59:59+00:00'),
    ('2021-08-31T23:00:00-07:00', 1, '2022-09-01T06:59:59+00:00'),
    ('2021-08-31T23:59:59-07:00', 1, '2022-09-01T06:59:59+00:00'),
    ('2021-09-01T00:00:01-07:00', 4, '2025-09-02T06:59:59+00:00'),
    ('2021-11-30T00:00:01-08:00', 4, '2025-12-01T07:59:59+00:00')
]
# testdata pattern is ({registration_ts}, {expiry_ts})
TEST_DATA_EXPIRY_RL = [
    ('2021-08-31T00:00:01-07:00', '2022-02-28T07:59:59+00:00'),
    ('2021-08-31T01:00:00-07:00', '2022-02-28T07:59:59+00:00'),
    ('2021-08-31T04:00:00-07:00', '2022-02-28T07:59:59+00:00'),
    ('2021-08-31T08:00:00-07:00', '2022-02-28T07:59:59+00:00'),
    ('2021-08-31T12:00:00-07:00', '2022-02-28T07:59:59+00:00'),
    ('2021-08-31T16:00:00-07:00', '2022-02-28T07:59:59+00:00'),
    ('2021-08-31T16:01:00-07:00', '2022-02-28T07:59:59+00:00'),
    ('2021-08-31T17:00:00-07:00', '2022-02-28T07:59:59+00:00'),
    ('2021-08-31T18:00:00-07:00', '2022-02-28T07:59:59+00:00'),
    ('2021-08-31T19:00:00-07:00', '2022-02-28T07:59:59+00:00'),
    ('2021-08-31T20:00:00-07:00', '2022-02-28T07:59:59+00:00'),
    ('2021-08-31T21:00:00-07:00', '2022-02-28T07:59:59+00:00'),
    ('2021-08-31T22:00:00-07:00', '2022-02-28T07:59:59+00:00'),
    ('2021-08-31T23:00:00-07:00', '2022-02-28T07:59:59+00:00'),
    ('2021-08-31T23:59:59-07:00', '2022-02-28T07:59:59+00:00'),
    ('2021-01-01T01:00:00-07:00', '2021-07-01T06:59:59+00:00')
]
# testdata pattern is ({registration_ts}, {add_1}, {add_2}, {add_3}, {expiry_ts})
TEST_DATA_EXPIRY_ADD = [
    ('2021-08-31T00:00:01-07:00', 10, 5, 2, '2038-09-01T06:59:59+00:00'),
    ('2021-01-31T00:00:01-08:00', 2, 3, 5, '2031-02-01T07:59:59+00:00')
]
# testdata pattern is ({desc}, {registration_ts}, {renew_count}, {expiry_ts})
TEST_DATA_EXPIRY_RENEW_RL = [
    ('Registration', '2021-08-31T00:00:01-07:00', 0, '2022-02-28T07:59:59+00:00'),
    ('1 renewal', '2021-08-31T00:00:01-07:00', 1, '2022-08-27T06:59:59+00:00'),
    ('2 renewals', '2021-08-31T00:00:01-07:00', 2, '2023-02-23T07:59:59+00:00')
]
# testdata pattern is ({desc}, {registration_ts}, {hour})
TEST_DATA_EXPIRY_REGISTRATION = [
    ('Daylight savings', '2021-08-31T12:00:01-07:00', 5, 6),
    ('No daylight savings', '2021-01-31T13:00:01-07:00', 10, 7)
]


@pytest.mark.parametrize('registration_ts,offset,expiry_ts', TEST_DATA_EXPIRY)
def test_expiry_date(session, registration_ts, offset, expiry_ts):
    """Assert that computing expiry ts from registraton ts works as expected."""
    # reg_ts = model_utils.ts_from_iso_format(registration_ts)
    expiry_test = model_utils.expiry_dt_from_years(offset, registration_ts)
    expiry_iso = model_utils.format_ts(expiry_test)
    # print(registration_ts + ', ' + model_utils.format_ts(reg_ts) + ', '  + expiry_iso)
    assert expiry_ts == expiry_iso


@pytest.mark.parametrize('registration_ts,expiry_ts', TEST_DATA_EXPIRY_RL)
def test_expiry_date_rl(session, registration_ts, expiry_ts):
    """Assert that computing an RL expiry ts from registraton ts works as expected."""
    reg_ts = model_utils.ts_from_iso_format(registration_ts)
    expiry_test = model_utils.expiry_dt_repairer_lien(reg_ts)
    expiry_iso = model_utils.format_ts(expiry_test)
    # print(registration_ts + ', ' + model_utils.format_ts(reg_ts) + ', '  + expiry_iso)
    assert expiry_ts == expiry_iso


@pytest.mark.parametrize('registration_ts,add_1,add_2,add_3,expiry_ts', TEST_DATA_EXPIRY_ADD)
def test_expiry_date_add(session, registration_ts, add_1, add_2, add_3, expiry_ts):
    """Assert that computing an renewal non-RL expiry ts from registraton ts works as expected."""
    reg_ts = model_utils.ts_from_iso_format(registration_ts)
    expiry_add_1 = model_utils.expiry_dt_from_years(add_1, registration_ts)
    assert expiry_add_1.year - add_1 == reg_ts.year
    assert expiry_add_1.hour in (6, 7)
    assert expiry_add_1.minute == 59
    assert expiry_add_1.second == 59
    expiry_add_2 = model_utils.expiry_dt_add_years(expiry_add_1, add_2)
    assert expiry_add_2.year - expiry_add_1.year == add_2
    assert expiry_add_2.hour in (6, 7)
    assert expiry_add_2.minute == 59
    assert expiry_add_2.second == 59
    expiry_add_3 = model_utils.expiry_dt_add_years(expiry_add_2, add_3)
    assert expiry_add_3.year - expiry_add_2.year == add_3
    assert expiry_add_3.hour in (6, 7)
    assert expiry_add_3.minute == 59
    assert expiry_add_3.second == 59
    expiry_iso = model_utils.format_ts(expiry_add_3)
    # print(registration_ts + ', ' + model_utils.format_ts(reg_ts) + ', '  + expiry_iso)
    assert expiry_ts == expiry_iso


@pytest.mark.parametrize('desc,registration_ts,renew_count,expiry_ts', TEST_DATA_EXPIRY_RENEW_RL)
def test_expiry_date_renew_rl(session, desc, registration_ts, renew_count, expiry_ts):
    """Assert that computing multiple RL renewal expiry ts from registration ts works as expected."""
    reg_ts = model_utils.ts_from_iso_format(registration_ts)
    expiry_test = model_utils.expiry_dt_repairer_lien(reg_ts)
    # print(model_utils.format_ts(expiry_test))
    if renew_count > 0:
        for x in range(renew_count):
            expiry_test = model_utils.expiry_dt_repairer_lien(expiry_test)
            # print(model_utils.format_ts(expiry_test))

    expiry_iso = model_utils.format_ts(expiry_test)
    assert expiry_ts == expiry_iso


def test_expiry_dt_from_years():
    """Assert that generating an expiry date from life years is performing as expected."""
    expiry_ts = model_utils.expiry_dt_from_years(5)
    now_ts = model_utils.now_ts()
    print('Expiry timestamp: ' + model_utils.format_ts(expiry_ts))
    print('Now timestamp: ' + model_utils.format_ts(now_ts))
    assert (expiry_ts.year - now_ts.year) == 5
    assert expiry_ts.hour in (6, 7)
    assert expiry_ts.minute == 59
    assert expiry_ts.second == 59
    assert expiry_ts.day in (1, now_ts.day, (now_ts.day + 1))
    assert expiry_ts.month in (now_ts.month, (now_ts.month + 1))


def test_ts_from_iso_format():
    """Assert that creating a UTC datetime object from an ISO date-time formatted string is performing as expected."""
    test_ts = model_utils.ts_from_iso_format('2021-02-16T23:00:00-08:00')
    print('Test timestamp: ' + model_utils.format_ts(test_ts))
    assert test_ts.day == 17
    assert test_ts.month == 2
    assert test_ts.year == 2021
    assert test_ts.hour == 7
    assert test_ts.minute == 0
    assert test_ts.second == 0

    test_ts = model_utils.ts_from_iso_format('2021-02-16T23:00:00+00:00')
    print('Test timestamp: ' + model_utils.format_ts(test_ts))
    assert test_ts.day == 16
    assert test_ts.hour == 23

    test_ts = model_utils.ts_from_iso_format('2021-02-16T13:00:00-08:00')
    # print('Test timestamp: ' + model_utils.format_ts(test_ts))
    assert test_ts.day == 16
    assert test_ts.hour == 21

    test_ts = model_utils.ts_from_iso_format('2021-03-31T23:00:00-08:00')
    # print('Test timestamp: ' + model_utils.format_ts(test_ts))
    assert test_ts.month == 4
    assert test_ts.day == 1
    assert test_ts.hour == 7


def test_ts_from_date_iso_format():
    """Assert that creating a UTC datetime object from an ISO date-time formatted string is performing as expected."""
    test_ts = model_utils.ts_from_date_iso_format('2021-02-16')
    print('Test timestamp: ' + model_utils.format_ts(test_ts))
    assert test_ts.day in (16, 17)
    assert test_ts.month == 2
    assert test_ts.year == 2021
    if test_ts.day == 16:
        assert test_ts.hour >= 8
    else:
        assert test_ts.hour <= 7


def test_now_ts_offset():
    """Assert that adjusting UTC now by a number of days is performing as expected."""
    now_ts = model_utils.now_ts() + _timedelta(days=60)
    test_ts = model_utils.now_ts_offset(60, True)
    print('Now timestamp + 60 days: ' + model_utils.format_ts(test_ts))
    assert test_ts.day == now_ts.day
    assert test_ts.month == now_ts.month
    assert test_ts.year == now_ts.year

    now_ts = model_utils.now_ts() - _timedelta(days=60)
    test_ts = model_utils.now_ts_offset(60, False)
    print('Now timestamp - 60 days: ' + model_utils.format_ts(test_ts))
    assert test_ts.day == now_ts.day
    assert test_ts.month == now_ts.month
    assert test_ts.year == now_ts.year


def test_today_ts_offset():
    """Assert that adjusting UTC today by a number of days is performing as expected."""
    test_now_ts = model_utils.now_ts_offset(7, False)
    test_today_ts = model_utils.today_ts_offset(7, False)
    # print('test now - 7 days: ' + model_utils.format_ts(test_now_ts))
    # print('test today - 7 days: ' + model_utils.format_ts(test_today_ts))
    assert test_today_ts.hour == 0
    assert test_today_ts.minute == 0
    assert test_today_ts.second == 0
    assert test_today_ts < test_now_ts


def test_expiry_dt_repairer_lien_now():
    """Assert that the computed expiry date for a repairer's lien performs as expected."""
    test_ts = model_utils.expiry_dt_repairer_lien()
    now_ts = model_utils.now_ts()
    delta = test_ts - now_ts
    assert delta.days == model_utils.REPAIRER_LIEN_DAYS
    assert test_ts.hour in (6, 7)
    assert test_ts.minute == 59
    assert test_ts.second == 59


@pytest.mark.parametrize('desc,registration_ts,life_years,hour', TEST_DATA_EXPIRY_REGISTRATION)
def test_expiry_dt_from_registration(session, desc, registration_ts, life_years, hour):
    """Assert that creating an expiry timestamp from a registration timestamp is performing as expected."""
    test_ts = model_utils.ts_from_iso_format(registration_ts)
    expiry_ts = model_utils.expiry_dt_from_registration(test_ts, life_years)
    print(model_utils.format_ts(expiry_ts))
    assert expiry_ts.year - test_ts.year == life_years
    assert expiry_ts.hour == hour
    assert expiry_ts.minute == 59
    assert expiry_ts.second == 59
