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

"""Tests to verify the endpoints for maintaining MH transport permits.

Test-Suite to ensure that the /permits endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app

from mhr_api.models import MhrRegistration
from mhr_api.services.authz import MHR_ROLE, STAFF_ROLE, COLIN_ROLE, REQUEST_TRANSPORT_PERMIT, \
                                   TRANSFER_SALE_BENEFICIARY
from tests.unit.services.utils import create_header, create_header_account


PERMIT = {
  'documentId': '80035947',
  'clientReferenceId': 'EX-TP001234',
  'submittingParty': {
    'businessName': 'SUBMITTING',
    'address': {
      'street': '1234 TEST-0001',
      'city': 'CITY',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V8R 3A5'
    },
    'phoneNumber': '2505058308'
  },
  'owner': {
    'individualName': {
       'first': 'BOB',
       'middle': 'ARTHUR', 
       'last': 'MCKAY'
     },
    'address': {
      'street': '1234 TEST-0001',
      'city': 'CITY',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V8R 3A5'
    },
    'phoneNumber': '2507701067'
  },
  'existingLocation': {
    'locationType': 'MH_PARK',
    'address': {
      'street': '1234 TEST-0001',
      'city': 'CITY',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V8R 3A5'
    },
    'leaveProvince': False,
    'parkName': 'park name',
    'pad': 'pad'
  },
  'newLocation': {
    'locationType': 'MH_PARK',
    'address': {
      'street': '1117 GLENDALE AVENUE',
      'city': 'SALMO',
      'region': 'BC',
      'country': 'CA',
      'postalCode': ''
    },
    'leaveProvince': False,
    'parkName': 'GLENDALE TRAILER PARK',
    'pad': '2',
    'taxCertificate': True,
    'taxExpiryDate': '2035-01-31T08:00:00+00:00'
  },
  'landStatusConfirmation': True
}
MOCK_AUTH_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
MOCK_PAY_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/pay/api/v1/'
DOC_ID_VALID = '63166035'

# testdata pattern is ({description}, {mhr_num}, {roles}, {status}, {account})
TEST_CREATE_DATA = [
    ('Invalid schema validation missing submitting', '000900', [MHR_ROLE, REQUEST_TRANSPORT_PERMIT],
     HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Missing account', '000900', [MHR_ROLE, REQUEST_TRANSPORT_PERMIT], HTTPStatus.BAD_REQUEST, None),
    ('Staff missing account', '000900', [MHR_ROLE, STAFF_ROLE, REQUEST_TRANSPORT_PERMIT], HTTPStatus.BAD_REQUEST, None),
    ('Invalid role product', '000900', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Invalid non-permit role', '000900', [MHR_ROLE, TRANSFER_SALE_BENEFICIARY], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Valid staff', '000900', [MHR_ROLE, STAFF_ROLE, REQUEST_TRANSPORT_PERMIT], HTTPStatus.CREATED, 'PS12345'),
    ('Valid non-staff legacy', '000900', [MHR_ROLE, REQUEST_TRANSPORT_PERMIT], HTTPStatus.CREATED, 'PS12345'),
    ('Invalid mhr num', '300655', [MHR_ROLE, REQUEST_TRANSPORT_PERMIT], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Invalid exempt', '000912', [MHR_ROLE, REQUEST_TRANSPORT_PERMIT], HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Invalid historical', '000913', [MHR_ROLE, REQUEST_TRANSPORT_PERMIT], HTTPStatus.BAD_REQUEST, 'PS12345')
]


@pytest.mark.parametrize('desc,mhr_num,roles,status,account', TEST_CREATE_DATA)
def test_create(session, client, jwt, desc, mhr_num, roles, status, account):
    """Assert that a post MH registration works as expected."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    json_data = copy.deepcopy(PERMIT)
    if STAFF_ROLE in roles:
        json_data['documentId'] = DOC_ID_VALID
    else:
        del json_data['documentId']
    json_data['mhrNumber'] = mhr_num
    if desc == 'Invalid schema validation missing submitting':
        del json_data['submittingParty']
    if account:
        headers = create_header_account(jwt, roles, 'UT-TEST', account)
    else:
        headers = create_header(jwt, roles)
    # test
    response = client.post('/api/v1/permits/' + mhr_num,
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    # current_app.logger.info(response.json)
    if desc == 'Invalid mhr num':
        assert response.status_code == status or response.status_code == HTTPStatus.NOT_FOUND
    else:
        assert response.status_code == status
    if response.status_code == HTTPStatus.CREATED:
        registration: MhrRegistration = MhrRegistration.find_by_mhr_number(response.json['mhrNumber'],
                                                                           account)
        assert registration
