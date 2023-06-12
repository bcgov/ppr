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
from mhr_api.resources.utils import NOT_FOUND

import pytest
from registry_schemas.example_data.mhr import REGISTRATION

from mhr_api.exceptions import BusinessException
from mhr_api.models import mhr_draft, MhrDraft, utils as model_utils, registration_utils as reg_utils
from mhr_api.models.registration_utils import AccountRegistrationParams
from mhr_api.models.type_tables import MhrRegistrationTypes

DEFAULT_ORDER = mhr_draft.QUERY_ACCOUNT_DRAFTS_DEFAULT_ORDER + mhr_draft.QUERY_ACCOUNT_DRAFTS_LIMIT
DRAFT_TRANSFER = {
  'type': 'TRANS',
  'registration': {
    'mhrNumber': '125234',
    'clientReferenceId': 'EX-TRANS-001',
    'submittingParty': {
      'businessName': 'ABC SEARCHING COMPANY',
      'address': {
        'street': '222 SUMMER STREET',
        'city': 'VICTORIA',
        'region': 'BC',
        'country': 'CA',
        'postalCode': 'V8W 2V8'
      },
      'emailAddress': 'bsmith@abc-search.com',
      'phoneNumber': '6041234567',
      'phoneExtension': '546'
    },
    'deleteOwnerGroups': [
      {
        'groupId': 1,
        'owners': [
          {
            'individualName': {
              'first': 'Jane',
              'last': 'Smith'
            },
            'address': {
              'street': '3122B LYNNLARK PLACE',
              'city': 'VICTORIA',
              'region': 'BC',
              'postalCode': ' ',
              'country': 'CA'
            },
            'phoneNumber': '6041234567'
          }
        ],
        'type': 'SOLE'
      }
    ],
    'addOwnerGroups': [
      {
        'groupId': 2,
        'owners': [
          {
            'individualName': {
              'first': 'James',
              'last': 'Smith'
            },
            'address': {
              'street': '3122B LYNNLARK PLACE',
              'city': 'VICTORIA',
              'region': 'BC',
              'postalCode': ' ',
              'country': 'CA'
            },
            'phoneNumber': '6041234567'
          }
        ],
        'type': 'SOLE',
        'status': 'ACTIVE'
      }
    ],
  }
}
# testdata pattern is ({account_id}, {has_results}, {draft_num}, {mhr_num}, {reg_type})
TEST_ACCOUNT_DRAFT_DATA = [
    ('PS12345', True, 'T500000', None, MhrRegistrationTypes.MHREG),
    ('PS12345', True, 'UT0001', 'UT-001', MhrRegistrationTypes.TRANS),
    ('ppr_staff', True, '101421', '100377', MhrRegistrationTypes.TRANS),
    ('999999', False, None, None, None)
]
# testdata pattern is ({account_id}, {status}, {draft_num}, {mhr_num}, {reg_type})
TEST_DRAFT_DATA = [
    ('PS12345', HTTPStatus.OK, 'T500000', None, MhrRegistrationTypes.MHREG),
    ('PS12345', HTTPStatus.OK, 'UT0001', 'UT-001', MhrRegistrationTypes.TRANS),
    ('ppr_staff', HTTPStatus.OK, '101421', '100377', MhrRegistrationTypes.TRANS),
    ('999999', HTTPStatus.NOT_FOUND, None, None, None),
    ('PS12345', HTTPStatus.BAD_REQUEST, 'T500001', None, None)
]
# testdata pattern is ({account_id}, {mhr_num}, {reg_type}, {draft_data})
TEST_SAVE_DRAFT_DATA = [
    ('PS12345', None, MhrRegistrationTypes.MHREG, REGISTRATION),
    ('PS12345', '125234', MhrRegistrationTypes.TRANS, DRAFT_TRANSFER)
]
# testdata pattern is ({status}, {draft_num}, {reg_type}, {draft_data}, {client_ref})
TEST_UPDATE_DRAFT_DATA = [
    (HTTPStatus.OK, 'T500000', MhrRegistrationTypes.MHREG, REGISTRATION, 'TEST-001'),
    (HTTPStatus.OK, 'UT0001', MhrRegistrationTypes.TRANS, DRAFT_TRANSFER, 'TEST-002'),
    (HTTPStatus.NOT_FOUND, None, None, None, None),
    (HTTPStatus.BAD_REQUEST, 'T500001', None, None, None)
]
# testdata pattern is ({sort_criteria}, {sort_order}, {expected_clause})
TEST_QUERY_ORDER_DATA = [
    (None, None, DEFAULT_ORDER),
    ('invalid', None, DEFAULT_ORDER),
    (reg_utils.REG_TS_PARAM, None, 
     mhr_draft.ORDER_BY_DATE + mhr_draft.SORT_DESCENDING + mhr_draft.QUERY_ACCOUNT_DRAFTS_LIMIT),
    (reg_utils.MHR_NUMBER_PARAM, reg_utils.SORT_DESCENDING,
     mhr_draft.ORDER_BY_MHR_NUMBER + mhr_draft.SORT_DESCENDING + mhr_draft.QUERY_ACCOUNT_DRAFTS_LIMIT),
    (reg_utils.REG_TYPE_PARAM, reg_utils.SORT_ASCENDING,
     mhr_draft.ORDER_BY_REG_TYPE + mhr_draft.SORT_ASCENDING + mhr_draft.QUERY_ACCOUNT_DRAFTS_LIMIT),
    (reg_utils.SUBMITTING_NAME_PARAM, reg_utils.SORT_ASCENDING,
     mhr_draft.ORDER_BY_SUBMITTING_NAME + mhr_draft.SORT_ASCENDING + mhr_draft.QUERY_ACCOUNT_DRAFTS_LIMIT),
    (reg_utils.CLIENT_REF_PARAM, reg_utils.SORT_DESCENDING,
     mhr_draft.ORDER_BY_CLIENT_REF + mhr_draft.SORT_DESCENDING + mhr_draft.QUERY_ACCOUNT_DRAFTS_LIMIT),
    (reg_utils.REG_TS_PARAM, reg_utils.SORT_ASCENDING,
     mhr_draft.ORDER_BY_DATE + mhr_draft.SORT_DESCENDING + mhr_draft.QUERY_ACCOUNT_DRAFTS_LIMIT),
    (reg_utils.USER_NAME_PARAM, reg_utils.SORT_DESCENDING,
     mhr_draft.ORDER_BY_USERNAME + mhr_draft.SORT_DESCENDING + mhr_draft.QUERY_ACCOUNT_DRAFTS_LIMIT)
]
# testdata pattern is ({filter1}, {value1}, {filter2}, {value2}, {clause1}, {clause2})
TEST_QUERY_FILTER_DATA = [
    (reg_utils.MHR_NUMBER_PARAM, '107600', None, None, mhr_draft.FILTER_MHR_NUMBER, None),
    (reg_utils.START_TS_PARAM, '2023-06-01T07:00:00+00:00', reg_utils.END_TS_PARAM, '2023-06-02T07:00:00+00:00', mhr_draft.FILTER_DATE, None),
    (reg_utils.USER_NAME_PARAM, 'USER', None, None, mhr_draft.FILTER_USERNAME, None),
    (reg_utils.SUBMITTING_NAME_PARAM, 'SUBMITTING', None, None, mhr_draft.FILTER_SUBMITTING_NAME, None),
    (reg_utils.REG_TYPE_PARAM, 'REG TYPE', None, None, mhr_draft.FILTER_REG_TYPE, None),
    (reg_utils.CLIENT_REF_PARAM, 'CLIENT', None, None, mhr_draft.FILTER_CLIENT_REF, None)
]


@pytest.mark.parametrize('account_id, has_results, draft_num, mhr_num, reg_type', TEST_ACCOUNT_DRAFT_DATA)
def test_find_all_by_account_id(session, account_id, has_results, draft_num, mhr_num, reg_type):
    """Assert that the draft summary list items contains all expected elements."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id=account_id,
                                                                  sbc_staff=False)
    draft_list = MhrDraft.find_all_by_account_id(params)
    if has_results:
        assert draft_list
        found_draft = False
        found_mhr = False
        for draft in draft_list:
            current_app.logger.info(draft)
            assert draft['draftNumber']
            assert draft['createDateTime']
            assert draft['lastUpdateDateTime']
            assert draft['path']
            assert draft.get('registrationDescription')
            assert draft.get('clientReferenceId')
            assert draft.get('submittingParty')
            if mhr_num and draft.get('mhrNumber') and draft['mhrNumber'] == mhr_num:
                found_mhr = True
            if draft['draftNumber'] == draft_num:
                assert draft['registrationType'] == reg_type
                found_draft = True
            if draft.get('mhrNumber'):
                assert 'outOfDate' in draft
        assert found_draft
        if mhr_num:
            assert found_mhr
    else:
        assert not draft_list


@pytest.mark.parametrize('account_id, status, draft_num, mhr_num, reg_type', TEST_DRAFT_DATA)
def test_find_by_draft_number(session, account_id, status, draft_num, mhr_num, reg_type):
    """Assert that the find draft by draft number contains all expected elements."""
    if status == HTTPStatus.OK:
        draft: MhrDraft = MhrDraft.find_by_draft_number(draft_num, False)
        assert draft
        assert draft.id
        assert draft.account_id == account_id
        assert draft.draft_number == draft_num
        assert draft.draft
        assert draft.create_ts
        assert draft.account_id
        assert draft.user_id
        assert draft.registration_type == reg_type
        if mhr_num:
            assert draft.mhr_number == mhr_num
            draft_json = draft.json
            assert 'outOfDate' in draft_json
    else:
        with pytest.raises(BusinessException) as error:
            MhrDraft.find_by_draft_number(draft_num, False)
        assert error
        assert error.value.status_code == status


@pytest.mark.parametrize('account_id, mhr_num, reg_type, draft_data', TEST_SAVE_DRAFT_DATA)
def test_save_then_delete(session, account_id, mhr_num, reg_type, draft_data):
    """Assert that a save then delete draft statement returns the expected result."""
    json_data = copy.deepcopy(draft_data)
    if mhr_num:
        json_data['mhrNumber'] = mhr_num
    draft_data = {
        'type': reg_type,
        'registration': json_data
    } 
    new_draft: MhrDraft = MhrDraft.create_from_json(draft_data, account_id, 'TESTUSER')
    new_draft.save()
    draft = new_draft.json
    assert draft
    assert draft['type'] == reg_type
    assert draft['createDateTime']
    assert draft['draftNumber']
    assert draft['registration']
    if mhr_num:
        draft['mhrNumber'] = mhr_num

    # Now test delete draft
    draft_number = draft['draftNumber']
    delete_draft = MhrDraft.delete(draft_number)
    assert delete_draft


@pytest.mark.parametrize('status, draft_num, reg_type, draft_data, client_ref', TEST_UPDATE_DRAFT_DATA)
def test_update(session, status, draft_num, reg_type, draft_data, client_ref):
    """Assert that update draft returns the expected result."""
    if status == HTTPStatus.OK:
        json_data = {
            'type': reg_type,
            'registration': copy.deepcopy(draft_data)
        }
        json_data['registration']['clientReferenceId'] = client_ref
        updated = MhrDraft.update(json_data, draft_num)
        # current_app.logger.info(updated.draft)
        updated_json = updated.save()
        # current_app.logger.info(updated_json)
        assert updated_json
        assert updated_json['type'] == reg_type
        assert updated_json['createDateTime']
        assert updated_json['lastUpdateDateTime']
        assert updated_json['draftNumber'] == draft_num
        assert updated_json['registration']
    else:
        with pytest.raises(BusinessException) as error:
            MhrDraft.find_by_draft_number(draft_num, False)
        assert error
        assert error.value.status_code == status


@pytest.mark.parametrize('account_id, status, draft_num, mhr_num, reg_type', TEST_DRAFT_DATA)
def test_delete(session, account_id, status, draft_num, mhr_num, reg_type):
    """Assert that delete draft returns the expected result."""
    if status == HTTPStatus.OK:
        delete_draft = MhrDraft.delete(draft_num)
        assert delete_draft
    else:
        with pytest.raises(BusinessException) as error:
            MhrDraft.find_by_draft_number(draft_num, False)
        assert error
        assert error.value.status_code == status


def test_draft_json(session):
    """Assert that the draft renders to a json format correctly."""
    json_data = {
        'type': MhrRegistrationTypes.MHREG,
        'registration': copy.deepcopy(REGISTRATION)
    }
    draft: MhrDraft = MhrDraft(
        draft_number='TEST1234',
        account_id='PS12345',
        create_ts=model_utils.now_ts(),
        registration_type=json_data['type'],
        draft=json_data['registration']
    )
    draft_json = draft.json
    assert draft_json
    assert draft_json['createDateTime']
    assert draft_json['draftNumber'] == draft.draft_number
    assert draft_json['type'] == draft.registration_type
    assert draft_json['registration'] == draft.draft


def test_draft_create_from_json(session):
    """Assert that the draft is created from json data correctly."""
    json_data = {
        'type': MhrRegistrationTypes.MHREG,
        'registration': copy.deepcopy(REGISTRATION)
    }
    draft: MhrDraft = MhrDraft.create_from_json(json_data, 'PS12345', 'TESTUSER')
    assert draft.draft == json_data['registration']
    assert draft.account_id == 'PS12345'
    assert draft.registration_type == json_data['type']


@pytest.mark.parametrize('sort_criteria,sort_order,expected_clause', TEST_QUERY_ORDER_DATA)
def test_account_order_by(session, sort_criteria, sort_order, expected_clause):
    """Assert that account registration query order by clause is as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id='PS12345',
                                                                  sbc_staff=False)
    params.sort_criteria = sort_criteria
    params.sort_direction = sort_order

    query: str = MhrDraft.build_account_query(params)
    # current_app.logger.debug(query)
    # current_app.logger.debug(expected_clause)
    assert query.endswith(expected_clause) or query.endswith((expected_clause + '\n'))


@pytest.mark.parametrize('filter1,value1,filter2,value2,clause1,clause2', TEST_QUERY_FILTER_DATA)
def test_account_filter(session, filter1, value1, filter2, value2, clause1, clause2):
    """Assert that the account drafts query filter clauses work as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id='PS12345',
                                                                  sbc_staff=False)
    filter_clause: str = clause1
    filter_clause2: str = None
    if filter1 == reg_utils.START_TS_PARAM:
        params.filter_reg_start_date = value1
    else:
        filter_clause = filter_clause.replace('?', value1)      
    if filter1 == reg_utils.REG_TYPE_PARAM:
        params.filter_registration_type = value1
    elif filter1 == reg_utils.MHR_NUMBER_PARAM:
        params.filter_mhr_number = value1
    elif filter1 == reg_utils.CLIENT_REF_PARAM:
        params.filter_client_reference_id = value1
    elif filter1 == reg_utils.SUBMITTING_NAME_PARAM:
        params.filter_submitting_name = value1
    elif filter1 == reg_utils.USER_NAME_PARAM:
        params.filter_username = value1
    if filter2 and value2:
      if filter2 == reg_utils.END_TS_PARAM:
          params.filter_reg_end_date = value2
      elif clause2:
          filter_clause2 = clause2.replace('?', value2)
      if filter2 == reg_utils.REG_TYPE_PARAM:
          params.filter_registration_type = value2
      elif filter2 == reg_utils.MHR_NUMBER_PARAM:
          params.filter_mhr_number = value2
      elif filter2 == reg_utils.CLIENT_REF_PARAM:
          params.filter_client_reference_id = value2
      elif filter2 == reg_utils.SUBMITTING_NAME_PARAM:
          params.filter_submitting_name = value2
      elif filter2 == reg_utils.USER_NAME_PARAM:
          params.filter_username = value2

    base_query: str = mhr_draft.QUERY_ACCOUNT_DRAFTS_BASE
    filter_query: str = MhrDraft.build_account_query_filter(base_query, params)
    #current_app.logger.debug(filter_clause)
    #current_app.logger.debug(filter_query)
    assert filter_query.find(filter_clause) > 0
    if filter_clause2:
      assert filter_query.find(filter_clause2) > 0
