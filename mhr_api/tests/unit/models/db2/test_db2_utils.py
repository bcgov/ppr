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
import copy

from flask import current_app

import pytest
from flask import current_app
from registry_schemas.example_data.mhr import REGISTRATION

from mhr_api.models import registration_utils as reg_utils, MhrRegistration, Db2Manuhome, utils as model_utils
from mhr_api.models.registration_utils import AccountRegistrationParams
from mhr_api.models.db2 import utils as db2_utils, registration_utils as legacy_reg_utils
from mhr_api.models.type_tables import MhrDocumentType, MhrRegistrationTypes


LOCATION = {
  'locationType': 'STRATA',
  'address': {
    'street': '940 BLANSHARD STREET',
    'city': 'VICTORIA',
    'region': 'BC',
    'postalCode': 'V1V 1V1',
    'country': 'CA'
  },
  'leaveProvince': False,
  'pidNumber': '000010626',
  'taxCertificate': True,
  'taxExpiryDate': '2022-05-21T07:59:59+00:00',
  'dealerName': 'NOR-TEC DESIGN GROUP LTD.',
  'exceptionPlan': 'TEST EXCEPTION',
  'additionalDescription': 'TEST DESCRIPTION',
  'legalDescription': 'LOT 14, BLOCK 521, NANOOSE DISTRICT, PLAN 35625'
}
DESCRIPTION = {
  'manufacturer': 'STARLINE',
  'baseInformation': {
    'year': 2018,
    'make': 'HEAVENLY HOMES',
    'model': 'CELESTIAL CASTLE 6000'
  },
  'sectionCount': 1,
  'sections': [
    {
      'serialNumber': '52D70556',
      'lengthFeet': 52,
      'lengthInches': 0,
      'widthFeet': 12,
      'widthInches': 0
    }
  ],
  'csaNumber': '786356',
  'csaStandard': 'Z240',
  'rebuiltRemarks': 'Rebuilt comments',
  'otherRemarks': 'Other comments'
}
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
    ('2523', False, reg_utils.REG_TYPE_PARAM, 'TRANSFER DUE TO SALE OR GIFT', "'098487'",
     db2_utils.REG_FILTER_REG_TYPE),
    ('2523', False, reg_utils.SUBMITTING_NAME_PARAM, 'LINDA', "'098487'", db2_utils.REG_FILTER_SUBMITTING_NAME),
    ('2523', False, reg_utils.CLIENT_REF_PARAM, 'A000873', "'098487'", db2_utils.REG_FILTER_CLIENT_REF),
    ('2523', False, reg_utils.STATUS_PARAM, 'EXEMPT', "'098487'", db2_utils.REG_FILTER_STATUS),
    ('2523', False, reg_utils.USER_NAME_PARAM, 'BCREG2', "'098487'", db2_utils.REG_FILTER_USERNAME),
    ('2523', True, reg_utils.MHR_NUMBER_PARAM, '098487', "'098487'", 'mh.mhregnum IN (?)'),
    ('2523', True, reg_utils.REG_TYPE_PARAM, 'TRANSFER DUE TO SALE OR GIFT', "'098487'",
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

# testdata pattern is ({account_id}, {collapse}, {start_value}, {end_value}, {second_filter_name},
#                      {second_filter_value}, {mhr_numbers}, {expected_date_clause}, {expected_second_clause})
TEST_QUERY_FILTER_DATA_MULTIPLE = [
    ('2523', False, '2021-10-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53', reg_utils.MHR_NUMBER_PARAM,
     '098487', "'dgfhdgf'", db2_utils.REG_FILTER_DATE, db2_utils.REG_FILTER_MHR),
    ('2523', False, '2021-10-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53', reg_utils.REG_TYPE_PARAM,
     'TRANSFER DUE TO SALE OR GIFT', "'098487'", db2_utils.REG_FILTER_DATE, db2_utils.REG_FILTER_REG_TYPE),
    ('2523', False, '2021-10-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53', reg_utils.SUBMITTING_NAME_PARAM,
     'LINDA', "'098487'", db2_utils.REG_FILTER_DATE, db2_utils.REG_FILTER_SUBMITTING_NAME),
    ('2523', False, '2021-10-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53', reg_utils.CLIENT_REF_PARAM,
     'A000873', "'098487'", db2_utils.REG_FILTER_DATE, db2_utils.REG_FILTER_CLIENT_REF),
    ('2523', False, '2021-10-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53', reg_utils.STATUS_PARAM,
     'EXEMPT', "'098487'", db2_utils.REG_FILTER_DATE, db2_utils.REG_FILTER_STATUS),
    ('2523', False, '2021-10-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53', reg_utils.USER_NAME_PARAM,
     'BCREG2', "'098487'", db2_utils.REG_FILTER_DATE, db2_utils.REG_FILTER_USERNAME),
]
# testdata pattern is ({mhr_num}, {staff}, {current}, {has_notes}, {ncan_doc_id}, {has_search_notes})
TEST_MHR_NUM_DATA_NOTE = [
    ('080282', True, True, True, None, False),
    ('080282', False, True, False, None, False),
    ('003936', True, True, False, None, False),
    ('092238', True, True, True, '63116143', False),
    ('092238', False, True, True, '63116143', False),
    ('022873', True, True, True, '43599221', True),
    ('022873', False, True, True, '43599221', True)
]
# testdata pattern is ({loc_data}, {desc_data})
TEST_DATA_NEW_REG = [
    (LOCATION, DESCRIPTION)
]
# testdata pattern is ({tran_doc_type}, {doc_type})
TEST_TRAN_DOC_TYPE = [
    (None, 'TRAN'),
    ('TRANS_FAMILY_ACT', 'TRAN'),
    ('TRANS_INFORMAL_SALE', 'TRAN'),
    ('TRANS_QUIT_CLAIM', 'TRAN'),
    ('TRANS_RECEIVERSHIP', 'TRAN'),
    ('TRANS_SEVER_GRANT', 'TRAN'),
    ('TRANS_WRIT_SEIZURE', 'TRAN'),
    ('ABAN', 'ABAN'),
    ('BANK', 'BANK'),
    ('COU', 'COU '),
    ('FORE', 'FORE'),
    ('GENT', 'GENT'),
    ('REIV', 'REIV'),
    ('REPV', 'REPV'),
    ('SZL', 'SZL '),
    ('TAXS', 'TAXS'),
    ('VEST', 'VEST')
]


@pytest.mark.parametrize('account_id, has_results', TEST_ACCOUNT_REG_DATA)
def test_find_account_registrations(session, account_id, has_results):
    """Assert that finding account summary MHR registration information works as expected."""
    if model_utils.is_legacy():
        params: AccountRegistrationParams = AccountRegistrationParams(account_id=account_id,
                                                                  collapse=True,
                                                                  sbc_staff=False)

        reg_list = db2_utils.find_all_by_account_id(params)
        if has_results:
            for registration in reg_list:
                assert registration['mhrNumber']
                assert registration['registrationType']
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
                reg_desc: str = registration['registrationDescription']
                ## current_app.logger.info(f'$$$ {reg_type} {reg_desc}')
                if reg_desc == MhrRegistrationTypes.MHREG:
                    assert 'lienRegistrationType' in registration
                    assert 'hasCaution' in registration
                if registration.get('mhrNumber') == '003936':
                    assert registration.get('statusType') == 'FROZEN'
                elif registration.get('mhrNumber') == '003304':
                    assert registration.get('statusType') != 'FROZEN'
                if registration.get('changes'):
                    for reg in registration.get('changes'):
                        desc: str = reg['registrationDescription']
                        if reg.get('registrationType') == MhrRegistrationTypes.REG_NOTE and desc.find('CAUTION') > 0:
                            assert reg.get('expireDays')
                        elif reg.get('registrationType') == MhrRegistrationTypes.PERMIT:
                            assert reg.get('expireDays')
        else:
            assert not reg_list


@pytest.mark.parametrize('account_id,sort_criteria,sort_order,mhr_numbers,expected_clause', TEST_QUERY_ORDER_DATA)
def test_account_reg_order(session, account_id, sort_criteria, sort_order, mhr_numbers, expected_clause):
    """Assert that account registration query order by clause is as expected."""
    if model_utils.is_legacy():
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
    if model_utils.is_legacy():
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
    if model_utils.is_legacy():
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
    if model_utils.is_legacy():
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


@pytest.mark.parametrize('account_id,collapse,start_value,end_value,second_filter_name,second_filter_value,mhr_numbers,expected_date_clause,expected_second_clause',
                         TEST_QUERY_FILTER_DATA_MULTIPLE)
def test_account_reg_filter_multiple(session, account_id, collapse, start_value, end_value, second_filter_name,
                                     second_filter_value, mhr_numbers, expected_date_clause, expected_second_clause):
    """Assert that account registration query filter clause is as expected when multiple filters are applied."""
    if model_utils.is_legacy():
        params: AccountRegistrationParams = AccountRegistrationParams(account_id=account_id,
                                                                  collapse=collapse,
                                                                  sbc_staff=False)
        date_filter_clause: str = expected_date_clause
        second_filter_clause: str = expected_second_clause
        params.filter_reg_start_date = start_value
        params.filter_reg_end_date = end_value
        # Set second filter in params and update query
        if second_filter_name == reg_utils.REG_TS_PARAM:
            params.filter_registration_date = second_filter_value
        elif second_filter_name == reg_utils.STATUS_PARAM:
            params.filter_status_type = second_filter_value
            second_filter_clause = second_filter_clause.replace('?', 'E')
        elif second_filter_name == reg_utils.REG_TYPE_PARAM:
            params.filter_registration_type = second_filter_value
            second_filter_clause = second_filter_clause.replace('?', 'TRAN')
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

        base_query: str = db2_utils.QUERY_ACCOUNT_REGISTRATIONS_SORT
        filter_query: str = db2_utils.build_account_query_filter(base_query, params, mhr_numbers,
                                                                MhrDocumentType.find_all())

        #current_app.logger.info(filter_query)
        #current_app.logger.info(second_filter_clause)
        assert filter_query.find(date_filter_clause) > 0
        assert filter_query.find(second_filter_clause) > 0


@pytest.mark.parametrize('account_id,collapse,filter_name,filter_value,mhr_numbers,expected_clause',
                         TEST_QUERY_FILTER_DATA)
def test_find_account_filter(session, account_id, collapse, filter_name, filter_value, mhr_numbers, expected_clause):
    """Assert that account registration query with an order by clause is as expected."""
    if model_utils.is_legacy():
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


def test_get_pid_list(session):
    """Assert that the get pid list query for synchronizing LTSA descriptions is as expected."""
    if model_utils.is_legacy():
        pid_list = db2_utils.get_pid_list()
        # assert pid_list
        for pid in pid_list:
            assert pid.get('pidNumber')


def test_update_pid_list(session):
    """Assert that pid list status update for synchronizing LTSA descriptions is as expected."""
    if model_utils.is_legacy():
        pid_list = [{'pidNumber': '  1789805'}]
        db2_utils.update_pid_list(pid_list, db2_utils.UPDATE_PID_STATUS_SUCCESS)
        db2_utils.update_pid_list(pid_list, ' ')


def test_get_next_mhr_number(session):
    """Assert that the get next mhr number query works as expected."""
    if model_utils.is_legacy():
        mhr1 = db2_utils.get_next_mhr_number()
        mhr2 = db2_utils.get_next_mhr_number()
        # assert number generated
        assert mhr1 and mhr2
        assert int(mhr1) + 1 == int(mhr2)


@pytest.mark.parametrize('mhr_num,staff,current,has_notes,ncan_doc_id,has_search_notes', TEST_MHR_NUM_DATA_NOTE)
def test_get_new_reg_json_note(session, mhr_num, staff, current, has_notes, ncan_doc_id, has_search_notes):
    """Assert that registration unit notes work as expected."""
    if model_utils.is_legacy():
        manuhome: Db2Manuhome = Db2Manuhome.find_by_mhr_number(mhr_num)
        assert manuhome
        registration: MhrRegistration = MhrRegistration(current_view=current, staff=staff, manuhome=manuhome)
        reg_json = db2_utils.get_new_registration_json(registration)
        if has_notes:
            assert reg_json.get('notes')
            has_ncan: bool = False
            for note in reg_json['notes']:
                # current_app.logger.info(note)
                if staff:
                    assert note.get('documentRegistrationNumber')
                    assert note.get('documentId')
                    assert note.get('documentDescription')
                    if ncan_doc_id and note.get('documentId') == ncan_doc_id:
                        has_ncan = True
                        assert note.get('cancelledDocumentType')
                        assert note.get('cancelledDocumentRegistrationNumber')
                        assert note.get('cancelledDocumentDescription')
                    assert note.get('createDateTime')
                    assert note.get('status')
                    assert 'remarks' in note
                    assert note.get('givingNoticeParty')
                else:
                    assert note.get('documentType')
                    assert note.get('documentDescription')
                    assert note.get('createDateTime')
                    assert note.get('status')
                    assert 'remarks' not in note
                    assert 'documentRegistrationNumber' not in note
                    assert 'documentId' not in note
                    assert 'givingNoticeParty' not in note
            if ncan_doc_id and staff:
                assert has_ncan
        elif staff and current:
            assert 'notes' in reg_json
            assert not reg_json.get('notes')
        else:
            assert not reg_json.get('notes')


@pytest.mark.parametrize('mhr_num,staff,current,has_notes,ncan_doc_id,has_search_notes', TEST_MHR_NUM_DATA_NOTE)
def test_get_search_json_note(session, mhr_num, staff, current, has_notes, ncan_doc_id, has_search_notes):
    """Assert that search unit notes work as expected."""
    if model_utils.is_legacy():
        manuhome: Db2Manuhome = Db2Manuhome.find_by_mhr_number(mhr_num)
        assert manuhome
        registration: MhrRegistration = MhrRegistration(current_view=current, staff=staff, manuhome=manuhome)
        reg_json = db2_utils.get_search_json(registration)
        if has_notes and has_search_notes:
            assert reg_json.get('notes')
            has_ncan: bool = False
            for note in reg_json.get('notes'):
                assert note.get('documentRegistrationNumber')
                assert note.get('documentId')
                assert note.get('documentDescription')
                if ncan_doc_id and note.get('documentId') == ncan_doc_id:
                    has_ncan = True
                    assert note.get('cancelledDocumentType')
                    assert note.get('cancelledDocumentRegistrationNumber')
                assert note.get('createDateTime')
                assert note.get('status')
                assert 'remarks' in note
                assert note.get('givingNoticeParty')
            if ncan_doc_id:
                assert has_ncan
        else:
            assert not reg_json.get('notes')


@pytest.mark.parametrize('loc_data,desc_data', TEST_DATA_NEW_REG)
def test_save_new_reg(session, loc_data, desc_data):
    """Assert that new MHR registration JSON uses the new location and description."""
    if model_utils.is_legacy():
        json_data = copy.deepcopy(REGISTRATION)
        json_data['documentId'] = '88878888'
        json_data['location'] = copy.deepcopy(loc_data)
        json_data['description'] = copy.deepcopy(desc_data)
        registration: MhrRegistration = MhrRegistration.create_new_from_json(json_data, 'PS12345')
        registration.save()
        reg_json = db2_utils.get_new_registration_json(registration)
        assert reg_json.get('location')
        loc = reg_json.get('location')
        assert loc.get('locationType') == loc_data.get('locationType')
        assert loc.get('pidNumber') == loc_data.get('pidNumber')
        assert loc.get('legalDescription') == loc_data.get('legalDescription')
        assert loc['address'].get('postalCode') == loc_data['address'].get('postalCode')
        assert reg_json.get('description')
        desc = reg_json.get('description')
        assert desc.get('make') == desc_data.get('make')
        assert desc.get('model') == desc_data.get('model')
        registration.current_view = True
        reg_json = db2_utils.get_new_registration_json(registration)
        assert reg_json.get('location')
        loc = reg_json.get('location')
        assert loc.get('locationType') == loc_data.get('locationType')
        assert loc.get('pidNumber') == loc_data.get('pidNumber')
        assert loc.get('legalDescription') == loc_data.get('legalDescription')
        assert loc['address'].get('postalCode') == loc_data['address'].get('postalCode')
        assert reg_json.get('description')
        desc = reg_json.get('description')
        assert desc.get('make') == desc_data.get('make')
        assert desc.get('model') == desc_data.get('model')


@pytest.mark.parametrize('loc_data,desc_data', TEST_DATA_NEW_REG)
def test_save_new_search(session, loc_data, desc_data):
    """Assert that new MHR search JSON uses the new location and description."""
    if model_utils.is_legacy():
        json_data = copy.deepcopy(REGISTRATION)
        json_data['documentId'] = '88878888'
        json_data['location'] = copy.deepcopy(loc_data)
        json_data['description'] = copy.deepcopy(desc_data)
        test_reg: MhrRegistration = MhrRegistration.create_new_from_json(json_data, 'PS12345')
        test_reg.save()
        registration: MhrRegistration = MhrRegistration.find_by_id(test_reg.id, True, True)
        reg_json = db2_utils.get_search_json(registration)
        assert reg_json.get('location')
        loc = reg_json.get('location')
        assert loc.get('locationType') == loc_data.get('locationType')
        assert loc.get('pidNumber') == loc_data.get('pidNumber')
        assert loc.get('legalDescription') == loc_data.get('legalDescription')
        assert loc['address'].get('postalCode') == loc_data['address'].get('postalCode')
        assert reg_json.get('description')
        desc = reg_json.get('description')
        assert desc.get('make') == desc_data.get('make')
        assert desc.get('model') == desc_data.get('model')


@pytest.mark.parametrize('tran_doc_type,doc_type', TEST_TRAN_DOC_TYPE)
def test_tran_doc_type(session, tran_doc_type, doc_type):
    """Assert that transfer sale or gift mapping of doc types works as expected."""
    reg_json = {}
    if tran_doc_type:
        reg_json['transferDocumentType'] = tran_doc_type
    test_doc_type = legacy_reg_utils.get_transfer_doc_type(reg_json)
    assert test_doc_type == doc_type
