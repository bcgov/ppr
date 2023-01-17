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
from mhr_api.models.type_tables import MhrDocumentType


# testdata pattern is ({account_id}, {has_results})
TEST_ACCOUNT_REG_DATA = [
    ('2523', True),
    ('999999', False)
]
# testdata pattern is ({account_id}, {sort_criteria}, {sort_order}, {mhr_numbers}, {expected_clause})
TEST_QUERY_ORDER_DATA = [
    ('2523', None, None, "'098487'", db2_utils.REG_ORDER_BY_DATE),
    ('2523', 'invalid', None, "'098487'",  db2_utils.REG_ORDER_BY_DATE),
    ('2523', reg_utils.REG_TS_PARAM, None, "'098487'", db2_utils.REG_ORDER_BY_DATE),
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

# testdata pattern is ({account_id}, {collapse}, {filter_name}, {filter_value}, {mhr_numbers}, {expected_clause})
TEST_QUERY_FILTER_DATA = [
    ('2523', False, reg_utils.MHR_NUMBER_PARAM, '098487', "'098487'", 'mh.mhregnum IN (?)'),
    ('2523', False, reg_utils.REG_TYPE_PARAM, 'SALE / GIFT TRANSFER', "'098487'", db2_utils.REG_FILTER_REG_TYPE),
    ('2523', False, reg_utils.SUBMITTING_NAME_PARAM, 'LINDA', "'098487'", db2_utils.REG_FILTER_SUBMITTING_NAME),
    ('2523', False, reg_utils.CLIENT_REF_PARAM, 'A000873', "'098487'", db2_utils.REG_FILTER_CLIENT_REF),
    ('2523', False, reg_utils.STATUS_PARAM, 'EXEMPT', "'098487'", db2_utils.REG_FILTER_STATUS),
    ('2523', False, reg_utils.USER_NAME_PARAM, 'BCREG2', "'098487'", db2_utils.REG_FILTER_USERNAME),
    ('2523', True, reg_utils.MHR_NUMBER_PARAM, '098487', "'098487'", 'mh.mhregnum IN (?)'),
    ('2523', True, reg_utils.REG_TYPE_PARAM, 'SALE / GIFT TRANSFER', "'098487'",
     db2_utils.REG_FILTER_REG_TYPE_COLLAPSE),
    ('2523', True, reg_utils.SUBMITTING_NAME_PARAM, 'LINDA', "'098487'", db2_utils.REG_FILTER_SUBMITTING_NAME_COLLAPSE),
    ('2523', True, reg_utils.CLIENT_REF_PARAM, 'A000873', "'098487'", db2_utils.REG_FILTER_CLIENT_REF_COLLAPSE),
    ('2523', True, reg_utils.STATUS_PARAM, 'EXEMPT', "'098487'", db2_utils.REG_FILTER_STATUS),
    ('2523', True, reg_utils.USER_NAME_PARAM, 'BCREG2', "'098487'", db2_utils.REG_FILTER_USERNAME_COLLAPSE)
]

# testdata pattern is ({account_id}, {collapse}, {start_value}, {end_value}, {mhr_numbers}, {expected_clause})
TEST_QUERY_FILTER_DATA_DATE = [
    ('2523', False, '2021-10-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53', "'098487'", db2_utils.REG_FILTER_DATE),
    ('2523', True, '2021-10-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53', "'098487'",
     db2_utils.REG_FILTER_DATE_COLLAPSE)
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
            if registration['registrationDescription'] == 'REGISTER NEW UNIT':
                assert 'lienRegistrationType' in registration
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

    query: str = db2_utils.build_account_query(params, mhr_numbers, None)
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


@pytest.mark.parametrize('account_id,collapse,filter_name,filter_value,mhr_numbers,expected_clause',
                         TEST_QUERY_FILTER_DATA)
def test_account_reg_filter(session, account_id, collapse, filter_name, filter_value, mhr_numbers, expected_clause):
    """Assert that account registration query filter clause is as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id=account_id,
                                                                  collapse=collapse,
                                                                  sbc_staff=False)
    filter_clause: str = expected_clause
    if filter_name == reg_utils.REG_TS_PARAM:
        params.filter_registration_date = filter_value
        filter_clause = filter_clause.replace('?', filter_value[0:10])
    elif filter_name == reg_utils.STATUS_PARAM:
        params.filter_status_type = filter_value
        filter_clause = filter_clause.replace('?', 'E')
    elif filter_name == reg_utils.REG_TYPE_PARAM:
        params.filter_registration_type = filter_value
        filter_clause = filter_clause.replace('?', 'TRAN')
    elif filter_name == reg_utils.MHR_NUMBER_PARAM:
        params.filter_mhr_number = filter_value
        filter_clause = filter_clause.replace('?', f"'{filter_value}'")
    else:
        filter_clause = filter_clause.replace('?', filter_value)
    if filter_name == reg_utils.CLIENT_REF_PARAM:
        params.filter_client_reference_id = filter_value
    elif filter_name == reg_utils.SUBMITTING_NAME_PARAM:
        params.filter_submitting_name = filter_value
    elif filter_name == reg_utils.USER_NAME_PARAM:
        params.filter_username = filter_value

    base_query: str = db2_utils.QUERY_ACCOUNT_REGISTRATIONS_SORT
    filter_query: str = db2_utils.build_account_query_filter(base_query, params, mhr_numbers,
                                                             MhrDocumentType.find_all())
    # current_app.logger.debug(filter_clause)
    # current_app.logger.debug(filter_query)
    assert filter_query.find(filter_clause) > 0


@pytest.mark.parametrize('account_id,collapse,start_value,end_value,mhr_numbers,expected_clause',
                         TEST_QUERY_FILTER_DATA_DATE)
def test_account_reg_filter_date(session, account_id, collapse, start_value, end_value, mhr_numbers, expected_clause):
    """Assert that account registration query filter clause is as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id=account_id,
                                                                  collapse=collapse,
                                                                  sbc_staff=False)
    filter_clause: str = expected_clause
    params.filter_reg_start_date = start_value
    params.filter_reg_end_date = end_value
    base_query: str = db2_utils.QUERY_ACCOUNT_REGISTRATIONS_SORT
    filter_query: str = db2_utils.build_account_query_filter(base_query, params, mhr_numbers,
                                                             MhrDocumentType.find_all())
    # current_app.logger.debug(filter_clause)
    # current_app.logger.debug(filter_query)
    assert filter_query.find(filter_clause) > 0


@pytest.mark.parametrize('account_id,collapse,filter_name,filter_value,mhr_numbers,expected_clause',
                         TEST_QUERY_FILTER_DATA)
def test_find_account_filter(session, account_id, collapse, filter_name, filter_value, mhr_numbers, expected_clause):
    """Assert that account registration query with an order by clause is as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id=account_id,
                                                                  collapse=collapse,
                                                                  sbc_staff=False)
    if filter_name == reg_utils.REG_TS_PARAM:
        params.filter_registration_date = filter_value
    elif filter_name == reg_utils.STATUS_PARAM:
        params.filter_status_type = filter_value
    elif filter_name == reg_utils.REG_TYPE_PARAM:
        params.filter_registration_type = filter_value
    elif filter_name == reg_utils.MHR_NUMBER_PARAM:
        params.filter_mhr_number = filter_value
    elif filter_name == reg_utils.CLIENT_REF_PARAM:
        params.filter_client_reference_id = filter_value
    elif filter_name == reg_utils.SUBMITTING_NAME_PARAM:
        params.filter_submitting_name = filter_value
    elif filter_name == reg_utils.USER_NAME_PARAM:
        params.filter_username = filter_value

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
