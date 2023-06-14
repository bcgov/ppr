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
"""This module holds common registration validation functions.

Refactored from registration_validator.
"""
from flask import current_app

from mhr_api.models import MhrRegistration, Db2Owngroup, Db2Document, MhrDraft
from mhr_api.models import registration_utils as reg_utils
from mhr_api.models.type_tables import MhrRegistrationStatusTypes, MhrStatusTypes
from mhr_api.models.type_tables import MhrRegistrationTypes
from mhr_api.models.db2.utils import get_db2_permit_count
from mhr_api.models.utils import is_legacy
from mhr_api.services import ltsa
from mhr_api.utils import valid_charset


DOC_ID_REQUIRED = 'Document ID is required for staff registrations. '
DOC_ID_EXISTS = 'Document ID must be unique: provided value already exists. '
DOC_ID_INVALID_CHECKSUM = 'Document ID is invalid: checksum failed. '
STATE_NOT_ALLOWED = 'The MH registration is not in a state where changes are allowed. '
STATE_FROZEN_AFFIDAVIT = 'A transfer to a benificiary is pending after an AFFIDAVIT transfer. '
DRAFT_NOT_ALLOWED = 'The draft for this registration is out of date: delete the draft and resubmit. '
CHARACTER_SET_UNSUPPORTED = 'The character set is not supported for {desc} value {value}. '
PPR_LIEN_EXISTS = 'This registration is not allowed to complete as an outstanding Personal Property Registry lien ' + \
    'exists on the manufactured home. '
LOCATION_PID_INVALID = 'Location PID verification failed: either the PID is invalid or the LTSA service is ' + \
                       'unavailable. '
SUBMITTING_REQUIRED = 'Submitting Party is required for MH registrations. '


def validate_doc_id(json_data, check_exists: bool = True):
    """Validate the registration document id."""
    doc_id = json_data.get('documentId')
    current_app.logger.debug(f'Validating doc_id={doc_id}.')
    error_msg = ''
    if not doc_id:
        error_msg += DOC_ID_REQUIRED
    elif not checksum_valid(doc_id):
        error_msg += DOC_ID_INVALID_CHECKSUM
    elif check_exists:
        exists_count = MhrRegistration.get_doc_id_count(doc_id)
        if exists_count > 0:
            error_msg += DOC_ID_EXISTS
    return error_msg


def checksum_valid(doc_id: str) -> bool:
    """Validate the document id with a checksum algorithm."""
    if not doc_id or len(doc_id) != 8:
        return False
    if doc_id.startswith('1') or doc_id.startswith('9') or doc_id.startswith('8') or doc_id.startswith('REG'):
        return True
    if not doc_id.isnumeric():
        return False
    dig1: int = int(doc_id[0:1])
    dig2: int = int(doc_id[1:2]) * 2
    dig3: int = int(doc_id[2:3])
    dig4: int = int(doc_id[3:4]) * 2
    dig5: int = int(doc_id[4:5])
    dig6: int = int(doc_id[5:6]) * 2
    dig7: int = int(doc_id[6:7])
    check_digit: int = int(doc_id[7:])
    dig_sum = dig1 + dig3 + dig5 + dig7
    if dig2 > 9:
        dig_sum += 1 + (dig2 % 10)
    else:
        dig_sum += dig2
    if dig4 > 9:
        dig_sum += 1 + (dig4 % 10)
    else:
        dig_sum += dig4
    if dig6 > 9:
        dig_sum += 1 + (dig6 % 10)
    else:
        dig_sum += dig6
    mod_sum = dig_sum % 10
    current_app.logger.debug(f'sum={dig_sum}, checkdigit= {check_digit}, mod_sum={mod_sum}')
    if mod_sum == 0:
        return mod_sum == check_digit
    return (10 - mod_sum) == check_digit


def validate_registration_state(registration: MhrRegistration, staff: bool, reg_type: str):
    """Validate registration state: changes are only allowed on active homes."""
    error_msg = ''
    if not registration:
        return error_msg
    if registration.status_type and registration.status_type != MhrRegistrationStatusTypes.ACTIVE:
        error_msg += STATE_NOT_ALLOWED
    elif is_legacy() and registration.manuhome:
        if registration.manuhome.mh_status != registration.manuhome.StatusTypes.REGISTERED:
            error_msg += STATE_NOT_ALLOWED
        elif registration.manuhome.reg_documents:
            last_doc: Db2Document = registration.manuhome.reg_documents[-1]
            if not staff and last_doc.document_type == Db2Document.DocumentTypes.TRANS_AFFIDAVIT:
                error_msg += STATE_NOT_ALLOWED
            elif staff and last_doc.document_type == Db2Document.DocumentTypes.TRANS_AFFIDAVIT and \
                    reg_type != MhrRegistrationTypes.TRANS:
                error_msg += STATE_NOT_ALLOWED
                error_msg += STATE_FROZEN_AFFIDAVIT
    return error_msg


def validate_draft_state(json_data):
    """Validate draft state: no change registration on the home after the draft was created."""
    error_msg = ''
    if not json_data.get('draftNumber'):
        return error_msg
    draft: MhrDraft = MhrDraft.find_by_draft_number(json_data.get('draftNumber'))
    if draft and draft.stale_count > 0:
        error_msg += DRAFT_NOT_ALLOWED
    return error_msg


def validate_submitting_party(json_data):
    """Verify submitting party names are valid."""
    error_msg = ''
    if not json_data.get('submittingParty'):
        return SUBMITTING_REQUIRED
    party = json_data.get('submittingParty')
    desc: str = 'submitting party'
    if party.get('businessName'):
        error_msg += validate_text(party.get('businessName'), desc + ' business name')
    elif party.get('personName'):
        error_msg += validate_individual_name(party.get('personName'), desc)
    return error_msg


def validate_individual_name(name_json, desc: str = ''):
    """Verify individual name is valid."""
    error_msg = validate_text(name_json.get('first'), desc + ' first')
    error_msg += validate_text(name_json.get('last'), desc + ' last')
    error_msg += validate_text(name_json.get('middle'), desc + ' middle')
    return error_msg


def validate_text(value: str, desc: str = ''):
    """Verify text characters are valid."""
    if value and not valid_charset(value):
        return CHARACTER_SET_UNSUPPORTED.format(desc=desc, value=value)
    return ''


def validate_ppr_lien(mhr_number: str):
    """Validate that there are no PPR liens for a change registration."""
    current_app.logger.debug(f'Validating mhr_number={mhr_number}.')
    error_msg = ''
    if mhr_number:
        lien_count: int = reg_utils.get_ppr_lien_count(mhr_number)
        if lien_count > 0:
            return PPR_LIEN_EXISTS
    return error_msg


def get_existing_location(registration: MhrRegistration):
    """Get the currently active location JSON."""
    if not registration:
        return {}
    if is_legacy() and registration.manuhome and registration.manuhome.reg_location:
        return registration.manuhome.reg_location.registration_json
    if registration.locations and registration.locations[0].status_type == MhrStatusTypes.ACTIVE:
        return registration.locations[0].json
    if registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.locations and reg.locations[0].status_type == MhrStatusTypes.ACTIVE:
                return reg.locations[0].json
    return {}


def get_permit_count(mhr_number: str, name: str) -> int:
    """Execute a query to count existing transport permit registrations on a home."""
    if is_legacy():
        return get_db2_permit_count(mhr_number, name)
    return 0


def validate_pid(pid: str):
    """Validate location pid exists with an LTSA lookup."""
    error_msg = ''
    if not pid:
        return error_msg
    lookup_result = ltsa.pid_lookup(pid)
    if not lookup_result:
        error_msg = LOCATION_PID_INVALID
    return error_msg


def get_existing_group_count(registration: MhrRegistration) -> int:
    """Count number of existing owner groups."""
    group_count: int = 0
    if registration and is_legacy() and registration.manuhome:
        for existing in registration.manuhome.reg_owner_groups:
            if existing.status in (Db2Owngroup.StatusTypes.ACTIVE, Db2Owngroup.StatusTypes.EXEMPT):
                group_count += 1
    return group_count
