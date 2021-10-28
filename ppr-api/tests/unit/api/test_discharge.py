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

"""Tests to verify the financing-statement discharges endpoint.

Test-Suite to ensure that the /financing-statement/registrationNum/discharges endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app
from registry_schemas.example_data.ppr import FINANCING_STATEMENT

from ppr_api.services.authz import COLIN_ROLE, PPR_ROLE, STAFF_ROLE
from tests.unit.services.utils import create_header, create_header_account


MOCK_URL_NO_KEY = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
# prep sample post discharge statement data
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
  'payment': {
      'receipt': '/pay/api/v1/payment-requests/2199700/receipts',
      'invoiceId': '2199700'
  }
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
  }
}
INVALID_BASE_DEBTOR = {
  'baseRegistrationNumber': 'TEST0001',
  'debtorName': {
      'businessName': 'TXST BUS 3 DEBTOR'
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
  }
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
  }
}
INVALID_CODE = {
  'baseRegistrationNumber': 'TEST0001',
  'debtorName': {
      'businessName': 'TEST BUS 2 DEBTOR'
  },
  'registeringParty': {
      'code': '300000000'
  }
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
      }
  }
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
    ('Missing account', [PPR_ROLE], HTTPStatus.BAD_REQUEST, False, 'TEST0D14', 'TEST0014'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 'TEST0D14', 'TEST0014'),
    ('Valid Request', [PPR_ROLE, STAFF_ROLE], HTTPStatus.OK, True, 'TEST0D14', 'TEST0014'),
    ('Valid Request other account', [PPR_ROLE], HTTPStatus.OK, True, 'TEST0021DC', 'TEST0021'),
    ('Unauthorized Request other account', [PPR_ROLE], HTTPStatus.UNAUTHORIZED, True, 'TEST0019DC', 'TEST0019'),
    ('Invalid Registration Number', [PPR_ROLE], HTTPStatus.NOT_FOUND, True, 'TESTXXXX', 'TEST0014'),
    ('Mismatch registrations non-staff', [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0D14', 'TEST0001'),
    ('Mismatch registrations staff', [PPR_ROLE, STAFF_ROLE], HTTPStatus.OK, True, 'TEST0D14', 'TEST0001'),
    ('Missing account staff', [PPR_ROLE, STAFF_ROLE], HTTPStatus.OK, False, 'TEST0D14', 'TEST0014')
]


@pytest.mark.parametrize('desc,json_data,roles,status,has_account,reg_num', TEST_CREATE_DATA)
def test_create_discharge(session, client, jwt, desc, json_data, roles, status, has_account, reg_num):
    """Assert that a post discharge registration statement works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.post('/api/v1/financing-statements/' + reg_num + '/discharges',
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    assert response.status_code == status


@pytest.mark.parametrize('desc,roles,status,has_account,reg_num,base_reg_num', TEST_GET_STATEMENT)
def test_get_discharge(session, client, jwt, desc, roles, status, has_account, reg_num, base_reg_num):
    """Assert that a get discharge registration statement works as expected."""
    current_app.config.update(AUTH_SVC_URL=MOCK_URL_NO_KEY)
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.get('/api/v1/financing-statements/' + base_reg_num + '/discharges/' + reg_num,
                          headers=headers)

    # check
    assert response.status_code == status
    # basic verification statement data check
    if status == HTTPStatus.OK:
        json_data = response.json
        assert json_data['dischargeRegistrationNumber'] == reg_num
        assert len(json_data['changes']) >= 1
        assert json_data['changes'][0]['dischargeRegistrationNumber'] == reg_num
        if desc != 'Mismatch registrations staff':
            assert json_data['baseRegistrationNumber'] == base_reg_num
            assert json_data['changes'][0]['baseRegistrationNumber'] == base_reg_num


def test_discharge_success(session, client, jwt):
    """Assert that a valid create statement returns a 200 status."""
    # setup - create a financing statement as the base registration, then a discharge
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['type'] = 'SA'
    statement['debtors'][0]['businessName'] = 'TEST BUS 2 DEBTOR'
    del statement['createDateTime']
    del statement['baseRegistrationNumber']
    del statement['payment']
    del statement['lifeInfinite']
    del statement['lienAmount']
    del statement['surrenderDate']
    del statement['documentId']

    rv1 = client.post('/api/v1/financing-statements',
                      json=statement,
                      headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                      content_type='application/json')
    assert rv1.status_code == HTTPStatus.CREATED
    assert rv1.json['baseRegistrationNumber']
    base_reg_num = rv1.json['baseRegistrationNumber']

    json_data = copy.deepcopy(STATEMENT_VALID)
    json_data['debtorName']['businessName'] = 'TEST BUS 2 DEBTOR'
    json_data['baseRegistrationNumber'] = base_reg_num
    del json_data['payment']

    # test
    rv = client.post('/api/v1/financing-statements/' + base_reg_num + '/discharges',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED
    # basic verification statement data check
    json_data = rv.json
    assert 'dischargeRegistrationNumber' in json_data
    assert len(json_data['changes']) >= 1
    assert 'dischargeRegistrationNumber' in json_data['changes'][0]
    assert json_data['baseRegistrationNumber'] == base_reg_num
    assert json_data['changes'][0]['baseRegistrationNumber'] == base_reg_num
