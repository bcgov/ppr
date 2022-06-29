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
import copy
from http import HTTPStatus

import pytest

from flask import current_app

from mhr_api.models import SearchResult, SearchRequest
from mhr_api.exceptions import BusinessException
from mhr_api.resources.v1.search_results import get_payment_details


# Valid test data
MHR_NUMBER_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'value': '022911'
    },
    'clientReferenceId': 'T-SQ-MM-1'
}
MHR_NUMBER_NIL_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'value': '999999'
    },
    'clientReferenceId': 'T-SQ-MM-2'
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

SET_SELECT_NIL = []

SET_SELECT_MM = [
    {'mhrNumber': '022911', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
     'homeLocation': 'FORT NELSON', 'serialNumber': '2427',
     'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
     'ownerName': {'first': 'PRITNAM', 'last': 'SANDHU'}}
]
SET_SELECT_MM_COMBO = [
    {'mhrNumber': '022911', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
     'homeLocation': 'FORT NELSON', 'includeLienInfo': True, 'serialNumber': '2427',
     'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
     'ownerName': {'first': 'PRITNAM', 'last': 'SANDHU'}}
]
SET_SELECT_SORT = [
    {'mhrNumber': '022911', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
     'homeLocation': 'FORT NELSON', 'serialNumber': '2427',
     'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
     'ownerName': {'first': 'PRITNAM', 'last': 'SANDHU'}},
    {'mhrNumber': '002200', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
     'homeLocation': 'FORT NELSON', 'serialNumber': '2427',
     'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
     'ownerName': {'first': 'PRITNAM', 'last': 'SANDHU'}},
    {'mhrNumber': '000199', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
     'homeLocation': 'FORT NELSON', 'serialNumber': '2427',
     'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
     'ownerName': {'first': 'PRITNAM', 'last': 'SANDHU'}},
    {'mhrNumber': '001999', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
     'homeLocation': 'FORT NELSON', 'serialNumber': '2427',
     'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
     'ownerName': {'first': 'PRITNAM', 'last': 'SANDHU'}}
]

# testdata pattern is ({description}, {search data}, {select data})
TEST_VALID_DATA = [
    ('MHR Number Match', MHR_NUMBER_JSON, SET_SELECT_MM),
    ('MHR Number No Match', MHR_NUMBER_NIL_JSON, SET_SELECT_NIL)
]

# testdata pattern is ({description}, {JSON data}, {search id})
TEST_INVALID_DATA = [
    ('Invalid search id', SET_SELECT_MM, 390000001),
    ('Invalid search completed', SET_SELECT_MM, 200000000)
]
# testdata pattern is ({description}, {JSON data}, {mhr_num}, {match_count})
TEST_PPR_SEARCH_DATA = [
    ('No match mhr number', SET_SELECT_MM_COMBO, '999999', 0),
    ('Single match mhr number', SET_SELECT_MM_COMBO, '022000', 1),
    ('Double match mhr number', SET_SELECT_MM_COMBO, '220000', 2)
]

# testdata pattern is ({mhr1}, {mhr2}, {mhr3}, mhr4)
TEST_SELECT_SORT_DATA = [
    ('001999', '002200', '000199', '022911'),
    ('000199', '002200', '001999', '022911'),
    ('022911', '002200', '000199', '001999'),
    ('000199', '001999', '002200', '022911')
]

@pytest.mark.parametrize('desc,search_data,select_data', TEST_VALID_DATA)
def test_search_valid_db2(session, desc, search_data, select_data):
    """Assert that search detail results on registration matches returns the expected result."""
    # test
    search_query = SearchRequest.create_from_json(search_data, 'PS12345')
    search_query.search_db2()
    # current_app.logger.info(search_query.json)
    search_detail = SearchResult.create_from_search_query(search_query)
    search_detail.save()

    # check
    assert search_detail.search_id == search_query.id
    assert not search_detail.search_select

    search_detail2 = SearchResult.validate_search_select(select_data, search_detail.search_id)
    search_detail2.update_selection(select_data)

    # check
    # current_app.logger.debug(search_detail2.search_select)
    if select_data:
      assert search_detail2.search_select
    result = search_detail2.json
    current_app.logger.debug(result)

    assert result['searchDateTime']
    assert result['searchQuery']
    if select_data:
      assert result['details']
      assert result['totalResultsSize'] == 1
      assert len(result['details']) == 1


@pytest.mark.parametrize('desc,json_data,search_id', TEST_INVALID_DATA)
def test_search_invalid(session, desc, json_data, search_id):
    """Assert that search detail results on invalid requests returns the expected result."""
    # test
    with pytest.raises(BusinessException) as bad_request_err:
        SearchResult.validate_search_select(json_data, search_id)

    # check
    assert bad_request_err
    if desc == 'Invalid search id':
        assert bad_request_err.value.status_code == HTTPStatus.NOT_FOUND
    else:
        assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    # print(bad_request_err.value.error)


@pytest.mark.parametrize('desc,json_data,mhr_num,match_count', TEST_PPR_SEARCH_DATA)
def test_search_ppr_by_mhr_number(session, desc, json_data, mhr_num, match_count):
    """Assert that a PPR MHR number search returns the expected result."""
    if json_data[0].get('includeLienInfo', False):
        # test
        result_json = SearchResult.search_ppr_by_mhr_number(mhr_num)
        # current_app.logger.debug(result_json)
        # check
        assert result_json is not None
        if match_count == 0:
            assert not result_json
        else:
            assert len(result_json) == match_count
            for result in result_json:
                assert result['financingStatement']
                statement = result['financingStatement']
                assert statement['type']
                assert statement['baseRegistrationNumber']
                assert statement['createDateTime']
                assert statement['registeringParty']
                assert statement['securedParties']
                assert statement['debtors']
                assert statement['vehicleCollateral'] or statement['generalCollateral']


@pytest.mark.parametrize('mhr1,mhr2,mhr3,mhr4', TEST_SELECT_SORT_DATA)
def test_search_sort(session, client, jwt, mhr1, mhr2, mhr3, mhr4):
    """Assert that submitting a new search selection is sorted as expected."""
    # setup
    select_data = copy.deepcopy(SET_SELECT_SORT)
    select_data[0]['mhrNumber'] = mhr1
    select_data[1]['mhrNumber'] = mhr2
    select_data[2]['mhrNumber'] = mhr3
    select_data[3]['mhrNumber'] = mhr4

    # test
    search_result: SearchResult = SearchResult()
    search_request: SearchRequest = SearchRequest(search_response=select_data)
    search_result.search = search_request
    search_result.set_search_selection(select_data)
    sorted_data = search_result.search_select

    # check
    assert len(sorted_data) == 4
    assert sorted_data[0]['mhrNumber'] == '000199'
    assert sorted_data[1]['mhrNumber'] == '001999'
    assert sorted_data[2]['mhrNumber'] == '002200'
    assert sorted_data[3]['mhrNumber'] == '022911'
