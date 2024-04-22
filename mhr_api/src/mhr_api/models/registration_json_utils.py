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

# pylint: disable=too-few-public-methods

"""This module holds methods to support registration model mapping to dict/json."""
from flask import current_app
from mhr_api.models import utils as model_utils
from mhr_api.models.registration_utils import include_caution_note, find_cancelled_note, get_document_description
from mhr_api.models.type_tables import (
    MhrDocumentTypes,
    MhrLocationTypes,
    MhrNoteStatusTypes,
    MhrOwnerStatusTypes,
    MhrPartyTypes,
    MhrRegistrationStatusTypes,
    MhrRegistrationTypes,
    MhrStatusTypes
)
from mhr_api.models.db2 import registration_utils as legacy_reg_utils

from .mhr_note import MhrNote


def set_payment_json(registration, reg_json: dict) -> dict:
    """Add registration payment info json if payment exists."""
    if registration.pay_invoice_id and registration.pay_path:
        payment = {
            'invoiceId': str(registration.pay_invoice_id),
            'receipt': registration.pay_path
        }
        reg_json['payment'] = payment
    return reg_json


def set_current_misc_json(registration, reg_json: dict, search: bool = False) -> dict:
    """Add miscellaneous current view registration properties."""
    dec_value: int = 0
    dec_ts = None
    own_land: bool = False
    if registration.documents[0].own_land and registration.documents[0].own_land == 'Y':
        own_land = True
    if registration.change_registrations:
        for reg in registration.change_registrations:
            doc = reg.documents[0]
            if reg.is_transfer() or reg.documents[0].document_type in (MhrDocumentTypes.REG_103,
                                                                       MhrDocumentTypes.REG_103E,
                                                                       MhrDocumentTypes.AMEND_PERMIT,
                                                                       MhrDocumentTypes.STAT,
                                                                       MhrDocumentTypes.REGC_CLIENT,
                                                                       MhrDocumentTypes.REGC_STAFF,
                                                                       MhrDocumentTypes.REGC,
                                                                       MhrDocumentTypes.PUBA):
                own_land = bool(doc.own_land and doc.own_land == 'Y')
            if reg.is_transfer() and doc.declared_value and doc.declared_value > 0 and \
                    (dec_ts is None or reg.registration_ts > dec_ts):
                dec_value = doc.declared_value
                dec_ts = reg.registration_ts
    reg_json['declaredValue'] = dec_value
    if dec_ts:
        reg_json['declaredDateTime'] = model_utils.format_ts(dec_ts)
    reg_json['ownLand'] = own_land
    if not search:
        reg_json = set_permit_json(registration, reg_json)
        reg_json = set_exempt_json(registration, reg_json)
    return reg_json


def set_permit_json(registration, reg_json: dict) -> dict:  # pylint: disable=too-many-branches; just one more.
    """Conditinally add the latest transport permit information if available."""
    if not registration or not reg_json or not registration.change_registrations:
        return reg_json
    permit_number: str = None
    permit_ts = None
    expiry_ts = None
    permit_status = None
    permit_reg_id: int = 0
    for reg in registration.change_registrations:
        if reg.documents[0].document_type == MhrDocumentTypes.REG_103:
            permit_number = reg.documents[0].document_registration_number
            permit_ts = reg.registration_ts
        # Registrations are in chronological order: get the latest permit, use latest amendment status, expiry.
        if reg.documents[0].document_type in (MhrDocumentTypes.REG_103, MhrDocumentTypes.AMEND_PERMIT):
            if reg.notes:
                permit_status = reg.notes[0].status_type
                expiry_ts = reg.notes[0].expiry_date
            permit_reg_id = reg.id
    if permit_number:
        reg_json['permitRegistrationNumber'] = permit_number
        reg_json['permitDateTime'] = model_utils.format_ts(permit_ts)
        if permit_status:
            reg_json['permitStatus'] = permit_status
        if expiry_ts:
            if expiry_ts.timestamp() < model_utils.now_ts().timestamp():
                reg_json['permitStatus'] = MhrNoteStatusTypes.EXPIRED
            reg_json['permitExpiryDateTime'] = model_utils.format_ts(expiry_ts)
        if reg_json.get('location') and permit_status == MhrStatusTypes.ACTIVE:
            reg_json['location']['permitWithinSamePark'] = is_same_mh_park(registration, reg_json)
        if permit_reg_id:
            for reg in registration.change_registrations:
                if reg.id == permit_reg_id and reg.draft:
                    reg_json['permitLandStatusConfirmation'] = reg.draft.draft.get('landStatusConfirmation', False)
        if 'permitLandStatusConfirmation' not in reg_json:
            reg_json['permitLandStatusConfirmation'] = False
    return reg_json


def is_same_mh_park(registration, reg_json: dict) -> bool:
    """When an active transport permits exists indicate if the location change was within the same MH park."""
    if not registration or not reg_json or not registration.change_registrations or not reg_json.get('location'):
        return False
    if not reg_json['location'].get('locationType') == MhrLocationTypes.MH_PARK:
        return False
    loc_reg_id: int = 0
    for reg in registration.change_registrations:
        if reg.locations and reg.locations[0].status_type == MhrStatusTypes.ACTIVE:
            loc_reg_id = reg.id
            break
    for reg in registration.change_registrations:
        if reg.locations and reg.locations[0].status_type != MhrStatusTypes.ACTIVE and \
                reg.locations[0].change_registration_id == loc_reg_id and \
                reg.locations[0].location_type == MhrLocationTypes.MH_PARK:
            current_name: str = str(reg_json['location'].get('parkName')).upper()
            return current_name == reg.locations[0].park_name
    return False


def set_exempt_json(registration, reg_json: dict) -> dict:
    """Conditinally add exemptDateTime as the timestamp of the registration that set the exempt status."""
    if not registration or not reg_json or not reg_json.get('status') == MhrRegistrationStatusTypes.EXEMPT:
        return reg_json
    exempt_ts = None
    if registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.documents[0].document_type in (MhrDocumentTypes.EXRS, MhrDocumentTypes.EXNR) and \
                    reg.notes and reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE:
                exempt_ts = reg.registration_ts
                break
        if not exempt_ts and reg_json.get('location') and reg_json['location']['address'].get('region') and \
                reg_json['location']['address'].get('region') != 'BC':  # must be either location outside of BC.
            for reg in registration.change_registrations:
                if reg.locations and reg.locations[0].status_type == MhrStatusTypes.ACTIVE:
                    exempt_ts = reg.registration_ts
                    break
    # Or conversion / initial registration set status to exempt
    if not exempt_ts and registration.registration_type in (MhrRegistrationTypes.MHREG,
                                                            MhrRegistrationTypes.MHREG_CONVERSION):
        exempt_ts = registration.registration_ts
    if exempt_ts:
        reg_json['exemptDateTime'] = model_utils.format_ts(exempt_ts)
    return reg_json


def set_submitting_json(registration, reg_json: dict) -> dict:
    """Build the submitting party JSON if available."""
    if reg_json and registration.parties:
        for party in registration.parties:
            if party.party_type == MhrPartyTypes.SUBMITTING:
                reg_json['submittingParty'] = party.json
                break
    return reg_json


def set_location_json(registration, reg_json: dict, current: bool) -> dict:
    """Add location properties to the registration JSON based on current."""
    location = None
    if registration.locations:
        loc = registration.locations[0]
        if (current or registration.current_view) and loc.status_type == MhrStatusTypes.ACTIVE:
            location = loc
        elif not (current or registration.current_view) and loc.registration_id == registration.id:
            location = loc
    if not location and current and registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.locations:
                loc = reg.locations[0]
                if loc.status_type == MhrStatusTypes.ACTIVE:
                    location = loc
    if location:
        if reg_json.get('registrationType', '') in (MhrRegistrationTypes.PERMIT,
                                                    MhrRegistrationTypes.PERMIT_EXTENSION,
                                                    MhrRegistrationTypes.AMENDMENT) and not current:
            reg_json['newLocation'] = location.json
        else:
            reg_json['location'] = location.json
    return reg_json


def get_sections_json(registration, reg_id) -> dict:
    """Build the description sections JSON from the registration id."""
    sections = []
    desc_reg = None
    if registration.id == reg_id:
        desc_reg = registration
    elif registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.id == reg_id:
                desc_reg = reg
                break
    if desc_reg and desc_reg.sections:
        for section in desc_reg.sections:
            sections.append(section.json)
    return sections


def set_description_json(registration, reg_json, current: bool) -> dict:
    """Build the description JSON conditional on current."""
    description = None
    if registration.descriptions:
        desc = registration.descriptions[0]
        if (current or registration.current_view) and desc.status_type == MhrStatusTypes.ACTIVE:
            description = desc
        elif not (current or registration.current_view) and desc.registration_id == registration.id:
            description = desc
    if not description and current and registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.descriptions:
                desc = reg.descriptions[0]
                if desc.status_type == MhrStatusTypes.ACTIVE:
                    description = desc
    if description:
        description_json = description.json
        description_json['sections'] = get_sections_json(registration, description.registration_id)
        reg_json['description'] = description_json
    return reg_json


def set_group_json(registration, reg_json, current: bool) -> dict:
    """Build the owner group JSON conditional on current."""
    owner_groups = []
    if registration.owner_groups:
        for group in registration.owner_groups:
            if (current or registration.current_view) and group.status_type in (MhrOwnerStatusTypes.ACTIVE,
                                                                                MhrOwnerStatusTypes.EXEMPT):
                owner_groups.append(group.json)
            elif not (current or registration.current_view) and group.registration_id == registration.id:
                owner_groups.append(group.json)
    if current and registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.owner_groups:
                for group in reg.owner_groups:
                    if group.status_type in (MhrOwnerStatusTypes.ACTIVE, MhrOwnerStatusTypes.EXEMPT):
                        owner_groups.append(group.json)
    reg_json['ownerGroups'] = owner_groups
    return reg_json


def set_transfer_group_json(registration, reg_json) -> dict:
    """Build the transfer registration owner groups JSON."""
    add_groups = []
    delete_groups = []
    if reg_json and registration.owner_groups:
        for group in registration.owner_groups:
            if group.registration_id == registration.id:
                add_groups.append(group.json)
            elif group.change_registration_id == registration.id:
                delete_groups.append(group.json)
    reg_json['addOwnerGroups'] = add_groups
    if registration.change_registrations:
        for reg in registration.change_registrations:
            for existing in reg.owner_groups:
                if existing.registration_id != registration.id and existing.change_registration_id == registration.id:
                    delete_groups.append(existing.json)
    reg_json['deleteOwnerGroups'] = delete_groups
    if not delete_groups and not add_groups and model_utils.is_legacy():  # Legacy MH home
        current_app.logger.debug(f'Transfer legacy MHR {registration.mhr_number} using legacy owner groups.')
        return legacy_reg_utils.set_transfer_group_json(registration, reg_json)
    return reg_json


def set_amend_correct_group_json(registration, reg_json: dict) -> dict:
    """Build the correction/amendment registration owner groups JSON."""
    if registration.reg_json and \
            registration.reg_json.get('addOwnerGroups') and \
            registration.reg_json.get('deleteOwnerGroups') and \
            reg_json.get('documentType') in (MhrDocumentTypes.REGC_CLIENT,
                                             MhrDocumentTypes.REGC_STAFF,
                                             MhrDocumentTypes.PUBA):
        reg_json = set_transfer_group_json(registration, reg_json)
    return reg_json


def update_notes_search_json(notes_json: dict, staff: bool) -> dict:
    """Build the search version of the registration as a json object."""
    if not notes_json:
        return notes_json
    updated_notes = []
    for note in notes_json:
        include: bool = True
        doc_type = note.get('documentType', '')
        if doc_type in ('REG_103', 'REG_103E', 'STAT', 'EXRE', 'NCAN', 'REG_102', 'NRED'):  # Always exclude
            include = False
        elif not staff and doc_type in ('NCON'):  # Always exclude for non-staff
            include = False
        elif not staff and doc_type == 'FZE':  # Only staff can see remarks.
            note['remarks'] = ''
        elif not staff and doc_type == 'REGC' and note.get('remarks') and \
                note['remarks'] != 'MANUFACTURED HOME REGISTRATION CANCELLED':
            # Only staff can see remarks if not default.
            note['remarks'] = 'MANUFACTURED HOME REGISTRATION CANCELLED'
        elif doc_type in ('TAXN', 'EXNR', 'EXRS', 'NPUB', 'REST', 'CAU', 'CAUC', 'CAUE') and \
                note.get('status') != MhrNoteStatusTypes.ACTIVE:  # Exclude if not active.
            include = False
        elif doc_type in ('CAU', 'CAUC', 'CAUE') and note.get('expiryDateTime') and \
                model_utils.date_elapsed(note.get('expiryDateTime')):  # Exclude if expiry elapsed.
            include = include_caution_note(notes_json, note.get('documentId'))
        if doc_type == 'FZE':  # Do not display contact info.
            if note.get('givingNoticeParty'):
                del note['givingNoticeParty']
        if include:
            updated_notes.append(note)
    return sort_notes(updated_notes)


def update_note_amend_correct(registration, note_json: dict, cancel_reg_id: int) -> dict:
    """Add cancelling registration information if an exemption note is cancelled by a correction or amendment."""
    if not registration.change_registrations:
        return note_json
    for reg in registration.change_registrations:
        if reg.id == cancel_reg_id and reg.documents[0].document_type in (MhrDocumentTypes.PUBA,
                                                                          MhrDocumentTypes.REGC_CLIENT,
                                                                          MhrDocumentTypes.REGC_STAFF):
            note_json['cancelledDocumentType'] = reg.documents[0].document_type
            note_json['cancelledDocumentDescription'] = get_document_description(reg.documents[0].document_type)
            note_json['cancelledDocumentRegistrationNumber'] = reg.documents[0].document_registration_number
            note_json['cancelledDateTime'] = model_utils.format_ts(reg.registration_ts)
    return note_json


def sort_key_notes_ts(item):
    """Sort the notes registration timestamp."""
    return item.get('createDateTime', '')


def sort_notes(notes):
    """Sort notes by registration timesamp."""
    notes.sort(key=sort_key_notes_ts, reverse=True)
    return notes


def get_notes_json(registration, search: bool, staff: bool = False) -> dict:  # pylint: disable=too-many-branches; 13
    """Fetch all the unit notes for the manufactured home. Search has special conditions on what is included."""
    notes = []
    if not registration.change_registrations:
        return notes
    cancel_notes = []
    for reg in registration.change_registrations:
        if reg.notes and (not search or reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE):
            note = reg.notes[0]
            if note.document_type in (MhrDocumentTypes.NCAN, MhrDocumentTypes.NRED, MhrDocumentTypes.EXRE):
                cnote = find_cancelled_note(registration, note.registration_id)
                if cnote:
                    cancel_note = cnote.json
                    cancel_note['ncan'] = note.json
                    cancel_notes.append(cancel_note)
            notes.append(note)
    if not notes:
        return notes
    notes_json = []
    for note in notes:  # Already sorted by timestamp.
        note_json = note.json
        if note_json.get('documentType') in (MhrDocumentTypes.NCAN, MhrDocumentTypes.NRED, MhrDocumentTypes.EXRE) and \
                cancel_notes:
            for cnote in cancel_notes:
                if cnote['ncan'].get('documentId') == note_json.get('documentId'):
                    note_json['cancelledDocumentType'] = cnote.get('documentType')
                    note_json['cancelledDocumentDescription'] = cnote.get('documentDescription')
                    note_json['cancelledDocumentRegistrationNumber'] = cnote.get('documentRegistrationNumber')
        elif note_json.get('documentType') in (MhrDocumentTypes.EXRS, MhrDocumentTypes.EXNR) and \
                note_json.get('status') == MhrNoteStatusTypes.CANCELLED and staff and not search:
            # Could be cancelled by correction/amendment - add info if available.
            note_json = update_note_amend_correct(registration, note_json, note.change_registration_id)
        if note_json.get('documentType') not in (MhrDocumentTypes.REG_103,
                                                 MhrDocumentTypes.REG_103E, MhrDocumentTypes.AMEND_PERMIT):
            notes_json.append(note_json)
    if search:
        return update_notes_search_json(notes_json, staff)
    return sort_notes(notes_json)


def get_non_staff_notes_json(registration, search: bool):
    """Build the non-BC Registries staff version of the active unit notes as JSON."""
    if search:
        return get_notes_json(registration, search)
    notes = get_notes_json(registration, search)
    if not notes:
        return notes
    updated_notes = []
    for note in notes:
        include: bool = True
        doc_type = note.get('documentType', '')
        if doc_type in (MhrDocumentTypes.STAT, MhrDocumentTypes.REG_102,  # Always exclude for non-staff
                        MhrDocumentTypes.REG_103, MhrDocumentTypes.REG_103E, MhrDocumentTypes.AMEND_PERMIT):
            include = False
        elif doc_type in ('TAXN', 'EXNR', 'EXRS', 'NPUB', 'REST', 'CAU', 'CAUC', 'CAUE', 'NCON') and \
                note.get('status') != MhrNoteStatusTypes.ACTIVE:  # Exclude if not active.
            include = False
        elif doc_type in ('CAU', 'CAUC', 'CAUE') and note.get('expiryDateTime') and \
                model_utils.date_elapsed(note.get('expiryDateTime')):  # Exclude if expiry elapsed.
            include = include_caution_note(notes, note.get('documentId'))
        # elif doc_type in ('REG_103', 'REG_103E') and note.get('expiryDateTime') and \
        #        model_utils.date_elapsed(note.get('expiryDateTime')):  # Exclude if expiry elapsed.
        if include:
            minimal_note = {
                'createDateTime': note.get('createDateTime'),
                'documentType': doc_type,
                'documentDescription':  note.get('documentDescription'),
                'status': note.get('status', '')
            }
            if doc_type in ('REG_103', 'REG_103E') and note.get('expiryDateTime'):
                minimal_note['expiryDateTime'] = note.get('expiryDateTime')
            updated_notes.append(minimal_note)
    return updated_notes


def set_note_json(registration, reg_json) -> dict:
    """Build the note JSON for an individual registration that has a unit note."""
    if reg_json and registration.notes:  # pylint: disable=too-many-nested-blocks; only 1 more.
        reg_note = registration.notes[0].json
        if reg_note.get('documentType') in (MhrDocumentTypes.NCAN,
                                            MhrDocumentTypes.NRED,
                                            MhrDocumentTypes.EXRE):
            cnote: MhrNote = find_cancelled_note(registration, registration.id)
            if cnote:
                current_app.logger.debug(f'Found cancelled note {cnote.document_type}')
                cnote_json = cnote.json
                reg_note['cancelledDocumentType'] = cnote_json.get('documentType')
                reg_note['cancelledDocumentDescription'] = cnote_json.get('documentDescription')
                reg_note['cancelledDocumentRegistrationNumber'] = cnote_json.get('documentRegistrationNumber')
            elif model_utils.is_legacy() and registration.manuhome:
                doc_id: str = registration.documents[0].document_id
                for note in registration.manuhome.reg_notes:
                    if doc_id == note.can_document_id:
                        reg_note['cancelledDocumentType'] = note.document_type
                        reg_note['cancelledDocumentDescription'] = \
                            get_document_description(note.document_type)
                        for doc in registration.manuhome.reg_documents:
                            if doc.id == note.reg_document_id:
                                reg_note['cancelledDocumentRegistrationNumber'] = doc.document_reg_id
        reg_json['note'] = reg_note
    elif reg_json and reg_json.get('documentType', '') == MhrDocumentTypes.CANCEL_PERMIT:
        return set_cancel_permit_note(registration, reg_json)
    return reg_json


def set_cancel_permit_note(registration, reg_json) -> dict:
    """Build the note JSON for a cancelled transport permit note."""
    cnote: MhrNote = find_cancelled_note(registration, registration.id)
    if cnote:
        current_app.logger.debug(f'Found cancelled note {cnote.document_type}')
        cnote_json = cnote.json
        cnote_json['cancelledDocumentType'] = cnote_json.get('documentType')
        cnote_json['cancelledDocumentDescription'] = cnote_json.get('documentDescription')
        cnote_json['cancelledDocumentRegistrationNumber'] = cnote_json.get('documentRegistrationNumber')
        reg_json['note'] = cnote_json
    elif model_utils.is_legacy() and registration.manuhome:
        doc_id: str = registration.documents[0].document_id
        reg_note = None
        for note in registration.manuhome.reg_notes:
            if doc_id == note.can_document_id:
                reg_note = {
                    'cancelledDocumentType': note.document_type,
                    'cancelledDocumentDescription': get_document_description(note.document_type)
                }
                for doc in registration.manuhome.reg_documents:
                    if doc.id == note.reg_document_id:
                        reg_note['cancelledDocumentRegistrationNumber'] = doc.document_reg_id
        if reg_note:
            reg_json['note'] = reg_note
    return reg_json
