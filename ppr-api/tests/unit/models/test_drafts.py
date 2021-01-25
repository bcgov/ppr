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
from http import HTTPStatus

import pytest

from ppr_api.models import Draft
from ppr_api.exceptions import BusinessException

import copy
from registry_schemas.example_data.ppr import DRAFT_AMENDMENT_STATEMENT
from registry_schemas.example_data.ppr import DRAFT_FINANCING_STATEMENT, DRAFT_CHANGE_STATEMENT



def test_find_all_by_account_id(session):
    """Assert that the draft summary list first item contains all expected elements."""
    draft_list = Draft.find_all_by_account_id('PS12345')
    assert draft_list[0]['type']
    assert draft_list[0]['documentId']
    assert draft_list[0]['registrationType']
    assert draft_list[0]['path']
    assert draft_list[0]['createDateTime']

def test_find_by_document_id_financing(session):
    """Assert that the find draft financing statement by document id contains all expected elements."""
    draft = Draft.find_by_document_id('TEST-FSD1', True)
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
    draft = Draft.find_by_document_id('TEST-CHD1', True)
    assert draft
    json_data = draft.json
    assert json_data['changeStatement']
    assert json_data['type'] == 'CHANGE_STATEMENT'
    assert json_data['changeStatement']['registeringParty']
    assert json_data['changeStatement']['baseRegistrationNumber']
    assert json_data['changeStatement']['changeType']

def test_find_by_document_id_amendment(session):
    """Assert that the find draft amendment statement by document id contains all expected elements."""
    draft = Draft.find_by_document_id('TEST-AMD1', True)
    assert draft
    json_data = draft.json
    assert json_data['amendmentStatement']
    assert json_data['type'] == 'AMENDMENT_STATEMENT'
    assert json_data['amendmentStatement']['registeringParty']
    assert json_data['amendmentStatement']['baseRegistrationNumber']
    assert json_data['amendmentStatement']['changeType']


def test_find_by_account_id_invalid(session):
    """Assert that the find draft statement by invalid account ID returns the expected result."""
    with pytest.raises(BusinessException) as not_found_err:
        Draft.find_all_by_account_id('X12345X')

    # check
    assert not_found_err
    assert not_found_err.value.status_code == HTTPStatus.NOT_FOUND


def test_find_by_document_id_invalid(session):
    """Assert that the find draft statement by invalid document returns the expected result."""
    with pytest.raises(BusinessException) as not_found_err:
        Draft.find_by_document_id('X12345X', False)

    # check
    assert not_found_err
    assert not_found_err.value.status_code == HTTPStatus.NOT_FOUND


def test_save_then_delete(session):
    """Assert that a save then delete draft statement returns the expected result."""
    json_data = copy.deepcopy(DRAFT_CHANGE_STATEMENT)
#    draft = Draft._save(json_data, 'PS12345')

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
    deleteDraft = Draft.delete(document_id)
    assert deleteDraft


def test_update(session):
    """Assert that a valid update draft statement returns the expected result."""
    json_data = copy.deepcopy(DRAFT_CHANGE_STATEMENT)
    updated = Draft.update(json_data, 'TEST-CHD1', 'PS12345')
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
        Draft.update(json_data, 'X12345X', 'PS12345')

    # check
    assert not_found_err
    assert not_found_err.value.status_code == HTTPStatus.NOT_FOUND


def test_delete_bad_id(session):
    """Assert that delete by invalid document ID works as expected """
    with pytest.raises(BusinessException) as not_found_err:
        Draft.delete('X12345X')

    # check
    assert not_found_err
    assert not_found_err.value.status_code == HTTPStatus.NOT_FOUND
