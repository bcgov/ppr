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

# prep sample post search data
from registry_schemas.example_data.ppr import SEARCH_SUMMARY

from ppr_api.services.authz import STAFF_ROLE, COLIN_ROLE, PPR_ROLE
from tests.unit.services.utils import create_header_account, create_header


SAMPLE_JSON_SUMMARY = copy.deepcopy(SEARCH_SUMMARY)


def test_search_detail_valid_200(session, client, jwt):
    """Assert that a valid search detail request returns a 200 status."""
    # setup
    json_data = {
        'type': 'BUSINESS_DEBTOR',
        'criteria': {
            'debtorName': {
                'business': 'TEST BUS 2 DEBTOR'
            }
        },
        'clientReferenceId': 'T-API-SQ-DB-2'
    }

    # test
    rv1 = client.post('/api/v1/searches',
                      json=json_data,
                      headers=create_header_account(jwt, [PPR_ROLE]),
                      content_type='application/json')
    search_id = rv1.json['searchId']
    json_data = []
    count_exact = 0
    for result in rv1.json['results']:
        if result['matchType'] == 'SIMILAR':
            result['selected'] = False
        else:
            count_exact += 1
        json_data.append(result)

    # print(json_data)
    # test
    rv = client.post('/api/v1/search-results/' + search_id,
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    # print(rv.json)
    assert rv.status_code == HTTPStatus.OK
    results = rv.json
    assert 'searchDateTime' in results
    assert 'exactResultsSize' in results
    assert 'similarResultsSize' in results
    assert 'searchQuery' in results
    assert 'details' in results
    assert len(results['details']) == count_exact


def test_search_detail_invalid_regnum_400(session, client, jwt):
    """Assert that search detail requests with a missing base registration number returns a 400 error."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_SUMMARY)
    del json_data[2]
    del json_data[0]['baseRegistrationNumber']

    # test
    rv = client.post('/api/v1/search-results/12346',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_search_detail_nonstaff_missing_account_400(session, client, jwt):
    """Assert that a search detail request with a non-staff jwt and no account ID returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_SUMMARY)

    # test
    rv = client.post('/api/v1/search-results/123456',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_search_detail_staff_missing_account_200(session, client, jwt):
    """Assert that a search detail request with a staff jwt and no account ID returns a 201 status."""
    # setup
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'value': 'TEST0001'
        },
        'clientReferenceId': 'T-API-SD-RN-1'
    }

    # test
    rv1 = client.post('/api/v1/searches',
                      json=json_data,
                      headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                      content_type='application/json')
    assert rv1.status_code == HTTPStatus.CREATED

    search_id = rv1.json['searchId']
    json_data = rv1.json['results']

    # test
    rv = client.post('/api/v1/search-results/' + search_id,
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.OK


def test_search_detail_nonstaff_unauthorized_401(session, client, jwt):
    """Assert that a search detail request with a non-ppr role and an account ID returns a 401 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_SUMMARY)

    # test
    rv = client.post('/api/v1/search-results/123456',
                     json=json_data,
                     headers=create_header_account(jwt, [COLIN_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_search_detail_no_duplicates_200(session, client, jwt):
    """Assert that a selection with 2 matches on the same registration returns the expected result."""
    # setup
    json_data = {
        'type': 'BUSINESS_DEBTOR',
        'criteria': {
            'debtorName': {
                'business': 'DUPLICATE NAME'
            }
        },
        'clientReferenceId': 'T-API-SQ-DB-3'
    }

    # test
    rv1 = client.post('/api/v1/searches',
                      json=json_data,
                      headers=create_header_account(jwt, [PPR_ROLE]),
                      content_type='application/json')
    search_id = rv1.json['searchId']
    json_data = []
    json_data.append(rv1.json['results'][0])
    json_data.append(rv1.json['results'][1])
    # print(json_data)
    # test
    rv = client.post('/api/v1/search-results/' + search_id,
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')

    # check
    # print(rv.json)
    assert rv.status_code == HTTPStatus.OK
    results = rv.json
    assert 'searchDateTime' in results
    assert 'exactResultsSize' in results
    assert 'similarResultsSize' in results
    assert 'searchQuery' in results
    assert 'details' in results
    assert len(results['details']) == 1


def test_get_search_detail_200(session, client, jwt):
    """Assert that a valid get search details request returns the expected result."""
    # no setup

    # test
    rv = client.get('/api/v1/search-results/200000005',
                    headers=create_header_account(jwt, [PPR_ROLE]))

    # check
    print(rv.json)
    assert rv.status_code == HTTPStatus.OK


def test_get_search_detail_too_old_400(session, client, jwt):
    """Assert that a get search details request on an old search returns a 400 status."""
    # no setup

    # test
    rv = client.get('/api/v1/search-results/200000006',
                    headers=create_header_account(jwt, [PPR_ROLE]))

    # check
    # print(rv.json)
    assert rv.status_code == HTTPStatus.BAD_REQUEST
