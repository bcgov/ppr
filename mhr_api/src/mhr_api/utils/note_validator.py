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
"""This module holds unit note registration validation for rules not covered by the schema.

Validation includes verifying the data combination for various registration document types and timestamps.
"""
from flask import current_app

from mhr_api.models import MhrRegistration, utils as model_utils
from mhr_api.models.type_tables import MhrRegistrationTypes, MhrDocumentTypes

from .registration_validator import validate_ppr_lien, validate_submitting_party, \
    validate_registration_state, checksum_valid


VALIDATOR_ERROR = 'Error performing manufacturer extra validation. '
DOC_ID_REQUIRED = 'Document ID is required for staff registrations. '
DOC_ID_EXISTS = 'Document ID must be unique: provided value already exists. '
DOC_ID_INVALID_CHECKSUM = 'Document ID is invalid: checksum failed. '
EFFECTIVE_FUTURE = 'Effective date and time cannot be in the future. '
EFFECTIVE_PAST = 'Effective date and time cannot be in the past for the registration document type {doc_type}. '
EFFECTIVE_NOT_ALLOWED = 'Effective date and time is not allowed for the registration document type {doc_type}. '
EXPIRY_REQUIRED = 'Expiry date and time is required for the registration document type. '
EXPIRY_NOT_ALLOWED = 'Expiry date and time is not allowed for the registration document type. '
EXPIRY_PAST = 'Expiry date and time cannot be in the past for the registration document type. '
EXPIRY_BEFORE_CURRENT = 'New expiry date and time must be after the current expiry date and time. '
EXPIRY_CURRENT_EXPIRED = 'Registration not allowed: the current expiry date and time has elapsed. '
REMARKS_REQUIRED = 'Remarks are required with the registration document type. '
REMARKS_NOT_ALLOWED = 'Remarks are not allowed with the registration document type. '
NOTICE_REQUIRED = 'The giving notice party is required with the registration document type. '
NOTICE_NAME_REQUIRED = 'The giving notice party person or business name is required. '
NOTICE_ADDRESS_REQUIRED = 'The giving notice address is required. '


def validate_note(registration: MhrRegistration, json_data, staff: bool = False, group_name: str = None) -> str:
    """Perform all extra manufacturer unit note registration data validation checks not covered by schema validation."""
    error_msg: str = ''
    try:
        current_app.logger.info(f'Validating unit note registration staff={staff}, group={group_name}')
        if registration:
            error_msg += validate_ppr_lien(registration.mhr_number)
        error_msg += validate_doc_id(json_data)
        error_msg += validate_submitting_party(json_data)
        error_msg += validate_registration_state(registration, staff, MhrRegistrationTypes.REG_NOTE)
        doc_type: str = None
        if json_data.get('note') and json_data['note'].get('documentType'):
            doc_type = json_data['note'].get('documentType')
        error_msg += validate_remarks(json_data, doc_type)
        error_msg += validate_giving_notice(json_data, doc_type)
        error_msg += validate_effective_ts(json_data, doc_type)
        error_msg += validate_expiry_ts(registration, json_data, doc_type)
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_noteexception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


def validate_doc_id(json_data, check_exists: bool = True) -> str:
    """Validate the registration document id."""
    doc_id: str = ''
    if json_data.get('note'):
        doc_id = json_data['note'].get('documentId')
    current_app.logger.debug(f'Validating doc_id={doc_id}.')
    error_msg: str = ''
    if not doc_id:
        error_msg += DOC_ID_REQUIRED
    elif not checksum_valid(doc_id):
        error_msg += DOC_ID_INVALID_CHECKSUM
    elif check_exists:
        exists_count = MhrRegistration.get_doc_id_count(doc_id)
        if exists_count > 0:
            error_msg += DOC_ID_EXISTS
    return error_msg


def validate_remarks(json_data, doc_type: str) -> str:
    """Validate the registration remarks."""
    error_msg: str = ''
    if not json_data.get('note'):
        return error_msg
    if doc_type and not json_data['note'].get('remarks') and doc_type == MhrDocumentTypes.CAU:
        error_msg += REMARKS_REQUIRED
    elif doc_type and json_data['note'].get('remarks') and doc_type == MhrDocumentTypes.NCAN:
        error_msg += REMARKS_NOT_ALLOWED
    return error_msg


def validate_giving_notice(json_data, doc_type: str) -> str:
    """Validate the registration giving notice party."""
    error_msg: str = ''
    if not json_data.get('note'):
        return error_msg
    if doc_type and not json_data['note'].get('givingNoticeParty') and \
            doc_type in (MhrDocumentTypes.CAU, MhrDocumentTypes.CAUC, MhrDocumentTypes.CAUE,
                         MhrDocumentTypes.NCAN, MhrDocumentTypes.REST, MhrDocumentTypes.TAXN):
        error_msg += NOTICE_REQUIRED
    elif json_data['note'].get('givingNoticeParty'):
        notice = json_data['note'].get('givingNoticeParty')
        if not notice.get('address'):
            error_msg += NOTICE_ADDRESS_REQUIRED
        if not notice.get('personName') and not notice.get('businessName'):
            error_msg += NOTICE_NAME_REQUIRED
    return error_msg


def validate_effective_ts(json_data, doc_type: str) -> str:
    """Validate the registration effective timestamp."""
    error_msg: str = ''
    if not json_data.get('note') or not json_data['note'].get('effectiveDateTime'):
        return error_msg
    effective = json_data['note'].get('effectiveDateTime')
    effective_ts = model_utils.ts_from_iso_format(effective)
    now = model_utils.now_ts()
    if effective_ts > now:
        error_msg += EFFECTIVE_FUTURE
    elif effective_ts < now and doc_type and \
            doc_type not in (MhrDocumentTypes.CAU, MhrDocumentTypes.CAUC, MhrDocumentTypes.CAUE,
                             MhrDocumentTypes.NCON, MhrDocumentTypes.NPUB, MhrDocumentTypes.REST,
                             MhrDocumentTypes.TAXN, MhrDocumentTypes.REG_102):
        error_msg += EFFECTIVE_PAST.format(doc_type=doc_type)
    if doc_type and doc_type == MhrDocumentTypes.NCAN:
        error_msg += EFFECTIVE_NOT_ALLOWED.format(doc_type=doc_type)
    return error_msg


def validate_expiry_ts(registration: MhrRegistration, json_data, doc_type: str) -> str:
    """Validate the registration expiry timestamp."""
    error_msg: str = ''
    if not json_data.get('note') or not doc_type:
        return error_msg
    if not json_data['note'].get('expiryDateTime') and doc_type == MhrDocumentTypes.CAUE:
        error_msg += EXPIRY_REQUIRED
    if not json_data['note'].get('expiryDateTime'):
        return error_msg
    expiry = json_data['note'].get('expiryDateTime')
    if doc_type not in (MhrDocumentTypes.CAUC, MhrDocumentTypes.CAUE):
        error_msg += EXPIRY_NOT_ALLOWED
    else:
        expiry_ts = model_utils.ts_from_iso_format(expiry)
        now = model_utils.now_ts()
        if expiry_ts < now:
            error_msg += EXPIRY_PAST
        if doc_type == MhrDocumentTypes.CAUE:
            expiry = get_cau_note_expiry(registration)
            if expiry and expiry_ts.date() < expiry:
                error_msg += EXPIRY_BEFORE_CURRENT
            if expiry and expiry < now.date():
                error_msg += EXPIRY_CURRENT_EXPIRED
    return error_msg


def get_cau_note_expiry(registration: MhrRegistration):
    """Get the most recent CAU note expiry timestamp."""
    expiry = None
    if not registration:
        return expiry
    if model_utils.is_legacy() and registration.manuhome and registration.manuhome.notes:
        for note in registration.manuhome.notes:
            if note.document_type in ('CAU', 'CAU '):
                expiry = note.expiry_date
    elif not model_utils.is_legacy and registration.notes:
        for note in registration.notes:
            if note.document_type == MhrDocumentTypes.CAU:
                expiry = note.expiry_date
    return expiry
