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
REG_NUMBER_JSON = {
    'type': 'REGISTRATION_NUMBER',
    'criteria': {
        'value': '?'
    },
    'clientReferenceId': 'HISTORICAL SEARCH',
    'accountName': 'UT HISTORICAL SEARCH'
}
AIRCRAFT_DOT_JSON = {
    'type': 'AIRCRAFT_DOT',
    'criteria': {
        'value': '?'
    },
    'clientReferenceId': 'HISTORICAL SEARCH',
    'accountName': 'UT HISTORICAL SEARCH'
}
MHR_NUMBER_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'value': '?'
    },
    'clientReferenceId': 'HISTORICAL SEARCH',
    'accountName': 'UT HISTORICAL SEARCH'
}
BUSINESS_DEBTOR_JSON = {
    'type': 'BUSINESS_DEBTOR',
    'criteria': {
        'debtorName': {
            'business': '0996357 B.C. LTD.'
        }
    },
    'clientReferenceId': 'HISTORICAL SEARCH',
    'accountName': 'UT HISTORICAL SEARCH',
    'searchDateTime': '2022-05-16T06:59:59+00:00'
}
INDIVIDUAL_DEBTOR_JSON = {
    'type': 'INDIVIDUAL_DEBTOR',
    'criteria': {
        'debtorName': {
            'last': 'BITTNER',
            'first': 'GAIL'
        }
    },
    'clientReferenceId': 'HISTORICAL SEARCH',
    'accountName': 'UT HISTORICAL SEARCH',
    'searchDateTime': '2021-12-16T07:59:59+00:00'
}
# testdata pattern is ({desc}, {search_ts})
TEST_DATA_HISTORICAL_ID = [
    ('Test get search historical id', '2022-09-26T06:59:59+00:00')
]
# testdata pattern is ({desc}, {search_ts}, {search_reg_id}, {criteria})
TEST_DATA_SEARCH_SERIAL_QUERY = [
    ('Test search historical serial number query', '2022-09-26T06:59:59+00:00', 2389990, '1G1YL2D73K5105174')
]
# testdata pattern is ({desc}, {search_ts}, {search_reg_id}, {criteria})
TEST_DATA_SEARCH_REG_NUM_QUERY = [
    ('Test search historical registration number query', '2022-09-26T06:59:59+00:00', 2389990, '924834N')
]
# testdata pattern is ({desc}, {search_ts}, {search_reg_id}, {criteria})
TEST_DATA_SEARCH_MHR_NUM_QUERY = [
    ('Test search historical mhr number query', '2022-01-01T07:59:59+00:00', 1847933, '106284')
]
# testdata pattern is ({desc}, {search_ts}, {search_reg_id}, {criteria})
TEST_DATA_SEARCH_AIRCRAFT_QUERY = [
    ('Test search historical aircraft serial# query', '2022-01-01T07:59:59+00:00', 1847933, 'BB2007')
]
# testdata pattern is ({desc}, {search_ts}, {search_reg_id}, {criteria})
TEST_DATA_SEARCH_BUS_DEBTOR_QUERY = [
    ('Test search historical business debtor query', 1892928, BUSINESS_DEBTOR_JSON)
]
# testdata pattern is ({desc}, {search_ts}, {search_reg_id}, {criteria})
TEST_DATA_SEARCH_IND_DEBTOR_QUERY = [
    ('Test search historical individual debtor query', 1821760, INDIVIDUAL_DEBTOR_JSON)
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


@pytest.mark.parametrize('desc,search_ts,reg_id,criteria', TEST_DATA_SEARCH_REG_NUM_QUERY)
def test_search_by_registration_number(session, desc, search_ts, reg_id, criteria):
    """Assert that registration number historical search step 1 works as expected."""
    search_criteria = copy.deepcopy(REG_NUMBER_JSON)
    search_criteria['criteria']['value'] = criteria
    search_criteria['searchDateTime'] = search_ts
    query: SearchRequest = SearchRequest(search_criteria=search_criteria,
                                         search_ts=model_utils.ts_from_iso_format(search_ts),
                                         account_id=search_historical.HISTORICAL_ACCOUNT_ID,
                                         client_reference_id=search_historical.HISTORICAL_REF_ID)

    query = search_historical.search_by_registration_number(query, reg_id, search_ts)
    query_json = query.json
    current_app.logger.debug(query_json)
    assert query_json.get('searchDateTime')
    assert query_json.get('totalResultsSize') >= 0
    assert query_json.get('returnedResultsSize') >= 0
    assert query_json.get('searchQuery')
    assert 'searchId' in query_json
    if query.returned_results_size > 0:
        current_app.logger.debug(json.dumps(query_json))


@pytest.mark.parametrize('desc,search_ts,reg_id,criteria', TEST_DATA_SEARCH_REG_NUM_QUERY)
def test_search_reg_num(session, desc, search_ts, reg_id, criteria):
    """Assert that historical search by registration number works as expected."""
    search_criteria = copy.deepcopy(REG_NUMBER_JSON)
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


@pytest.mark.parametrize('desc,search_ts,reg_id,criteria', TEST_DATA_SEARCH_MHR_NUM_QUERY)
def test_search_by_mhr_number(session, desc, search_ts, reg_id, criteria):
    """Assert that mhr number historical search step 1 works as expected."""
    search_criteria = copy.deepcopy(MHR_NUMBER_JSON)
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


@pytest.mark.parametrize('desc,search_ts,reg_id,criteria', TEST_DATA_SEARCH_MHR_NUM_QUERY)
def test_search_mhr_num(session, desc, search_ts, reg_id, criteria):
    """Assert that historical search by mhr number works as expected."""
    search_criteria = copy.deepcopy(MHR_NUMBER_JSON)
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


@pytest.mark.parametrize('desc,search_ts,reg_id,criteria', TEST_DATA_SEARCH_AIRCRAFT_QUERY)
def test_search_by_aircraft_dot(session, desc, search_ts, reg_id, criteria):
    """Assert that aircraft DOT historical search step 1 works as expected."""
    search_criteria = copy.deepcopy(AIRCRAFT_DOT_JSON)
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


@pytest.mark.parametrize('desc,search_ts,reg_id,criteria', TEST_DATA_SEARCH_AIRCRAFT_QUERY)
def test_search_ac_dot(session, desc, search_ts, reg_id, criteria):
    """Assert that historical search by aircraft DOT works as expected."""
    search_criteria = copy.deepcopy(AIRCRAFT_DOT_JSON)
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


@pytest.mark.parametrize('desc,reg_id,search_criteria', TEST_DATA_SEARCH_BUS_DEBTOR_QUERY)
def test_search_by_business_debtor(session, desc, reg_id, search_criteria):
    """Assert that business debtor name historical search step 1 works as expected."""
    search_ts = search_criteria['searchDateTime']
    query: SearchRequest = SearchRequest(search_criteria=search_criteria,
                                         search_ts=model_utils.ts_from_iso_format(search_ts),
                                         account_id=search_historical.HISTORICAL_ACCOUNT_ID,
                                         client_reference_id=search_historical.HISTORICAL_REF_ID)

    query = search_historical.search_by_business_name(query, reg_id, search_ts)
    query_json = query.json
    current_app.logger.debug(query_json)
    assert query_json.get('searchDateTime')
    assert query_json.get('totalResultsSize') >= 0
    assert query_json.get('returnedResultsSize') >= 0
    assert query_json.get('searchQuery')
    assert 'searchId' in query_json
    if query.returned_results_size > 0:
        current_app.logger.debug(json.dumps(query_json))


@pytest.mark.parametrize('desc,reg_id,search_criteria', TEST_DATA_SEARCH_BUS_DEBTOR_QUERY)
def test_search_bus_debtor(session, desc, reg_id, search_criteria):
    """Assert that historical search by business debtor name works as expected."""
    query: SearchRequest = search_historical.search(search_criteria, reg_id)
    assert query.id > 0
    if query:
        result: SearchResult = search_historical.build_search_results(reg_id, query)
        if search_criteria.get('accountName'):
            result.account_name = search_criteria.get('accountName')
        report_json = result.json
        current_app.logger.debug(json.dumps(report_json))
        # current_app.logger.debug(report_json)


@pytest.mark.parametrize('desc,reg_id,search_criteria', TEST_DATA_SEARCH_IND_DEBTOR_QUERY)
def test_search_by_individual_debtor(session, desc, reg_id, search_criteria):
    """Assert that individual debtor name historical search step 1 works as expected."""
    search_ts = search_criteria['searchDateTime']
    query: SearchRequest = SearchRequest(search_criteria=search_criteria,
                                         search_ts=model_utils.ts_from_iso_format(search_ts),
                                         account_id=search_historical.HISTORICAL_ACCOUNT_ID,
                                         client_reference_id=search_historical.HISTORICAL_REF_ID)
    query = search_historical.search_by_individual_name(query, reg_id, search_ts)
    query_json = query.json
    current_app.logger.debug(query_json)
    assert query_json.get('searchDateTime')
    assert query_json.get('totalResultsSize') >= 0
    assert query_json.get('returnedResultsSize') >= 0
    assert query_json.get('searchQuery')
    assert 'searchId' in query_json
    if query.returned_results_size > 0:
        current_app.logger.debug(json.dumps(query_json))


@pytest.mark.parametrize('desc,reg_id,search_criteria', TEST_DATA_SEARCH_IND_DEBTOR_QUERY)
def test_search_ind_debtor(session, desc, reg_id, search_criteria):
    """Assert that historical search by individual debtor name works as expected."""
    query: SearchRequest = search_historical.search(search_criteria, reg_id)
    assert query.id > 0
    if query:
        result: SearchResult = search_historical.build_search_results(reg_id, query)
        if search_criteria.get('accountName'):
            result.account_name = search_criteria.get('accountName')
        report_json = result.json
        current_app.logger.debug(json.dumps(report_json))
        # current_app.logger.debug(report_json)
