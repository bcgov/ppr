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

"""Tests to assure the MHR Extra Registrations Model.

Test-Suite to ensure that the MHR Extra Registrations Model is working as expected.
"""
from mhr_api.models import MhrExtraRegistration

import pytest


# testdata pattern is ({account_id}, {count})
TEST_ACCOUNT_REG_DATA = [
    ('PS12345', 2),
    ('TESTXX', 0)
]


def test_find_by_id(session):
    """Assert that find user extra validation by ID contains all expected elements."""
    registration = MhrExtraRegistration.find_by_id(200000000)
    assert registration
    assert registration.id == 200000000
    assert registration.account_id == 'PS12345'
    assert registration.mhr_number == 'TEST01'


def test_find_by_mhr_number(session):
    """Assert that find user extra registration by MHR number contains all expected elements."""
    registration = MhrExtraRegistration.find_by_mhr_number('TEST01', 'PS12345')
    assert registration
    assert registration.id == 200000000
    assert registration.account_id == 'PS12345'
    assert registration.mhr_number == 'TEST01'


def test_save_add(session):
    """Assert that saving an added user extra registration works as expected."""
    registration = MhrExtraRegistration(account_id='PS12345', mhr_number='TEST02')
    registration.save()
    assert registration.id > 0
    MhrExtraRegistration.delete('TEST02', 'PS12345')


def test_save_remove(session):
    """Assert that saving a removed user extra registration works as expected."""
    registration = MhrExtraRegistration(account_id='PS12345', mhr_number='TEST05')
    registration.removed_ind = MhrExtraRegistration.REMOVE_IND
    registration.save()
    assert registration.id > 0
    reg2 = MhrExtraRegistration.find_by_mhr_number('TEST05', 'PS12345')
    assert reg2
    assert reg2.removed_ind == MhrExtraRegistration.REMOVE_IND
    MhrExtraRegistration.delete('TEST05', 'PS12345')
    registration = MhrExtraRegistration.find_by_mhr_number('TEST05', 'PS12345')
    assert not registration


def test_delete(session):
    """Assert that deleting a user extra registration works as expected."""
    registration = MhrExtraRegistration(account_id='PS12345', mhr_number='TEST06')
    registration.save()
    assert registration.id > 0
    test_reg = MhrExtraRegistration.find_by_mhr_number('TEST06', 'PS12345')
    assert test_reg
    MhrExtraRegistration.delete('TEST06', 'PS12345')
    test_reg = MhrExtraRegistration.find_by_mhr_number('TEST06', 'PS12345')
    assert not test_reg


def test_find_by_mhr_number_invalid(session):
    """Assert that find user extra registration by non-existent MHR number returns the expected result."""
    registration = MhrExtraRegistration.find_by_mhr_number('TESTXX', 'PS12345')
    assert not registration


def test_find_by_mhr_number_invalid_account(session):
    """Assert that find user extra registration by non-existent account id returns the expected result."""
    registration = MhrExtraRegistration.find_by_mhr_number('TEST01', 'XXXXXX')
    assert not registration


@pytest.mark.parametrize('account_id, count', TEST_ACCOUNT_REG_DATA)
def test_find_by_account_id(session, account_id, count):
    """Assert that finding account extra registrations works as expected."""
    extra_reg_list = MhrExtraRegistration.find_by_account_id(account_id)
    if count > 0:
        assert extra_reg_list
        assert len(extra_reg_list) >= count
        for reg in extra_reg_list:
            assert reg.id > 0
            assert reg.account_id
            assert reg.mhr_number
    else:
        assert not extra_reg_list


@pytest.mark.parametrize('account_id, count', TEST_ACCOUNT_REG_DATA)
def test_find_mhr_numbers_by_account_id(session, account_id, count):
    """Assert that finding account extra registration mhr numbers works as expected."""
    mhr_list = MhrExtraRegistration.find_mhr_numbers_by_account_id(account_id)
    if count > 0:
        assert mhr_list
        assert len(mhr_list) >= count
        for mhr in mhr_list:
            assert mhr['mhr_number']
    else:
        assert not mhr_list
