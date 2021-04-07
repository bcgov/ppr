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

from ppr_api.services.authz import STAFF_ROLE, PPR_ROLE, COLIN_ROLE
from tests.unit.services.utils import create_header_account, create_header


def test_party_non_existent_404(session, client, jwt):
    """Assert that a party code for a non-existent party returns a 404 error."""
    # no setup

    # test
    rv = client.get('/api/v1/party-codes/12345',
                    headers=create_header_account(jwt, [PPR_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_party_valid_200(session, client, jwt):
    """Assert that a valid party code for returns a clientParty schema object."""
    # no setup

    # test
    rv = client.get('/api/v1/party-codes/200000000',
                    headers=create_header_account(jwt, [PPR_ROLE]))

    # check
    print(rv.json)
    assert rv.status_code == HTTPStatus.OK
    assert 'contact' in rv.json
    assert 'address' in rv.json
    assert 'businessName' in rv.json


def test_party_nonstaff_missing_account_400(session, client, jwt):
    """Assert that a get client party request with a non-staff jwt and no account ID returns a 400 status."""
    # setup

    # test
    rv = client.get('/api/v1/party-codes/200000000',
                    headers=create_header(jwt, [COLIN_ROLE]))

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_party_staff_missing_account_200(session, client, jwt):
    """Assert that a get client party request with a staff jwt and no account ID returns a 200 status."""
    # setup

    # test
    rv = client.get('/api/v1/party-codes/200000000',
                    headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]))

    # check
    assert rv.status_code == HTTPStatus.OK


def test_party_nonstaff_unauthorized_404(session, client, jwt):
    """Assert that a get client party request with a non-ppr role and account ID returns a 404 status."""
    # setup

    # test
    rv = client.get('/api/v1/party-codes/5000009',
                    headers=create_header_account(jwt, [COLIN_ROLE]))

    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED
