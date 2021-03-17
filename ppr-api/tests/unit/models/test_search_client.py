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
import json

import pytest

from ppr_api.models import SearchClient
from ppr_api.models.utils import now_ts_offset, format_ts
from ppr_api.exceptions import BusinessException


# Valid test search criteria
AIRCRAFT_DOT_AC_JSON = {
    'type': 'AIRCRAFT_DOT',
    'criteria': {
        'value': 'CFYXW'
    },
    'clientReferenceId': 'T-SQ-AC-1'
}
AIRCRAFT_DOT_AF_JSON = {
    'type': 'AIRCRAFT_DOT',
    'criteria': {
        'value': 'AF16031'
    },
    'clientReferenceId': 'T-SQ-AF-1'
}
MHR_NUMBER_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'value': '220000'
    },
    'clientReferenceId': 'T-SQ-MH-1'
}
REGISTRATION_NUMBER_JSON = {
    'type': 'REGISTRATION_NUMBER',
    'criteria': {
        'value': 'TEST0001'
    },
    'clientReferenceId': 'T-SQ-RG-3'
}
AMENDMENT_NUMBER_JSON = {
    'type': 'REGISTRATION_NUMBER',
    'criteria': {
        'value': 'TEST0007'
    },
    'clientReferenceId': 'T-SQ-RG-3'
}
CHANGE_NUMBER_JSON = {
    'type': 'REGISTRATION_NUMBER',
    'criteria': {
        'value': 'TEST0008'
    },
    'clientReferenceId': 'T-SQ-RG-3'
}
SERIAL_NUMBER_JSON = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'value': 'JU622994'
    },
    'clientReferenceId': 'T-SQ-SS-1'
}
INDIVIDUAL_DEBTOR_JSON = {
    'type': 'INDIVIDUAL_DEBTOR',
    'criteria': {
        'debtorName': {
            'last': 'Debtor',
            'first': 'Test Ind'
        }
    },
    'clientReferenceId': 'T-SQ-IS-1'
}
BUSINESS_DEBTOR_JSON = {
    'type': 'BUSINESS_DEBTOR',
    'criteria': {
        'debtorName': {
            'business': 'TEST BUS 2 DEBTOR'
        }
    },
    'clientReferenceId': 'T-SQ-DB-1'
}
# Invalid combination of search criteria
RG_INVALID_JSON = {
    'type': 'REGISTRATION_NUMBER',
    'criteria': {
        'debtorName': {
            'business': 'BROWN AUTOMOTIVE LTD.'
        }
    }
}
MH_INVALID_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'debtorName': {
            'business': 'BROWN AUTOMOTIVE LTD.'
        }
    }
}
AC_INVALID_JSON = {
    'type': 'AIRCRAFT_DOT',
    'criteria': {
        'debtorName': {
            'business': 'BROWN AUTOMOTIVE LTD.'
        }
    }
}
SS_INVALID_JSON = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'debtorName': {
            'business': 'BROWN AUTOMOTIVE LTD.'
        }
    }
}
IS_INVALID_JSON = {
    'type': 'INDIVIDUAL_DEBTOR',
    'criteria': {
        'debtorName': {
            'business': 'BROWN AUTOMOTIVE LTD.'
        }
    }
}
BS_INVALID_JSON = {
    'type': 'BUSINESS_DEBTOR',
    'criteria': {
        'debtorName': {
            'last': 'Smith',
            'first': 'John'
        }
    }
}

# Discharged financing statement criteria
BS_DISCHARGED_JSON = {
    'type': 'BUSINESS_DEBTOR',
    'criteria': {
        'debtorName': {
            'business': 'ZZZZZ99'
        }
    },
    'clientReferenceId': 'T-SQ-DB-4'
}
AC_DISCHARGED_JSON = {
    'type': 'AIRCRAFT_DOT',
    'criteria': {
        'value': 'ZZZZZ999999'
    },
    'clientReferenceId': 'T-SQ-AC-4'
}
SS_DISCHARGED_JSON = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'value': 'ZZZZZ999999'
    },
    'clientReferenceId': 'T-SQ-SS-4'
}
MH_DISCHARGED_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'value': '399999'
    },
    'clientReferenceId': 'T-SQ-MH-4'
}
RG_DISCHARGED_JSON = {
    'type': 'REGISTRATION_NUMBER',
    'criteria': {
        'value': 'TEST0014'
    },
    'clientReferenceId': 'T-SQ-RG-7'
}
IS_DISCHARGED_JSON = {
    'type': 'INDIVIDUAL_DEBTOR',
    'criteria': {
        'debtorName': {
            'last': 'TEST IND DEBTOR',
            'first': 'ZZZZZ99'
        }
    },
    'clientReferenceId': 'T-SQ-IS-3'
}
# Expired financing statement criteria
BS_EXPIRED_JSON = {
    'type': 'BUSINESS_DEBTOR',
    'criteria': {
        'debtorName': {
            'business': 'XXXXX99'
        }
    },
    'clientReferenceId': 'T-SQ-DB-4'
}
AC_EXPIRED_JSON = {
    'type': 'AIRCRAFT_DOT',
    'criteria': {
        'value': 'XXXXX999999'
    },
    'clientReferenceId': 'T-SQ-AC-4'
}
SS_EXPIRED_JSON = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'value': 'XXXXX999999'
    },
    'clientReferenceId': 'T-SQ-SS-4'
}
MH_EXPIRED_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'value': '299999'
    },
    'clientReferenceId': 'T-SQ-MH-4'
}
RG_EXPIRED_JSON = {
    'type': 'REGISTRATION_NUMBER',
    'criteria': {
        'value': 'TEST0013'
    },
    'clientReferenceId': 'T-SQ-RG-7'
}
IS_EXPIRED_JSON = {
    'type': 'INDIVIDUAL_DEBTOR',
    'criteria': {
        'debtorName': {
            'last': 'TEST IND DEBTOR',
            'first': 'XXXXX99'
        }
    },
    'clientReferenceId': 'T-SQ-IS-3'
}
# Test valid criteria with no results.
BS_NONE_JSON = {
    'type': 'BUSINESS_DEBTOR',
    'criteria': {
        'debtorName': {
            'business': 'XZXZXZXZ'
        }
    },
    'clientReferenceId': 'T-SQ-DB-4'
}
AC_NONE_JSON = {
    'type': 'AIRCRAFT_DOT',
    'criteria': {
        'value': 'TESTXXXX'
    },
    'clientReferenceId': 'T-SQ-AC-4'
}
SS_NONE_JSON = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'value': 'TESTXXXX'
    },
    'clientReferenceId': 'T-SQ-SS-4'
}
MH_NONE_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'value': '999999'
    },
    'clientReferenceId': 'T-SQ-MH-4'
}
RG_NONE_JSON = {
    'type': 'REGISTRATION_NUMBER',
    'criteria': {
        'value': 'TESTXXXX'
    },
    'clientReferenceId': 'T-SQ-RG-7'
}
IS_NONE_JSON = {
    'type': 'INDIVIDUAL_DEBTOR',
    'criteria': {
        'debtorName': {
            'last': 'TEST IND DEBTOR',
            'first': 'XZXZXZXZ'
        }
    },
    'clientReferenceId': 'T-SQ-IS-3'
}

# testdata pattern is ({search type}, {JSON data})
TEST_VALID_DATA = [
    ('AC', AIRCRAFT_DOT_AC_JSON),
    ('AF', AIRCRAFT_DOT_AF_JSON),
    ('AM', AMENDMENT_NUMBER_JSON),
    ('CH', CHANGE_NUMBER_JSON),
    ('RG', REGISTRATION_NUMBER_JSON),
    ('MH', MHR_NUMBER_JSON),
    ('SS', SERIAL_NUMBER_JSON),
    ('IS', INDIVIDUAL_DEBTOR_JSON),
    ('BS', BUSINESS_DEBTOR_JSON)
]

# testdata pattern is ({search type}, {JSON data})
TEST_NONE_DATA = [
    ('RG', RG_NONE_JSON),
    ('MH', MH_NONE_JSON),
    ('AC', AC_NONE_JSON),
    ('SS', SS_NONE_JSON),
    ('IS', IS_NONE_JSON),
    ('BS', BS_NONE_JSON)
]

# testdata pattern is ({search type}, {JSON data})
TEST_INVALID_DATA = [
    ('RG', RG_INVALID_JSON),
    ('MH', MH_INVALID_JSON),
    ('AC', AC_INVALID_JSON),
    ('SS', SS_INVALID_JSON),
    ('IS', IS_INVALID_JSON),
    ('BS', BS_INVALID_JSON)
]

# testdata pattern is ({search type}, {JSON data}, {expected # of results})
TEST_VALID_DATA_COUNT = [
    ('SS', SERIAL_NUMBER_JSON, 7),
    ('IS', INDIVIDUAL_DEBTOR_JSON, 4),
    ('BS', BUSINESS_DEBTOR_JSON, 2)
]

# testdata pattern is ({search type}, {JSON data}, {excluded match criteria})
TEST_DISCHARGED_DATA = [
    ('RG', RG_DISCHARGED_JSON, 'TEST0014'),
    ('AC', SS_DISCHARGED_JSON, 'ZZZZZ999999'),
    ('MH', SS_DISCHARGED_JSON, 'ZZZZZ999999'),
    ('SS', SS_DISCHARGED_JSON, 'ZZZZZ999999'),
    ('IS', IS_DISCHARGED_JSON, 'ZZZZZ99'),
    ('BS', BS_DISCHARGED_JSON, 'ZZZZZ99')
]

# testdata pattern is ({search type}, {JSON data}, {excluded match criteria})
TEST_EXPIRED_DATA = [
    ('RG', RG_EXPIRED_JSON, 'TEST0013'),
    ('AC', SS_EXPIRED_JSON, 'XXXXX999999'),
    ('MH', SS_EXPIRED_JSON, 'XXXXX999999'),
    ('SS', SS_EXPIRED_JSON, 'XXXXX999999'),
    ('IS', IS_EXPIRED_JSON, 'XXXXX99'),
    ('BS', BS_EXPIRED_JSON, 'XXXXX99')
]


def test_search_no_account(session):
    """Assert that a search query with not account id returns the expected result."""
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'value': 'TEST0001'
        },
        'clientReferenceId': 'T-SQ-RG-4'
    }
    query = SearchClient.create_from_json(json_data, None)
    query.search()

    assert query.search_id
    assert query.search_response


@pytest.mark.parametrize('search_type,json_data', TEST_VALID_DATA)
def test_search_valid(session, search_type, json_data):
    """Assert that a valid search returns the expected search type result."""
    query = SearchClient.create_from_json(json_data, None)
    query.search()

    result = query.json
#    print(result)
    assert query.search_id
    assert query.search_response
    assert result['searchId']
    assert result['searchQuery']
    assert result['searchDateTime']
    assert result['totalResultsSize']
    assert result['maxResultsSize']
    assert result['returnedResultsSize']
    assert len(result['results']) >= 1
    assert result['results'][0]['baseRegistrationNumber']
    assert result['results'][0]['createDateTime']
    assert result['results'][0]['matchType'] == 'EXACT'
    assert result['results'][0]['registrationType']
    if search_type == 'BS':
        assert result['results'][0]['debtor']
        assert result['results'][0]['debtor']['businessName'] == 'TEST BUS 2 DEBTOR'
    elif search_type == 'IS':
        assert result['results'][0]['debtor']
        assert result['results'][0]['debtor']['personName']
        assert result['results'][0]['debtor']['personName']['last'] == 'DEBTOR'
        assert result['results'][0]['debtor']['personName']['first'] == 'TEST IND'
    elif search_type == 'AM':
        assert result['results'][0]['baseRegistrationNumber'] == 'TEST0001'
        assert result['results'][0]['registrationNumber'] == 'TEST0007'
    elif search_type == 'CH':
        assert result['results'][0]['baseRegistrationNumber'] == 'TEST0001'
        assert result['results'][0]['registrationNumber'] == 'TEST0008'
    elif search_type == 'RG':
        assert result['results'][0]['baseRegistrationNumber'] == 'TEST0001'
    else:
        assert result['results'][0]['vehicleCollateral']
        assert result['results'][0]['vehicleCollateral']['year']
        assert result['results'][0]['vehicleCollateral']['make']
        assert result['results'][0]['vehicleCollateral']['serialNumber']
        if search_type != 'MH':
            assert result['results'][0]['vehicleCollateral']['model']
        if search_type == 'AF':
            assert result['results'][0]['vehicleCollateral']['type'] == 'AF'
            assert result['results'][0]['vehicleCollateral']['serialNumber'] == 'AF16031'
        elif search_type == 'AC':
            assert result['results'][0]['vehicleCollateral']['type'] == 'AC'
            assert result['results'][0]['vehicleCollateral']['serialNumber'] == 'CFYXW'
        elif search_type == 'MH':
            assert result['results'][0]['vehicleCollateral']['manufacturedHomeRegistrationNumber'] == '220000'


@pytest.mark.parametrize('search_type,json_data', TEST_NONE_DATA)
def test_search_no_results(session, search_type, json_data):
    """Assert that a search query with no results returns the expected result."""
    query = SearchClient.create_from_json(json_data, None)
    query.search()

    assert query.search_id
    assert not query.search_response
    assert query.returned_results_size == 0


@pytest.mark.parametrize('search_type,json_data,excluded_match', TEST_EXPIRED_DATA)
def test_search_expired(session, search_type, json_data, excluded_match):
    """Assert that an expired financing statement is excluded from the search results."""
    query = SearchClient.create_from_json(json_data, None)
    query.search()
    result = query.json

    assert result['searchId']
    if search_type == 'RG':
        assert not query.search_response
        assert query.returned_results_size == 0
    elif 'results' in result:
        for r in result['results']:
            if search_type == 'BS':
                assert r['debtor']['businessName'] != excluded_match
            elif search_type == 'IS':
                assert r['debtor']['personName']['first'] != excluded_match
            else:
                assert r['vehicleCollateral']['serialNumber'] != excluded_match


@pytest.mark.parametrize('search_type,json_data,excluded_match', TEST_DISCHARGED_DATA)
def test_search_discharged(session, search_type, json_data, excluded_match):
    """Assert that a discharged financing statement is excluded from the search results."""
    query = SearchClient.create_from_json(json_data, None)
    query.search()
    result = query.json

    assert result['searchId']
    if search_type == 'RG':
        assert not query.search_response
        assert query.returned_results_size == 0
    elif 'results' in result:
        for r in result['results']:
            if search_type == 'BS':
                assert r['debtor']['businessName'] != excluded_match
            elif search_type == 'IS':
                assert r['debtor']['personName']['first'] != excluded_match
            else:
                assert r['vehicleCollateral']['serialNumber'] != excluded_match


def test_search_startdatetime_invalid(session, client, jwt):
    """Assert that validation of a search with an invalid startDateTime throws a BusinessException."""
    # setup
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'value': 'TEST0001'
        },
        'clientReferenceId': 'T-API-SQ-RG-7',
        'endDateTime': '2021-01-20T19:38:43+00:00'
    }
    ts_start = now_ts_offset(1, True)
    json_data['startDateTime'] = format_ts(ts_start)

    # test
    with pytest.raises(BusinessException) as bad_request_err:
        SearchClient.validate_query(json_data)

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    print(bad_request_err.value.error)


def test_search_enddatatetime_invalid(session, client, jwt):
    """Assert that validation of a search with an invalid endDateTime throws a BusinessException."""
    # setup
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'value': 'TEST0001'
        },
        'clientReferenceId': 'T-API-SQ-RG-8',
        'startDateTime': '2021-01-20T19:38:43+00:00'
    }
    ts_end = now_ts_offset(1, True)
    json_data['endDateTime'] = format_ts(ts_end)

    # test
    with pytest.raises(BusinessException) as bad_request_err:
        SearchClient.validate_query(json_data)

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    print(bad_request_err.value.error)


def test_find_by_account_id(session):
    """Assert that the account search history list first item contains all expected elements."""
    history = SearchClient.find_all_by_account_id('PS12345')
    print(history)
    assert history
    assert history[0]['searchId']
    assert history[0]['searchDateTime']
    assert history[0]['totalResultsSize']
    assert history[0]['returnedResultsSize']
    assert history[0]['searchQuery']
    assert len(history) >= 2


def test_find_by_account_id_no_result(session):
    """Assert that the find draft statement by invalid account ID returns the expected result."""
    with pytest.raises(BusinessException) as not_found_err:
        SearchClient.find_all_by_account_id('X12345X')

    # check
    assert not_found_err
    assert not_found_err.value.status_code == HTTPStatus.NOT_FOUND


def test_create_from_json(session):
    """Assert that the search_client creates from a json format correctly."""
    json_data = {
        'type': 'SERIAL_NUMBER',
        'criteria': {
            'value': 'JU622994'
        },
        'clientReferenceId': 'T-SQ-SS-1'
    }
    search_client = SearchClient.create_from_json(json_data, 'PS12345')

    assert search_client.account_id == 'PS12345'
    assert search_client.search_type_cd == 'SS'
    assert search_client.client_reference_id == 'T-SQ-SS-1'
    assert search_client.search_ts
    assert search_client.search_criteria


def test_search_autosave(session):
    """Assert that a valid search query selection update works as expected."""
    query = SearchClient.find_by_id(200000000)
    assert query.search_response
    update_data = json.loads(query.search_response)
    if update_data[0]['matchType'] == 'EXACT':
        update_data[0]['matchType'] = 'SIMILAR'
    else:
        update_data[0]['matchType'] = 'EXACT'

    query.update_search_selection(update_data)
    json_data = query.json
    assert json_data['results'][0]['matchType'] == update_data[0]['matchType']


@pytest.mark.parametrize('search_type,json_data', TEST_INVALID_DATA)
def test_search_invalid_criteria_400(session, client, jwt, search_type, json_data):
    """Assert that validation of a search request with invalid criteria throws a BusinessException."""
    # test
    with pytest.raises(BusinessException) as bad_request_err:
        SearchClient.validate_query(json_data)

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    # print(bad_request_err.value.error)


@pytest.mark.parametrize('search_type,json_data,result_size', TEST_VALID_DATA_COUNT)
def test_get_total_count(session, search_type, json_data, result_size):
    """Assert that the get total count function works as expected."""
    search_client = SearchClient.create_from_json(json_data, 'PS12345')
    search_client.get_total_count()
    # print('test_total_count ' + search_type + ' actual results size=' + str(search_client.total_results_size))
    assert search_client.total_results_size >= result_size
