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

from ppr_api.models import Registration, FinancingStatement, Draft
from ppr_api.exceptions import BusinessException

import copy
from registry_schemas.example_data.ppr import FINANCING_STATEMENT, DISCHARGE_STATEMENT
from registry_schemas.example_data.ppr import AMENDMENT_STATEMENT, RENEWAL_STATEMENT, CHANGE_STATEMENT
from registry_schemas.example_data.ppr import DRAFT_AMENDMENT_STATEMENT, DRAFT_CHANGE_STATEMENT

def test_find_by_id(session):
    """Assert that find registration by ID contains all expected elements."""
    registration = Registration.find_by_id(200000000)
    assert registration
    assert registration.registration_id == 200000000
    assert registration.registration_num == 'TEST0001'
    assert registration.registration_type_cd
    assert registration.registration_ts
    assert registration.account_id
    assert registration.client_reference_id

def test_find_by_id_AS(session):
    """Assert that find an amemdment registration by ID contains all expected elements."""
    registration = Registration.find_by_id(200000008)
    assert registration
    assert registration.registration_id == 200000008
    assert registration.registration_num
    assert registration.registration_type_cd == 'CO'
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

def test_find_by_id_CS_DT(session):
    """Assert that find an change registration DT by ID contains all expected elements."""
    registration = Registration.find_by_id(200000009)
    assert registration
    assert registration.registration_id == 200000009
    assert registration.registration_num
    assert registration.registration_type_cd == 'DT'
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

def test_find_by_id_CS_ST(session):
    """Assert that find an change registration ST by ID contains all expected elements."""
    registration = Registration.find_by_id(200000010)
    assert registration
    assert registration.registration_id == 200000010
    assert registration.registration_num
    assert registration.registration_type_cd == 'ST'
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

def test_find_by_id_CS_SU(session):
    """Assert that find an change registration SU by ID contains all expected elements."""
    registration = Registration.find_by_id(200000011)
    assert registration
    assert registration.registration_id == 200000011
    assert registration.registration_num
    assert registration.registration_type_cd == 'SU'
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

def test_find_by_registration_num_FS(session):
    """Assert that find a financing statement by registration number contains all expected elements."""
    registration = Registration.find_by_registration_number('TEST0001')
    assert registration
    assert registration.registration_id == 200000000
    assert registration.registration_num == 'TEST0001'
    assert registration.registration_type_cd
    assert registration.registration_ts
    assert registration.account_id
    assert registration.client_reference_id

def test_find_by_registration_num_DS(session):
    """Assert that find a discharge statement by registration number contains all expected elements."""
    registration = Registration.find_by_registration_number('TEST00D4')
    assert registration
    assert registration.registration_id == 200000004
    assert registration.registration_num == 'TEST00D4'
    assert registration.registration_type_cd == 'DC'
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


def test_find_by_id_invalid(session):
    """Assert that find registration by non-existent ID returns the expected result."""
    registration = Registration.find_by_id(100000234)
    assert not registration


def test_find_by_reg_num_invalid(session):
    """Assert that find registration by non-existent registration number returns the expected result."""
    registration = Registration.find_by_registration_number('100000234')
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
    print(str(registration.registration_id))
    print(registration.document_number)    
    print(registration.registration_num)    
#    print(registration.json)
    registration.save()
    assert registration.financing_id == 200000003
    assert registration.registration_id
    assert registration.registration_num
    assert registration.registration_type_cd
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
    assert registration.registration_id
    assert registration.registration_num
    assert registration.registration_type_cd
    assert registration.registration_ts
    assert registration.account_id
    assert registration.client_reference_id

    result = registration.json
    assert result
    assert result['baseRegistrationNumber']
    assert result['renewalRegistrationNumber']
    assert result['createDateTime']
    assert result['registeringParty']

def test_save_renewal_RL(session):
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
    assert registration.registration_id
    assert registration.registration_num
    assert registration.registration_type_cd
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
            if party.party_type_cd == 'DB' or party.party_type_cd == 'DI':
                json_data['deleteDebtors'][0]['partyId'] = party.party_id
            elif party.party_type_cd == 'SP':
                json_data['deleteSecuredParties'][0]['partyId'] = party.party_id

    for gc in financing_statement.general_collateral:
        if gc.registration_id != 200000000 and not gc.registration_id_end:
            json_data['deleteGeneralCollateral'][0]['collateralId'] = gc.collateral_id

    for vc in financing_statement.vehicle_collateral:
        if vc.registration_id != 200000000 and not vc.registration_id_end:
            json_data['deleteVehicleCollateral'][0]['vehicleId'] = vc.vehicle_id

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
    """Assert that creating an amendment statement from a draft on a non-RL financing 
       statement contains all expected elements."""
    json_data = copy.deepcopy(AMENDMENT_STATEMENT)
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['payment']

    financing_statement = FinancingStatement.find_by_financing_id(200000000)
    assert financing_statement
    for party in financing_statement.parties:
        if party.registration_id != 200000000 and not party.registration_id_end:
            if party.party_type_cd == 'DB' or party.party_type_cd == 'DI':
                json_data['deleteDebtors'][0]['partyId'] = party.party_id
            elif party.party_type_cd == 'SP':
                json_data['deleteSecuredParties'][0]['partyId'] = party.party_id

    for gc in financing_statement.general_collateral:
        if gc.registration_id != 200000000 and not gc.registration_id_end:
            json_data['deleteGeneralCollateral'][0]['collateralId'] = gc.collateral_id

    for vc in financing_statement.vehicle_collateral:
        if vc.registration_id != 200000000 and not vc.registration_id_end:
            json_data['deleteVehicleCollateral'][0]['vehicleId'] = vc.vehicle_id

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
 #   assert 'documentId' in result


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
            if party.party_type_cd == 'DB' or party.party_type_cd == 'DI':
                json_data['deleteDebtors'][0]['partyId'] = party.party_id
            elif party.party_type_cd == 'SP':
                json_data['deleteSecuredParties'][0]['partyId'] = party.party_id

    for gc in financing_statement.general_collateral:
        if gc.registration_id != 200000000 and not gc.registration_id_end:
            json_data['deleteGeneralCollateral'][0]['collateralId'] = gc.collateral_id

    for vc in financing_statement.vehicle_collateral:
        if vc.registration_id != 200000000 and not vc.registration_id_end:
            json_data['deleteVehicleCollateral'][0]['vehicleId'] = vc.vehicle_id

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
            if party.party_type_cd == 'DB' or party.party_type_cd == 'DI':
                json_data['deleteDebtors'][0]['partyId'] = party.party_id
            elif party.party_type_cd == 'SP':
                json_data['deleteSecuredParties'][0]['partyId'] = party.party_id

    for gc in financing_statement.general_collateral:
        if gc.registration_id != 200000000 and not gc.registration_id_end:
            json_data['deleteGeneralCollateral'][0]['collateralId'] = gc.collateral_id

    for vc in financing_statement.vehicle_collateral:
        if vc.registration_id != 200000000 and not vc.registration_id_end:
            json_data['deleteVehicleCollateral'][0]['vehicleId'] = vc.vehicle_id

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


def test_renewal_client_code_invalid(session):
    """Assert that the renewal statement json with an invalid RP client code validates correctly."""
    json_data = copy.deepcopy(RENEWAL_STATEMENT)
    del json_data['createDateTime']
    del json_data['renewalRegistrationNumber']
    del json_data['payment']
    del json_data['courtOrderInformation']
    del json_data['registeringParty']
    party = {
        'code': '900000000'
    }
    json_data['registeringParty'] = party

    financing_statement = FinancingStatement.find_by_financing_id(200000004)
    assert financing_statement
  
    with pytest.raises(BusinessException) as bad_request_err:
        Registration.create_from_json(json_data, 
                                      'RS', 
                                      financing_statement, 
                                      'TEST0001',
                                      'PS12345')

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    print(bad_request_err.value.error)


def test_amendment_party_id_invalid(session):
    """Assert that the amendment statement json with an invalid SP delete party ID validates correctly."""
    registration = Registration.find_by_id(200000008)
    assert registration

    json_data = registration.json
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['addGeneralCollateral']
    del json_data['addVehicleCollateral']
    del json_data['deleteGeneralCollateral']
    del json_data['deleteVehicleCollateral']
    del json_data['addDebtors']
    del json_data['addSecuredParties']
    json_data['deleteSecuredParties'][0]['partyId'] = 300000000
    json_data['deleteDebtors'][0]['partyId'] = 300000001

    financing_statement = FinancingStatement.find_by_financing_id(200000000)
    with pytest.raises(BusinessException) as bad_request_err:
        Registration.create_from_json(json_data, 
                                      'AMENDMENT', 
                                      financing_statement, 
                                      'TEST0005',
                                      'PS12345')

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    print(bad_request_err.value.error)



def test_amendment_vehicle_id_invalid(session):
    """Assert that the amendment statement json with an invalid delete vehicle collateral ID validates correctly."""
    registration = Registration.find_by_id(200000008)
    assert registration

    json_data = registration.json
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['addGeneralCollateral']
    del json_data['addVehicleCollateral']
    del json_data['deleteGeneralCollateral']
    del json_data['addDebtors']
    del json_data['addSecuredParties']
    del json_data['deleteDebtors']
    del json_data['deleteSecuredParties']
    json_data['deleteVehicleCollateral'][0]['vehicleId'] = 300000000

    financing_statement = FinancingStatement.find_by_financing_id(200000000)
    with pytest.raises(BusinessException) as bad_request_err:
        Registration.create_from_json(json_data, 
                                      'AMENDMENT', 
                                      financing_statement, 
                                      'TEST0001',
                                      'PS12345')

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    print(bad_request_err.value.error)



def test_amendment_collateral_id_invalid(session):
    """Assert that the amendment statement json with an invalid delete general collateral ID validates correctly."""
    registration = Registration.find_by_id(200000008)
    assert registration

    json_data = registration.json
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['addGeneralCollateral']
    del json_data['addVehicleCollateral']
    del json_data['deleteVehicleCollateral']
    del json_data['addDebtors']
    del json_data['addSecuredParties']
    del json_data['deleteDebtors']
    del json_data['deleteSecuredParties']
    json_data['deleteGeneralCollateral'][0]['collateralId'] = 300000000

    financing_statement = FinancingStatement.find_by_financing_id(200000000)
    with pytest.raises(BusinessException) as bad_request_err:
        Registration.create_from_json(json_data, 
                                      'AMENDMENT', 
                                      financing_statement, 
                                      'TEST0001',
                                      'PS12345')

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    print(bad_request_err.value.error)

