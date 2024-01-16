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
from .location import Db2Location
from .mhomnote import Db2Mhomnote, FROM_LEGACY_STATUS
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


def set_own_land(manuhome, reg_json: dict) -> dict:
    """Assign the own land value from the initial registration or the latest transfer."""
    if not manuhome or not manuhome.current_view or not reg_json or not manuhome.reg_documents:
        return reg_json
    own_land: bool = False
    for doc in manuhome.reg_documents:
        if doc.document_type in ('101', '101 ', 'TRAN', 'DEAT', 'AFFE', 'LETA', 'WILL'):
            own_land = (doc.own_land and doc.own_land == 'Y')
    reg_json['ownLand'] = own_land
    return reg_json


def set_permit_json(manuhome, reg_json: dict) -> dict:
    """Conditinally add the latest transport permit information if available."""
    if not manuhome or not manuhome.current_view or not reg_json or not manuhome.reg_notes:
        return reg_json
    permit_number: str = None
    permit_ts = None
    expiry_dt = None
    permit_status = None
    for note in manuhome.reg_notes:
        if note.document_type in (Db2Document.DocumentTypes.PERMIT, Db2Document.DocumentTypes.PERMIT_TRIM):
            for doc in manuhome.reg_documents:
                if doc.id == note.reg_document_id and doc.document_type in (Db2Document.DocumentTypes.PERMIT,
                                                                            Db2Document.DocumentTypes.PERMIT_TRIM):
                    permit_status = FROM_LEGACY_STATUS.get(note.status)
                    expiry_dt = note.expiry_date
                    permit_number = doc.document_reg_id
                    permit_ts = doc.registration_ts
    if permit_number:
        reg_json['permitRegistrationNumber'] = permit_number
        reg_json['permitDateTime'] = model_utils.format_local_ts(permit_ts)
        reg_json['permitStatus'] = permit_status
        if expiry_dt < model_utils.today_local().date():
            reg_json['permitStatus'] = MhrNoteStatusTypes.EXPIRED
        reg_json['permitExpiryDateTime'] = model_utils.format_local_date(expiry_dt)
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
    elif doc_type == MhrDocumentTypes.CANCEL_PERMIT:
        current_app.logger.debug('Cancel transport permit looking for amended registration notes to cancel.')
        for note in manuhome.reg_notes:
            if note.status == Db2Mhomnote.StatusTypes.ACTIVE and \
                    note.document_type in (Db2Document.DocumentTypes.PERMIT, Db2Document.DocumentTypes.PERMIT_TRIM):
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
        if note.document_type in (MhrDocumentTypes.EXRS, MhrDocumentTypes.EXNR) and \
                note.status == Db2Mhomnote.StatusTypes.CANCELLED:
            for doc in reg_documents:
                if doc.id == note.can_document_id and doc.document_type in (MhrDocumentTypes.PUBA,
                                                                            MhrDocumentTypes.REGC):
                    note_json['cancelledDocumentType'] = doc.document_type
                    note_json['cancelledDocumentRegistrationNumber'] = doc.document_reg_id
                    note_json['cancelledDateTime'] = model_utils.format_local_ts(doc.registration_ts)
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


def get_transfer_doc_type(reg_json) -> str:
    """Get the legacy mapping of a transfer sale or gift document type."""
    doc_type = Db2Document.DocumentTypes.TRANS
    if reg_json.get('transferDocumentType'):
        tran_doc_type = reg_json.get('transferDocumentType')
        if len(tran_doc_type) < 5:
            doc_type = tran_doc_type
            if len(doc_type) == 3:
                doc_type += ' '
    return doc_type


def cancel_exemption_note(manuhome, doc_id: int):
    """Update status, candocid for a registration that cancels an exemption unit note."""
    if not manuhome.reg_notes:
        return
    for note in manuhome.reg_notes:
        if note.document_type in (MhrDocumentTypes.EXRS, MhrDocumentTypes.EXNR):
            note.can_document_id = doc_id
            note.status = Db2Mhomnote.StatusTypes.CANCELLED


def update_location(registration,
                    manuhome,
                    reg_json: dict,
                    new_doc_type: str,
                    new_doc_id: str):
    """Update location and conditionally status if location out of province."""
    if not reg_json or not reg_json.get('location') or not new_doc_type or \
            new_doc_type not in (MhrDocumentTypes.REGC,
                                 MhrDocumentTypes.REGC_CLIENT,
                                 MhrDocumentTypes.REGC_STAFF,
                                 MhrDocumentTypes.STAT,
                                 MhrDocumentTypes.PUBA,
                                 MhrDocumentTypes.CANCEL_PERMIT):
        return manuhome
    manuhome.new_location = Db2Location.create_from_registration(registration, reg_json, False)
    manuhome.new_location.manuhome_id = manuhome.id
    manuhome.new_location.location_id = (manuhome.reg_location.location_id + 1)
    manuhome.reg_location.status = Db2Location.StatusTypes.HISTORICAL
    manuhome.reg_location.can_document_id = new_doc_id
    if new_doc_type == MhrDocumentTypes.CANCEL_PERMIT and \
            manuhome.mh_status == 'E' and manuhome.new_location.province and \
            manuhome.new_location.province == model_utils.PROVINCE_BC:
        manuhome.mh_status = 'R'
    elif new_doc_type in (MhrDocumentTypes.CANCEL_PERMIT, MhrDocumentTypes.STAT) and \
            manuhome.new_location.province and manuhome.new_location.province != model_utils.PROVINCE_BC:
        manuhome.mh_status = 'E'
    return manuhome
