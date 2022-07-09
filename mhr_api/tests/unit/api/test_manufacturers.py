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

"""Tests to verify the manufacturers endpoints.

Test-Suite to ensure that the /manufacturers/* endpoints are working as expected.
"""

from http import HTTPStatus

import pytest

from mhr_api.services.authz import COLIN_ROLE, MHR_ROLE, STAFF_ROLE
from tests.unit.services.utils import create_header_account, create_header


# testdata pattern is ({desc}, {roles}, {account_id}, {status}, {size})
TEST_ACCOUNT_PARTIES_DATA = [
    ('Valid', [MHR_ROLE], '2523', HTTPStatus.OK, 1),
    ('Valid no results', [MHR_ROLE], '1234', HTTPStatus.OK, 0),
    ('Non-staff no account', [MHR_ROLE], None, HTTPStatus.BAD_REQUEST, 0),
    ('Staff no account', [MHR_ROLE, STAFF_ROLE], None, HTTPStatus.BAD_REQUEST, 0),
    ('Unauthorized', [COLIN_ROLE], '1234', HTTPStatus.UNAUTHORIZED, 0)
]


@pytest.mark.parametrize('desc,roles,account_id,status,size', TEST_ACCOUNT_PARTIES_DATA)
def test_manufacturer_parties(session, client, jwt, desc, roles, account_id, status, size):
    """Assert that the manufacturer parties endpoint behaves as expected."""
    # setup
    headers = create_header_account(jwt, roles, 'test-user', account_id) if account_id else create_header(jwt, roles)

    # test
    rv = client.get('/api/v1/manufacturers/parties', headers=headers)

    # check
    assert rv.status_code == status
    if status == HTTPStatus.OK:
        results = rv.json
        assert len(results) == size
        if size > 0:
            for result in results:
                assert result.get('bcolAccountNumber') is not None
                assert result.get('dealerName') is not None
                assert result['submittingParty']
                assert result['submittingParty']['businessName']
                assert result['submittingParty']['phoneNumber']
                assert result['submittingParty']['address']
                assert result['submittingParty']['address']['street']
                assert result['submittingParty']['address']['city']
                assert result['submittingParty']['address']['region']
                assert result['submittingParty']['address']['country']
                assert result['submittingParty']['address']['postalCode']
                assert result['owner']
                assert result['owner']['businessName']
                assert result['owner']['phoneNumber']
                assert result['owner']['address']
                assert result['owner']['address']['street']
                assert result['owner']['address']['city']
                assert result['owner']['address']['region']
                assert result['owner']['address']['country']
                assert result['owner']['address']['postalCode']
                assert result.get('manufacturerName') is not None
