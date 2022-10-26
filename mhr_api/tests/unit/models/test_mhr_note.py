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

"""Tests to assure the MHR note Model.

Test-Suite to ensure that the MHR note Model is working as expected.
"""
import copy

import pytest
from registry_schemas.example_data.mhr import NOTE

from mhr_api.models import MhrNote
from mhr_api.models.type_tables import MhrDocumentTypes, MhrNoteStatusTypes


# testdata pattern is ({id}, {has_results})
TEST_ID_DATA = [
    (200000000, True),
    (300000000, False)
]
TEST_NOTE = MhrNote(id=1,
    status_type='ACTIVE',
    document_type=MhrDocumentTypes.REG_101,
    document_id=200000000,
    remarks='remarks',
    destroyed='N')


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_id(session, id, has_results):
    """Assert that find note by primary key contains all expected elements."""
    note: MhrNote = MhrNote.find_by_id(id)
    if has_results:
        assert note
        assert note.id == 200000000
        assert note.registration_id == 200000000
        assert note.change_registration_id == 200000000
        assert note.document_type == MhrDocumentTypes.REG_101
        assert note.status_type == MhrNoteStatusTypes.ACTIVE
        assert note.destroyed == 'N'
        assert not note.expiry_date
    else:
        assert not note


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_registration_id(session, id, has_results):
    """Assert that find note by registration id contains all expected elements."""
    notes = MhrNote.find_by_registration_id(id)
    if has_results:
        assert notes
        note = notes[0]
        assert note.id == 200000000
        assert note.registration_id == 200000000
        assert note.change_registration_id == 200000000
        assert note.document_type == MhrDocumentTypes.REG_101
        assert note.status_type == MhrNoteStatusTypes.ACTIVE
        assert note.destroyed == 'N'
        assert not note.expiry_date
    else:
        assert not notes


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_document_id(session, id, has_results):
    """Assert that find note by document id contains all expected elements."""
    note: MhrNote = MhrNote.find_by_document_id(id)
    if has_results:
        assert note
        assert note.id == 200000000
        assert note.registration_id == 200000000
        assert note.change_registration_id == 200000000
        assert note.document_type == MhrDocumentTypes.REG_101
        assert note.status_type == MhrNoteStatusTypes.ACTIVE
        assert note.destroyed == 'N'
        assert not note.expiry_date
    else:
        assert not note


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_change_registration_id(session, id, has_results):
    """Assert that find note by change registration id contains all expected elements."""
    notes = MhrNote.find_by_change_registration_id(id)
    if has_results:
        assert notes
        note = notes[0]
        assert note.id == 200000000
        assert note.registration_id == 200000000
        assert note.change_registration_id == 200000000
        assert note.document_type == MhrDocumentTypes.REG_101
        assert note.status_type == MhrNoteStatusTypes.ACTIVE
        assert note.destroyed == 'N'
        assert not note.expiry_date
    else:
        assert not notes


def test_note_json(session):
    """Assert that the document model renders to a json format correctly."""
    note: MhrNote = TEST_NOTE
    note_json = {
        'documentType': note.document_type,
        'remarks': note.remarks,
        'destroyed': False
    }
    assert note.json == note_json


def test_create_from_reg_json(session):
    """Assert that the new MHR note is created from MH registration json data correctly."""
    json_data = copy.deepcopy(NOTE)
    json_data['remarks'] = 'remarks'
    json_data['documentType'] = MhrDocumentTypes.EXNR
    note: MhrNote = MhrNote.create_from_json(json_data, 1000, 2000, 3000)
    assert note
    assert note.registration_id == 1000
    assert note.document_id == 2000
    assert note.change_registration_id == 3000
    assert note.destroyed == 'N'
    assert note.document_type == MhrDocumentTypes.EXNR
    assert note.remarks == 'remarks'
