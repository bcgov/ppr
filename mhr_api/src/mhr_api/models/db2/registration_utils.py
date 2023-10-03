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
"""This module holds miscellaneous legacy registration utility functions."""
from flask import current_app

from mhr_api.models import utils as model_utils
from mhr_api.models.type_tables import (
    MhrDocumentTypes,
    MhrNoteStatusTypes,
    MhrPartyTypes,
    MhrStatusTypes,
    MhrTenancyTypes
)

from .document import Db2Document
from .mhomnote import Db2Mhomnote
from .owngroup import Db2Owngroup


def update_note_json(registration, note_json: dict) -> dict:
    """Conditionally update the note json with new registration data if available."""
    if not registration.change_registrations:
        return note_json
    for reg in registration.change_registrations:
        if reg.notes:
            doc = reg.documents[0]
            if doc.document_id == note_json.get('documentId'):
                note_json['createDateTime'] = model_utils.format_ts(reg.registration_ts)
                note = reg.notes[0]
                if note.expiry_date:
                    note_json['expiryDateTime'] = model_utils.format_ts(note.expiry_date)
                if note.effective_ts:
                    note_json['effectiveDateTime'] = model_utils.format_ts(note.effective_ts)
                if note.document_type in (MhrDocumentTypes.NCAN, MhrDocumentTypes.NRED, MhrDocumentTypes.EXRE):
                    note_json['remarks'] = note.remarks
                # Use modernized person giving notice data if available.
                notice_party = note.get_giving_notice()
                if notice_party:
                    note_json['givingNoticeParty'] = notice_party.json
    return note_json


def update_location_json(registration, reg_json: dict) -> dict:
    """Conditionally update the location json with the modernized registration data if available."""
    if not registration.locations:
        return reg_json
    active_loc = registration.locations[0]
    active_doc_id = registration.documents[0].document_id
    if active_loc.status_type != MhrStatusTypes.ACTIVE and registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.locations and reg.locations[0].status_type == MhrStatusTypes.ACTIVE:
                active_loc = reg.locations[0]
                active_doc_id = reg.documents[0].document_id
    if active_loc.status_type == MhrStatusTypes.ACTIVE and active_doc_id:
        legacy_loc = registration.manuhome.reg_location
        for doc in registration.manuhome.reg_documents:
            if legacy_loc.reg_document_id == doc.id:
                current_app.logger.info(f'Comparing modern doc_id={active_doc_id} to legacy id={doc.id}')
                if active_doc_id == legacy_loc.reg_document_id:
                    current_app.logger.debug('Using modernized location data')
                    reg_json['location'] = active_loc.json
    return reg_json


def update_description_json(registration, reg_json: dict) -> dict:
    """Conditionally update the description json with the modernized registration data if available."""
    if not registration.descriptions:
        return reg_json
    active_desc = registration.descriptions[0]
    active_doc_id = registration.documents[0].document_id
    if active_desc.status_type != MhrStatusTypes.ACTIVE and registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.descriptions and reg.descriptions[0].status_type == MhrStatusTypes.ACTIVE:
                active_desc = reg.descriptions[0]
                active_doc_id = reg.documents[0].document_id
    if active_desc.status_type == MhrStatusTypes.ACTIVE and active_doc_id:
        legacy_desc = registration.manuhome.reg_descript
        for doc in registration.manuhome.reg_documents:
            if legacy_desc.reg_document_id == doc.id:
                current_app.logger.info(f'Comparing modern doc_id={active_doc_id} to legacy id={doc.id}')
                if active_doc_id == legacy_desc.reg_document_id:
                    current_app.logger.debug('Using modernized description data')
                    desc_json = active_desc.json
                    desc_json['sections'] = reg_json['description'].get('sections')
                    reg_json['description'] = desc_json
    return reg_json


def set_owner_sequence_num(owner_groups) -> int:
    """Get the next owner group sequence number."""
    sequence_num: int = 1
    if owner_groups:
        for group in owner_groups:
            if group.status in (Db2Owngroup.StatusTypes.ACTIVE, Db2Owngroup.StatusTypes.EXEMPT):
                group.sequence_number = sequence_num
                sequence_num += 1


def update_group_type(groups, existing_count: int = 0):
    """Set type if multiple active owner groups and a trustee, admin, executor exists."""
    if not groups or ((len(groups) + existing_count) == 1 and groups[0].get('type') == MhrTenancyTypes.SOLE):
        return groups
    for group in groups:
        for owner in group.get('owners'):
            if owner.get('partyType') and owner['partyType'] in (MhrPartyTypes.ADMINISTRATOR,
                                                                 MhrPartyTypes.EXECUTOR,
                                                                 MhrPartyTypes.TRUSTEE):
                group['type'] = MhrTenancyTypes.NA
                break
    return groups


def adjust_group_interest(groups, new: bool):
    """For TC and optionally JT groups adjust group interest value."""
    tc_count: int = 0
    for group in groups:
        if group.tenancy_type != Db2Owngroup.TenancyTypes.SOLE and \
                group.status == Db2Owngroup.StatusTypes.ACTIVE and \
                group.interest_numerator and group.interest_denominator and \
                group.interest_numerator > 0 and group.interest_denominator > 0:
            tc_count += 1
    if tc_count > 0:
        for group in groups:
            if new or (group.modified and group.status == Db2Owngroup.StatusTypes.ACTIVE):
                fraction: str = str(group.interest_numerator) + '/' + str(group.interest_denominator)
                if len(fraction) > 10:
                    group.interest = ''
                elif group.interest.upper().startswith(model_utils.OWNER_INTEREST_UNDIVIDED):
                    group.interest = model_utils.OWNER_INTEREST_UNDIVIDED + ' '
                else:
                    group.interest = ''
                group.interest += fraction
                current_app.logger.debug('Updating group interest to: ' + group.interest)


def get_next_note_id(reg_notes) -> int:
    """Get the next mhomnote.note_id value: part of the composite key."""
    note_id: int = 1
    if reg_notes:
        for note in reg_notes:
            if note.note_id >= note_id:
                note_id = note.note_id + 1
    return note_id


def set_caution(notes) -> bool:
    """Check if an active caution exists on the MH registration: exists and not cancelled or expired."""
    has_caution: bool = False
    if not notes:
        return has_caution
    for note in notes:
        if note.document_type in (MhrDocumentTypes.CAU, MhrDocumentTypes.CAUC, MhrDocumentTypes.CAUE) and \
                note.status == Db2Mhomnote.StatusTypes.ACTIVE:
            if (not note.expiry_date or note.expiry_date.isoformat() == '0001-01-01') and \
                    note.document_type == MhrDocumentTypes.CAUC:
                has_caution = True
            elif note.expiry_date:
                now_ts = model_utils.now_ts()
                has_caution = note.expiry_date > now_ts.date()
                break
    return has_caution


def cancel_note(manuhome, reg_json, doc_type: str, doc_id: int):
    """Update status, candocid for a registration that cancels a unit note."""
    if not reg_json.get('cancelDocumentId') and not reg_json.get('updateDocumentId'):
        return
    cancel_doc_type: str = None
    cancel_doc_id: str = reg_json.get('cancelDocumentId')
    if not cancel_doc_id:
        cancel_doc_id: str = reg_json.get('updateDocumentId')
    for note in manuhome.reg_notes:
        if note.reg_document_id == cancel_doc_id:
            note.can_document_id = doc_id
            note.status = Db2Mhomnote.StatusTypes.CANCELLED
            cancel_doc_type = note.document_type
            break
    if doc_type == MhrDocumentTypes.NCAN and cancel_doc_type in (MhrDocumentTypes.CAU,
                                                                 Db2Document.DocumentTypes.CAUTION,
                                                                 Db2Document.DocumentTypes.CONTINUE_CAUTION,
                                                                 Db2Document.DocumentTypes.EXTEND_CAUTION):
        for note in manuhome.reg_notes:
            if note.status == Db2Mhomnote.StatusTypes.ACTIVE and \
                    note.document_type in (MhrDocumentTypes.CAU, Db2Document.DocumentTypes.CAUTION,
                                           Db2Document.DocumentTypes.CONTINUE_CAUTION,
                                           Db2Document.DocumentTypes.EXTEND_CAUTION):
                note.can_document_id = doc_id
                note.status = Db2Mhomnote.StatusTypes.CANCELLED
    elif doc_type == MhrDocumentTypes.EXRE and cancel_doc_type in (MhrDocumentTypes.EXNR,
                                                                   MhrDocumentTypes.EXRS,
                                                                   MhrDocumentTypes.EXMN):
        for note in manuhome.reg_notes:
            if note.status == Db2Mhomnote.StatusTypes.ACTIVE and \
                    note.document_type in (MhrDocumentTypes.EXNR, MhrDocumentTypes.EXRS, MhrDocumentTypes.EXMN):
                note.can_document_id = doc_id
                note.status = Db2Mhomnote.StatusTypes.CANCELLED


def get_note_doc_reg_num(reg_documents, doc_id: str) -> str:
    """Get the document registration number matching the doc_id from document."""
    reg_num: str = ''
    if doc_id and reg_documents:
        for doc in reg_documents:
            if doc.id == doc_id:
                return doc.document_reg_id
    return reg_num


def sort_key_notes_ts(item):
    """Sort the notes registration timestamp."""
    return item.get('createDateTime', '')


def sort_notes(notes):
    """Sort notes by registration timesamp."""
    notes.sort(key=sort_key_notes_ts, reverse=True)
    return notes


def get_notes_json(reg_notes, reg_documents):
    """Get the unit notes json sorted in descending order by timestamp (most recent first)."""
    notes = []
    if not reg_notes or not reg_documents:
        return notes
    for note in reg_notes:
        note_json = note.registration_json
        note_json['documentRegistrationNumber'] = get_note_doc_reg_num(reg_documents, note.reg_document_id)
        notes.append(note_json)
    # Add any NCAN registration using the cancelled note as a base.
    for doc in reg_documents:
        if doc.document_type in (MhrDocumentTypes.NCAN, MhrDocumentTypes.NRED, MhrDocumentTypes.EXRE):
            for note in reg_notes:
                if doc.id == note.can_document_id:
                    cancel_json = note.registration_json
                    note_json = {
                        'cancelledDocumentType': cancel_json.get('documentType'),
                        'cancelledDocumentRegistrationNumber': get_note_doc_reg_num(reg_documents,
                                                                                    note.reg_document_id),
                        'documentType': doc.document_type.strip(),
                        'documentId': doc.id,
                        'documentRegistrationNumber': doc.document_reg_id,
                        'status': MhrNoteStatusTypes.ACTIVE.value,
                        'createDateTime':  model_utils.format_local_ts(doc.registration_ts),
                        'remarks': cancel_json.get('remarks'),
                        'givingNoticeParty': cancel_json.get('givingNoticeParty')
                    }
                    notes.append(note_json)
    # Now sort in descending timestamp order.
    return sort_notes(notes)
