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

import copy
from http import HTTPStatus

import pytest
from flask import current_app

from mhr_api.models import SearchRequest
from mhr_api.models.utils import format_ts, now_ts_offset
from mhr_api.services.authz import COLIN_ROLE, MHR_ROLE, STAFF_ROLE
from tests.unit.services.utils import create_header, create_header_account


# Valid test search criteria
MHR_NUMBER_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'value': '022911'
    },
    'clientReferenceId': 'T-SQ-MH-1'
}
ORG_NAME_JSON = {
    'type': 'ORGANIZATION_NAME',
    'criteria': {
        'value': 'GUTHRIE HOLDINGS LTD.'
    },
    'clientReferenceId': 'T-SQ-MO-1'
}
OWNER_NAME_JSON = {
    'type': 'OWNER_NAME',
    'criteria': {
        'ownerName': {
            'first': 'David',
            'last': 'Hamm'
        }
    },
    'clientReferenceId': 'T-SQ-MI-1'
}
SERIAL_NUMBER_JSON = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'value': '4551'
    },
    'clientReferenceId': 'T-SQ-MS-1'
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

# testdata pattern is ({search_type}, {json_data})
TEST_SEARCH_TYPE_DATA = [
    ('MM', MHR_NUMBER_JSON),
    ('MB', ORG_NAME_JSON),
    ('MI', OWNER_NAME_JSON),
    ('MS', SERIAL_NUMBER_JSON)
]

# testdata pattern is ({desc}, {type}, {value}, {roles}, {account_id}, {status})
TEST_SEARCH_DATA = [
    ('Invalid search type', 'MHX_NUMBER', '022911', [MHR_ROLE], '1234', HTTPStatus.BAD_REQUEST),
    ('Non-staff no account', 'MHR_NUMBER', '022911', [MHR_ROLE], None, HTTPStatus.BAD_REQUEST),
    ('Staff no account', 'MHR_NUMBER', '022911', [MHR_ROLE, STAFF_ROLE], None, HTTPStatus.BAD_REQUEST),
    ('Valid no results', 'MHR_NUMBER', '999999', [MHR_ROLE], '1234', HTTPStatus.CREATED),
    ('Unauthorized', 'MHR_NUMBER', '022911', [COLIN_ROLE], '1234', HTTPStatus.UNAUTHORIZED)
]

# testdata pattern is ({desc}, {json_data}, {search_id}, {roles}, {account_id}, {status})
TEST_SELECTED_DATA = [
    ('Invalid missing MHR number', SELECTED_JSON_INVALID, 200000004, [MHR_ROLE], '1234', HTTPStatus.BAD_REQUEST),
    ('Non-staff no account', SELECTED_JSON, 200000004, [MHR_ROLE], None, HTTPStatus.BAD_REQUEST),
    ('Staff no account', SELECTED_JSON, 200000004, [MHR_ROLE, STAFF_ROLE], None, HTTPStatus.BAD_REQUEST),
    ('Valid no selection', SELECTED_JSON_NONE, 200000004, [MHR_ROLE], '1234', HTTPStatus.ACCEPTED),
    ('Invalid search id', SELECTED_JSON, 300000004, [MHR_ROLE], '1234', HTTPStatus.NOT_FOUND),
    ('Unauthorized', SELECTED_JSON, 200000004, [COLIN_ROLE], '1234', HTTPStatus.UNAUTHORIZED)
]


@pytest.mark.parametrize('search_type,json_data', TEST_SEARCH_TYPE_DATA)
def test_search_valid(session, client, jwt, search_type, json_data):
    """Assert that valid search criteria returns a 201 status."""
    rv = client.post('/api/v1/searches',
                     json=json_data,
                     headers=create_header_account(jwt, [MHR_ROLE]),
                     content_type='application/json')
    # check
    current_app.logger.debug(rv.json)
    assert rv.status_code == HTTPStatus.CREATED


@pytest.mark.parametrize('desc,type,value,roles,account_id,status', TEST_SEARCH_DATA)
def test_search(session, client, jwt, desc, type, value, roles, account_id, status):
    """Assert that valid search criteria returns a 201 status."""
    # setup
    json_data = copy.deepcopy(MHR_NUMBER_JSON)
    json_data['type'] = type
    json_data['criteria']['value'] = value
    headers = create_header_account(jwt, roles) if account_id else create_header(jwt, roles)

    rv = client.post('/api/v1/searches',
                     json=json_data,
                     headers=headers,
                     content_type='application/json')
    # check
    assert rv.status_code == status


@pytest.mark.parametrize('desc,json_data,search_id,roles,account_id,status', TEST_SELECTED_DATA)
def test_put_selected(session, client, jwt, desc, json_data, search_id, roles, account_id, status):
    """Assert that valid search criteria returns a 201 status."""
    # setup
    headers = create_header_account(jwt, roles) if account_id else create_header(jwt, roles)

    rv = client.put('/api/v1/searches/' + str(search_id),
                    json=json_data,
                    headers=headers,
                    content_type='application/json')
    # check
    assert rv.status_code == status
