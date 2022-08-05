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

"""Tests to verify the endpoints for maintaining MH registrations.

Test-Suite to ensure that the /registrations endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app

from mhr_api.services.authz import COLIN_ROLE, MHR_ROLE, STAFF_ROLE

from tests.unit.services.utils import create_header, create_header_account


# testdata pattern is ({desc}, {roles}, {status}, {has_account}, {results_size})
TEST_GET_ACCOUNT_DATA = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, False, 0),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 0),
    ('Valid request', [MHR_ROLE], HTTPStatus.OK, True, 1),
    ('Invalid request staff no account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, 0)
]


@pytest.mark.parametrize('desc,roles,status,has_account,results_size', TEST_GET_ACCOUNT_DATA)
def test_get_account_registrations(session, client, jwt, desc, roles, status, has_account, results_size):
    """Assert that a get account registrations summary list endpoint works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    # test
    rv = client.get('/api/v1/registrations',
                    headers=headers)

    # check
    # print(rv.json)
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        assert rv.json
        assert len(rv.json) >= results_size
        for registration in rv.json:
            assert registration['mhrNumber']
            assert registration['registrationDescription']
            assert registration['statusType'] is not None
            assert registration['createDateTime'] is not None
            assert registration['username'] is not None
            assert registration['submittingParty'] is not None
            assert registration['clientReferenceId'] is not None
            assert registration['ownerNames'] is not None
            assert registration['path'] is not None
            assert registration['inUserList'] is not None
