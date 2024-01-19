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

"""Tests to verify the auth-api integration.

Test-Suite to ensure that the client for the auth-api service is working as expected.
"""
import pytest
from flask import current_app

from mhr_api.services import authz
from tests.unit.services.utils import helper_create_jwt


MOCK_URL_NO_KEY = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
MOCK_URL = 'https://bcregistry-bcregistry-mock.apigee.net/auth/api/v1/'

# testdata pattern is ({description}, {account id}, {valid})
TEST_SBC_DATA = [
    ('Valid account id', '1234', True),
    ('No account id', None, False),
    ('Invalid account id', authz.STAFF_ROLE, False),
    ('Invalid account id', '2518', False)
]
TEST_REG_STAFF_DATA = [
    ('Valid account id', authz.STAFF_ROLE, True),
    ('No account id', None, False),
    ('Invalid account id', authz.GOV_ACCOUNT_ROLE, False),
    ('Invalid account id', '2518', False)
]
TEST_STAFF_DATA = [
    ('Valid account id', authz.STAFF_ROLE, True),
    ('No account id', None, False),
    ('Invalid account id', authz.BCOL_HELP_ROLE, False),
    ('Invalid account id', '2518', False)
]
TEST_BCOL_HELPDESK_DATA = [
    ('Valid account id', authz.BCOL_HELP_ACCOUNT, True),
    ('Invalid REG staff account id', authz.STAFF_ROLE, False),
    ('No account id', None, False),
    ('Invalid account id', '2518', False)
]


@pytest.mark.parametrize('desc,account_id,valid', TEST_SBC_DATA)
def test_sbc_office_account(session, jwt, desc, account_id, valid):
    """Assert that sbc office account check returns the expected result."""
    # setup
    current_app.config.update(AUTH_SVC_URL=MOCK_URL_NO_KEY)
    token = helper_create_jwt(jwt, [authz.GOV_ACCOUNT_ROLE])
    result = authz.is_sbc_office_account(token, account_id)
    # check
    assert result == valid


@pytest.mark.parametrize('desc,account_id,valid', TEST_REG_STAFF_DATA)
def test_reg_staff_account(session, desc, account_id, valid):
    """Assert that registries staff account check returns the expected result."""
    # test
    result = authz.is_reg_staff_account(account_id)
    # check
    assert result == valid


@pytest.mark.parametrize('desc,account_id,valid', TEST_STAFF_DATA)
def test_staff_account(session, desc, account_id, valid):
    """Assert that staff account check returns the expected result."""
    # test
    result = authz.is_staff_account(account_id)
    # check
    assert result == valid


@pytest.mark.parametrize('desc,account_id,valid', TEST_BCOL_HELPDESK_DATA)
def test_bcol_helpdesk_account(session, desc, account_id, valid):
    """Assert that bcol helpdesk account check returns the expected result."""
    # test
    result = authz.is_bcol_help(account_id)
    # check
    assert result == valid
