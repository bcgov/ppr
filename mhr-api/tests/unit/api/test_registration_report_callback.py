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


# testdata pattern is ({desc}, {status}, {registration_id}, {has_key}, {has_config_key}, {is_param}, {bad_key})
TEST_CALLBACK_DATA = [
    ('Invalid reg id header key', HTTPStatus.NOT_FOUND, 300000005, True, True, False, None),
    ('Invalid reg id param key', HTTPStatus.NOT_FOUND, 300000005, True, True, True, None),
    ('Unauthorized no key', HTTPStatus.UNAUTHORIZED, 300000005, False, True, True, None),
    ('Unauthorized invalid key header', HTTPStatus.UNAUTHORIZED, 300000005, True, True, False, "JUNK"),
    ('Unauthorized invalid key param', HTTPStatus.UNAUTHORIZED, 300000005, True, True, True, "JUNK"),
    ('Unauthorized no config key', HTTPStatus.UNAUTHORIZED, 300000005, True, False, True, None),
]


@pytest.mark.parametrize('desc,status,registration_id,has_key,has_config_key,is_param,bad_key', TEST_CALLBACK_DATA)
def test_registration_report_callback(session, client, jwt, desc, status, registration_id, has_key, has_config_key, is_param, bad_key):
    """Assert that a callback request returns the expected status."""
    # setup
    config_key = current_app.config.get("SUBSCRIPTION_API_KEY", "")
    if not has_config_key and config_key:
        current_app.config.update(SUBSCRIPTION_API_KEY="")
    elif not config_key and has_config_key:
        current_app.config.update(SUBSCRIPTION_API_KEY="afassdfdssds12342s")
        config_key = current_app.config.get('SUBSCRIPTION_API_KEY')
    test_key = bad_key if bad_key else config_key
    url: str = f"/api/v1/registration-report-callback/{registration_id}"
    headers = None
    if test_key and has_key:
        if is_param:
            url += f"?x-apikey={test_key}"
        else:
            headers = {
                'x-apikey': test_key
            }

    # test
    rv = client.post(url, headers=headers)

    if not has_config_key and config_key:
        current_app.config.update(SUBSCRIPTION_API_KEY=config_key)
    # check
    assert rv.status_code == status
