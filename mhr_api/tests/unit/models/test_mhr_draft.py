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
from registry_schemas.example_data.mhr import REGISTRATION

from mhr_api.exceptions import BusinessException
from mhr_api.models import MhrDraft, utils as model_utils
from mhr_api.models.type_tables import MhrRegistrationTypes


def test_find_all_by_account_id(session):
    """Assert that the draft summary list items contains all expected elements."""
    draft_list = MhrDraft.find_all_by_account_id('PS12345')
    # print(draft_list)
    assert draft_list
    for draft in draft_list:
        assert draft['draftNumber']
        assert draft['registrationType']
        assert draft['registrationDescription']
        assert draft['createDateTime']
        assert draft['lastUpdateDateTime']
        assert 'clientReferenceId' in draft
        assert draft['path']
        assert 'submittingParty' in draft


def test_find_by_draft_number(session):
    """Assert that the find draft by draft number contains all expected elements."""
    draft: MhrDraft = MhrDraft.find_by_draft_number('T500000', True)
    assert draft
    assert draft.id
    assert draft.draft_number
    assert draft.draft
    assert draft.create_ts
    assert draft.account_id
    assert draft.user_id


def test_find_by_account_id_no_result(session):
    """Assert that the find draft statement by invalid account ID returns the expected result."""
    drafts = MhrDraft.find_all_by_account_id('X12345X')

    # check
    assert not drafts


def test_find_by_draft_number_invalid(session):
    """Assert that the find draft by invalid draft number returns the expected result."""
    with pytest.raises(BusinessException) as not_found_err:
        MhrDraft.find_by_draft_number('X12345X', False)

    # check
    assert not_found_err
    assert not_found_err.value.status_code == HTTPStatus.NOT_FOUND


def test_save_then_delete(session):
    """Assert that a save then delete draft statement returns the expected result."""
    json_data = copy.deepcopy(REGISTRATION)
    json_data['registrationType'] = 'MHREG'
    new_draft: MhrDraft = MhrDraft.create_from_json(json_data, 'PS12345')
    new_draft.save()
    draft = new_draft.json
    assert draft
    assert draft['registrationType'] == 'MHREG'
    assert draft['createDateTime']
    assert draft['draftNumber']

    # Now test delete draft
    draft_number = draft['draftNumber']
    delete_draft = MhrDraft.delete(draft_number)
    assert delete_draft


def test_update(session):
    """Assert that a valid update draft returns the expected result."""
    json_data = copy.deepcopy(REGISTRATION)
    json_data['registrationType'] = 'MHREG'
    new_draft: MhrDraft = MhrDraft.create_from_json(json_data, 'PS12345')
    new_draft.save()
    draft_number = new_draft.draft_number
    json_data['clientReferenceId'] = 'TU-0001'
    updated = MhrDraft.update(json_data, draft_number)
    updated.save()
    draft = updated.json
    assert draft
    assert draft['registrationType'] == 'MHREG'
    assert draft['createDateTime']
    assert draft['lastUpdateDateTime']
    assert draft['draftNumber'] == draft_number
    assert draft['clientReferenceId'] == 'TU-0001'


def test_update_invalid(session):
    """Assert that an update draft a non-existent draft number returns the expected result."""
    json_data = copy.deepcopy(REGISTRATION)

    with pytest.raises(BusinessException) as not_found_err:
        MhrDraft.update(json_data, 'X12345X')

    # check
    assert not_found_err
    assert not_found_err.value.status_code == HTTPStatus.NOT_FOUND


def test_delete_bad_id(session):
    """Assert that delete by invalid draft number works as expected."""
    with pytest.raises(BusinessException) as not_found_err:
        MhrDraft.delete('X12345X')

    # check
    assert not_found_err
    assert not_found_err.value.status_code == HTTPStatus.NOT_FOUND


def test_draft_json(session):
    """Assert that the draft renders to a json format correctly."""
    json_data = copy.deepcopy(REGISTRATION)
    json_data['registrationType'] = MhrRegistrationTypes.MHREG
    draft: MhrDraft = MhrDraft(
        draft_number='TEST1234',
        account_id='PS12345',
        create_ts=model_utils.now_ts(),
        registration_type=json_data['registrationType'],
        draft=json_data,
    )

    draft_json = draft.json
    assert draft_json
    assert draft_json['draftNumber'] == draft.draft_number
    assert draft_json['registrationType'] == draft.registration_type


def test_draft_create_from_json(session):
    """Assert that the draft is created from json data correctly."""
    json_data = copy.deepcopy(REGISTRATION)
    json_data['registrationType'] = MhrRegistrationTypes.MHREG
    draft: MhrDraft = MhrDraft.create_from_json(json_data, 'PS12345')

    assert draft.draft
    assert draft.account_id == 'PS12345'
    assert draft.registration_type == json_data['registrationType']
