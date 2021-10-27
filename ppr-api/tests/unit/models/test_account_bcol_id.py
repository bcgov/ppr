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

"""Tests to assure the Account BCOL ID Model.

Test-Suite to ensure that the Account BCOL ID Model is working as expected.
"""
import pytest

from ppr_api.models import AccountBcolId


# testdata pattern is ({description}, {is_crown_charge}, {account_id})
TEST_DATA_CROWN_CHARGE = [
    ('Exists crown charge', True, 'PS12345'),
    ('Exists not crown charge', False, 'PS0001'),
    ('Does not exist', False, 'PS1234X')
]


def test_find_by_id(session):
    """Assert that find account bcol id mapping by ID contains all expected elements."""
    account_bcol_id = AccountBcolId.find_by_id(200000000)
    assert account_bcol_id
    assert account_bcol_id.id == 200000000
    assert account_bcol_id.account_id == 'PS12345'
    assert account_bcol_id.bconline_account == 200000000
    assert account_bcol_id.crown_charge_ind == AccountBcolId.CROWN_CHARGE_YES


def test_find_by_account_id(session):
    """Assert that find account bcol id mapping by account ID contains all expected elements."""
    account_bcol_id = AccountBcolId.find_by_account_id('PS12345')
    assert account_bcol_id
    assert len(account_bcol_id) == 2


def test_find_by_account_bcol_number(session):
    """Assert that find account bcol id mapping by account and bcol number contains all expected elements."""
    account_bcol_id = AccountBcolId.find_by_account_id_bcol_number('PS12345', 200000000)
    assert account_bcol_id
    assert account_bcol_id.id == 200000000
    assert account_bcol_id.account_id == 'PS12345'
    assert account_bcol_id.bconline_account == 200000000


def test_save(session):
    """Assert that saving an an account bcol id mapping works as expected."""
    account_bcol_id = AccountBcolId(account_id='PS12345', bconline_account=200000004)
    account_bcol_id.save()
    assert account_bcol_id.id > 0
    test_mapping = AccountBcolId.find_by_account_id_bcol_number('PS12345', 200000004)
    assert test_mapping
    assert test_mapping.account_id == 'PS12345'
    assert test_mapping.bconline_account == 200000004


def test_delete(session):
    """Assert that deleting an account bcol id mapping works as expected."""
    account_bcol_id = AccountBcolId(account_id='PS12345', bconline_account=200000003)
    account_bcol_id.save()
    assert account_bcol_id.id > 0
    test_mapping = AccountBcolId.find_by_account_id_bcol_number('PS12345', 200000003)
    assert test_mapping
    AccountBcolId.delete(test_mapping.account_id, test_mapping.bconline_account)
    test_mapping = AccountBcolId.find_by_account_id_bcol_number('PS12345', 200000003)
    assert not test_mapping


def test_find_by_id_invalid(session):
    """Assert that find account bcol id mapping by an invalid ID returns the expected result."""
    account_bcol_id = AccountBcolId.find_by_id(300000000)
    assert not account_bcol_id


def test_find_by_account_id_invalid(session):
    """Assert that find account bcol id mapping by and invalid account ID returns the expected result."""
    account_bcol_id = AccountBcolId.find_by_account_id('PS1234X')
    assert not account_bcol_id


def test_find_by_account_bcol_number_invalid(session):
    """Assert that find account bcol id mapping by an invalid account and bcol number returns the expected result."""
    account_bcol_id = AccountBcolId.find_by_account_id_bcol_number('PS12345', 300000000)
    assert not account_bcol_id


@pytest.mark.parametrize('desc,is_crown_charge,account_id', TEST_DATA_CROWN_CHARGE)
def test_crown_charge_account(session, desc, is_crown_charge, account_id):
    """Assert that crown_charge_account behaves as expected."""
    crown_charge_account = AccountBcolId.crown_charge_account(account_id)
    assert crown_charge_account == is_crown_charge
