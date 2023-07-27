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
import copy
from http import HTTPStatus

import pytest
from flask import current_app

from mhr_api.models import MhrManufacturer
from mhr_api.services.authz import COLIN_ROLE, MHR_ROLE, STAFF_ROLE
from tests.unit.services.utils import create_header_account, create_header
from tests.unit.utils.test_registration_data import MANUFACTURER_VALID


# testdata pattern is ({desc}, {roles}, {account_id}, {status}, {size})
TEST_ACCOUNT_DATA = [
    ('Valid', [MHR_ROLE], '2523', HTTPStatus.OK, 1),
    ('Valid no results', [MHR_ROLE], '1234', HTTPStatus.NOT_FOUND, 0),
    ('Non-staff no account', [MHR_ROLE], None, HTTPStatus.BAD_REQUEST, 0),
    ('Staff no account', [MHR_ROLE, STAFF_ROLE], None, HTTPStatus.BAD_REQUEST, 0),
    ('Unauthorized', [COLIN_ROLE], '1234', HTTPStatus.UNAUTHORIZED, 0)
]
# testdata pattern is ({desc}, {roles}, {account_id}, {status}, {has_submitting})
TEST_CREATE_DATA = [
    ('Valid', [MHR_ROLE], 'TEST', HTTPStatus.OK, True),
    ('Invalid exists', [MHR_ROLE], '2523', HTTPStatus.BAD_REQUEST, True),
    ('Invalid validation error', [MHR_ROLE], 'TEST', HTTPStatus.BAD_REQUEST, False)
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
        assert owner.get('organizationName')
        assert owner.get('address')
        assert json_data.get('location')
        assert json_data['location'].get('locationType')
        assert json_data['location'].get('dealerName')
        assert json_data['location'].get('address')
        assert json_data.get('description')
        assert json_data['description'].get('manufacturer')


@pytest.mark.parametrize('desc,roles,account,status,has_submitting', TEST_CREATE_DATA)
def test_create(session, client, jwt, desc, roles, account, status, has_submitting):
    """Assert that a post MH information works as expected."""
    # setup
    headers = None
    json_data = copy.deepcopy(MANUFACTURER_VALID)
    if not has_submitting:
        del json_data['submittingParty']
    if account:
        headers = create_header_account(jwt, roles, 'UT-TEST', account)
    else:
        headers = create_header(jwt, roles)
    # test
    response = client.post('/api/v1/manufacturers',
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    current_app.logger.debug(response.json)
    assert response.status_code == status
    if response.status_code == HTTPStatus.CREATED:
        manufacturer: MhrManufacturer = MhrManufacturer.find_by_account_id(account)
        assert manufacturer
