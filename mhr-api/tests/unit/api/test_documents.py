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
from http import HTTPStatus

import pytest
from flask import current_app

from mhr_api.models import MhrRegistration
from mhr_api.services.authz import MHR_ROLE, STAFF_ROLE, COLIN_ROLE, REQUEST_EXEMPTION_RES, \
                                   TRANSFER_DEATH_JT, TRANSFER_SALE_BENEFICIARY, REQUEST_TRANSPORT_PERMIT, \
                                   REGISTER_MH
from tests.unit.services.utils import create_header, create_header_account


MOCK_PAY_URL = "https://test.api.connect.gov.bc.ca/mockTarget/pay/api/v1/"
PAY_RECEIPT_URL = "/api/v1/documents/receipts/{reg_id}"
MANUFACTURER_ROLES = [MHR_ROLE, TRANSFER_SALE_BENEFICIARY, REQUEST_TRANSPORT_PERMIT, REGISTER_MH]
QUALIFIED_USER = [MHR_ROLE, REQUEST_EXEMPTION_RES, TRANSFER_DEATH_JT, TRANSFER_SALE_BENEFICIARY]
# testdata pattern is ({desc}, {roles}, {status}, {has_account}, {doc_id}, {exists}, {valid})
TEST_VERIFY_ID_DATA = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, False, '40583993', True, True),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, '40583993', True, True),
    ('Valid request not exists no checksum', [MHR_ROLE], HTTPStatus.OK, True, '80888999', False, True),
    ('Valid request not exists checksum', [MHR_ROLE], HTTPStatus.OK, True, '79289202', False, True),
    ('Invalid request staff no account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, '40583993', True, True),
    # ('Valid request exists', [MHR_ROLE], HTTPStatus.OK, True, '40583993', True, True)
]
# testdata pattern is ({desc}, {roles}, {status}, {has_account}, {doc_id})
TEST_DATA_GET = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, False, '40583993'),
    ('Missing account staff', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, '40583993'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, '40583993'),
    ('Not exists no checksum legacy', [MHR_ROLE], HTTPStatus.NOT_FOUND, True, 'REG88999'),
    ('Not exists no checksum MAN', [MHR_ROLE], HTTPStatus.NOT_FOUND, True, '80888999'),
    ('Not exists no checksum QS', [MHR_ROLE], HTTPStatus.NOT_FOUND, True, '10888999'),
    ('Not exists no checksum GA', [MHR_ROLE], HTTPStatus.NOT_FOUND, True, '90888999'),
    ('Not exists checksum', [MHR_ROLE], HTTPStatus.NOT_FOUND, True, '79289202'),
    ('Not exists no checksum staff', [MHR_ROLE, STAFF_ROLE], HTTPStatus.NOT_FOUND, True, '1001000000'),
    ('Invalid checksum', [MHR_ROLE], HTTPStatus.BAD_REQUEST, True, '79289200')
]
# testdata pattern is ({desc}, {roles}, {status}, {has_account}, {start_digit})
TEST_DATA_QS_DOC_ID_DATA = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, False, None),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, None),
    ('Valid request QS lawyyer/notary', QUALIFIED_USER, HTTPStatus.OK, True, '1'),
    ('Valid request QS manufacturer', MANUFACTURER_ROLES, HTTPStatus.OK, True, '8'),
]
# testdata pattern is ({desc}, {roles}, {status}, {account_id}, {staff_reg_id})
TEST_DATA_GET_RECEIPT = [
    ("Missing account", [MHR_ROLE], HTTPStatus.BAD_REQUEST, None, 200000006),
    ("Missing account staff", [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, None, 200000006),
    ("Not staff", [MHR_ROLE], HTTPStatus.UNAUTHORIZED, "PS12345", 200000006),
    ("Invalid Role", [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, "PS12345", 200000006),
    ("Not found", [MHR_ROLE, STAFF_ROLE], HTTPStatus.NOT_FOUND, "ppr_staff", 10000000),
    ("Valid staff", [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, "ppr_staff", 200000006),
]


@pytest.mark.parametrize('desc,roles,status,has_account,doc_id,exists,valid', TEST_VERIFY_ID_DATA)
def test_get_doc_id_verify(session, client, jwt, desc, roles, status, has_account, doc_id, exists, valid):
    """Assert that a get document id status endpoint works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    # test
    rv = client.get('/api/v1/documents/verify/' + doc_id,
                    headers=headers)

    # check
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        response = rv.json
        current_app.logger.debug(response)
        assert response
        assert response['documentId'] == doc_id
        assert response['exists'] == exists
        assert response['valid'] == valid


@pytest.mark.parametrize('desc,roles,status,has_account,doc_id', TEST_DATA_GET)
def test_get_document(session, client, jwt, desc, roles, status, has_account, doc_id):
    """Assert that a get document endpoint by document id works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    # test
    rv = client.get('/api/v1/documents/' + doc_id,
                    headers=headers)

    # check
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        response = rv.json
        current_app.logger.debug(response)
        assert response
        assert response['documentId'] == doc_id


@pytest.mark.parametrize('desc,roles,status,has_account,start_digit', TEST_DATA_QS_DOC_ID_DATA)
def test_get_qs_doc_id(session, client, jwt, desc, roles, status, has_account, start_digit):
    """Assert that the get QS document id endpoint works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    # test
    rv = client.get('/api/v1/documents/qs-document-ids',headers=headers)

    # check
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        response = rv.json
        assert response
        assert str(response.get("documentId")).startswith(start_digit)


@pytest.mark.parametrize('desc,roles,status,account_id,staff_reg_id', TEST_DATA_GET_RECEIPT)
def test_get_receipt_report(session, client, jwt, desc, roles, status, account_id, staff_reg_id):
    """Assert that a get account registrations summary list response with staff receipts works as expected."""
   # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    if account_id is not None:
        headers = create_header_account(jwt, roles, 'test-user', account_id)
        if account_id == "ppr_staff":
            headers["Staff-Account-Id"] = "1234"
    else:
        headers = create_header(jwt, roles)

    if STAFF_ROLE in roles and staff_reg_id > 0 and status == HTTPStatus.OK:
        reg: MhrRegistration = MhrRegistration.find_by_id(staff_reg_id)
        reg.account_id = "ppr_staff"
        reg.pay_invoice_id = staff_reg_id
        reg.save()
    url = PAY_RECEIPT_URL.format(reg_id=staff_reg_id)
    # test
    rv = client.get(url, headers=headers)

    # check
    assert rv.status_code == status
