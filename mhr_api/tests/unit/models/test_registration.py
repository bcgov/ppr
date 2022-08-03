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

"""Tests to assure the Registration Model.

Test-Suite to ensure that the Registration Model is working as expected.
"""
from flask import current_app

import pytest

from mhr_api.models import Registration


# testdata pattern is ({mhr_num}, {exists}, {reg_description}, {in_list})
TEST_SUMMARY_REG_DATA = [
    ('077741', True, 'Manufactured Home Registration', False),
    ('TESTXX', False, None, False),
    ('045349', True, 'Manufactured Home Registration', True)
]


@pytest.mark.parametrize('mhr_num,exists,reg_desc,in_list', TEST_SUMMARY_REG_DATA)
def test_find_summary_by_mhr_number(session, mhr_num, exists, reg_desc, in_list):
    """Assert that finding summary MHR registration information works as expected."""
    registration = Registration.find_summary_by_mhr_number('PS12345', mhr_num)
    if exists:
        current_app.logger.info(registration)
        assert registration['mhrNumber'] == mhr_num
        assert registration['registrationDescription'] == reg_desc
        assert registration['statusType'] is not None
        assert registration['createDateTime'] is not None
        assert registration['username'] is not None
        assert registration['submittingParty'] is not None
        assert registration['clientReferenceId'] is not None
        assert registration['ownerNames'] is not None
        assert registration['path'] is not None
        assert registration['inUserList'] == in_list
    else:
        assert not registration
