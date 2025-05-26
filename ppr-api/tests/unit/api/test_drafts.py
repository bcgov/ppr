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

"""Tests to verify the drafts endpoint.

Test-Suite to ensure that the /drafts endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest

from registry_schemas.example_data.ppr import DRAFT_FINANCING_STATEMENT, DRAFT_CHANGE_STATEMENT, \
     DRAFT_AMENDMENT_STATEMENT, AMENDMENT_STATEMENT, FINANCING_STATEMENT

from ppr_api.models import Draft, FinancingStatement, Registration, utils as model_utils
from ppr_api.resources import cc_payment_utils, utils as resource_utils
from ppr_api.resources.financing_utils import setup_cc_draft
from ppr_api.services.authz import STAFF_ROLE, COLIN_ROLE, PPR_ROLE
from tests.unit.services.utils import create_header_account, create_header


CC_PAYREF = {
     "invoiceId": "88888888",
     "receipt": "receipt",
     "ccPayment": True,
     "paymentActionRequired": True,
     "paymentPortalURL": "{PAYMENT_PORTAL_URL}/{invoice_id}/{return_URL}"
}
# prep sample post, put draft statement data
SAMPLE_JSON_FINANCING = copy.deepcopy(DRAFT_FINANCING_STATEMENT)
SAMPLE_JSON_CHANGE = copy.deepcopy(DRAFT_CHANGE_STATEMENT)
SAMPLE_JSON_AMENDMENT = copy.deepcopy(DRAFT_AMENDMENT_STATEMENT)
# testdata pattern is ({desc}, {role}, {status}, {draft_json}, {reg_num}, {reg_type}, {invoice_id}, {draft_num})
TEST_CANCEL_DRAFT = [
    ('Valid new SA', [PPR_ROLE], HTTPStatus.OK, FINANCING_STATEMENT, None, "SA", "20000100", None),
    ('Valid amendment', [PPR_ROLE], HTTPStatus.OK, AMENDMENT_STATEMENT, "TEST0001", "AM", "20000102", None),
    ('Missing account', [PPR_ROLE], HTTPStatus.BAD_REQUEST, FINANCING_STATEMENT, None, "SA", "20000100", 'PT500002'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, FINANCING_STATEMENT, None, "SA", "20000100", 'PT500002'),
    ('Invalid Draft Number', [PPR_ROLE], HTTPStatus.NOT_FOUND, FINANCING_STATEMENT, None, "SA", "20000100", 'PT500002'),
]


def test_draft_create_invalid_type(session, client, jwt):
    """Assert that create draft  with an invalid type returns a 404 error."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)
    json_data['type'] = 'INVALID_TYPE'

    # test
    rv = client.post('/api/v1/drafts',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.INTERNAL_SERVER_ERROR


def test_draft_create_valid_financing_201(session, client, jwt):
    """Assert that a valid draft financing statement returns a 201 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)

    # test
    rv = client.post('/api/v1/drafts',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED
    assert rv.json['financingStatement']['documentId']

    # now delete draft
    document_id = rv.json['financingStatement']['documentId']
    rv2 = client.delete('/api/v1/drafts/' + document_id,
                        headers=create_header_account(jwt, [PPR_ROLE]))
    # check delete
    assert rv2.status_code == HTTPStatus.NO_CONTENT


def test_draft_create_valid_amendment_201(session, client, jwt):
    """Assert that a valid draft amendment statement returns a 201 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_AMENDMENT)

    # test
    rv = client.post('/api/v1/drafts',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED
    assert rv.json['amendmentStatement']['documentId']

    # now delete draft
    document_id = rv.json['amendmentStatement']['documentId']
    rv2 = client.delete('/api/v1/drafts/' + document_id,
                        headers=create_header_account(jwt, [PPR_ROLE]))
    # check delete
    assert rv2.status_code == HTTPStatus.NO_CONTENT


def test_draft_valid_change_201(session, client, jwt):
    """Assert that a valid draft change statement returns a 201 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_CHANGE)

    # test
    rv = client.post('/api/v1/drafts',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED
    assert rv.json['changeStatement']['documentId']

    # now delete draft
    document_id = rv.json['changeStatement']['documentId']
    rv2 = client.delete('/api/v1/drafts/' + document_id,
                        headers=create_header_account(jwt, [PPR_ROLE]))
    # check delete
    assert rv2.status_code == HTTPStatus.NO_CONTENT


def test_draft_get_list_200(session, client, jwt):
    """Assert that a get draft list for an account returns a 200 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts',
                    headers=create_header_account(jwt, [PPR_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.OK


def test_draft_valid_get_statement_200(session, client, jwt):
    """Assert that a valid get draft by document ID returns a 200 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts/D-T-FS01',
                    headers=create_header_account(jwt, [PPR_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.OK


def test_draft_invalid_get_statement_404(session, client, jwt):
    """Assert that a get draft by invalid document ID returns a 404 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts/D0012345',
                    headers=create_header_account(jwt, [PPR_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_draft_update_invalid_type_404(session, client, jwt):
    """Assert that an update draft financing statement request with an invalid type returns a 404."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)
    json_data['financingStatement']['type'] = 'XA'

    # test
    rv = client.put('/api/v1/drafts/D0034001',
                    json=json_data,
                    headers=create_header_account(jwt, [PPR_ROLE]),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_draft_update_valid_financing_200(session, client, jwt):
    """Assert that a valid draft financing statement update request returns a 200 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)

    # test
    rv = client.put('/api/v1/drafts/D-T-FS01',
                    json=json_data,
                    headers=create_header_account(jwt, [PPR_ROLE]),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.OK


def test_draft_update_valid_amendment_200(session, client, jwt):
    """Assert that a valid draft amendment statement update request returns a 200 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_AMENDMENT)

    # test
    rv = client.put('/api/v1/drafts/D-T-AM01',
                    json=json_data,
                    headers=create_header_account(jwt, [PPR_ROLE]),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.OK


def test_draft_update_valid_change_200(session, client, jwt):
    """Assert that a valid draft change statement update request returns a 200 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_CHANGE)

    # test
    rv = client.put('/api/v1/drafts/D-T-CH01',
                    json=json_data,
                    headers=create_header_account(jwt, [PPR_ROLE]),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.OK

# def test_draft_delete_204(session, client, jwt):
#    """Assert that a valid delete draft request returns a 204 status."""
    # setup

    # test
#    rv = client.delete(f'/api/v1/drafts/TEST-FSD1',
#                       headers=create_header_account(jwt, [PPR_ROLE]))
    # check
#    assert rv.status_code == HTTPStatus.NO_CONTENT


def test_draft_delete_404(session, client, jwt):
    """Assert that an invalid delete draft document ID returns a 404 status."""
    # setup

    # test
    rv = client.delete('/api/v1/drafts/X12345X',
                       headers=create_header_account(jwt, [PPR_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_draft_create_nonstaff_missing_account_400(session, client, jwt):
    """Assert that a non-staff draft request with no account ID returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)

    # test
    rv = client.post('/api/v1/drafts',
                     json=json_data,
                     headers=create_header(jwt, [COLIN_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_draft_create_staff_missing_account_400(session, client, jwt):
    """Assert that a staff draft request with no account ID returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)

    # test
    rv = client.post('/api/v1/drafts',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_draft_create_nonstaff_unauthorized_401(session, client, jwt):
    """Assert that a non-ppr role draft request with an account ID returns a 404 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)

    # test
    rv = client.post('/api/v1/drafts',
                     json=json_data,
                     headers=create_header_account(jwt, [COLIN_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_draft_list_nonstaff_missing_account_400(session, client, jwt):
    """Assert that a non-staff draft list request with no account ID returns a 400 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts',
                    headers=create_header(jwt, [COLIN_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_draft_list_staff_missing_account_400(session, client, jwt):
    """Assert that a staff draft list request with no account ID returns a 400 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts',
                    headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_draft_list_nonstaff_unauthorized_401(session, client, jwt):
    """Assert that a non-ppr role draft list request with an account ID returns a 404 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts',
                    headers=create_header_account(jwt, [COLIN_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_draft_update_nonstaff_missing_account_400(session, client, jwt):
    """Assert that a non-staff update draft request with no account ID returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)

    # test
    rv = client.put('/api/v1/drafts/TEST-FSD1',
                    json=json_data,
                    headers=create_header(jwt, [COLIN_ROLE]),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_draft_update_staff_missing_account_400(session, client, jwt):
    """Assert that a staff update draft request with no account ID returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)

    # test
    rv = client.put('/api/v1/drafts/TEST-FSD1',
                    json=json_data,
                    headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_draft_update_nonstaff_unauthorized_401(session, client, jwt):
    """Assert that a non-ppr role update draft request with an account ID returns a 404 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)

    # test
    rv = client.put('/api/v1/drafts/TEST-FSD1',
                    json=json_data,
                    headers=create_header_account(jwt, [COLIN_ROLE]),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_draft_get_nonstaff_missing_account_400(session, client, jwt):
    """Assert that a non-staff draft get request with no account ID returns a 400 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts/TEST-FSD1',
                    headers=create_header(jwt, [COLIN_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_draft_get_staff_missing_account_400(session, client, jwt):
    """Assert that a staff draft get request with no account ID returns a 201 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts/D-T-FS01',
                    headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_draft_get_nonstaff_unauthorized_401(session, client, jwt):
    """Assert that a non-ppr role draft get request with an account ID returns a 404 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts/TEST-FSD1',
                    headers=create_header_account(jwt, [COLIN_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize('desc,roles,status,draft_json,reg_num,reg_type,invoice_id,draft_num', TEST_CANCEL_DRAFT)
def test_cancel_drafts(session, client, jwt, desc, roles, status, draft_json, reg_num, reg_type, invoice_id, draft_num):
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
        new_reg: Registration = None
        base_reg: Registration = None
        if reg_type == "SA":
            save_reg: Registration = resource_utils.create_new_pay_registration(json_data, "PS12345")
            new_fs: FinancingStatement = cc_payment_utils.save_new_cc_draft(json_data, save_reg)
            new_reg = new_fs.registration[0]
        else:
            financing_statement: FinancingStatement = FinancingStatement.find_by_financing_id(200000000)
            assert financing_statement
            for party in financing_statement.parties:
                if party.registration_id != 200000000 and not party.registration_id_end:
                    if party.party_type == 'DB' or party.party_type == 'DI':
                        json_data['deleteDebtors'][0]['partyId'] = party.id
                    elif party.party_type == 'SP':
                        json_data['deleteSecuredParties'][0]['partyId'] = party.id

            for gc in financing_statement.general_collateral:
                if gc.registration_id != 200000000 and not gc.registration_id_end:
                    json_data['deleteGeneralCollateral'][0]['collateralId'] = gc.id

            for vc in financing_statement.vehicle_collateral:
                if vc.registration_id != 200000000 and not vc.registration_id_end:
                    json_data['deleteVehicleCollateral'][0]['vehicleId'] = vc.id

            save_reg: Registration = resource_utils.create_new_pay_registration(json_data, "PS12345", model_utils.REG_CLASS_AMEND)
            new_reg: Registration = cc_payment_utils.save_change_cc_draft(financing_statement.registration[0],
                                                                          json_data,
                                                                          save_reg)
        draft: Draft = new_reg.draft
        test_id = draft.document_number

    rv = client.patch('/api/v1/drafts/cancel/' + test_id, headers=headers)

    # check
    assert rv.status_code == status


def setup_cancel_registration(draft_json: dict, reg_type: str, invoice_id: str) -> dict:
    """Create pending draft to cancel."""
    json_data = copy.deepcopy(draft_json)
    if reg_type == "SA":
        json_data['type'] = reg_type
        del json_data['createDateTime']
        del json_data['baseRegistrationNumber']
        del json_data['payment']
        del json_data['lifeInfinite']
        del json_data['expiryDate']
        del json_data['documentId']
        del json_data['lienAmount']
        del json_data['surrenderDate']
    elif reg_type == "AM":
        del json_data['createDateTime']
        del json_data['amendmentRegistrationNumber']
        del json_data['payment']
        del json_data['addTrustIndenture']
        del json_data['removeTrustIndenture']
        if json_data.get("courtOrderInformation"):
            del json_data["courtOrderInformation"]
        if "documentId" in json_data:
            del json_data["documentId"]
    pay_ref: dict = copy.deepcopy(CC_PAYREF)
    if invoice_id:
        pay_ref["invoiceId"] = invoice_id
    json_data = setup_cc_draft(json_data, pay_ref, "PS12345", "username@idir")
    return json_data
