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
"""Test Suite to ensure the model utility functions are working as expected."""
from datetime import timedelta as _timedelta

import pytest

from flask import current_app

from mhr_api.models import utils as model_utils, queries, registration_utils as reg_utils
from mhr_api.models.registration_utils import AccountRegistrationParams


# testdata pattern is ({start_ts}, {end_ts})
TEST_DATA_MANUFACTURER_MHREG = [
    ('2023-05-25T07:01:00+00:00', '2023-05-26T07:01:00+00:00'),
    (None, '2023-05-26T07:01:00+00:00'),
    ('2023-05-25T07:01:00+00:00', None),
    (None, None)
]
# testdata pattern is ({start_ts}, {end_ts})
TEST_DATA_MANUFACTURER_MHREG_UPDATE = [
    ('2023-05-25T07:01:00+00:00', '2023-05-26T07:01:00+00:00'),
    (None, None)
]
# testdata pattern is ({description}, {mhr_number}, {ppr_reg_type})
TEST_DATA_PPR_REG_TYPE = [
    ('Valid request no lien', '100000', None)
]
# testdata pattern is ({description}, {mhr_number}, {valid})
TEST_DATA_MHR_CHECK = [
    ('Valid', '000899', True),
    ('Invalid exists', '000900', False),
    ('Invalid too high', '999900', False)
]
# testdata pattern is ({account_id}, {sort_criteria}, {sort_order}, {mhr_numbers}, {expected_clause})
TEST_QUERY_ORDER_DATA = [
    ('PS12345', None, None, "'000900'", queries.REG_ORDER_BY_DATE),
    ('PS12345', 'invalid', None, "'000900'",  queries.REG_ORDER_BY_DATE),
    ('PS12345', reg_utils.REG_TS_PARAM, None, "'000900'", queries.REG_ORDER_BY_DATE),
    ('PS12345', reg_utils.REG_TYPE_PARAM, reg_utils.SORT_ASCENDING, "'000900'", queries.REG_ORDER_BY_REG_TYPE),
    ('PS12345', reg_utils.SUBMITTING_NAME_PARAM, reg_utils.SORT_DESCENDING, "'000900'",
     queries.REG_ORDER_BY_SUBMITTING_NAME),
    ('PS12345', reg_utils.CLIENT_REF_PARAM, reg_utils.SORT_ASCENDING, "'000900'", queries.REG_ORDER_BY_CLIENT_REF),
    ('PS12345', reg_utils.REG_TS_PARAM, reg_utils.SORT_ASCENDING, "'000900'", queries.REG_ORDER_BY_DATE),
    ('PS12345', reg_utils.STATUS_PARAM, reg_utils.SORT_ASCENDING, "'000900'", queries.REG_ORDER_BY_STATUS),
    ('PS12345', reg_utils.USER_NAME_PARAM, reg_utils.SORT_DESCENDING, "'000900'", queries.REG_ORDER_BY_USERNAME),
    ('PS12345', reg_utils.OWNER_NAME_PARAM, reg_utils.SORT_DESCENDING, "'000900'", queries.REG_ORDER_BY_OWNER_NAME),
    ('PS12345', reg_utils.EXPIRY_DAYS_PARAM, reg_utils.SORT_DESCENDING, "'000900'", queries.REG_ORDER_BY_EXPIRY_DAYS),
    ('PS12345', reg_utils.MHR_NUMBER_PARAM, reg_utils.SORT_ASCENDING, "'000900'", queries.REG_ORDER_BY_MHR_NUMBER)
]

# testdata pattern is ({account_id}, {collapse}, {filter_name}, {filter_value}, {mhr_numbers}, {expected_clause})
TEST_QUERY_FILTER_DATA = [
    ('PS12345', False, reg_utils.SUBMITTING_NAME_PARAM, 'SUBMITTING', "'000903'", queries.REG_FILTER_SUBMITTING_NAME),
    ('PS12345', True, reg_utils.SUBMITTING_NAME_PARAM, 'SUBMIT', "'000905'", queries.REG_FILTER_SUBMITTING_NAME_COLLAPSE),
    ('PS12345', False, reg_utils.USER_NAME_PARAM, 'TEST U', "'000926'", queries.REG_FILTER_USERNAME),
    ('PS12345', True, reg_utils.USER_NAME_PARAM, 'TEST U', "'000900'", queries.REG_FILTER_USERNAME_COLLAPSE),
    ('PS12345', True, reg_utils.REG_TYPE_PARAM, 'TRANSPORT PERMIT', "'000926'",queries.REG_FILTER_REG_TYPE_COLLAPSE),
    ('PS12345', True, reg_utils.REG_TYPE_PARAM, 'REG_103', "'000926'",queries.REG_FILTER_REG_TYPE_COLLAPSE),
    ('PS12345', False, reg_utils.MHR_NUMBER_PARAM, '000900', "'000900'", queries.REG_FILTER_MHR),
    ('PS12345', False, reg_utils.CLIENT_REF_PARAM, 'UT-0010', "'000900'", queries.REG_FILTER_CLIENT_REF),
    ('PS12345', True, reg_utils.CLIENT_REF_PARAM, 'UT-001', "'000907'", queries.REG_FILTER_CLIENT_REF_COLLAPSE),
    ('PS12345', False, reg_utils.REG_TYPE_PARAM, 'TRANSPORT PERMIT', "'000926'", queries.REG_FILTER_REG_TYPE),
    ('PS12345', False, reg_utils.REG_TYPE_PARAM, 'REG_103', "'000926'", queries.REG_FILTER_REG_TYPE),
    ('PS12345', True, reg_utils.STATUS_PARAM, 'EXEMPT', "'000912'", queries.REG_FILTER_STATUS_COLLAPSE),
    ('PS12345', False, reg_utils.STATUS_PARAM, 'EXEMPT', "'000912'", queries.REG_FILTER_STATUS)
]

# testdata pattern is ({account_id}, {collapse}, {start_value}, {end_value}, {mhr_numbers}, {expected_clause})
TEST_QUERY_FILTER_DATA_DATE = [
    ('PS12345', False, '2024-04-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53', "'000900'", queries.REG_FILTER_DATE),
    ('PS12345', True, '2024-04-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53', "'000900'",
     queries.REG_FILTER_DATE_COLLAPSE)
]

# testdata pattern is ({account_id}, {collapse}, {start_value}, {end_value}, {second_filter_name},
#                      {second_filter_value}, {mhr_numbers}, {expected_date_clause}, {expected_second_clause})
TEST_QUERY_FILTER_DATA_MULTIPLE = [
    ('PS12345', False, '2024-04-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53', reg_utils.REG_TYPE_PARAM,
     'TRANSPORT PERMIT', "'000926'", queries.REG_FILTER_DATE, queries.REG_FILTER_REG_TYPE),
    ('PS12345', False, '2024-04-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53', reg_utils.REG_TYPE_PARAM,
     'REG_103', "'000926'", queries.REG_FILTER_DATE, queries.REG_FILTER_REG_TYPE),
    ('PS12345', False, '2024-04-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53', reg_utils.SUBMITTING_NAME_PARAM,
     'SUBMITTING', "'000903'", queries.REG_FILTER_DATE, queries.REG_FILTER_SUBMITTING_NAME),
    ('PS12345', False, '2024-04-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53', reg_utils.CLIENT_REF_PARAM,
     'UT-001', "'000907'", queries.REG_FILTER_DATE, queries.REG_FILTER_CLIENT_REF),
    ('PS12345', False, '2024-04-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53', reg_utils.STATUS_PARAM,
     'EXEMPT', "'000912'", queries.REG_FILTER_DATE, queries.REG_FILTER_STATUS),
    ('PS12345', False, '2024-04-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53', reg_utils.USER_NAME_PARAM,
     'TEST U', "'000926'", queries.REG_FILTER_DATE, queries.REG_FILTER_USERNAME),
    ('PS12345', False, '2024-04-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53', reg_utils.MHR_NUMBER_PARAM,
     '000900', "'000900'", queries.REG_FILTER_DATE, queries.REG_FILTER_MHR)
]


@pytest.mark.parametrize('start_ts,end_ts', TEST_DATA_MANUFACTURER_MHREG)
def test_get_batch_manufacturer_reg_report_data(session, start_ts, end_ts):
    """Assert that fetching manufacturer MHREG data by optional timestamp range works as expected."""
    results_json = reg_utils.get_batch_manufacturer_reg_report_data(start_ts, end_ts)
    if results_json:
        for result in results_json:
            assert result.get('registrationId')
            assert result.get('accountId')
            assert result.get('reportId')
            assert result.get('reportData')
            assert 'batchStorageUrl' in result


def test_get_batch_manufacturer_reg_report_name(session):
    """Assert that fetching manufacturer MHREG data by optional timestamp range works as expected."""
    now_ts = model_utils.now_ts()
    time = str(now_ts.hour) + '_' + str(now_ts.minute)
    test_name: str = reg_utils.BATCH_DOC_NAME_MANUFACTURER_MHREG.format(time=time)
    storage_name: str = reg_utils.get_batch_storage_name_manufacturer_mhreg()
    assert storage_name.find(test_name) > -1


@pytest.mark.parametrize('start_ts,end_ts', TEST_DATA_MANUFACTURER_MHREG_UPDATE)
def test_update_manufacturer_reg_report_batch_url(session, start_ts, end_ts):
    """Assert that batch updating of the registration report batch storage url works as expected."""
    results_json = reg_utils.get_batch_manufacturer_reg_report_data(start_ts, end_ts)
    if results_json:
        batch_url: str = reg_utils.get_batch_storage_name_manufacturer_mhreg()
        update_count: int = reg_utils.update_reg_report_batch_url(results_json, batch_url)
        assert update_count > 0


@pytest.mark.parametrize('desc, mhr_number, ppr_reg_type', TEST_DATA_PPR_REG_TYPE)
def test_validate_ppr_reg_type(session, desc, mhr_number, ppr_reg_type):
    """Assert that the PPR reg type query works as expected."""
    reg_type = reg_utils.get_ppr_registration_type(mhr_number)
    assert reg_type == ppr_reg_type


@pytest.mark.parametrize('desc, mhr_number, valid', TEST_DATA_MHR_CHECK)
def test_validate_mhr_number(session, desc, mhr_number, valid):
    """Assert that the staff new MH MHR number check works as expected."""
    result: bool = reg_utils.validate_mhr_number(mhr_number)
    assert result == valid


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
            order_clause = order_clause.replace(queries.ACCOUNT_SORT_DESCENDING, queries.ACCOUNT_SORT_ASCENDING)
    elif params.has_sort():
        if params.sort_direction and params.sort_direction == reg_utils.SORT_ASCENDING:
            order_clause += queries.ACCOUNT_SORT_ASCENDING
        else:
            order_clause += queries.ACCOUNT_SORT_DESCENDING

    query: str = reg_utils.build_account_query(params)
    # current_app.logger.debug(query)
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
    reg_list = reg_utils.find_all_by_account_id(params)
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
        filter_clause = filter_clause.replace('?', filter_value)
    elif filter_name == reg_utils.REG_TYPE_PARAM:
        params.filter_registration_type = filter_value
        filter_clause = filter_clause.replace('?', 'REG_103')
    elif filter_name == reg_utils.MHR_NUMBER_PARAM:
        params.filter_mhr_number = filter_value
        filter_clause = filter_clause.replace('?', filter_value)
    else:
        filter_clause = filter_clause.replace('?', filter_value)
    if filter_name == reg_utils.CLIENT_REF_PARAM:
        params.filter_client_reference_id = filter_value
    elif filter_name == reg_utils.SUBMITTING_NAME_PARAM:
        params.filter_submitting_name = filter_value
    elif filter_name == reg_utils.USER_NAME_PARAM:
        params.filter_username = filter_value

    base_query: str = queries.QUERY_ACCOUNT_DEFAULT
    filter_query: str = reg_utils.build_account_query_filter(base_query, params)
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
    params.filter_reg_end_date = model_utils.format_ts(model_utils.now_ts())  # end_value
    base_query: str = queries.QUERY_ACCOUNT_DEFAULT
    filter_query: str = reg_utils.build_account_query_filter(base_query, params)
    # current_app.logger.debug(filter_clause)
    # current_app.logger.debug(filter_query)
    assert filter_query.find(filter_clause) > 0


@pytest.mark.parametrize('account_id,collapse,start_value,end_value,second_filter_name,second_filter_value,mhr_numbers,expected_date_clause,expected_second_clause',
                         TEST_QUERY_FILTER_DATA_MULTIPLE)
def test_account_reg_filter_multiple(session, account_id, collapse, start_value, end_value, second_filter_name,
                                     second_filter_value, mhr_numbers, expected_date_clause, expected_second_clause):
    """Assert that account registration query filter clause is as expected when multiple filters are applied."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id=account_id,
                                                                collapse=collapse,
                                                                sbc_staff=False)
    date_filter_clause: str = expected_date_clause
    second_filter_clause: str = expected_second_clause
    params.filter_reg_start_date = start_value
    params.filter_reg_end_date = model_utils.format_ts(model_utils.now_ts())
    # params.filter_reg_end_date = end_value
    # Set second filter in params and update query
    if second_filter_name == reg_utils.REG_TS_PARAM:
        params.filter_registration_date = second_filter_value
    elif second_filter_name == reg_utils.STATUS_PARAM:
        params.filter_status_type = second_filter_value
        second_filter_clause = second_filter_clause.replace('?', second_filter_value)
    elif second_filter_name == reg_utils.REG_TYPE_PARAM:
        params.filter_registration_type = second_filter_value
        second_filter_clause = second_filter_clause.replace('?', 'REG_103')
    elif second_filter_name == reg_utils.MHR_NUMBER_PARAM:
        params.filter_mhr_number = second_filter_value
        second_filter_clause = second_filter_clause.replace('?', second_filter_value)
    elif second_filter_name == reg_utils.CLIENT_REF_PARAM:
        params.filter_client_reference_id = second_filter_value
        second_filter_clause = second_filter_clause.replace('?', second_filter_value)
    elif second_filter_name == reg_utils.SUBMITTING_NAME_PARAM:
        second_filter_clause = second_filter_clause.replace('?', second_filter_value)
        params.filter_submitting_name = second_filter_value
    elif second_filter_name == reg_utils.USER_NAME_PARAM:
        params.filter_username = second_filter_value
        second_filter_clause = second_filter_clause.replace('?', second_filter_value)

    base_query: str = queries.QUERY_ACCOUNT_DEFAULT
    filter_query: str = reg_utils.build_account_query_filter(base_query, params)

    # current_app.logger.info(filter_query)
    # current_app.logger.info(second_filter_clause)
    assert filter_query.find(date_filter_clause) > 0
    assert filter_query.find(second_filter_clause) > 0


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
        # params.collapse = True
    elif filter_name == reg_utils.MHR_NUMBER_PARAM:
        params.filter_mhr_number = filter_value
    elif filter_name == reg_utils.CLIENT_REF_PARAM:
        params.filter_client_reference_id = filter_value
    elif filter_name == reg_utils.SUBMITTING_NAME_PARAM:
        params.filter_submitting_name = filter_value
    elif filter_name == reg_utils.USER_NAME_PARAM:
        params.filter_username = filter_value

    reg_list = reg_utils.find_all_by_account_id(params)
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
