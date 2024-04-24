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
from ppr_api.models import FinancingStatement, Draft, utils as model_utils

from ppr_api.exceptions import BusinessException


SECURITIES_ACT_NOTICES = [
    {
        'securitiesActNoticeType': 'LIEN',
        'effectiveDateTime': '2024-04-22T06:59:59+00:00',
        'description': 'DETAIL DESC',
        'securitiesActOrders': [
            {
                'courtOrder': True,
                'courtName': 'name',
                'courtRegistry': 'registry',
                'fileNumber': 'file',
                'orderDate': '2024-04-22T06:59:59+00:00',
                'effectOfOrder': 'effect'
            }
        ]        
    }
]
# testdata pattern is ({registration type}, {account ID}, {create draft})
TEST_REGISTRATION_DATA = [
    ('SA', 'PS12345', False),
    ('SA', 'PS12345', True),
    ('SE', 'PS00002', True),
    ('RL', 'PS12345', False),
    ('OT', 'PS12345', False),
    ('SA', None, False)
]
# testdata pattern is ({description}, {registration number}, {reg_type}, {account ID}, {http status}, {is staff},
#                      {is create})
TEST_REGISTRATION_NUMBER_DATA = [
    ('Valid', 'TEST0001', 'SA', 'PS12345', HTTPStatus.OK, False, True),
    ('Valid added from another account', 'TEST0019', 'SA', 'PS12345', HTTPStatus.OK, False, True),
    ('Invalid reg num', 'TESTXXXX', 'SA', 'PS12345', HTTPStatus.NOT_FOUND, False, True),
    ('Mismatch account id non-staff', 'TEST0001', 'SA', 'PS1234X', HTTPStatus.UNAUTHORIZED, False, True),
    ('Expired non-staff', 'TEST0013', 'SA', 'PS12345', HTTPStatus.BAD_REQUEST, False, True),
    ('Discharged non-staff', 'TEST0014', 'SA', 'PS12345', HTTPStatus.BAD_REQUEST, False, True),
    ('Mismatch staff', 'TEST0001', 'SA', 'PS1234X', HTTPStatus.OK, True, True),
    ('Expired staff not create', 'TEST0013', 'SA', 'PS12345', HTTPStatus.OK, True, False),
    ('Expired staff create', 'TEST0013', 'SA', 'PS12345', HTTPStatus.BAD_REQUEST, True, True),
    ('Discharged staff not create', 'TEST0014', 'SA', 'PS12345', HTTPStatus.OK, True, False),
    ('Discharged staff create', 'TEST0014', 'SA', 'PS12345', HTTPStatus.BAD_REQUEST, True, True),
    ('Valid SE', 'TEST0022', 'SE', 'PS00002', HTTPStatus.OK, False, True)
]
# testdata pattern is ({description}, {registration number}, {type}, {debtor name}, {is valid})
TEST_DEBTOR_NAME_DATA = [
    ('Valid Individual', 'TEST0001', 'DI', 'Debtor', True),
    ('Valid Business', 'TEST0002', 'DB', 'Test Bus', True),
    ('Invalid Business', 'TEST0002', 'DB', 'Text Bus', False),
]
# testdata pattern is ({registration number}, {results size})
TEST_DEBTOR_NAMES_DATA = [
    ('TEST0001', 4),
    ('TEST0002', 1),
    ('TESTXXXX', 0)
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
# testdata pattern is ({reg_num}, {reg_type}, {current_view}, {expiry_ts}, {life})
TEST_VERIFICATION_EXPIRY_DATA = [
    ('TEST0016', 'SA', False, '2026-09-04T06:59:59+00:00', 5),
    ('TEST0016', 'SA', True, '2041-09-04T06:59:59+00:00', 20),
    ('TEST0017', 'RL', False, '2022-02-27T07:59:59+00:00', 0),
    ('TEST0017', 'RL', True, '2023-02-23T07:59:59+00:00', 0)
]

# testdata pattern is ({reg_num}, {reg_type}, {expiry_ts}, {renewal2_ts}, {renewal1_ts})
TEST_HISTORY_EXPIRY_DATA = [
    ('TEST0016', 'SA', '2041-09-04T06:59:59+00:00', '2036-09-04T06:59:59+00:00', '2041-09-04T06:59:59+00:00')
#    ('TEST0017', 'RL', '2023-02-23T07:59:59+00:00', '2022-08-27T06:59:59+00:00', '2023-02-23T07:59:59+00:00')
]

@pytest.mark.parametrize('reg_type,account_id,create_draft', TEST_REGISTRATION_DATA)
def test_save(session, reg_type, account_id, create_draft):
    """Assert that saveing a valid financing statement works as expected."""
    json_data = copy.deepcopy(FINANCING_STATEMENT)
    json_data['type'] = reg_type
    del json_data['createDateTime']
    del json_data['baseRegistrationNumber']
    del json_data['payment']
    if reg_type == model_utils.REG_TYPE_SECURITIES_NOTICE:
        json_data['lifeInfinite'] = True
        del json_data['lifeYears']
        del json_data['vehicleCollateral']
        json_data['securitiesActNotices'] = copy.deepcopy(SECURITIES_ACT_NOTICES)
    else:
        del json_data['lifeInfinite']
    del json_data['expiryDate']
    del json_data['documentId']
    if reg_type != model_utils.REG_TYPE_REPAIRER_LIEN:
        del json_data['lienAmount']
        del json_data['surrenderDate']
    if reg_type != model_utils.REG_TYPE_SECURITY_AGREEMENT:
        del json_data['trustIndenture']
        if reg_type != model_utils.REG_TYPE_SECURITIES_NOTICE:
            del json_data['generalCollateral']
    if reg_type == model_utils.REG_TYPE_OTHER:
        json_data['otherTypeDescription'] = 'Other ACT'

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
    if reg_type != model_utils.REG_TYPE_SECURITIES_NOTICE:
        assert result['vehicleCollateral'][0]
    else:
        assert not result.get('vehicleCollateral')
        assert result.get('securitiesActNotices')
        for notice in result.get('securitiesActNotices'):
            assert notice.get('securitiesActOrders')
    if reg_type in (model_utils.REG_TYPE_SECURITY_AGREEMENT, model_utils.REG_TYPE_SECURITIES_NOTICE):
        assert result['generalCollateral'][0]
    assert 'documentId' not in result
    if reg_type == model_utils.REG_TYPE_OTHER:
        assert result['registrationDescription'] == 'CROWN CHARGE - OTHER - FILED PURSUANT TO OTHER ACT'
        assert result['otherTypeDescription'] == 'Other ACT'


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


@pytest.mark.parametrize('desc,reg_number,reg_type,account_id,status,staff,create', TEST_REGISTRATION_NUMBER_DATA)
def test_find_by_registration_number(session, desc, reg_number, reg_type, account_id, status, staff, create):
    """Assert that a fetch financing statement by registration number works as expected."""
    if status == HTTPStatus.OK:
        statement = FinancingStatement.find_by_registration_number(reg_number, account_id, staff, create)
        assert statement
        result = statement.json
        assert result['type'] == reg_type
        assert result['baseRegistrationNumber'] == reg_number
        assert result['registeringParty']
        assert result['createDateTime']
        assert result['debtors'][0]
        assert result['securedParties'][0]
        if reg_number == 'TEST0001':
            assert result['vehicleCollateral'][0]
        if reg_type != 'SE':
            assert result['expiryDate']
            assert result['lifeYears']
        if reg_number == 'TEST0001':
            assert result['generalCollateral'][0]
            assert result['trustIndenture']
        if statement.current_view_json and reg_number == 'TEST0001':
            assert result['courtOrderInformation']
        if reg_type == 'SE':
            assert result.get('lifeInfinite')
            assert result['generalCollateral'][0]
            assert result.get('securitiesActNotices')
            assert result['securitiesActNotices'][0].get('securitiesActOrders')
    else:
        with pytest.raises(BusinessException) as request_err:
            FinancingStatement.find_by_registration_number(reg_number, account_id, staff, create)

        # check
        assert request_err
        assert request_err.value.status_code == status


@pytest.mark.parametrize('desc,reg_number,type,debtor_name,valid', TEST_DEBTOR_NAME_DATA)
def test_validate_debtor_name(session, desc, reg_number, type, debtor_name, valid):
    """Assert that base debtor check on an existing registration works as expected."""
    json_data = copy.deepcopy(DISCHARGE_STATEMENT)
    if type == 'DB':
        json_data['debtorName']['businessName'] = debtor_name
    else:
        person = {
            'last': debtor_name,
            'first': 'Test ind',
            'middle': '1'
        }
        del json_data['debtorName']['businessName']
        json_data['debtorName']['personName'] = person

    statement = FinancingStatement.find_by_registration_number(reg_number, 'PS12345', False)
    assert statement

    # valid business name
    valid_debtor = statement.validate_debtor_name(json_data['debtorName'], False)
    if valid:
        assert valid_debtor
    else:
        assert not valid_debtor


@pytest.mark.parametrize('reg_num,results_size', TEST_DEBTOR_NAMES_DATA)
def test_find_debtor_names(session, reg_num, results_size):
    """Assert that finding debtor names by registration number works as expected."""
    names_json = FinancingStatement.find_debtor_names_by_registration_number(reg_num)
    if results_size == 0:
        assert not names_json or len(names_json) == 0
    else:
        assert names_json and len(names_json) == results_size
        if reg_num == 'TEST0001':
            assert names_json[0]['personName']['last'] == 'DEBTOR'
            assert names_json[1]['businessName'] == 'TEST BUS 2 DEBTOR'
            assert names_json[2]['businessName'] == 'TEST 7 AMEND DEBTOR'
            assert names_json[3]['businessName'] == 'TEST 8 TRANSFER DEBTOR'


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


def test_gc_legacy_json(session):
    """Assert that the financing statement JSON contains expected general collateral."""
    result = FinancingStatement.find_by_id(200000012)
    result.mark_update_json = False
    result.current_view_json = False
    json_data = result.json
    # print(json_data)
    assert len(json_data['generalCollateral']) == 3
    for collateral in json_data['generalCollateral']:
        assert 'collateralId' in collateral
        assert 'addedDateTime' in collateral
        assert 'description' in collateral
        assert 'descriptionAdd' not in collateral
        assert 'descriptionDelete' not in collateral


def test_gc_legacy_current_json(session):
    """Assert that the financing statement JSON contains expected general collateral."""
    result = FinancingStatement.find_by_id(200000012)
    result.mark_update_json = False
    result.current_view_json = True
    json_data = result.json
    # print(json_data)
    assert len(json_data['generalCollateral']) >= 4
    for collateral in json_data['generalCollateral']:
        assert 'collateralId' in collateral
        assert 'addedDateTime' in collateral
        # print(collateral)
        if collateral['collateralId'] in (200000004, 200000005, 200000006):
            assert collateral['description']
            assert 'descriptionAdd' not in collateral
            assert 'descriptionDelete' not in collateral
        if collateral['collateralId'] == 200000007:
            assert collateral['descriptionAdd']
            assert 'descriptionDelete' not in collateral
            assert 'description' not in collateral
        if collateral['collateralId'] == 200000008:
            assert collateral['descriptionDelete']
            assert 'descriptionAdd' not in collateral
            assert 'description' not in collateral
        if collateral['collateralId'] == 200000009:
            assert collateral['descriptionAdd']
            assert collateral['descriptionDelete']
            assert 'description' not in collateral


@pytest.mark.parametrize('reg_type,life,life_infinite,expected_life', TEST_LIFE_EXPIRY_DATA)
def test_life_expiry(session, reg_type, life, life_infinite, expected_life):
    """Assert that creating a financing statment with different registration types sets life and expiry as expected."""
    json_data = copy.deepcopy(FINANCING_STATEMENT)
    json_data['type'] = reg_type
    if life is None:
        del json_data['lifeYears']
    else:
        json_data['lifeYears'] = life
    json_data['lifeInfinite'] = life_infinite
    if reg_type == model_utils.REG_TYPE_OTHER:
        json_data['otherTypeDescription'] = 'TEST OTHER DESC'

    statement = FinancingStatement.create_from_json(json_data, 'PS12345', 'TESTID')

    assert statement.life == expected_life
    if statement.life != model_utils.LIFE_INFINITE:
        assert statement.expire_date
        if reg_type == model_utils.REG_TYPE_REPAIRER_LIEN:
            expire_date = model_utils.expiry_dt_repairer_lien()
            assert model_utils.format_ts(statement.expire_date) == model_utils.format_ts(expire_date)
        else:
            expire_date = model_utils.expiry_dt_from_years(statement.life)
            assert model_utils.format_ts(statement.expire_date) == model_utils.format_ts(expire_date)
    else:
        assert statement.expire_date is None
    if reg_type == model_utils.REG_TYPE_OTHER:
        assert statement.crown_charge_other == 'TEST OTHER DESC'


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
    # assert json_data['expiryDate'] == expiry_ts
    if life:
        assert 'lifeYears' in json_data
        assert json_data['lifeYears'] == life
