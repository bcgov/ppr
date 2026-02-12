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

"""Tests to verify the endpoints for maintaining MH documents.

Test-Suite to ensure that the /documents endpoint is working as expected.
"""
import copy
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
import requests

from mhr_api.models import MhrDraft, MhrReviewRegistration, MhrReviewStep
from mhr_api.models import utils as model_utils
from mhr_api.models.mhr_review_step import DeclinedReasonTypes
from mhr_api.models.type_tables import MhrRegistrationTypes, MhrReviewStatusTypes
from mhr_api.resources.v1.review_registrations import upload_rejection_report, validate_review, validate_status_type
from mhr_api.services.authz import COLIN_ROLE, MHR_ROLE, QUALIFIED_USER_GROUP, STAFF_ROLE
from mhr_api.services.payment.client import SBCPaymentClient
from mhr_api.utils.logging import logger
from tests.unit.services.utils import create_header, create_header_account

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
PAYLOAD_IN_REVIEW = { "statusType": "IN_REVIEW" }
PAYLOAD_APPROVED = { "statusType": "APPROVED" }
TEST_REVIEW: MhrReviewStep = MhrReviewStep(create_ts = model_utils.now_ts(),
                                           staff_note="staff Note review",
                                           username="first last",
                                           status_type=MhrReviewStatusTypes.IN_REVIEW)


# testdata pattern is ({desc}, {roles}, {status}, {has_account}, {test_id})
TEST_DATA_GET_ALL = [
    ('Missing account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, 191000000),
    ('Not staff', [MHR_ROLE, QUALIFIED_USER_GROUP], HTTPStatus.UNAUTHORIZED, True, 191000000),
    ('Invalid role', [COLIN_ROLE, STAFF_ROLE], HTTPStatus.UNAUTHORIZED, True, 191000000),
    ('Valid', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, True, 191000000),
]
# testdata pattern is ({desc}, {roles}, {status}, {has_account}, {test_id})
TEST_DATA_GET_REVIEW = [
    ('Missing account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, 191000000),
    ('Not staff', [MHR_ROLE, QUALIFIED_USER_GROUP], HTTPStatus.UNAUTHORIZED, True, 191000000),
    ('Invalid role', [COLIN_ROLE, STAFF_ROLE], HTTPStatus.UNAUTHORIZED, True, 191000000),
    ('Not found', [MHR_ROLE, STAFF_ROLE], HTTPStatus.NOT_FOUND, True, 191000001),
    ('Valid', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, True, 191000000),
]
# testdata pattern is ({desc}, {roles}, {status}, {has_account}, {test_id}, {payload})
TEST_DATA_PATCH_REVIEW = [
    ('Missing account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, 191000000, PAYLOAD_IN_REVIEW),
    ('Not staff', [MHR_ROLE, QUALIFIED_USER_GROUP], HTTPStatus.UNAUTHORIZED, True, 191000000, PAYLOAD_IN_REVIEW),
    ('Invalid role', [COLIN_ROLE, STAFF_ROLE], HTTPStatus.UNAUTHORIZED, True, 191000000, PAYLOAD_IN_REVIEW),
    ('Not found', [MHR_ROLE, STAFF_ROLE], HTTPStatus.NOT_FOUND, True, 191000001, PAYLOAD_IN_REVIEW),
    ('Invalid no payload', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, True, 191000000, {}),
    ('Valid', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, True, 191000000, PAYLOAD_IN_REVIEW),
    ('Invalid status', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, True, 191000000, PAYLOAD_APPROVED),
]
# testdata pattern is ({desc}, {current}, {new}}, {valid})
TEST_DATA_STATUS_TYPE = [
    ('Valid NEW IN_REVIEW', MhrReviewStatusTypes.NEW, MhrReviewStatusTypes.IN_REVIEW.value, True),
    ('Valid IN_REVIEW NEW', MhrReviewStatusTypes.IN_REVIEW, MhrReviewStatusTypes.NEW.value, True),
    ('Valid IN_REVIEW APPROVED', MhrReviewStatusTypes.IN_REVIEW, MhrReviewStatusTypes.APPROVED.value, True),
    ('Valid IN_REVIEW DECLINED', MhrReviewStatusTypes.IN_REVIEW, MhrReviewStatusTypes.DECLINED.value, True),
    ('Valid APPROVED APPROVED', MhrReviewStatusTypes.APPROVED, MhrReviewStatusTypes.APPROVED.value, True),
    ('Valid DECLINED DECLINED', MhrReviewStatusTypes.DECLINED, MhrReviewStatusTypes.DECLINED.value, True),
    ('Invalid PAY_PENDING NEW', MhrReviewStatusTypes.PAY_PENDING, MhrReviewStatusTypes.NEW.value, False),
    ('Invalid PAY_CANCELLED NEW', MhrReviewStatusTypes.PAY_CANCELLED, MhrReviewStatusTypes.NEW.value, False),
    ('Invalid APPROVED NEW', MhrReviewStatusTypes.APPROVED, MhrReviewStatusTypes.NEW.value, False),
    ('Invalid DECLINED NEW', MhrReviewStatusTypes.DECLINED, MhrReviewStatusTypes.NEW.value, False),
    ('Invalid NEW APPROVED', MhrReviewStatusTypes.NEW, MhrReviewStatusTypes.APPROVED.value, False),
    ('Invalid NEW DECLINED', MhrReviewStatusTypes.NEW, MhrReviewStatusTypes.DECLINED.value, False),
]
# testdata pattern is ({desc}, {username}, {status}}, {reject_reason}, {staff_note} {valid})
TEST_DATA_IN_REVIEW = [
    ('Valid approved', "first last", MhrReviewStatusTypes.APPROVED.value, None, None, True),
    ('Valid declined', "first last", MhrReviewStatusTypes.DECLINED.value, DeclinedReasonTypes.INCOMPLETE.value, None, True),
    ('Invalid user', "joe staff", MhrReviewStatusTypes.APPROVED.value, None, None, False),
    ('Declined no reason', "first last", MhrReviewStatusTypes.DECLINED.value, None, None, False),
    ('Declined invalid reason', "first last", MhrReviewStatusTypes.DECLINED.value, "JUNK", None, False),
    ('Declined other no note', "first last", MhrReviewStatusTypes.DECLINED.value, DeclinedReasonTypes.OTHER.value, None, False),
    ('Valid declined other note', "first last", MhrReviewStatusTypes.DECLINED.value, DeclinedReasonTypes.OTHER.value, "note", True),
]
# testdata pattern is ({desc}, {test_id}, {report_data}, {document_id}, {filing_date})
TEST_DATA_REJECTION_REPORT = [
    ('Valid', 191000000, b'test-report-data', '0100000000', '1970-01-01'),
    ('Invalid no report data', 191000000, None, '0100000000', '1970-01-01'),
    ('Invalid no document id', 191000000, b'test-report-data', None, '1970-01-01'),
    ('Invalid no filing date', 191000000, b'test-report-data', '0100000000', None)
]


@pytest.mark.parametrize('desc,username,status,reason,note,valid', TEST_DATA_IN_REVIEW)
def test_in_review(session, client, jwt, desc, username, status, reason, note, valid):
    """Assert that validation of IN_REVIEW requests works as expected."""
    review_reg = create_review_reg_in_review(191000000)
    assert review_reg
    test_json = {
        "statusType": status
    }
    if reason:
        test_json["declinedReasonType"] = reason
    if note:
        test_json["staffNote"] = note
    error_msg: str = validate_review(test_json, review_reg, username)
    if valid:
        assert error_msg == ""
    else:
        assert error_msg != ""


@pytest.mark.parametrize('desc,current,new_status,valid', TEST_DATA_STATUS_TYPE)
def test_status_type(session, client, jwt, desc, current, new_status, valid):
    """Assert that status type transition validation works as expected."""
    test_json = copy.deepcopy(PAYLOAD_IN_REVIEW)
    test_json["statusType"] = new_status
    review_reg: MhrReviewRegistration = MhrReviewRegistration(status_type=current)
    error_msg = validate_status_type(test_json, review_reg)
    if valid:
        assert error_msg == ""
    else:
        assert error_msg != ""


@pytest.mark.parametrize('desc,roles,status,has_account,test_id', TEST_DATA_GET_ALL)
def test_get_all_reviews(session, client, jwt, desc, roles, status, has_account, test_id):
    """Assert that a get staff reviews works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    # test
    review_reg: MhrReviewRegistration = None
    if status == HTTPStatus.OK:
        review_reg = create_review_reg(test_id)
    rv = client.get('/api/v1/reviews', headers=headers)

    # check
    assert rv.status_code == status
    if status == HTTPStatus.OK:
        resp_json = rv.json
        assert resp_json
        for review in resp_json:
            assert review.get("statusType")
            assert review.get("createDateTime")


@pytest.mark.parametrize('desc,roles,status,has_account,test_id', TEST_DATA_GET_REVIEW)
def test_get_review(session, client, jwt, desc, roles, status, has_account, test_id):
    """Assert that a get staff review by review ID works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    # test
    review_reg: MhrReviewRegistration = None
    if status == HTTPStatus.OK:
        review_reg = create_review_reg(test_id)
    path = f"/api/v1/reviews/{test_id}"
    rv = client.get(path, headers=headers)

    # check
    assert rv.status_code == status
    if status == HTTPStatus.OK:
        resp_json = rv.json
        assert resp_json
        assert resp_json.get("registrationType")
        assert resp_json.get("payment")


@pytest.mark.parametrize('desc,roles,status,has_account,test_id,payload', TEST_DATA_PATCH_REVIEW)
def test_patch_review(session, client, jwt, desc, roles, status, has_account, test_id, payload):
    """Assert that a staff review update by review ID works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    # test
    review_reg: MhrReviewRegistration = None
    if status == HTTPStatus.OK or desc in ("Invalid no payload", "Invalid status"):
        review_reg = create_review_reg(test_id)
    path = f"/api/v1/reviews/{test_id}"
    rv = client.patch(path, json=payload, headers=headers, content_type='application/json')

    # check
    assert rv.status_code == status
    if status == HTTPStatus.OK:
        resp_json = rv.json
        assert resp_json
        assert resp_json.get("registrationType")
        assert resp_json.get("payment")


@pytest.mark.parametrize('desc,test_id,report_data, document_id, filing_date', TEST_DATA_REJECTION_REPORT)
def test_upload_rejection_report(session, client, jwt, desc, test_id, report_data, document_id, filing_date):
    """Assert that upload rejection report works as expected."""
    review_reg = create_review_reg(test_id)
    with patch.object(SBCPaymentClient, "get_sa_token", return_value="mock-token"):
        with patch.object(requests, "post") as post_mock:
            res_mock = MagicMock()
            res_mock.status_code = HTTPStatus.CREATED
            res_mock.json_return_value = {"documentURL": "mock-document-url"}
            post_mock.return_value = res_mock
            result = upload_rejection_report(report_data, document_id, filing_date, review_reg.id)

    if desc.startswith('Invalid'):
        assert result is None
        return

    assert result
    post_mock.assert_called_once()
    _, kwargs = post_mock.call_args

    assert kwargs["headers"]["Authorization"] == "Bearer mock-token"
    assert kwargs["data"] == report_data
    assert kwargs["params"] == {
        "consumerDocumentId": document_id,
        "consumerFilingDate": filing_date,
    }


def create_review_reg(test_id: int) -> MhrReviewRegistration:
    """Create a review registration for testing."""
    draft: MhrDraft = copy.deepcopy(TEST_DRAFT)
    draft.id = test_id
    json_data = copy.deepcopy(TEST_TRANSFER)
    json_data["payment"] = copy.deepcopy(PAYREF)
    json_data["payment"]["invoiceId"] = str(test_id)
    draft.draft = json_data
    review_reg: MhrReviewRegistration = MhrReviewRegistration.create_from_json(json_data, draft)
    review_reg.id = test_id
    review_reg.save()
    return review_reg


def create_review_reg_in_review(test_id: int) -> MhrReviewRegistration:
    """Create a review registration for testing."""
    draft: MhrDraft = copy.deepcopy(TEST_DRAFT)
    draft.id = test_id
    json_data = copy.deepcopy(TEST_TRANSFER)
    json_data["payment"] = copy.deepcopy(PAYREF)
    json_data["payment"]["invoiceId"] = str(test_id)
    draft.draft = json_data
    review_reg: MhrReviewRegistration = MhrReviewRegistration.create_from_json(json_data, draft)
    review_reg.id = test_id
    review_reg.assignee_name = "first last"
    review_reg.status_type = MhrReviewStatusTypes.IN_REVIEW
    review_reg.save()
    review_step = copy.deepcopy(TEST_REVIEW)
    review_step.id = test_id
    review_step.review_registration_id = review_reg.id
    review_step.save()
    new_reg = MhrReviewRegistration.find_by_id(review_reg.id)
    return new_reg
