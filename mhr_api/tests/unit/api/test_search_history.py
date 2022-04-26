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

"""Tests to verify the search history endpoint.

Test-Suite to ensure that the /search-history endpoint is working as expected.
"""

from http import HTTPStatus

import pytest

from mhr_api.services.authz import COLIN_ROLE, MHR_ROLE, STAFF_ROLE
from tests.unit.services.utils import create_header_account, create_header


# testdata pattern is ({desc}, {roles}, {account_id}, {status})
TEST_SEARCH_DATA = [
    ('Valid', [MHR_ROLE], '1234', HTTPStatus.OK),
    ('Non-staff no account', [MHR_ROLE], None, HTTPStatus.BAD_REQUEST),
    ('Staff no account', [MHR_ROLE, STAFF_ROLE], None, HTTPStatus.BAD_REQUEST),
    ('Unauthorized', [COLIN_ROLE], '1234', HTTPStatus.UNAUTHORIZED)
]


@pytest.mark.parametrize('desc,roles,account_id,status', TEST_SEARCH_DATA)
def test_search_history(session, client, jwt, desc, roles, account_id, status):
    """Assert that valid search criteria returns a 201 status."""
    # setup
    headers = create_header_account(jwt, roles) if account_id else create_header(jwt, roles)

    # test
    rv = client.get('/api/v1/search-history', headers=headers)

    # check
    assert rv.status_code == status



def test_search_history_valid_200(session, client, jwt):
    """Assert that valid search history account with some records returns a 200 status."""
    # no setup

    # test
    rv = client.get('/api/v1/search-history',
                    headers=create_header_account(jwt, [MHR_ROLE], 'test-user', 'PS12345'))
    # check
    assert rv.status_code == HTTPStatus.OK


def test_search_history_missing_account_400(session, client, jwt):
    """Assert that a search history request with no account ID returns a 400 status."""
    # no setup

    # test
    rv = client.get('/api/v1/search-history',
                    headers=create_header(jwt, [MHR_ROLE]))

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_search_history_unauthorized_401(session, client, jwt):
    """Assert that a search history request with a non-ppr role and an account ID returns a 401 status."""
    # no setup

    # test
    rv = client.get('/api/v1/search-history',
                    headers=create_header_account(jwt, [COLIN_ROLE], 'test-user', 'PS12345'))

    # check
    # print(rv.json)
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_search_history_not_no_result(session, client, jwt):
    """Assert that a search history request with an unknown account ID returns a 404 status."""
    # no setup

    # test
    rv = client.get('/api/v1/search-history',
                    headers=create_header_account(jwt, [MHR_ROLE], 'test-user', 'PZZ49X42'))

    # check
    # print(rv.json)
    assert rv.status_code == HTTPStatus.OK
    assert len(rv.json) == 0
