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

from mhr_api.models import MhrDraft, MhrRegistration, MhrReviewRegistration
from mhr_api.models.mhr_draft import DRAFT_STAFF_REVIEW_PREFIX
from mhr_api.models.type_tables import MhrRegistrationStatusTypes, MhrRegistrationTypes, MhrReviewStatusTypes
from mhr_api.resources import staff_review_utils
from mhr_api.resources.registration_utils import setup_staff_review


PAYREF = {
     "invoiceId": "88888888",
     "receipt": "receipt",
}
PAYREF_PRIORITY = {
     "invoiceId": "88888888",
     "receipt": "receipt",
     "priority": True
}
TEST_TRANSFER = {
    'mhrNumber': '125234',
    'registrationType': 'TRANS_WILL',
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
    (PAYREF, "PS12345", "username", "mhr_qualified_user", TEST_TRANSFER, None, "000919", MhrRegistrationTypes.TRANS_WILL),
    (PAYREF_PRIORITY, "PS12345", "username", "mhr_qualified_user", TEST_TRANSFER, None, "000919", MhrRegistrationTypes.TRANS_WILL)
]


@pytest.mark.parametrize('pay_ref,account_id,username,usergroup,draft_json,draft_num,mhr_num,reg_type', TEST_CHANGE_DATA)
def test_change_registration(session, pay_ref, account_id, username, usergroup, draft_json, draft_num, mhr_num, reg_type):
    """Assert that a change registration is set up correctly for a credit card payment client registration."""
    json_data = copy.deepcopy(draft_json)
    json_data["registrationType"] = reg_type
    json_data["mhrNumber"] = mhr_num
    json_data = setup_staff_review(json_data, pay_ref, account_id, username, usergroup)
    if draft_num:
        json_data["draftNumber"] = draft_num
    base_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    assert base_reg
    new_reg: MhrRegistration = staff_review_utils.save_review_registration(base_reg, json_data)
    assert not new_reg.id
    assert new_reg.draft
    assert new_reg.reg_json
    draft: MhrDraft = new_reg.draft
    assert draft.draft_number.startswith(DRAFT_STAFF_REVIEW_PREFIX)
    assert draft.mhr_number == mhr_num
    assert draft.registration_type == reg_type
    reg_json = new_reg.reg_json
    assert reg_json.get("reviewPending")
    assert reg_json.get("status")
    assert reg_json["payment"] == pay_ref
    assert reg_json.get("accountId") == account_id
    assert reg_json.get("username") == username
    assert reg_json.get("usergroup") == usergroup
    assert reg_json.get("registrationType") == reg_type
    assert reg_json.get("mhrNumber") == mhr_num
    test_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    assert test_reg.status_type == MhrRegistrationStatusTypes.DRAFT.value
    review_regs = MhrReviewRegistration.find_by_mhr_number(mhr_num)
    assert review_regs
    review_reg: MhrReviewRegistration = review_regs[0]
    assert review_reg.account_id == account_id
    assert review_reg.registration_type == reg_type
    assert review_reg.mhr_number == mhr_num
    assert review_reg.user_id == username
    assert review_reg.pay_invoice_id == int(pay_ref.get("invoiceId"))
    assert review_reg.pay_path == pay_ref.get("receipt")
    assert review_reg.priority == pay_ref.get("priority", False)
    assert review_reg.document_type
    assert review_reg.submitting_name
    assert review_reg.registration_data
    assert review_reg.status_type == MhrReviewStatusTypes.NEW
