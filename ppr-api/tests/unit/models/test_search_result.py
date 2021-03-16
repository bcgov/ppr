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

"""Tests to assure the Search Detail Model.

Test-Suite to ensure that the Search Detail Model (search step 2 select search
results) is working as expected.
"""
from http import HTTPStatus

import pytest

from ppr_api.models import SearchResult, SearchClient
from ppr_api.exceptions import BusinessException


def test_search_single(session):
    """Assert that a search detail results on a registration with updates returns the expected result."""
    # setup
    json_data = [{
        'baseRegistrationNumber': 'TEST0001',
        'matchType': 'EXACT',
        'registrationType': 'SA'
    }]

    # test
    search_detail = SearchResult.validate_search_select(json_data, 200000001)
    search_detail.update_selection(json_data)
    result = search_detail.json

    # check
    # print(result)
    assert result['searchDateTime']
    assert result['exactResultsSize'] == 1
    assert result['similarResultsSize'] == 0
    assert result['totalResultsSize'] == 1
    assert result['searchQuery']
    assert result['details']
    assert len(result['details']) == 1
    assert result['details'][0]['financingStatement']
    assert 'changes' in result['details'][0]['financingStatement']
    assert len(result['details'][0]['financingStatement']['changes']) > 0


def test_search_single_financing_only(session):
    """Assert that search details for a financing statement with no registrations returns the expected result."""
    # setup
    json_data = [{
        'baseRegistrationNumber': 'TEST0012',
        'matchType': 'EXACT',
        'registrationType': 'SA'
    }]

    # test
    search_detail = SearchResult.validate_search_select(json_data, 200000002)
    search_detail.update_selection(json_data)
    result = search_detail.json

    # check
    # print(result)
    assert result['details']
    assert len(result['details']) == 1
    assert result['details'][0]['financingStatement']
    assert 'changes' not in result['details'][0]['financingStatement']


def test_search_single_renewal(session):
    """Assert that a search detail results on a renewal statement registration returns the expected result."""
    # setup
    json_data = [{
        'baseRegistrationNumber': 'TEST0002',
        'matchType': 'EXACT',
        'registrationType': 'SA'
    }]

    # test
    search_detail = SearchResult.validate_search_select(json_data, 200000003)
    search_detail.update_selection(json_data)
    result = search_detail.json

    # check
    # print(result)
    assert len(result['details']) == 1
    assert result['details'][0]['financingStatement']
    assert 'changes' in result['details'][0]['financingStatement']
    assert len(result['details'][0]['financingStatement']['changes']) >= 1
    assert result['details'][0]['financingStatement']['changes'][0]['statementType'] == 'RENEWAL_STATEMENT'


def test_search_id_invalid(session, client, jwt):
    """Assert that validation of an invalid search ID throws a BusinessException."""
    # setup
    json_data = [{
        'baseRegistrationNumber': 'TEST0001',
        'matchType': 'EXACT',
        'registrationType': 'SA'
    }]

    # test
    with pytest.raises(BusinessException) as bad_request_err:
        SearchResult.validate_search_select(json_data, 300000000)

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    print(bad_request_err.value.error)


def test_search_id_invalid_used(session, client, jwt):
    """Assert that validation of a search ID that has already been submitted throws a BusinessException."""
    # setup
    json_data = [{
        'baseRegistrationNumber': 'TEST0001',
        'matchType': 'EXACT',
        'registrationType': 'SA'
    }]

    # test
    with pytest.raises(BusinessException) as bad_request_err:
        SearchResult.validate_search_select(json_data, 200000000)

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    print(bad_request_err.value.error)


def test_search_id_date_valid(session, client, jwt):
    """Assert that finding by search ID with a date check on a valid date works as expected."""
    # no setup

    # test
    search_detail = SearchResult.find_by_search_id(200000005, True)

    # check
    assert search_detail


def test_search_id_date_invalid(session, client, jwt):
    """Assert that finding by search ID with a date check on an old date works as expected."""
    # no setup

    # test
    with pytest.raises(BusinessException) as bad_request_err:
        SearchResult.find_by_search_id(200000006, True)

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    print(bad_request_err.value.error)


def test_search_detail_full_create(session, client, jwt):
    """Assert that submitting a new search and selecting the detail results works as expected."""
    # setup
    json_data = {
        'type': 'SERIAL_NUMBER',
        'criteria': {
            'value': 'JU622994'
        },
        'clientReferenceId': 'T-SR-SS-1001'
    }
    search_query = SearchClient.create_from_json(json_data, 'PS12345')

    # test
    search_query.search()
    query_json = search_query.json
    # print(query_json)
    search_detail = SearchResult.create_from_search_query(search_query)
    search_detail.save()

    # check
    assert search_detail.search_id == search_query.search_id
    assert not search_detail.search_select
    assert search_detail.exact_match_count > 0
    assert search_detail.similar_match_count > 0
    exact_count = search_detail.exact_match_count
    similar_count = search_detail.similar_match_count

    # Search step 2: modify search selection and update.
    # setup
    query_results_json = query_json['results']
    select_json = []
    for result in query_results_json:
        if result['matchType'] == 'EXACT':
            select_json.append(result)
        elif result['baseRegistrationNumber'] not in ('TEST0002', 'TEST0003'):
            select_json.append(result)

    # test
    search_detail2 = SearchResult.validate_search_select(select_json, search_detail.search_id)
    search_detail2.update_selection(select_json)

    # check
    # print(search_detail2.search_select)
    assert search_detail2.search_select
    assert exact_count == search_detail2.exact_match_count
    assert similar_count > search_detail2.similar_match_count
    details_json = search_detail2.json
    # print(details_json)
    for detail in details_json['details']:
        assert detail['financingStatement']['baseRegistrationNumber'] not in ('TEST0002', 'TEST0003')
