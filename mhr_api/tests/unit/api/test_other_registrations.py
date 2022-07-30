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

"""Tests to verify the account extra/other registrations endpoint.

Test-Suite to ensure that the /other-registrations/{mhr_number} endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app

from mhr_api.models import SearchResult, SearchRequest
from mhr_api.resources.v1.search_results import get_payment_details
from mhr_api.services.authz import COLIN_ROLE, MHR_ROLE, STAFF_ROLE, BCOL_HELP, GOV_ACCOUNT_ROLE

from tests.unit.services.utils import create_header, create_header_account, create_header_account_report


# testdata pattern is ({desc}, {roles}, {status}, {has_account}, {mhr_number})
TEST_GET_DATA = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, False, '077741'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, '077741'),
    ('Valid request', [MHR_ROLE], HTTPStatus.OK, True, '077741'),
    ('Invalid MHR number', [MHR_ROLE], HTTPStatus.NOT_FOUND, True, 'TESTXX'),
    ('Invalid request staff no account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, '077741')
]
TEST_POST_DATA = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, False, '077741'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, '077741'),
    ('Valid request', [MHR_ROLE], HTTPStatus.CREATED, True, '077741'),
    ('Duplicate/already added request', [MHR_ROLE], HTTPStatus.CONFLICT, True, '045349'),
    ('Invalid MHR number', [MHR_ROLE], HTTPStatus.NOT_FOUND, True, 'TESTXX'),
    ('Invalid request staff no account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, '077741')
]
TEST_DELETE_DATA = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, False, '045349'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, '045349'),
    ('Valid request', [MHR_ROLE], HTTPStatus.NO_CONTENT, True, '045349'),
    ('Invalid non-existent MHR number', [MHR_ROLE], HTTPStatus.NOT_FOUND, True, 'TESTXX'),
    ('Invalid not added MHR number', [MHR_ROLE], HTTPStatus.NOT_FOUND, True, '077741'),
    ('Invalid request staff no account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, '045349')
]


@pytest.mark.parametrize('desc,roles,status,has_account, mhr_number', TEST_GET_DATA)
def test_get_mhr_summary(session, client, jwt, desc, roles, status, has_account, mhr_number):
    """Assert that a get MH registration summary info by MHR number works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    # test
    rv = client.get('/api/v1/other-registrations/' + mhr_number,
                    headers=headers)

    # check
    # print(rv.json)
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        registration = rv.json
        assert registration['mhrNumber'] == mhr_number
        assert registration['registrationDescription']
        assert registration['statusType'] is not None
        assert registration['createDateTime'] is not None
        assert registration['username'] is not None
        assert registration['submittingParty'] is not None
        assert registration['clientReferenceId'] is not None
        assert registration['ownerNames'] is not None
        assert registration['path'] is not None
        assert registration['inUserList'] is not None


@pytest.mark.parametrize('desc,roles,status,has_account, mhr_number', TEST_POST_DATA)
def test_post_other_account_reg(session, client, jwt, desc, roles, status, has_account, mhr_number):
    """Assert that adding another account's registration to the current account list works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    # test
    rv = client.post('/api/v1/other-registrations/' + mhr_number,
                     headers=headers)

    # check
    # print(rv.json)
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        registration = rv.json
        assert registration['mhrNumber'] == mhr_number
        assert registration['registrationDescription']
        assert registration['statusType'] is not None
        assert registration['createDateTime'] is not None
        assert registration['username'] is not None
        assert registration['submittingParty'] is not None
        assert registration['clientReferenceId'] is not None
        assert registration['ownerNames'] is not None
        assert registration['path'] is not None
        assert not registration['inUserList']


@pytest.mark.parametrize('desc,roles,status,has_account, mhr_number', TEST_DELETE_DATA)
def test_delete_other_account_reg(session, client, jwt, desc, roles, status, has_account, mhr_number):
    """Assert that removing another account's registration to the current account list works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    # test
    rv = client.delete('/api/v1/other-registrations/' + mhr_number,
                     headers=headers)

    # check
    # print(rv.json)
    assert rv.status_code == status
