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

"""Tests to assure the MHR review registration Model.

Test-Suite to ensure that the MHR review registration Model is working as expected.
"""
import copy

import pytest

from mhr_api.models import MhrDraft, MhrReviewRegistration, utils as model_utils
from mhr_api.models.type_tables import MhrRegistrationTypes, MhrReviewStatusTypes


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
    'reviewPending': True,
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
# testdata pattern is ({pay_ref}, {account_id}, {username}, {draft_json}, {mhr_num}, {reg_type}, {test_id})
TEST_DATA = [
    (PAYREF, "PS12345", "username", TEST_TRANSFER, "000919", MhrRegistrationTypes.TRANS_WILL, 300000001),
    (PAYREF_PRIORITY, "PS12345", "username", TEST_TRANSFER, "000919", MhrRegistrationTypes.TRANS_WILL, 300000002)
]

# testdata pattern is ({pay_ref}, {account_id}, {username}, {draft_json}, {mhr_num}, {reg_type}, {test_id})
TEST_ID_DATA = [
    (PAYREF, "PS12345", "username", TEST_TRANSFER, "000919", MhrRegistrationTypes.TRANS_WILL, 300000001),
]


@pytest.mark.parametrize('pay_ref,account_id,username,draft_json,mhr_num,reg_type,test_id', TEST_ID_DATA)
def test_find_by_id(session, pay_ref, account_id, username, draft_json, mhr_num, reg_type, test_id):
    """Assert that find mhr review registrations by id contains all expected elements."""
    json_data = copy.deepcopy(draft_json)
    json_data["payment"] = copy.deepcopy(pay_ref)
    draft: MhrDraft = MhrDraft(id=test_id,
                               draft_number="UT123434",
                               create_ts=model_utils.now_ts(),
                               update_ts=model_utils.now_ts(),
                               account_id=account_id,
                               user_id=username,
                               registration_type=reg_type,
                               mhr_number=mhr_num)
    draft.draft = json_data
    review_reg: MhrReviewRegistration = MhrReviewRegistration.create_from_json(json_data, draft)
    review_reg.id = test_id
    review_reg.save()
    test_reg = MhrReviewRegistration.find_by_id(test_id)
    assert test_reg
    assert test_reg.account_id == account_id
    assert test_reg.draft_id == test_id
    assert test_reg.registration_type == reg_type
    assert test_reg.mhr_number == mhr_num
    assert test_reg.user_id == username
    assert test_reg.pay_invoice_id == int(pay_ref.get("invoiceId"))
    assert test_reg.pay_path == pay_ref.get("receipt")
    assert test_reg.priority == pay_ref.get("priority", False)
    assert test_reg.document_type
    assert test_reg.submitting_name
    assert test_reg.registration_data
    assert test_reg.status_type == MhrReviewStatusTypes.NEW


@pytest.mark.parametrize('pay_ref,account_id,username,draft_json,mhr_num,reg_type,test_id', TEST_ID_DATA)
def test_find_by_mhr_num(session, pay_ref, account_id, username, draft_json, mhr_num, reg_type, test_id):
    """Assert that find mhr review registrations by mhr number contains all expected elements."""
    json_data = copy.deepcopy(draft_json)
    json_data["payment"] = copy.deepcopy(pay_ref)
    draft: MhrDraft = MhrDraft(id=test_id,
                               draft_number="UT123434",
                               create_ts=model_utils.now_ts(),
                               update_ts=model_utils.now_ts(),
                               account_id=account_id,
                               user_id=username,
                               registration_type=reg_type,
                               mhr_number=mhr_num)
    draft.draft = json_data
    review_reg: MhrReviewRegistration = MhrReviewRegistration.create_from_json(json_data, draft)
    review_reg.id = test_id
    review_reg.save()
    test_regs = MhrReviewRegistration.find_by_mhr_number(mhr_num)
    assert test_regs
    assert len(test_regs) == 1


@pytest.mark.parametrize('pay_ref,account_id,username,draft_json,mhr_num,reg_type,test_id', TEST_DATA)
def test_create_from_json(session, pay_ref, account_id, username, draft_json, mhr_num, reg_type, test_id):
    """Assert that the new MHR review registration is created from json data correctly."""
    json_data = copy.deepcopy(draft_json)
    json_data["payment"] = copy.deepcopy(pay_ref)
    draft: MhrDraft = MhrDraft(id=test_id,
                               draft_number="UT123434",
                               create_ts=model_utils.now_ts(),
                               update_ts=model_utils.now_ts(),
                               account_id=account_id,
                               user_id=username,
                               registration_type=reg_type,
                               mhr_number=mhr_num)
    draft.draft = json_data
    review_reg: MhrReviewRegistration = MhrReviewRegistration.create_from_json(json_data, draft)
    assert review_reg.account_id == account_id
    assert review_reg.draft_id == test_id
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
