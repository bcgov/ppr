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


# testdata pattern is ({account_id}, {mhr_num}, {exists}, {reg_description}, {in_list})
TEST_SUMMARY_REG_DATA = [
    ('PS12345', '077741', True, 'Manufactured Home Registration', False),
    ('PS12345', 'TESTXX', False, None, False),
    ('PS12345', '045349', True, 'Manufactured Home Registration', True)
]
# testdata pattern is ({account_id}, {has_results})
TEST_ACCOUNT_REG_DATA = [
    ('PS12345', True),
    ('999999', False)
]


@pytest.mark.parametrize('account_id,mhr_num,exists,reg_desc,in_list', TEST_SUMMARY_REG_DATA)
def test_find_summary_by_mhr_number(session, account_id, mhr_num, exists, reg_desc, in_list):
    """Assert that finding summary MHR registration information works as expected."""
    registration = Registration.find_summary_by_mhr_number(account_id, mhr_num)
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


@pytest.mark.parametrize('account_id, has_results', TEST_ACCOUNT_REG_DATA)
def test_find_account_registrations(session, account_id, has_results):
    """Assert that finding account summary MHR registration information works as expected."""
    reg_list = Registration.find_all_by_account_id(account_id)
    if has_results:
        for registration in reg_list:
            assert registration['mhrNumber']
            assert registration['registrationDescription']
            assert registration['statusType'] is not None
            assert registration['createDateTime'] is not None
            assert registration['username'] is not None
            assert registration['submittingParty'] is not None
            assert registration['clientReferenceId'] is not None
            assert registration['ownerNames'] is not None
            assert registration['path'] is not None
            assert registration['inUserList'] is not None
    else:
        assert not reg_list
