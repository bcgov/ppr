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

from ppr_api.models import FinancingStatement, Registration, registration_utils as registration_utils, \
    utils as model_utils
from ppr_api.models.registration_utils import AccountRegistrationParams


SE_AMEND_REG = {
  'addSecuritiesActNotices': [
        {
            'securitiesActNoticeType': 'LIEN',
            'effectiveDateTime': '2024-04-22T06:59:59+00:00',
            'securitiesActOrders': [
                {
                    'courtOrder': True,
                    'courtName': 'court name',
                    'courtRegistry': 'registry',
                    'fileNumber': 'filenumber',
                    'orderDate': '2024-04-22T06:59:59+00:00',
                    'effectOfOrder': 'effect'
                }
            ]
        }
    ],
    'deleteSecuritiesActNotices': [
        {
            'noticeId': 300000000,
            'securitiesActNoticeType': 'LIEN',
            'effectiveDateTime': '2024-04-22T06:59:59+00:00',
            'securitiesActOrders': [
                {
                    'courtOrder': True,
                    'courtName': 'court name',
                    'courtRegistry': 'registry',
                    'fileNumber': 'filenumber',
                    'orderDate': '2024-04-22T06:59:59+00:00',
                    'effectOfOrder': 'effect'
                }
            ]
        }
    ]
}
# testdata pattern is ({description}, {account_id}, {result_count}, {valid})
TEST_REG_COUNT_DATA = [
    ('Valid Account', 'PS12345', 1, True),
    ('Inalid Account', 'XX12345', 0, False)
]
# testdata pattern is ({sort_criteria}, {sort_order}, {expected_clause})
TEST_QUERY_ORDER_DATA = [
    (None, None, ' ORDER BY registration_ts DESC'),
    ('invalid', None, ' ORDER BY registration_ts DESC'),
    ('registrationNumber', None, ' ORDER BY registration_number DESC'),
    ('registrationNumber', 'asc', ' ORDER BY registration_number asc'),
    ('registrationType', 'ascending', ' ORDER BY registration_type ascending'),
    ('registeringName', 'descending', ' ORDER BY registering_name descending'),
    ('clientReferenceId', 'asc', ' ORDER BY client_reference_id asc'),
    ('startDateTime', 'ascending', ' ORDER BY registration_ts ascending'),
    ('endDateTime', 'desc', ' ORDER BY registration_ts desc')
]

# testdata pattern is ({reg_num}, {reg_type}, {client_ref}, {registering_name}, {status}, {start_ts}, {end_ts})
TEST_QUERY_BASE_DATA = [
    (None, None, None, None, None, None, None),
    ('TEST', None, None, None, None, None, None),
    ('TEST0018A', None, None, None, None, None, None),
    ('test', None, None, None, None, None, None),
    (None, 'SA', None, None, None, None, None),
    (None, None, 'TEST-SA-00', None, None, None, None),
    (None, None, None, 'TEST U', None, None, None),
    (None, None, None, None, 'HDC', None, None),
    (None, None, None, None, None, '2021-09-02T16:00:00+00:00', '2022-01-28T16:00:00+00:00'),
    ('TEST0', None, 'TEST-SA-00', None, None, None, None),
    ('TEST0', None, None, None, None, '2021-09-02T16:00:00+00:00', '2022-01-28T16:00:00+00:00'),
    (None, 'SA', None, None, None, '2021-09-02T16:00:00+00:00', '2022-01-28T16:00:00+00:00')
]
# testdata pattern is ({reg_num}, {client_ref}, {start_ts}, {end_ts})
TEST_FILTER_API_DATA = [
    (None, None, None, None),
    ('TEST', None, None, None),
    ('TEST0018A', None, None, None),
    ('test', None, None, None),
    (None, 'TEST-SA-00', None, None),
    (None, 'SA', None, None),
    (None, None, '2021-09-02T16:00:00+00:00', '2022-01-28T16:00:00+00:00'),
    ('TEST0', 'TEST-SA-00', None, None),
    ('TEST0', None, '2021-09-02T16:00:00+00:00', '2022-01-28T16:00:00+00:00')
]
# testdata pattern is ({description}, {has_add}, {result_count})
TEST_AMEND_SE_COUNT_DATA = [
    ('No add securites notice', False, 0),
    ('Add securities notice', True, 1)
]
# testdata pattern is ({description}, {reg_num}, {account_id}, {notice_id}, {has_data})
TEST_AMEND_SE_DELETE_DATA = [
    ('Valid', 'TEST0022', 'PS00002', 200000000, True),
    ('No results', 'TEST0022', 'PS00002', 200000001, False)
]
# testdata pattern is ({reg_id}, {reg_num}, {account_id_remove}, {account_id_add})
TEST_ADD_REMOVE_DATA = [
    (200000005, 'TEST0005', 'PS12345', 'PS12345_R')
]


@pytest.mark.parametrize('reg_id,reg_num,account_id_before,account_id_after', TEST_ADD_REMOVE_DATA)
def test_add_remove_account_reg(session, reg_id, reg_num, account_id_before, account_id_after):
    """Assert that removing a registration from an account and restoring it works as expected."""
    registration: Registration = Registration.find_by_id(reg_id)
    assert registration.account_id == account_id_before
    assert registration.registration_num == reg_num
    registration_utils.update_account_reg_remove(account_id_before, reg_num)
    registration: Registration = Registration.find_by_id(reg_id)
    # assert registration.account_id == account_id_after
    registration_utils.update_account_reg_restore(account_id_before, reg_num)
    registration: Registration = Registration.find_by_id(reg_id)
    assert registration.account_id == account_id_before


@pytest.mark.parametrize('desc,reg_num,account_id,notice_id,has_data', TEST_AMEND_SE_DELETE_DATA)
def test_find_securities_notice_by_id(session, desc, reg_num, account_id, notice_id, has_data):
    """Assert that SE amendment get notice count works as expected."""
    statement: FinancingStatement = FinancingStatement.find_by_registration_number(reg_num, account_id, False)
    notice = registration_utils.find_securities_notice_by_id(notice_id, statement)
    if has_data:
        assert notice
        assert notice.id == notice_id
    else:
        assert not notice


@pytest.mark.parametrize('desc,has_add,result_count', TEST_AMEND_SE_COUNT_DATA)
def test_get_securities_act_notices_count(session, desc, has_add, result_count):
    """Assert that SE amendment get notice count works as expected."""
    statement: FinancingStatement = FinancingStatement.find_by_registration_number('TEST0001', 'PS12345', False)
    json_data = copy.deepcopy(SE_AMEND_REG)
    if not has_add:
        del json_data['addSecuritiesActNotices']
    count: int = registration_utils.get_securities_act_notices_count(statement, json_data)
    assert count == result_count


@pytest.mark.parametrize('desc,account_id,result_count,valid', TEST_REG_COUNT_DATA)
def test_get_account_reg_count(session, desc, account_id, result_count, valid):
    """Assert that account registrations count works as expected."""
    count: int = Registration.get_account_reg_count(account_id)
    if valid:
        assert count >= result_count
    else:
        assert count == 0


@pytest.mark.parametrize('sort_criteria,sort_order,value', TEST_QUERY_ORDER_DATA)
def test_account_reg_order(session, sort_criteria, sort_order, value):
    """Assert that account registration query order by clause is as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id='PS12345',
                                                                  collapse=True,
                                                                  account_name='Unit Testing',
                                                                  sbc_staff=False)
    params.sort_criteria = sort_criteria
    params.sort_direction = sort_order
    clause = registration_utils.get_account_reg_query_order(params)
    assert clause == value


@pytest.mark.parametrize('reg_num,reg_type,client_ref,registering,status,start_ts,end_ts', TEST_QUERY_BASE_DATA)
def test_account_reg_base_query(session, reg_num, reg_type, client_ref, registering, status, start_ts, end_ts):
    """Assert that account registration query base is as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id='PS12345',
                                                                  collapse=True,
                                                                  account_name='Unit Testing',
                                                                  sbc_staff=False)
    params.registration_number = reg_num
    params.registration_type = reg_type
    params.client_reference_id = client_ref
    params.registering_name = registering
    params.status_type = status
    params.start_date_time = start_ts
    params.end_date_time = end_ts
    query = registration_utils.build_account_reg_base_query(params, True)
    if params.registration_number:
        assert query.find(registration_utils.QUERY_ACCOUNT_REG_NUM_CLAUSE) != -1
    if params.registration_type:
        assert query.find(registration_utils.QUERY_ACCOUNT_REG_TYPE_CLAUSE) != -1
    # if params.client_reference_id:
    #     assert query.find(registration_utils.QUERY_ACCOUNT_CLIENT_REF_CLAUSE) != -1
    # if params.registering_name:
    #     assert query.find(registration_utils.QUERY_ACCOUNT_REG_NAME_CLAUSE) != -1
    if params.status_type:
        assert query.find(registration_utils.QUERY_ACCOUNT_STATUS_CLAUSE) != -1
    if params.start_date_time and params.end_date_time:
        date_clause = registration_utils.build_reg_date_clause(params, True)
        assert query.find(date_clause) != -1


@pytest.mark.parametrize('reg_num,reg_type,client_ref,registering,status,start_ts,end_ts', TEST_QUERY_BASE_DATA)
def test_account_change_base_query(session, reg_num, reg_type, client_ref, registering, status, start_ts, end_ts):
    """Assert that account change registration query base is as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id='PS12345',
                                                                  collapse=True,
                                                                  account_name='Unit Testing',
                                                                  sbc_staff=False)
    params.registration_number = reg_num
    params.registration_type = reg_type
    params.client_reference_id = client_ref
    params.registering_name = registering
    params.status_type = status
    params.start_date_time = start_ts
    params.end_date_time = end_ts
    query = registration_utils.build_account_change_base_query(params)
    # current_app.logger.debug('change base query:')
    # current_app.logger.debug('\n' + query)
    if params.registration_number:
        assert query.find(registration_utils.QUERY_ACCOUNT_CHANGE_REG_NUM_CLAUSE) != -1
    if params.registration_type:
        assert query.find(registration_utils.QUERY_ACCOUNT_CHANGE_REG_TYPE_CLAUSE) != -1
    if params.client_reference_id:
        assert query.find(registration_utils.QUERY_ACCOUNT_CHANGE_CLIENT_REF_CLAUSE) != -1
    if params.registering_name:
        assert query.find(registration_utils.QUERY_ACCOUNT_CHANGE_REG_NAME_CLAUSE) != -1
    if params.status_type:
        assert query.find(registration_utils.QUERY_ACCOUNT_CHANGE_STATUS_CLAUSE) != -1
    if params.start_date_time and params.end_date_time:
        date_clause = registration_utils.build_reg_date_clause(params, False)
        assert query.find(date_clause) != -1
    assert query.find(registration_utils.QUERY_ACCOUNT_REG_LIMIT) != -1


@pytest.mark.parametrize('reg_num,reg_type,client_ref,registering,status,start_ts,end_ts', TEST_QUERY_BASE_DATA)
def test_account_reg_query(session, reg_num, reg_type, client_ref, registering, status, start_ts, end_ts):
    """Assert that account registration dynamically built query is as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id='PS12345',
                                                                  collapse=True,
                                                                  account_name='Unit Testing',
                                                                  sbc_staff=False)
    params.registration_number = reg_num
    params.registration_type = reg_type
    params.client_reference_id = client_ref
    params.registering_name = registering
    params.status_type = status
    params.start_date_time = start_ts
    params.end_date_time = end_ts
    query = registration_utils.build_account_reg_query(params, True)
    # current_app.logger.debug('reg query:')
    # current_app.logger.debug('\n' + query)
    if params.registration_number:
        assert query.find(registration_utils.QUERY_ACCOUNT_REG_NUM_CLAUSE) != -1
    if params.registration_type:
        assert query.find(registration_utils.QUERY_ACCOUNT_REG_TYPE_CLAUSE) != -1
    # if params.client_reference_id:
    #    assert query.find(registration_utils.QUERY_ACCOUNT_CLIENT_REF_CLAUSE) != -1
    # if params.registering_name:
    #    assert query.find(registration_utils.QUERY_ACCOUNT_REG_NAME_CLAUSE) != -1
    if params.status_type:
        assert query.find(registration_utils.QUERY_ACCOUNT_STATUS_CLAUSE) != -1
    if params.start_date_time and params.end_date_time:
        date_clause = registration_utils.build_reg_date_clause(params, True)
        assert query.find(date_clause) != -1
    assert query.find(' ORDER BY ') != -1
    assert query.find(registration_utils.QUERY_ACCOUNT_REG_LIMIT) != -1


@pytest.mark.parametrize('reg_num,reg_type,client_ref,registering,status,start_ts,end_ts', TEST_QUERY_BASE_DATA)
def test_account_change_query(session, reg_num, reg_type, client_ref, registering, status, start_ts, end_ts):
    """Assert that account change registration query is as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id='PS12345',
                                                                  collapse=True,
                                                                  account_name='Unit Testing',
                                                                  sbc_staff=False)
    params.registration_number = reg_num
    params.registration_type = reg_type
    params.client_reference_id = client_ref
    params.registering_name = registering
    params.status_type = status
    params.start_date_time = start_ts
    params.end_date_time = end_ts
    query = registration_utils.build_account_change_query(params)
    # current_app.logger.debug('change query:')
    # current_app.logger.debug('\n' + query)
    if params.registration_number:
        assert query.find(registration_utils.QUERY_ACCOUNT_CHANGE_REG_NUM_CLAUSE) != -1
    if params.registration_type:
        assert query.find(registration_utils.QUERY_ACCOUNT_CHANGE_REG_TYPE_CLAUSE) != -1
    if params.client_reference_id:
        assert query.find(registration_utils.QUERY_ACCOUNT_CHANGE_CLIENT_REF_CLAUSE) != -1
    if params.registering_name:
        assert query.find(registration_utils.QUERY_ACCOUNT_CHANGE_REG_NAME_CLAUSE) != -1
    if params.status_type:
        assert query.find(registration_utils.QUERY_ACCOUNT_CHANGE_STATUS_CLAUSE) != -1
    if params.start_date_time and params.end_date_time:
        date_clause = registration_utils.build_reg_date_clause(params, False)
        assert query.find(date_clause) != -1
    assert query.find(registration_utils.QUERY_ACCOUNT_REG_LIMIT) != -1


@pytest.mark.parametrize('reg_num,reg_type,client_ref,registering,status,start_ts,end_ts', TEST_QUERY_BASE_DATA)
def test_account_query_params(session, reg_num, reg_type, client_ref, registering, status, start_ts, end_ts):
    """Assert that account registration dynamically built query is as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id='PS12345',
                                                                  collapse=True,
                                                                  account_name='Unit Testing',
                                                                  sbc_staff=False)
    params.registration_number = reg_num
    params.registration_type = reg_type
    params.client_reference_id = client_ref
    params.registering_name = registering
    params.status_type = status
    params.start_date_time = start_ts
    params.end_date_time = end_ts
    params.page_number = 1
    query_params: dict = registration_utils.build_account_query_params(params)
    # print('query_params:')
    # print(query_params)
    assert query_params.get('query_account')
    assert query_params.get('page_size')
    assert 'page_offset' in query_params

    if params.registration_number:
        assert query_params.get('reg_num')
    else:
        assert 'reg_num' not in query_params
    if params.registration_type:
        assert query_params.get('registration_type')
    else:
        assert 'registration_type' not in query_params
    if params.client_reference_id:
        assert query_params.get('client_reference_id')
    else:
        assert 'client_reference_id' not in query_params
    if params.registering_name:
        assert query_params.get('registering_name')
    else:
        assert 'registering_name' not in query_params
    if params.status_type:
        assert query_params.get('status_type')
    else:
        assert 'status_type' not in query_params
    assert 'start_date_time' not in query_params
    assert 'end_date_time' not in query_params


@pytest.mark.parametrize('reg_num,reg_type,client_ref,registering,status,start_ts,end_ts', TEST_QUERY_BASE_DATA)
def test_find_all_by_account_id_filter(session, reg_num, reg_type, client_ref, registering, status, start_ts, end_ts):
    """Assert that the account registration filter works is as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id='PS12345',
                                                                  collapse=True,
                                                                  account_name='Unit Testing',
                                                                  sbc_staff=False)
    params.registration_number = reg_num
    params.registration_type = reg_type
    params.client_reference_id = client_ref
    params.registering_name = registering
    params.status_type = status
    if start_ts and end_ts:
        params.start_date_time = start_ts
        params.end_date_time = model_utils.format_ts(model_utils.now_ts())
    statement_list = Registration.find_all_by_account_id_filter(params, True)
    assert statement_list
    assert statement_list[0]['totalRegistrationCount']
    for statement in statement_list:
        assert statement['registrationNumber']
        assert statement['registrationType']
        assert statement['registrationClass']
        assert statement['registrationDescription']
        assert statement['statusType']
        assert statement['createDateTime']
        assert statement['lastUpdateDateTime']
        assert statement['expireDays']
        assert statement['registeringParty']
        assert statement['securedParties']
        assert 'vehicleCount' in statement
        # current_app.logger.info('base reg_num=' + statement.get('registrationNumber'))
        if statement['registrationNumber'] == ('TEST0016'):
            assert statement['registeringName'] == ''
            assert statement['clientReferenceId'] == ''
        elif statement['registrationNumber'] not in ('TEST0019', 'TEST0021'):
            assert statement['registeringName']
            assert statement['clientReferenceId']
        if statement['registrationNumber'] in ('TEST0019', 'TEST0021'):
            assert not statement['path']
        elif not is_ci_testing():
            assert statement['path']
        assert statement['baseRegistrationNumber']
        if reg_num == 'TEST0018A':
            assert len(statement['changes']) > 0
        if 'changes' in statement:
            for change in statement['changes']:
                # current_app.logger.info('reg_num=' + change.get('registrationNumber'))
                assert change['registrationNumber']
                assert change['baseRegistrationNumber']
                assert change['registrationType']
                assert change['registrationClass']
                assert change['registrationDescription']
                assert change['createDateTime']
                assert change['registeringParty']
                assert change['securedParties']
                if change['baseRegistrationNumber'] not in ('TEST0019', 'TEST0021'):
                    assert change['registeringName']
                    assert change['clientReferenceId']
                if not is_ci_testing():
                    assert 'path' in change
                assert 'legacy' in change
                #if change['baseRegistrationNumber'] in ('TEST0019', 'TEST0021'):
                #    assert not change['path']
                #elif change.get('registrationNumber', '') in ('TEST00D4', 'TEST00R5', 'TEST0007'):
                #    assert not change['path']
                #else:
                #    assert change['path']


@pytest.mark.parametrize('reg_num,client_ref,start_ts,end_ts', TEST_FILTER_API_DATA)
def test_find_all_by_account_id_api_filter(session, reg_num, client_ref, start_ts, end_ts):
    """Assert that the api account registration filter works is as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id='PS12345',
                                                                  collapse=True,
                                                                  account_name='Unit Testing',
                                                                  sbc_staff=False)
    params.from_ui = False
    params.registration_number = reg_num
    params.client_reference_id = client_ref
    if start_ts and end_ts:
        params.start_date_time = start_ts
        params.end_date_time = model_utils.format_ts(model_utils.now_ts())
    statement_list = Registration.find_all_by_account_id_api_filter(params, True)
    assert statement_list
    assert 'totalRegistrationCount' not in statement_list[0]
    for statement in statement_list:
        assert statement['registrationNumber']
        assert statement['registrationType']
        assert statement['registrationClass']
        assert statement['registrationDescription']
        assert statement['statusType']
        assert statement['createDateTime']
        assert statement['lastUpdateDateTime']
        assert statement['expireDays']
        assert statement['registeringParty']
        assert statement['securedParties']
        assert 'legacy' in statement
        assert 'vehicleCount' not in statement
        if statement['registrationNumber'] == ('TEST0016'):
            assert statement['registeringName'] == ''
            assert statement['clientReferenceId'] == ''
        elif statement['registrationNumber'] not in ('TEST0019', 'TEST0021'):
            assert statement['registeringName']
            assert statement['clientReferenceId']
        if statement['registrationNumber'] in ('TEST0019', 'TEST0021'):
            assert not statement['path']
        elif not is_ci_testing():
            assert statement['path']
        assert statement['baseRegistrationNumber']
        if reg_num == 'TEST0018A':
            assert len(statement['changes']) > 0
        if 'changes' in statement:
            for change in statement['changes']:
                assert change['registrationNumber']
                assert change['baseRegistrationNumber']
                assert change['registrationType']
                assert change['registrationClass']
                assert change['registrationDescription']
                assert change['createDateTime']
                assert change['registeringParty']
                assert change['securedParties']
                if change['baseRegistrationNumber'] not in ('TEST0019', 'TEST0021'):
                    assert change['registeringName']
                    assert change['clientReferenceId']
                if not is_ci_testing():
                    assert 'path' in change
                assert 'legacy' in change
                # if change['baseRegistrationNumber'] in ('TEST0019', 'TEST0021'):
                #    assert not change['path']
                # elif change.get('registrationNumber', '') == 'TEST00D4':
                #    assert not change['path']
                # else:
                #    assert change['path']



def is_ci_testing() -> bool:
    """Check unit test environment: exclude most reports for CI testing."""
    return  current_app.config.get("DEPLOYMENT_ENV", "testing") == "testing"
