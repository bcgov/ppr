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

"""Tests to assure the Registration Model.

Test-Suite to ensure that the Registration Model is working as expected.
"""
from http import HTTPStatus

import pytest

from mhr_api.exceptions import BusinessException
from mhr_api.models import Registration, GeneralCollateral
from mhr_api.models import registration_utils as registration_utils
# from mhr_api.services.authz import STAFF_ROLE, BCOL_HELP, GOV_ACCOUNT_ROLE


# testdata pattern is ({description}, {registration number}, {account ID}, {http status}, {is staff}, {base_reg_num})
TEST_REGISTRATION_NUMBER_DATA = [
    ('Valid Renewal', 'TEST00R5', 'PS12345', HTTPStatus.OK, False, 'TEST0005'),
    ('Valid Change', 'TEST0010', 'PS12345', HTTPStatus.OK, False, 'TEST0001'),
    ('Valid Amendment', 'TEST0007', 'PS12345', HTTPStatus.OK, False, 'TEST0001'),
    ('Valid Amendment added another account', 'TEST0019AM', 'PS12345', HTTPStatus.OK, False, 'TEST0019'),
    ('Invalid reg num', 'TESTXXXX', 'PS12345', HTTPStatus.NOT_FOUND, False, 'TEST0005'),
    ('Mismatch account id staff', 'TEST00R5', 'PS1234X', HTTPStatus.OK, True, 'TEST0005'),
    ('Mismatch registration numbers staff', 'TEST00R5', 'PS12345', HTTPStatus.OK, True, 'TEST0001'),
    ('Discharged staff', 'TEST0D14', 'PS12345', HTTPStatus.OK, True, 'TEST0014')
]
# testdata pattern is ({base_reg_num}, {reg_num}, {reg_num_name})
TEST_VERIFICATION_DATA = [
    ('TEST0004', 'TEST00D4', 'dischargeRegistrationNumber'),
    ('TEST0005', 'TEST00R5', 'renewalRegistrationNumber'),
    ('TEST0018', 'TEST0018A3', 'amendmentRegistrationNumber'),
    ('TEST0018', 'TEST0018A2', 'amendmentRegistrationNumber'),
    ('TEST0001', 'TEST0009', 'changeRegistrationNumber')
]


def test_find_by_id(session):
    """Assert that find registration by ID contains all expected elements."""
    registration = Registration.find_by_id(200000000)
    assert registration
    assert registration.id == 200000000
    assert registration.registration_num == 'TEST0001'
    assert registration.registration_type
    assert registration.registration_ts
    assert registration.account_id
    assert registration.client_reference_id


def test_find_by_id_as(session):
    """Assert that find an amemdment registration by ID contains all expected elements."""
    registration = Registration.find_by_id(200000008)
    assert registration
    assert registration.id == 200000008
    assert registration.registration_num
    assert registration.registration_type == 'CO'
    assert registration.financing_id
    json_data = registration.json
    assert json_data['changeType'] == 'CO'
    assert json_data['courtOrderInformation']
    assert json_data['addDebtors']
    assert len(json_data['addDebtors']) == 1
    assert json_data['addSecuredParties']
    assert len(json_data['addSecuredParties']) == 1
    assert json_data['addGeneralCollateral']
    assert len(json_data['addGeneralCollateral']) == 1
    assert json_data['addVehicleCollateral']
    assert len(json_data['addVehicleCollateral']) == 1
    assert json_data['deleteDebtors']
    assert len(json_data['deleteDebtors']) == 1
    assert json_data['deleteSecuredParties']
    assert len(json_data['deleteSecuredParties']) == 1
    assert json_data['deleteGeneralCollateral']
    assert len(json_data['deleteGeneralCollateral']) == 1
    assert json_data['deleteVehicleCollateral']
    assert len(json_data['deleteVehicleCollateral']) == 1
    assert 'documentId' not in json_data


def test_find_by_id_cs_dt(session):
    """Assert that find an change registration DT by ID contains all expected elements."""
    registration = Registration.find_by_id(200000009)
    assert registration
    assert registration.id == 200000009
    assert registration.registration_num
    assert registration.registration_type == 'DT'
    assert registration.financing_id
    json_data = registration.json
    assert json_data['changeType'] == 'DT'
    assert json_data['addDebtors']
    assert len(json_data['addDebtors']) == 1
    assert json_data['deleteDebtors']
    assert len(json_data['deleteDebtors']) == 1
    assert 'addSecuredParties' not in json_data
    assert 'addGeneralCollateral' not in json_data
    assert 'addVehicleCollateral' not in json_data
    assert 'deleteSecuredParties' not in json_data
    assert 'deleteGeneralCollateral' not in json_data
    assert 'deleteVehicleCollateral' not in json_data
    assert 'documentId' not in json_data


def test_find_by_id_cs_st(session):
    """Assert that find an change registration ST by ID contains all expected elements."""
    registration = Registration.find_by_id(200000010)
    assert registration
    assert registration.id == 200000010
    assert registration.registration_num
    assert registration.registration_type == 'ST'
    assert registration.financing_id
    json_data = registration.json
    assert json_data['changeType'] == 'ST'
    assert json_data['addSecuredParties']
    assert len(json_data['addSecuredParties']) == 1
    assert json_data['deleteSecuredParties']
    assert len(json_data['deleteSecuredParties']) == 1
    assert 'addDebtors' not in json_data
    assert 'addGeneralCollateral' not in json_data
    assert 'addVehicleCollateral' not in json_data
    assert 'deleteDebtors' not in json_data
    assert 'deleteGeneralCollateral' not in json_data
    assert 'deleteVehicleCollateral' not in json_data


def test_find_by_id_cs_su(session):
    """Assert that find an change registration SU by ID contains all expected elements."""
    registration = Registration.find_by_id(200000011)
    assert registration
    assert registration.id == 200000011
    assert registration.registration_num
    assert registration.registration_type == 'SU'
    assert registration.financing_id
    json_data = registration.json
    assert json_data['changeType'] == 'SU'
    assert json_data['addVehicleCollateral']
    assert len(json_data['addVehicleCollateral']) >= 1
    assert json_data['deleteVehicleCollateral']
    assert len(json_data['deleteVehicleCollateral']) == 1
    assert json_data['addGeneralCollateral']
    assert len(json_data['addGeneralCollateral']) == 1
    assert json_data['deleteGeneralCollateral']
    assert len(json_data['deleteGeneralCollateral']) == 1
    assert 'addDebtors' not in json_data
    assert 'deleteDebtors' not in json_data
    assert 'addSecuredParties' not in json_data
    assert 'deleteSecuredParties' not in json_data


@pytest.mark.parametrize('desc,reg_number,account_id,status,staff,base_reg_number', TEST_REGISTRATION_NUMBER_DATA)
def test_find_by_registration_number(session, desc, reg_number, account_id, status, staff, base_reg_number):
    """Assert that a fetch financing statement by registration number works as expected."""
    if status == HTTPStatus.OK:
        registration = Registration.find_by_registration_number(reg_number, account_id, staff, base_reg_number)
        assert registration.id >= 200000000
        assert registration.registration_num == reg_number
        assert registration.base_registration_num
        assert registration.registration_type
        assert registration.registration_type_cl
        assert registration.registration_ts
        assert registration.account_id
        # assert registration.client_reference_id
    else:
        with pytest.raises(BusinessException) as request_err:
            Registration.find_by_registration_number(reg_number, account_id, staff, base_reg_number)

        # check
        assert request_err
        assert request_err.value.status_code == status
        print(request_err.value.error)


def test_find_by_registration_num_fs(session):
    """Assert that find a financing statement by registration number contains all expected elements."""
    registration = Registration.find_by_registration_number('TEST0001', 'PS12345', False)
    assert registration
    assert registration.id == 200000000
    assert registration.registration_num == 'TEST0001'
    assert registration.registration_type
    assert registration.registration_ts
    assert registration.account_id
    assert registration.client_reference_id


def test_find_by_registration_num_ds(session):
    """Assert that find a discharge statement by registration number contains all expected elements."""
    registration = Registration.find_by_registration_number('TEST00D4', 'PS12345', True)
    assert registration
    assert registration.id == 200000004
    assert registration.registration_num == 'TEST00D4'
    assert registration.registration_type == 'DC'
    assert registration.registration_ts
    assert registration.account_id
    assert registration.client_reference_id
    assert registration.parties
    assert len(registration.parties) == 1
    assert registration.financing_statement

    json_data = registration.json
    assert json_data['dischargeRegistrationNumber']
    assert json_data['createDateTime']
    assert json_data['registeringParty']


def test_find_by_registration_num_gc(session):
    """Assert that find an amendment with general collateral changes contains all expected elements."""
    registration = Registration.find_by_registration_number('TEST0018A3', 'PS12345', True)
    assert registration
    assert registration.registration_num == 'TEST0018A3'
    assert registration.registration_type == 'AM'
    assert registration.general_collateral
    collateral = registration.general_collateral
    assert len(collateral) == 2
    json_data = registration.json
    assert len(json_data['addGeneralCollateral']) == 1
    assert json_data['addGeneralCollateral'][0]['collateralId'] == 200000009
    assert 'addedDateTime' in json_data['addGeneralCollateral'][0]
    assert 'description' in json_data['addGeneralCollateral'][0]
    assert 'descriptionAdd' not in json_data['addGeneralCollateral'][0]
    assert 'descriptionDelete' not in json_data['addGeneralCollateral'][0]
    assert len(json_data['deleteGeneralCollateral']) == 1
    assert json_data['deleteGeneralCollateral'][0]['collateralId'] == 200000010
    assert 'addedDateTime' in json_data['deleteGeneralCollateral'][0]
    assert 'description' in json_data['deleteGeneralCollateral'][0]
    assert 'descriptionAdd' not in json_data['deleteGeneralCollateral'][0]
    assert 'descriptionDelete' not in json_data['deleteGeneralCollateral'][0]


def test_find_by_id_invalid(session):
    """Assert that find registration by non-existent ID returns the expected result."""
    registration = Registration.find_by_id(100000234)
    assert not registration


@pytest.mark.parametrize('base_reg_num,reg_num,reg_num_name', TEST_VERIFICATION_DATA)
def test_verification_json(session, base_reg_num, reg_num, reg_num_name):
    """Assert that generating verification statement json works as expected."""
    registration = Registration.find_by_registration_number(reg_num, 'PS12345', True)
    json_data = registration.verification_json(reg_num_name)
    assert json_data[reg_num_name] == reg_num
    assert json_data['baseRegistrationNumber'] == base_reg_num
    assert len(json_data['changes']) >= 1
    assert json_data['changes'][0][reg_num_name] == reg_num
