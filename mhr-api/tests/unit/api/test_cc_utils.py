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

"""Tests to assure the credit card payment helper functions.

Test-Suite to ensure that the credit card payment helper functions are working as expected.
"""
import copy

import pytest
from registry_schemas.example_data.mhr import REGISTRATION, EXEMPTION, PERMIT, TRANSFER

from mhr_api.models import MhrDraft, MhrRegistration
from mhr_api.models.mhr_draft import DRAFT_PAY_PENDING_PREFIX
from mhr_api.models.type_tables import MhrRegistrationStatusTypes, MhrRegistrationTypes
from mhr_api.resources import cc_payment_utils
from mhr_api.resources.registration_utils import setup_cc_draft


CC_PAYREF = {
     "invoiceId": "88888888",
     "receipt": "receipt",
     "ccPayment": True,
     "paymentActionRequired": True,
     "paymentPortalURL": "{PAYMENT_PORTAL_URL}/{invoice_id}/{return_URL}"
}
TEST_TRANSFER = {
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
    ]
}
# testdata pattern is ({pay_ref}, {account_id}, {username}, {usergroup}, {draft_json}, {draft_num}, {mhr_num}, {reg_type})
TEST_CHANGE_DATA = [
    (CC_PAYREF, "PS12345", "username", "mhr_qualified_user", TEST_TRANSFER, None, "000919", MhrRegistrationTypes.TRANS),
    (CC_PAYREF, "PS12345", "username", "mhr_qualified_user", TEST_TRANSFER, "T500001", "000919", MhrRegistrationTypes.TRANS)
]
TEST_NEW_DATA = [
    (CC_PAYREF, "PS12345", "username", "mhr_qualified_user", REGISTRATION, None, None, MhrRegistrationTypes.MHREG)
]
# testdata pattern is ({draft_json}, {mhr_num}, {reg_type}, {invoice_id})
TEST_REGISTRATION_DATA = [
    (REGISTRATION, None, MhrRegistrationTypes.MHREG.value, "20000200"),
    (EXEMPTION, "000919", MhrRegistrationTypes.EXEMPTION_RES.value, "20000201"),
    (PERMIT, "000900", MhrRegistrationTypes.PERMIT.value, "20000202"),
    (TRANSFER, "000919", MhrRegistrationTypes.TRANS.value, "20000203")
]


@pytest.mark.parametrize('pay_ref,account_id,username,usergroup,draft_json,draft_num,mhr_num,reg_type', TEST_CHANGE_DATA)
def test_change_registration(session, pay_ref, account_id, username, usergroup, draft_json, draft_num, mhr_num, reg_type):
    """Assert that a change registration is set up correctly for a credit card payment client registration."""
    json_data = copy.deepcopy(draft_json)
    json_data["registrationType"] = reg_type
    if not draft_num:
        del json_data["mhrNumber"]
    else:
        json_data["mhrNumber"] = mhr_num
    json_data = setup_cc_draft(json_data, pay_ref, account_id, username, usergroup)
    if draft_num:
        json_data["draftNumber"] = draft_num
    base_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    assert base_reg
    new_reg: MhrRegistration = cc_payment_utils.save_change_cc_draft(base_reg, json_data)
    assert not new_reg.id
    assert new_reg.draft
    assert new_reg.reg_json
    draft: MhrDraft = new_reg.draft
    assert draft.draft_number.startswith(DRAFT_PAY_PENDING_PREFIX)
    assert draft.user_id == pay_ref.get("invoiceId")
    assert draft.mhr_number == mhr_num
    assert draft.registration_type == reg_type
    reg_json = new_reg.reg_json
    assert reg_json.get("paymentPending")
    assert reg_json.get("status")
    assert reg_json["payment"] == pay_ref
    assert reg_json.get("accountId") == account_id
    assert reg_json.get("username") == username
    assert reg_json.get("usergroup") == usergroup
    assert reg_json.get("registrationType") == reg_type
    assert reg_json.get("mhrNumber") == mhr_num
    test_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    assert test_reg.status_type == MhrRegistrationStatusTypes.DRAFT.value


@pytest.mark.parametrize('pay_ref,account_id,username,usergroup,draft_json,draft_num,mhr_num,reg_type', TEST_NEW_DATA)
def test_new_registration(session, pay_ref, account_id, username, usergroup, draft_json, draft_num, mhr_num, reg_type):
    """Assert that a new home registration is set up correctly for a credit card payment client registration."""
    json_data = copy.deepcopy(draft_json)
    json_data["registrationType"] = reg_type
    if json_data.get("mhrNumber"):
        del json_data["mhrNumber"]
    json_data = setup_cc_draft(json_data, pay_ref, account_id, username, usergroup)
    if draft_num:
        json_data["draftNumber"] = draft_num
    new_reg: MhrRegistration = cc_payment_utils.save_new_cc_draft(json_data)
    assert not new_reg.id
    assert new_reg.draft
    assert new_reg.reg_json
    draft: MhrDraft = new_reg.draft
    assert draft.draft_number.startswith(DRAFT_PAY_PENDING_PREFIX)
    assert draft.user_id == pay_ref.get("invoiceId")
    assert not draft.mhr_number
    assert draft.registration_type == reg_type
    reg_json = new_reg.reg_json
    assert reg_json.get("paymentPending")
    assert reg_json.get("status")
    assert reg_json["payment"] == pay_ref
    assert reg_json.get("accountId") == account_id
    assert reg_json.get("username") == username
    assert reg_json.get("usergroup") == usergroup
    assert reg_json.get("registrationType") == reg_type
    assert not reg_json.get("mhrNumber")


def setup_registration(draft_json: dict, reg_type: str, invoice_id: str) -> dict:
    """Set up registration for cc processing."""
    json_data = copy.deepcopy(draft_json)
    json_data["registrationType"] = reg_type
    if json_data.get("mhrNumber") and reg_type == MhrRegistrationTypes.MHREG.value:
        del json_data["mhrNumber"]
    elif reg_type == MhrRegistrationTypes.EXEMPTION_RES.value:
        del json_data['documentId']
        del json_data['documentRegistrationNumber']
        del json_data['documentDescription']
        del json_data['createDateTime']
        json_data['nonResidential'] = False
    elif reg_type == MhrRegistrationTypes.PERMIT.value:
        del json_data['documentId']
        del json_data['documentRegistrationNumber']
        del json_data['documentDescription']
        del json_data['createDateTime']
        del json_data['payment']
        del json_data['note']
    elif reg_type == MhrRegistrationTypes.TRANS.value:
        del json_data['documentId']
        del json_data['documentDescription']
        del json_data['createDateTime']
        del json_data['payment']
    pay_ref: dict = copy.deepcopy(CC_PAYREF)
    if invoice_id:
        pay_ref["invoiceId"] = invoice_id
    json_data = setup_cc_draft(json_data, pay_ref, "PS12345", "username@idir", "ppr_staff")
    return json_data


@pytest.mark.parametrize('draft_json,mhr_num,reg_type,invoice_id', TEST_REGISTRATION_DATA)
def test_create_registration(session, draft_json, mhr_num, reg_type, invoice_id):
    """Assert that creating a new cc payment registration from a callback works as expected."""
    json_data = setup_registration(draft_json, reg_type, invoice_id)
    new_reg: MhrRegistration = None
    base_reg: MhrRegistration = None
    if reg_type == MhrRegistrationTypes.MHREG.value:
        new_reg = cc_payment_utils.save_new_cc_draft(json_data)
    else:
        json_data["mhrNumber"] = mhr_num
        base_reg: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, "PS12345", True)
        new_reg: MhrRegistration = cc_payment_utils.save_change_cc_draft(base_reg, json_data)
    draft: MhrDraft = MhrDraft.find_by_invoice_id(invoice_id)
    assert draft
    assert new_reg.draft
    test_reg: MhrRegistration = None
    if reg_type == MhrRegistrationTypes.MHREG.value:
        test_reg = cc_payment_utils.create_new_registration(draft)
        assert test_reg
        assert test_reg.mhr_number
        assert test_reg.owner_groups
        assert test_reg.descriptions
        assert test_reg.locations
    else:
        test_reg = cc_payment_utils.create_change_registration(draft, base_reg)
    assert test_reg.id > 0
    assert test_reg.documents
    assert test_reg.parties
    if reg_type == MhrRegistrationTypes.EXEMPTION_RES.value:
        base_reg = MhrRegistration.find_all_by_mhr_number(mhr_num, "PS12345", True)
        assert base_reg.status_type == MhrRegistrationStatusTypes.EXEMPT.value
    elif reg_type == MhrRegistrationTypes.PERMIT.value:
        assert test_reg.locations
    elif reg_type == MhrRegistrationTypes.TRANS.value:
        assert test_reg.owner_groups
