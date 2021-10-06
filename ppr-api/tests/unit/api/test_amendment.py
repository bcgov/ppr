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

"""Tests to verify the financing-statement amendments endpoint.

Test-Suite to ensure that the /financing-statement/registrationNum/amendments endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from registry_schemas.example_data.ppr import AMENDMENT_STATEMENT, FINANCING_STATEMENT

from ppr_api.services.authz import COLIN_ROLE, PPR_ROLE, STAFF_ROLE
from ppr_api.models import utils as model_utils
from tests.unit.services.utils import create_header, create_header_account


# prep sample post amendment statement data
SAMPLE_JSON = copy.deepcopy(AMENDMENT_STATEMENT)
STATEMENT_VALID = {
  'baseRegistrationNumber': 'TEST0001',
  'debtorName': {
      'businessName': 'TEST BUS 2 DEBTOR'
  },
  'registeringParty': {
      'businessName': 'ABC SEARCHING COMPANY',
      'address': {
          'street': '222 SUMMER STREET',
          'city': 'VICTORIA',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V8W 2V8'
      },
      'emailAddress': 'bsmith@abc-search.com'
  },
  'changeType': 'AM',
  'description': 'Test amendment.',
  'addSecuredParties': [
    {
      'businessName': 'BANK OF BRITISH COLUMBIA',
      'address': {
          'street': '3721 BEACON AVENUE',
          'city': 'SIDNEY',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V7R 1R7'
      }
    }
  ]
}
INVALID_REG_NUM = {
  'baseRegistrationNumber': 'TESTXXX1',
  'debtorName': {
      'businessName': 'TEST BUS 2 DEBTOR'
  },
  'registeringParty': {
      'businessName': 'ABC SEARCHING COMPANY',
      'address': {
          'street': '222 SUMMER STREET',
          'city': 'VICTORIA',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V8W 2V8'
      },
      'emailAddress': 'bsmith@abc-search.com'
  },
  'changeType': 'AM',
  'description': 'Test amendment.',
  'addSecuredParties': [
    {
      'businessName': 'BANK OF BRITISH COLUMBIA',
      'address': {
          'street': '3721 BEACON AVENUE',
          'city': 'SIDNEY',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V7R 1R7'
      }
    }
  ]
}
MISSING_BASE_DEBTOR = {
  'baseRegistrationNumber': 'TEST0001',
  'registeringParty': {
      'businessName': 'ABC SEARCHING COMPANY',
      'address': {
          'street': '222 SUMMER STREET',
          'city': 'VICTORIA',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V8W 2V8'
      },
      'emailAddress': 'bsmith@abc-search.com'
  },
  'changeType': 'AM',
  'description': 'Test amendment.',
  'addSecuredParties': [
    {
      'businessName': 'BANK OF BRITISH COLUMBIA',
      'address': {
          'street': '3721 BEACON AVENUE',
          'city': 'SIDNEY',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V7R 1R7'
      }
    }
  ]
}
INVALID_BASE_DEBTOR = {
  'baseRegistrationNumber': 'TEST0001',
  'debtorName': {
      'businessName': 'XXXX BUS 3 DEBTOR'
  },
  'registeringParty': {
      'businessName': 'ABC SEARCHING COMPANY',
      'address': {
          'street': '222 SUMMER STREET',
          'city': 'VICTORIA',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V8W 2V8'
      },
      'emailAddress': 'bsmith@abc-search.com'
  },
  'changeType': 'AM',
  'description': 'Test amendment.',
  'addSecuredParties': [
    {
      'businessName': 'BANK OF BRITISH COLUMBIA',
      'address': {
          'street': '3721 BEACON AVENUE',
          'city': 'SIDNEY',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V7R 1R7'
      }
    }
  ]
}
INVALID_HISTORICAL = {
  'baseRegistrationNumber': 'TEST0003',
  'debtorName': {
      'businessName': 'TEST BUS 2 DEBTOR'
  },
  'registeringParty': {
      'businessName': 'ABC SEARCHING COMPANY',
      'address': {
          'street': '222 SUMMER STREET',
          'city': 'VICTORIA',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V8W 2V8'
      },
      'emailAddress': 'bsmith@abc-search.com'
  },
  'changeType': 'AM',
  'description': 'Test amendment.',
  'addSecuredParties': [
    {
      'businessName': 'BANK OF BRITISH COLUMBIA',
      'address': {
          'street': '3721 BEACON AVENUE',
          'city': 'SIDNEY',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V7R 1R7'
      }
    }
  ]
}
INVALID_CODE = {
  'baseRegistrationNumber': 'TEST0001',
  'debtorName': {
      'businessName': 'TEST BUS 2 DEBTOR'
  },
  'registeringParty': {
      'code': '300000000'
  },
  'changeType': 'AM',
  'description': 'Test amendment.',
  'addSecuredParties': [
    {
      'businessName': 'BANK OF BRITISH COLUMBIA',
      'address': {
          'street': '3721 BEACON AVENUE',
          'city': 'SIDNEY',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V7R 1R7'
      }
    }
  ]
}
INVALID_ADDRESS = {
  'baseRegistrationNumber': 'TEST0001',
  'debtorName': {
      'businessName': 'TEST BUS 2 DEBTOR'
  },
  'registeringParty': {
      'businessName': 'ABC SEARCHING COMPANY',
      'address': {
          'street': '222 SUMMER STREET',
          'city': 'VICTORIA',
          'region': 'BC',
          'country': 'XX',
          'postalCode': 'V8W 2V8'
      },
      'emailAddress': 'bsmith@abc-search.com'
  },
  'changeType': 'AM',
  'description': 'Test amendment.',
  'addSecuredParties': [
    {
      'businessName': 'BANK OF BRITISH COLUMBIA',
      'address': {
          'street': '3721 BEACON AVENUE',
          'city': 'SIDNEY',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V7R 1R7'
      }
    }
  ]
}


# testdata pattern is ({description}, {test data}, {roles}, {status}, {has_account}, {reg_num})
TEST_CREATE_DATA = [
    ('Invalid registration number', INVALID_REG_NUM, [PPR_ROLE], HTTPStatus.NOT_FOUND, True, 'TESTXXX1'),
    ('Invalid missing base debtor', MISSING_BASE_DEBTOR, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0001'),
    ('Invalid base debtor', INVALID_BASE_DEBTOR, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0001'),
    ('Invalid historical', INVALID_HISTORICAL, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0013'),
    ('Invalid party code extra validation', INVALID_CODE, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0001'),
    ('Invalid party address extra validation', INVALID_ADDRESS, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0001'),
    ('Missing account', STATEMENT_VALID, [PPR_ROLE], HTTPStatus.BAD_REQUEST, False, 'TEST0001'),
    ('Invalid role', STATEMENT_VALID, [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 'TEST0001')
]

# testdata pattern is ({description}, {roles}, {status}, {has_account}, {reg_num}, {base_reg_num})
TEST_GET_STATEMENT = [
    ('Missing account', [PPR_ROLE], HTTPStatus.BAD_REQUEST, False, 'TEST0007', 'TEST0001'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 'TEST0007', 'TEST0001'),
    ('Valid Request', [PPR_ROLE], HTTPStatus.OK, True, 'TEST0007', 'TEST0001'),
    ('Invalid Registration Number', [PPR_ROLE], HTTPStatus.NOT_FOUND, True, 'TESTXXXX', 'TEST0001'),
    ('Mismatch registrations non-staff', [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0007', 'TEST0002'),
    ('Mismatch registrations staff', [PPR_ROLE, STAFF_ROLE], HTTPStatus.OK, True, 'TEST0007', 'TEST0002'),
    ('Missing account staff', [PPR_ROLE, STAFF_ROLE], HTTPStatus.OK, False, 'TEST0007', 'TEST0001')
]
TEST_DATA_AMENDMENT_CHANGE_TYPE = [
    (model_utils.REG_TYPE_AMEND_SUBSTITUTION_COLLATERAL, False),
    (model_utils.REG_TYPE_AMEND_ADDITION_COLLATERAL, False),
    (model_utils.REG_TYPE_AMEND_DEBTOR_RELEASE, False),
    (model_utils.REG_TYPE_AMEND_DEBTOR_TRANSFER, False),
    (model_utils.REG_TYPE_AMEND_PARIAL_DISCHARGE, False),
    (model_utils.REG_TYPE_AMEND_SP_TRANSFER, False)
]


@pytest.mark.parametrize('desc,json_data,roles,status,has_account,reg_num', TEST_CREATE_DATA)
def test_create_amendment(session, client, jwt, desc, json_data, roles, status, has_account, reg_num):
    """Assert that a post amendment registration statement works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.post('/api/v1/financing-statements/' + reg_num + '/amendments',
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    # print('Response data:')
    # print(response.json)
    assert response.status_code == status


@pytest.mark.parametrize('desc,roles,status,has_account,reg_num,base_reg_num', TEST_GET_STATEMENT)
def test_get_amendment(session, client, jwt, desc, roles, status, has_account, reg_num, base_reg_num):
    """Assert that a get amendment registration statement works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.get('/api/v1/financing-statements/' + base_reg_num + '/amendments/' + reg_num,
                          headers=headers)

    # check
    assert response.status_code == status
    # basic verification statement data check
    if status == HTTPStatus.OK:
        json_data = response.json
        assert json_data['amendmentRegistrationNumber'] == reg_num
        assert len(json_data['changes']) >= 1
        assert json_data['changes'][0]['amendmentRegistrationNumber'] == reg_num
        if desc != 'Mismatch registrations staff':
            assert json_data['baseRegistrationNumber'] == base_reg_num
            assert json_data['changes'][0]['baseRegistrationNumber'] == base_reg_num


def test_amendment_court_order_success(session, client, jwt):
    """Assert that a valid CO type amendment statement returns a 200 status."""
    # setup
    rv1 = create_financing_test(session, client, jwt)
    assert rv1.status_code == HTTPStatus.CREATED
    assert rv1.json['baseRegistrationNumber']
    base_reg_num = rv1.json['baseRegistrationNumber']

    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = base_reg_num
    json_data['debtorName']['businessName'] = 'TEST BUS 2 DEBTOR'
    json_data['changeType'] = 'CO'
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['payment']
    del json_data['removeTrustIndenture']
    del json_data['addTrustIndenture']
    del json_data['deleteDebtors']
    del json_data['documentId']
    json_data['deleteDebtors'] = rv1.json['debtors']
    del json_data['deleteSecuredParties']
    json_data['deleteSecuredParties'] = rv1.json['securedParties']
    del json_data['deleteGeneralCollateral']
    json_data['deleteGeneralCollateral'] = rv1.json['generalCollateral']
    del json_data['deleteVehicleCollateral']
    json_data['deleteVehicleCollateral'] = rv1.json['vehicleCollateral']
#    print(json_data)

    # test
    rv = client.post('/api/v1/financing-statements/' + base_reg_num + '/amendments',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')

    # check
#    print(rv.json)
    assert rv.status_code == HTTPStatus.CREATED
    json_data = rv.json
    assert 'amendmentRegistrationNumber' in json_data
    assert len(json_data['changes']) >= 1
    assert 'amendmentRegistrationNumber' in json_data['changes'][0]
    assert json_data['baseRegistrationNumber'] == base_reg_num
    assert json_data['changes'][0]['baseRegistrationNumber'] == base_reg_num


def test_amendment_success(session, client, jwt):
    """Assert that a valid AM type amendment statement returns a 200 status."""
    # setup
    rv1 = create_financing_test(session, client, jwt)
    assert rv1.status_code == HTTPStatus.CREATED
    assert rv1.json['baseRegistrationNumber']
    base_reg_num = rv1.json['baseRegistrationNumber']

    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = base_reg_num
    json_data['debtorName']['businessName'] = 'TEST BUS 2 DEBTOR'
    json_data['changeType'] = 'AM'
    del json_data['courtOrderInformation']
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['payment']
    del json_data['removeTrustIndenture']
    del json_data['addTrustIndenture']
    del json_data['addSecuredParties']
    del json_data['deleteSecuredParties']
    del json_data['addDebtors']
    del json_data['deleteDebtors']
    del json_data['deleteGeneralCollateral']
    del json_data['addGeneralCollateral']
    del json_data['deleteVehicleCollateral']
    del json_data['documentId']
    json_data['deleteVehicleCollateral'] = rv1.json['vehicleCollateral']

    # test
    rv = client.post('/api/v1/financing-statements/' + base_reg_num + '/amendments',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.CREATED
    json_data = rv.json
    assert 'amendmentRegistrationNumber' in json_data
    assert len(json_data['changes']) >= 1
    assert 'amendmentRegistrationNumber' in json_data['changes'][0]
    assert json_data['baseRegistrationNumber'] == base_reg_num
    assert json_data['changes'][0]['baseRegistrationNumber'] == base_reg_num


@pytest.mark.parametrize('change_type, is_general_collateral', TEST_DATA_AMENDMENT_CHANGE_TYPE)
def test_change_types(session, client, jwt, change_type, is_general_collateral):
    """Assert that setting the amendment change type from the amendment data works as expected."""
    json_data = copy.deepcopy(AMENDMENT_STATEMENT)
    json_data['changeType'] = change_type
    json_data['debtorName']['businessName'] = 'TEST BUS 2 DEBTOR'
    del json_data['createDateTime']
    del json_data['payment']
    del json_data['documentId']
    del json_data['amendmentRegistrationNumber']
    del json_data['courtOrderInformation']
    del json_data['addTrustIndenture']
    del json_data['removeTrustIndenture']

    if change_type in (model_utils.REG_TYPE_AMEND_ADDITION_COLLATERAL,
                       model_utils.REG_TYPE_AMEND_SUBSTITUTION_COLLATERAL,
                       model_utils.REG_TYPE_AMEND_PARIAL_DISCHARGE):
        del json_data['addSecuredParties']
        del json_data['deleteSecuredParties']
        del json_data['addDebtors']
        del json_data['deleteDebtors']
    if change_type == model_utils.REG_TYPE_AMEND_PARIAL_DISCHARGE:
        del json_data['addVehicleCollateral']
        del json_data['addGeneralCollateral']
        del json_data['deleteGeneralCollateral']
    elif change_type == model_utils.REG_TYPE_AMEND_ADDITION_COLLATERAL:
        del json_data['deleteVehicleCollateral']
        del json_data['deleteGeneralCollateral']
        if is_general_collateral:
            del json_data['addVehicleCollateral']
        else:
            del json_data['addGeneralCollateral']
    elif change_type == model_utils.REG_TYPE_AMEND_SUBSTITUTION_COLLATERAL:
        if is_general_collateral:
            del json_data['addVehicleCollateral']
            del json_data['deleteVehicleCollateral']
        else:
            del json_data['addGeneralCollateral']
            del json_data['deleteGeneralCollateral']
    if change_type in (model_utils.REG_TYPE_AMEND_DEBTOR_RELEASE,
                       model_utils.REG_TYPE_AMEND_DEBTOR_TRANSFER,
                       model_utils.REG_TYPE_AMEND_SP_TRANSFER):
        del json_data['addVehicleCollateral']
        del json_data['deleteVehicleCollateral']
        del json_data['addGeneralCollateral']
        del json_data['deleteGeneralCollateral']
    if change_type == model_utils.REG_TYPE_AMEND_DEBTOR_RELEASE:
        del json_data['addSecuredParties']
        del json_data['deleteSecuredParties']
        del json_data['addDebtors']
    elif change_type == model_utils.REG_TYPE_AMEND_DEBTOR_TRANSFER:
        del json_data['addSecuredParties']
        del json_data['deleteSecuredParties']
    elif change_type == model_utils.REG_TYPE_AMEND_SP_TRANSFER:
        del json_data['addDebtors']
        del json_data['deleteDebtors']

    base_reg_num = 'TEST0001'

    json_data['baseRegistrationNumber'] = base_reg_num
    # Set well known ids for deletes
    if 'deleteDebtors' in json_data:
        json_data['deleteDebtors'][0]['partyId'] = 200000024
    if 'deleteSecuredParties' in json_data:
        json_data['deleteSecuredParties'][0]['partyId'] = 200000026
    if 'deleteGeneralCollateral' in json_data:
        json_data['deleteGeneralCollateral'][0]['collateraId'] = 200000000
    if 'deleteVehicleCollateral' in json_data:
        json_data['deleteVehicleCollateral'][0]['vehicleId'] = 200000008

    rv = client.post('/api/v1/financing-statements/' + base_reg_num + '/amendments',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')
    # check
    # print(rv.json)
    assert rv.status_code == HTTPStatus.CREATED
    assert 'amendmentRegistrationNumber' in rv.json


def create_financing_test(session, client, jwt):
    """Create a financing statement for testing."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['debtors'][0]['businessName'] = 'TEST BUS 2 DEBTOR'
    statement['type'] = 'SA'
    del statement['createDateTime']
    del statement['baseRegistrationNumber']
    del statement['payment']
    del statement['documentId']
    del statement['lifeInfinite']
    del statement['lienAmount']
    del statement['surrenderDate']

    return client.post('/api/v1/financing-statements',
                       json=statement,
                       headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                       content_type='application/json')
