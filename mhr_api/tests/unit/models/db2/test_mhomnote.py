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
import copy

from flask import current_app

from mhr_api.models import Db2Mhomnote, Db2Document
from mhr_api.models.db2 import address_utils
from mhr_api.models.type_tables import MhrNoteStatusTypes

NOTE = {
    'noteId': 2,
    'documentType': 'NPUB',
    'documentId': '62133670',
    'effectiveDateTime': '2023-02-21T18:56:00+00:00',
    'remarks': 'NOTICE OF ACTION COMMENCED MARCH 1 2022 WITH CRANBROOK COURT REGISTRY COURT FILE NO. 3011.',
    'givingNoticeParty': {
      'personName': {
        'first': 'JOHNNY',
        'middle': 'B',
        'last': 'SMITH'
      },
      'address': {
        'street': '222 SUMMER STREET',
        'city': 'VICTORIA',
        'region': 'BC',
        'country': 'CA',
        'postalCode': 'V8W 2V8'
      },
      'phoneNumber': '2504930122'
    }
}

# testdata pattern is ({exists}, {manuhome_id}, {doc_id}, {doc_type}, {expiry}, {count})
TEST_DATA = [
    (True, 1, '41009149', 'EXRS', None, 1),
    (True, 7, '90011251', '103', '2012-02-24', 2),
    (False, 0, None, None, None, 0)
]
# testdata pattern is ({manuhome_id}, {doc_id}, {doc_type}, {expiry}, {has_party})
TEST_CREATE_DATA = [
    (100000, '90600001', 'CAUC', '2023-10-14T00:00:01-08:00', True),
    (100000, '90600002', 'NPUB', None, False)
]
LEGACY_ADDRESS = '222 SUMMER STREET                                                               VICTORIA' + \
                 '                                BC CA                            V8W 2V8'


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
            if note.status == MhrNoteStatusTypes.ACTIVE:
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
            # current_app.logger.debug(reg_json)
            assert reg_json.get('documentType') == doc_type
            assert reg_json.get('documentId') == doc_id
            assert reg_json.get('createDateTime') is not None
            if not expiry:
                assert not reg_json.get('expiryDateTime')
            else:
                assert str(reg_json.get('expiryDateTime'))[0:10] == expiry
            assert reg_json.get('remarks') is not None
            assert reg_json.get('givingNoticeParty') is not None
            notice_json = reg_json.get('givingNoticeParty')
            assert notice_json.get('businessName')
            assert notice_json.get('phoneNumber')
            assert notice_json.get('address')
            assert notice_json['address']['street']
            assert notice_json['address']['city']
            assert notice_json['address']['region']
            assert notice_json['address']['country']
            assert notice_json['address']['postalCode'] is not None
            assert reg_json.get('status') in (MhrNoteStatusTypes.ACTIVE,
                                              MhrNoteStatusTypes.CANCELLED,
                                              MhrNoteStatusTypes.EXPIRED)
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
                       legacy_address=LEGACY_ADDRESS,
                       remarks='remarks')

    test_json = {
        'documentType': note.document_type,
        'documentId': note.reg_document_id,
        'remarks': note.remarks,
        'status': MhrNoteStatusTypes.ACTIVE.value,
        'destroyed': False,
        'givingNoticeParty': {
            'businessName': note.name,
            'address': address_utils.get_address_from_db2(note.legacy_address),
            'phoneNumber': note.phone_number
        }
    }
    assert note.json == test_json


# testdata pattern is ({manuhome_id}, {doc_id}, {doc_type}, {expiry}, {has_party})
@pytest.mark.parametrize('manuhome_id,doc_id,doc_type,expiry,has_party', TEST_CREATE_DATA)
def test_create_from_json(session, manuhome_id, doc_id, doc_type, expiry, has_party):
    """Assert that creating a note from JSON contains all expected elements."""
    doc: Db2Document = Db2Document(id=doc_id,
                                   document_type=doc_type,
                                   name='TEST NAME',
                                   legacy_address='1234 TEST ST KELOWNA',
                                   phone_number='2501234442')
    note_json = copy.deepcopy(NOTE)
    note_json['documentId'] = doc_id
    note_json['documentType'] = doc_type
    if expiry:
        note_json['expiryDateTime'] = expiry
    if not has_party:
        del note_json['givingNoticeParty']
    note: Db2Mhomnote = Db2Mhomnote.create_from_registration(note_json, doc, manuhome_id)
    assert note
    assert note.manuhome_id == manuhome_id
    assert note.reg_document_id == doc_id
    assert note.remarks == note_json.get('remarks')
    assert note.status == Db2Mhomnote.StatusTypes.ACTIVE
    assert note.note_id == note_json.get('noteId')
    assert note.expiry_date
    if has_party:
        assert note.name
        assert note.phone_number
        assert note.legacy_address
    else:
        assert not note.name
        assert not note.phone_number
        assert not note.legacy_address
