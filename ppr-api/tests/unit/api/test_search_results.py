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
from registry_schemas.example_data.ppr import SEARCH_SUMMARY

from ppr_api.callback.document_storage.storage_service import GoogleStorageService
from ppr_api.models import SearchResult, SearchRequest
from ppr_api.services.authz import COLIN_ROLE, PPR_ROLE, STAFF_ROLE, BCOL_HELP, SBC_OFFICE
from tests.unit.services.utils import create_header, create_header_account, create_header_account_report


SAMPLE_JSON_SUMMARY = copy.deepcopy(SEARCH_SUMMARY)
MOCK_URL_NO_KEY = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
MOCK_PAY_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/pay/api/v1/'
TEST_SEARCH_REPORT_FILE = 'tests/unit/api/test-get-search-report.pdf'
# testdata pattern is ({desc}, {roles}, {status}, {has_account}, {search_id}, {is_report})
TEST_GET_DATA = [
    ('Missing account', [PPR_ROLE], HTTPStatus.BAD_REQUEST, False, 200000005, False),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 200000005, False),
    ('Invalid request too old', [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 200000006, False),
    ('Valid request', [PPR_ROLE], HTTPStatus.OK, True, 200000005, False),
    ('Invalid search Id', [PPR_ROLE], HTTPStatus.NOT_FOUND, True, 300000006, False),
    ('Invalid request staff no account', [PPR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, 200000005, False),
    ('Report pending request', [PPR_ROLE], HTTPStatus.NOT_FOUND, True, 200000007, True),
    ('Report valid request', [PPR_ROLE], HTTPStatus.OK, True, 200000008, True)
]
# testdata pattern is ({desc}, {status}, {search_id})
TEST_CALLBACK_DATA = [
    ('Invalid id', HTTPStatus.NOT_FOUND, 300000005),
    ('Not async search id', HTTPStatus.BAD_REQUEST, 200000005),
    ('Max retries exceeded', HTTPStatus.INTERNAL_SERVER_ERROR, 200000010),
    ('Report already exists', HTTPStatus.OK, 200000008)
]
# testdata pattern is ({desc}, {status}, {search_id})
TEST_NOTIFICATION_DATA = [
    ('Invalid id', HTTPStatus.NOT_FOUND, 300000005),
    ('Not async search id', HTTPStatus.BAD_REQUEST, 200000005),
    ('Max retries exceeded', HTTPStatus.INTERNAL_SERVER_ERROR, 200000012),
    ('Bad callback url', HTTPStatus.INTERNAL_SERVER_ERROR, 200000011)
]


def test_search_detail_valid_200(session, client, jwt):
    """Assert that a valid search detail request returns a 200 status."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
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
                      headers=create_header_account(jwt, [PPR_ROLE], 'test-user', STAFF_ROLE),
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


def test_search_detail_staff_missing_account_400(session, client, jwt):
    """Assert that a search detail request with a staff jwt and no account ID returns a 400 status."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
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
                      headers=create_header_account(jwt, [PPR_ROLE], 'test-user', STAFF_ROLE),
                      content_type='application/json')
    assert rv1.status_code == HTTPStatus.CREATED

    search_id = rv1.json['searchId']
    json_data = rv1.json['results']

    # test
    rv = client.post('/api/v1/search-results/' + search_id,
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


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
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
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
                      headers=create_header_account(jwt, [PPR_ROLE], 'test-user', STAFF_ROLE),
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


@pytest.mark.parametrize('desc,roles,status,has_account, search_id, is_report', TEST_GET_DATA)
def test_get_search_detail(session, client, jwt, desc, roles, status, has_account, search_id, is_report):
    """Assert that a get search detail info by search id works as expected."""
    current_app.config.update(AUTH_SVC_URL=MOCK_URL_NO_KEY)
    headers = None
    # setup
    if is_report:
        headers = create_header_account_report(jwt, roles)
    elif has_account and BCOL_HELP in roles:
        headers = create_header_account(jwt, roles, 'test-user', BCOL_HELP)
    elif has_account and STAFF_ROLE in roles:
        headers = create_header_account(jwt, roles, 'test-user', STAFF_ROLE)
    elif has_account and SBC_OFFICE in roles:
        headers = create_header_account(jwt, roles, 'test-user', SBC_OFFICE)
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


@pytest.mark.parametrize('desc,status,search_id', TEST_CALLBACK_DATA)
def test_callback_search_report(session, client, jwt, desc, status, search_id):
    """Assert that a callback request returns the expected status."""
    # test
    rv = client.patch('/api/v1/search-results/callback/' + str(search_id),
                      headers=None)
    # check
    assert rv.status_code == status


def test_valid_callback_search_report(session, client, jwt):
    """Assert that a valid callback request returns a 200 status."""
    # setup
    json_data = {
        'type': 'SERIAL_NUMBER',
        'criteria': {
            'value': 'JU622994'
        },
        'clientReferenceId': 'UT-SS-1001'
    }
    search_query = SearchRequest.create_from_json(json_data, 'PS12345')
    search_query.search()
    query_json = search_query.json
    search_detail = SearchResult.create_from_search_query(search_query)
    search_detail.save()
    select_json = query_json['results']
    search_detail.update_selection(select_json, 'UNIT TEST INC.', 'CALLBACK_URL')

    # test
    rv = client.patch('/api/v1/search-results/callback/' + str(search_detail.search_id),
                      headers=None)
    # check
    print(rv.json)
    assert rv.status_code == HTTPStatus.OK
    response = rv.json
    assert response['name']
    assert response['selfLink']
    GoogleStorageService.delete_document(response['name'])


@pytest.mark.parametrize('desc,status,search_id', TEST_NOTIFICATION_DATA)
def test_notification_search_report(session, client, jwt, desc, status, search_id):
    """Assert that a notification message request returns the expected status."""
    # test
    rv = client.post('/api/v1/search-results/notifications/' + str(search_id),
                     headers=None)
    # check
    assert rv.status_code == status
