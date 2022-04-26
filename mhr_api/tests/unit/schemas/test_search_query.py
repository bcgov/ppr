# Copyright © 2020 Province of British Columbia
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
"""Test Suite to ensure the MHR Search Query schema is valid."""
import copy

import pytest

from registry_schemas import validate
from registry_schemas.example_data.mhr import SEARCH_QUERY


SEARCH_QUERY_OWNER = {
  'type': 'MHR_NUMBER',
  'criteria': {
    'ownerName': {
      'first': 'James',
      'last': 'Smith'
    }
  },
  'clientReferenceId': 'EX-00000402'
}
LONG_CLIENT_REF = '01234567890123456789012345678901234567890'
LONG_ORG_NAME = '01234567890123456789012345678901234567890123456789012345678901234567890'

# testdata pattern is ({desc}, {is valid}, {type}, {ref}, {criteria}, {query_data})
TEST_DATA_QUERY = [
    ('Valid MHR', True, 'MHR_NUMBER', 'ex-00001', '001234', SEARCH_QUERY),
    ('Valid SERIAL', True, 'SERIAL_NUMBER', 'ex-00001', 'XVF003456', SEARCH_QUERY),
    ('Valid ORG NAME', True, 'ORGANIZATION_NAME', 'ex-00001', 'SAGE HILL INC.', SEARCH_QUERY),
    ('Valid OWNER NAME', True, 'OWNER_NAME', 'ex-00001', None, SEARCH_QUERY_OWNER),
    ('Valid No Client Ref', True, 'MHR_NUMBER', None, '001234', SEARCH_QUERY),
    ('Invalid Client Ref too long', False, 'MHR_NUMBER', LONG_CLIENT_REF, '001234', SEARCH_QUERY),
    ('Invalid missing Type', False, None, None, '001234', SEARCH_QUERY),
    ('Invalid missing criteria', False, 'MHR_NUMBER', 'ex-00001', None, SEARCH_QUERY),
    ('Invalid ORG NAME too long', False, 'ORGANIZATION_NAME', 'ex-00001', LONG_ORG_NAME, SEARCH_QUERY)
]
# testdata pattern is ({is valid}, {type})
TEST_DATA_TYPE = [
    (True, 'MHR_NUMBER'),
    (True, 'SERIAL_NUMBER'),
    (True, 'OWNER_NAME'),
    (True, 'ORGANIZATION_NAME'),
    (False, 'XX')
]


@pytest.mark.parametrize('desc, valid, type, ref, criteria, query_data', TEST_DATA_QUERY)
def test_search_query(desc, valid, type, ref, criteria, query_data):
    """Assert that the schema is performing as expected."""
    query = copy.deepcopy(query_data)
    if not type:
        del query['type']
    else:
        query['type'] = type
    if not ref:
        del query['clientReferenceId']
    else:
        query['clientReferenceId'] = ref
    if not criteria and type != 'OWNER_NAME':
        del query['criteria']
    elif criteria:
        query['criteria']['value'] = criteria

    is_valid, errors = validate(query, 'searchQuery', 'mhr')

    if errors:
        for err in errors:
            print(err.message)

    if valid:
        assert is_valid
    else:
        assert not is_valid


@pytest.mark.parametrize('valid, type', TEST_DATA_TYPE)
def test_search_query_type(valid, type):
    """Assert the validation of all search types."""
    query = copy.deepcopy(SEARCH_QUERY)
    query['type'] = type

    is_valid, errors = validate(query, 'searchQuery', 'mhr')

    if errors:
        for err in errors:
            print(err.message)

    if valid:
        assert is_valid
    else:
        assert not is_valid
