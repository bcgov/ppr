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
import copy
from datetime import timedelta as _timedelta

import pytest
from registry_schemas.example_data.ppr import AMENDMENT_STATEMENT

from ppr_api.models import utils as model_utils, Registration, SearchRequest


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
    ('2021-11-30T00:00:01-08:00', 4, '2025-12-01T07:59:59+00:00'),
    ('2022-11-30T00:00:01-08:00', 15, '2037-12-01T07:59:59+00:00'),
    ('2022-11-30T00:00:01-08:00', 16, '2038-12-01T07:59:59+00:00'),
    ('2022-11-30T00:00:01-08:00', 25, '2047-12-01T07:59:59+00:00'),
    ('2022-09-01T00:00:01-07:00', 15, '2037-09-02T06:59:59+00:00'),
    ('2022-09-01T00:00:01-07:00', 16, '2038-09-02T06:59:59+00:00'),
    ('2022-09-01T00:00:01-07:00', 25, '2047-09-02T06:59:59+00:00')
]
# testdata pattern is ({registration_ts}, {expiry_ts})
TEST_DATA_EXPIRY_RL = [
    ('2021-08-31T06:59:59+00:00', '2022-02-27T07:59:59+00:00'),
    ('2021-09-01T06:59:59+00:00', '2022-02-28T07:59:59+00:00'),
    ('2021-09-02T06:59:59+00:00', '2022-03-01T07:59:59+00:00'),
    ('2021-09-13T06:59:59+00:00', '2022-03-12T07:59:59+00:00'),
    ('2021-09-14T06:59:59+00:00', '2022-03-13T07:59:59+00:00'),
    ('2021-09-30T06:59:59+00:00', '2022-03-29T06:59:59+00:00'),
    ('2021-10-01T06:59:59+00:00', '2022-03-30T06:59:59+00:00'),
    ('2021-10-31T06:59:59+00:00', '2022-04-29T06:59:59+00:00'),
    ('2021-11-07T06:59:59+00:00', '2022-05-06T06:59:59+00:00'),
    ('2021-11-08T07:59:59+00:00', '2022-05-07T06:59:59+00:00'),
    ('2021-12-01T07:59:59+00:00', '2022-05-30T06:59:59+00:00'),
    ('2022-01-01T07:59:59+00:00', '2022-06-30T06:59:59+00:00'),
    ('2022-02-01T07:59:59+00:00', '2022-07-31T06:59:59+00:00'),
    ('2022-03-01T07:59:59+00:00', '2022-08-28T06:59:59+00:00'),
    ('2022-03-13T07:59:59+00:00', '2022-09-09T06:59:59+00:00'),
    ('2022-03-14T06:59:59+00:00', '2022-09-10T06:59:59+00:00'),
    ('2022-04-01T06:59:59+00:00', '2022-09-28T06:59:59+00:00'),
    ('2022-05-01T06:59:59+00:00', '2022-10-28T06:59:59+00:00'),
    ('2022-05-10T06:59:59+00:00', '2022-11-06T06:59:59+00:00'),
    ('2022-05-11T06:59:59+00:00', '2022-11-07T07:59:59+00:00'),
    ('2022-06-01T06:59:59+00:00', '2022-11-28T07:59:59+00:00'),
    ('2022-07-01T06:59:59+00:00', '2022-12-28T07:59:59+00:00'),
    ('2022-08-01T06:59:59+00:00', '2023-01-28T07:59:59+00:00')
]
# testdata pattern is ({registration_ts}, {add_1}, {add_2}, {add_3}, {expiry_ts})
TEST_DATA_EXPIRY_ADD = [
    ('2021-08-31T00:00:01-07:00', 10, 5, 2, '2038-09-01T06:59:59+00:00'),
    ('2021-01-31T00:00:01-08:00', 2, 3, 5, '2031-02-01T07:59:59+00:00')
]
# testdata pattern is ({desc}, {registration_ts}, {renew_count}, {expiry_ts})
TEST_DATA_EXPIRY_RENEW_RL = [
    ('Registration', '2021-08-31T00:00:01-07:00', 0, '2022-02-27T07:59:59+00:00'),
    ('1 renewal', '2021-08-31T00:00:01-07:00', 1, '2022-08-26T06:59:59+00:00'),
    ('2 renewals', '2021-08-31T00:00:01-07:00', 2, '2023-02-22T07:59:59+00:00')
]
# testdata pattern is ({desc}, {renew_count}, {expiry_days})
TEST_DATA_EXPIRY_RL_DAYS = [
    ('Registration', 0, 180),
    ('1 renewal', 1, 360),
    ('2 renewals', 2, 540),
    ('3 renewals', 3, 720)
]

# testdata pattern is ({desc}, {registration_ts}, {life_years}, {hour}, {expiry_ts})
TEST_DATA_EXPIRY_REGISTRATION = [
    ('Daylight savings', '2021-08-31T12:00:01-07:00', 5, 6, '2026-09-01T06:59:59+00:00'),
    ('Daylight savings after 5 PM', '2021-08-31T17:00:01-07:00', 5, 6, '2026-09-01T06:59:59+00:00'),
    ('No daylight savings', '2021-01-31T13:00:01-08:00', 10, 7, '2031-02-01T07:59:59+00:00'),
    ('No daylight savings after 4 PM', '2021-01-31T16:00:01-08:00', 10, 7, '2031-02-01T07:59:59+00:00')
]
# testdata pattern is ({desc}, {utc_ts}, {local_ts})
TEST_DATA_LOCAL_TIMEZONE = [
    ('Daylight savings', '2021-09-01T06:59:59-00:00', '2021-08-31T23:59:59-07:00'),
    ('No daylight savings', '2021-02-01T07:59:59-00:00', '2021-01-31T23:59:59-08:00')
]
# testdata pattern is ({financing_ts}, {renewal_ts}, today_offset, valid)
TEST_DATA_COURT_ORDER_DATE = [
    ('2021-08-31T00:00:01-07:00', '2021-08-31T00:00:01-07:00', 0, True),
    ('2021-08-31T00:00:01-07:00', '2021-08-30T00:00:01-07:00', 0, False),
    ('2021-08-31T00:00:01-07:00', None, -1, True),
    ('2021-08-31T00:00:01-07:00', None, 0, True),
    ('2021-08-31T00:00:01-07:00', None, 1, False),
]
# testdata pattern is ({change_type}, {is_general_collateral})
TEST_DATA_AMENDMENT_CHANGE_TYPE = [
    (model_utils.REG_TYPE_AMEND, False),
    (model_utils.REG_TYPE_AMEND_COURT, False),
    (model_utils.REG_TYPE_AMEND_SUBSTITUTION_COLLATERAL, False),
    (model_utils.REG_TYPE_AMEND_ADDITION_COLLATERAL, False),
    (model_utils.REG_TYPE_AMEND_SUBSTITUTION_COLLATERAL, True),
    (model_utils.REG_TYPE_AMEND_ADDITION_COLLATERAL, True),
    (model_utils.REG_TYPE_AMEND_DEBTOR_RELEASE, False),
    (model_utils.REG_TYPE_AMEND_DEBTOR_TRANSFER, False),
    (model_utils.REG_TYPE_AMEND_PARIAL_DISCHARGE, False),
    (model_utils.REG_TYPE_AMEND_SP_TRANSFER, False)
]
# testdata pattern is ({desc}, {reg_num}, {doc_name})
TEST_DATA_DOC_STORAGE_NAME = [
    ('Financing', 'TEST0001', 'ppsalien-200000000-TEST0001.pdf'),
    ('Discharge', 'TEST00D4', 'discharge-200000004-TEST00D4.pdf'),
    ('Renewal', 'TEST00R5', 'renewal-200000006-TEST00R5.pdf'),
    ('Change', 'TEST0008', 'change-200000009-TEST0008.pdf'),
    ('Amendment', 'TEST0007', 'amendment-200000008-TEST0007.pdf')
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


@pytest.mark.parametrize('desc,renew_count,expiry_days', TEST_DATA_EXPIRY_RL_DAYS)
def test_expiry_rl_days(session, desc, renew_count, expiry_days):
    """Assert that computing multiple renewal days to expiry works as expected."""
    expiry_test = model_utils.expiry_dt_repairer_lien()
    now = model_utils.now_ts()
    # print(model_utils.format_ts(expiry_test))
    if renew_count > 0:
        for x in range(renew_count):
            expiry_test = model_utils.expiry_dt_repairer_lien(expiry_test)
            # print(model_utils.format_ts(expiry_test))
    ts_delta = expiry_test - now
    assert ts_delta.days == expiry_days


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


@pytest.mark.parametrize('desc,registration_ts,life_years,hour,expiry', TEST_DATA_EXPIRY_REGISTRATION)
def test_expiry_dt_from_registration(session, desc, registration_ts, life_years, hour, expiry):
    """Assert that creating an expiry timestamp from a registration timestamp is performing as expected."""
    test_ts = model_utils.ts_from_iso_format(registration_ts)
    expiry_ts = model_utils.expiry_dt_from_registration(test_ts, life_years)
    new_expiry = model_utils.format_ts(expiry_ts)
    print(new_expiry)
    assert expiry_ts.year - test_ts.year == life_years
    assert expiry_ts.hour == hour
    assert expiry_ts.minute == 59
    assert expiry_ts.second == 59
    assert new_expiry == expiry


@pytest.mark.parametrize('desc,utc_ts,local_ts', TEST_DATA_LOCAL_TIMEZONE)
def test_to_local_timezone(session, desc, utc_ts, local_ts):
    """Assert that converting UTC time to local time is performing as expected."""
    adjusted_ts = model_utils.to_local_timestamp(model_utils.ts_from_iso_format(utc_ts))
    local_iso = adjusted_ts.isoformat()
    print(utc_ts + ' ' + local_iso + ' ' + local_ts)
    assert adjusted_ts.hour == 23
    assert adjusted_ts.minute == 59
    assert adjusted_ts.second == 59
    assert local_iso == local_ts


@pytest.mark.parametrize('change_type, is_general_collateral', TEST_DATA_AMENDMENT_CHANGE_TYPE)
def test_amendment_change_type(change_type, is_general_collateral):
    """Assert that setting the amendment change type from the amendment data works as expected."""
    json_data = copy.deepcopy(AMENDMENT_STATEMENT)
    if change_type != model_utils.REG_TYPE_AMEND_COURT:
        del json_data['courtOrderInformation']
    if change_type != model_utils.REG_TYPE_AMEND:
        del json_data['addTrustIndenture']
        del json_data['removeTrustIndenture']

    if change_type in (model_utils.REG_TYPE_AMEND_ADDITION_COLLATERAL,
                       model_utils.REG_TYPE_AMEND_SUBSTITUTION_COLLATERAL,
                       model_utils.REG_TYPE_AMEND_PARIAL_DISCHARGE):
        del json_data['addSecuredParties']
        del json_data['deleteSecuredParties']
        del json_data['addDebtors']
        del json_data['deleteDebtors']
    if change_type == model_utils.REG_TYPE_AMEND_PARIAL_DISCHARGE:
        del json_data['addVehicleCollateral']
        del json_data['addGeneralCollateral']
        del json_data['deleteGeneralCollateral']
    elif change_type == model_utils.REG_TYPE_AMEND_ADDITION_COLLATERAL:
        del json_data['deleteVehicleCollateral']
        del json_data['deleteGeneralCollateral']
        if is_general_collateral:
            del json_data['addVehicleCollateral']
        else:
            del json_data['addGeneralCollateral']
    elif change_type == model_utils.REG_TYPE_AMEND_SUBSTITUTION_COLLATERAL:
        if is_general_collateral:
            del json_data['addVehicleCollateral']
            del json_data['deleteVehicleCollateral']
        else:
            del json_data['addGeneralCollateral']
            del json_data['deleteGeneralCollateral']
    if change_type in (model_utils.REG_TYPE_AMEND_DEBTOR_RELEASE,
                       model_utils.REG_TYPE_AMEND_DEBTOR_TRANSFER,
                       model_utils.REG_TYPE_AMEND_SP_TRANSFER):
        del json_data['addVehicleCollateral']
        del json_data['deleteVehicleCollateral']
        del json_data['addGeneralCollateral']
        del json_data['deleteGeneralCollateral']
    if change_type == model_utils.REG_TYPE_AMEND_DEBTOR_RELEASE:
        del json_data['addSecuredParties']
        del json_data['deleteSecuredParties']
        del json_data['addDebtors']
    elif change_type == model_utils.REG_TYPE_AMEND_DEBTOR_TRANSFER:
        del json_data['addSecuredParties']
        del json_data['deleteSecuredParties']
    elif change_type == model_utils.REG_TYPE_AMEND_SP_TRANSFER:
        del json_data['addDebtors']
        del json_data['deleteDebtors']

    # print(json_data)
    type = model_utils.amendment_change_type(json_data)
    assert type == change_type


def test_cleanup_amendment():
    """Assert that removing empty lists/arrays from amendment data works as expected."""
    json_data = copy.deepcopy(AMENDMENT_STATEMENT)
    # print(json_data)
    json_data = model_utils.cleanup_amendment(json_data)
    assert 'addVehicleCollateral' in json_data
    assert 'deleteVehicleCollateral' in json_data
    assert 'addGeneralCollateral' in json_data
    assert 'deleteGeneralCollateral' in json_data
    assert 'addSecuredParties' in json_data
    assert 'deleteSecuredParties' in json_data
    assert 'addDebtors' in json_data
    assert 'deleteDebtors' in json_data
    json_data['addVehicleCollateral'] = []
    json_data['deleteVehicleCollateral'] = []
    json_data['addGeneralCollateral'] = []
    json_data['deleteGeneralCollateral'] = []
    json_data['addSecuredParties'] = []
    json_data['deleteSecuredParties'] = []
    json_data['addDebtors'] = []
    json_data['deleteDebtors'] = []
    json_data = model_utils.cleanup_amendment(json_data)
    assert 'addVehicleCollateral' not in json_data
    assert 'deleteVehicleCollateral' not in json_data
    assert 'addGeneralCollateral' not in json_data
    assert 'deleteGeneralCollateral' not in json_data
    assert 'addSecuredParties' not in json_data
    assert 'deleteSecuredParties' not in json_data
    assert 'addDebtors' not in json_data
    assert 'deleteDebtors' not in json_data


@pytest.mark.parametrize('financing_ts,renewal_ts,today_offset,valid', TEST_DATA_COURT_ORDER_DATE)
def test_valid_court_order_date(session, financing_ts, renewal_ts, today_offset, valid):
    """Assert that checking a RL renewal court order date works as expected."""
    reg_ts = model_utils.ts_from_iso_format(financing_ts)
    test_renew_ts = renewal_ts
    if not test_renew_ts:
        now_offset = model_utils.now_ts_offset(today_offset, True)
        test_renew_ts = model_utils.format_ts(now_offset)
    test_valid = model_utils.valid_court_order_date(reg_ts, test_renew_ts)
    # print(financing_ts + ' ' + test_renew_ts)
    assert test_valid == valid


@pytest.mark.parametrize('desc,reg_num,doc_name', TEST_DATA_DOC_STORAGE_NAME)
def test_doc_storage_name(session, desc, reg_num, doc_name):
    """Assert that building a storage document name works as expected."""
    registration: Registration = Registration.find_by_registration_number(reg_num, 'PS12345', True)
    test_name = registration.registration_ts.isoformat()[:10]
    test_name = test_name.replace('-', '/') + '/' + registration.registration_type_cl.lower() + \
                '-' + str(registration.id) + '-' + registration.registration_num + '.pdf'
    name = model_utils.get_doc_storage_name(registration)
    assert test_name == name


def test_search_doc_storage_name(session):
    """Assert that building a search storage document name works as expected."""
    search: SearchRequest = SearchRequest(id=2000, search_ts=model_utils.now_ts())
    test_name = search.search_ts.isoformat()[:10]
    test_name = test_name.replace('-', '/') + '/search-results-report-2000.pdf'
    name = model_utils.get_search_doc_storage_name(search)
    assert test_name == name
