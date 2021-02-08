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
from ppr_api.utils.datetime import now_ts_offset, format_ts
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
    assert result['totalResultsSize']
    assert result['maxResultsSize']
    assert result['returnedResultsSize']
    assert result['results'][0]
    assert result['results'][0]['baseRegistrationNumber'] == 'TEST0001'
    assert result['results'][0]['createDateTime']
    assert result['results'][0]['matchType']
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
    assert result['totalResultsSize']
    assert result['maxResultsSize']
    assert result['returnedResultsSize']
    assert result['results'][0]
    assert result['results'][0]['baseRegistrationNumber'] == 'TEST0001'
    assert result['results'][0]['registrationNumber'] == 'TEST0007'
    assert result['results'][0]['createDateTime']
    assert result['results'][0]['matchType']
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
    assert result['totalResultsSize']
    assert result['maxResultsSize']
    assert result['returnedResultsSize']
    assert result['results'][0]
    assert result['results'][0]['baseRegistrationNumber'] == 'TEST0001'
    assert result['results'][0]['registrationNumber'] == 'TEST0008'
    assert result['results'][0]['createDateTime']
    assert result['results'][0]['matchType']
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
            'value': 'T200000'
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
    assert result['results'][0]['vehicleCollateral']['manufacturedHomeRegistrationNumber']


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


def test_search_aircraft_dot(session):
    """Assert that a search query by aircraft DOT returns the expected result."""
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
    assert result['results'][0]['matchType']
    assert result['results'][0]['registrationType']
    assert result['results'][0]['vehicleCollateral']
    assert result['results'][0]['vehicleCollateral']['type']
    assert result['results'][0]['vehicleCollateral']['serialNumber']
    assert result['results'][0]['vehicleCollateral']['year']
    assert result['results'][0]['vehicleCollateral']['make']
    assert result['results'][0]['vehicleCollateral']['model']


def test_search_reg_num_invalid(session):
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


def test_search_mhr_num_invalid(session):
    """Assert that a search by mhr number query with no results 
       returns the expected result."""
    json_data = {
        'type': 'MHR_NUMBER',
        'criteria': {
            'value': 'TESTXXXX'
        },
        'clientReferenceId': 'T-SQ-MH-2'
    }
    query = SearchClient.create_from_json(json_data, None)
    query.search()

    assert query.search_id
    assert not query.search_response
    assert query.returned_results_size == 0


def test_search_serial_num_invalid(session):
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


def test_search_aircraft_dot_invalid(session):
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


def test_search_startDateTime_invalid(session, client, jwt):
    """Assert that validation of a search request with an invalid startDateTime 
       throws a BusinessException."""
    # setup
    json_data = {
        'type': 'REGISTRATION_NUMBER',
        'criteria': {
            'value': 'TEST0001'
        },
        'clientReferenceId': 'T-API-SQ-RG-6',
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
        'clientReferenceId': 'T-API-SQ-RG-7',
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

