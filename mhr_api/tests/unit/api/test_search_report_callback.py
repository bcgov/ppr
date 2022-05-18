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

"""Tests to verify the callback search report endpoint.

Test-Suite to ensure that the /search-report-callback endpoint is working as expected.
"""
from http import HTTPStatus

import pytest


# testdata pattern is ({desc}, {status}, {search_id})
# Add more when report available.
TEST_CALLBACK_DATA = [
    ('Invalid id', HTTPStatus.NOT_FOUND, 300000005)
]


@pytest.mark.parametrize('desc,status,search_id', TEST_CALLBACK_DATA)
def test_search_report_callback(session, client, jwt, desc, status, search_id):
    """Assert that a callback request returns the expected status."""
    # test
    rv = client.post('/api/v1/search-report-callback/' + str(search_id),
                     headers=None)
    # check
    assert rv.status_code == status


def test_search_report_serial(session, client, jwt):
    """Assert that a callback request returns the expected status."""
    # test
    rv = client.post('/api/v1/search-report-callback/8958',
                     headers=None)
