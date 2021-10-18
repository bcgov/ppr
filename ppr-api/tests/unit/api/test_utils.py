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
import pytest
from flask import current_app

from ppr_api.resources.utils import get_account_name
from ppr_api.services.authz import PPR_ROLE
from tests.unit.services.utils import helper_create_jwt


MOCK_URL_NO_KEY = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
# testdata pattern is ({description}, {account id}, {has name})
TEST_USER_ORGS_DATA_JSON = [
    ('Valid no account', None, True),
    ('Valid account', '2617', True),
    ('No token', '2617', False),
]


@pytest.mark.parametrize('desc, account_id, has_name', TEST_USER_ORGS_DATA_JSON)
def test_get_account_name(session, client, jwt, desc, account_id, has_name):
    """Assert that a get user profile returns the expected response code and data."""
    # setup
    current_app.config.update(AUTH_SVC_URL=MOCK_URL_NO_KEY)
    token = helper_create_jwt(jwt, [PPR_ROLE]) if has_name else None

    # test
    name = get_account_name(token, account_id)

    # check
    if has_name:
        assert name
    else:
        assert not name
