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
import json

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
SELECT_1 = {
    'mhrNumber': '022911', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
    'homeLocation': 'FORT NELSON', 'serialNumber': '2427',
    'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
    'organizationName': 'CRYSTAL RIVER COURT LTD.'
}
SELECT_2 = {
    'mhrNumber': '002200', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
    'homeLocation': 'FORT NELSON', 'serialNumber': '9427',
    'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
    'organizationName': 'CRYSTAL POND DESIGN LIMITED'    
}
SELECT_3 = {
    'mhrNumber': '002200', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
    'homeLocation': 'FORT NELSON', 'serialNumber': '2427',
    'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
    'organizationName': 'CRYSTAL RIVER COURT LTD.'}
SELECT_4 = {
    'mhrNumber': '001999', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
    'homeLocation': 'FORT NELSON', 'serialNumber': '2427',
    'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
    'organizationName': 'CRYSTAL RIVER COURT LTD.'
}
SELECT_1_IND = {
    'mhrNumber': '022911', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
    'homeLocation': 'FORT NELSON', 'serialNumber': '2427',
    'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
    'ownerName': {'first': 'PRITNAM', 'last': 'SANDHU'}
}
SELECT_2_IND = {
    'mhrNumber': '002200', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
    'homeLocation': 'FORT NELSON', 'serialNumber': '9427',
    'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
    'ownerName': {'first': 'JANE', 'last': 'SANDHU'}   
}
SELECT_3_IND = {
    'mhrNumber': '002200', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
    'homeLocation': 'FORT NELSON', 'serialNumber': '2427',
    'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
    'ownerName': {'first': 'JOHN', 'last': 'SANDHU'}
}
SELECT_4_IND = {
    'mhrNumber': '001999', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
    'homeLocation': 'FORT NELSON', 'serialNumber': '2427',
    'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
    'ownerName': {'first': 'PRITNAM', 'last': 'SANDHU'}
}

# testdata pattern is ({description}, {search data}, {select data})
TEST_VALID_DATA = [
    ('MHR Number Match not certified', MHR_NUMBER_JSON, SET_SELECT_MM, False),
    ('MHR Number Match certified', MHR_NUMBER_JSON, SET_SELECT_MM, True),
    ('MHR Number No Match', MHR_NUMBER_NIL_JSON, SET_SELECT_NIL, False)
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

# testdata pattern is ({mhr1}, {mhr2}, {mhr3}, {mhr4}, {search_type})
TEST_SELECT_SORT_DATA = [
    ('001999', '002200', '000199', '022911', SearchRequest.SearchTypes.SERIAL_NUM),
    ('000199', '002200', '001999', '022911', SearchRequest.SearchTypes.SERIAL_NUM),
    ('022911', '002200', '000199', '001999', SearchRequest.SearchTypes.OWNER_NAME),
    ('000199', '001999', '002200', '022911', SearchRequest.SearchTypes.OWNER_NAME)
]
# testdata pattern is ({mhr1}, {mhr2}, {mhr3}, {mhr4})
TEST_SELECT_SORT_DATA_SERIAL = [
    (SELECT_4, SELECT_2, SELECT_3, SELECT_1),
    (SELECT_2, SELECT_3, SELECT_4, SELECT_1),
    (SELECT_1, SELECT_2, SELECT_3, SELECT_4),
    (SELECT_2, SELECT_1, SELECT_3, SELECT_4)
]
# testdata pattern is ({mhr1}, {mhr2}, {mhr3}, {mhr4})
TEST_SELECT_SORT_DATA_ORG = [
    (SELECT_4, SELECT_2, SELECT_3, SELECT_1),
    (SELECT_2, SELECT_3, SELECT_4, SELECT_1),
    (SELECT_1, SELECT_2, SELECT_3, SELECT_4),
    (SELECT_2, SELECT_1, SELECT_3, SELECT_4)
]
TEST_SELECT_SORT_DATA_IND = [
    (SELECT_4_IND, SELECT_2_IND, SELECT_3_IND, SELECT_1_IND),
    (SELECT_2_IND, SELECT_3_IND, SELECT_4_IND, SELECT_1_IND),
    (SELECT_1_IND, SELECT_2_IND, SELECT_3_IND, SELECT_4_IND),
    (SELECT_2_IND, SELECT_1_IND, SELECT_3_IND, SELECT_4_IND)
]


@pytest.mark.parametrize('desc,search_data,select_data,certified', TEST_VALID_DATA)
def test_search_valid(session, desc, search_data, select_data,certified):
    """Assert that search detail results on registration matches returns the expected result."""
    # test
    search_query = SearchRequest.create_from_json(search_data, 'PS12345')
    search_query.search()
    # current_app.logger.info(search_query.json)
    search_detail = SearchResult.create_from_search_query(search_query)
    search_detail.save()

    # check
    assert search_detail.search_id == search_query.id
    assert not search_detail.search_select

    search_detail2 = SearchResult.validate_search_select(select_data, search_detail.search_id)
    search_detail2.update_selection(select_data, 'account name', None, certified)

    # check
    # current_app.logger.debug(search_detail2.search_select)
    if select_data:
      assert search_detail2.search_select
    result = search_detail2.json
    # current_app.logger.debug(result)

    assert result['searchDateTime']
    assert result['searchQuery']
    if certified:
        assert result.get('certified')
    else:
        assert not result.get('certified')
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


@pytest.mark.parametrize('mhr1,mhr2,mhr3,mhr4,search_type', TEST_SELECT_SORT_DATA)
def test_search_sort_mhr(session, client, jwt, mhr1, mhr2, mhr3, mhr4, search_type):
    """Assert that submitting a new search selection is sorted as expected."""
    # setup
    select_data = copy.deepcopy(SET_SELECT_SORT)
    select_data[0]['mhrNumber'] = mhr1
    select_data[1]['mhrNumber'] = mhr2
    select_data[2]['mhrNumber'] = mhr3
    select_data[3]['mhrNumber'] = mhr4

    # test
    search_result: SearchResult = SearchResult()
    search_request: SearchRequest = SearchRequest(search_response=select_data, search_type=search_type)
    search_result.search = search_request
    search_result.set_search_selection(select_data)
    sorted_data = search_result.search_select

    # check
    assert len(sorted_data) == 4
    assert sorted_data[0]['mhrNumber'] == '022911'
    assert sorted_data[1]['mhrNumber'] == '002200'
    assert sorted_data[2]['mhrNumber'] == '001999'
    assert sorted_data[3]['mhrNumber'] == '000199'


@pytest.mark.parametrize('mhr1,mhr2,mhr3,mhr4', TEST_SELECT_SORT_DATA_SERIAL)
def test_search_sort_serial(session, client, jwt, mhr1, mhr2, mhr3, mhr4):
    """Assert that submitting a new serial number search selection is sorted as expected."""
    # setup
    select_data = []
    select_data.append(mhr1)
    select_data.append(mhr2)
    select_data.append(mhr3)
    select_data.append(mhr4)

    # test
    search_result: SearchResult = SearchResult()
    search_request: SearchRequest = SearchRequest(search_response=select_data,
                                                  search_type=SearchRequest.SearchTypes.SERIAL_NUM)
    search_result.search = search_request
    search_result.set_search_selection(select_data)
    sorted_data = search_result.search_select

    # check
    assert len(sorted_data) == 4
    assert sorted_data[0]['mhrNumber'] == '022911'
    assert sorted_data[1]['mhrNumber'] == '002200'
    assert sorted_data[1]['serialNumber'] == '2427'
    assert sorted_data[2]['mhrNumber'] == '002200'
    assert sorted_data[2]['serialNumber'] == '9427'
    assert sorted_data[3]['mhrNumber'] == '001999'


@pytest.mark.parametrize('mhr1,mhr2,mhr3,mhr4', TEST_SELECT_SORT_DATA_ORG)
def test_search_sort_org(session, client, jwt, mhr1, mhr2, mhr3, mhr4):
    """Assert that submitting a new owner organization search selection is sorted as expected."""
    # setup
    select_data = []
    select_data.append(mhr1)
    select_data.append(mhr2)
    select_data.append(mhr3)
    select_data.append(mhr4)
    #current_app.logger.info(json.dumps(select_data))

    # test
    search_result: SearchResult = SearchResult()
    search_request: SearchRequest = SearchRequest(search_response=select_data,
                                                  search_type=SearchRequest.SearchTypes.ORGANIZATION_NAME)
    search_result.search = search_request
    search_result.set_search_selection(select_data)
    sorted_data = search_result.search_select

    # check
    assert len(sorted_data) == 4
    assert sorted_data[0]['mhrNumber'] == '022911'
    assert sorted_data[1]['mhrNumber'] == '002200'
    assert sorted_data[1]['organizationName'] == 'CRYSTAL POND DESIGN LIMITED'
    assert sorted_data[2]['mhrNumber'] == '002200'
    assert sorted_data[2]['organizationName'] == 'CRYSTAL RIVER COURT LTD.'
    assert sorted_data[3]['mhrNumber'] == '001999'


@pytest.mark.parametrize('mhr1,mhr2,mhr3,mhr4', TEST_SELECT_SORT_DATA_IND)
def test_search_sort_ind(session, client, jwt, mhr1, mhr2, mhr3, mhr4):
    """Assert that submitting a new owner individual search selection is sorted as expected."""
    # setup
    select_data = []
    select_data.append(mhr1)
    select_data.append(mhr2)
    select_data.append(mhr3)
    select_data.append(mhr4)
    #current_app.logger.info(json.dumps(select_data))

    # test
    search_result: SearchResult = SearchResult()
    search_request: SearchRequest = SearchRequest(search_response=select_data,
                                                  search_type=SearchRequest.SearchTypes.OWNER_NAME)
    search_result.search = search_request
    search_result.set_search_selection(select_data)
    sorted_data = search_result.search_select

    # check
    assert len(sorted_data) == 4
    assert sorted_data[0]['mhrNumber'] == '022911'
    assert sorted_data[1]['mhrNumber'] == '002200'
    assert sorted_data[1]['ownerName']['first'] == 'JANE'
    assert sorted_data[2]['mhrNumber'] == '002200'
    assert sorted_data[2]['ownerName']['first'] == 'JOHN'
    assert sorted_data[3]['mhrNumber'] == '001999'
