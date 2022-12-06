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

"""Tests to assure the MHR Registration DB2 Model utils.

Test-Suite to ensure that the MH Registration DB2 Model helper methods are working as expected.
"""
from flask import current_app

import pytest
from flask import current_app

from mhr_api.models import registration_utils as reg_utils, utils as model_utils
from mhr_api.models.registration_utils import AccountRegistrationParams
from mhr_api.models.db2 import utils as db2_utils


# testdata pattern is ({account_id}, {has_results})
TEST_ACCOUNT_REG_DATA = [
    ('2523', True),
    ('999999', False)
]
# testdata pattern is ({account_id}, {sort_criteria}, {sort_order}, {mhr_numbers}, {expected_clause})
TEST_QUERY_ORDER_DATA = [
    ('2523', None, None, "'098487'", db2_utils.REG_ORDER_BY_DATE),
    ('2523', 'invalid', None, "'098487'",  db2_utils.REG_ORDER_BY_DATE),
    ('2523',reg_utils, None, "'098487'", db2_utils.REG_ORDER_BY_DATE),
    ('2523', reg_utils.MHR_NUMBER_PARAM, reg_utils.SORT_ASCENDING, "'098487'", db2_utils.REG_ORDER_BY_MHR_NUMBER),
    ('2523', reg_utils.REG_TYPE_PARAM, reg_utils.SORT_ASCENDING, "'098487'", db2_utils.REG_ORDER_BY_REG_TYPE),
    ('2523', reg_utils.SUBMITTING_NAME_PARAM, reg_utils.SORT_DESCENDING, "'098487'",
     db2_utils.REG_ORDER_BY_SUBMITTING_NAME),
    ('2523', reg_utils.CLIENT_REF_PARAM, reg_utils.SORT_ASCENDING, "'098487'", db2_utils.REG_ORDER_BY_CLIENT_REF),
    ('2523', reg_utils.REG_TS_PARAM, reg_utils.SORT_ASCENDING, "'098487'", db2_utils.REG_ORDER_BY_DATE),
    ('2523', reg_utils.STATUS_PARAM, reg_utils.SORT_ASCENDING, "'098487'", db2_utils.REG_ORDER_BY_STATUS),
    ('2523', reg_utils.USER_NAME_PARAM, reg_utils.SORT_DESCENDING, "'098487'", db2_utils.REG_ORDER_BY_USERNAME),
    ('2523', reg_utils.OWNER_NAME_PARAM, reg_utils.SORT_DESCENDING, "'098487'", db2_utils.REG_ORDER_BY_OWNER_NAME),
    ('2523', reg_utils.EXPIRY_DAYS_PARAM, reg_utils.SORT_DESCENDING, "'098487'", db2_utils.REG_ORDER_BY_EXPIRY_DAYS)
]


@pytest.mark.parametrize('account_id, has_results', TEST_ACCOUNT_REG_DATA)
def test_find_account_registrations(session, account_id, has_results):
    """Assert that finding account summary MHR registration information works as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id=account_id,
                                                                  collapse=True,
                                                                  sbc_staff=False)

    reg_list = db2_utils.find_all_by_account_id(params)
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
            assert registration['documentId'] is not None
            assert not registration.get('inUserList')
    else:
        assert not reg_list


@pytest.mark.parametrize('account_id,sort_criteria,sort_order,mhr_numbers,expected_clause', TEST_QUERY_ORDER_DATA)
def test_account_reg_order(session, account_id, sort_criteria, sort_order, mhr_numbers, expected_clause):
    """Assert that account registration query order by clause is as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id=account_id,
                                                                  collapse=True,
                                                                  sbc_staff=False)
    params.sort_criteria = sort_criteria
    params.sort_direction = sort_order
    order_clause = expected_clause
    if params.has_sort() and params.sort_criteria == reg_utils.REG_TS_PARAM:
        if params.sort_direction and params.sort_direction == reg_utils.SORT_ASCENDING:
            order_clause = order_clause.replace(db2_utils.SORT_DESCENDING, db2_utils.SORT_ASCENDING)
    elif params.has_sort():
        if params.sort_direction and params.sort_direction == reg_utils.SORT_ASCENDING:
            order_clause += db2_utils.SORT_ASCENDING
        else:
            order_clause += db2_utils.SORT_DESCENDING

    query: str = db2_utils.build_account_query(params, mhr_numbers)
    current_app.logger.debug(query)
    # current_app.logger.debug(order_clause)
    assert query.endswith(order_clause) or query.endswith((order_clause + '\n'))


@pytest.mark.parametrize('account_id,sort_criteria,sort_order,mhr_numbers,expected_clause', TEST_QUERY_ORDER_DATA)
def test_find_account_sort_order(session, account_id, sort_criteria, sort_order, mhr_numbers, expected_clause):
    """Assert that account registration query with an order by clause is as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id=account_id,
                                                                  collapse=True,
                                                                  sbc_staff=False)
    params.sort_criteria = sort_criteria
    params.sort_direction = sort_order
    reg_list = db2_utils.find_all_by_account_id(params)
    assert reg_list
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
        assert registration['documentId'] is not None
        assert not registration.get('inUserList')
