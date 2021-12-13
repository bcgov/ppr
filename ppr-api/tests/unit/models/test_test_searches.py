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

"""Tests to assure the TestSearch Model.

Test-Suite to ensure that the TestSearch Model is working as expected.
"""
import pytest

from ppr_api.models import TestSearch, TestSearchResult


@pytest.mark.parametrize('id', [300000000, 300000001, 300000100, 300000101])
def test_find_by_id(session, id):
    """Assert that the find search by id contains all expected elements."""
    search = TestSearch.find_by_id(id)
    assert search.id == id
    assert search.search_criteria
    assert search.run_time
    assert search.batch_id
    assert search.results
    assert search.json


@pytest.mark.parametrize('batch_id', [200000000, 200000001])
def test_find_all_by_batch_id(session, batch_id):
    """Assert that the test search list contains all expected elements."""
    search_list = TestSearch.find_all_by_batch_id(batch_id)
    assert search_list
    for search in search_list:
        assert search.id
        assert search.search_criteria
        assert search.run_time
        assert search.batch_id
        assert search.results
        assert search.json


@pytest.mark.parametrize('id', [300000000, 300000001, 300000100, 300000101])
def test_get_results(session, id):
    """Assert that the get results method returns the expected results."""
    search = TestSearch.find_by_id(id)
    # exact legacy
    results_ex_leg = search.get_results(TestSearchResult.MatchType.EXACT.value, TestSearchResult.Source.LEGACY.value)
    for result in results_ex_leg:
        assert result['matchType'] == TestSearchResult.MatchType.EXACT.value
        assert result['source'] == TestSearchResult.Source.LEGACY.value
        obj = TestSearchResult.find_by_id(result['id'])
        assert obj and obj.search_id == search.id

    # similar legacy
    results_sim_leg = search.get_results(TestSearchResult.MatchType.SIMILAR.value, TestSearchResult.Source.LEGACY.value)
    for result in results_sim_leg:
        assert result['matchType'] == TestSearchResult.MatchType.SIMILAR.value
        assert result['source'] == TestSearchResult.Source.LEGACY.value
        obj = TestSearchResult.find_by_id(result['id'])
        assert obj and obj.search_id == search.id

    # exact api
    results_ex_api = search.get_results(TestSearchResult.MatchType.EXACT.value, TestSearchResult.Source.API.value)
    for result in results_ex_api:
        assert result['matchType'] == TestSearchResult.MatchType.EXACT.value
        assert result['source'] == TestSearchResult.Source.API.value
        obj = TestSearchResult.find_by_id(result['id'])
        assert obj and obj.search_id == search.id

    # similar api
    results_sim_api = search.get_results(TestSearchResult.MatchType.SIMILAR.value, TestSearchResult.Source.API.value)
    for result in results_sim_api:
        assert result['matchType'] == TestSearchResult.MatchType.SIMILAR.value
        assert result['source'] == TestSearchResult.Source.API.value
        obj = TestSearchResult.find_by_id(result['id'])
        assert obj and obj.search_id == search.id


@pytest.mark.parametrize('passed_id, failed_id', [(300000000, 300000001), (300000100, 300000101)])
def test_avg_index_diff(session, passed_id, failed_id):
    """Assert that the avg_index_diff method returns as expected."""
    passed_search = TestSearch.find_by_id(passed_id)
    failed_search = TestSearch.find_by_id(failed_id)

    # verify data is what we assumed
    for result in passed_search.results:
        assert result.index == result.paired_index

    failed = False
    for result in failed_search.results:
        if result.index != result.paired_index:
            failed = True
            break
    assert failed

    # test avg_index_diff
    assert passed_search.avg_index_diff(TestSearchResult.MatchType.EXACT.value) == 0
    assert passed_search.avg_index_diff(TestSearchResult.MatchType.SIMILAR.value) == 0
    assert failed_search.avg_index_diff(TestSearchResult.MatchType.EXACT.value) > 0
    assert failed_search.avg_index_diff(TestSearchResult.MatchType.SIMILAR.value) > 0
    # specific to current examples
    assert failed_search.avg_index_diff(TestSearchResult.MatchType.EXACT.value) == 1.5
    assert failed_search.avg_index_diff(TestSearchResult.MatchType.SIMILAR.value) == 0.5


@pytest.mark.parametrize('passed_id, failed_id', [(300000000, 300000001), (300000100, 300000101)])
def test_fail_index(session, passed_id, failed_id):
    """Assert that the fail_index method returns as expected."""
    passed_search = TestSearch.find_by_id(passed_id)
    failed_search = TestSearch.find_by_id(failed_id)

    # verify data is what we assumed
    for result in passed_search.results:
        assert result.index == result.paired_index

    failed = False
    for result in failed_search.results:
        if result.index != result.paired_index:
            failed = True
    assert failed

    # test fail_index
    assert passed_search.fail_index(TestSearchResult.MatchType.EXACT.value) == -1
    assert passed_search.fail_index(TestSearchResult.MatchType.SIMILAR.value) == -1
    assert failed_search.fail_index(TestSearchResult.MatchType.EXACT.value) > -1
    assert failed_search.fail_index(TestSearchResult.MatchType.SIMILAR.value) > -1
    # specific to current examples
    assert failed_search.fail_index(TestSearchResult.MatchType.EXACT.value) == 0
    assert failed_search.fail_index(TestSearchResult.MatchType.SIMILAR.value) == 1


@pytest.mark.parametrize('passed_id, failed_id', [(300000000, 300000001), (300000100, 300000101)])
def test_missed_matches(session, passed_id, failed_id):
    """Assert that the missed_matches method returns as expected."""
    passed_search = TestSearch.find_by_id(passed_id)
    failed_search = TestSearch.find_by_id(failed_id)

    # verify data is what we assumed
    for result in passed_search.results:
        assert result.index == result.paired_index

    failed = False
    for result in failed_search.results:
        if result.index != result.paired_index:
            failed = True
    assert failed

    # test fail_index
    assert len(passed_search.missed_matches(TestSearchResult.MatchType.EXACT.value)) == 0
    assert len(passed_search.missed_matches(TestSearchResult.MatchType.SIMILAR.value)) == 0
    assert len(failed_search.missed_matches(TestSearchResult.MatchType.EXACT.value)) == 1
    assert len(failed_search.missed_matches(TestSearchResult.MatchType.SIMILAR.value)) == 1
