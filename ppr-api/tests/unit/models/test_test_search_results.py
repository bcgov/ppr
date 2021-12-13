# Copyright © 2021 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests to assure the TestSearchResult Model.

Test-Suite to ensure that the TestSearchResult Model is working as expected.
"""
import pytest

from ppr_api.models import TestSearchResult


@pytest.mark.parametrize('id', [
    # search 1 (BS)
    400000000, 400000001, 400000002, 400000003, 400000004, 400000005, 400000006, 400000007,
    # search 2 (BS)
    400000100, 400000101, 400000102, 400000103, 400000104, 400000105, 400000106, 400000107, 400000108, 400000109,
    400000110,
    # search 3 (IS)
    400000200, 400000201, 400000202, 400000203, 400000204, 400000205, 400000206, 400000207,
    # search 4 (IS)
    400000300, 400000101, 400000302, 400000303, 400000304, 400000305, 400000306, 400000307, 400000308, 400000309,
    400000310
])
def test_find_by_id(session, id):
    """Assert that the find search result by id contains all expected elements."""
    result = TestSearchResult.find_by_id(id)
    assert result.id == id
    assert result.index == 0 or result.index
    assert result.details
    assert result.doc_id
    assert result.search_id
    assert result.paired_index == 0 or result.paired_index
    assert result.json


@pytest.mark.parametrize('search_id', [300000000, 300000001, 300000100, 300000101])
def test_find_all_by_search_id(session, search_id):
    """Assert that the test search result list contains all expected elements."""
    result_list = TestSearchResult.find_all_by_search_id(search_id)
    assert result_list
    for result in result_list:
        assert result.id
        assert result.index == 0 or result.index
        assert result.details
        assert result.doc_id
        assert result.search_id == search_id
        assert result.paired_index == 0 or result.paired_index
        assert result.json


@pytest.mark.parametrize('legacy_result_id, api_result_id', [
    # matching index pair exact
    (400000000, 400000004),
    # matching index pair similar
    (400000002, 400000006),
    # diff index pair exact
    (400000100, 400000110),
    # diff index pair similar
    (400000103, 400000108),
    # no pair legacy
    (400000104, None),
    # no pair api
    (None, 400000107),
])
def test_paired_index(session, legacy_result_id, api_result_id):
    """Assert that the paired index property returns the expected value."""
    legacy_result = TestSearchResult.find_by_id(legacy_result_id)
    api_result = TestSearchResult.find_by_id(api_result_id)

    if legacy_result_id and api_result_id:
        # assert they are pairs
        assert legacy_result.source == TestSearchResult.Source.LEGACY.value
        assert api_result.source == TestSearchResult.Source.API.value
        assert legacy_result.doc_id == api_result.doc_id and api_result.doc_id is not None

        # assert paired index corresponds with it's pair
        assert legacy_result.paired_index == api_result.index
        assert api_result.paired_index == legacy_result.index

    else:
        # it is either a missed or extra match so it should return -1
        result = legacy_result or api_result
        assert result
        assert result.paired_index == -1


@pytest.mark.parametrize('id, expected', [
    # legacy exact
    (
        400000000,
        {
            'documentId': 'R7654321',
            'details': 'BUSINESS SEARCH TEST 1',
            'index': 0,
            'id': 400000000,
            'matchType': 'E',
            'pairedIndex': 0,
            'source': 'legacy'
        }
    ),
    # api exact
    (
        400000004,
        {
            'documentId': 'R7654321',
            'details': '{"businessName": "BUSINESS SEARCH TEST 1", "partyId": 200000002}',
            'index': 0,
            'id': 400000004,
            'matchType': 'E',
            'pairedIndex': 0,
            'source': 'api'
        }
    ),
    # legacy similar
    (
        400000002,
        {
            'documentId': 'R7654323',
            'details': 'BUSINESS SEARCH TEST 2',
            'index': 0,
            'id': 400000002,
            'matchType': 'S',
            'pairedIndex': 0,
            'source': 'legacy'
        }
    ),
    # api similar
    (
        400000006,
        {
            'documentId': 'R7654323',
            'details': '{"businessName": "BUSINESS SEARCH TEST 2", "partyId": 200000004}',
            'index': 0,
            'id': 400000006,
            'matchType': 'S',
            'pairedIndex': 0,
            'source': 'api'
        }
    ),
])
def test_json(session, id, expected):
    """Assert that the json property returns the expected value."""
    result = TestSearchResult.find_by_id(id)

    assert result.json == expected
