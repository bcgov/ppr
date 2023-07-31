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

"""Tests to verify the qualified supplier endpoints.

Test-Suite to ensure that the /qualified-suppliers/* endpoints are working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app

from mhr_api.models import MhrQualifiedSupplier
from mhr_api.services.authz import COLIN_ROLE, MHR_ROLE, STAFF_ROLE
from tests.unit.services.utils import create_header_account, create_header
from tests.unit.utils.test_registration_data import MANUFACTURER_VALID

INVALID_BUS_NAME = 'TEST \U0001d5c4\U0001d5c6/\U0001d5c1 INVALID'
VALID_BUS_NAME = 'TEST NOTARY PUBLIC'
SUPPLIER_JSON = {
    'businessName': 'TEST NOTARY PUBLIC',
    'address': {
        'street': '1704 GOVERNMENT ST.',
        'city': 'PENTICTON',
        'region': 'BC',
        'postalCode': 'V2A 7A1',
        'country': 'CA'
    },
    'emailAddress': 'test@gmail.com',
    'phoneNumber': '2507701067'
}
# testdata pattern is ({desc}, {roles}, {account_id}, {status})
TEST_ACCOUNT_DATA = [
    ('Valid', [MHR_ROLE], 'test', HTTPStatus.OK),
    ('Valid no results', [MHR_ROLE], '1234', HTTPStatus.NOT_FOUND),
    ('Non-staff no account', [MHR_ROLE], None, HTTPStatus.BAD_REQUEST),
    ('Staff no account', [MHR_ROLE, STAFF_ROLE], None, HTTPStatus.BAD_REQUEST),
    ('Unauthorized', [COLIN_ROLE], 'test', HTTPStatus.UNAUTHORIZED)
]
# testdata pattern is ({desc}, {roles}, {account_id}, {status}, {bus_name})
TEST_CREATE_DATA = [
    ('Valid', [MHR_ROLE], 'new-test', HTTPStatus.OK, VALID_BUS_NAME),
    ('Invalid exists', [MHR_ROLE], 'test', HTTPStatus.BAD_REQUEST, VALID_BUS_NAME),
    ('Invalid validation error', [MHR_ROLE], 'new-test', HTTPStatus.BAD_REQUEST, INVALID_BUS_NAME)
]


@pytest.mark.parametrize('desc,roles,account_id,status', TEST_ACCOUNT_DATA)
def test_get_account_supplier(session, client, jwt, desc, roles, account_id, status):
    """Assert that the GET account qualified supplier info endpoint behaves as expected."""
    # setup
    headers = create_header_account(jwt, roles, 'test-user', account_id) if account_id else create_header(jwt, roles)

    # test
    response = client.get('/api/v1/qualified-suppliers', headers=headers)

    # check
    assert response.status_code == status
    if status == HTTPStatus.OK:
        json_data = response.json
        assert json_data
        assert json_data.get('businessName')
        assert json_data.get('partyType')
        assert json_data.get('address')
        assert json_data.get('phoneNumber')


@pytest.mark.parametrize('desc,roles,account,status,bus_name', TEST_CREATE_DATA)
def test_create_account_supplier(session, client, jwt, desc, roles, account, status, bus_name):
    """Assert that a post MH qualified supplier information works as expected."""
    # setup
    headers = None
    json_data = copy.deepcopy(SUPPLIER_JSON)
    json_data['businessName'] = bus_name
    if account:
        headers = create_header_account(jwt, roles, 'UT-TEST', account)
    else:
        headers = create_header(jwt, roles)
    # test
    response = client.post('/api/v1/qualified-suppliers',
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    current_app.logger.debug(response.json)
    assert response.status_code == status
    if response.status_code == HTTPStatus.CREATED:
        json_data = response.json
        assert json_data
        assert json_data.get('businessName')
        assert json_data.get('partyType')
        assert json_data.get('address')
        assert json_data.get('phoneNumber')
        supplier: MhrQualifiedSupplier = MhrQualifiedSupplier.find_by_account_id(account)
        assert supplier
