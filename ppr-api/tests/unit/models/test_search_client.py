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

import pytest

from ppr_api.models import SearchClient, Registration
from ppr_api.models.utils import now_ts_offset, format_ts
from ppr_api.exceptions import BusinessException

import copy
from registry_schemas.example_data.ppr import SEARCH_QUERY, SEARCH_SUMMARY


def test_search_reg_num_financing(session):
    """Assert that a search query by financing statement registration number 
       returns the expected result."""
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'value': 'TEST0001'
        },
        'clientReferenceId': 'T-SQ-RG-1'
    }
    query = SearchClient.create_from_json(json_data, 'PS12345')
    query.search()

    result = query.json
#    print(result)
    assert query.search_id
    assert query.search_response
    assert result['searchId']
    assert result['searchQuery']
    assert result['searchDateTime']
    assert result['totalResultsSize'] == 1
    assert result['returnedResultsSize'] == 1
    assert result['maxResultsSize'] == 1000
    assert result['results'][0]
    assert result['results'][0]['baseRegistrationNumber'] == 'TEST0001'
    assert result['results'][0]['createDateTime']
    assert result['results'][0]['matchType'] == 'EXACT'
    assert result['results'][0]['registrationType']


def test_search_reg_num_amendment(session):
    """Assert that a search query by amendment statement registration number 
       returns the expected result."""
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'value': 'TEST0007'
        },
        'clientReferenceId': 'T-SQ-RG-2'
    }
    query = SearchClient.create_from_json(json_data, 'PS12345')
    query.search()

    result = query.json
#    print(result)
    assert query.search_id
    assert query.search_response
    assert result['searchId']
    assert result['searchQuery']
    assert result['searchDateTime']
    assert result['totalResultsSize'] == 1
    assert result['returnedResultsSize'] == 1
    assert result['maxResultsSize'] == 1000
    assert result['results'][0]
    assert result['results'][0]['baseRegistrationNumber'] == 'TEST0001'
    assert result['results'][0]['registrationNumber'] == 'TEST0007'
    assert result['results'][0]['createDateTime']
    assert result['results'][0]['matchType'] == 'EXACT'
    assert result['results'][0]['registrationType']


def test_search_reg_num_change(session):
    """Assert that a search query by change statement registration number 
       returns the expected result."""
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'value': 'TEST0008'
        },
        'clientReferenceId': 'T-SQ-RG-3'
    }
    query = SearchClient.create_from_json(json_data, 'PS12345')
    query.search()

    result = query.json
#    print(result)
    assert query.search_id
    assert query.search_response
    assert result['searchId']
    assert result['searchQuery']
    assert result['searchDateTime']
    assert result['totalResultsSize'] == 1
    assert result['returnedResultsSize'] == 1
    assert result['maxResultsSize'] == 1000
    assert result['results'][0]
    assert result['results'][0]['baseRegistrationNumber'] == 'TEST0001'
    assert result['results'][0]['registrationNumber'] == 'TEST0008'
    assert result['results'][0]['createDateTime']
    assert result['results'][0]['matchType'] == 'EXACT'
    assert result['results'][0]['registrationType']


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


def test_search_mhr_num(session):
    """Assert that a search query by mhr number returns the expected result."""
    json_data = {
        'type': 'MHR_NUMBER',
        'criteria': {
            'value': '220000'
        },
        'clientReferenceId': 'T-SQ-MH-1'
    }
    query = SearchClient.create_from_json(json_data, 'PS12345')
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
    assert result['results'][0]
    assert result['results'][0]['baseRegistrationNumber']
    assert result['results'][0]['createDateTime']
    assert result['results'][0]['matchType']
    assert result['results'][0]['registrationType']
    assert result['results'][0]['vehicleCollateral']
    assert result['results'][0]['vehicleCollateral']['type']
    assert result['results'][0]['vehicleCollateral']['serialNumber']
    assert result['results'][0]['vehicleCollateral']['year']
    assert result['results'][0]['vehicleCollateral']['make']
    assert result['results'][0]['vehicleCollateral']['manufacturedHomeRegistrationNumber'] == '220000'
    if len(result['results']) > 0:
        assert result['results'][1]['vehicleCollateral']['manufacturedHomeRegistrationNumber'] == '220000'

    # Test no partial match: 22000 and 220000 exist, 22000 search should not return 220000
    json_data['criteria']['value'] = '22000'
    query = SearchClient.create_from_json(json_data, 'PS12345')
    query.search()

    result = query.json
    assert result['results'][0]
    for r in result['results']:
      assert r['vehicleCollateral']['manufacturedHomeRegistrationNumber'] == '22000'


def test_search_serial_num(session):
    """Assert that a search query by serial number returns the expected result."""
    json_data = {
        'type': 'SERIAL_NUMBER',
        'criteria': {
            'value': 'JU622994'
        },
        'clientReferenceId': 'T-SQ-SS-1'
    }
    query = SearchClient.create_from_json(json_data, 'PS12345')
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
    assert len(result['results']) >= 4
    assert result['results'][0]['baseRegistrationNumber']
    assert result['results'][0]['createDateTime']
    assert result['results'][0]['matchType']
    assert result['results'][0]['registrationType']
    assert result['results'][0]['vehicleCollateral']
    assert result['results'][0]['vehicleCollateral']['type']
    assert result['results'][0]['vehicleCollateral']['serialNumber']
    assert result['results'][0]['vehicleCollateral']['year']
    assert result['results'][0]['vehicleCollateral']['make']


def test_search_aircraft_dot_AC(session):
    """Assert that a search query by aircraft DOT returns the expected AC serial type result."""
    json_data = {
        'type': 'AIRCRAFT_DOT',
        'criteria': {
            'value': 'CFYXW'
        },
        'clientReferenceId': 'T-SQ-AC-1'
    }
    query = SearchClient.create_from_json(json_data, 'PS12345')
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
    assert result['results'][0]['vehicleCollateral']
    assert result['results'][0]['vehicleCollateral']['type'] == 'AC'
    assert result['results'][0]['vehicleCollateral']['serialNumber'] == 'CFYXW'
    assert result['results'][0]['vehicleCollateral']['year']
    assert result['results'][0]['vehicleCollateral']['make']
    assert result['results'][0]['vehicleCollateral']['model']


def test_search_aircraft_dot_AF(session):
    """Assert that a search query by aircraft DOT returns the expected AF serial type result."""
    json_data = {
        'type': 'AIRCRAFT_DOT',
        'criteria': {
            'value': 'AF16031'
        },
        'clientReferenceId': 'T-SQ-AF-1'
    }
    query = SearchClient.create_from_json(json_data, 'PS12345')
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
    assert result['results'][0]['vehicleCollateral']
    assert result['results'][0]['vehicleCollateral']['type'] == 'AF'
    assert result['results'][0]['vehicleCollateral']['serialNumber'] == 'AF16031'
    assert result['results'][0]['vehicleCollateral']['year']
    assert result['results'][0]['vehicleCollateral']['make']
    assert result['results'][0]['vehicleCollateral']['model']


def test_search_debtor_bus(session):
    """Assert that a search by debtor business name returns the expected BS serial
       type result."""
    json_data = {
        'type': 'BUSINESS_DEBTOR',
        'criteria': {
            'debtorName': {
                'business': 'TEST BUS 2 DEBTOR'
            }
        },
        'clientReferenceId': 'T-SQ-DB-1'
    }
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
    assert result['results'][0]['debtor']
    assert result['results'][0]['debtor']['businessName'] == 'TEST BUS 2 DEBTOR'


def test_search_reg_num_none(session):
    """Assert that a search by registration number query with no results 
       returns the expected result."""
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'value': 'TESTXXXX'
        },
        'clientReferenceId': 'T-SQ-RG-5'
    }
    query = SearchClient.create_from_json(json_data, None)
    query.search()

    assert query.search_id
    assert not query.search_response
    assert query.returned_results_size == 0


def test_search_mhr_num_none(session):
    """Assert that a search by mhr number query with no results 
       returns the expected result."""
    json_data = {
        'type': 'MHR_NUMBER',
        'criteria': {
            'value': '999999'
        },
        'clientReferenceId': 'T-SQ-MH-2'
    }
    query = SearchClient.create_from_json(json_data, None)
    query.search()

    assert query.search_id
    assert not query.search_response
    assert query.returned_results_size == 0

    # Verify partial match fails
    json_data['criteria']['value'] = '2200'
    query = SearchClient.create_from_json(json_data, None)
    query.search()

    assert query.search_id
    assert not query.search_response
    assert query.returned_results_size == 0


def test_search_serial_num_none(session):
    """Assert that a search by serial number query with no results 
       returns the expected result."""
    json_data = {
        'type': 'SERIAL_NUMBER',
        'criteria': {
            'value': 'TESTXXXX'
        },
        'clientReferenceId': 'T-SQ-SS-2'
    }
    query = SearchClient.create_from_json(json_data, None)
    query.search()

    assert query.search_id
    assert not query.search_response
    assert query.returned_results_size == 0


def test_search_aircraft_dot_none(session):
    """Assert that a search by aircraft DOT query with no results 
       returns the expected result."""
    json_data = {
        'type': 'AIRCRAFT_DOT',
        'criteria': {
            'value': 'TESTXXXX'
        },
        'clientReferenceId': 'T-SQ-AC-2'
    }
    query = SearchClient.create_from_json(json_data, None)
    query.search()

    assert query.search_id
    assert not query.search_response
    assert query.returned_results_size == 0


def test_search_debtor_bus_none(session):
    """Assert that a search by debtor business name query with no results 
       returns the expected result."""
    json_data = {
        'type': 'BUSINESS_DEBTOR',
        'criteria': {
            'debtorName': {
                'business': 'XZXZXZXZ'
            }
        },
        'clientReferenceId': 'T-SQ-DB-2'
    }
    query = SearchClient.create_from_json(json_data, None)
    query.search()

    assert query.search_id
    assert not query.search_response
    assert query.returned_results_size == 0


def test_search_reg_num_expired(session):
    """Assert that a search by registration number on an expired financing statement is 
       excluded in the results."""
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'value': 'TEST0013'
        },
        'clientReferenceId': 'T-SQ-RG-6'
    }
    query = SearchClient.create_from_json(json_data, None)
    query.search()

    assert query.search_id
    assert not query.search_response
    assert query.returned_results_size == 0


def test_search_mhr_number_expired(session):
    """Assert that a search by MHR number on an expired financing statement is 
       excluded in the results."""
    json_data = {
        'type': 'MHR_NUMBER',
        'criteria': {
            'value': '299999'
        },
        'clientReferenceId': 'T-SQ-MH-3'
    }
    query = SearchClient.create_from_json(json_data, None)
    query.search()
    result = query.json

    assert result['searchId']
    if 'results' in result:
        for r in result['results']:
            assert r['vehicleCollateral']['serialNumber'] != 'XXXXX999999'


def test_search_serial_number_expired(session):
    """Assert that a search by serial number on an expired financing statement is 
       excluded in the results."""
    json_data = {
        'type': 'SERIAL_NUMBER',
        'criteria': {
            'value': 'XXXXX999999'
        },
        'clientReferenceId': 'T-SQ-SS-3'
    }
    query = SearchClient.create_from_json(json_data, None)
    query.search()
    result = query.json

    assert result['searchId']
    if 'results' in result:
        for r in result['results']:
            assert r['vehicleCollateral']['serialNumber'] != 'XXXXX999999'


def test_search_aircraft_dot_expired(session):
    """Assert that a search by aircraft DOT on an expired financing statement is 
       excluded in the results."""
    json_data = {
        'type': 'AIRCRAFT_DOT',
        'criteria': {
            'value': 'XXXXX999999'
        },
        'clientReferenceId': 'T-SQ-AC-3'
    }
    query = SearchClient.create_from_json(json_data, None)
    query.search()
    result = query.json

    assert result['searchId']
    if 'results' in result:
        for r in result['results']:
            assert r['vehicleCollateral']['serialNumber'] != 'XXXXX999999'


def test_search_debtor_bus_expired(session):
    """Assert that a search by debtor business name on an expired financing statement
       is excluded from the result."""
    json_data = {
        'type': 'BUSINESS_DEBTOR',
        'criteria': {
            'debtorName': {
                'business': 'XXXXX99'
            }
        },
        'clientReferenceId': 'T-SQ-DB-3'
    }
    query = SearchClient.create_from_json(json_data, None)
    query.search()
    result = query.json

    assert result['searchId']
    if 'results' in result:
        for r in result['results']:
            assert r['debtor']['businessName'] != 'XXXXX99'


def test_search_reg_num_discharged(session):
    """Assert that a search by registration number on a discharged financing statement is 
       excluded in the results."""
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'value': 'TEST0014'
        },
        'clientReferenceId': 'T-SQ-RG-7'
    }
    query = SearchClient.create_from_json(json_data, None)
    query.search()

    assert query.search_id
    assert not query.search_response
    assert query.returned_results_size == 0


def test_search_mhr_number_discharged(session):
    """Assert that a search by MHR number on a discharged financing statement is 
       excluded in the results."""
    json_data = {
        'type': 'MHR_NUMBER',
        'criteria': {
            'value': '399999'
        },
        'clientReferenceId': 'T-SQ-MH-4'
    }
    query = SearchClient.create_from_json(json_data, None)
    query.search()
    result = query.json

    assert result['searchId']
    if 'results' in result:
        for r in result['results']:
            assert r['vehicleCollateral']['serialNumber'] != 'ZZZZZ999999'


def test_search_serial_number_discharged(session):
    """Assert that a search by serial number on a discharged financing statement is 
       excluded in the results."""
    json_data = {
        'type': 'SERIAL_NUMBER',
        'criteria': {
            'value': 'ZZZZZ999999'
        },
        'clientReferenceId': 'T-SQ-SS-4'
    }
    query = SearchClient.create_from_json(json_data, None)
    query.search()
    result = query.json

    assert result['searchId']
    if 'results' in result:
        for r in result['results']:
            assert r['vehicleCollateral']['serialNumber'] != 'ZZZZZ999999'


def test_search_aircraft_dot_discharged(session):
    """Assert that a search by aircraft DOT on a discarged financing statement is 
       excluded in the results."""
    json_data = {
        'type': 'AIRCRAFT_DOT',
        'criteria': {
            'value': 'ZZZZZ999999'
        },
        'clientReferenceId': 'T-SQ-AC-4'
    }
    query = SearchClient.create_from_json(json_data, None)
    query.search()
    result = query.json

    assert result['searchId']
    if 'results' in result:
        for r in result['results']:
            assert r['vehicleCollateral']['serialNumber'] != 'XXXXX999999'


def test_search_debtor_bus_discharged(session):
    """Assert that a search by debtor business name on a discharged financing statement
       is excluded from the results."""
    json_data = {
        'type': 'BUSINESS_DEBTOR',
        'criteria': {
            'debtorName': {
                'business': 'ZZZZZ99'
            }
        },
        'clientReferenceId': 'T-SQ-DB-4'
    }
    query = SearchClient.create_from_json(json_data, None)
    query.search()
    result = query.json

    assert result['searchId']
    if 'results' in result:
        for r in result['results']:
            assert r['debtor']['businessName'] != 'ZZZZZ99'


def test_search_startDateTime_invalid(session, client, jwt):
    """Assert that validation of a search request with an invalid startDateTime 
       throws a BusinessException."""
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
    json_data['startDateTime'] =  format_ts(ts_start)

    # test
    with pytest.raises(BusinessException) as bad_request_err:
        SearchClient.validate_query(json_data)

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    print(bad_request_err.value.error)


def test_search_endDateTime_invalid(session, client, jwt):
    """Assert that validation of a search request with an invalid endDateTime 
       throws a BusinessException."""
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
    json_data['endDateTime'] =  format_ts(ts_end)

    # test
    with pytest.raises(BusinessException) as bad_request_err:
        SearchClient.validate_query(json_data)

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    print(bad_request_err.value.error)

def test_search_SS_invalid_criteria(session, client, jwt):
    """Assert that validation of a serial number search request with invalid criteria 
       throws a BusinessException."""
    # setup
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'debtorName': {
                'business': 'BROWN AUTOMOTIVE LTD.'
            }
       }
    }

    # test
    with pytest.raises(BusinessException) as bad_request_err:
        SearchClient.validate_query(json_data)

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    print(bad_request_err.value.error)


def test_search_IS_invalid_criteria(session, client, jwt):
    """Assert that validation of an individual debtor search request with invalid criteria 
       throws a BusinessException."""
    # setup
    json_data = {
        'type': 'INDIVIDUAL_DEBTOR',
        'criteria': {
            'debtorName': {
                'business': 'BROWN AUTOMOTIVE LTD.'
            }
       }
    }

    # test
    with pytest.raises(BusinessException) as bad_request_err:
        SearchClient.validate_query(json_data)

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    print(bad_request_err.value.error)


def test_search_BS_invalid_criteria(session, client, jwt):
    """Assert that validation of a business debtor search request with invalid criteria 
       throws a BusinessException."""
    # setup
    json_data = {
        'type': 'BUSINESS_DEBTOR',
        'criteria': {
            'debtorName': {
                'last': 'Smith',
                'first': 'John'
            }
       }
    }

    # test
    with pytest.raises(BusinessException) as bad_request_err:
        SearchClient.validate_query(json_data)

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    print(bad_request_err.value.error)


def test_find_by_account_id(session):
    """Assert that the account search history list first item contains all expected
       elements."""
    history = SearchClient.find_all_by_account_id('PS12345')
    assert history[0]['searchId']
    assert history[0]['searchDateTime']
    assert history[0]['totalResultsSize']
    assert history[0]['returnedResultsSize']
    assert history[0]['maxResultsSize']
    assert history[0]['searchQuery']
    assert history[0]['results']
    assert len(history) >= 3


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

