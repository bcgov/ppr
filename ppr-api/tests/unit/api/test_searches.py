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
# prep sample post search data
from registry_schemas.example_data.ppr import SEARCH_QUERY

from ppr_api.models import SearchRequest
from ppr_api.models.utils import format_ts, now_ts_offset
from ppr_api.resources.searches import get_payment_details
from ppr_api.services.authz import BCOL_HELP, COLIN_ROLE, PPR_ROLE, SBC_OFFICE, STAFF_ROLE
from tests.unit.services.utils import create_header, create_header_account


MOCK_PAY_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/pay/api/v1/'

SAMPLE_JSON_DATA = copy.deepcopy(SEARCH_QUERY)
# Valid test search criteria
AIRCRAFT_DOT_JSON = {
    'type': 'AIRCRAFT_DOT',
    'criteria': {
        'value': 'CFYXW'
    },
    'clientReferenceId': 'T-SQ-AC-1'
}
MHR_NUMBER_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'value': '220000'
    },
    'clientReferenceId': 'T-SQ-MH-1'
}
REGISTRATION_NUMBER_JSON = {
    'type': 'REGISTRATION_NUMBER',
    'criteria': {
        'value': 'TEST0001'
    },
    'clientReferenceId': 'T-SQ-RG-3'
}
SERIAL_NUMBER_JSON = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'value': 'JU622994'
    },
    'clientReferenceId': 'T-SQ-SS-1'
}
INDIVIDUAL_DEBTOR_JSON = {
    'type': 'INDIVIDUAL_DEBTOR',
    'criteria': {
        'debtorName': {
            'last': 'Debtor',
            'first': 'Test Ind'
        }
    },
    'clientReferenceId': 'T-SQ-IS-1'
}
BUSINESS_DEBTOR_JSON = {
    'type': 'BUSINESS_DEBTOR',
    'criteria': {
        'debtorName': {
            'business': 'TEST BUS 2 DEBTOR'
        }
    },
    'clientReferenceId': 'T-SQ-DB-1'
}

# testdata pattern is ({search type}, {JSON data})
TEST_VALID_DATA = [
    ('AC', AIRCRAFT_DOT_JSON),
    ('RG', REGISTRATION_NUMBER_JSON),
    ('MH', MHR_NUMBER_JSON),
    ('SS', SERIAL_NUMBER_JSON),
    ('IS', INDIVIDUAL_DEBTOR_JSON),
    ('BS', BUSINESS_DEBTOR_JSON)
]
# testdata pattern is ({role}, {routingSlip}, {bcolNumber}, {datNUmber}, {certified}, {status})
TEST_STAFF_SEARCH_DATA = [
    (STAFF_ROLE, None, None, None, False, HTTPStatus.CREATED),
    (STAFF_ROLE, '12345', None, None, False, HTTPStatus.CREATED),
    (STAFF_ROLE, '12345', None, None, True, HTTPStatus.CREATED),
    (STAFF_ROLE, None, '654321', '111111', False, HTTPStatus.CREATED),
    (STAFF_ROLE, None, None, None, True, HTTPStatus.CREATED),
    (STAFF_ROLE, '12345', '654321', '111111', False, HTTPStatus.BAD_REQUEST),
    (BCOL_HELP, None, None, None, False, HTTPStatus.CREATED),
    (SBC_OFFICE, '12345', None, None, False, HTTPStatus.CREATED),
    (SBC_OFFICE, '12345', None, None, True, HTTPStatus.CREATED),
    (SBC_OFFICE, None, '654321', '111111', False, HTTPStatus.CREATED),
    (SBC_OFFICE, None, None, None, False, HTTPStatus.BAD_REQUEST)
]


@pytest.mark.parametrize('search_type,json_data', TEST_VALID_DATA)
def test_search_valid(session, client, jwt, search_type, json_data):
    """Assert that valid search criteria returns a 201 status."""
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    rv = client.post('/api/v1/searches',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED
    assert 'certified' not in rv.json['searchQuery']


@pytest.mark.parametrize('search_type,json_data', TEST_VALID_DATA)
def test_staff_search_certified(session, client, jwt, search_type, json_data):
    """Assert that valid staff certified search criteria returns a 201 status."""
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    rv = client.post('/api/v1/searches?certified=true',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE], 'test-user', STAFF_ROLE),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED
    assert rv.json['searchQuery']['certified']


# testdata pattern is ({role}, {routing_slip}, {bcol_number}, {datNUmber}, {certified}, {status})
@pytest.mark.parametrize('role,routing_slip,bcol_number,dat_number,certified,status', TEST_STAFF_SEARCH_DATA)
def test_staff_search(session, client, jwt, role, routing_slip, bcol_number, dat_number, certified, status):
    """Assert that staff search requests returns the correct status."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    params = ''
    if certified:
        params = '?certified=true'
    if routing_slip:
        if len(params) > 0:
            params += '&routingSlipNumber=' + str(routing_slip)
        else:
            params = '?routingSlipNumber=' + str(routing_slip)
    if bcol_number:
        if len(params) > 0:
            params += '&bcolAccountNumber=' + str(bcol_number)
        else:
            params = '?bcolAccountNumber=' + str(bcol_number)
    if dat_number:
        if len(params) > 0:
            params += '&datNumber=' + str(dat_number)
    print('params=' + params)
    rv = client.post('/api/v1/searches' + params,
                     json=REGISTRATION_NUMBER_JSON,
                     headers=create_header_account(jwt, [PPR_ROLE], 'test-user', role),
                     content_type='application/json')
    # check
    assert rv.status_code == status


def test_search_query_invalid_type_400(session, client, jwt):
    """Assert that search criteria with an invalid type returns a 400 error."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_DATA)
    json_data['type'] = 'INVALID_TYPE'

    # test
    rv = client.post('/api/v1/searches',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST
    # print(rv.json)


def test_search_query_nonstaff_missing_account_400(session, client, jwt):
    """Assert that a search request with a non-staff jwt and no account ID returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_DATA)
    del json_data['criteria']['debtorName']['business']
    del json_data['criteria']['value']

    # test
    rv = client.post('/api/v1/searches',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_search_query_staff_missing_account_400(session, client, jwt):
    """Assert that a search request with a staff jwt and no account ID returns a 201 status."""
    # setup
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'value': 'TEST0001'
        },
        'clientReferenceId': 'T-API-SQ-RN-1'
    }

    # test
    rv = client.post('/api/v1/searches',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_search_query_no_result_200(session, client, jwt):
    """Assert that a valid search request with no results returns a 201 status."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'value': 'TESTXXXX'
        },
        'clientReferenceId': 'T-API-SQ-RN-5'
    }

    # test
    rv = client.post('/api/v1/searches',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.CREATED
    assert 'results' not in rv.json


def test_search_query_nonstaff_unauthorized_404(session, client, jwt):
    """Assert that a search request with a non-ppr role and an account ID returns a 404 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_DATA)
    del json_data['criteria']['debtorName']['business']
    del json_data['criteria']['value']

    # test
    rv = client.post('/api/v1/searches',
                     json=json_data,
                     headers=create_header_account(jwt, [COLIN_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_search_query_invalid_start_datetime_400(session, client, jwt):
    """Assert that a valid search request with an invalid startDateTime returns a 400 status."""
    # setup
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'value': 'TEST0001'
        },
        'clientReferenceId': 'T-API-SQ-RN-6',
        'endDateTime': '2021-01-20T19:38:43+00:00'
    }
    ts_start = now_ts_offset(1, True)
    json_data['startDateTime'] = format_ts(ts_start)

    # test
    rv = client.post('/api/v1/searches',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST
    # print(rv.json)


def test_search_selection_update_valid(session, client, jwt):
    """Assert that a valid search selection update returns a 200 status."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    json_data = [
        {
            'baseRegistrationNumber': 'TEST0001',
            'matchType': 'EXACT',
            'createDateTime': '2021-03-02T22:46:43+00:00',
            'registrationType': 'SA',
            'debtor': {
                'businessName': 'TEST BUS 2 DEBTOR',
                'partyId': 200000002
            }
        },
        {
            'baseRegistrationNumber': 'TEST0002',
            'matchType': 'EXACT',
            'createDateTime': '2021-03-02T22:46:43+00:00',
            'registrationType': 'RL',
            'debtor': {
                'businessName': 'TEST BUS 2 DEBTOR',
                'partyId': 200000006
            }
        },
        {
            'baseRegistrationNumber': 'TEST0003',
            'matchType': 'SIMILAR',
            'createDateTime': '2021-03-02T22:46:43+00:00',
            'registrationType': 'RL',
            'selected': True,
            'debtor': {
                'businessName': 'TEST BUS 3 DEBTOR',
                'partyId': 200000009
            }
        }
    ]
    if json_data[2]['selected']:
        json_data[2]['selected'] = False
    else:
        json_data[2]['selected'] = True
    # test
    rv = client.put('/api/v1/searches/200000004',
                    json=json_data,
                    headers=create_header_account(jwt, [PPR_ROLE]),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.ACCEPTED
    assert rv.json[2]['selected'] == json_data[2]['selected']


def test_search_selection_update_invalid_400(session, client, jwt):
    """Assert that an invalid search selection update returns a 400 status."""
    # setup missing required matchType
    json_data = [
        {
            'baseRegistrationNumber': 'TEST0001',
            'createDateTime': '2021-03-02T22:46:43+00:00',
            'registrationType': 'SA',
            'debtor': {
                'businessName': 'TEST BUS 2 DEBTOR',
                'partyId': 200000002
            }
        }
    ]

    # test
    rv = client.put('/api/v1/searches/200000004',
                    json=json_data,
                    headers=create_header_account(jwt, [PPR_ROLE], 'test-user', STAFF_ROLE),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_search_selection_update_unauthorized_404(session, client, jwt):
    """Assert that a valid search selection update with an invalid role returns a 404 status."""
    # setup
    json_data = [
        {
            'baseRegistrationNumber': 'TEST0001',
            'matchType': 'EXACT',
            'createDateTime': '2021-03-02T22:46:43+00:00',
            'registrationType': 'SA',
            'debtor': {
                'businessName': 'TEST BUS 2 DEBTOR',
                'partyId': 200000002
            }
        }
    ]

    # test
    rv = client.put('/api/v1/searches/200000004',
                    json=json_data,
                    headers=create_header_account(jwt, [COLIN_ROLE], 'test-user', COLIN_ROLE),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_search_selection_update_nonstaff_no_account_400(session, client, jwt):
    """Assert that a valid search selection update with non-staff role, no account ID returns a 400 status."""
    # setup
    json_data = [
        {
            'baseRegistrationNumber': 'TEST0001',
            'matchType': 'EXACT',
            'createDateTime': '2021-03-02T22:46:43+00:00',
            'registrationType': 'SA',
            'debtor': {
                'businessName': 'TEST BUS 2 DEBTOR',
                'partyId': 200000002
            }
        }
    ]

    # test
    rv = client.put('/api/v1/searches/200000004',
                    json=json_data,
                    headers=create_header(jwt, [PPR_ROLE]),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_get_payment_details(session, client, jwt):
    """Assert that a valid search request payment details setup works as expected."""
    # setup
    json_data = copy.deepcopy(SERIAL_NUMBER_JSON)
    query = SearchRequest.create_from_json(json_data)
    # test
    details = get_payment_details(query, json_data['type'])

    # check
    assert details
    assert details['label'] == 'Serial/VIN Number:'
    assert details['value'] == 'JU622994'
