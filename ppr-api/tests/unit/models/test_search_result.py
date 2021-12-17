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

from ppr_api.models import SearchResult, SearchRequest
from ppr_api.exceptions import BusinessException


# Valid test data
SINGLE_JSON = [{
    'baseRegistrationNumber': 'TEST0001',
    'matchType': 'EXACT',
    'registrationType': 'SA'
}]

SINGLE_NO_HISTORY_JSON = [{
    'baseRegistrationNumber': 'TEST0012',
    'matchType': 'EXACT',
    'registrationType': 'SA'
}]

SINGLE_RENEWAL_JSON = [{
    'baseRegistrationNumber': 'TEST0002',
    'matchType': 'EXACT',
    'registrationType': 'SA'
}]
SET_SELECT = [
    {'baseRegistrationNumber': 'TEST0004', 'matchType': 'EXACT', 'createDateTime': '2021-12-16T01:18:38+00:00',
     'registrationType': 'SA',
     'vehicleCollateral': {'type': 'MV', 'serialNumber': 'JU622994', 'year': 2018, 'make': 'HONDA',
                           'model': 'CIVIC'}},
    {'baseRegistrationNumber': 'TEST0001', 'matchType': 'EXACT', 'createDateTime': '2021-12-16T01:18:38+00:00',
     'registrationType': 'SA',
     'vehicleCollateral': {'type': 'MV', 'serialNumber': 'JU622994', 'year': 2014, 'make': 'BMW', 'model': 'Z4'}},
    {'baseRegistrationNumber': '107169B', 'matchType': 'SIMILAR', 'createDateTime': '2021-12-03T00:31:40+00:00',
     'registrationType': 'SA',
     'vehicleCollateral': {'type': 'MV', 'serialNumber': 'KM8J3CA46JU622994', 'year': 2018, 'make': 'HYUNDAI',
                           'model': 'TUCSON'}},
    {'baseRegistrationNumber': 'TEST0001', 'matchType': 'SIMILAR', 'createDateTime': '2021-12-16T01:18:38+00:00',
     'registrationType': 'SA',
     'vehicleCollateral': {'type': 'MV', 'serialNumber': 'KM8J3CA46JU622994', 'year': 2018, 'make': 'HYUNDAI',
                           'model': 'TUSCON'}},
    {'baseRegistrationNumber': '103838B', 'matchType': 'SIMILAR', 'createDateTime': '2021-10-08T00:02:33+00:00',
     'registrationType': 'RL',
     'vehicleCollateral': {'type': 'MV', 'serialNumber': 'KM8J3CA46JU622994', 'year': 2018, 'make': 'HYUNDAI',
                           'model': 'TUCSON'}},
    {'baseRegistrationNumber': 'TEST0002', 'matchType': 'SIMILAR', 'createDateTime': '2021-12-16T01:18:38+00:00',
     'registrationType': 'RL',
     'vehicleCollateral': {'type': 'MV', 'serialNumber': 'KX8J3CA46JU622994', 'year': 2014, 'make': 'HYUNDAI',
                           'model': 'TUSCON'}},
    {'baseRegistrationNumber': 'TEST0005', 'matchType': 'SIMILAR', 'createDateTime': '2021-12-16T01:18:38+00:00',
     'registrationType': 'SA',
     'vehicleCollateral': {'type': 'MV', 'serialNumber': 'YJ46JU622994', 'year': 2018, 'make': 'TESLA',
                           'model': 'MODEL 3'}}
]
SEARCH_SELECT_1 = [
    {'baseRegistrationNumber': 'TEST0004', 'matchType': 'EXACT'},
    {'baseRegistrationNumber': 'TEST0001', 'matchType': 'EXACT'},
    {'baseRegistrationNumber': '107169B', 'matchType': 'SIMILAR'},
    {'baseRegistrationNumber': 'TEST0001', 'matchType': 'SIMILAR'},
    {'baseRegistrationNumber': '103838B', 'matchType': 'SIMILAR'},
    {'baseRegistrationNumber': 'TEST0002', 'matchType': 'SIMILAR'},
    {'baseRegistrationNumber': 'TEST0005', 'matchType': 'SIMILAR'}
]
SEARCH_SELECT_2 = [
    {'baseRegistrationNumber': 'TEST0004', 'matchType': 'EXACT'}
]
SEARCH_SELECT_3 = [
    {'baseRegistrationNumber': 'TEST0005', 'matchType': 'SIMILAR'}
]
SEARCH_SELECT_4 = [
    {'baseRegistrationNumber': 'TEST0004', 'matchType': 'EXACT'},
    {'baseRegistrationNumber': 'TEST0001', 'matchType': 'EXACT'},
    {'baseRegistrationNumber': '107169B', 'matchType': 'SIMILAR'},
    {'baseRegistrationNumber': 'TEST0001', 'matchType': 'SIMILAR'},
]

# testdata pattern is ({description}, {JSON data}, {search id}, {has history}, {first statement type})
TEST_VALID_DATA = [
    ('Match with history', SINGLE_JSON, 200000001, True, None),
    ('Match with no history', SINGLE_NO_HISTORY_JSON, 200000002, False, None),
    ('Match with renewal', SINGLE_RENEWAL_JSON, 200000003, True, 'RENEWAL_STATEMENT')
]

# testdata pattern is ({description}, {JSON data}, {search id}, {has history}, {first statement type})
TEST_INVALID_DATA = [
    ('Invalid search id', SINGLE_JSON, 390000001, True, None),
    ('Invalid search completed', SINGLE_JSON, 200000000, True, None)
]

# testdata pattern is ({description}, {select_data}, {select_count})
TEST_SEARCH_SELECT_DATA = [
    ('All selection', SEARCH_SELECT_1, 7),
    ('EXACT missing 1 selection', SEARCH_SELECT_2, 2),
    ('Just 1 SIMILAR selection', SEARCH_SELECT_3, 3),
    ('All exact, 2 SIMILAR selection', SEARCH_SELECT_4, 4)
]


@pytest.mark.parametrize('desc,json_data,search_id,has_history,statement_type', TEST_VALID_DATA)
def test_search(session, desc, json_data, search_id, has_history, statement_type):
    """Assert that search detail results on registration matches returns the expected result."""
    # test
    search_detail = SearchResult.validate_search_select(json_data, search_id)
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
    if has_history:
        assert 'changes' in result['details'][0]['financingStatement']
        assert len(result['details'][0]['financingStatement']['changes']) > 0
        if statement_type:
            assert result['details'][0]['financingStatement']['changes'][0]['statementType'] == statement_type
    else:
        assert 'changes' not in result['details'][0]['financingStatement']


@pytest.mark.parametrize('desc,json_data,search_id,has_history,statement_type', TEST_INVALID_DATA)
def test_search_invalid(session, desc, json_data, search_id, has_history, statement_type):
    """Assert that search detail results on invalid requests returns the expected result."""
    # test
    with pytest.raises(BusinessException) as bad_request_err:
        SearchResult.validate_search_select(json_data, search_id)

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
    search_query = SearchRequest.create_from_json(json_data, 'PS12345')

    # test
    search_query.search()
    query_json = search_query.json
    # print(query_json)
    search_detail = SearchResult.create_from_search_query(search_query)
    search_detail.save()

    # check
    assert search_detail.search_id == search_query.id
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


def test_search_history_sort(session, client, jwt):
    """Assert that search results history sort order works as expected."""
    # setup
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'value': 'TEST0001'
        }
    }
    search_query = SearchRequest.create_from_json(json_data, 'PS12345')

    # test
    search_query.search()
    search_detail = SearchResult.create_from_search_query(search_query)
    search_detail.save()

    # check
    assert search_detail.search_id == search_query.id
    result = search_detail.json
    # print(details_json)
    history = result[0]['financingStatement']['changes']
    assert len(history) == 4
    assert history[0]['changeRegistrationNumber'] == 'TEST0010'
    assert history[1]['changeRegistrationNumber'] == 'TEST0009'
    assert history[2]['changeRegistrationNumber'] == 'TEST0008'
    assert history[3]['amendmentRegistrationNumber'] == 'TEST0007'


@pytest.mark.parametrize('desc,select_data,select_count', TEST_SEARCH_SELECT_DATA)
def test_set_search_select(session, client, jwt, desc, select_data, select_count):
    """Assert that submitting a new search selection with minimal data works as expected."""
    # setup
    search_request: SearchRequest = SearchRequest(search_response=SET_SELECT)
    search_result: SearchResult = SearchResult()
    search_result.search = search_request

    # test
    selection = search_result.set_search_selection(select_data)

    # check
    assert selection
    assert len(selection) == select_count
    for select in selection:
        assert select['baseRegistrationNumber']
        assert select['matchType']
        assert select['createDateTime']
        assert select['registrationType']
        assert select['vehicleCollateral']
        assert select['vehicleCollateral']['type']
        assert select['vehicleCollateral']['serialNumber']
        assert select['vehicleCollateral']['year']
        assert select['vehicleCollateral']['make']
        assert select['vehicleCollateral']['model']
