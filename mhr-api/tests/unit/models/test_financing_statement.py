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

"""Tests to assure the Financing Statement Model.

Test-Suite to ensure that the Financing Statement Model is working as expected.
"""
from http import HTTPStatus

import pytest

from mhr_api.models import FinancingStatement
from mhr_api.exceptions import BusinessException


# testdata pattern is ({registration type}, {account ID}, {create draft})
TEST_REGISTRATION_DATA = [
    ('SA', 'PS12345', False),
    ('SA', 'PS12345', True),
    ('RL', 'PS12345', False),
    ('OT', 'PS12345', False),
    ('SA', None, False)
]
# testdata pattern is ({description}, {registration number}, {account ID}, {http status}, {is staff}, {is create})
TEST_REGISTRATION_NUMBER_DATA = [
    ('Valid', 'TEST0001', 'PS12345', HTTPStatus.OK, False, True),
    ('Valid added from another account', 'TEST0019', 'PS12345', HTTPStatus.OK, False, True),
    ('Invalid reg num', 'TESTXXXX', 'PS12345', HTTPStatus.NOT_FOUND, False, True),
    ('Expired non-staff', 'TEST0013', 'PS12345', HTTPStatus.BAD_REQUEST, False, True),
    ('Discharged non-staff', 'TEST0014', 'PS12345', HTTPStatus.BAD_REQUEST, False, True),
    ('Mismatch staff', 'TEST0001', 'PS1234X', HTTPStatus.OK, True, True),
    ('Expired staff not create', 'TEST0013', 'PS12345', HTTPStatus.OK, True, False),
    ('Expired staff create', 'TEST0013', 'PS12345', HTTPStatus.BAD_REQUEST, True, True),
    ('Discharged staff not create', 'TEST0014', 'PS12345', HTTPStatus.OK, True, False),
    ('Discharged staff create', 'TEST0014', 'PS12345', HTTPStatus.BAD_REQUEST, True, True),
]
# testdata pattern is ({reg_num}, {reg_type}, {current_view}, {expiry_ts}, {life})
TEST_VERIFICATION_EXPIRY_DATA = [
    ('TEST0016', 'SA', False, '2026-09-04T06:59:59+00:00', 5),
    ('TEST0016', 'SA', True, '2041-09-04T06:59:59+00:00', 20)
]

# testdata pattern is ({reg_num}, {reg_type}, {expiry_ts}, {renewal2_ts}, {renewal1_ts})
TEST_HISTORY_EXPIRY_DATA = [
    ('TEST0016', 'SA', '2041-09-04T06:59:59+00:00', '2036-09-04T06:59:59+00:00', '2041-09-04T06:59:59+00:00')
]


def test_find_by_id(session):
    """Assert that find financing statement by ID contains all expected elements."""
    result = FinancingStatement.find_by_id(200000000)
    assert result
    assert result.id
    if result:
        json_data = result.json
        assert json_data['type'] == 'SA'
        assert json_data['baseRegistrationNumber'] == 'TEST0001'
        assert json_data['registeringParty']
        assert json_data['createDateTime']
        assert json_data['debtors'][0]
        assert json_data['securedParties'][0]
        assert json_data['generalCollateral'][0]
        assert json_data['vehicleCollateral'][0]


def test_find_by_financing_id(session):
    """Assert that find financing statement by financing statement ID contains all expected elements."""
    result = FinancingStatement.find_by_financing_id(200000000)
    assert result
    assert result.id
    if result:
        result.mark_update_json = True
        json_data = result.json
        # print(json_data)
        assert json_data['type'] == 'SA'
        assert json_data['baseRegistrationNumber'] == 'TEST0001'
        assert json_data['registeringParty']
        assert json_data['createDateTime']
        assert json_data['debtors'][0]
        assert json_data['securedParties'][0]
        assert json_data['generalCollateral'][0]
        assert json_data['vehicleCollateral'][0]
        assert json_data['expiryDate']
        assert json_data['lifeYears']
        assert json_data['trustIndenture']


@pytest.mark.parametrize('desc,reg_number,account_id,status,staff,create', TEST_REGISTRATION_NUMBER_DATA)
def test_find_by_registration_number(session, desc, reg_number, account_id, status, staff, create):
    """Assert that a fetch financing statement by registration number works as expected."""
    if status == HTTPStatus.OK:
        statement = FinancingStatement.find_by_registration_number(reg_number, account_id, staff, create)
        assert statement
        result = statement.json
        assert result['type'] == 'SA'
        assert result['baseRegistrationNumber'] == reg_number
        assert result['registeringParty']
        assert result['createDateTime']
        assert result['debtors'][0]
        assert result['securedParties'][0]
        if reg_number == 'TEST0001':
            assert result['vehicleCollateral'][0]
        assert result['expiryDate']
        assert result['lifeYears']
        if reg_number == 'TEST0001':
            assert result['generalCollateral'][0]
            assert result['trustIndenture']
        if statement.current_view_json and reg_number == 'TEST0001':
            assert result['courtOrderInformation']
    else:
        with pytest.raises(BusinessException) as request_err:
            FinancingStatement.find_by_registration_number(reg_number, account_id, staff, create)

        # check
        assert request_err
        assert request_err.value.status_code == status


def test_current_json(session):
    """Assert that financing statement JSON contains expected current view elements."""
    result = FinancingStatement.find_by_id(200000000)
    result.mark_update_json = True
    result.current_view_json = True
    json_data = result.json
    assert len(json_data['debtors']) >= 2
    assert len(json_data['securedParties']) >= 2
    assert len(json_data['generalCollateral']) >= 2
    assert len(json_data['vehicleCollateral']) >= 2
    assert 'added' in json_data['debtors'][1]
    assert 'added' in json_data['securedParties'][1]
    assert 'added' not in json_data['generalCollateral'][1]
    assert 'added' in json_data['vehicleCollateral'][1]
    assert json_data['debtors'][1]['added']
    assert json_data['securedParties'][1]['added']
    assert json_data['vehicleCollateral'][1]['added']


@pytest.mark.parametrize('reg_num, reg_type, expiry_ts, renewal2_ts, renewal1_ts', TEST_HISTORY_EXPIRY_DATA)
def test_renewal_expiry(session, reg_num, reg_type, expiry_ts, renewal2_ts, renewal1_ts):
    """Assert that a financing statement with renewal history returns the expected expiry dates."""
    statement = FinancingStatement.find_by_registration_number(reg_num, 'PS12345', True)
    statement.include_changes_json = True
    json_data = statement.json
    # print(json_data)
    assert 'expiryDate' in json_data
    assert json_data['expiryDate'] == expiry_ts
    assert 'changes' in json_data
    assert len(json_data['changes']) == 2
    assert json_data['changes'][0]['expiryDate'] == renewal1_ts
    assert json_data['changes'][1]['expiryDate'] == renewal2_ts


@pytest.mark.parametrize('reg_num, reg_type, current_view, expiry_ts, life', TEST_VERIFICATION_EXPIRY_DATA)
def test_verification_expiry(session, reg_num, reg_type, current_view, expiry_ts, life):
    """Assert that a financing statement with renewal history returns the expected verification expiry dates."""
    statement = FinancingStatement.find_by_registration_number(reg_num, 'PS12345', True)
    statement.current_view_json = current_view
    json_data = statement.json
    # print(json_data)
    assert 'expiryDate' in json_data
    assert json_data['expiryDate'] == expiry_ts
    if life:
        assert 'lifeYears' in json_data
        assert json_data['lifeYears'] == life
