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
TEST_ACCOUNT_DATA = [
    ('Valid', [MHR_ROLE], '2523', HTTPStatus.OK, 1),
    ('Valid no results', [MHR_ROLE], '1234', HTTPStatus.NOT_FOUND, 0),
    ('Non-staff no account', [MHR_ROLE], None, HTTPStatus.BAD_REQUEST, 0),
    ('Staff no account', [MHR_ROLE, STAFF_ROLE], None, HTTPStatus.BAD_REQUEST, 0),
    ('Unauthorized', [COLIN_ROLE], '1234', HTTPStatus.UNAUTHORIZED, 0)
]


@pytest.mark.parametrize('desc,roles,account_id,status,size', TEST_ACCOUNT_DATA)
def test_account_manufacturer(session, client, jwt, desc, roles, account_id, status, size):
    """Assert that the GET account manufacturer info endpoint behaves as expected."""
    # setup
    headers = create_header_account(jwt, roles, 'test-user', account_id) if account_id else create_header(jwt, roles)

    # test
    rv = client.get('/api/v1/manufacturers', headers=headers)

    # check
    assert rv.status_code == status
    if status == HTTPStatus.OK:
        json_data = rv.json
        assert json_data
        assert json_data.get('submittingParty')
        assert json_data['submittingParty'].get('businessName')
        assert json_data['submittingParty'].get('address')
        assert json_data['submittingParty'].get('phoneNumber')
        assert json_data.get('ownerGroups')
        assert json_data['ownerGroups'][0].get('groupId') == 1
        assert json_data['ownerGroups'][0].get('type') == 'SOLE'
        assert json_data['ownerGroups'][0].get('owners')
        owner = json_data['ownerGroups'][0]['owners'][0]
        assert owner.get('businessName')
        assert owner.get('address')
        assert json_data.get('location')
        assert json_data['location'].get('locationType')
        assert json_data['location'].get('dealerName')
        assert json_data['location'].get('address')
        assert json_data.get('description')
        assert json_data['description'].get('manufacturer')
