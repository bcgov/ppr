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
from registry_schemas.example_data.ppr import CHANGE_STATEMENT

from ppr_api.services.authz import COLIN_ROLE, PPR_ROLE, STAFF_ROLE, SBC_OFFICE, BCOL_HELP
from tests.unit.services.utils import create_header, create_header_account, create_header_account_report


MOCK_PAY_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/pay/api/v1/'
# prep sample post change statement data
SAMPLE_JSON = copy.deepcopy(CHANGE_STATEMENT)
STATEMENT_VALID = {
  'baseRegistrationNumber': 'TEST0001',
  'debtorName': {
      'businessName': 'TEST BUS 2 DEBTOR'
  },
  'authorizationReceived': True,
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
  'debtorName': {
      'businessName': 'TEST BUS 2 DEBTOR'
  },
  'authorizationReceived': True,
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
  'authorizationReceived': True,
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
  'debtorName': {
      'businessName': 'TEXT BUS 3 DEBTOR'
  },
  'authorizationReceived': True,
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
  'debtorName': {
      'businessName': 'TEST BUS 2 DEBTOR'
  },
  'authorizationReceived': True,
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
  'debtorName': {
      'businessName': 'TEST BUS 2 DEBTOR'
  },
  'authorizationReceived': True,
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
  'debtorName': {
      'businessName': 'TEST BUS 2 DEBTOR'
  },
  'authorizationReceived': True,
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

# testdata pattern is ({description}, {roles}, {status}, {has_account}, {reg_num}, {base_reg_num})
TEST_GET_STATEMENT = [
    ('Missing account', [PPR_ROLE], HTTPStatus.BAD_REQUEST, False, 'TEST0009', 'TEST0001'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 'TEST0009', 'TEST0001'),
    ('Valid Request', [PPR_ROLE], HTTPStatus.OK, True, 'TEST0009', 'TEST0001'),
    ('Invalid Registration Number', [PPR_ROLE], HTTPStatus.NOT_FOUND, True, 'TESTXXXX', 'TEST0001'),
    ('Mismatch registrations non-staff', [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0009', 'TEST0002'),
    ('Mismatch registrations staff', [PPR_ROLE, STAFF_ROLE], HTTPStatus.OK, True, 'TEST0009', 'TEST0002'),
    ('Missing account staff', [PPR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, 'TEST0009', 'TEST0001')
]


@pytest.mark.parametrize('desc,roles,status,has_account,reg_num,base_reg_num', TEST_GET_STATEMENT)
def test_get_change(session, client, jwt, desc, roles, status, has_account, reg_num, base_reg_num):
    """Assert that a get change registration statement works as expected."""
    headers = None
    # setup
    if status == HTTPStatus.UNAUTHORIZED and desc.startswith('Report'):
        headers = create_header_account_report(jwt, roles)
    elif has_account and BCOL_HELP in roles:
        headers = create_header_account(jwt, roles, 'test-user', BCOL_HELP)
    elif has_account and STAFF_ROLE in roles:
        headers = create_header_account(jwt, roles, 'test-user', STAFF_ROLE)
    elif has_account and SBC_OFFICE in roles:
        headers = create_header_account(jwt, roles, 'test-user', SBC_OFFICE)
    elif has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.get('/api/v1/financing-statements/' + base_reg_num + '/changes/' + reg_num,
                          headers=headers)

    # check
    assert response.status_code == status
    # basic verification statement data check
    if status == HTTPStatus.OK:
        json_data = response.json
        assert json_data['changeRegistrationNumber'] == reg_num
        assert len(json_data['changes']) >= 1
        assert json_data['changes'][0]['changeRegistrationNumber'] == reg_num
        if desc != 'Mismatch registrations staff':
            assert json_data['baseRegistrationNumber'] == base_reg_num
            assert json_data['changes'][0]['baseRegistrationNumber'] == base_reg_num
