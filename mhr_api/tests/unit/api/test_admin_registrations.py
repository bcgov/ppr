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

"""Tests to verify the endpoints for maintaining MH staff admin registrations.

Test-Suite to ensure that the /admin-registrations endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app

from mhr_api.models import MhrRegistration
from mhr_api.models.type_tables import MhrDocumentTypes
from mhr_api.services.authz import MHR_ROLE, STAFF_ROLE, COLIN_ROLE, TRANSFER_DEATH_JT
from tests.unit.services.utils import create_header, create_header_account


ADMIN_REGISTRATION = {
  'clientReferenceId': 'EX-TP001234',
  'attentionReference': 'JOHN SMITH',
  'documentType': 'NRED',
  'documentId': '62133670',
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
    'documentType': 'NRED',
    'documentId': '62133670',
    'remarks': 'REMARKS',
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
STAT_REGISTRATION = {
  'clientReferenceId': 'EX-TP001234',
  'attentionReference': 'JOHN SMITH',
  'documentType': 'STAT',
  'documentId': '80058756',
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
  'location': {
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
  }
}
MOCK_AUTH_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
MOCK_PAY_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/pay/api/v1/'

# testdata pattern is ({description}, {mhr_num}, {roles}, {status}, {account})
TEST_CREATE_DATA = [
    ('Invalid schema validation missing submitting', '000900', [MHR_ROLE, STAFF_ROLE],
     HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Staff missing account', '000900', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, None),
    ('Invalid role product', '000900', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Invalid non-staff role', '000900', [MHR_ROLE, TRANSFER_DEATH_JT], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Valid staff NCAN', '000915', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345'),
    ('Invalid mhr num', '300655', [MHR_ROLE, STAFF_ROLE], HTTPStatus.NOT_FOUND, 'PS12345'),
    ('Invalid exempt', '000912', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Invalid historical', '000913', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Invalid missing note party', '000900', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Valid staff NRED', '000914', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345'),
    ('Valid staff STAT', '000931', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345')
]


@pytest.mark.parametrize('desc,mhr_num,roles,status,account', TEST_CREATE_DATA)
def test_create(session, client, jwt, desc, mhr_num, roles, status, account):
    """Assert that a post MH registration works as expected."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    json_data = copy.deepcopy(ADMIN_REGISTRATION)
    if desc == 'Valid staff STAT':
        json_data = copy.deepcopy(STAT_REGISTRATION)
        json_data['mhrNumber'] = mhr_num
    else:
        json_data['mhrNumber'] = mhr_num
        json_data['documentType'] = MhrDocumentTypes.NRED
        json_data['note']['documentType'] = MhrDocumentTypes.NRED
    if desc == 'Invalid schema validation missing submitting':
        del json_data['submittingParty']
    elif desc == 'Invalid missing note party':
        del json_data['note']['givingNoticeParty']
    elif status == HTTPStatus.CREATED:
        json_data['documentId'] = '80058756'
        if json_data.get('note'):
            json_data['note']['documentId'] = '80058756'
    if mhr_num == '000914':
        json_data['updateDocumentId'] = 'UT000020'
    elif mhr_num == '000915':
        json_data['updateDocumentId'] = 'UT000022'
        json_data['documentType'] = MhrDocumentTypes.NCAN
        json_data['note']['documentType'] = MhrDocumentTypes.NCAN
    if account:
        headers = create_header_account(jwt, roles, 'UT-TEST', account)
    else:
        headers = create_header(jwt, roles)
    # test
    response = client.post('/api/v1/admin-registrations/' + mhr_num,
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    # current_app.logger.debug(response.json)
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
        if desc != 'Valid staff STAT':
            assert reg_json.get('note')
            note_json = reg_json.get('note')
            assert note_json.get('documentType')
            assert note_json.get('documentId')
            assert note_json.get('createDateTime')
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
            assert reg_json.get('documentType')
            assert reg_json.get('documentDescription')
        else:
            assert reg_json.get('location')
