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
"""This module holds common validation functions for legacy DB2 manufactured homes.

Refactored from registration_validator.
"""
from flask import current_app
from mhr_api.models import Db2Manuhome, Db2Owngroup, Db2Document, Db2Mhomnote, Db2Owner, utils as model_utils
from mhr_api.models import registration_json_utils as reg_json_utils
from mhr_api.models.type_tables import (
    MhrDocumentTypes,
    MhrPartyTypes,
    MhrRegistrationTypes,
    MhrStatusTypes,
    MhrTenancyTypes
)
from mhr_api.models.db2.owngroup import NEW_TENANCY_LEGACY
from mhr_api.models.db2.utils import get_db2_permit_count
from mhr_api.models.utils import to_db2_ind_name


STATE_NOT_ALLOWED = 'The MH registration is not in a state where changes are allowed. '
STATE_FROZEN_AFFIDAVIT = 'A transfer to a benificiary is pending after an AFFIDAVIT transfer. '
STATE_FROZEN_NOTE = 'Registration not allowed: this manufactured home has an active TAXN, NCON, or REST unit note. '
STATE_FROZEN_PERMIT = 'Registration not allowed: this manufactured home has an active transport permit. '
STATE_FROZEN_EXEMPT = 'Registration not allowed: this manufactured home has an active exemption registration. '
EXEMPT_EXNR_INVALID = 'Registration not allowed: the home is exempt because of an existing non-residential exemption. '
EXEMPT_EXRS_INVALID = 'Residential exemption registration not allowed: the home is already exempt. '
DELETE_GROUP_ID_INVALID = 'The owner group with ID {group_id} is not active and cannot be changed. '
DELETE_GROUP_ID_NONEXISTENT = 'No owner group with ID {group_id} exists. '
DELETE_GROUP_TYPE_INVALID = 'The owner group tenancy type with ID {group_id} is invalid. '
GROUP_INTEREST_MISMATCH = 'The owner group interest numerator sum does not equal the interest common denominator. '
AMEND_PERMIT_INVALID = 'Amend transport permit not allowed: no active tansport permit exists.'
STATE_ACTIVE_PERMIT = 'New transport permit registration not allowed: an active permit registration exists. ' + \
    'Staff or the account that created the active transport permit can resubmit with moveCompleted set to true. '
EXEMPT_PERMIT_INVALID = 'Registration not allowed: the home is not exempt because of a transport permit location. '
OWNER_SUFFIX_MAX_LENGTH = 'Owner name suffix character length exceeds the legacy maximum allowed length of 70 ' + \
    '(extra middle names may be included). '


def validate_registration_state(registration,  # pylint: disable=too-many-branches; 1 more
                                staff: bool,
                                reg_type: str,
                                doc_type: str = None,
                                reg_json: dict = None):
    """Validate registration state: changes are only allowed on active homes."""
    error_msg = ''
    current_app.logger.debug(f'Validating legacy registration state reg type={reg_type} doc type={doc_type}')
    if not registration or not registration.manuhome:
        return error_msg
    manuhome: Db2Manuhome = registration.manuhome
    current_app.logger.debug(f'MH status={manuhome.mh_status}')
    if doc_type and doc_type == MhrDocumentTypes.EXRE:
        return validate_registration_state_exre(manuhome)
    if reg_type and reg_type in (MhrRegistrationTypes.EXEMPTION_NON_RES, MhrRegistrationTypes.EXEMPTION_RES):
        return validate_registration_state_exemption(manuhome, reg_type, staff)
    if reg_type and reg_type == MhrRegistrationTypes.PERMIT:  # Prevent if active permit exists.
        if not doc_type or doc_type != MhrDocumentTypes.AMEND_PERMIT:
            error_msg += validate_no_active_permit(registration, reg_json)
    if manuhome.mh_status != manuhome.StatusTypes.REGISTERED:
        if doc_type and doc_type == MhrDocumentTypes.EXRE:
            current_app.logger.debug(f'Allowing EXEMPT/CANCELLED state registration for doc type={doc_type}')
        elif manuhome.mh_status == manuhome.StatusTypes.EXEMPT and doc_type and \
                doc_type in (MhrDocumentTypes.PUBA, MhrDocumentTypes.REGC_STAFF, MhrDocumentTypes.REGC_CLIENT):
            current_app.logger.debug(f'Allowing EXEMPT state registration for doc type={doc_type}')
        elif manuhome.mh_status == manuhome.StatusTypes.EXEMPT and doc_type and \
                doc_type == MhrDocumentTypes.CANCEL_PERMIT:
            return check_state_cancel_permit(manuhome, error_msg)
        elif manuhome.mh_status == manuhome.StatusTypes.EXEMPT and doc_type and \
                doc_type == MhrDocumentTypes.AMEND_PERMIT:
            return check_exempt_permit(manuhome, staff, error_msg)
        elif manuhome.mh_status == manuhome.StatusTypes.CANCELLED or \
                doc_type is None or \
                doc_type not in (MhrDocumentTypes.NPUB, MhrDocumentTypes.NCON,
                                 MhrDocumentTypes.NCAN, MhrDocumentTypes.NRED,
                                 MhrDocumentTypes.CANCEL_PERMIT):
            error_msg += STATE_NOT_ALLOWED
    elif manuhome.reg_documents:
        last_doc: Db2Document = manuhome.reg_documents[-1]
        if not staff and last_doc.document_type == Db2Document.DocumentTypes.TRANS_AFFIDAVIT:
            error_msg += STATE_NOT_ALLOWED
        elif staff and last_doc.document_type == Db2Document.DocumentTypes.TRANS_AFFIDAVIT and \
                reg_type != MhrRegistrationTypes.TRANS:
            error_msg += STATE_NOT_ALLOWED
            error_msg += STATE_FROZEN_AFFIDAVIT
    return check_state_note(manuhome, staff, error_msg, reg_type, doc_type)


def validate_registration_state_exre(manuhome: Db2Manuhome):
    """Validate registration state for rescind exemption requests."""
    error_msg = ''
    if manuhome.mh_status in (manuhome.StatusTypes.EXEMPT, manuhome.StatusTypes.CANCELLED):
        return error_msg
    return STATE_NOT_ALLOWED


def validate_registration_state_exemption(manuhome: Db2Manuhome, reg_type: str, staff: bool):
    """Validate registration state for residential/non-residential exemption requests."""
    error_msg = ''
    if manuhome.mh_status == manuhome.StatusTypes.REGISTERED:
        return check_state_note(manuhome, staff, error_msg, reg_type)
    if manuhome.mh_status == manuhome.StatusTypes.CANCELLED:
        error_msg += STATE_NOT_ALLOWED
    elif reg_type == MhrRegistrationTypes.EXEMPTION_RES:
        error_msg += EXEMPT_EXRS_INVALID
    # else:
    #    for note in manuhome.reg_notes:
    #        if note.document_type == MhrDocumentTypes.EXNR and note.status == Db2Mhomnote.StatusTypes.ACTIVE:
    #            error_msg += EXEMPT_EXNR_INVALID
    return error_msg


def check_exempt_permit(manuhome: Db2Manuhome, staff: bool, error_msg: str) -> str:
    """Check home is exempt because active permit location is outside of BC."""
    if staff or not manuhome.mh_status == Db2Manuhome.StatusTypes.EXEMPT:
        return error_msg
    # current_app.logger.debug(f'Location province = {manuhome.reg_location.province}')
    if manuhome.reg_notes:
        for note in manuhome.reg_notes:
            if note.document_type in (Db2Document.DocumentTypes.PERMIT,
                                      Db2Document.DocumentTypes.PERMIT_TRIM,
                                      Db2Document.DocumentTypes.PERMIT_EXTENSION) and \
                    note.status == Db2Mhomnote.StatusTypes.ACTIVE and \
                    manuhome.reg_location.province != 'BC':
                current_app.logger.debug('Exempt because transport permit location not BC.')
                return error_msg
    error_msg += EXEMPT_PERMIT_INVALID
    return error_msg


def get_existing_location(registration) -> dict:
    """Get the currently active location JSON."""
    if not registration or not registration.manuhome:
        return {}
    manuhome: Db2Manuhome = registration.manuhome
    if manuhome and manuhome.reg_location:
        # Use modernized if exists.
        doc_id: str = manuhome.reg_location.reg_document_id
        if registration.locations and registration.locations[0].status_type == MhrStatusTypes.ACTIVE and \
                registration.documents and registration.documents[0].document_id == doc_id:
            return registration.locations[0].json
        if registration.change_registrations:
            for reg in registration.change_registrations:
                if reg.locations and reg.locations[0].status_type == MhrStatusTypes.ACTIVE and \
                        reg.documents and reg.documents[0].document_id == doc_id:
                    return reg.locations[0].json
        return manuhome.reg_location.registration_json
    return {}


def get_existing_description(registration) -> dict:
    """Get the currently active description JSON."""
    if not registration or not registration.manuhome:
        return {}
    manuhome: Db2Manuhome = registration.manuhome
    if manuhome and manuhome.reg_descript:
        # Use modernized if exists.
        doc_id: str = manuhome.reg_descript.reg_document_id
        if registration.descriptions and registration.descriptions[0].status_type == MhrStatusTypes.ACTIVE and \
                registration.documents and registration.documents[0].document_id == doc_id:
            description = registration.descriptions[0]
            description_json = description.json
            description_json['sections'] = reg_json_utils.get_sections_json(registration,
                                                                            description.registration_id)
            return description_json
        if registration.change_registrations:
            for reg in registration.change_registrations:
                if reg.descriptions and reg.descriptions[0].status_type == MhrStatusTypes.ACTIVE and \
                        reg.documents and reg.documents[0].document_id == doc_id:
                    description = reg.descriptions[0]
                    description_json = description.json
                    description_json['sections'] = reg_json_utils.get_sections_json(registration,
                                                                                    description.registration_id)
                    return description_json
        return manuhome.reg_descript.registration_json
    return {}


def get_permit_count(mhr_number: str, name: str) -> int:
    """Execute a query to count existing transport permit registrations on a home."""
    return get_db2_permit_count(mhr_number, name)


def get_existing_group_count(registration) -> int:
    """Count number of existing owner groups."""
    group_count: int = 0
    if not registration or not registration.manuhome:
        return group_count
    manuhome: Db2Manuhome = registration.manuhome
    for existing in manuhome.reg_owner_groups:
        if existing.status in (Db2Owngroup.StatusTypes.ACTIVE, Db2Owngroup.StatusTypes.EXEMPT):
            group_count += 1
    return group_count


def get_existing_owner_groups(registration) -> dict:
    """Get the existing active/exempt owner groups."""
    groups = []
    if not registration or not registration.manuhome:
        return groups
    manuhome: Db2Manuhome = registration.manuhome
    for existing in manuhome.reg_owner_groups:
        if existing.status in (Db2Owngroup.StatusTypes.ACTIVE, Db2Owngroup.StatusTypes.EXEMPT):
            groups.append(existing.json)
    return groups


def check_state_note(manuhome: Db2Manuhome, staff: bool, error_msg: str, reg_type: str, doc_type: str = None) -> str:
    """Check registration state for non-staff: frozen if active TAXN, NCON, or REST unit note."""
    if staff:
        return error_msg
    if manuhome.notes:
        for note in manuhome.reg_notes:
            if note.document_type in (MhrDocumentTypes.TAXN, MhrDocumentTypes.NCON, MhrDocumentTypes.REST) and \
                    note.status == Db2Mhomnote.StatusTypes.ACTIVE:
                error_msg += STATE_FROZEN_NOTE
            elif note.document_type in (Db2Document.DocumentTypes.PERMIT,
                                        Db2Document.DocumentTypes.PERMIT_TRIM,
                                        Db2Document.DocumentTypes.PERMIT_EXTENSION) and \
                    reg_type not in (MhrRegistrationTypes.PERMIT, MhrRegistrationTypes.PERMIT_EXTENSION) and \
                    note.status == Db2Mhomnote.StatusTypes.ACTIVE and note.expiry_date and \
                    note.expiry_date > model_utils.today_local().date():
                # STATE_FROZEN_PERMIT rule removed for QS residential exemptions 21424.
                if not model_utils.is_transfer(reg_type) and MhrRegistrationTypes.EXEMPTION_RES != reg_type and \
                        (not doc_type or doc_type != MhrDocumentTypes.CANCEL_PERMIT):
                    error_msg += STATE_FROZEN_PERMIT
    return error_msg


def check_state_cancel_permit(manuhome: Db2Manuhome, error_msg: str) -> str:
    """Check no active exemption registration exists: cancel permit not allowed in this state."""
    if manuhome.notes:
        for note in manuhome.reg_notes:
            if note.document_type in (MhrDocumentTypes.EXRS,
                                      MhrDocumentTypes.EXMN,
                                      MhrDocumentTypes.EXNR) and note.status == Db2Mhomnote.StatusTypes.ACTIVE:
                error_msg += STATE_FROZEN_EXEMPT
    return error_msg


def owner_name_match(registration=None, request_owner: dict = None) -> bool:
    """Verify the request owner name matches one of the current owner names."""
    request_name: str = ''
    match: bool = False
    if not registration or not registration.manuhome or not registration.manuhome.reg_owner_groups or not request_owner:
        return match
    is_business = request_owner.get('organizationName')
    if is_business:
        request_name = request_owner.get('organizationName').strip().upper()
    elif request_owner.get('individualName') and request_owner['individualName'].get('first') and \
            request_owner['individualName'].get('last'):
        request_name = to_db2_ind_name(request_owner.get('individualName')).strip()
    if not request_name:
        return False
    for group in registration.manuhome.reg_owner_groups:
        if group.status == Db2Owngroup.StatusTypes.ACTIVE:
            for owner in group.owners:
                if owner.owner_type == Db2Owner.OwnerTypes.BUSINESS and is_business and \
                        owner.name.strip() == request_name:
                    return True
                if owner.owner_type == Db2Owner.OwnerTypes.INDIVIDUAL and not is_business and \
                        owner.name.strip() == request_name:
                    return True
    return match


def validate_delete_owners(registration=None, json_data: dict = None) -> str:
    """Check groups id's and owners are valid for deleted groups."""
    error_msg = ''
    if not registration or not registration.manuhome or not registration.manuhome.reg_owner_groups:
        return error_msg
    for deleted in json_data['deleteOwnerGroups']:
        if deleted.get('groupId'):
            group_id = deleted['groupId']
            found: bool = False
            for existing in registration.manuhome.reg_owner_groups:
                if existing.group_id == group_id:
                    found = True
                    tenancy_type = deleted.get('type')
                    if existing.status not in (Db2Owngroup.StatusTypes.ACTIVE, Db2Owngroup.StatusTypes.EXEMPT):
                        error_msg += DELETE_GROUP_ID_INVALID.format(group_id=group_id)
                    if tenancy_type and NEW_TENANCY_LEGACY.get(tenancy_type) and \
                            existing.tenancy_type != NEW_TENANCY_LEGACY.get(tenancy_type) and \
                            tenancy_type != MhrTenancyTypes.NA:
                        error_msg += DELETE_GROUP_TYPE_INVALID.format(group_id=group_id)
            if not found:
                error_msg += DELETE_GROUP_ID_NONEXISTENT.format(group_id=group_id)
    return error_msg


def delete_group(group_id: int, delete_groups):
    """Check if owner group is flagged for deletion."""
    if not delete_groups or group_id < 1:
        return False
    for group in delete_groups:
        if group.get('groupId', 0) == group_id:
            return True
    return False


def interest_required(groups, registration=None, delete_groups=None) -> bool:
    """Determine if group interest is required."""
    group_count: int = len(groups)  # Verify interest if multiple groups or existing interest.
    if group_count > 1:
        return True
    if registration and registration.manuhome and registration.manuhome.reg_owner_groups:
        for existing in registration.manuhome.reg_owner_groups:
            if existing.status == Db2Owngroup.StatusTypes.ACTIVE and \
                    existing.tenancy_type != Db2Owngroup.TenancyTypes.SOLE and \
                    not delete_group(existing.group_id, delete_groups) and \
                    existing.get_interest_fraction(False) > 0:
                group_count += 1
    return group_count > 1


def validate_group_interest(groups,  # pylint: disable=too-many-branches
                            denominator: int,
                            registration=None,
                            delete_groups=None) -> str:
    """Verify owner group interest values are valid."""
    error_msg = ''
    numerator_sum: int = 0
    group_count: int = len(groups)  # Verify interest if multiple groups or existing interest.
    if registration and registration.manuhome and registration.manuhome.reg_owner_groups:
        for existing in registration.manuhome.reg_owner_groups:
            if existing.status == Db2Owngroup.StatusTypes.ACTIVE and \
                    existing.tenancy_type != Db2Owngroup.TenancyTypes.SOLE and \
                    not delete_group(existing.group_id, delete_groups):
                den = existing.get_interest_fraction(False)
                if den > 0:
                    group_count += 1
                    if den == denominator:
                        numerator_sum += existing.interest_numerator
                    elif den < denominator:
                        numerator_sum += (denominator/den * existing.interest_numerator)
                    else:
                        numerator_sum += int((denominator * existing.interest_numerator)/den)
    current_app.logger.debug(f'group_count={group_count} denominator={denominator}')
    if group_count < 2:  # Could have transfer of joint tenants with no interest.
        return error_msg
    for group in groups:
        num = group.get('interestNumerator', 0)
        den = group.get('interestDenominator', 0)
        if num and den and num > 0 and den > 0:
            if den == denominator:
                numerator_sum += num
            else:
                numerator_sum += (denominator/den * num)
    if numerator_sum != denominator:
        error_msg = GROUP_INTEREST_MISMATCH
    return error_msg


def get_modified_group(registration, group_id: int) -> dict:
    """Find the existing owner group as JSON, matching on the group id."""
    group = {}
    if not registration or not registration.manuhome or not group_id:
        return group
    for existing in registration.manuhome.reg_owner_groups:
        if existing.group_id == group_id:
            group = existing.json
            break
    return group


def has_active_permit(registration) -> bool:
    """Verify an existing transport permit exists on the home."""
    if not registration or not registration.manuhome or not registration.manuhome.notes:
        return False
    for note in registration.manuhome.reg_notes:
        if note.document_type in (Db2Document.DocumentTypes.PERMIT, Db2Document.DocumentTypes.PERMIT_TRIM) and \
                note.status == Db2Mhomnote.StatusTypes.ACTIVE and note.expiry_date and \
                note.expiry_date >= model_utils.today_local().date():
            return True
    return False


def validate_no_active_permit(registration, reg_json: dict) -> str:
    """Verify no existing acive transport permit exists on the home."""
    error_msg = ''
    if reg_json and reg_json.get('moveCompleted'):  # Skip rule check for all users if true.
        return error_msg
    if not registration or not registration.manuhome or not registration.manuhome.notes:
        return error_msg
    for note in registration.manuhome.reg_notes:
        if note.document_type in (Db2Document.DocumentTypes.PERMIT, Db2Document.DocumentTypes.PERMIT_TRIM) and \
                note.status == Db2Mhomnote.StatusTypes.ACTIVE and note.expiry_date and \
                note.expiry_date >= model_utils.today_local().date():
            error_msg += STATE_ACTIVE_PERMIT
    return error_msg


def validate_owner_suffix(owner: dict) -> str:
    """Verify legacy suffix does not exceed maximum allowed length of 70 characters."""
    error_msg = ''
    if not owner.get('description') and not owner.get('suffix'):
        return error_msg
    if owner.get('organizationName') and (not owner.get('partyType') or
                                          owner.get('partyType') == MhrPartyTypes.OWNER_BUS):
        return error_msg
    suffix = owner.get('suffix', '')
    if owner.get('partyType', '') in (MhrPartyTypes.ADMINISTRATOR, MhrPartyTypes.EXECUTOR, MhrPartyTypes.TRUSTEE):
        suffix = owner.get('description', '')
    if len(suffix) > 70:
        return OWNER_SUFFIX_MAX_LENGTH
    # check combined length with extra names.
    if owner.get('individualName') and owner['individualName'].get('middle'):
        middle_names = str(owner['individualName'].get('middle')).split(' ', 1)
        if middle_names and len(middle_names) > 1:
            extra_names = middle_names[1].strip()
            test_suffix = extra_names + ', ' + suffix
            if len(test_suffix) > 70:
                error_msg += OWNER_SUFFIX_MAX_LENGTH
    return error_msg
