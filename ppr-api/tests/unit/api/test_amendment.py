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
from tests.unit.services.utils import create_header, create_header_account


# prep sample post amendment statement data
SAMPLE_JSON = copy.deepcopy(AMENDMENT_STATEMENT)
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
  'baseDebtor': {
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
  'baseDebtor': {
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
    ('Invalid historical', INVALID_HISTORICAL, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0003'),
    ('Invalid party code extra validation', INVALID_CODE, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0001'),
    ('Invalid party address extra validation', INVALID_ADDRESS, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0001'),
    ('Missing account', STATEMENT_VALID, [PPR_ROLE], HTTPStatus.BAD_REQUEST, False, 'TEST0001'),
    ('Invalid role', STATEMENT_VALID, [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 'TEST0001')
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


def test_amendment_court_order_success(session, client, jwt):
    """Assert that a valid CO type amendment statement returns a 200 status."""
    # setup
    rv1 = create_financing_test(session, client, jwt)
    assert rv1.status_code == HTTPStatus.CREATED
    assert rv1.json['baseRegistrationNumber']
    base_reg_num = rv1.json['baseRegistrationNumber']

    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = base_reg_num
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
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


def test_amendment_success(session, client, jwt):
    """Assert that a valid AM type amendment statement returns a 200 status."""
    # setup
    rv1 = create_financing_test(session, client, jwt)
    assert rv1.status_code == HTTPStatus.CREATED
    assert rv1.json['baseRegistrationNumber']
    base_reg_num = rv1.json['baseRegistrationNumber']

    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = base_reg_num
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
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
