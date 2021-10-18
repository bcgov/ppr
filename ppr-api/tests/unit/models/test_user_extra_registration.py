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

"""Tests to assure the Trust Indenture Model.

Test-Suite to ensure that the Trust Indenture Model is working as expected.
"""
from ppr_api.models import UserExtraRegistration


def test_find_by_id(session):
    """Assert that find user extra validation by ID contains all expected elements."""
    registration = UserExtraRegistration.find_by_id(200000000)
    assert registration
    assert registration.id == 200000000
    assert registration.account_id == 'PS12345'
    assert registration.registration_number == 'TEST0019'


def test_find_by_registration_number(session):
    """Assert that find user extra registration by registration number contains all expected elements."""
    registration = UserExtraRegistration.find_by_registration_number('TEST0019', 'PS12345')
    assert registration
    assert registration.id == 200000000
    assert registration.account_id == 'PS12345'
    assert registration.registration_number == 'TEST0019'


def test_save_add(session):
    """Assert that saving an added user extra registration works as expected."""
    registration = UserExtraRegistration(account_id='PS12345', registration_number='TEST0019A')
    registration.save()
    assert registration.id > 0
    UserExtraRegistration.delete('TEST0019A', 'PS12345')


def test_save_remove(session):
    """Assert that saving a removed user extra registration works as expected."""
    registration = UserExtraRegistration(account_id='PS12345', registration_number='TEST0005')
    registration.removed_ind = UserExtraRegistration.REMOVE_IND
    registration.save()
    assert registration.id > 0
    reg2 = UserExtraRegistration.find_by_registration_number('TEST0005', 'PS12345')
    assert reg2
    assert reg2.removed_ind == UserExtraRegistration.REMOVE_IND
    UserExtraRegistration.delete('TEST0005', 'PS12345')
    registration = UserExtraRegistration.find_by_registration_number('TEST0005', 'PS12345')
    assert not registration


def test_delete(session):
    """Assert that saving a user extra registration works as expected."""
    registration = UserExtraRegistration(account_id='PS12345', registration_number='TEST0019B')
    registration.save()
    assert registration.id > 0
    test_reg = UserExtraRegistration.find_by_registration_number('TEST0019B', 'PS12345')
    assert test_reg
    UserExtraRegistration.delete('TEST0019B', 'PS12345')
    test_reg = UserExtraRegistration.find_by_registration_number('TEST0019B', 'PS12345')
    assert not test_reg


def test_find_by_reg_num_invalid(session):
    """Assert that find user extra registration by non-existent registration number returns the expected result."""
    registration = UserExtraRegistration.find_by_registration_number('TESTXXXX', 'PS12345')
    assert not registration


def test_find_by_reg_num_invalid_account(session):
    """Assert that find user extra registration by non-existent account id returns the expected result."""
    registration = UserExtraRegistration.find_by_registration_number('TEST0019', 'XXXXXX')
    assert not registration
