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
import copy
from http import HTTPStatus

import pytest
from registry_schemas.example_data.ppr import (
    AMENDMENT_STATEMENT,
    CHANGE_STATEMENT,
    DISCHARGE_STATEMENT,
    DRAFT_AMENDMENT_STATEMENT,
    DRAFT_CHANGE_STATEMENT,
    FINANCING_STATEMENT,
    RENEWAL_STATEMENT,
)

from ppr_api.exceptions import BusinessException
from ppr_api.models import Draft, GeneralCollateralLegacy, FinancingStatement, Registration, utils as model_utils


# testdata pattern is ({description}, {registration number}, {account ID}, {http status}, {is staff}, {base_reg_num})
TEST_REGISTRATION_NUMBER_DATA = [
    ('Valid Renewal', 'TEST00R5', 'PS12345', HTTPStatus.OK, False, 'TEST0005'),
    ('Valid Change', 'TEST0010', 'PS12345', HTTPStatus.OK, False, 'TEST0001'),
    ('Valid Amendment', 'TEST0007', 'PS12345', HTTPStatus.OK, False, 'TEST0001'),
    ('Invalid reg num', 'TESTXXXX', 'PS12345', HTTPStatus.NOT_FOUND, False, 'TEST0005'),
    ('Mismatch account id non-staff', 'TEST00R5', 'PS1234X', HTTPStatus.BAD_REQUEST, False, 'TEST0005'),
    ('Mismatch registration numbers non-staff', 'TEST00R5', 'PS12345', HTTPStatus.BAD_REQUEST, False, 'TEST0001'),
    ('Discharged non-staff', 'TEST0D14', 'PS12345', HTTPStatus.BAD_REQUEST, False, 'TEST0014'),
    ('Mismatch account id staff', 'TEST00R5', 'PS1234X', HTTPStatus.OK, True, 'TEST0005'),
    ('Mismatch registration numbers staff', 'TEST00R5', 'PS12345', HTTPStatus.OK, True, 'TEST0001'),
    ('Discharged staff', 'TEST0D14', 'PS12345', HTTPStatus.OK, True, 'TEST0014')
]
# testdata pattern is ({description}, {account ID}, {collapse results})
TEST_ACCOUNT_REGISTRATION_DATA = [
    ('Default registration format', 'PS12345', False),
    ('Collapsed parent/child registration format', 'PS12345', True)
]
# testdata pattern is ({reg_type}, {life}, {life_infinite}, {expected_life})
TEST_LIFE_EXPIRY_DATA = [
    ('SA', 5, False, 5),
    ('SA', None, True, 99),
    ('RL', 1, False, model_utils.REPAIRER_LIEN_YEARS),
    ('MH', 1, False, model_utils.LIFE_INFINITE),
    ('LT', None, True, model_utils.LIFE_INFINITE),
    ('FR', 5, False, model_utils.LIFE_INFINITE),
    ('OT', None, True, model_utils.LIFE_INFINITE),
    ('ML', 1, False, model_utils.LIFE_INFINITE),
]
# testdata pattern is ({reg_num}, {reg_type}, {expected_ts})
TEST_EXPIRY_DATA = [
    ('TEST0016', 'SA', '2041-09-04T06:59:59+00:00'),
    ('TEST0016R1', 'RE', '2036-09-04T06:59:59+00:00'),
    ('TEST0016R2', 'RE', '2041-09-04T06:59:59+00:00'),
    ('TEST0017', 'RL', '2023-02-23T07:59:59+00:00'),
    ('TEST0017R1', 'RE', '2022-08-27T06:59:59+00:00'),
    ('TEST0017R2', 'RE', '2023-02-23T07:59:59+00:00')
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


@pytest.mark.parametrize('desc,account_id,collapse', TEST_ACCOUNT_REGISTRATION_DATA)
def test_find_all_by_account_id(session, desc, account_id, collapse):
    """Assert that the financing statement summary list by account id first item contains all expected elements."""
    statement_list = Registration.find_all_by_account_id(account_id, collapse)

    assert statement_list
    for statement in statement_list:
        assert statement['registrationNumber']
        assert statement['registrationType']
        assert statement['registrationClass']
        assert statement['registrationDescription']
        assert statement['statusType']
        assert statement['createDateTime']
        assert statement['lastUpdateDateTime']
        assert statement['registeringName']
        assert statement['path']
        if statement['registrationClass'] not in ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN'):
            assert statement['baseRegistrationNumber']
        if not collapse or statement['registrationClass'] in ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN'):
            assert statement['expireDays']
            assert statement['registeringParty']
            assert statement['securedParties']
        if not collapse:
            assert 'changes' not in statement


def test_find_all_by_account_id_no_result(session):
    """Assert that the financing statement summary list by invalid account id works as expected."""
    statement_list = Registration.find_all_by_account_id('XXXXX45')

    assert len(statement_list) == 0


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


def test_find_by_registration_num_legacy_gc(session):
    """Assert that find an amendment statement with legacy general collateral contains all expected elements."""
    registration = Registration.find_by_registration_number('TEST0018A1', 'PS12345', True)
    assert registration
    assert registration.registration_num == 'TEST0018A1'
    assert registration.registration_type == 'AM'
    assert registration.registration_ts
    assert registration.account_id
    assert registration.client_reference_id
    assert registration.parties
    assert len(registration.parties) == 1
    assert registration.financing_statement
    assert registration.general_collateral_legacy
    collateral = registration.general_collateral_legacy
    assert len(collateral) == 1
    assert collateral[0].status == GeneralCollateralLegacy.StatusTypes.ADDED
    json_data = registration.json
    assert len(json_data['addGeneralCollateral']) == 1
    assert json_data['addGeneralCollateral'][0]['collateralId'] == 200000007
    assert 'addedDateTime' in json_data['addGeneralCollateral'][0]
    assert 'added' not in json_data['addGeneralCollateral'][0]
    assert 'legacy' not in json_data['addGeneralCollateral'][0]

    registration = Registration.find_by_registration_number('TEST0018A2', 'PS12345', True)
    assert registration
    assert registration.registration_num == 'TEST0018A2'
    assert registration.general_collateral_legacy
    collateral = registration.general_collateral_legacy
    assert len(collateral) == 1
    assert collateral[0].status == GeneralCollateralLegacy.StatusTypes.DELETED
    json_data = registration.json
    assert len(json_data['deleteGeneralCollateral']) == 1
    assert json_data['deleteGeneralCollateral'][0]['collateralId'] == 200000008
    assert 'addedDateTime' in json_data['deleteGeneralCollateral'][0]
    assert 'added' not in json_data['deleteGeneralCollateral'][0]
    assert 'legacy' not in json_data['deleteGeneralCollateral'][0]


def test_find_by_registration_num_gc(session):
    """Assert that find an amendment with general collateral changes contains all expected elements."""
    registration = Registration.find_by_registration_number('TEST0018A3', 'PS12345', True)
    assert registration
    assert registration.registration_num == 'TEST0018A3'
    assert registration.registration_type == 'AM'
    assert registration.general_collateral
    collateral = registration.general_collateral
    assert len(collateral) == 1
    json_data = registration.json
    assert len(json_data['addGeneralCollateral']) == 1
    assert json_data['addGeneralCollateral'][0]['collateralId'] == 200000009
    assert 'addedDateTime' in json_data['addGeneralCollateral'][0]
    assert 'added' not in json_data['addGeneralCollateral'][0]
    assert 'legacy' not in json_data['addGeneralCollateral'][0]
    assert len(json_data['deleteGeneralCollateral']) == 1
    assert json_data['deleteGeneralCollateral'][0]['collateralId'] == 200000005
    assert 'addedDateTime' in json_data['deleteGeneralCollateral'][0]
    assert 'added' not in json_data['deleteGeneralCollateral'][0]
    assert 'legacy' not in json_data['deleteGeneralCollateral'][0]


def test_find_by_id_invalid(session):
    """Assert that find registration by non-existent ID returns the expected result."""
    registration = Registration.find_by_id(100000234)
    assert not registration


def test_save_discharge(session):
    """Assert that creating a discharge statement contains all expected elements."""
    json_data = copy.deepcopy(DISCHARGE_STATEMENT)
    del json_data['createDateTime']
    del json_data['dischargeRegistrationNumber']
    del json_data['payment']

    financing_statement = FinancingStatement.find_by_financing_id(200000003)
    assert financing_statement

    registration = Registration.create_from_json(json_data,
                                                 'DISCHARGE',
                                                 financing_statement,
                                                 'TEST0003',
                                                 'PS12345')
    # print(str(registration.id))
    # print(registration.document_number)
    # print(registration.registration_num)
    # print(registration.json)
    registration.save()
    assert registration.financing_id == 200000003
    assert registration.id
    assert registration.registration_num
    assert registration.registration_type
    assert registration.registration_ts
    assert registration.account_id
    assert registration.client_reference_id

    result = registration.json
    assert result
    assert result['baseRegistrationNumber']
    assert result['dischargeRegistrationNumber']
    assert result['createDateTime']
    assert result['registeringParty']


def test_save_renewal(session):
    """Assert that creating a renewal statement on a non-RL financing statement contains all expected elements."""
    json_data = copy.deepcopy(RENEWAL_STATEMENT)
    del json_data['createDateTime']
    del json_data['renewalRegistrationNumber']
    del json_data['payment']
    del json_data['courtOrderInformation']

    financing_statement = FinancingStatement.find_by_financing_id(200000004)
    assert financing_statement

    registration = Registration.create_from_json(json_data,
                                                 'RENEWAL',
                                                 financing_statement,
                                                 'TEST0005',
                                                 'PS12345')
#    print(registration.financing_id)
#    print(registration.json)
    registration.save()
    assert registration.financing_id == 200000004
    assert registration.id
    assert registration.registration_num
    assert registration.registration_type
    assert registration.registration_ts
    assert registration.account_id
    assert registration.client_reference_id

    result = registration.json
    assert result
    assert result['baseRegistrationNumber']
    assert result['renewalRegistrationNumber']
    assert result['createDateTime']
    assert result['registeringParty']


def test_save_renewal_rl(session):
    """Assert that creating a renewal statement on a RL financing statement contains all expected elements."""
    json_data = copy.deepcopy(RENEWAL_STATEMENT)
    del json_data['createDateTime']
    del json_data['renewalRegistrationNumber']
    del json_data['payment']
    del json_data['expiryDate']

    financing_statement = FinancingStatement.find_by_financing_id(200000001)
    assert financing_statement

    registration = Registration.create_from_json(json_data,
                                                 'RENEWAL',
                                                 financing_statement,
                                                 'TEST0002',
                                                 'PS12345')
#    print(registration.financing_id)
#    print(registration.json)
    registration.save()
    assert registration.financing_id == 200000001
    assert registration.id
    assert registration.registration_num
    assert registration.registration_type
    assert registration.registration_ts
    assert registration.account_id
    assert registration.client_reference_id

    result = registration.json
    assert result
    assert result['baseRegistrationNumber']
    assert result['renewalRegistrationNumber']
    assert result['createDateTime']
    assert result['registeringParty']
    assert result['courtOrderInformation']


def test_save_amendment(session):
    """Assert that creating an amendment statement on a non-RL financing statement contains all expected elements."""
    json_data = copy.deepcopy(AMENDMENT_STATEMENT)
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']
    json_data['changeType'] = 'CO'

    financing_statement = FinancingStatement.find_by_financing_id(200000000)
    assert financing_statement
    for party in financing_statement.parties:
        if party.registration_id != 200000000 and not party.registration_id_end:
            if party.party_type == 'DB' or party.party_type == 'DI':
                json_data['deleteDebtors'][0]['partyId'] = party.id
            elif party.party_type == 'SP':
                json_data['deleteSecuredParties'][0]['partyId'] = party.id

    for gc in financing_statement.general_collateral:
        if gc.registration_id != 200000000 and not gc.registration_id_end:
            json_data['deleteGeneralCollateral'][0]['collateralId'] = gc.id

    for vc in financing_statement.vehicle_collateral:
        if vc.registration_id != 200000000 and not vc.registration_id_end:
            json_data['deleteVehicleCollateral'][0]['vehicleId'] = vc.id

    registration = Registration.create_from_json(json_data,
                                                 'AMENDMENT',
                                                 financing_statement,
                                                 'TEST0001',
                                                 'PS12345')
#    print(registration.financing_id)
#    print(registration.json)
    registration.save()
    result = registration.json
    assert result
    assert result['baseRegistrationNumber']
    assert result['amendmentRegistrationNumber']
    assert result['createDateTime']
    assert result['registeringParty']
    assert result['courtOrderInformation']
    assert result['addDebtors']
    assert result['deleteDebtors']
    assert result['addSecuredParties']
    assert result['deleteSecuredParties']
    assert result['addGeneralCollateral']
    assert result['deleteGeneralCollateral']
    assert result['addVehicleCollateral']
    assert result['deleteVehicleCollateral']
    assert 'documentId' not in result


def test_save_amendment_from_draft(session):
    """Assert that creating an amendment statement from a draft on a non-RL financing statement.

    Verify it contains all expected elements.
    """
    json_data = copy.deepcopy(AMENDMENT_STATEMENT)
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['payment']

    financing_statement = FinancingStatement.find_by_financing_id(200000000)
    assert financing_statement
    for party in financing_statement.parties:
        if party.registration_id != 200000000 and not party.registration_id_end:
            if party.party_type == 'DB' or party.party_type == 'DI':
                json_data['deleteDebtors'][0]['partyId'] = party.id
            elif party.party_type == 'SP':
                json_data['deleteSecuredParties'][0]['partyId'] = party.id

    for gc in financing_statement.general_collateral:
        if gc.registration_id != 200000000 and not gc.registration_id_end:
            json_data['deleteGeneralCollateral'][0]['collateralId'] = gc.id

    for vc in financing_statement.vehicle_collateral:
        if vc.registration_id != 200000000 and not vc.registration_id_end:
            json_data['deleteVehicleCollateral'][0]['vehicleId'] = vc.id

    # Now create a draft amendment
    draft_json = copy.deepcopy(DRAFT_AMENDMENT_STATEMENT)
    draft = Draft.create_from_json(draft_json, 'PS12345')
    draft.save()
    assert draft.document_number
    json_data['documentId'] = draft.document_number
    registration = Registration.create_from_json(json_data,
                                                 'AMENDMENT',
                                                 financing_statement,
                                                 'TEST0001',
                                                 'PS12345')
    registration.save()
    assert registration.draft
    result = registration.json
    assert result
    # assert 'documentId' in result


def test_save_change(session):
    """Assert that creating a change statement contains all expected elements."""
    json_data = copy.deepcopy(CHANGE_STATEMENT)
    json_data['changeType'] = 'SU'
    del json_data['createDateTime']
    del json_data['changeRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']

    financing_statement = FinancingStatement.find_by_financing_id(200000000)
    assert financing_statement
    for party in financing_statement.parties:
        if party.registration_id != 200000000 and not party.registration_id_end:
            if party.party_type == 'DB' or party.party_type == 'DI':
                json_data['deleteDebtors'][0]['partyId'] = party.id
            elif party.party_type == 'SP':
                json_data['deleteSecuredParties'][0]['partyId'] = party.id

    for gc in financing_statement.general_collateral:
        if gc.registration_id != 200000000 and not gc.registration_id_end:
            json_data['deleteGeneralCollateral'][0]['collateralId'] = gc.id

    for vc in financing_statement.vehicle_collateral:
        if vc.registration_id != 200000000 and not vc.registration_id_end:
            json_data['deleteVehicleCollateral'][0]['vehicleId'] = vc.id

    registration = Registration.create_from_json(json_data,
                                                 'CHANGE',
                                                 financing_statement,
                                                 'TEST0001',
                                                 'PS12345')
#    print(registration.financing_id)
#    print(registration.json)
    registration.save()
    result = registration.json
    assert result
    assert result['baseRegistrationNumber']
    assert result['changeRegistrationNumber']
    assert result['createDateTime']
    assert result['registeringParty']
    assert result['addDebtors']
    assert result['deleteDebtors']
    assert result['addSecuredParties']
    assert result['deleteSecuredParties']
    assert result['addGeneralCollateral']
    assert result['deleteGeneralCollateral']
    assert result['addVehicleCollateral']
    assert result['deleteVehicleCollateral']
    assert 'documentId' not in result


def test_save_change_from_draft(session):
    """Assert that creating a change statement from a draft contains all expected elements."""
    json_data = copy.deepcopy(CHANGE_STATEMENT)
    json_data['changeType'] = 'SU'
    del json_data['createDateTime']
    del json_data['changeRegistrationNumber']
    del json_data['payment']

    financing_statement = FinancingStatement.find_by_financing_id(200000000)
    assert financing_statement
    for party in financing_statement.parties:
        if party.registration_id != 200000000 and not party.registration_id_end:
            if party.party_type == 'DB' or party.party_type == 'DI':
                json_data['deleteDebtors'][0]['partyId'] = party.id
            elif party.party_type == 'SP':
                json_data['deleteSecuredParties'][0]['partyId'] = party.id

    for gc in financing_statement.general_collateral:
        if gc.registration_id != 200000000 and not gc.registration_id_end:
            json_data['deleteGeneralCollateral'][0]['collateralId'] = gc.id

    for vc in financing_statement.vehicle_collateral:
        if vc.registration_id != 200000000 and not vc.registration_id_end:
            json_data['deleteVehicleCollateral'][0]['vehicleId'] = vc.id

    # Now create a draft change
    draft_json = copy.deepcopy(DRAFT_CHANGE_STATEMENT)
    draft = Draft.create_from_json(draft_json, 'PS12345')
    draft.save()
    assert draft.document_number
    json_data['documentId'] = draft.document_number

    registration = Registration.create_from_json(json_data,
                                                 'CHANGE',
                                                 financing_statement,
                                                 'TEST0001',
                                                 'PS12345')
    registration.save()
    assert registration.draft
    result = registration.json
    assert result
#    assert 'documentId' in result


@pytest.mark.parametrize('reg_type,life,life_infinite,expected_life', TEST_LIFE_EXPIRY_DATA)
def test_life_years(session, reg_type, life, life_infinite, expected_life):
    """Assert that creating a registration with different registration types sets life as expected."""
    json_data = copy.deepcopy(FINANCING_STATEMENT)
    json_data['type'] = reg_type
    if life is None:
        del json_data['lifeYears']
    else:
        json_data['lifeYears'] = life
    json_data['lifeInfinite'] = life_infinite
    registration = Registration.create_financing_from_json(json_data, 'PS12345', 'TESTID')
    assert registration.life == expected_life


@pytest.mark.parametrize('reg_num, reg_type, expiry_ts', TEST_EXPIRY_DATA)
def test_expiry(session, reg_num, reg_type, expiry_ts):
    """Assert that creating a registration with renewals return the expected expiry date."""
    registration = Registration.find_by_registration_number(reg_num, 'PS12345', True)
    json_data = registration.json if reg_type == 'RE' else registration.financing_statement.json
    assert 'expiryDate' in json_data
    print(json_data['expiryDate'] + ' ' + expiry_ts)
    assert json_data['expiryDate'] == expiry_ts
