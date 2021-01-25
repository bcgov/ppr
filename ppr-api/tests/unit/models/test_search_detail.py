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

from ppr_api.models import Search, Registration, SearchDetail
from ppr_api.utils.datetime import now_ts_offset, format_ts
from ppr_api.exceptions import BusinessException


def test_search_valid_single(session):
    """Assert that a search detail results on a registration number returns the
    expected result."""
    json_data = [{
        'baseRegistrationNumber': 'TEST0001', 
        'matchType': 'EXACT', 
        'registrationType': 'SA'
    }]
    select = SearchDetail.create_from_json(json_data, 200000001)
    select.save()

    result = select.json
    #print(result)
    assert select.search_id
    assert select.search_response
    assert len(result) == 1
    assert result[0]['financingStatement']


def test_search_id_invalid(session, client, jwt):
    """Assert that validation of an invalid search ID throws a BusinessException."""
    # setup
    json_data = [{
        'baseRegistrationNumber': 'TEST0001', 
        'matchType': 'EXACT', 
        'registrationType': 'SA'
    }]

    # test
    with pytest.raises(BusinessException) as bad_request_err:
        SearchDetail.validate_search_select(json_data, 300000000)

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    print(bad_request_err.value.error)


def test_search_id_invalid_used(session, client, jwt):
    """Assert that validation of a search ID that has already been submitted 
       throws a BusinessException."""
    # setup
    json_data = [{
        'baseRegistrationNumber': 'TEST0001', 
        'matchType': 'EXACT', 
        'registrationType': 'SA'
    }]

    # test
    with pytest.raises(BusinessException) as bad_request_err:
        SearchDetail.validate_search_select(json_data, 200000000)

    # check
    assert bad_request_err
    assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
    print(bad_request_err.value.error)


