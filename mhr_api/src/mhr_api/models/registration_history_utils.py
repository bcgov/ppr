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

"""This module holds methods to support a manufactured home registration history model mapping to dict/json."""
from flask import current_app
from mhr_api.models import utils as model_utils
from mhr_api.models.registration_json_utils import set_group_json
from mhr_api.models.registration_utils import find_cancelled_note, get_document_description
from mhr_api.models.type_tables import (
    MhrDocumentTypes,
    MhrNoteStatusTypes,
    MhrRegistrationTypes
)

from .mhr_document import MhrDocument
from .mhr_note import MhrNote
from .mhr_registration import MhrRegistration


def get_history_json(registration: MhrRegistration, is_reg_view: bool) -> dict:
    """Get the complete history of a manufactured home as JSON."""
    current_app.logger.debug(f'{registration.mhr_number} get home history reg_view={is_reg_view}.')
    registration.staff = True
    registration.current_view = False
    registration.report_view = False
    history_json = {
        'mhrNumber': registration.mhr_number,
        'statusType': registration.status_type
    }
    if is_reg_view:
        return get_reg_view_json(registration, history_json)
    history_json = set_registrations_json(registration, history_json)
    history_json = set_descriptions_json(registration, history_json)
    history_json = set_locations_json(registration, history_json)
    history_json = set_owner_groups_json(registration, history_json)
    history_json = set_notes_json(registration, history_json)
    return history_json


def get_reg_view_json(registration: MhrRegistration, history_json: dict) -> dict:
    """Get the complete history of a manufactured home as an array of registrations in ascending order."""
    registrations_json = []
    registrations_json.append(get_reg_json(registration, None))
    if registration.change_registrations:
        for reg in registration.change_registrations:
            registrations_json.append(get_reg_json(reg, registration))
    history_json['registrations'] = registrations_json
    return history_json


def set_registrations_json(registration: MhrRegistration, history_json: dict) -> dict:
    """Get the minimal history of a manufactured home's registrations in ascending order."""
    registrations_json = []
    registrations_json.append(get_reg_summary_json(registration))
    if registration.change_registrations:
        for reg in registration.change_registrations:
            registrations_json.append(get_reg_summary_json(reg))
    history_json['registrations'] = registrations_json
    return history_json


def set_descriptions_json(registration: MhrRegistration, history_json: dict) -> dict:
    """Get the history of a manufactured home's description changes in ascending order."""
    descriptions_json = []
    descriptions_json.append(get_description_json(registration, True))
    if registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.descriptions:
                descriptions_json.append(get_description_json(reg, True))
    history_json['descriptions'] = descriptions_json
    return history_json


def set_locations_json(registration: MhrRegistration, history_json: dict) -> dict:
    """Get the history of a manufactured home's location changes in ascending order."""
    locations_json = []
    locations_json.append(get_location_json(registration))
    if registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.locations:
                locations_json.append(get_location_json(reg))
    history_json['locations'] = locations_json
    return history_json


def set_owner_groups_json(registration: MhrRegistration, history_json: dict) -> dict:
    """Get the history of a manufactured home's location changes in ascending order."""
    groups_json = []
    groups_json = get_owner_groups_json(registration, None, groups_json)
    if registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.owner_groups:
                groups_json = get_owner_groups_json(reg, registration, groups_json)
    history_json['ownerGroups'] = groups_json
    return history_json


def set_notes_json(registration: MhrRegistration, history_json: dict) -> dict:
    """Get the history of a manufactured home's note changes in ascending order."""
    if not registration.change_registrations:
        return history_json
    notes_json = []
    for reg in registration.change_registrations:
        if reg.notes:
            note_json = get_note_json(reg, registration, True)
            if note_json:
                notes_json.append(note_json)
    if notes_json:
        history_json['notes'] = notes_json
    return history_json


def set_base_reg_json(registration: MhrRegistration, reg_json: dict) -> dict:
    """Set the base registration information for a particular change."""
    if not registration or not registration.documents:
        return reg_json
    doc: MhrDocument = registration.documents[0]
    reg_json['createDateTime'] = model_utils.format_ts(registration.registration_ts)
    reg_json['registrationDescription'] = get_document_description(doc.document_type)
    reg_json['documentId'] = doc.document_id
    reg_json['documentRegistrationNumber'] = doc.document_registration_number
    return reg_json


def get_reg_summary_json(registration: MhrRegistration) -> dict:
    """Get the summary information for a particular registration."""
    doc: MhrDocument = registration.documents[0]
    reg_json = {
        'createDateTime': model_utils.format_ts(registration.registration_ts),
        'registrationDescription': get_document_description(doc.document_type),
        'documentId': doc.document_id,
        'documentRegistrationNumber': doc.document_registration_number
    }
    if doc.attention_reference:
        reg_json['attentionReference'] = doc.attention_reference
    if doc.affirm_by:
        reg_json['affirmByName'] = doc.affirm_by
    if registration.is_transfer():
        if doc.declared_value and doc.declared_value > 0:
            reg_json['declaredValue'] = doc.declared_value
        if doc.consideration_value:
            reg_json['consideration'] = doc.consideration_value
        if doc.own_land:
            reg_json['ownLand'] = doc.own_land == 'Y'
        if doc.transfer_date:
            reg_json['transferDate'] = model_utils.format_ts(doc.transfer_date)
    return reg_json


def get_reg_json(registration: MhrRegistration,  # pylint: disable=too-many-branches; just 2 more.
                 base_reg: MhrRegistration) -> dict:
    """Get the detail information of what changed for a particular registration."""
    doc: MhrDocument = registration.documents[0]
    reg_json = {
        'createDateTime': model_utils.format_ts(registration.registration_ts),
        'registrationType': registration.registration_type,
        'registrationDescription': get_document_description(doc.document_type),
        'documentId': doc.document_id,
        'documentRegistrationNumber': doc.document_registration_number
    }
    if doc.attention_reference:
        reg_json['attentionReference'] = doc.attention_reference
    if doc.affirm_by:
        reg_json['affirmByName'] = doc.affirm_by
    if registration.client_reference_id:
        reg_json['clientReferenceId'] = registration.client_reference_id
    if registration.is_transfer():
        if doc.declared_value and doc.declared_value > 0:
            reg_json['declaredValue'] = doc.declared_value
        if doc.consideration_value:
            reg_json['consideration'] = doc.consideration_value
        if doc.own_land:
            reg_json['ownLand'] = doc.own_land == 'Y'
        if doc.transfer_date:
            reg_json['transferDate'] = model_utils.format_ts(doc.transfer_date)
    if registration.locations:
        reg_json['location'] = registration.locations[0].json
    if registration.descriptions:
        reg_json['description'] = get_description_json(registration, False)
    if registration.owner_groups:
        if registration.registration_type in (MhrRegistrationTypes.MHREG, MhrRegistrationTypes.MHREG_CONVERSION):
            reg_json = set_group_json(registration, reg_json, False)
        else:
            reg_json = set_change_group_json(registration, base_reg, reg_json)
    if registration.notes:
        reg_json['note'] = get_note_json(registration, base_reg, False)
    return reg_json


def get_description_json(registration: MhrRegistration, include_reg_summary: bool = True) -> dict:
    """Get the description for a particular registration if available."""
    if not registration.descriptions:
        return {}
    description_json = registration.descriptions[0].json
    if include_reg_summary:
        description_json = set_base_reg_json(registration, description_json)
    if not description_json.get('csaNumber'):
        del description_json['csaNumber']
    if not description_json.get('csaStandard'):
        del description_json['csaStandard']
    if not description_json.get('engineerName'):
        del description_json['engineerName']
    if not description_json.get('rebuiltRemarks'):
        del description_json['rebuiltRemarks']
    if not description_json.get('otherRemarks'):
        del description_json['otherRemarks']
    sections = []
    if registration.sections:
        for section in registration.sections:
            sections.append(section.json)
    description_json['sections'] = sections
    return description_json


def get_location_json(registration: MhrRegistration) -> dict:
    """Get the location for a particular registration if available."""
    if not registration.locations:
        return {}
    location_json = registration.locations[0].json
    location_json = set_base_reg_json(registration, location_json)
    return location_json


def get_deleted_owner_groups_json(registration: MhrRegistration, base_reg: MhrRegistration, groups_json):
    """Append the deleted owner groups for a particular registration if available to the history array of groups."""
    if not base_reg.change_registrations:
        return groups_json
    # Initial reg owners may have been deleted by this registration.
    for group in base_reg.owner_groups:
        if group.registration_id != registration.id and group.change_registration_id == registration.id:
            group_json = group.json
            group_json = set_base_reg_json(registration, group_json)
            group_json['changeType'] = 'DELETED'
            groups_json.append(group_json)
    for reg in base_reg.change_registrations:
        if reg.owner_groups:
            for group in reg.owner_groups:
                if group.registration_id != registration.id and group.change_registration_id == registration.id:
                    group_json = group.json
                    group_json = set_base_reg_json(registration, group_json)
                    group_json['changeType'] = 'DELETED'
                    groups_json.append(group_json)
    return groups_json


def get_owner_groups_json(registration: MhrRegistration, base_reg: MhrRegistration, groups_json):
    """Append the owner groups for a particular registration if available to the history array of groups."""
    if not registration.owner_groups:
        return groups_json
    if not base_reg:
        for group in registration.owner_groups:
            group_json = group.json
            group_json = set_base_reg_json(registration, group_json)
            groups_json.append(group_json)
        return groups_json
    if not base_reg.change_registrations:
        return groups_json
    # Deleted first
    groups_json = get_deleted_owner_groups_json(registration, base_reg, groups_json)
    for reg in base_reg.change_registrations:
        if reg.owner_groups:
            for group in reg.owner_groups:
                group_json = group.json
                group_json = set_base_reg_json(registration, group_json)
                group_json['changeType'] = 'ADDED'
                groups_json.append(group_json)
    return groups_json


def get_note_json(registration: MhrRegistration, base_reg: MhrRegistration, include_reg_summary: bool = True) -> dict:
    """Get the note for a particular registration if available. If it is a cancel note add some original note info."""
    if not registration.notes:
        return None
    note: MhrNote = registration.notes[0]
    # Not sure if excluding: waiting on UX requirements.
    # if include_reg_summary and note.document_type in (MhrDocumentTypes.REG_103,
    #                                                  MhrDocumentTypes.REG_103E,
    #                                                  MhrDocumentTypes.AMEND_PERMIT):
    #    return None
    note_json = note.json
    if include_reg_summary:
        note_json = set_base_reg_json(registration, note_json)
    if note.document_type in (MhrDocumentTypes.NCAN, MhrDocumentTypes.NRED, MhrDocumentTypes.EXRE):
        cnote = find_cancelled_note(base_reg, note.registration_id)
        if cnote:
            note_json['cancelledDocumentType'] = cnote.document_type
            note_json['cancelledDocumentDescription'] = get_document_description(cnote.document_type)
            for reg in base_reg.change_registrations:
                if reg.id == cnote.registration_id:
                    note_json['cancelledDocumentRegistrationNumber'] = reg.documents[0].document_registration_number
                    note_json['cancelledDateTime'] = model_utils.format_ts(reg.registration_ts)
                    break
    elif base_reg and base_reg.change_registrations and note.status_type == MhrNoteStatusTypes.CANCELLED:
        for reg in base_reg.change_registrations:
            if reg.id == note.change_registration_id and note.registration_id != note.change_registration_id:
                note_json['cancelDateTime'] = model_utils.format_ts(reg.registration_ts)
                note_json['cancelDocumentDescription'] = get_document_description(reg.documents[0].document_type)
                note_json['cancelDocumentRegistrationNumber'] = reg.documents[0].document_registration_number
    return note_json


def set_change_group_json(registration: MhrRegistration, base_reg: MhrRegistration, reg_json) -> dict:
    """Build the owner groups JSON for a registration than changes owner groups."""
    add_groups = []
    delete_groups = []
    if reg_json and registration.owner_groups:
        for group in registration.owner_groups:
            add_groups.append(group.json)
    if base_reg.change_registrations:
        for reg in base_reg.change_registrations:
            for existing in reg.owner_groups:
                if existing.registration_id != registration.id and existing.change_registration_id == registration.id:
                    delete_groups.append(existing.json)
    reg_json['deleteOwnerGroups'] = delete_groups
    reg_json['addOwnerGroups'] = add_groups
    return reg_json
