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

"""Tests to verify the party-codes endpoint.

Test-Suite to ensure that the /party-codes endpoint is working as expected.
"""
from http import HTTPStatus

import pytest

from ppr_api.services.authz import STAFF_ROLE, PPR_ROLE, COLIN_ROLE
from tests.unit.services.utils import create_header_account, create_header


TEST_UPDATE_JSON = {
    'paymentConfirmationDialog': True,
    'selectConfirmationDialog': False
}
TEST_INVALID_JSON = {
}
# testdata pattern is ({description}, {is staff}, {include account}, {response status}, {role})
TEST_DATA = [
    ('Valid', False, True, HTTPStatus.OK, PPR_ROLE),
    ('Missing account ID', False, False, HTTPStatus.BAD_REQUEST, PPR_ROLE),
    ('Staff missing account ID', True, False, HTTPStatus.OK, PPR_ROLE),
    ('Valid data but unauthorized', False, True, HTTPStatus.UNAUTHORIZED, COLIN_ROLE)
]
# testdata pattern is ({description}, {is staff}, {include account}, {response status}, {role}, {data})
TEST_DATA_UPDATE = [
    ('Valid', False, True, HTTPStatus.OK, PPR_ROLE, TEST_UPDATE_JSON),
    ('Missing account ID', False, False, HTTPStatus.BAD_REQUEST, PPR_ROLE, TEST_UPDATE_JSON),
    ('Staff missing account ID', True, False, HTTPStatus.OK, PPR_ROLE, TEST_UPDATE_JSON),
    ('Valid data but unauthorized', False, True, HTTPStatus.UNAUTHORIZED, COLIN_ROLE, TEST_UPDATE_JSON),
    ('Schema validation error', False, True, HTTPStatus.BAD_REQUEST, PPR_ROLE, TEST_INVALID_JSON)
]


@pytest.mark.parametrize('desc,staff,include_account,status,role', TEST_DATA)
def test_get_user_profile(session, client, jwt, desc, staff, include_account, status, role):
    """Assert that a get user profile returns the expected response code and data."""
    # setup
    headers = None
    if include_account:
        if staff:
            headers = create_header_account(jwt, [role, STAFF_ROLE])
        else:
            headers = create_header_account(jwt, [role])
    else:
        if staff:
            headers = create_header(jwt, [role, STAFF_ROLE])
        else:
            headers = create_header(jwt, [role])

    # test
    rv = client.get('/api/v1/user-profile', headers=headers)
    # check
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        response_data = rv.json
        assert response_data
        assert 'paymentConfirmationDialog' in response_data
        assert 'selectConfirmationDialog' in response_data
        assert 'defaultDropDowns' in response_data
        assert 'defaultTableFilters' in response_data


@pytest.mark.parametrize('desc,staff,include_account,status,role,data', TEST_DATA_UPDATE)
def test_update_user_profile(session, client, jwt, desc, staff, include_account, status, role, data):
    """Assert that updating a user profile returns the expected response code and data."""
    # setup
    headers = None
    if include_account:
        if staff:
            headers = create_header_account(jwt, [role, STAFF_ROLE])
        else:
            headers = create_header_account(jwt, [role])
    else:
        if staff:
            headers = create_header(jwt, [role, STAFF_ROLE])
        else:
            headers = create_header(jwt, [role])
    # create profile
    client.get('/api/v1/user-profile', headers=headers)

    # test
    rv = client.patch('/api/v1/user-profile',
                      json=data,
                      headers=headers,
                      content_type='application/json')
    # check
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        response_data = rv.json
        assert response_data
        assert 'paymentConfirmationDialog' in response_data
        assert 'selectConfirmationDialog' in response_data
        assert 'defaultDropDowns' in response_data
        assert 'defaultTableFilters' in response_data
