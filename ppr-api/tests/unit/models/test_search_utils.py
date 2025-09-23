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
# from flask import current_app
import copy

import pytest
from flask import current_app

from ppr_api.models import search_utils, utils as model_utils
from ppr_api.models.search_utils import AccountSearchParams
from ppr_api.resources.utils import set_search_params_criteria
from ppr_api.services.authz import is_staff_account
from ppr_api.utils.logging import logger


# testdata pattern is ({sort_criteria}, {sort_order}, {expected_clause})
TEST_QUERY_ORDER_DATA = [
    (None, None, ' ORDER BY search_ts DESC'),
    ('invalid', None, ' ORDER BY search_ts DESC'),
    ('type', 'ascending', ' ORDER BY search_type ASC'),
    ('username', 'descending', ' ORDER BY username DESC'),
    ('clientReferenceId', 'ascending', ' ORDER BY client_reference_id ASC'),
    ('searchDateTime', 'ascending', ' ORDER BY search_ts ASC'),
]
# testdata pattern is ({search_type}, {client_ref}, {username}, {start_ts}, {end_ts}, {filter_clause})
TEST_QUERY_FILTER_DATA = [
    (None, None, None, None, None, None),
    ('RG', None, None, None, None, search_utils.SEARCH_FILTER_TYPE),
    ('PPR', None, None, None, None, search_utils.SEARCH_FILTER_TYPE_PPR),
    ('MHR', None, None, None, None, search_utils.SEARCH_FILTER_TYPE_MHR),
    (None, 'T-S-RG-003', None, None, None, search_utils.SEARCH_FILTER_CLIENT_REF),
    (None, None, 'TESTUSER', None, None, search_utils.SEARCH_FILTER_USERNAME),
    (None, None, None, 14, 1, search_utils.SEARCH_FILTER_DATE),
]
# testdata pattern is ({search_type}, {criteria}, {filter_clause})
TEST_QUERY_CRITERIA_DATA = [
    (None, "TEST", search_utils.SEARCH_FILTER_CRITERIA_DEFAULT),
    ("REGISTRATION_NUMBER", "TEST", search_utils.SEARCH_FILTER_CRITERIA_DEFAULT),
    ("AIRCRAFT_DOT", "TEST", search_utils.SEARCH_FILTER_CRITERIA_DEFAULT),
    ("MHR_NUMBER", "TEST", search_utils.SEARCH_FILTER_CRITERIA_DEFAULT),
    ("SERIAL_NUMBER", "TEST", search_utils.SEARCH_FILTER_CRITERIA_DEFAULT),
    ("MHR_SERIAL_NUMBER", "TEST", search_utils.SEARCH_FILTER_CRITERIA_DEFAULT),
    ("MHR_ORGANIZATION_NAME", "TEST", search_utils.SEARCH_FILTER_CRITERIA_DEFAULT),
    ("MHR_MHR_NUMBER", "TEST", search_utils.SEARCH_FILTER_CRITERIA_DEFAULT),
    ("BUSINESS_DEBTOR", "TEST", search_utils.SEARCH_FILTER_CRITERIA_DEFAULT),
    ("INDIVIDUAL_DEBTOR", "TEST", search_utils.SEARCH_FILTER_CRITERIA_DEFAULT),
    ("MHR_OWNER_NAME", "TEST", search_utils.SEARCH_FILTER_CRITERIA_DEFAULT),
    ("INDIVIDUAL_DEBTOR", "FNAME TEST", search_utils.SEARCH_FILTER_CRITERIA_DEFAULT),
    ("MHR_OWNER_NAME", "FNAME TEST", search_utils.SEARCH_FILTER_CRITERIA_DEFAULT),
]

@pytest.mark.parametrize('sort_criteria,sort_order,value', TEST_QUERY_ORDER_DATA)
def test_account_search_order(session, sort_criteria, sort_order, value):
    """Assert that account registration query order by clause is as expected."""
    params: AccountSearchParams = AccountSearchParams(account_id='PS12345', sbc_staff=False)
    params.sort_criteria = sort_criteria
    params.sort_direction = sort_order
    clause = search_utils.get_account_query_order(params)
    assert clause == value


@pytest.mark.parametrize('search_type,client_ref,username,start_ts,end_ts,filter_clause', TEST_QUERY_FILTER_DATA)
def test_account_filter_clause(session, search_type, client_ref, username, start_ts, end_ts, filter_clause):
    """Assert that account search history query filter clause is as expected."""
    params: AccountSearchParams = AccountSearchParams(account_id='PS12345', sbc_staff=False)
    params.filter_search_type = search_type
    params.filter_client_reference_id = client_ref
    params.filter_username = username
    if start_ts and end_ts:
        params.filter_start_date = model_utils.format_ts(model_utils.today_ts_offset(start_ts, False))
        params.filter_end_date = model_utils.format_ts(model_utils.today_ts_offset(end_ts, False))
    base_query: str = search_utils.ACCOUNT_SEARCH_HISTORY_BASE
    query: str = search_utils.build_account_query_filter(base_query, params)
    if params.has_filter():
        assert query.find(filter_clause) != -1


@pytest.mark.parametrize('search_type,criteria,filter_clause', TEST_QUERY_CRITERIA_DATA)
def test_account_criteria_clause(session, search_type,criteria,filter_clause):
    """Assert that account search history query criteria filter clause is as expected."""
    params: AccountSearchParams = AccountSearchParams(account_id='PS12345', sbc_staff=False)
    params.filter_search_type = search_type
    params.filter_search_criteria = criteria
    params = set_search_params_criteria(params)
    base_query: str = search_utils.ACCOUNT_SEARCH_HISTORY_BASE
    query: str = search_utils.build_account_query_filter(base_query, params)
    # logger.info(query)
    if params.has_filter():
        assert query.find(filter_clause) != -1


@pytest.mark.parametrize('search_type,client_ref,username,start_ts,end_ts,filter_clause', TEST_QUERY_FILTER_DATA)
def test_account_filter_query(session, search_type, client_ref, username, start_ts, end_ts, filter_clause):
    """Assert that account search history filter query is as expected."""
    params: AccountSearchParams = AccountSearchParams(account_id='PS12345', sbc_staff=False)
    params.filter_search_type = search_type
    params.filter_client_reference_id = client_ref
    params.filter_username = username
    if start_ts and end_ts:
        params.filter_start_date = model_utils.format_ts(model_utils.today_ts_offset(start_ts, False))
        params.filter_end_date = model_utils.format_ts(model_utils.today_ts_offset(end_ts, False))
    query: str = search_utils.build_search_history_query(params)
    if params.has_filter():
        assert query.find(filter_clause) != -1
    assert query.find(' ORDER BY ') != -1
    assert query.find(search_utils.QUERY_ACCOUNT_HISTORY_LIMIT) != -1


@pytest.mark.parametrize('search_type,client_ref,username,start_ts,end_ts,filter_clause', TEST_QUERY_FILTER_DATA)
def test_account_query_params(session, search_type,client_ref,username,start_ts,end_ts,filter_clause):
    """Assert that account search history query params are as expected."""
    params: AccountSearchParams = AccountSearchParams(account_id='PS12345', sbc_staff=False)
    params.filter_search_type = search_type
    params.filter_client_reference_id = client_ref
    params.filter_username = username
    if start_ts and end_ts:
        params.filter_start_date = model_utils.format_ts(model_utils.today_ts_offset(start_ts, False))
        params.filter_end_date = model_utils.format_ts(model_utils.today_ts_offset(end_ts, False))
    params.page_number = 1
    query_params: dict = search_utils.build_account_query_params(params)
    # print('query_params:')
    # print(query_params)
    assert query_params.get('query_account')
    assert query_params.get('page_size')
    assert 'page_offset' in query_params
    if params.filter_search_type and params.filter_search_type not in ('PPR', 'MHR'):
        assert query_params.get('query_type')
    else:
        assert 'query_type' not in query_params
    if params.filter_search_criteria:
        assert query_params.get('query_criteria')
    else:
        assert 'query_criteria' not in query_params
    if params.filter_client_reference_id:
        assert query_params.get('query_client_ref')
    else:
        assert 'query_client_ref' not in query_params
    if params.filter_username:
        assert query_params.get('query_username')
    else:
        assert 'query_username' not in query_params
    if params.filter_start_date and params.filter_end_date:
        assert query_params.get('query_start')
        assert query_params.get('query_end')
    else:
        assert 'query_start' not in query_params
        assert 'query_end' not in query_params


@pytest.mark.parametrize('search_type,criteria,filter_clause', TEST_QUERY_CRITERIA_DATA)
def test_account_criteria_params(session, search_type,criteria,filter_clause):
    """Assert that account search history query params filtering by criteria are as expected."""
    params: AccountSearchParams = AccountSearchParams(account_id='PS12345', sbc_staff=False)
    params.filter_search_type = search_type
    params.filter_search_criteria = criteria
    params = set_search_params_criteria(params)
    # logger.info(f"{params.filter_search_type} {params.filter_search_criteria} {params.filter_first_name} {params.filter_last_name}")
    params.page_number = 1
    query_params: dict = search_utils.build_account_query_params(params)
    # logger.info(query_params)
    # print(query_params)
    assert query_params.get('query_account')
    assert query_params.get('page_size')
    assert 'page_offset' in query_params
    if params.filter_search_type:
        assert query_params.get('query_type')
    else:
        assert 'query_type' not in query_params
    if params.filter_search_criteria:
        assert query_params.get('query_criteria')


def is_ci_testing() -> bool:
    """Check unit test environment: exclude most reports for CI testing."""
    return  current_app.config.get("DEPLOYMENT_ENV", "testing") == "testing"
