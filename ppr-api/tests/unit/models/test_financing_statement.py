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
import copy

import pytest
from registry_schemas.example_data.ppr import FINANCING_STATEMENT, DISCHARGE_STATEMENT, DRAFT_FINANCING_STATEMENT
from ppr_api.models import FinancingStatement, Draft

from ppr_api.exceptions import BusinessException


def test_save_sa(session):
    """Assert that a save valid SA financing statement works as expected."""
    json_data = copy.deepcopy(FINANCING_STATEMENT)
    json_data['type'] = 'SA'
    del json_data['createDateTime']
    del json_data['baseRegistrationNumber']
    del json_data['payment']
    del json_data['lifeInfinite']
    del json_data['lienAmount']
    del json_data['surrenderDate']
    del json_data['expiryDate']
    del json_data['documentId']

    statement = FinancingStatement.create_from_json(json_data, 'PS12345')
    statement.save()
    assert statement.financing_id

    result = statement.json
    assert result
    assert result['baseRegistrationNumber']
    assert result['registrationDescription']
    assert result['registrationAct']
    assert result['createDateTime']
    assert result['registeringParty']
    assert result['debtors'][0]
    assert result['securedParties'][0]
    assert result['vehicleCollateral'][0]
    assert result['generalCollateral'][0]
    assert 'documentId' not in result


def test_save_sa_from_draft(session):
    """Assert that a save valid SA financing statement from draft works as expected."""
    json_data = copy.deepcopy(FINANCING_STATEMENT)
    json_data['type'] = 'SA'
    del json_data['createDateTime']
    del json_data['baseRegistrationNumber']
    del json_data['payment']
    del json_data['lifeInfinite']
    del json_data['lienAmount']
    del json_data['surrenderDate']
    del json_data['expiryDate']

    # Now create draft
    draft_json = copy.deepcopy(DRAFT_FINANCING_STATEMENT)
    draft = Draft.create_from_json(draft_json, 'PS12345')
    draft.save()
    assert draft.document_number
    json_data['documentId'] = draft.document_number

    statement = FinancingStatement.create_from_json(json_data, 'PS12345')
    statement.save()
    assert statement.registration
    assert statement.registration[0].draft
    result = statement.json
    assert result
#    assert 'documentId' in result


def test_save_rl(session):
    """Assert that a save valid RL financing statement works as expected."""
    json_data = copy.deepcopy(FINANCING_STATEMENT)
    json_data['type'] = 'RL'
    del json_data['createDateTime']
    del json_data['baseRegistrationNumber']
    del json_data['payment']
    del json_data['lifeInfinite']
    del json_data['trustIndenture']
    del json_data['generalCollateral']
    del json_data['expiryDate']
    del json_data['documentId']

    statement = FinancingStatement.create_from_json(json_data, 'PS12345')
    statement.save()
    assert statement.financing_id

    result = statement.json
    assert result
    assert result['baseRegistrationNumber']
    assert result['createDateTime']
    assert result['registeringParty']
    assert result['debtors'][0]
    assert result['securedParties'][0]
    assert result['vehicleCollateral'][0]


def test_save_no_account(session):
    """Assert that a save valid financing statement with no account ID works as expected."""
    json_data = copy.deepcopy(FINANCING_STATEMENT)
    json_data['type'] = 'SA'
    del json_data['createDateTime']
    del json_data['baseRegistrationNumber']
    del json_data['payment']
    del json_data['lifeInfinite']
    del json_data['lienAmount']
    del json_data['surrenderDate']
    del json_data['expiryDate']
    del json_data['documentId']

    statement = FinancingStatement.create_from_json(json_data, 'PS12345')
    statement.save()
    assert statement.financing_id

    result = statement.json
    assert result
    assert result['baseRegistrationNumber']
    assert result['createDateTime']
    assert result['registeringParty']
    assert result['debtors'][0]
    assert result['securedParties'][0]
    assert result['vehicleCollateral'][0]
    assert result['generalCollateral'][0]


def test_find_all_by_account_id(session):
    """Assert that the financing statement summary list by account id first item contains all expected elements."""
    statement_list = FinancingStatement.find_all_by_account_id('PS12345', True)

    assert statement_list
    assert statement_list[0]['matchType']
    assert statement_list[0]['baseRegistrationNumber']
    assert statement_list[0]['registrationType']
    assert statement_list[0]['createDateTime']


def test_find_all_by_account_id_invalid(session):
    """Assert that the financing statement summary list by invalid account id works as expected."""
    with pytest.raises(BusinessException) as not_found_err:
        FinancingStatement.find_all_by_account_id('XX12345', True)

    # check
    assert not_found_err
    assert not_found_err.value.status_code == HTTPStatus.NOT_FOUND


def test_find_by_registration_number_valid(session):
    """Assert that a fetch individual financing statement on a valid registration number works as expected."""
    statement = FinancingStatement.find_by_registration_number('TEST0001', False)
    assert statement
    result = statement.json
    assert result['type'] == 'SA'
    assert result['baseRegistrationNumber'] == 'TEST0001'
    assert result['registeringParty']
    assert result['createDateTime']
    assert result['debtors'][0]
    assert result['securedParties'][0]
    assert result['generalCollateral'][0]
    assert result['vehicleCollateral'][0]
    assert result['expiryDate']
    assert result['lifeYears']
    assert result['trustIndenture']


def test_find_by_id(session):
    """Assert that find financing statement by ID contains all expected elements."""
    result = FinancingStatement.find_by_id(200000000)
    assert result
    assert result.registration_num
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
    assert result.registration_num
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
        assert json_data['expiryDate']
        assert json_data['lifeYears']
        assert json_data['trustIndenture']


def test_find_by_registration_number_invalid(session):
    """Assert that a fetch financing statement on a non-existent registration number works as expected."""
    with pytest.raises(BusinessException) as not_found_err:
        FinancingStatement.find_by_registration_number('X12345X', False)

    # check
    assert not_found_err
    assert not_found_err.value.status_code == HTTPStatus.NOT_FOUND


def test_find_by_registration_number_historical(session):
    """Assert that a fetch a discharged financing statement on a valid registration number works as expected."""
    with pytest.raises(BusinessException) as historical_err:
        FinancingStatement.find_by_registration_number('TEST0003', False)

    # check
    assert historical_err
    assert historical_err.value.status_code == HTTPStatus.BAD_REQUEST


def test_find_by_registration_number_historical_staff(session):
    """Assert that a fetch discharged financing statement on a registration number works as expected for staff."""
    result = FinancingStatement.find_by_registration_number('TEST0003', True)
    assert result


def test_validate_base_debtor(session):
    """Assert that base debtor check on an existing registration works as expected."""
    json_data = copy.deepcopy(DISCHARGE_STATEMENT)
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'

#    statement = FinancingStatement.find_by_financing_id(200000000)
    statement = FinancingStatement.find_by_registration_number('TEST0001', False)
    assert statement

    # valid business name
    valid = statement.validate_base_debtor(json_data['baseDebtor'], False)
    assert valid

    # invalid business name
    json_data['baseDebtor']['businessName'] = 'xxx debtor'
    valid = statement.validate_base_debtor(json_data['baseDebtor'], False)
    assert not valid

    # invalid individual name
    person = {
        'last': 'Debtor',
        'first': 'Test ind',
        'middle': '1'
    }
    del json_data['baseDebtor']['businessName']
    json_data['baseDebtor']['personName'] = person
    valid = statement.validate_base_debtor(json_data['baseDebtor'], False)
    assert not valid

    # invalid individual name
    json_data['baseDebtor']['personName']['first'] = 'John'
    valid = statement.validate_base_debtor(json_data['baseDebtor'], False)
    assert not valid


def test_financing_client_code_invalid(session):
    """Assert that the financing statement json with an invalid RP client code validates correctly."""
    json_data = copy.deepcopy(FINANCING_STATEMENT)
    del json_data['createDateTime']
    del json_data['baseRegistrationNumber']
    del json_data['payment']
    del json_data['lifeInfinite']
    del json_data['trustIndenture']
    del json_data['generalCollateral']
    del json_data['expiryDate']
    del json_data['registeringParty']
    del json_data['documentId']
    party = {
        'code': '900000000'
    }
    sp = {
        'code': '900000001'
    }
    json_data['registeringParty'] = party
    json_data['securedParties'].append(sp)
    with pytest.raises(BusinessException) as bad_request_err:
        FinancingStatement.create_from_json(json_data, 'PS12345')

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    print(bad_request_err.value.error)
