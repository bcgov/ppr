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

"""Tests to verify the ops health check endpoint.

Test-Suite to ensure that the /ops endpoint is working as expected.
"""
from http import HTTPStatus


def test_health_check(session, client, jwt):
    """Assert that a party code for a non-existent party returns a 404 error."""
    # no setup

    # test
    rv = client.get('/ops/healthz')
    # check
    assert rv.status_code == HTTPStatus.OK
