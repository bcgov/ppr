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

"""Tests to verify the searches endpoint.

Test-Suite to ensure that the /searches endpoint is working as expected.
"""
from http import HTTPStatus

import pytest
from flask import current_app

from mhr_api.services.authz import COLIN_ROLE, MHR_ROLE, STAFF_ROLE
from tests.unit.services.utils import create_header, create_header_account, create_header_account_report


MHR_NUMBER_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'value': '022911'
    },
    'clientReferenceId': 'T-SQ-MH-1'
}
SELECTED_JSON_NONE = []
SELECTED_JSON = [
    {'baseInformation': {
        'make': 'GLENDALE', 'model': '', 'year': 1968
    },
    'createDateTime': '1995-11-14T00:00:01+00:00',
    'homeLocation': 'FORT NELSON',
    'mhrNumber': '022911',
    'ownerName': {
        'first': 'PRITNAM',
        'last': 'SANDHU'
    },
    'serialNumber': '2427',
    'status': 'EXEMPT'}
]
SELECTED_JSON_INVALID = [
    {'baseInformation': {
        'make': 'GLENDALE', 'model': '', 'year': 1968
    },
    'createDateTime': '1995-11-14T00:00:01+00:00',
    'homeLocation': 'FORT NELSON',
    'ownerName': {
        'first': 'PRITNAM',
        'last': 'SANDHU'
    },
    'serialNumber': '2427',
    'status': 'EXEMPT'}
]


MOCK_AUTH_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
MOCK_PAY_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/pay/api/v1/'
TEST_SEARCH_REPORT_FILE = 'tests/unit/api/test-get-search-report.pdf'

# testdata pattern is ({desc}, {json_data}, {search_id}, {roles}, {account_id}, {status})
TEST_SELECTED_DATA = [
    ('Valid no selection', SELECTED_JSON_NONE, None, [MHR_ROLE], '1234', HTTPStatus.OK),
    ('Valid selection', SELECTED_JSON, None, [MHR_ROLE], '1234', HTTPStatus.OK),
    ('Invalid missing MHR number', SELECTED_JSON_INVALID, 200000004, [MHR_ROLE], '1234', HTTPStatus.BAD_REQUEST),
    ('Non-staff no account', SELECTED_JSON, 200000004, [MHR_ROLE], None, HTTPStatus.BAD_REQUEST),
    ('Staff no account', SELECTED_JSON, 200000004, [MHR_ROLE, STAFF_ROLE], None, HTTPStatus.BAD_REQUEST),
    ('Invalid search id', SELECTED_JSON, 300000004, [MHR_ROLE], '1234', HTTPStatus.NOT_FOUND),
    ('Unauthorized', SELECTED_JSON, 200000004, [COLIN_ROLE], '1234', HTTPStatus.UNAUTHORIZED)
]

# testdata pattern is ({desc}, {roles}, {status}, {has_account}, {search_id}, {is_report})
TEST_GET_DATA = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, False, 200000005, False),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 200000005, False),
    ('Invalid request too old', [MHR_ROLE], HTTPStatus.BAD_REQUEST, True, 200000006, False),
    ('Valid request', [MHR_ROLE], HTTPStatus.OK, True, 200000005, False),
    ('Invalid no search selection', [MHR_ROLE], HTTPStatus.BAD_REQUEST, True, 200000001, False),
    ('Invalid search Id', [MHR_ROLE], HTTPStatus.NOT_FOUND, True, 300000006, False),
    ('Invalid request staff no account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, 200000005, False)
]


@pytest.mark.parametrize('desc,json_data,search_id,roles,account_id,status', TEST_SELECTED_DATA)
def test_post_selected(session, client, jwt, desc, json_data, search_id, roles, account_id, status):
    """Assert that valid search criteria returns a 201 status."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = create_header_account(jwt, roles) if account_id else create_header(jwt, roles)

    if search_id and status != HTTPStatus.OK:
        rv = client.post('/api/v1/search-results/' + str(search_id),
                         json=json_data,
                         headers=headers,
                         content_type='application/json')
        # check
        assert rv.status_code == status
    else:
        rv = client.post('/api/v1/searches',
                        json=MHR_NUMBER_JSON,
                        headers=create_header_account(jwt, [MHR_ROLE]),
                        content_type='application/json')
        test_search_id = rv.json['searchId']
        rv = client.post('/api/v1/search-results/' + test_search_id,
                         json=json_data,
                         headers=headers,
                         content_type='application/json')
        # check
        assert rv.status_code == status


@pytest.mark.parametrize('desc,roles,status,has_account, search_id, is_report', TEST_GET_DATA)
def test_get_search_detail(session, client, jwt, desc, roles, status, has_account, search_id, is_report):
    """Assert that a get search detail info by search id works as expected."""
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    # setup
    if is_report:
        headers = create_header_account_report(jwt, roles)
    elif has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    # test
    rv = client.get('/api/v1/search-results/' + str(search_id),
                    headers=headers)

    # check
    # print(rv.json)
    assert rv.status_code == status
