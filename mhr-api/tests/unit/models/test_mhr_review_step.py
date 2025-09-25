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

from mhr_api.models import MhrDraft, MhrReviewRegistration, MhrReviewStep, utils as model_utils
from mhr_api.models.mhr_review_step import DeclinedReasonTypes
from mhr_api.models.type_tables import MhrRegistrationTypes, MhrReviewStatusTypes


PAYREF = {
     "invoiceId": "88888888",
     "receipt": "receipt",
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
TEST_DRAFT: MhrDraft = MhrDraft(id=191000000,
                                draft_number="UT123434",
                                create_ts=model_utils.now_ts(),
                                update_ts=model_utils.now_ts(),
                                account_id="PS1245",
                                user_id="username",
                                registration_type=MhrRegistrationTypes.TRANS_WILL,
                                mhr_number="000919")
TEST_REVIEW: MhrReviewStep = MhrReviewStep(create_ts = model_utils.now_ts(),
                                           staff_note="staff Note review",
                                           username="first last",
                                           status_type=MhrReviewStatusTypes.IN_REVIEW)

# testdata pattern is ({staff_note}, {client_note}, {change_note}, {username}, {status_type}, {test_id})
TEST_ID_DATA = [
    ("staff note", "client", "change", "first last", MhrReviewStatusTypes.IN_REVIEW, 191000000),
]
# testdata pattern is ({staff_note}, {username}, {status_type}, {reason_type}, {test_review_id})
TEST_DECLINE_DATA = [
    ("staff note", "first last", MhrReviewStatusTypes.DECLINED, DeclinedReasonTypes.OTHER, 191000000),
]


@pytest.mark.parametrize('staff_note,username,status_type,reason_type,test_id', TEST_DECLINE_DATA)
def test_decline(session, staff_note, username, status_type, reason_type, test_id):
    """Assert that find mhr review step by id contains all expected elements."""
    review_reg: MhrReviewRegistration = create_review_reg()
    review_step = copy.deepcopy(TEST_REVIEW)
    review_step.id = test_id
    review_step.review_registration_id = review_reg.id
    review_step.save()
    step_id: int = int(test_id) + 1
    step: MhrReviewStep = MhrReviewStep(id=step_id,
                                        create_ts = model_utils.now_ts(),
                                        staff_note=staff_note,
                                        username=username,
                                        status_type=status_type,
                                        declined_reason_type = reason_type,
                                        review_registration_id=review_reg.id)
    step.save()
    test_step: MhrReviewStep = MhrReviewStep.find_by_id(step_id)
    assert test_step.declined_reason_type
    test_json = test_step.json
    assert test_json.get("declinedReasonType") == DeclinedReasonTypes.OTHER.value


@pytest.mark.parametrize('staff_note,client_note,change_note,username,status_type,test_id', TEST_ID_DATA)
def test_find_by_id(session, staff_note, client_note, change_note, username, status_type, test_id):
    """Assert that find mhr review step by id contains all expected elements."""
    review_reg: MhrReviewRegistration = create_review_reg()
    step: MhrReviewStep = MhrReviewStep(id=test_id,
                                        create_ts = model_utils.now_ts(),
                                        staff_note=staff_note,
                                        client_note=client_note,
                                        change_note=change_note,
                                        username=username,
                                        status_type=status_type,
                                        review_registration_id=review_reg.id)
    step.save()
    test_step: MhrReviewStep = MhrReviewStep.find_by_id(test_id)
    assert test_step
    assert test_step.id == test_id
    assert test_step.staff_note == staff_note
    assert test_step.client_note == client_note
    assert test_step.change_note == change_note
    assert test_step.username == username
    assert test_step.review_registration_id == review_reg.id
    assert test_step.status_type == status_type
    assert test_step.review_registration
    assert test_step.review_registration.id == review_reg.id


@pytest.mark.parametrize('staff_note,client_note,change_note,username,status_type,test_id', TEST_ID_DATA)
def test_find_by_registration_id(session, staff_note, client_note, change_note, username, status_type, test_id):
    """Assert that find mhr review step by registration id contains all expected elements."""
    review_reg: MhrReviewRegistration = create_review_reg()
    step: MhrReviewStep = MhrReviewStep(id=test_id,
                                        create_ts = model_utils.now_ts(),
                                        staff_note=staff_note,
                                        client_note=client_note,
                                        change_note=change_note,
                                        username=username,
                                        status_type=status_type,
                                        review_registration_id=review_reg.id)
    step.save()
    test_steps: MhrReviewStep = MhrReviewStep.find_by_registration_id(review_reg.id)
    assert test_steps
    test_step = test_steps[0]
    assert test_step
    assert test_step.id == test_id
    assert test_step.staff_note == staff_note
    assert test_step.client_note == client_note
    assert test_step.change_note == change_note
    assert test_step.username == username
    assert test_step.review_registration_id == review_reg.id
    assert test_step.status_type == status_type
    assert test_step.review_registration
    assert test_step.review_registration.id == review_reg.id


def create_review_reg() -> MhrReviewRegistration:
    """Create a review registration for testing."""
    draft: MhrDraft = copy.deepcopy(TEST_DRAFT)
    json_data = copy.deepcopy(TEST_TRANSFER)
    json_data["payment"] = copy.deepcopy(PAYREF)
    draft.draft = json_data
    review_reg: MhrReviewRegistration = MhrReviewRegistration.create_from_json(json_data, draft)
    review_reg.save()
    return review_reg
