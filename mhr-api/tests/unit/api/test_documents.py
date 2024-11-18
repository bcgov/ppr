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

from mhr_api.services.authz import COLIN_ROLE, MHR_ROLE, STAFF_ROLE
from tests.unit.services.utils import create_header, create_header_account


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
