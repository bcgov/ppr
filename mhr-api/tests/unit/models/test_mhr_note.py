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

from mhr_api.models import MhrNote, utils as model_utils
from mhr_api.models.type_tables import MhrDocumentTypes, MhrNoteStatusTypes


# testdata pattern is ({id}, {has_results})
TEST_ID_DATA = [
    (200000001, True),
    (300000000, False)
]
# testdata pattern is ({destroyed}, {reason}, {other})
TEST_EXNR_DATA = [
    (False, 'OFFICE', None),
    (False, 'STORAGE_SHED', None),
    (False, 'OTHER', 'Some other reason'),
    (True, 'BURNT', None),
    (True, 'DILAPIDATED', None),
    (True, 'OTHER', 'Some other reason')
 ]
# testdata pattern is ({doc_type}, {include})
TEST_GIVING_NOTICE_DATA = [
    (MhrDocumentTypes.CAU.value, True),
    (MhrDocumentTypes.CAUC.value, True),
    (MhrDocumentTypes.CAUE.value, True),
    (MhrDocumentTypes.NPUB.value, True),
    (MhrDocumentTypes.NCON.value, True),
    (MhrDocumentTypes.REG_102.value, True),
    (MhrDocumentTypes.TAXN.value, True),
    (MhrDocumentTypes.EXNR.value, False),
    (MhrDocumentTypes.NCAN.value, False),
    (MhrDocumentTypes.NRED.value, False),
    (MhrDocumentTypes.STAT.value, False),
    (MhrDocumentTypes.REST.value, False),
    (MhrDocumentTypes.REGC.value, False),
    (MhrDocumentTypes.EXRS.value, False),
    (MhrDocumentTypes.REG_103.value, False),
    (MhrDocumentTypes.REG_103E.value, False)
]

TEST_NOTE = MhrNote(id=1,
    status_type='ACTIVE',
    document_type=MhrDocumentTypes.EXRS,
    document_id=200000000,
    remarks='remarks',
    destroyed='N',
    effective_ts = model_utils.now_ts(),
    expiry_date = model_utils.now_ts_offset(90, True))


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_id(session, id, has_results):
    """Assert that find note by primary key contains all expected elements."""
    note: MhrNote = MhrNote.find_by_id(id)
    if has_results:
        assert note
        assert note.id == id
        assert note.registration_id == id
        assert note.change_registration_id == id
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
        assert note.id == id
        assert note.registration_id == id
        assert note.change_registration_id == id
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
        assert note.id == id
        assert note.registration_id == id
        assert note.change_registration_id == id
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
        assert note.id == id
        assert note.registration_id == id
        assert note.change_registration_id == id
        assert note.document_type == MhrDocumentTypes.REG_101
        assert note.status_type == MhrNoteStatusTypes.ACTIVE
        assert note.destroyed == 'N'
        assert not note.expiry_date
    else:
        assert not notes
 

@pytest.mark.parametrize('doc_type, include', TEST_GIVING_NOTICE_DATA)
def test_include_giving_notice(session, doc_type, include):
    """Assert that including person giving notice by doc type works as expected."""
    notes= MhrNote.find_by_registration_id(200000011)
    note: MhrNote = notes[0]
    note.document_type = doc_type
    note_json = note.json
    if include:
        assert note_json.get('givingNoticeParty')
    else:
        assert 'givingNoticeParty' not in note_json


def test_note_json(session):
    """Assert that the document model renders to a json format correctly."""
    note: MhrNote = TEST_NOTE
    note_json = {
        'documentId': str(note.document_id),
        'status': note.status_type,
        'documentType': note.document_type,
        'documentDescription': 'RESIDENTIAL EXEMPTION',
        'remarks': note.remarks,
        'destroyed': False,
        'effectiveDateTime': model_utils.format_ts(note.effective_ts),
        'expiryDateTime': model_utils.format_ts(note.expiry_date)
    }
    assert note.json == note_json


def test_create_from_reg_json(session):
    """Assert that the new MHR note is created from MH registration json data correctly."""
    json_data = copy.deepcopy(NOTE)
    json_data['remarks'] = 'remarks'
    json_data['documentType'] = MhrDocumentTypes.CAU
    reg_ts = model_utils.now_ts()
    effective_ts = model_utils.now_ts_offset(10, False)
    json_data['effectiveDateTime'] = model_utils.format_ts(effective_ts)
    note: MhrNote = MhrNote.create_from_json(json_data, 1000, 2000, reg_ts, 3000)
    assert note
    assert note.registration_id == 1000
    assert note.document_id == 2000
    assert note.change_registration_id == 3000
    assert note.destroyed == 'N'
    assert note.document_type == MhrDocumentTypes.CAU
    assert note.remarks == 'remarks'
    assert note.effective_ts
    assert note.expiry_date


@pytest.mark.parametrize('destroyed, reason, other', TEST_EXNR_DATA)
def test_exnr_json(session, destroyed, reason, other):
    """Assert that EXNR mapping from JSON to model works as expected."""
    json_data = copy.deepcopy(NOTE)
    json_data['remarks'] = 'remarks'
    json_data['documentType'] = MhrDocumentTypes.EXNR
    json_data['destroyed'] = destroyed
    json_data['nonResidentialReason'] = reason
    if other:
        json_data['nonResidentialOther'] = other
    reg_ts = model_utils.now_ts()
    if destroyed:
        destroyed_ts = model_utils.now_ts_offset(10, True)
        json_data['expiryDateTime'] = model_utils.format_ts(destroyed_ts)
    note: MhrNote = MhrNote.create_from_json(json_data, 1000, 2000, reg_ts, 3000)
    assert note
    assert note.registration_id == 1000
    assert note.document_id == 2000
    assert note.change_registration_id == 3000
    assert note.document_type == MhrDocumentTypes.EXNR
    assert note.remarks == 'remarks'
    assert note.expiry_date
    if destroyed:
        assert note.destroyed == 'Y'
    else:
        assert note.destroyed == 'N'
    assert note.non_residential_reason == reason
    if other:
        assert note.non_residential_other == other
    else:
        assert not note.non_residential_other
    note_json = note.json
    assert note_json.get('nonResidentialReason') == reason
    if other:
        assert note_json.get('nonResidentialOther') == other
    if destroyed:
        assert note_json.get('destroyed')
    else:
        assert not note_json.get('destroyed')
