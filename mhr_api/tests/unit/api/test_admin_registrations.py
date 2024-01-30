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

from mhr_api.models import MhrRegistrationReport, MhrDocument
from mhr_api.models.type_tables import MhrDocumentTypes, MhrRegistrationStatusTypes
from mhr_api.resources.v1.admin_registrations import get_transaction_type
from mhr_api.services.authz import BCOL_HELP_ROLE, MHR_ROLE, STAFF_ROLE, COLIN_ROLE, TRANSFER_DEATH_JT
from mhr_api.services.payment import TransactionTypes
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
REGC_PUBA_REGISTRATION = {
  'clientReferenceId': 'EX-TP001234',
  'attentionReference': 'JOHN SMITH',
  'documentType': 'REGC_STAFF',
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
  },
  'note': {
    'documentType': 'REGC_STAFF',
    'documentId': '80058756',
    'remarks': 'REMARKS'
  }
}
LOCATION_VALID = {
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
DESCRIPTION_VALID = {
  'manufacturer': 'STARLINE',
  'baseInformation': {
    'year': 2018,
    'make': 'WATSON IND. (ALTA)',
    'model': 'DUCHESS'
  },
  'sectionCount': 2,
  'sections': [
    {
      'serialNumber': '52D70556-A',
      'lengthFeet': 52,
      'lengthInches': 0,
      'widthFeet': 12,
      'widthInches': 0
    },
    {
      'serialNumber': '52D70556-B',
      'lengthFeet': 52,
      'lengthInches': 0,
      'widthFeet': 12,
      'widthInches': 0
    }
  ],
  'csaNumber': '786356',
  'csaStandard': 'Z240',
  'engineerDate': '2024-10-22T07:59:00+00:00',
  'engineerName': ' Dave Smith ENG. LTD.'
}
ADD_OG_VALID = [
    {
      'groupId': 2,
      'owners': [
        {
          'individualName': {
            'first': 'James',
            'last': 'Smith'
          },
          'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
          },
          'phoneNumber': '6041234567',
          'ownerId': 2
        }
      ],
      'type': 'SOLE'
    }
]
DELETE_OG_VALID = [
    {
        'groupId': 1,
        'owners': [
        {
            'individualName': {
            'first': 'Jane',
            'last': 'Smith'
            },
            'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
            },
            'phoneNumber': '6041234567',
            'ownerId': 1
        }
        ],
        'type': 'SOLE'
    }
]

MOCK_AUTH_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
MOCK_PAY_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/pay/api/v1/'

# testdata pattern is ({description}, {mhr_num}, {roles}, {status}, {account})
TEST_CREATE_DATA = [
    ('Invalid schema validation missing submitting', '000900', [MHR_ROLE, STAFF_ROLE],
     HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Staff missing account', '000900', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, None),
    ('Invalid role product', '000900', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Invalid BCOL helpdesk role', '000900', [MHR_ROLE, BCOL_HELP_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Invalid non-staff role', '000900', [MHR_ROLE, TRANSFER_DEATH_JT], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Valid staff NCAN', '000915', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345'),
    ('Invalid mhr num', '300655', [MHR_ROLE, STAFF_ROLE], HTTPStatus.NOT_FOUND, 'PS12345'),
    ('Invalid exempt', '000912', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Invalid historical', '000913', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Invalid missing note party', '000900', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Valid staff NRED', '000914', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345'),
    ('Valid staff STAT', '000931', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345'),
    ('Valid staff CANCEL_PERMIT', '000931', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345'),
    ('Valid staff PUBA location', '000931', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345'),
    ('Valid staff REGC location', '000931', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345'),
    ('Valid staff PUBA description', '000931', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345'),
    ('Valid staff REGC description', '000931', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345'),
    ('Valid staff PUBA owners', '000919', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345'),
    ('Valid staff REGC owners', '000919', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345')
]
# testdata pattern is ({description}, {mhr_num}, {account}, {doc_type}, {mh_status}, {region})
TEST_AMEND_CORRECT_STATUS_DATA = [
    ('Valid correct ACTIVE AB', '000912', 'PS12345', 'REGC_STAFF', MhrRegistrationStatusTypes.ACTIVE.value, 'AB'),
    ('Valid correct client ACTIVE', '000912', 'PS12345', 'REGC_CLIENT', MhrRegistrationStatusTypes.ACTIVE.value,  None),
    ('Valid amend ACTIVE AB', '000912', 'PS12345', 'PUBA', MhrRegistrationStatusTypes.ACTIVE.value, 'AB'),
    ('Valid correct EXEMPT', '000931', 'PS12345', 'REGC_CLIENT', MhrRegistrationStatusTypes.EXEMPT.value, 'BC'),
    ('Valid amend EXEMPT', '000931', 'PS12345', 'PUBA', MhrRegistrationStatusTypes.EXEMPT.value, 'AB')
]
# testdata pattern is ({doc_type}, {pay_trans_type})
TEST_TRANS_TYPE_DATA = [
    (MhrDocumentTypes.NRED, TransactionTypes.UNIT_NOTE),
    (MhrDocumentTypes.NCAN, TransactionTypes.UNIT_NOTE),
    (MhrDocumentTypes.STAT, TransactionTypes.ADMIN_RLCHG),
    (MhrDocumentTypes.REGC_CLIENT, TransactionTypes.CORRECTION),
    (MhrDocumentTypes.REGC_STAFF, TransactionTypes.CORRECTION),
    (MhrDocumentTypes.PUBA, TransactionTypes.AMENDMENT)
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
    elif desc == 'Valid staff REGC location':
        json_data = copy.deepcopy(REGC_PUBA_REGISTRATION)
        json_data['mhrNumber'] = mhr_num
        json_data['documentType'] = MhrDocumentTypes.REGC_STAFF
        json_data['note']['documentType'] = MhrDocumentTypes.REGC_STAFF
    elif desc == 'Valid staff PUBA location':
        json_data = copy.deepcopy(REGC_PUBA_REGISTRATION)
        json_data['mhrNumber'] = mhr_num
        json_data['documentType'] = MhrDocumentTypes.PUBA
        json_data['note']['documentType'] = MhrDocumentTypes.PUBA
    elif desc == 'Valid staff CANCEL_PERMIT':
        json_data['mhrNumber'] = mhr_num
        json_data['documentType'] = MhrDocumentTypes.CANCEL_PERMIT
        json_data['updateDocumentId'] = 'UT000046'
        del json_data['note']
        json_data['location'] = copy.deepcopy(LOCATION_VALID)
    elif desc == 'Valid staff PUBA description':
        json_data = copy.deepcopy(REGC_PUBA_REGISTRATION)
        json_data['mhrNumber'] = mhr_num
        json_data['documentType'] = MhrDocumentTypes.PUBA
        del json_data['note']
        del json_data['location']
        json_data['description'] = DESCRIPTION_VALID
    elif desc == 'Valid staff REGC description':
        json_data = copy.deepcopy(REGC_PUBA_REGISTRATION)
        json_data['mhrNumber'] = mhr_num
        json_data['documentType'] = MhrDocumentTypes.REGC_CLIENT
        del json_data['note']
        del json_data['location']
        json_data['description'] = DESCRIPTION_VALID
    elif desc == 'Valid staff PUBA owners':
        json_data = copy.deepcopy(REGC_PUBA_REGISTRATION)
        json_data['mhrNumber'] = mhr_num
        json_data['documentType'] = MhrDocumentTypes.PUBA
        del json_data['note']
        del json_data['location']
        json_data['addOwnerGroups'] = ADD_OG_VALID
        json_data['deleteOwnerGroups'] = DELETE_OG_VALID
    elif desc == 'Valid staff REGC owners':
        json_data = copy.deepcopy(REGC_PUBA_REGISTRATION)
        json_data['mhrNumber'] = mhr_num
        json_data['documentType'] = MhrDocumentTypes.REGC_STAFF
        del json_data['note']
        del json_data['location']
        json_data['addOwnerGroups'] = ADD_OG_VALID
        json_data['deleteOwnerGroups'] = DELETE_OG_VALID
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
        reg_json = response.json
        doc_id = reg_json.get('documentId')
        if not doc_id:
            doc_id = reg_json['note']['documentId']
        doc: MhrDocument = MhrDocument.find_by_document_id(doc_id)
        assert doc
        assert reg_json.get('mhrNumber')
        assert reg_json.get('createDateTime')
        assert reg_json.get('registrationType')
        assert reg_json.get('clientReferenceId')
        assert reg_json.get('submittingParty')
        if desc not in ('Valid staff STAT', 'Valid staff CANCEL_PERMIT') and \
              json_data.get('documentType') not in (MhrDocumentTypes.REGC_STAFF,
                                                    MhrDocumentTypes.REGC_CLIENT,
                                                    MhrDocumentTypes.PUBA):
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
        if json_data['documentType'] in (MhrDocumentTypes.STAT,
                                         MhrDocumentTypes.PUBA,
                                         MhrDocumentTypes.REGC_STAFF,
                                         MhrDocumentTypes.REGC_CLIENT,
                                         MhrDocumentTypes.CANCEL_PERMIT):
            if json_data.get('location'):
                assert reg_json.get('location')
            else:
                assert not reg_json.get('location')
            if json_data.get('description'):
                assert reg_json.get('description')
            else:
                assert not reg_json.get('description')
            if json_data.get('addOwnerGroups'):
                assert reg_json.get('addOwnerGroups')
                assert reg_json.get('deleteOwnerGroups')
            else:
                assert not reg_json.get('addOwnerGroups')
                assert not reg_json.get('deleteOwnerGroups')
            if doc:
                assert doc.document_type == json_data['documentType']
                reg_report: MhrRegistrationReport = MhrRegistrationReport.find_by_registration_id(doc.registration_id)
                assert reg_report
                assert reg_report.batch_registration_data


@pytest.mark.parametrize('desc,mhr_num,account,doc_type,mh_status,region', TEST_AMEND_CORRECT_STATUS_DATA)
def test_amend_correct_status(session, client, jwt, desc, mhr_num, account, doc_type, mh_status, region):
    """Assert that a post MH amendment/correction status change registration works as expected."""
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = create_header_account(jwt, [MHR_ROLE, STAFF_ROLE], 'UT-TEST', account)
    json_data = copy.deepcopy(REGC_PUBA_REGISTRATION)
    json_data['mhrNumber'] = mhr_num
    json_data['documentType'] = doc_type
    json_data['status'] = mh_status
    del json_data['note']
    if not region:
          del json_data['location']
    else:
          json_data['location']['address']['region'] = region
    # test
    response = client.post('/api/v1/admin-registrations/' + mhr_num,
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    # current_app.logger.debug(response.json)
    assert response.status_code == HTTPStatus.CREATED
    reg_json = response.json
    assert reg_json.get('documentType') == doc_type
    assert reg_json.get('status') == mh_status
    doc_id = reg_json.get('documentId')
    doc: MhrDocument = MhrDocument.find_by_document_id(doc_id)
    assert doc.document_type == json_data['documentType']
    reg_report: MhrRegistrationReport = MhrRegistrationReport.find_by_registration_id(doc.registration_id)
    assert reg_report
    assert reg_report.batch_registration_data


@pytest.mark.parametrize('doc_type,pay_trans_type', TEST_TRANS_TYPE_DATA)
def test_transaction_type(session, client, jwt, doc_type, pay_trans_type):
    """Assert that mapping document type to payment transaction type works as expected."""
    json_data = {
        'documentType': doc_type
    }
    trans_type: str = get_transaction_type(json_data)
    assert trans_type == pay_trans_type
