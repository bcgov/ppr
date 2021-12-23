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

import pytest
from registry_schemas.example_data.ppr import DRAFT_AMENDMENT_STATEMENT, DRAFT_CHANGE_STATEMENT

from ppr_api.exceptions import BusinessException
from ppr_api.models import Draft
from ppr_api.models.utils import now_ts


def test_find_all_by_account_id(session):
    """Assert that the draft summary list items contains all expected elements."""
    draft_list = Draft.find_all_by_account_id('PS12345')
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
    drafts = Draft.find_all_by_account_id('X12345X')

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
