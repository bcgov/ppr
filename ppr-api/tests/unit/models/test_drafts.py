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

"""Tests to assure the Draft Model.

Test-Suite to ensure that the Draft Model is working as expected.
"""
import copy
from http import HTTPStatus

from flask import current_app

import pytest
from registry_schemas.example_data.ppr import DRAFT_AMENDMENT_STATEMENT, DRAFT_CHANGE_STATEMENT

from ppr_api.exceptions import BusinessException
from ppr_api.models import Draft, utils as model_utils
from ppr_api.models.utils import now_ts
from ppr_api.models.registration_utils import AccountRegistrationParams


# testdata pattern is ({sort_criteria}, {sort_order}, {expected_clause})
TEST_QUERY_ORDER_DATA = [
    (None, None, ' ORDER BY create_ts DESC'),
    ('invalid', None, ' ORDER BY create_ts DESC'),
    ('registrationNumber', None, ' ORDER BY document_number DESC'),
    ('registrationNumber', 'asc', ' ORDER BY document_number asc'),
    ('registrationType', 'ascending', ' ORDER BY registration_type ascending'),
    ('registeringName', 'descending', ' ORDER BY registering_name descending'),
    ('clientReferenceId', 'asc', ' ORDER BY client_reference_id asc'),
    ('startDateTime', 'ascending', ' ORDER BY create_ts ascending'),
    ('endDateTime', 'desc', ' ORDER BY create_ts desc')
]

# testdata pattern is ({doc_num}, {reg_type}, {client_ref}, {registering_name}, {start_ts}, {end_ts})
TEST_QUERY_BASE_DATA = [
    (None, None, None, None, None, None),
    ('D-T', None, None, None, None, None),
    ('d-t', None, None, None, None, None),
    (None, 'SA', None, None, None, None),
    (None, 'AM', None, None, None, None),
    (None, None, 'A-00000', None, None, None),
    (None, None, None, 'TEST U', None, None),
    (None, None, None, None, '2022-01-22T16:00:00+00:00', '2022-01-28T16:00:00+00:00'),
    ('D-T-', None, 'A-00000', None, None, None),
    ('D-T-', None, None, None, '2022-01-22T16:00:00+00:00', '2022-01-28T16:00:00+00:00'),
    (None, 'SA', None, None, '2022-01-22T16:00:00+00:00', '2022-01-28T16:00:00+00:00')
]


def test_find_all_by_account_id(session):
    """Assert that the draft summary list items contains all expected elements."""
    draft_list = Draft.find_all_by_account_id('PS12345', None, True)
    # print(draft_list)
    assert draft_list
    for draft in draft_list:
        assert draft['type']
        assert draft['documentId']
        assert draft['registrationType']
        assert draft['registrationDescription']
        assert draft['createDateTime']
        assert draft['lastUpdateDateTime']
        assert 'clientReferenceId' in draft
        assert draft['path']
        assert 'registeringParty' in draft
        assert 'securedParties' in draft
        assert draft['registeringName']
        if draft['type'] != 'FINANCING_STATEMENT':
            assert draft['baseRegistrationNumber']
        assert draft['documentId'] != 'D-T-0001'


def test_find_by_document_id_financing(session):
    """Assert that the find draft financing statement by document id contains all expected elements."""
    draft = Draft.find_by_document_number('D-T-FS01', True)
    assert draft
    json_data = draft.json
    assert json_data['financingStatement']
    assert json_data['type'] == 'FINANCING_STATEMENT'
    assert json_data['financingStatement']['securedParties'][0]
    assert json_data['financingStatement']['debtors'][0]
    assert json_data['financingStatement']['vehicleCollateral'][0]
    assert json_data['financingStatement']['lifeYears']


def test_find_by_document_id_change(session):
    """Assert that the find draft change statement by document id contains all expected elements."""
    draft = Draft.find_by_document_number('D-T-CH01', True)
    assert draft
    json_data = draft.json
    assert json_data['changeStatement']
    assert json_data['type'] == 'CHANGE_STATEMENT'
    assert json_data['changeStatement']['registeringParty']
    assert json_data['changeStatement']['baseRegistrationNumber']
    assert json_data['changeStatement']['changeType']


def test_find_by_document_id_amendment(session):
    """Assert that the find draft amendment statement by document id contains all expected elements."""
    draft = Draft.find_by_document_number('D-T-AM01', True)
    assert draft
    json_data = draft.json
    assert json_data['amendmentStatement']
    assert json_data['type'] == 'AMENDMENT_STATEMENT'
    assert json_data['amendmentStatement']['registeringParty']
    assert json_data['amendmentStatement']['baseRegistrationNumber']
    assert json_data['amendmentStatement']['changeType']


def test_find_by_account_id_no_result(session):
    """Assert that the find draft statement by invalid account ID returns the expected result."""
    drafts = Draft.find_all_by_account_id('X12345X', None, True)

    # check
    assert len(drafts) == 0


def test_find_by_document_id_invalid(session):
    """Assert that the find draft statement by invalid document returns the expected result."""
    with pytest.raises(BusinessException) as not_found_err:
        Draft.find_by_document_number('X12345X', False)

    # check
    assert not_found_err
    assert not_found_err.value.status_code == HTTPStatus.NOT_FOUND


def test_save_then_delete(session):
    """Assert that a save then delete draft statement returns the expected result."""
    json_data = copy.deepcopy(DRAFT_CHANGE_STATEMENT)

    new_draft = Draft.create_from_json(json_data, 'PS12345')
    new_draft.save()
    draft = new_draft.json
    assert draft
    assert draft['changeStatement']
    assert draft['type'] == 'CHANGE_STATEMENT'
    assert draft['createDateTime']
    assert draft['changeStatement']['registeringParty']
    assert draft['changeStatement']['baseRegistrationNumber']
    assert draft['changeStatement']['changeType']
    assert draft['changeStatement']['documentId']

    # Now test delete draft
    document_id = draft['changeStatement']['documentId']
    delete_draft = Draft.delete(document_id)
    assert delete_draft


def test_update(session):
    """Assert that a valid update draft statement returns the expected result."""
    json_data = copy.deepcopy(DRAFT_CHANGE_STATEMENT)
    updated = Draft.update(json_data, 'D-T-CH01')
    updated.save()
    draft = updated.json
    assert draft
    assert draft['changeStatement']
    assert draft['type'] == 'CHANGE_STATEMENT'
    assert draft['createDateTime']
    assert draft['lastUpdateDateTime']
    assert draft['changeStatement']['registeringParty']
    assert draft['changeStatement']['baseRegistrationNumber']
    assert draft['changeStatement']['changeType']
    assert draft['changeStatement']['documentId']


def test_update_invalid(session):
    """Assert that an update draft statement with a non-existent document id returns the expected result."""
    json_data = copy.deepcopy(DRAFT_CHANGE_STATEMENT)

    with pytest.raises(BusinessException) as not_found_err:
        Draft.update(json_data, 'X12345X')

    # check
    assert not_found_err
    assert not_found_err.value.status_code == HTTPStatus.NOT_FOUND


def test_delete_bad_id(session):
    """Assert that delete by invalid document ID works as expected."""
    with pytest.raises(BusinessException) as not_found_err:
        Draft.delete('X12345X')

    # check
    assert not_found_err
    assert not_found_err.value.status_code == HTTPStatus.NOT_FOUND


def test_draft_json(session):
    """Assert that the draft renders to a json format correctly."""
    json_data = copy.deepcopy(DRAFT_CHANGE_STATEMENT)
    draft = Draft(
        document_number='TEST1234',
        account_id='PS12345',
        create_ts=now_ts(),
        registration_type=json_data['changeStatement']['changeType'],
        registration_type_cl='CHANGE',
        draft=json_data,  # json.dumps(json_data),
        registration_number=json_data['changeStatement']['baseRegistrationNumber']
    )

    draft_json = draft.json
    assert draft_json
    assert draft_json['type'] == 'CHANGE_STATEMENT'


def test_draft_create_from_json(session):
    """Assert that the draft creates from json data correctly."""
    json_data = copy.deepcopy(DRAFT_CHANGE_STATEMENT)
    draft = Draft.create_from_json(json_data, 'PS12345')

    assert draft.draft
    assert draft.account_id == 'PS12345'
    assert draft.registration_type_cl == 'CHANGE'
    assert draft.registration_type == json_data['changeStatement']['changeType']
    assert draft.registration_number == json_data['changeStatement']['baseRegistrationNumber']

    json_data = copy.deepcopy(DRAFT_AMENDMENT_STATEMENT)
    draft = Draft.create_from_json(json_data, 'PS12345')

    assert draft.draft
    assert draft.account_id == 'PS12345'
    assert draft.registration_type_cl == 'COURTORDER'
    assert draft.registration_type == 'CO'
    assert draft.registration_number == json_data['amendmentStatement']['baseRegistrationNumber']


@pytest.mark.parametrize('sort_criteria,sort_order,value', TEST_QUERY_ORDER_DATA)
def test_account_draft_order(session, sort_criteria, sort_order, value):
    """Assert that account draft query order by clause is as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id='PS12345',
                                                                  collapse=True,
                                                                  account_name='Unit Testing',
                                                                  sbc_staff=False)
    params.sort_criteria = sort_criteria
    params.sort_direction = sort_order
    clause = Draft.get_account_draft_query_order(params)
    assert clause == value


@pytest.mark.parametrize('doc_num,reg_type,client_ref,registering,start_ts,end_ts', TEST_QUERY_BASE_DATA)
def test_account_draft_query(session, doc_num, reg_type, client_ref, registering, start_ts, end_ts):
    """Assert that account draft query is as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id='PS12345',
                                                                  collapse=True,
                                                                  account_name='Unit Testing',
                                                                  sbc_staff=False)
    params.registration_number = doc_num
    params.registration_type = reg_type
    params.client_reference_id = client_ref
    params.registering_name = registering
    params.start_date_time = start_ts
    params.end_date_time = end_ts
    query = Draft.build_account_draft_query(params)
    # current_app.logger.info('\n' + query)
    if params.registration_number:
        assert query.find(model_utils.QUERY_ACCOUNT_DRAFTS_DOC_NUM_CLAUSE) != -1
    if params.registration_type:
        assert query.find(model_utils.QUERY_ACCOUNT_DRAFTS_REG_TYPE_CLAUSE) != -1
    if params.client_reference_id:
        assert query.find(model_utils.QUERY_ACCOUNT_DRAFTS_CLIENT_REF_CLAUSE) != -1
    if params.registering_name:
        assert query.find(model_utils.QUERY_ACCOUNT_DRAFTS_REG_NAME_CLAUSE) != -1
    if params.start_date_time and params.end_date_time:
        assert query.find(model_utils.QUERY_ACCOUNT_DRAFTS_DATE_CLAUSE) != -1
    order_by = Draft.get_account_draft_query_order(params)
    assert query.find(order_by) != -1
    assert query.find(model_utils.QUERY_ACCOUNT_DRAFTS_LIMIT) != -1


@pytest.mark.parametrize('doc_num,reg_type,client_ref,registering,start_ts,end_ts', TEST_QUERY_BASE_DATA)
def test_account_draft_query_params(session, doc_num, reg_type, client_ref, registering, start_ts, end_ts):
    """Assert that account registration dynamically built query params are as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id='PS12345',
                                                                  collapse=True,
                                                                  account_name='Unit Testing',
                                                                  sbc_staff=False)
    params.registration_number = doc_num
    params.registration_type = reg_type
    params.client_reference_id = client_ref
    params.registering_name = registering
    params.start_date_time = start_ts
    params.end_date_time = end_ts
    query_params: dict = Draft.build_account_draft_query_params(params)
    # current_app.logger.info(query_params)
    assert query_params.get('query_account')
    assert query_params.get('max_results_size')

    if params.registration_number:
        assert query_params.get('doc_num')
    else:
        assert 'doc_num' not in query_params
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
    if params.start_date_time and params.end_date_time:
        assert query_params.get('start_date_time')
        assert query_params.get('end_date_time')
    else:
        assert 'start_date_time' not in query_params
        assert 'end_date_time' not in query_params


@pytest.mark.parametrize('doc_num,reg_type,client_ref,registering,start_ts,end_ts', TEST_QUERY_BASE_DATA)
def test_find_all_by_account_id_filter(session, doc_num, reg_type, client_ref, registering, start_ts, end_ts):
    """Assert that account change registration query is as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id='PS12345',
                                                                  collapse=True,
                                                                  account_name='Unit Testing',
                                                                  sbc_staff=False)
    params.from_ui = True
    params.registration_number = doc_num
    params.registration_type = reg_type
    params.client_reference_id = client_ref
    params.registering_name = registering
    if start_ts and end_ts:
        params.start_date_time = start_ts
        params.end_date_time = model_utils.format_ts(model_utils.now_ts())
    draft_list = Draft.find_all_by_account_id_filter(params, True)
    assert draft_list
    for draft in draft_list:
        assert draft['type']
        assert draft['documentId']
        assert draft['registrationType']
        assert draft['registrationDescription']
        assert draft['createDateTime']
        assert draft['lastUpdateDateTime']
        assert 'clientReferenceId' in draft
        assert draft['path']
        assert 'registeringParty' in draft
        assert 'securedParties' in draft
        assert draft['registeringName']
        if draft['type'] != 'FINANCING_STATEMENT':
            assert draft['baseRegistrationNumber']
        assert draft['documentId'] != 'D-T-0001'
