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

from flask import current_app

from mhr_api.models import SearchResult, SearchRequest
from mhr_api.exceptions import BusinessException


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

SET_SELECT_NIL = []

SET_SELECT_MM = [
    {'mhrNumber': '022911', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
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
