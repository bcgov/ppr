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

"""Tests to verify the legacy ltsa legal description synchronization endpoint.

Test-Suite to ensure that the /ltsa-sync endpoint is working as expected.
"""
from http import HTTPStatus

import pytest
from flask import current_app

from mhr_api.models.utils import is_legacy


# testdata pattern is ({desc}, {status}, {use_param})
TEST_SYNC_DATA = [
    ('Valid request header', HTTPStatus.BAD_REQUEST, False),
    ('Valid request param', HTTPStatus.BAD_REQUEST, True),
    ('Unauthorized', HTTPStatus.UNAUTHORIZED, False)
]


@pytest.mark.parametrize('desc,status,use_param', TEST_SYNC_DATA)
def test_ltsa_sync(session, client, jwt, desc, status, use_param):
    """Assert that a callback request returns the expected status."""
    # invert logic to execute otherwise the test could be making up to 500 ltsa calls.
    if not is_legacy():
        headers = None
        path: str = '/api/v1/ltsa-sync'
        if status != HTTPStatus.UNAUTHORIZED:
            apikey = current_app.config.get('SUBSCRIPTION_API_KEY')
            if apikey and use_param:
                path += '?x-apikey=' + apikey
            else:
                headers = {
                    'x-apikey': apikey
                }
        rv = client.post(path, headers=headers)
        current_app.logger.debug(rv.json)
        # check
        assert rv.status_code == status
        if status == HTTPStatus.OK:
            resp_json = rv.json
            assert resp_json
            assert 'errorCount' in resp_json
            assert 'successCount' in resp_json
            assert 'errorPids' in resp_json
            assert 'successPids' in resp_json
