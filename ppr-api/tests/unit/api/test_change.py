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

"""Tests to verify the financing-statement changes endpoint.

Test-Suite to ensure that the /financing-statement/registrationNum/changes endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from registry_schemas.example_data.ppr import CHANGE_STATEMENT, FINANCING_STATEMENT

from ppr_api.services.authz import COLIN_ROLE, PPR_ROLE, STAFF_ROLE
from tests.unit.services.utils import create_header, create_header_account


# prep sample post change statement data
SAMPLE_JSON = copy.deepcopy(CHANGE_STATEMENT)
STATEMENT_VALID = {
  'baseRegistrationNumber': 'TEST0001',
  'baseDebtor': {
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
  'changeType': 'AC',
  'addVehicleCollateral': [
      {
          'type': 'MV',
          'serialNumber': 'KM8J3CA46JU724994',
          'year': 2018,
          'make': 'HYUNDAI',
          'model': 'TUCSON'
      }
  ],
  'payment': {
      'receipt': '/pay/api/v1/payment-requests/2199700/receipts',
      'invoiceId': '2199700'
  }
}
INVALID_REG_NUM = {
  'baseRegistrationNumber': 'TESTXXX1',
  'baseDebtor': {
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
  'changeType': 'AC',
  'addVehicleCollateral': [
      {
          'type': 'MV',
          'serialNumber': 'KM8J3CA46JU724994',
          'year': 2018,
          'make': 'HYUNDAI',
          'model': 'TUCSON'
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
  'changeType': 'AC',
  'addVehicleCollateral': [
      {
          'type': 'MV',
          'serialNumber': 'KM8J3CA46JU724994',
          'year': 2018,
          'make': 'HYUNDAI',
          'model': 'TUCSON'
      }
  ]
}
INVALID_BASE_DEBTOR = {
  'baseRegistrationNumber': 'TEST0001',
  'baseDebtor': {
      'businessName': 'TEST BUS 3 DEBTOR'
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
  'changeType': 'AC',
  'addVehicleCollateral': [
      {
          'type': 'MV',
          'serialNumber': 'KM8J3CA46JU724994',
          'year': 2018,
          'make': 'HYUNDAI',
          'model': 'TUCSON'
      }
  ]
}
INVALID_HISTORICAL = {
  'baseRegistrationNumber': 'TEST0003',
  'baseDebtor': {
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
  'changeType': 'AC',
  'addVehicleCollateral': [
      {
          'type': 'MV',
          'serialNumber': 'KM8J3CA46JU724994',
          'year': 2018,
          'make': 'HYUNDAI',
          'model': 'TUCSON'
      }
  ]
}
INVALID_CODE = {
  'baseRegistrationNumber': 'TEST0001',
  'baseDebtor': {
      'businessName': 'TEST BUS 2 DEBTOR'
  },
  'registeringParty': {
      'code': '300000000'
  },
  'changeType': 'AC',
  'addVehicleCollateral': [
      {
          'type': 'MV',
          'serialNumber': 'KM8J3CA46JU724994',
          'year': 2018,
          'make': 'HYUNDAI',
          'model': 'TUCSON'
      }
  ]
}
INVALID_ADDRESS = {
  'baseRegistrationNumber': 'TEST0001',
  'baseDebtor': {
      'businessName': 'TEST BUS 2 DEBTOR'
  },
  'registeringParty': {
      'businessName': 'ABC SEARCHING COMPANY',
      'address': {
          'street': '222 SUMMER STREET',
          'city': 'VICTORIA',
          'region': 'XX',
          'country': 'CA',
          'postalCode': 'V8W 2V8'
      },
      'emailAddress': 'bsmith@abc-search.com'
  },
  'changeType': 'AC',
  'addVehicleCollateral': [
      {
          'type': 'MV',
          'serialNumber': 'KM8J3CA46JU724994',
          'year': 2018,
          'make': 'HYUNDAI',
          'model': 'TUCSON'
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
    ('Missing account', [PPR_ROLE], HTTPStatus.BAD_REQUEST, False, 'TEST0010', 'TEST0001'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 'TEST0010', 'TEST0001'),
    ('Valid Request', [PPR_ROLE], HTTPStatus.OK, True, 'TEST0010', 'TEST0001'),
    ('Invalid Registration Number', [PPR_ROLE], HTTPStatus.NOT_FOUND, True, 'TESTXXXX', 'TEST0001'),
    ('Mismatch registrations non-staff', [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0010', 'TEST0002'),
    ('Mismatch registrations staff', [PPR_ROLE, STAFF_ROLE], HTTPStatus.OK, True, 'TEST0010', 'TEST0002'),
    ('Missing account staff', [PPR_ROLE, STAFF_ROLE], HTTPStatus.OK, False, 'TEST0010', 'TEST0001')
]


@pytest.mark.parametrize('desc,json_data,roles,status,has_account,reg_num', TEST_CREATE_DATA)
def test_create_change(session, client, jwt, desc, json_data, roles, status, has_account, reg_num):
    """Assert that a post change registration statement works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.post('/api/v1/financing-statements/' + reg_num + '/changes',
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    # print('Response data:')
    # print(response.json)
    assert response.status_code == status


@pytest.mark.parametrize('desc,roles,status,has_account,reg_num,base_reg_num', TEST_GET_STATEMENT)
def test_get_change(session, client, jwt, desc, roles, status, has_account, reg_num, base_reg_num):
    """Assert that a get change registration statement works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.get('/api/v1/financing-statements/' + base_reg_num + '/changes/' + reg_num,
                          headers=headers)

    # check
    assert response.status_code == status


def test_change_substitute_collateral_success(session, client, jwt):
    """Assert that a valid SU type change statement returns a 200 status."""
    # setup
    rv1 = create_financing_test(session, client, jwt)
    assert rv1.status_code == HTTPStatus.CREATED
    assert rv1.json['baseRegistrationNumber']
    base_reg_num = rv1.json['baseRegistrationNumber']

    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = base_reg_num
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
    json_data['changeType'] = 'SU'
    del json_data['createDateTime']
    del json_data['changeRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']
    del json_data['addSecuredParties']
    del json_data['deleteSecuredParties']
    del json_data['deleteDebtors']
    del json_data['addDebtors']
    del json_data['deleteGeneralCollateral']
    json_data['deleteGeneralCollateral'] = rv1.json['generalCollateral']
    del json_data['deleteVehicleCollateral']
    json_data['deleteVehicleCollateral'] = rv1.json['vehicleCollateral']

    # test
    rv = client.post('/api/v1/financing-statements/' + base_reg_num + '/changes',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.CREATED


def test_change_debtor_transfer_success(session, client, jwt):
    """Assert that a valid DT type change statement returns a 200 status."""
    # setup
    rv1 = create_financing_test(session, client, jwt)
    assert rv1.status_code == HTTPStatus.CREATED
    assert rv1.json['baseRegistrationNumber']
    base_reg_num = rv1.json['baseRegistrationNumber']

    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = base_reg_num
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
    json_data['changeType'] = 'DT'
    del json_data['createDateTime']
    del json_data['changeRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']
    del json_data['addSecuredParties']
    del json_data['deleteSecuredParties']
    del json_data['addVehicleCollateral']
    del json_data['deleteVehicleCollateral']
    del json_data['deleteGeneralCollateral']
    del json_data['addGeneralCollateral']
    del json_data['deleteDebtors']
    json_data['deleteDebtors'] = rv1.json['debtors']

    # test
    rv = client.post('/api/v1/financing-statements/' + base_reg_num + '/changes',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.CREATED


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
