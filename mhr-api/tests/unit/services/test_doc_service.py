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

"""Tests to verify the auth-api integration.

Test-Suite to ensure that the client for the auth-api service is working as expected.
"""
import pytest
from flask import current_app

from mhr_api.services import doc_service


# testdata pattern is ({description}, {doc_id}, {result_count})
TEST_LOOKUP_DATA = [
    ('Valid doc id', '99990001', 1),
    ('Invalid doc id',  '00123456', 0)
]


@pytest.mark.parametrize('desc,doc_id,result_count', TEST_LOOKUP_DATA)
def test_doc_id_lookup(session, jwt, desc, doc_id, result_count):
    """Assert that doc service document id lookup returns the expected result."""
    if is_ci_testing() or not current_app.config.get("DOC_SERVICE_URL"):
        return

    # setup
    result = doc_service.doc_id_lookup(doc_id)
    # check
    assert result
    assert result.get("resultCount") >= result_count
    if result_count > 0:
        assert result.get("results")
    else:
        assert not result.get("results")


def is_ci_testing() -> bool:
    """Check unit test environment: exclude most reports for CI testing."""
    return  current_app.config.get("DEPLOYMENT_ENV", "testing") == "testing"
