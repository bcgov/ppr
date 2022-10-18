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

"""Tests to assure the legacy DB2 MH Note Model.

Test-Suite to ensure that the legacy DB2 MH Note Model is working as expected.
"""

import pytest

from flask import current_app

from mhr_api.models import Db2Mhomnote


# testdata pattern is ({exists}, {manuhome_id}, {doc_id}, {doc_type}, {expiry}, {count})
TEST_DATA = [
    (True, 1, '41009149', 'EXRS', None, 1),
    (True, 7, '90011251', '103', '2012-02-24', 2),
    (False, 0, None, None, None, 0)
]


@pytest.mark.parametrize('exists,manuhome_id,doc_id,doc_type,expiry,count', TEST_DATA)
def test_find_by_manuhome_id(session, exists, manuhome_id, doc_id, doc_type, expiry, count):
    """Assert that find notes by manuhome id contains all expected elements."""
    notes: Db2Mhomnote = Db2Mhomnote.find_by_manuhome_id(manuhome_id)
    if exists:
        assert notes
        assert len(notes) == count
        for note in notes:
            assert note.manuhome_id == manuhome_id
            assert note.note_id > 0
            assert note.note_number >= 0
            assert note.status
            if note.status == 'A':
                assert note.reg_document_id == doc_id
                assert note.document_type == doc_type
            assert note.can_document_id is not None
            assert note.phone_number is not None
            assert note.name is not None
            assert note.legacy_address is not None
            assert note.remarks is not None

    else:
        assert not notes


@pytest.mark.parametrize('exists,manuhome_id,doc_id,doc_type,expiry,count', TEST_DATA)
def test_find_by_manuhome_id_active(session, exists, manuhome_id, doc_id, doc_type, expiry, count):
    """Assert that find the active notes by manuhome id contains all expected elements."""
    notes: Db2Mhomnote = Db2Mhomnote.find_by_manuhome_id_active(manuhome_id)
    if exists:
        assert notes
        for note in notes:
            assert note.manuhome_id == manuhome_id
            assert note.note_id > 0
            assert note.note_number >= 0
            assert note.status
            assert note.reg_document_id == doc_id
            assert note.document_type == doc_type
            assert note.can_document_id is not None
            assert note.phone_number is not None
            assert note.name is not None
            assert note.legacy_address is not None
            assert note.remarks is not None
            reg_json = note.registration_json
            current_app.logger.debug(reg_json)
            assert reg_json.get('documentType') == doc_type
            assert reg_json.get('documentId') == doc_id
            assert reg_json.get('createDateTime') is not None
            if not expiry:
                assert not reg_json.get('expiryDate')
            else:
                assert str(reg_json.get('expiryDate'))[0:10] == expiry
            assert reg_json.get('remarks') is not None
            assert reg_json.get('contactName') is not None
            assert reg_json.get('contactAddress')
            assert reg_json['contactAddress']['street']
            assert reg_json['contactAddress']['city']
            assert reg_json['contactAddress']['region']
            assert reg_json['contactAddress']['country']
            assert reg_json['contactAddress']['postalCode'] is not None
    else:
        assert not notes


def test_note_json(session):
    """Assert that the note renders to a json format correctly."""
    note = Db2Mhomnote(note_id=1,
                       note_number=1,
                       status='A',
                       reg_document_id='1234',
                       can_document_id='5678',
                       document_type='103',
                       destroyed='N',
                       phone_number='6041234567',
                       name='contact _name',
                       legacy_address='legacy address',
                       remarks='remarks')

    test_json = {
        'noteId': note.note_id,
        'noteNumber': note.note_number,
        'status': note.status,
        'registrationDocumentId': note.reg_document_id,
        'canDocumentId': note.can_document_id,
        'documentType': note.document_type,
        'destroyed': note.destroyed,
        'phoneNumber': note.phone_number,
        'name': note.name,
        'legacyAddress': note.legacy_address,
        'remarks': note.remarks
    }
    assert note.json == test_json
