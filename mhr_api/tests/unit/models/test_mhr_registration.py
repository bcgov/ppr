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
import copy
from http import HTTPStatus

from flask import current_app

import pytest
from registry_schemas.example_data.mhr import REGISTRATION

from mhr_api.exceptions import BusinessException
from mhr_api.models import MhrRegistration, MhrDraft
from mhr_api.models.type_tables import MhrPartyTypes, MhrOwnerStatusTypes
from mhr_api.models.type_tables import MhrRegistrationTypes, MhrRegistrationStatusTypes


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
# testdata pattern is ({reg_id}, {has_results})
TEST_ID_DATA = [
    (200000000, True),
    (300000000, False)
]
# testdata pattern is ({mhr_number}, {has_results}, {account_id})
TEST_MHR_NUM_DATA = [
    ('UT-001', False, 'PS12345'),
    ('UX-XXX', False, 'PS12345'),
    ('150062', True, '2523')
]
# testdata pattern is ({doc_id}, {exist_count})
TEST_DOC_ID_DATA = [
    ('80048709', 1),
    ('80048756', 0)
]


@pytest.mark.parametrize('account_id,mhr_num,exists,reg_desc,in_list', TEST_SUMMARY_REG_DATA)
def test_find_summary_by_mhr_number(session, account_id, mhr_num, exists, reg_desc, in_list):
    """Assert that finding summary MHR registration information works as expected."""
    registration = MhrRegistration.find_summary_by_mhr_number(account_id, mhr_num)
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
    reg_list = MhrRegistration.find_all_by_account_id(account_id)
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
            assert not registration.get('inUserList')
    else:
        assert not reg_list


@pytest.mark.parametrize('reg_id, has_results', TEST_ID_DATA)
def test_find_by_id(session, reg_id, has_results):
    """Assert that finding an MHR registration by id works as expected."""
    registration: MhrRegistration = MhrRegistration.find_by_id(reg_id)
    if has_results:
        assert registration
        assert registration.id == reg_id
        assert registration.mhr_number
        assert registration.status_type
        assert registration.registration_type
        assert registration.registration_ts
    else:
        assert not registration


@pytest.mark.parametrize('mhr_number, has_results, account_id', TEST_MHR_NUM_DATA)
def test_find_by_mhr_number(session, mhr_number, has_results, account_id):
    """Assert that finding an MHR registration by MHR number works as expected."""
    if has_results:
        registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_number, account_id)
        assert registration
        assert registration.id
        assert registration.mhr_number == mhr_number
        assert registration.status_type in MhrRegistrationStatusTypes
        assert registration.registration_type in MhrRegistrationTypes
        assert registration.registration_ts
    else:
        with pytest.raises(BusinessException) as not_found_err:
            MhrRegistration.find_by_mhr_number(mhr_number, 'PS12345')
        # check
        assert not_found_err
        assert not_found_err.value.status_code == HTTPStatus.NOT_FOUND


def test_create_new_from_json(session):
    """Assert that the new MHR registration is created from json data correctly."""
    json_data = copy.deepcopy(REGISTRATION)
    registration: MhrRegistration = MhrRegistration.create_new_from_json(json_data, 'PS12345')
    assert registration.id > 0
    assert registration.mhr_number
    assert registration.registration_ts
    assert registration.status_type in MhrRegistrationStatusTypes
    assert registration.registration_type in MhrRegistrationTypes
    assert registration.account_id == 'PS12345'
    assert registration.client_reference_id    
    assert registration.draft
    assert registration.draft.id > 0
    assert registration.draft_id == registration.draft.id
    assert registration.draft.draft_number
    assert registration.draft.registration_type == registration.registration_type
    assert registration.draft.create_ts == registration.registration_ts
    assert registration.draft.account_id == registration.account_id
    assert registration.parties
    for party in registration.parties:
        assert party.registration_id > 0
        assert party.change_registration_id > 0
        assert party.party_type in MhrPartyTypes
        assert party.status_type in MhrOwnerStatusTypes
        assert party.compressed_name


def test_save_new(session):
    """Assert that saving a new MHR registration is working correctly."""
    json_data = copy.deepcopy(REGISTRATION)
    registration: MhrRegistration = MhrRegistration.create_new_from_json(json_data, 'PS12345')
    registration.save()
    reg_new = MhrRegistration.find_by_mhr_number(registration.mhr_number, 'PS12345')
    assert reg_new
    draft_new = MhrDraft.find_by_draft_number(registration.draft.draft_number, True)
    assert draft_new


@pytest.mark.parametrize('doc_id, exists_count', TEST_DOC_ID_DATA)
def test_get_doc_id_count(session, doc_id, exists_count):
    """Assert that counting existing document id's works as expected."""
    count: int = MhrRegistration.get_doc_id_count(doc_id)
    assert count == exists_count
