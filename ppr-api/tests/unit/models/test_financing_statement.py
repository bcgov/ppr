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


# testdata pattern is ({registration type}, {account ID}, {create draft})
TEST_REGISTRATION_DATA = [
    ('SA', 'PS12345', False),
    ('SA', 'PS12345', True),
    ('RL', 'PS12345', False),
    ('SA', None, False)
]
# testdata pattern is ({description}, {registration number}, {account ID}, {http status}, {is staff})
TEST_REGISTRATION_NUMBER_DATA = [
    ('Valid', 'TEST0001', 'PS12345', HTTPStatus.OK, False),
    ('Invalid reg num', 'TESTXXXX', 'PS12345', HTTPStatus.NOT_FOUND, False),
    ('Mismatch account id non-staff', 'TEST0001', 'PS1234X', HTTPStatus.BAD_REQUEST, False),
    ('Expired non-staff', 'TEST0013', 'PS12345', HTTPStatus.BAD_REQUEST, False),
    ('Discharged non-staff', 'TEST0014', 'PS12345', HTTPStatus.BAD_REQUEST, False),
    ('Mismatch staff', 'TEST0001', 'PS1234X', HTTPStatus.OK, True),
    ('Expired staff', 'TEST0013', 'PS12345', HTTPStatus.OK, True),
    ('Discharged staff', 'TEST0014', 'PS12345', HTTPStatus.OK, True)
]


@pytest.mark.parametrize('reg_type,account_id,create_draft', TEST_REGISTRATION_DATA)
def test_save(session, reg_type, account_id, create_draft):
    """Assert that saveing a valid financing statement works as expected."""
    json_data = copy.deepcopy(FINANCING_STATEMENT)
    json_data['type'] = reg_type
    del json_data['createDateTime']
    del json_data['baseRegistrationNumber']
    del json_data['payment']
    del json_data['lifeInfinite']
    del json_data['expiryDate']
    del json_data['documentId']
    if reg_type != 'RL':
        del json_data['lienAmount']
        del json_data['surrenderDate']
    if reg_type != 'SA':
        del json_data['trustIndenture']
        del json_data['generalCollateral']

    if create_draft:
        draft_json = copy.deepcopy(DRAFT_FINANCING_STATEMENT)
        draft = Draft.create_from_json(draft_json, account_id)
        draft.save()
        assert draft.document_number
        json_data['documentId'] = draft.document_number

    statement = FinancingStatement.create_from_json(json_data, account_id, 'UNIT_TEST')
    statement.save()
    assert statement.id
    assert statement.registration[0].account_id == account_id
    assert statement.registration[0].user_id == 'UNIT_TEST'
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
    if reg_type == 'SA':
        assert result['generalCollateral'][0]
    assert 'documentId' not in result


def test_find_all_by_account_id(session):
    """Assert that the financing statement summary list by account id first item contains all expected elements."""
    statement_list = FinancingStatement.find_all_by_account_id('PS12345')

    assert statement_list
    assert statement_list[0]['registrationNumber']
    assert statement_list[0]['registrationType']
    assert statement_list[0]['registrationClass']
    assert statement_list[0]['registrationDescription']
    assert statement_list[0]['statusType']
    assert statement_list[0]['createDateTime']
    assert statement_list[0]['lastUpdateDateTime']
    assert statement_list[0]['expireDays']
    assert statement_list[0]['registeringParty']
    assert statement_list[0]['securedParties']
    # assert statement_list[0]['clientReferenceId']
    assert statement_list[0]['path']


def test_find_all_by_account_id_no_result(session):
    """Assert that the financing statement summary list by invalid account id works as expected."""
    statement_list = FinancingStatement.find_all_by_account_id('XXXXX45')

    assert len(statement_list) == 0


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


@pytest.mark.parametrize('desc,reg_number,account_id,status,staff', TEST_REGISTRATION_NUMBER_DATA)
def test_find_by_registration_number(session, desc, reg_number, account_id, status, staff):
    """Assert that a fetch financing statement by registration number works as expected."""
    if status == HTTPStatus.OK:
        statement = FinancingStatement.find_by_registration_number(reg_number, account_id, staff)
        assert statement
        result = statement.json
        assert result['type'] == 'SA'
        assert result['baseRegistrationNumber'] == reg_number
        assert result['registeringParty']
        assert result['createDateTime']
        assert result['debtors'][0]
        assert result['securedParties'][0]
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
            FinancingStatement.find_by_registration_number(reg_number, account_id, staff)

        # check
        assert request_err
        assert request_err.value.status_code == status


def test_validate_base_debtor(session):
    """Assert that base debtor check on an existing registration works as expected."""
    json_data = copy.deepcopy(DISCHARGE_STATEMENT)
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'

#    statement = FinancingStatement.find_by_financing_id(200000000)
    statement = FinancingStatement.find_by_registration_number('TEST0001', 'PS12345', False)
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
    assert 'added' in json_data['generalCollateral'][1]
    assert 'added' in json_data['vehicleCollateral'][1]
    assert json_data['debtors'][1]['added']
    assert json_data['securedParties'][1]['added']
    assert json_data['generalCollateral'][1]['added']
    assert json_data['vehicleCollateral'][1]['added']
