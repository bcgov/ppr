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
        'value': 'GUTHRIE HOLDINGS LTD.'
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
OWNER_NAME_JSON2 = {
    'type': 'OWNER_NAME',
    'criteria': {
        'ownerName': {
            'first': 'DWAYNE',
            'middle': 'LARRY',
            'last': 'MANKE'
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
        'value': '4551'
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
        'value': 'XXXXXXXXX'
    },
    'clientReferenceId': 'T-SQ-MS-4'
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

    query: SearchRequest = SearchRequest.create_from_json(json_data, 'PS12345', 'UNIT_TEST')
    query.search()
    assert not query.updated_selection
    result = query.json
    current_app.logger.debug(result)
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
        assert match['status']
        assert match['createDateTime']
        assert match['homeLocation']
        assert match['serialNumber']
        assert match['baseInformation']
        assert match['baseInformation']['year']
        assert match['baseInformation']['make']
        assert match['baseInformation']['model'] is not None
        assert 'organizationName' in match or 'ownerName' in match
        if match.get('ownerName'):
            assert match['ownerName']['first']
            assert match['ownerName']['last']


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
