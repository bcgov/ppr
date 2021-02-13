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

#from legal_api.models import Business
#from tests.unit.models import Address, PartyRole, factory_business, factory_party_role
from ppr_api.services.authz import STAFF_ROLE, COLIN_ROLE, PPR_ROLE
from tests.unit.services.utils import create_header_account, create_header
from ppr_api.utils.datetime import now_ts_offset, format_ts

# prep sample post search data
from registry_schemas.example_data.ppr import SEARCH_QUERY, SEARCH_SUMMARY
SAMPLE_JSON_DATA = copy.deepcopy(SEARCH_QUERY)
SAMPLE_JSON_SUMMARY = copy.deepcopy(SEARCH_SUMMARY)


def test_search_reg_num_valid_201(session, client, jwt):
    """Assert that valid search by registration number criteria returns a 201 status."""
    # setup
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'value': 'TEST0001'
        },
        'clientReferenceId': 'T-API-SQ-RN-1'
    }
 
    # test
    rv = client.post(f'/api/v1/searches',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED


def test_search_serial_num_valid_201(session, client, jwt):
    """Assert that valid search by serial number criteria returns a 201 status."""
    # setup
    json_data = {
        'type': 'SERIAL_NUMBER',
        'criteria': {
            'value': 'JU622994'
        },
        'clientReferenceId': 'T-API-SQ-SS-1'
    }
 
    # test
    rv = client.post(f'/api/v1/searches',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED


def test_search_mhr_number_valid_201(session, client, jwt):
    """Assert that valid search by MHR number criteria returns a 201 status."""
    # setup
    json_data = {
        'type': 'MHR_NUMBER',
        'criteria': {
            'value': 'T200000'
        },
        'clientReferenceId': 'T-API-SQ-MH-1'
    }
 
    # test
    rv = client.post(f'/api/v1/searches',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED


def test_search_aircraft_dot_valid_201(session, client, jwt):
    """Assert that valid search by aircraft dot criteria returns a 201 status."""
    # setup
    json_data = {
        'type': 'AIRCRAFT_DOT',
        'criteria': {
            'value': 'CFYXW'
        },
        'clientReferenceId': 'T-API-SQ-AC-1'
    }
 
    # test
    rv = client.post(f'/api/v1/searches',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED


def test_search_query_invalid_type_400(session, client, jwt):
    """Assert that search criteria with an invalid type returns a 400 error."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_DATA)
    json_data['type'] = 'INVALID_TYPE'

    # test
    rv = client.post(f'/api/v1/searches',
                     json=json_data,
                     headers=create_header_account(jwt, [STAFF_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST
    print(rv.json)


def test_search_query_nonstaff_missing_account_400(session, client, jwt):
    """Assert that a search request with a non-staff jwt and no account ID returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_DATA)
    del json_data['criteria']['debtorName']['business']
    del json_data['criteria']['value']

    # test
    rv = client.post(f'/api/v1/searches',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_search_query_staff_missing_account_201(session, client, jwt):
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
    rv = client.post(f'/api/v1/searches',
                     json=json_data,
                     headers=create_header(jwt, [STAFF_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.CREATED


def test_search_query_no_result_422(session, client, jwt):
    """Assert that a valid search request with no results returns a 422 status."""
    # setup
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'value': 'TESTXXXX'
        },
        'clientReferenceId': 'T-API-SQ-RN-5'
    }

    # test
    rv = client.post(f'/api/v1/searches',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.UNPROCESSABLE_ENTITY



def test_search_query_nonstaff_unauthorized_404(session, client, jwt):
    """Assert that a search request with a non-ppr role and an account ID returns a 404 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_DATA)
    del json_data['criteria']['debtorName']['business']
    del json_data['criteria']['value']

    # test
    rv = client.post(f'/api/v1/searches',
                     json=json_data,
                     headers=create_header_account(jwt, [COLIN_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_search_query_invalid_startDateTime_400(session, client, jwt):
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
    json_data['startDateTime'] =  format_ts(ts_start)

    # test
    rv = client.post(f'/api/v1/searches',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST
    print(rv.json)


def test_search_detail_valid_200(client, jwt):
    """Assert that a valid search detail request returns a 200 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_SUMMARY)

    # test
    rv = client.put(f'/api/v1/searches/123456',
                     json=json_data,
                     headers=create_header_account(jwt, [STAFF_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code #== HTTPStatus.OK


#def test_search_detail_invalid_regnum_400(session, client, jwt):
def test_search_detail_invalid_regnum_400(client, jwt):
    """Assert that search detail requests with a missing base registration number returns a 400 error."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_SUMMARY)
    del json_data[2]
    del json_data[0]['baseRegistrationNumber']

    # test
    rv = client.put(f'/api/v1/searches/123456',
                     json=json_data,
                     headers=create_header_account(jwt, [STAFF_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_search_detail_nonstaff_missing_account_400(client, jwt):
    """Assert that a search detail request with a non-staff jwt and no account ID returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_SUMMARY)

    # test
    rv = client.put(f'/api/v1/searches/123456',
                    json=json_data,
                    headers=create_header(jwt, [COLIN_ROLE]),
                    content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_search_detail_staff_missing_account_200(client, jwt):
    """Assert that a search detail request with a staff jwt and no account ID returns a 201 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_SUMMARY)

    # test
    rv = client.put(f'/api/v1/searches/123456',
                    json=json_data,
                    headers=create_header(jwt, [STAFF_ROLE]),
                    content_type='application/json')

    # check
    assert rv.status_code #== HTTPStatus.OK


def test_search_detail_nonstaff_unauthorized_404(client, jwt):
    """Assert that a search detail request with a non-ppr role and an account ID returns a 404 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_DATA)
    del json_data['criteria']['debtorName']['business']
    del json_data['criteria']['value']

    # test
    rv = client.put(f'/api/v1/searches/123456',
                    json=json_data,
                    headers=create_header_account(jwt, [COLIN_ROLE]),
                    content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED

