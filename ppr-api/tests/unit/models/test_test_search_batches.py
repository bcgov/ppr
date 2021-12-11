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

"""Tests to assure the TestSearchBatch Model.

Test-Suite to ensure that the TestSearchBatch Model is working as expected.
"""
from datetime import datetime, timedelta

import pytest

from ppr_api.models import TestSearchBatch
from ppr_api.models.search_request import SearchRequest


@pytest.mark.parametrize('id', [200000000, 200000001])
def test_find_by_id(session, id):
    """Assert that the find batch by id contains all expected elements."""
    batch = TestSearchBatch.find_by_id(id)
    assert batch.id == id
    assert batch.search_type
    assert batch.sim_val_business
    assert batch.sim_val_first_name
    assert batch.sim_val_last_name
    assert batch.test_date
    assert batch.searches
    assert batch.json


def test_find_search_batches(session):
    """Assert that the find search batches contains all expected elements."""
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)

    all_bs_batches = TestSearchBatch.find_search_batches(SearchRequest.SearchTypes.BUSINESS_DEBTOR.value)
    all_is_batches = TestSearchBatch.find_search_batches(SearchRequest.SearchTypes.INDIVIDUAL_DEBTOR.value)
    bs_batches_after_now = TestSearchBatch.find_search_batches(
        SearchRequest.SearchTypes.BUSINESS_DEBTOR.value,
        now
    )
    bs_batches_before_now = TestSearchBatch.find_search_batches(
        SearchRequest.SearchTypes.BUSINESS_DEBTOR.value,
        None,
        now
    )
    bs_batches_after_yesterday_before_now = TestSearchBatch.find_search_batches(
        SearchRequest.SearchTypes.BUSINESS_DEBTOR.value,
        yesterday,
        now
    )
    assert len(all_bs_batches) == 1
    assert len(all_is_batches) == 1
    assert len(bs_batches_after_now) == 0
    assert len(bs_batches_before_now) == 1
    assert len(bs_batches_after_yesterday_before_now) == 1

    responses = all_bs_batches + all_is_batches + bs_batches_before_now + bs_batches_after_yesterday_before_now
    for batch in responses:
        assert batch.id
        assert batch.search_type
        assert batch.sim_val_business
        assert batch.sim_val_first_name
        assert batch.sim_val_last_name
        assert batch.test_date
        assert batch.searches
        assert batch.json
