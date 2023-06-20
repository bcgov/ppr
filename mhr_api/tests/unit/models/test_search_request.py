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

"""Tests to assure the Search Model.

Test-Suite to ensure that the Search Model is working as expected.
"""
from http import HTTPStatus
import copy

from flask import current_app

import pytest

from mhr_api.models import SearchRequest, utils as model_utils, search_utils
from mhr_api.exceptions import BusinessException


MHR_NUMBER_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'value': '022911'
    },
    'clientReferenceId': 'T-SQ-MH-1'
}
MH_INVALID_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'ownerName': {
            'first': 'JAMES',
            'last': 'BROWN'
        }
    }
}
# Test valid criteria with no results.
MH_NONE_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'value': '999999'
    },
    'clientReferenceId': 'T-SQ-MH-4'
}
ORG_NAME_JSON = {
    'type': 'ORGANIZATION_NAME',
    'criteria': {
        'value': 'JANDEL HOMES LTD.'
    },
    'clientReferenceId': 'T-SQ-MO-1'
}
MO_INVALID_JSON = {
    'type': 'ORGANIZATION_NAME',
    'criteria': {
        'ownerName': {
            'first': 'JAMES',
            'last': 'BROWN'
        }
    }
}
# Test valid criteria with no results.
MO_NONE_JSON = {
    'type': 'ORGANIZATION_NAME',
    'criteria': {
        'value': 'XXXXXXXXXXXZZZZZ'
    },
    'clientReferenceId': 'T-SQ-MH-4'
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
OWNER_NAME_VALID_JSON = {
    'type': 'OWNER_NAME',
    'criteria': {
        'ownerName': {
            'first': 'B',
            'last': 'MCKAY'
        }
    },
    'clientReferenceId': 'T-SQ-MI-1'
}
OWNER_NAME_NONE_JSON = {
    'type': 'OWNER_NAME',
    'criteria': {
        'ownerName': {
            'first': 'JUNKJUNK',
            'last': 'JUNK'
        }
    },
    'clientReferenceId': 'T-SQ-MI-1'
}
OWNER_NAME_JSON2 = {
    'type': 'OWNER_NAME',
    'criteria': {
        'ownerName': {
            'first': 'ROSE',
            'middle': 'CHERYL',
            'last': 'LESLIE'
        }
    },
    'clientReferenceId': 'T-SQ-MI-1'
}
MI_INVALID_JSON = {
    'type': 'OWNER_NAME',
    'criteria': {
        'value': 'GUTHRIE HOLDINGS LTD.'
    }
}
# Test valid criteria with no results.
MI_NONE_JSON = {
    'type': 'OWNER_NAME',
    'criteria': {
        'ownerName': {
            'first': 'ZZZZYYYYY',
            'last': 'XXXXXXXXOO'
        }
    },
    'clientReferenceId': 'T-SQ-MI-4'
}
SERIAL_NUMBER_JSON = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'value': '9493'
    },
    'clientReferenceId': 'T-SQ-MS-1'
}
MS_INVALID_JSON = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'ownerName': {
            'first': 'JAMES',
            'last': 'BROWN'
        }
    }
}
# Test valid criteria with no results.
MS_NONE_JSON = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'value': 'XXX999999999'
    },
    'clientReferenceId': 'T-SQ-MS-4'
}
UPDATE_RESULTS_ORG_BASE = [
    {
        'mhrNumber': '003456',
        'organizationName': 'TEST LTD.',
        'activeCount': 1,
        'exemptCount': 0,
        'historicalCount': 0
    }
]
UPDATE_ORG_RESULT_1 = {
    'mhrNumber': '003456',
    'organizationName': 'TEST LTD.',
    'activeCount': 0,
    'exemptCount': 1,
    'historicalCount': 0
}
UPDATE_ORG_RESULT_2 = {
    'mhrNumber': '003456',
    'organizationName': 'TEST LTD.',
    'activeCount': 0,
    'exemptCount': 0,
    'historicalCount': 1
}
UPDATE_ORG_RESULT_3 = {
    'mhrNumber': '003457',
    'organizationName': 'TEST LTD.',
    'activeCount': 1,
    'exemptCount': 0,
    'historicalCount': 0
}
UPDATE_ORG_RESULT_4 = {
    'mhrNumber': '003458',
    'organizationName': 'TEST LTD.',
    'activeCount': 0,
    'exemptCount': 1,
    'historicalCount': 0
}
ORG_NAME_JSON_COLLAPSE = {
    'type': 'ORGANIZATION_NAME',
    'criteria': {
        'value': 'RANCOURT HOLDINGS LTD.'
    },
    'clientReferenceId': 'T-SQ-MO-2'
}
OWNER_NAME_JSON_COLLAPSE = {
    'type': 'OWNER_NAME',
    'criteria': {
        'ownerName': {
            'first': 'GAYLEEN',
            'last': 'ALEXANDER'
        }
    },
    'clientReferenceId': 'T-SQ-MI-3'
}
SERIAL_NUMBER_JSON_COLLAPSE = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'value': '000060'
    },
    'clientReferenceId': 'T-SQ-MS-3'
}
UPDATE_RESULTS_OWNER_BASE = [
    {
        'mhrNumber': '003456',
        'ownerName': {
            'first': 'JOHN',
            'last': 'SMITH'
        },
        'activeCount': 1,
        'exemptCount': 0,
        'historicalCount': 0
    }
]
UPDATE_OWNER_RESULT_1 = {
    'mhrNumber': '003456',
    'ownerName': {
        'first': 'JOHN',
        'last': 'SMITH'
    },
    'activeCount': 0,
    'exemptCount': 1,
    'historicalCount': 0
}
UPDATE_OWNER_RESULT_2 = {
    'mhrNumber': '003456',
    'ownerName': {
        'first': 'JOHN',
        'last': 'SMITH'
    },
    'activeCount': 0,
    'exemptCount': 0,
    'historicalCount': 1
}
UPDATE_OWNER_RESULT_3 = {
    'mhrNumber': '003457',
    'ownerName': {
        'first': 'JOHN',
        'last': 'SMITH'
    },
    'activeCount': 1,
    'exemptCount': 0,
    'historicalCount': 0
}
UPDATE_OWNER_RESULT_4 = {
    'mhrNumber': '003458',
    'ownerName': {
        'first': 'JOHN',
        'last': 'SMITH'
    },
    'activeCount': 0,
    'exemptCount': 1,
    'historicalCount': 0
}
UPDATE_RESULTS_SERIAL_BASE = [
    {
        'mhrNumber': '003456',
        'serialNumber': '313000A008326ABC',
        'activeCount': 1,
        'exemptCount': 0,
        'historicalCount': 0
    }
]
UPDATE_SERIAL_RESULT_1 = {
    'mhrNumber': '003456',
    'serialNumber': '313000A008326ABC',
    'activeCount': 1,
    'exemptCount': 0,
    'historicalCount': 0
}
UPDATE_SERIAL_RESULT_2 = {
    'mhrNumber': '003456',
    'serialNumber': '313000A008326ABC',
    'activeCount': 1,
    'exemptCount': 0,
    'historicalCount': 0
}
UPDATE_SERIAL_RESULT_3 = {
    'mhrNumber': '003457',
    'serialNumber': '313000A008326ABC',
    'activeCount': 1,
    'exemptCount': 0,
    'historicalCount': 0
}
UPDATE_SERIAL_RESULT_4 = {
    'mhrNumber': '003458',
    'serialNumber': '313000A008326ABC',
    'activeCount': 1,
    'exemptCount': 0,
    'historicalCount': 0
}


# testdata pattern is ({search type}, {JSON data})
TEST_VALID_DATA = [
    ('MM', MHR_NUMBER_JSON),
    ('MO', ORG_NAME_JSON),
    ('MI', OWNER_NAME_JSON),
    ('MI', OWNER_NAME_JSON2),
    ('MS', SERIAL_NUMBER_JSON),
]
# testdata pattern is ({search type}, {JSON data})
TEST_NONE_DATA = [
    ('MM', MH_NONE_JSON),
    ('MO', MO_NONE_JSON),
    ('MI', MO_NONE_JSON),
    ('MS', MS_NONE_JSON)
]
# testdata pattern is ({search type}, {JSON data})
TEST_INVALID_DATA = [
    ('MM', MH_INVALID_JSON),
    ('MO', MO_INVALID_JSON),
    ('MI', MI_INVALID_JSON),
    ('MS', MS_INVALID_JSON)
]
# testdata pattern is ({mhr_number}, {expected_num})
TEST_MHR_NUMBER_DATA = [
    ('001232', '001232'),
    (' 1232 ', '001232'),
    ('1232', '001232'),
    ('01232', '001232')
]
# testdata pattern is ({search_value}, {count}, {mhr_num1}, {result_val1}, {mhr_num2}, {result_val2})
TEST_SERIAL_NUMBER_DATA = [
    ('999999', 0, None, None, None, None),
    ('D1644', 6, '010469', 'D1644', '100570', '03A001644'),
    ('S60009493', 2, '103147', 'S60009493', '017874', '9493'),
    ('WIN24440204003A', 1, '088121', 'WIN24440204003A', '088121', 'WIN24440204003B'),
    ('003000ZA002773B', 1, '102878', '003000ZA002773B', None, None),
    ('PHH310OR1812828CRCM', 1, '102909', 'PHH310OR1812828CRCM', None, None),
    ('0310282AB', 1, '058161', '0310282AB', None, None),
    ('681323', 1, '010448', '681323', None, None),
    ('681324', 1, '010448', '681324', None, None),
    ('A4820717A', 1, '007109', 'A4820717A', '007109', 'A4820717B')
]

# testdata pattern is ({last_name}, {first_name}, count)
TEST_OWNER_IND_DATA = [
    ('Hamm', 'David', 2),
    ('Hamm', '', 245)
]
# testdata pattern is ({result1}, {result2}, {result_count}, {active_count}, {exempt_count}, {historical_count})
TEST_UPDATE_DATA_ORG = [
    (UPDATE_ORG_RESULT_1, None, 1, 1, 1, 0),
    (UPDATE_ORG_RESULT_2, None, 1, 1, 0, 1),
    (UPDATE_ORG_RESULT_1, UPDATE_ORG_RESULT_2, 1, 1, 1, 1),
    (UPDATE_ORG_RESULT_1, UPDATE_ORG_RESULT_3, 2, 1, 1, 0),
    (UPDATE_ORG_RESULT_3, UPDATE_ORG_RESULT_4, 3, 1, 0, 0)
]
# testdata pattern is ({result1}, {result2}, {result_count}, {active_count}, {exempt_count}, {historical_count})
TEST_UPDATE_DATA_OWNER = [
    (UPDATE_OWNER_RESULT_1, None, 1, 1, 1, 0),
    (UPDATE_OWNER_RESULT_2, None, 1, 1, 0, 1),
    (UPDATE_OWNER_RESULT_1, UPDATE_OWNER_RESULT_2, 1, 1, 1, 1),
    (UPDATE_OWNER_RESULT_1, UPDATE_OWNER_RESULT_3, 2, 1, 1, 0),
    (UPDATE_OWNER_RESULT_3, UPDATE_OWNER_RESULT_4, 3, 1, 0, 0)
]
# testdata pattern is ({result1}, {result2}, {result_count}, {active_count}, {exempt_count}, {historical_count})
TEST_UPDATE_DATA_SERIAL = [
    (None, None, 1, 1, 0, 0),
    (UPDATE_SERIAL_RESULT_1, None, 1, 2, 0, 0),
    (UPDATE_SERIAL_RESULT_1, UPDATE_SERIAL_RESULT_2, 1, 3, 0, 0),
    (UPDATE_SERIAL_RESULT_1, UPDATE_SERIAL_RESULT_3, 2, 2, 0, 0),
    (UPDATE_SERIAL_RESULT_3, UPDATE_SERIAL_RESULT_4, 3, 1, 0, 0)
]
# testdata pattern is ({mhr_num}, {search_data}, {active_count}, {exempt_count}, {historical_count})
TEST_COLLAPSE_DATA = [
    ('091688', ORG_NAME_JSON_COLLAPSE, 1, 0, 2),
    ('005520', OWNER_NAME_JSON_COLLAPSE, 1, 0, 5),
    ('099327', SERIAL_NUMBER_JSON_COLLAPSE, 3, 0, 0)
]
# testdata pattern is ({mhr_num}, {status}, {city}, {serial}, {year}, {make}, {model}, {id}, {o_status})
TEST_MHR_NUMBER_DATA_DIRECT = [
    ('UT-001', 'ACTIVE', 'CITY', '003000ZA002783A', 2015, 'make', 'model', 200000000, 'ACTIVE'),
    ('JUNK01', 'ACTIVE', 'CITY', '003000ZA002783A', 2015, 'make', 'model', 200000000, 'ACTIVE')
]
# testdata pattern is ({mhr_num}, {status}, {city}, {serial}, {year}, {make}, {model}, {id}, {o_status})
TEST_SERIAL_NUMBER_DATA_DIRECT = [
    ('UT-001', 'ACTIVE', 'CITY', '003000ZA002783A', 2015, 'make', 'model', 200000000, 'ACTIVE'),
    ('JUNK01', 'ACTIVE', 'CITY', '9999999', 2015, 'make', 'model', 200000000, 'ACTIVE')
]
# testdata pattern is ({mhr_num}, {status}, {city}, {serial}, {year}, {id}, {criteria}, {bus_name}, {o_status})
TEST_OWNER_BUS_DATA_DIRECT = [
    ('UT-001', 'ACTIVE', 'CITY', '003000ZA002783A', 2015, 200000000, 'REAL', 'REAL ENGINEERED HOMES INC', 'ACTIVE'),
    ('JUNK01', 'ACTIVE', 'CITY', '9999999', 2015, 200000000, 'JUNK NON-EXISTENT', None, 'ACTIVE')
]
# testdata pattern is ({mhr_num}, {status}, {city}, {serial}, {year}, {id}, {criteria}, {last}, {first}, {middle}, {o_status})
TEST_OWNER_IND_DATA_DIRECT = [
    ('UT-001', 'ACTIVE', 'CITY', '003000ZA002783A', 2015, 200000000, OWNER_NAME_VALID_JSON, 'MCKAY', 'BOB', 'ARTHUR',
     'ACTIVE'),
    ('JUNK01', 'ACTIVE', 'CITY', '9999999', 2015, 200000000, OWNER_NAME_NONE_JSON, None, None, None, 'ACTIVE')
]


def test_search_no_account(session):
    """Assert that a search query with no account id returns the expected result."""
    json_data = copy.deepcopy(MHR_NUMBER_JSON)
    query = SearchRequest.create_from_json(json_data, None)
    query.search()

    assert query.id
    assert query.search_response


@pytest.mark.parametrize('search_type,json_data', TEST_VALID_DATA)
def test_search_valid(session, search_type, json_data):
    """Assert that a valid search returns the expected search type result."""
    test_data = copy.deepcopy(json_data)
    test_data['type'] = model_utils.TO_DB_SEARCH_TYPE[json_data['type']]
    SearchRequest.validate_query(test_data)
    # current_app.logger.info('type=' + str(json_data['type']))
    query: SearchRequest = SearchRequest.create_from_json(json_data, 'PS12345', 'UNIT_TEST')
    query.search()
    assert not query.updated_selection
    result = query.json
    current_app.logger.debug('Results size:' + str(result['totalResultsSize']))
    assert query.id
    assert query.search_response
    assert query.account_id == 'PS12345'
    assert query.user_id == 'UNIT_TEST'
    assert result['searchId']
    assert result['searchQuery']
    assert result['searchDateTime']
    assert result['totalResultsSize']
    assert result['maxResultsSize']
    assert result['returnedResultsSize']
    assert len(result['results']) >= 1
    for match in result['results']:
        assert match['mhrNumber']
        if match['mhrNumber'] != '089036':  # bogus incomplete data
            assert match['status']
            assert match.get('activeCount') >= 0
            assert match.get('exemptCount') >= 0
            assert match.get('historicalCount') >= 0
            assert match['createDateTime']
            assert match['homeLocation']
            assert match['serialNumber']
            assert match['baseInformation']
            assert 'year' in match['baseInformation']
            assert 'make' in match['baseInformation']
            assert match['baseInformation']['model'] is not None
            assert 'organizationName' in match or 'ownerName' in match
            if match.get('ownerName'):
                assert match['ownerName']['first']
                assert match['ownerName']['last']
            assert match['ownerStatus'] in ('ACTIVE', 'EXEMPT', 'PREVIOUS')


@pytest.mark.parametrize('search_type,json_data', TEST_NONE_DATA)
def test_search_no_results(session, search_type, json_data):
    """Assert that a search query with no results returns the expected result."""
    query: SearchRequest = SearchRequest.create_from_json(json_data, None)
    query.search()

    assert query.id
    assert not query.search_response
    assert query.returned_results_size == 0


def test_create_from_json(session):
    """Assert that the search_client creates from a json format correctly."""
    json_data = copy.deepcopy(MHR_NUMBER_JSON)
    search_client = SearchRequest.create_from_json(json_data, 'PS12345', 'USERID')

    assert search_client.account_id == 'PS12345'
    assert search_client.search_type == 'MM'
    assert search_client.client_reference_id == 'T-SQ-MH-1'
    assert search_client.search_ts
    assert search_client.search_criteria
    assert search_client.user_id == 'USERID'


@pytest.mark.parametrize('search_type,json_data', TEST_INVALID_DATA)
def test_search_invalid_criteria_400(session, client, jwt, search_type, json_data):
    """Assert that validation of a search request with invalid criteria throws a BusinessException."""
    test_data = copy.deepcopy(json_data)
    test_data['type'] = model_utils.TO_DB_SEARCH_TYPE[json_data['type']]
    # test
    with pytest.raises(BusinessException) as bad_request_err:
        SearchRequest.validate_query(test_data)

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    # print(bad_request_err.value.error)


@pytest.mark.parametrize('mhr_number,expected_number', TEST_MHR_NUMBER_DATA)
def test_search_mhr_number(session, mhr_number, expected_number):
    """Assert that an mhr number search works with different values."""
    test_data = copy.deepcopy(MHR_NUMBER_JSON)
    test_data['criteria']['value'] = mhr_number

    format_test = copy.deepcopy(test_data)
    search_utils.format_mhr_number(format_test)
    assert format_test['criteria']['value'] == expected_number

    query: SearchRequest = SearchRequest.create_from_json(test_data, 'PS12345', 'UNIT_TEST')
    query.search()
    result = query.json
    # current_app.logger.debug(result)
    assert len(result['results']) >= 1
    assert result['results'][0]['mhrNumber'] == expected_number


@pytest.mark.parametrize('search_value,count,mhr1,result1,mhr2,result2', TEST_SERIAL_NUMBER_DATA)
def test_search_serial(session, search_value, count, mhr1, result1, mhr2, result2):
    """Assert that a valid search returns the expected serial number search result."""
    test_data = copy.deepcopy(SERIAL_NUMBER_JSON)
    test_data['criteria']['value'] = search_value

    query: SearchRequest = SearchRequest.create_from_json(test_data, 'PS12345', 'UNIT_TEST')
    query.search()
    assert not query.updated_selection
    result = query.json
    # current_app.logger.debug('Results size:' + str(result['totalResultsSize']))
    assert query.id
    if count < 1:
        assert not result.get('results')
    elif not model_utils.is_legacy():
        assert len(result['results']) >= count
        match_count = 0
        for match in result['results']:
            if match['mhrNumber'] == mhr1:
                match_count += 1
                assert match['serialNumber'].find(result1) != -1
            if mhr2 and result2 and match['mhrNumber'] == mhr2:
                assert match['serialNumber'].find(result2) != -1
        assert match_count > 0


@pytest.mark.parametrize('last_name,first_name,count', TEST_OWNER_IND_DATA)
def test_search_owner_ind(session, last_name, first_name, count):
    """Assert that a search by individual owner returns the expected result."""
    test_data = copy.deepcopy(OWNER_NAME_JSON)
    test_data['criteria']['ownerName']['last'] = last_name
    test_data['criteria']['ownerName']['first'] = first_name
    SearchRequest.validate_query(test_data)
    last: str = str(last_name).upper()

    query: SearchRequest = SearchRequest.create_from_json(test_data, 'PS12345', 'UNIT_TEST')
    query.search()
    assert not query.updated_selection
    result = query.json
    assert result['totalResultsSize'] >= count
    assert len(result.get('results')) >= count
    for match in result.get('results'):
        assert str(match['ownerName'].get('last')).startswith(last)


@pytest.mark.parametrize('result1,result2,result_count,active_count,exempt_count,historical_count',
                         TEST_UPDATE_DATA_ORG)
def test_update_result_org(session, result1, result2, result_count, active_count, exempt_count, historical_count):
    """Assert that a search consolidating/collapsing results works as expected."""
    results = copy.deepcopy(UPDATE_RESULTS_ORG_BASE)
    if result1:
        SearchRequest.update_result_matches(results, result1, SearchRequest.SearchTypes.ORGANIZATION_NAME)
    if result2:
        SearchRequest.update_result_matches(results, result2, SearchRequest.SearchTypes.ORGANIZATION_NAME)
    assert len(results) == result_count
    match = results[0]
    assert match.get('activeCount') == active_count
    assert match.get('exemptCount') == exempt_count
    assert match.get('historicalCount') == historical_count


@pytest.mark.parametrize('result1,result2,result_count,active_count,exempt_count,historical_count',
                         TEST_UPDATE_DATA_OWNER)
def test_update_result_owner(session, result1, result2, result_count, active_count, exempt_count, historical_count):
    """Assert that a search consolidating/collapsing results works as expected."""
    results = copy.deepcopy(UPDATE_RESULTS_OWNER_BASE)
    if result1:
        SearchRequest.update_result_matches(results, result1, SearchRequest.SearchTypes.OWNER_NAME)
    if result2:
        SearchRequest.update_result_matches(results, result2, SearchRequest.SearchTypes.OWNER_NAME)
    assert len(results) == result_count
    match = results[0]
    assert match.get('activeCount') == active_count
    assert match.get('exemptCount') == exempt_count
    assert match.get('historicalCount') == historical_count


@pytest.mark.parametrize('result1,result2,result_count,active_count,exempt_count,historical_count',
                         TEST_UPDATE_DATA_SERIAL)
def test_update_result_serial(session, result1, result2, result_count, active_count, exempt_count, historical_count):
    """Assert that a search consolidating/collapsing results works as expected."""
    results = copy.deepcopy(UPDATE_RESULTS_SERIAL_BASE)
    if result1:
        SearchRequest.update_result_matches(results, result1, SearchRequest.SearchTypes.SERIAL_NUM)
    if result2:
        SearchRequest.update_result_matches(results, result2, SearchRequest.SearchTypes.SERIAL_NUM)
    assert len(results) == result_count
    match = results[0]
    assert match.get('activeCount') == active_count
    assert match.get('exemptCount') == exempt_count
    assert match.get('historicalCount') == historical_count


@pytest.mark.parametrize('mhr_num,json_data,active_count,exempt_count,historical_count', TEST_COLLAPSE_DATA)
def test_search_collapse(session, mhr_num, json_data, active_count, exempt_count, historical_count):
    """Assert that a search returns the expected result with multiple matches within an MH registration."""
    test_data = copy.deepcopy(json_data)
    test_data['type'] = model_utils.TO_DB_SEARCH_TYPE[json_data['type']]
    # current_app.logger.info('type=' + str(json_data['type']))
    query: SearchRequest = SearchRequest.create_from_json(json_data, 'PS12345', 'UNIT_TEST')
    query.search()
    assert not query.updated_selection
    result = query.json
    # current_app.logger.debug('Results size:' + str(result['totalResultsSize']))
    assert len(result['results']) >= 1
    for match in result['results']:
        if match['mhrNumber'] == mhr_num:
            assert match.get('activeCount') == active_count
            assert match.get('exemptCount') == exempt_count
            assert match.get('historicalCount') == historical_count


@pytest.mark.parametrize('mhr_num,status,city,serial,year,make,model,id,o_status', TEST_MHR_NUMBER_DATA_DIRECT)
def test_search_mhr_number_direct(session, mhr_num, status, city, serial, year, make, model, id, o_status):
    """Assert that a success mhr number search works as expected."""
    test_data = copy.deepcopy(MHR_NUMBER_JSON)
    test_data['criteria']['value'] = mhr_num

    query: SearchRequest = SearchRequest.create_from_json(test_data, 'PS12345', 'UNIT_TEST')
    query.search_by_mhr_number()
    results = query.json
    if mhr_num == 'JUNK01':
        assert results['totalResultsSize'] == 0
        assert results['returnedResultsSize'] == 0
        assert not results.get('results')
    else:
        assert results['totalResultsSize'] == 1
        assert results['returnedResultsSize'] == 1
        assert results.get('maxResultsSize')
        assert results.get('searchId')
        assert results.get('searchDateTime')
        assert results.get('searchQuery')
        assert results.get('results')
        assert len(results['results']) == 1
        result = results['results'][0]
        assert result.get('mhrNumber') == mhr_num
        assert result.get('status') == status
        assert result.get('homeLocation') == city
        assert result.get('serialNumber') == serial
        assert result.get('baseInformation')
        assert result['baseInformation'].get('year') == year
        assert result['baseInformation'].get('make') == make
        assert result['baseInformation'].get('model') == model
        assert result.get('mhId') == id
        if o_status == 'ACTIVE':
            assert result.get('activeCount') == 1
        elif o_status == 'EXEMPT':
            assert result.get('exemptCount') == 1
        elif o_status == 'PREVIOUS':
            assert result.get('historicalCount') == 1


@pytest.mark.parametrize('mhr_num,status,city,serial,year,make,model,id,o_status', TEST_SERIAL_NUMBER_DATA_DIRECT)
def test_search_serial_number_direct(session, mhr_num, status, city, serial, year, make, model, id, o_status):
    """Assert that a serial number search works as expected."""
    test_data = copy.deepcopy(SERIAL_NUMBER_JSON)
    test_data['criteria']['value'] = serial

    query: SearchRequest = SearchRequest.create_from_json(test_data, 'PS12345', 'UNIT_TEST')
    query.search_by_serial_number()
    results = query.json
    if mhr_num == 'JUNK01':
        assert results['totalResultsSize'] == 0
        assert results['returnedResultsSize'] == 0
        assert not results.get('results')
    else:
        assert results['totalResultsSize'] == 1
        assert results['returnedResultsSize'] == 1
        assert results.get('maxResultsSize')
        assert results.get('searchId')
        assert results.get('searchDateTime')
        assert results.get('searchQuery')
        assert results.get('results')
        assert len(results['results']) == 1
        result = results['results'][0]
        assert result.get('mhrNumber') == mhr_num
        assert result.get('status') == status
        assert result.get('homeLocation') == city
        assert result.get('serialNumber') == serial
        assert result.get('baseInformation')
        assert result['baseInformation'].get('year') == year
        assert result['baseInformation'].get('make') == make
        assert result['baseInformation'].get('model') == model
        assert result.get('mhId') == id
        if o_status == 'ACTIVE':
            assert result.get('activeCount') == 1
        elif o_status == 'EXEMPT':
            assert result.get('exemptCount') == 1
        elif o_status == 'PREVIOUS':
            assert result.get('historicalCount') == 1


@pytest.mark.parametrize('mhr_num,status,city,serial,year,id,criteria,bus_name,o_status', TEST_OWNER_BUS_DATA_DIRECT)
def test_search_owner_bus_direct(session, mhr_num, status, city, serial, year, id, criteria, bus_name, o_status):
    """Assert that a owner business name search works as expected."""
    test_data = copy.deepcopy(ORG_NAME_JSON)
    test_data['criteria']['value'] = criteria

    query: SearchRequest = SearchRequest.create_from_json(test_data, 'PS12345', 'UNIT_TEST')
    query.search_by_organization_name()
    results = query.json
    if mhr_num == 'JUNK01':
        assert results['totalResultsSize'] == 0
        assert results['returnedResultsSize'] == 0
        assert not results.get('results')
    else:
        assert results['totalResultsSize'] >= 1
        assert results['returnedResultsSize'] >= 1
        assert results.get('maxResultsSize')
        assert results.get('searchId')
        assert results.get('searchDateTime')
        assert results.get('searchQuery')
        assert results.get('results')
        assert len(results['results']) >= 1
        for result in results['results']:
            assert result.get('mhrNumber')
            if result.get('mhrNumber') == mhr_num:
                assert result.get('status') == status
                assert result.get('homeLocation') == city
                assert result.get('serialNumber') == serial
                assert result.get('baseInformation')
                assert result['baseInformation'].get('year') == year
                assert result.get('mhId') == id
                assert result.get('organizationName') == bus_name
                if o_status == 'ACTIVE':
                    assert result.get('activeCount') == 1
                elif o_status == 'EXEMPT':
                    assert result.get('exemptCount') == 1
                elif o_status == 'PREVIOUS':
                    assert result.get('historicalCount') == 1


@pytest.mark.parametrize('mhr_num,status,city,serial,year,id,criteria,last,first,middle,o_status',
                         TEST_OWNER_IND_DATA_DIRECT)
def test_search_owner_ind_direct(session, mhr_num, status, city, serial, year, id, criteria, last, first, middle,
                                 o_status):
    """Assert that a owner individual name search works as expected."""
    query: SearchRequest = SearchRequest.create_from_json(criteria, 'PS12345', 'UNIT_TEST')
    query.search_by_owner_name()
    results = query.json
    if mhr_num == 'JUNK01':
        assert results['totalResultsSize'] == 0
        assert results['returnedResultsSize'] == 0
        assert not results.get('results')
    else:
        assert results['totalResultsSize'] >= 1
        assert results['returnedResultsSize'] >= 1
        assert results.get('maxResultsSize')
        assert results.get('searchId')
        assert results.get('searchDateTime')
        assert results.get('searchQuery')
        assert results.get('results')
        assert len(results['results']) >= 1
        for result in results['results']:
            assert result.get('mhrNumber')
            if result.get('mhrNumber') == mhr_num:
                assert result.get('status') == status
                assert result.get('homeLocation') == city
                assert result.get('serialNumber') == serial
                assert result.get('baseInformation')
                assert result['baseInformation'].get('year') == year
                assert result.get('mhId') == id
                assert result.get('ownerName')
                assert result['ownerName'].get('last') == last
                assert result['ownerName'].get('first') == first
                if middle:
                    assert result['ownerName'].get('middle') == middle
                if o_status == 'ACTIVE':
                    assert result.get('activeCount') == 1
                elif o_status == 'EXEMPT':
                    assert result.get('exemptCount') == 1
                elif o_status == 'PREVIOUS':
                    assert result.get('historicalCount') == 1


def test_search_key(session):
    """Use to check the value of a specific serial number search key."""
    key1: str = search_utils.get_serial_number_key('0312269A')
    key2: str = search_utils.get_serial_number_key('0312269B')
    current_app.logger.info(f'key1={key1} key2={key2}')
    key1: str = search_utils.get_serial_number_key('003000ZA00S783A')
    key2: str = search_utils.get_serial_number_key('003000ZA00S7834')
    current_app.logger.info(f'key1={key1} key2={key2}')
