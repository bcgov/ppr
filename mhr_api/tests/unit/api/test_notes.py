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

"""Tests to verify the endpoints for maintaining MH unit notes.

Test-Suite to ensure that the /notes endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app

from mhr_api.models import MhrRegistration
from mhr_api.services.authz import MHR_ROLE, STAFF_ROLE, COLIN_ROLE, TRANSFER_DEATH_JT
from tests.unit.services.utils import create_header, create_header_account


NOTE_REGISTRATION = {
  'clientReferenceId': 'EX-TP001234',
  'attentionReference': 'JOHN SMITH',
  'submittingParty': {
    'businessName': 'BOB PATERSON HOMES INC.',
    'address': {
      'street': '1200 S. MACKENZIE AVE.',
      'city': 'WILLIAMS LAKE',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V2G 3Y1'
    },
    'phoneNumber': '6044620279'
  },
  'note': {
    'documentType': 'CAU',
    'documentId': '62133670',
    'effectiveDateTime': '2023-02-21T18:56:00+00:00',
    'remarks': 'NOTICE OF ACTION COMMENCED MARCH 1 2022 WITH CRANBROOK COURT REGISTRY COURT FILE NO. 3011.',
    'givingNoticeParty': {
      'personName': {
        'first': 'JOHNNY',
        'middle': 'B',
        'last': 'SMITH'
      },
      'address': {
        'street': '222 SUMMER STREET',
        'city': 'VICTORIA',
        'region': 'BC',
        'country': 'CA',
        'postalCode': 'V8W 2V8'
      },
      'phoneNumber': '2504930122'
    }
  }
}
MOCK_AUTH_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
MOCK_PAY_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/pay/api/v1/'

# testdata pattern is ({description}, {mhr_num}, {roles}, {status}, {account})
TEST_CREATE_DATA = [
    ('Invalid schema validation missing submitting', '003936', [MHR_ROLE, STAFF_ROLE],
     HTTPStatus.BAD_REQUEST, 'ppr_staff'),
    ('Staff missing account', '003936', [MHR_ROLE, STAFF_ROLE],
     HTTPStatus.BAD_REQUEST, None),
    ('Invalid role product', '003936', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, 'ppr_staff'),
    ('Invalid non-staff role', '003936', [MHR_ROLE, TRANSFER_DEATH_JT], HTTPStatus.UNAUTHORIZED, 'ppr_staff'),
    ('Valid staff', '102876', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'ppr_staff'),
    ('Invalid mhr num', '300655', [MHR_ROLE, STAFF_ROLE], HTTPStatus.NOT_FOUND, 'ppr_staff'),
    ('Invalid exempt', '098655', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, 'ppr_staff'),
    ('Invalid historical', '099942', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, 'ppr_staff'),
    ('Invalid missing note remarks', '098666', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, 'ppr_staff')
]


@pytest.mark.parametrize('desc,mhr_num,roles,status,account', TEST_CREATE_DATA)
def test_create(session, client, jwt, desc, mhr_num, roles, status, account):
    """Assert that a post MH registration works as expected."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    json_data = copy.deepcopy(NOTE_REGISTRATION)
    json_data['mhrNumber'] = mhr_num
    if desc == 'Invalid schema validation missing submitting':
        del json_data['submittingParty']
    elif desc == 'Invalid missing note remarks':
        del json_data['note']['remarks']
    elif status == HTTPStatus.CREATED:
        json_data['note']['documentId'] = '80048756'
    if account:
        headers = create_header_account(jwt, roles, 'UT-TEST', account)
    else:
        headers = create_header(jwt, roles)
    # test
    response = client.post('/api/v1/notes/' + mhr_num,
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    current_app.logger.debug(response.json)
    assert response.status_code == status
    if response.status_code == HTTPStatus.CREATED:
        registration: MhrRegistration = MhrRegistration.find_by_mhr_number(response.json['mhrNumber'],
                                                                           account)
        assert registration
        reg_json = response.json
        assert reg_json.get('mhrNumber')
        assert reg_json.get('createDateTime')
        assert reg_json.get('registrationType')
        assert reg_json.get('clientReferenceId')
        assert reg_json.get('submittingParty')
        assert reg_json.get('note')
        note_json = reg_json.get('note')
        assert note_json.get('documentType')
        assert note_json.get('documentId')
        assert note_json.get('createDateTime')
        assert note_json.get('expiryDateTime')
        assert note_json.get('remarks') is not None
        assert note_json.get('givingNoticeParty')
        notice_json = note_json.get('givingNoticeParty')
        assert notice_json.get('personName')
        assert notice_json['personName'].get('first')
        assert notice_json['personName'].get('last')
        assert notice_json.get('phoneNumber')
        assert notice_json.get('address')
        assert notice_json['address']['street']
        assert notice_json['address']['city']
        assert notice_json['address']['region']
        assert notice_json['address']['country']
        assert notice_json['address']['postalCode'] is not None
