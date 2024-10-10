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

"""Tests to verify the callback registration report endpoint.

Test-Suite to ensure that the /registration-report-callback endpoint is working as expected.
"""
from http import HTTPStatus

import pytest
from flask import current_app


# testdata pattern is ({desc}, {status}, {registration_id})
# Add more when report available.
TEST_CALLBACK_DATA = [
    ('Invalid id', HTTPStatus.NOT_FOUND, 300000005),
    ('Unauthorized', HTTPStatus.UNAUTHORIZED, 300000005)
]


@pytest.mark.parametrize('desc,status,registration_id', TEST_CALLBACK_DATA)
def test_registration_report_callback(session, client, jwt, desc, status, registration_id):
    """Assert that a callback request returns the expected status."""
    # test
    headers = None
    if status != HTTPStatus.UNAUTHORIZED:
        apikey = current_app.config.get('SUBSCRIPTION_API_KEY')
        if apikey:
            headers = {
                'x-apikey': apikey
            }
    rv = client.post('/api/v1/registration-report-callback/' + str(registration_id),
                     headers=headers)
    # check
    assert rv.status_code == status
