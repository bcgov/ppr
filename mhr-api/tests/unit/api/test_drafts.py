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

"""Tests to verify the endpoints for maintaining MH draft registrations.

Test-Suite to ensure that the /drafts endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app
from registry_schemas.example_data.mhr import REGISTRATION, PERMIT

from mhr_api.models import MhrDraft, MhrRegistration
from mhr_api.models.type_tables import MhrRegistrationTypes
from mhr_api.resources import cc_payment_utils
from mhr_api.resources.registration_utils import setup_cc_draft
from mhr_api.services.authz import COLIN_ROLE, MHR_ROLE, STAFF_ROLE
from tests.unit.services.utils import create_header, create_header_account


DRAFT_TRANSFER = {
  'type': 'TRANS',
  'registration': {
    'mhrNumber': '125234',
    'clientReferenceId': 'EX-TRANS-001',
    'submittingParty': {
      'businessName': 'ABC SEARCHING COMPANY',
      'address': {
        'street': '222 SUMMER STREET',
        'city': 'VICTORIA',
        'region': 'BC',
        'country': 'CA',
        'postalCode': 'V8W 2V8'
      },
      'emailAddress': 'bsmith@abc-search.com',
      'phoneNumber': '6041234567',
      'phoneExtension': '546'
    },
    'deleteOwnerGroups': [
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
            'phoneNumber': '6041234567'
          }
        ],
        'type': 'SOLE'
      }
    ],
    'addOwnerGroups': [
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
            'phoneNumber': '6041234567'
          }
        ],
        'type': 'SOLE',
        'status': 'ACTIVE'
      }
    ],
  }
}
CC_PAYREF = {
     "invoiceId": "88888888",
     "receipt": "receipt",
     "ccPayment": True,
     "paymentActionRequired": True,
     "paymentPortalURL": "{PAYMENT_PORTAL_URL}/{invoice_id}/{return_URL}"
}

# testdata pattern is ({desc}, {roles}, {status}, {has_account}, {results_size})
TEST_GET_ACCOUNT_DATA = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, False, 0),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 0),
    ('Valid request', [MHR_ROLE], HTTPStatus.OK, True, 2),
    ('Invalid request staff no account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, 0)
]
# testdata pattern is ({description}, {roles}, {status}, {has_account}, {reg_type})
TEST_CREATE_DATA = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, False, MhrRegistrationTypes.TRANS),
    ('Staff missing account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, MhrRegistrationTypes.TRANS),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, MhrRegistrationTypes.TRANS),
    ('Invalid type schema validation', [MHR_ROLE], HTTPStatus.BAD_REQUEST, True, 'XXXXX'),
    ('Valid', [MHR_ROLE], HTTPStatus.CREATED, True, MhrRegistrationTypes.TRANS)
]
# testdata pattern is ({description}, {roles}, {status}, {account}, {draft_num})
TEST_GET_DRAFT = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, None, 'T500002'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345', 'T500002'),
    ('Valid Request', [MHR_ROLE], HTTPStatus.OK, 'PS12345', 'T500002'),
    ('Invalid Draft Number', [MHR_ROLE], HTTPStatus.NOT_FOUND, 'PS12345', 'XXXXXX'),
    ('Invalid request Staff no account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, None, 'T500002')
]
# testdata pattern is ({results_size}, {params})
TEST_GET_ACCOUNT_DATA_FILTER = [
    (2, '?sortCriteriaName=createDateTime&sortDirection=ascending'),
    (2, '?sortCriteriaName=mhrNumber&sortDirection=descending'),
    (2, '?sortCriteriaName=clientReferenceId&sortDirection=ascending'),
    (2, '?sortCriteriaName=submittingName'),
    (2, '?sortCriteriaName=username'),
    (2, '?sortCriteriaName=registrationType&sortDirection=ascending'),
    (1, '?mhrNumber=000900'),
    (2, '?submittingName=ABC&username=TEST USER'),
    (2, '?startDateTime=2022-08-01T23:59:27%2B00:00&endDateTime=2030-12-31T23:59:27%2B00:00'),
    (1, '?registrationType=MANUFACTURED HOME REGISTRATION&clientReferenceId=EX&sortCriteriaName=createDateTime')
]
# testdata pattern is ({desc}, {role}, {status}, {draft_json}, {mhr_num}, {reg_type}, {invoice_id}, {draft_num})
TEST_CANCEL_DRAFT = [
    ('Valid new reg', [MHR_ROLE], HTTPStatus.OK, REGISTRATION, None, MhrRegistrationTypes.MHREG.value, "20000100", None),
    ('Valid permit', [MHR_ROLE], HTTPStatus.OK, PERMIT, "000900", MhrRegistrationTypes.PERMIT.value, "20000102", None),
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, REGISTRATION, None, MhrRegistrationTypes.MHREG.value, "20000100", 'PT500002'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, REGISTRATION, None, MhrRegistrationTypes.MHREG.value, "20000100", 'PT500002'),
    ('Invalid Draft Number', [MHR_ROLE], HTTPStatus.NOT_FOUND, REGISTRATION, None, MhrRegistrationTypes.MHREG.value, "20000100", 'PT500002'),
]


@pytest.mark.parametrize('desc,roles,status,has_account,results_size', TEST_GET_ACCOUNT_DATA)
def test_get_account_drafts(session, client, jwt, desc, roles, status, has_account, results_size):
    """Assert that a get account drafts summary list endpoint works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    # test
    rv = client.get('/api/v1/drafts',
                    headers=headers)

    # check
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        assert rv.json
        assert len(rv.json) >= results_size
        for registration in rv.json:
            assert registration['draftNumber']
            assert registration['registrationType'] is not None
            assert registration['registrationDescription']
            assert registration['createDateTime'] is not None
            assert registration['lastUpdateDateTime'] is not None
            assert registration['registeringName'] is not None
            assert registration['submittingParty'] is not None
            assert registration['clientReferenceId'] is not None
            assert registration['path'] is not None
            if registration['registrationType'] != MhrRegistrationTypes.MHREG:
                assert registration.get('mhrNumber')


@pytest.mark.parametrize('results_size,request_params', TEST_GET_ACCOUNT_DATA_FILTER)
def test_get_account_drafts_filter(session, client, jwt, results_size, request_params):
    """Assert that a get account drafts summary list endpoint works as expected with sorting and filtering."""
    headers = None
    # setup
    headers = create_header_account(jwt, [MHR_ROLE])
    # test
    rv = client.get('/api/v1/drafts' + request_params,
                    headers=headers)

    # check
    assert rv.status_code == HTTPStatus.OK
    assert rv.json
    assert len(rv.json) >= results_size


@pytest.mark.parametrize('desc,roles,status,has_account,reg_type', TEST_CREATE_DATA)
def test_create_draft(session, client, jwt, desc, roles, status, has_account, reg_type):
    """Assert that a post MH draft works as expected."""
    # setup
    headers = None
    json_data = {
        'type': reg_type,
        'registration': copy.deepcopy(DRAFT_TRANSFER)
    }
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.post('/api/v1/drafts',
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    assert response.status_code == status
    if response.status_code == HTTPStatus.CREATED:
        draft: MhrDraft = MhrDraft.find_by_draft_number(response.json['draftNumber'], False)
        assert draft


@pytest.mark.parametrize('desc,roles,status,account_id,draft_num', TEST_GET_DRAFT)
def test_get_draft(session, client, jwt, desc, roles, status, account_id, draft_num):
    """Assert that a get account draft by draft number works as expected."""
    # setup
    headers = None
    if account_id:
        headers = create_header_account(jwt, roles, 'test-user', account_id)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.get('/api/v1/drafts/' + draft_num,
                          headers=headers)
    # check
    assert response.status_code == status


@pytest.mark.parametrize('desc,roles,status,account_id,draft_num', TEST_GET_DRAFT)
def test_delete_draft(session, client, jwt, desc, roles, status, account_id, draft_num):
    """Assert that a delete account draft by draft number works as expected."""
    # setup
    headers = None
    if account_id:
        headers = create_header_account(jwt, roles, 'test-user', account_id)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.delete('/api/v1/drafts/' + draft_num,
                             headers=headers)
    # check
    if status != HTTPStatus.OK:
        assert response.status_code == status
    else:
        assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.parametrize('desc,roles,status,account_id,draft_num', TEST_GET_DRAFT)
def test_update_draft(session, client, jwt, desc, roles, status, account_id, draft_num):
    """Assert that an update account draft by draft number works as expected."""
    # setup
    json_data = {
        'registration': copy.deepcopy(DRAFT_TRANSFER)
    }
    headers = None
    if account_id:
        headers = create_header_account(jwt, roles, 'test-user', account_id)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.put('/api/v1/drafts/' + draft_num,
                          json=json_data,
                          headers=headers,
                          content_type='application/json')
    # check
    assert response.status_code == status


@pytest.mark.parametrize('desc,roles,status,draft_json,mhr_num,reg_type,invoice_id,draft_num', TEST_CANCEL_DRAFT)
def test_cancel_drafts(session, client, jwt, desc, roles, status, draft_json, mhr_num, reg_type, invoice_id, draft_num):
    """Assert that cancelling a draft in a pending state works as expected."""
    headers = None
    # setup
    test_id: str = draft_num if draft_num else ""
    if desc != "Missing account":
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    # test
    if status == HTTPStatus.OK:
        json_data = setup_cancel_registration(draft_json, reg_type, invoice_id)
        new_reg: MhrRegistration = None
        base_reg: MhrRegistration = None
        if reg_type == MhrRegistrationTypes.MHREG.value:
            new_reg = cc_payment_utils.save_new_cc_draft(json_data)
        else:
            json_data["mhrNumber"] = mhr_num
            base_reg: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, "PS12345", True)
            new_reg = cc_payment_utils.save_change_cc_draft(base_reg, json_data)
        test_id = new_reg.draft.draft_number

    rv = client.patch('/api/v1/drafts/cancel/' + test_id, headers=headers)

    # check
    assert rv.status_code == status


def setup_cancel_registration(draft_json: dict, reg_type: str, invoice_id: str) -> dict:
    """Create pending draft to cancel."""
    json_data = copy.deepcopy(draft_json)
    json_data["registrationType"] = reg_type
    if json_data.get("mhrNumber") and reg_type == MhrRegistrationTypes.MHREG.value:
        del json_data["mhrNumber"]
    elif reg_type == MhrRegistrationTypes.PERMIT.value:
        del json_data['documentId']
        del json_data['documentRegistrationNumber']
        del json_data['documentDescription']
        del json_data['createDateTime']
        del json_data['payment']
        del json_data['note']
    pay_ref: dict = copy.deepcopy(CC_PAYREF)
    if invoice_id:
        pay_ref["invoiceId"] = invoice_id
    json_data = setup_cc_draft(json_data, pay_ref, "PS12345", "username@idir", "ppr_staff")
    return json_data
