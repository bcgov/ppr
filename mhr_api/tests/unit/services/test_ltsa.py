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

from mhr_api.models import LtsaDescription
from mhr_api.services import ltsa


# testdata pattern is ({description}, {pid}, {valid})
TEST_LOOKUP_DATA = [
    ('Valid pid', '012-684-597', True),
    ('Valid pid unformatted', '012684597', True),
    ('Invalid pid missing', None, False),
    ('Invalid pid',  '888-684-597', False)
]
# testdata pattern is ({pid}, {update})
TEST_SAVE_DATA = [
    ('023270098', False),
    ('008000000', True)
]


@pytest.mark.parametrize('desc,pid,valid', TEST_LOOKUP_DATA)
def test_pid_lookup(session, jwt, desc, pid, valid):
    """Assert that ltsa pid lookup service returns the expected result."""
    # setup
    result = ltsa.pid_lookup(pid)
    # check
    if valid:
        current_app.logger.info(result)
        assert result
    else:
        assert not result or result.get('errorMessage')


@pytest.mark.parametrize('pid,update', TEST_SAVE_DATA)
def test_save_ltsa_description(session, jwt, pid, update):
    """Assert that saving or updating a ltsa legal description by pid lookup works as expected."""
    # setup
    result: LtsaDescription = ltsa.save_description(pid, update)
    # check
    assert result
    assert result.id
    assert result.pid_number == pid
    assert result.ltsa_description
    assert result.update_ts
