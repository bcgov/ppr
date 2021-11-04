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
import copy

import pytest
from flask import current_app

from ppr_api.resources.utils import get_account_name, validate_financing, validate_registration
from ppr_api.services.authz import PPR_ROLE
from tests.unit.services.utils import helper_create_jwt
from tests.unit.utils.test_financing_validator import FINANCING
from tests.unit.utils.test_registration_validator import AMENDMENT_VALID


MOCK_URL_NO_KEY = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
# testdata pattern is ({description}, {account id}, {has name})
TEST_USER_ORGS_DATA_JSON = [
    ('Valid no account', None, True),
    ('Valid account', '2617', True),
    ('No token', '2617', False),
]
# testdata pattern is ({description}, {valid data})
TEST_VALIDATE_REGISTRATION_DATA = [
    ('Valid amendment', True),
    ('Invalid amendment', False)
]
# testdata pattern is ({description}, {valid data})
TEST_VALIDATE_FINANCING_DATA = [
    ('Valid financing statement registration', True),
    ('Invalid financing statement registration', False)
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


@pytest.mark.parametrize('desc, valid', TEST_VALIDATE_FINANCING_DATA)
def test_validate_financing(session, client, jwt, desc, valid):
    """Assert that validate a financing statement registration works as expected."""
    # setup
    json_data = copy.deepcopy(FINANCING)
    if not valid:
        del json_data['authorizationReceived']

    # test
    error_msg = validate_financing(json_data)
    if valid:
        assert error_msg == ''
    else:
        assert error_msg != ''


@pytest.mark.parametrize('desc, valid', TEST_VALIDATE_REGISTRATION_DATA)
def test_validate_registration(session, client, jwt, desc, valid):
    """Assert that validate a registration works as expected."""
    # setup
    json_data = copy.deepcopy(AMENDMENT_VALID)
    if not valid:
        del json_data['authorizationReceived']

    # test
    error_msg = validate_registration(json_data)
    if valid:
        assert error_msg == ''
    else:
        assert error_msg != ''
