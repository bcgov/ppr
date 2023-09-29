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
"""Test Suite to ensure the datetime utility functions are working as expected."""
import copy
import json

from flask import current_app

import pytest

from ppr_api.models import utils as model_utils, Registration, SearchRequest, search_historical, SearchResult


SERIAL_NUMBER_JSON = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'value': '?'
    },
    'clientReferenceId': 'HISTORICAL SEARCH',
    'accountName': 'UT HISTORICAL SEARCH'
}
# testdata pattern is ({desc}, {search_ts})
TEST_DATA_HISTORICAL_ID = [
    ('Test get search historical id', '2022-09-26T06:59:59+00:00')
]
# testdata pattern is ({desc}, {search_ts}, {search_reg_id}, {criteria})
TEST_DATA_SEARCH_SERIAL_QUERY = [
    ('Test search historical serial number query', '2022-09-26T06:59:59+00:00', 2389990, '1G1YL2D73K5105174')
]


@pytest.mark.parametrize('desc,search_ts', TEST_DATA_HISTORICAL_ID)
def test_get_search_historical_id(session, desc, search_ts):
    """Assert that getting the historical search max registration id works as expected."""
    max_reg_id = search_historical.get_search_historical_id(search_ts)
    assert max_reg_id >= 0


@pytest.mark.parametrize('desc,search_ts,reg_id,criteria', TEST_DATA_SEARCH_SERIAL_QUERY)
def test_search_by_serial_type(session, desc, search_ts, reg_id, criteria):
    """Assert that serial number historical search step 1 works as expected."""
    search_criteria = copy.deepcopy(SERIAL_NUMBER_JSON)
    search_criteria['criteria']['value'] = criteria
    search_criteria['searchDateTime'] = search_ts
    query: SearchRequest = SearchRequest(search_criteria=search_criteria,
                                         search_ts=model_utils.ts_from_iso_format(search_ts),
                                         account_id=search_historical.HISTORICAL_ACCOUNT_ID,
                                         client_reference_id=search_historical.HISTORICAL_REF_ID)

    query = search_historical.search_by_serial_type(query, reg_id, search_ts)
    query_json = query.json
    current_app.logger.debug(query_json)
    assert query_json.get('searchDateTime')
    assert query_json.get('totalResultsSize') >= 0
    assert query_json.get('returnedResultsSize') >= 0
    assert query_json.get('searchQuery')
    assert 'searchId' in query_json
    if query.returned_results_size > 0:
        current_app.logger.debug(json.dumps(query_json))


@pytest.mark.parametrize('desc,search_ts,reg_id,criteria', TEST_DATA_SEARCH_SERIAL_QUERY)
def test_search_serial(session, desc, search_ts, reg_id, criteria):
    """Assert that historical search works as expected."""
    search_criteria = copy.deepcopy(SERIAL_NUMBER_JSON)
    search_criteria['criteria']['value'] = criteria
    search_criteria['searchDateTime'] = search_ts
    query: SearchRequest = search_historical.search(search_criteria, reg_id)
    assert query.id > 0
    if query:
        result: SearchResult = search_historical.build_search_results(reg_id, query)
        if search_criteria.get('accountName'):
            result.account_name = search_criteria.get('accountName')
        report_json = result.json
        current_app.logger.debug(json.dumps(report_json))
        # current_app.logger.debug(report_json)
