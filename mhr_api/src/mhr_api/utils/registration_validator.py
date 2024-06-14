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
"""This module holds registration validation for rules not covered by the schema.

Validation includes verifying the data combination for various registrations/filings and timestamps.
"""
from flask import current_app
from mhr_api.models import MhrRegistration
from mhr_api.models import registration_utils as reg_utils, utils as model_utils
from mhr_api.models.type_tables import (
    MhrDocumentTypes,
    MhrLocationTypes,
    MhrNoteStatusTypes,
    MhrPartyTypes,
    MhrRegistrationTypes,
    MhrTenancyTypes
)
from mhr_api.models.mhr_note import NonResidentialReasonTypes
from mhr_api.services.authz import MANUFACTURER_GROUP, QUALIFIED_USER_GROUP, DEALERSHIP_GROUP
from mhr_api.utils import validator_utils


OWNERS_NOT_ALLOWED = 'Owners not allowed with new registrations: use ownerGroups instead. '
OWNER_GROUPS_REQUIRED = 'At least one owner group is required for staff registrations. '
DECLARED_VALUE_REQUIRED = 'Declared value is required and must be greater than 0 for this registration. '
CONSIDERATION_REQUIRED = 'Consideration is required for this registration. '
TRANSFER_DATE_REQUIRED = 'Transfer date is required for this registration. '
VALIDATOR_ERROR = 'Error performing extra validation. '
NOTE_DOC_TYPE_INVALID = 'The note document type is invalid for the registration type. '
LOCATION_ADDRESS_MISMATCH = 'The existing location address must match the current location address. '
OWNER_NAME_MISMATCH = 'The existing owner name must match exactly a current owner name for this registration. '
MANUFACTURER_DEALER_INVALID = 'The existing location must be a dealer or manufacturer lot for this registration. '
MANUFACTURER_PERMIT_INVALID = 'A manufacturer can only submit a transport permit once for a home. '
PARTY_TYPE_INVALID = 'Death of owner requires an executor, trustee, administrator owner party type. '
GROUP_PARTY_TYPE_INVALID = 'For TRUSTEE, ADMINISTRATOR, or EXECUTOR, all owner party types within the group ' + \
                            'must be identical. '
OWNER_DESCRIPTION_REQUIRED = 'Owner description is required for the owner party type. '
TRANSFER_PARTY_TYPE_INVALID = 'Owner party type of administrator, executor, trustee not allowed for this registration. '
TENANCY_PARTY_TYPE_INVALID = 'Owner group tenancy type must be NA for executors, trustees, or administrators. '
TENANCY_TYPE_NA_INVALID = 'Tenancy type NA is not allowed when there is 1 active owner group with 1 owner. '
REG_STAFF_ONLY = 'Only BC Registries Staff are allowed to submit this registration. '
TRAN_DEATH_GROUP_COUNT = 'Only one owner group can be modified in a transfer due to death registration. '
TRAN_DEATH_JOINT_TYPE = 'The existing tenancy type must be joint for this transfer registration. '
TRAN_ADMIN_OWNER_INVALID = 'The existing owners must be administrators for this registration. '
TRAN_DEATH_OWNER_INVALID = 'The owners must be individuals or businesses for this registration. '
TRAN_EXEC_OWNER_INVALID = 'The owners must be individuals, businesses, or executors for this registration. '
TRAN_ADMIN_NEW_OWNER = 'The new owners must be administrators for this registration. '
TRAN_DEATH_NEW_OWNER = 'The new owners must be individuals or businesses for this registration. '
TRAN_AFFIDAVIT_NEW_OWNER = 'The new owners must be executors for this registration. '
TRAN_DEATH_ADD_OWNER = 'Owners cannot be added with this registration. '
TRAN_DEATH_CERT_MISSING = 'A death certificate number is required with this registration. '
TRAN_DEATH_CORP_NUM_MISSING = 'A removed business owner corporation number is required with this registration. '
TRAN_DEATH_DATE_MISSING = 'A death date and time is required with this registration. '
TRAN_DEATH_DATE_INVALID = 'A death date and time must be in the past. '
TRAN_DEATH_QS_JOINT = 'A lawyer/notary qualified supplier JOINT tenancy business owner is not allowed with this ' + \
    'registration. '
TRAN_AFFIDAVIT_DECLARED_VALUE = 'Declared value cannot be greater than 25000 for this registration. '
TRAN_WILL_PROBATE = 'One (and only one) deceased owner must have a probate document (no death certificate). '
TRAN_WILL_DEATH_CERT = 'Deceased owners without a probate document must have a death certificate ' + \
    'or corporation number. '
TRAN_WILL_NEW_OWNER = 'The new owners must be executors for this registration. '
TRAN_EXEC_DEATH_CERT = 'All deceased owners must have a death certificate or corporation number. '
TRAN_ADMIN_GRANT = 'One (and only one) deceased owner must have a grant document (no death certificate). '
TRAN_ADMIN_DEATH_CERT = 'Deceased owners without a grant document must have a death certificate or corporation number. '
TRAN_QUALIFIED_DELETE = 'Qualified suppliers must either delete one owner group or all owner groups. '
NOTICE_NAME_REQUIRED = 'The giving notice party person or business name is required. '
NOTICE_ADDRESS_REQUIRED = 'The giving notice address is required. '
DESTROYED_FUTURE = 'The exemption destroyed/converted date (expiryDateTime) cannot be in the future. '
DESTROYED_EXRS = 'The destroyed/converted date (note expiryDateTime) cannot be submitted with a residential exemption. '
LOCATION_NOT_ALLOWED = 'A Residential Exemption is not allowed when the home current location is a ' \
    'dealer/manufacturer lot or manufactured home park. '
TRANS_DOC_TYPE_INVALID = 'The transferDocumentType is only allowed with a TRANS transfer due to sale or gift. '
AMEND_LOCATION_TYPE_QS = 'New location type cannot be different than the existing location type.'
AMEND_PERMIT_INVALID = 'Amend transport permit not allowed: no active tansport permit exists. '
TRAN_DEATH_QS_JOINT_REMOVE = 'A lawyer/notary qualified supplier JOINT tenancy business owner cannot be changed ' + \
    'with this registration. '
PERMIT_QS_ADDRESS_MISSING = 'No existing qualified supplier lot address found. '
PERMIT_QS_INFO_MISSING = 'No existing qualified supplier service agreement information found. '
PERMIT_QS_ADDRESS_MISMATCH = 'The current transport permit home location address must match the ' + \
    'manufacturer/dealer lot address. '
PERMIT_MANUFACTURER_NAME_MISMATCH = 'The current location manufacturer name must match the service agreement name. '
EXNR_DATE_MISSING = 'Non-residential exemptions require a destroyed/converted date (note expiryDateTime). '
EXNR_REASON_MISSING = 'Non-residential exemptions require one of the defined reason types (note nonResidentialReason). '
EXNR_OTHER_MISSING = 'Non-residential exemptions require an other description (note nonResidentialOther) if the ' + \
    'reason type is OTHER. '
EXNR_OTHER_INVALID = 'Non-residential exemptions other description (note nonResidentialOther) is not allowed with ' + \
    'the request reason type. '
EXNR_DESTROYED_INVALID = 'Non-residential exemption destroyed reason (note nonResidentialReason) is invalid. ' + \
    'Allowed values are BURNT, DISMANTLED, DILAPIDATED, or OTHER. '
EXNR_CONVERTED_INVALID = 'Non-residential exemption converted reason (note nonResidentialReason) is invalid. ' + \
    'Allowed values are OFFICE, STORAGE_SHED, BUNKHOUSE, or OTHER. '
TRANS_DOC_TYPE_NOT_ALLOWED = 'The transferDocumentType is only allowed with BC Registries staff TRANS registrations. '
AMEND_PERMIT_QS_ADDRESS_INVALID = 'Amend transport permit can only change the home location address street. ' + \
    'City and province may not be modified. '
PERMIT_ACTIVE_ACCOUNT_INVALID = 'Create new transport permit request invalid: an active, non-expired transport ' + \
    'permit created by another account exists. '

PPR_SECURITY_AGREEMENT = ' SA TA TG TM '


def validate_registration(json_data, staff: bool = False):
    """Perform all registration data validation checks not covered by schema validation."""
    error_msg = ''
    try:
        if staff:
            error_msg += validator_utils.validate_doc_id(json_data, True)
            if not json_data.get('ownerGroups'):
                error_msg += OWNER_GROUPS_REQUIRED
        error_msg += validator_utils.validate_submitting_party(json_data)
        error_msg += validator_utils.validate_mhr_number(json_data.get('mhrNumber', ''), staff)
        owner_count: int = len(json_data.get('ownerGroups')) if json_data.get('ownerGroups') else 0
        error_msg += validator_utils.validate_owner_groups(json_data.get('ownerGroups'), True, None, None, owner_count)
        error_msg += validate_owner_party_type(json_data, json_data.get('ownerGroups'), True, owner_count)
        error_msg += validator_utils.validate_location(json_data.get('location'))
        error_msg += validator_utils.validate_description(json_data.get('description'), staff)
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_registration exception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


def validate_transfer(registration: MhrRegistration,  # pylint: disable=too-many-branches
                      json_data,
                      staff: bool,
                      group: str):
    """Perform all transfer data validation checks not covered by schema validation."""
    error_msg = ''
    try:
        current_app.logger.info(f'Validating transfer staff={staff}, group={group}')
        if not staff and reg_utils.is_transfer_due_to_death_staff(json_data.get('registrationType')):
            return REG_STAFF_ONLY
        if staff:
            error_msg += validator_utils.validate_doc_id(json_data, True)
        elif registration:
            error_msg += validator_utils.validate_ppr_lien(registration.mhr_number, MhrRegistrationTypes.TRANS, staff)
        active_group_count: int = validator_utils.get_active_group_count(json_data, registration)
        error_msg += validator_utils.validate_submitting_party(json_data)
        error_msg += validator_utils.validate_owner_groups(json_data.get('addOwnerGroups'),
                                                           False,
                                                           registration,
                                                           json_data.get('deleteOwnerGroups'),
                                                           active_group_count)
        error_msg += validate_owner_party_type(json_data, json_data.get('addOwnerGroups'), False, active_group_count)
        reg_type: str = json_data.get('registrationType', MhrRegistrationTypes.TRANS)
        error_msg += validator_utils.validate_registration_state(registration, staff, reg_type)
        error_msg += validator_utils.validate_draft_state(json_data)
        if registration and json_data.get('deleteOwnerGroups'):
            error_msg += validator_utils.validate_delete_owners(registration, json_data)
        if not staff:
            if not isinstance(json_data.get('declaredValue', 0), int) or not json_data.get('declaredValue') or \
                    json_data.get('declaredValue') < 0:
                error_msg += DECLARED_VALUE_REQUIRED
            if reg_type == MhrRegistrationTypes.TRANS and \
                    (not json_data.get('transferDocumentType') or
                     json_data.get('transferDocumentType') in (MhrDocumentTypes.TRANS_QUIT_CLAIM,
                                                               MhrDocumentTypes.TRANS_RECEIVERSHIP,
                                                               MhrDocumentTypes.TRANS_SEVER_GRANT)):
                if not json_data.get('consideration'):
                    error_msg += CONSIDERATION_REQUIRED
                if not json_data.get('transferDate'):
                    error_msg += TRANSFER_DATE_REQUIRED
            if json_data.get('deleteOwnerGroups') and len(json_data.get('deleteOwnerGroups')) != 1 and \
                    group == QUALIFIED_USER_GROUP and \
                    len(json_data.get('deleteOwnerGroups')) != validator_utils.get_existing_group_count(registration):
                error_msg += TRAN_QUALIFIED_DELETE
        if reg_type != MhrRegistrationTypes.TRANS and json_data.get('transferDocumentType'):
            error_msg += TRANS_DOC_TYPE_INVALID
        elif not staff and json_data.get('transferDocumentType'):
            error_msg += TRANS_DOC_TYPE_NOT_ALLOWED
        if reg_utils.is_transfer_due_to_death(json_data.get('registrationType')):
            error_msg += validate_transfer_death(registration, json_data, group, active_group_count)
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_transfer exception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


def validate_exemption(registration: MhrRegistration, json_data, staff: bool = False):
    """Perform all exemption data validation checks not covered by schema validation."""
    error_msg = ''
    try:
        current_app.logger.info(f'Validating exemption staff={staff}')
        if staff:
            error_msg += validator_utils.validate_doc_id(json_data)
        elif registration:
            error_msg += validator_utils.validate_ppr_lien(registration.mhr_number,
                                                           MhrRegistrationTypes.EXEMPTION_RES,
                                                           staff)
        error_msg += validator_utils.validate_submitting_party(json_data)
        reg_type: str = MhrRegistrationTypes.EXEMPTION_RES
        if json_data.get('nonResidential') or \
                (json_data.get('note') and json_data['note'].get('documentType') == MhrDocumentTypes.EXNR):
            reg_type = MhrRegistrationTypes.EXEMPTION_NON_RES
        error_msg += validator_utils.validate_registration_state(registration, staff, reg_type)
        error_msg += validator_utils.validate_draft_state(json_data)
        if reg_type == MhrRegistrationTypes.EXEMPTION_RES:
            location = validator_utils.get_existing_location(registration)
            if location and (location.get('parkName') or location.get('dealerName')):
                error_msg += LOCATION_NOT_ALLOWED
        error_msg += validate_exemption_note(json_data, reg_type)
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_exemption exception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


def validate_permit(registration: MhrRegistration,
                    json_data: dict,
                    account_id: str,
                    staff: bool = False,
                    group_name: str = None):
    """Perform all transport permit data validation checks not covered by schema validation."""
    error_msg = ''
    try:
        current_app.logger.info(f'Validating permit account={account_id} staff={staff}')
        if staff:
            error_msg += validator_utils.validate_doc_id(json_data, True)
        elif registration:
            error_msg += validator_utils.validate_ppr_lien(registration.mhr_number, MhrRegistrationTypes.PERMIT, staff)
        current_location = validator_utils.get_existing_location(registration)
        error_msg += validator_utils.validate_submitting_party(json_data)
        if json_data.get('amendment'):
            error_msg += validator_utils.validate_registration_state(registration, staff, MhrRegistrationTypes.PERMIT,
                                                                     MhrDocumentTypes.AMEND_PERMIT)
        else:
            error_msg += validator_utils.validate_registration_state(registration,
                                                                     staff,
                                                                     MhrRegistrationTypes.PERMIT,
                                                                     MhrDocumentTypes.REG_103,
                                                                     json_data)
            if not staff and json_data.get('moveCompleted'):
                error_msg += validate_active_permit(registration, account_id)
            if registration and group_name and group_name == MANUFACTURER_GROUP:
                error_msg += validate_manufacturer_permit(registration.mhr_number, json_data, current_location)
            if registration and group_name and group_name == DEALERSHIP_GROUP and current_location and \
                    current_location.get('locationType', '') != MhrLocationTypes.MANUFACTURER:
                error_msg += MANUFACTURER_DEALER_INVALID
        error_msg += validator_utils.validate_draft_state(json_data)
        error_msg += validate_permit_location(json_data, current_location, staff)
        error_msg += validate_amend_permit(registration, json_data)
        if group_name and group_name == DEALERSHIP_GROUP and not json_data.get('qsLocation'):
            error_msg += PERMIT_QS_INFO_MISSING
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_permit exception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


def validate_amend_permit(registration: MhrRegistration, json_data):
    """Perform all extra amend transport permit data validation checks."""
    error_msg = ''
    if not json_data.get('amendment'):
        return error_msg
    if not validator_utils.has_active_permit(registration):
        error_msg += AMEND_PERMIT_INVALID
    return error_msg


def validate_exemption_note(json_data: dict, reg_type: str) -> str:  # pylint: disable=too-many-branches
    """Perform all exemption note validation checks not covered by schema validation."""
    error_msg = ''
    if not json_data.get('note'):
        return error_msg
    note_json = json_data['note']
    if note_json.get('documentType') and \
            note_json.get('documentType') not in (MhrDocumentTypes.EXRS, MhrDocumentTypes.EXNR):
        error_msg += NOTE_DOC_TYPE_INVALID
    if note_json.get('givingNoticeParty'):
        notice = note_json.get('givingNoticeParty')
        if not notice.get('address'):
            error_msg += NOTICE_ADDRESS_REQUIRED
        if not notice.get('personName') and not notice.get('businessName'):
            error_msg += NOTICE_NAME_REQUIRED
    if reg_type == MhrRegistrationTypes.EXEMPTION_NON_RES:
        if not note_json.get('expiryDateTime'):
            error_msg += EXNR_DATE_MISSING
        else:
            expiry = note_json.get('expiryDateTime')
            expiry_ts = model_utils.ts_from_iso_format(expiry)
            now = model_utils.now_ts()
            if expiry_ts > now:
                error_msg += DESTROYED_FUTURE
        if not note_json.get('nonResidentialReason'):
            error_msg += EXNR_REASON_MISSING
        elif note_json.get('destroyed') and\
                note_json.get('nonResidentialReason') not in (NonResidentialReasonTypes.BURNT,
                                                              NonResidentialReasonTypes.DISMANTLED,
                                                              NonResidentialReasonTypes.DILAPIDATED,
                                                              NonResidentialReasonTypes.OTHER):
            error_msg += EXNR_DESTROYED_INVALID
        elif not note_json.get('destroyed') and\
                note_json.get('nonResidentialReason') not in (NonResidentialReasonTypes.OFFICE,
                                                              NonResidentialReasonTypes.STORAGE_SHED,
                                                              NonResidentialReasonTypes.BUNKHOUSE,
                                                              NonResidentialReasonTypes.OTHER):
            error_msg += EXNR_CONVERTED_INVALID
        elif note_json.get('nonResidentialReason', '') != NonResidentialReasonTypes.OTHER and \
                note_json.get('nonResidentialOther'):
            error_msg += EXNR_OTHER_INVALID
        elif note_json.get('nonResidentialReason', '') == NonResidentialReasonTypes.OTHER and \
                not note_json.get('nonResidentialOther'):
            error_msg += EXNR_OTHER_MISSING
    elif note_json.get('expiryDateTime'):
        error_msg += DESTROYED_EXRS
    return error_msg


def validate_permit_location(json_data: dict, current_location: dict, staff: bool):
    """Perform all transport permit location validation checks not covered by schema validation."""
    error_msg: str = ''
    if json_data.get('newLocation'):
        location = json_data.get('newLocation')
        error_msg += validator_utils.validate_location(location)
        error_msg += validator_utils.validate_location_different(current_location, location)
        # Skip tax cert info validation for amendments if not provided.
        if json_data.get('amendment') and json_data.get('taxCertificate'):
            error_msg += validator_utils.validate_tax_certificate(location, current_location, staff)
        elif not json_data.get('amendment'):
            error_msg += validator_utils.validate_tax_certificate(location, current_location, staff)
        if not json_data.get('amendment') and not json_data.get('landStatusConfirmation'):
            if location.get('locationType') and \
                    location['locationType'] in (MhrLocationTypes.STRATA,
                                                 MhrLocationTypes.RESERVE,
                                                 MhrLocationTypes.OTHER):
                error_msg += validator_utils.STATUS_CONFIRMATION_REQUIRED
            elif current_location and location.get('locationType', '') == MhrLocationTypes.MH_PARK:
                if current_location.get('locationType', '') != MhrLocationTypes.MH_PARK or \
                        current_location.get('parkName', '') != location.get('parkName'):
                    error_msg += validator_utils.STATUS_CONFIRMATION_REQUIRED
        if not staff and json_data.get('amendment'):
            error_msg += validate_amend_location_address(json_data, current_location)
        if location.get('pidNumber'):
            error_msg += validator_utils.validate_pid(location.get('pidNumber'))
    return error_msg


def validate_amend_location_address(json_data: dict, current_location: dict) -> str:
    """Check that amend transport permit only changes the location address street value."""
    error_msg: str = ''
    if not current_location or not current_location.get('address') or not json_data['newLocation'].get('address'):
        return error_msg
    addr_1 = json_data['newLocation'].get('address')
    addr_2 = current_location.get('address')
    if addr_1.get('city'):
        addr_1['city'] = str(addr_1.get('city')).upper().strip()
    if addr_1.get('city', '') != addr_2.get('city', '') or \
            addr_1.get('region', '') != addr_2.get('region', '') or \
            addr_1.get('country', '') != addr_2.get('country', ''):
        error_msg = AMEND_PERMIT_QS_ADDRESS_INVALID
    if addr_2.get('postalCode', '') != addr_1.get('postalCode', ''):
        error_msg = AMEND_PERMIT_QS_ADDRESS_INVALID
    return error_msg


def validate_permit_location_address(json_data: dict, current_location: dict) -> str:
    """Manufacturer check that current location address matches supplier lot address."""
    error_msg: str = ''
    if not current_location or not current_location.get('address'):
        return error_msg
    if not json_data.get('qsLocation') or not json_data['qsLocation'].get('address'):
        return PERMIT_QS_ADDRESS_MISSING
    addr_1 = json_data['qsLocation'].get('address')
    addr_2 = current_location.get('address')
    # current_app.logger.debug(addr_1)
    # current_app.logger.debug(addr_2)
    if addr_2.get('street'):
        addr_2['street'] = str(addr_2.get('street')).upper().strip()
    if addr_2.get('city'):
        addr_2['city'] = str(addr_2.get('city')).upper().strip()
    if addr_1.get('street', '') != addr_2.get('street', '') or \
            addr_1.get('city', '') != addr_2.get('city', '') or \
            addr_1.get('region', '') != addr_2.get('region', '') or \
            addr_1.get('country', '') != addr_2.get('country', ''):
        error_msg = PERMIT_QS_ADDRESS_MISMATCH
    del json_data['qsLocation']
    return error_msg


def existing_owner_added(new_owners, owner) -> bool:
    """Check if the existing owner name matches an owner name in the new group."""
    if owner and new_owners:
        for owner_json in new_owners:
            if owner_json.get('individualName') and owner.get('individualName') and \
                    owner_json['individualName'].get('last') == owner['individualName'].get('last') and \
                    owner_json['individualName'].get('first') == owner['individualName'].get('first'):
                if owner_json['individualName'].get('middle', '') == owner['individualName'].get('middle', ''):
                    return True
            elif owner_json.get('organizationName') and owner.get('organizationName') and \
                    owner_json.get('organizationName') == owner.get('organizationName'):
                return True
    return False


def validate_transfer_death_existing_owners(reg_type: str, modified_group: dict, group: str):
    """Apply existing owner validation rules specific to transfer due to death registration types."""
    error_msg: str = ''
    if not modified_group or not modified_group.get('owners'):
        return error_msg
    owners = modified_group.get('owners')
    for owner_json in owners:
        if reg_type == MhrRegistrationTypes.TRAND and \
                owner_json.get('partyType') not in (MhrPartyTypes.OWNER_BUS, MhrPartyTypes.OWNER_IND):
            error_msg += TRAN_DEATH_OWNER_INVALID
        if reg_type == MhrRegistrationTypes.TRAND and group and group == QUALIFIED_USER_GROUP and \
                owner_json.get('partyType') == MhrPartyTypes.OWNER_BUS:
            error_msg += TRAN_DEATH_QS_JOINT_REMOVE
    return error_msg


def new_owner_exists(modified_group, owner) -> bool:
    """Check if the new owner name matches an existing group owner name."""
    if owner and modified_group and modified_group.get('owners'):
        for owner_json in modified_group.get('owners'):
            if owner_json.get('individualName') and owner.get('individualName') and \
                    owner_json['individualName'].get('last') == owner['individualName'].get('last') and \
                    owner_json['individualName'].get('first') == owner['individualName'].get('first'):
                if owner_json['individualName'].get('middle', '') == owner['individualName'].get('middle', ''):
                    return True
            elif owner_json.get('organizationName') and owner.get('organizationName') and \
                    owner_json.get('organizationName') == owner.get('organizationName'):
                return True
    return False


def validate_transfer_death_new_owners(reg_type: str, new_owners, modified_group):
    """Apply new owner validation rules specific to transfer due to death registration types."""
    error_msg: str = ''
    if not new_owners:
        return error_msg
    exec_count: int = 0
    for owner in new_owners:
        party_type = owner.get('partyType')
        if reg_type == MhrRegistrationTypes.TRAND and party_type and \
                party_type not in (MhrPartyTypes.OWNER_BUS, MhrPartyTypes.OWNER_IND):
            error_msg += TRAN_DEATH_NEW_OWNER
        elif reg_type == MhrRegistrationTypes.TRANS_ADMIN and \
                (not party_type or party_type != MhrPartyTypes.ADMINISTRATOR):
            error_msg += TRAN_ADMIN_NEW_OWNER
        elif reg_type in (MhrRegistrationTypes.TRANS_WILL, MhrRegistrationTypes.TRANS_AFFIDAVIT) and \
                party_type and party_type == MhrPartyTypes.EXECUTOR:
            exec_count += 1
        if reg_type == MhrRegistrationTypes.TRAND and modified_group and not new_owner_exists(modified_group, owner):
            error_msg += TRAN_DEATH_ADD_OWNER
    if exec_count != len(new_owners) and reg_type == MhrRegistrationTypes.TRANS_AFFIDAVIT:
        error_msg += TRAN_AFFIDAVIT_NEW_OWNER
    elif exec_count != len(new_owners) and reg_type == MhrRegistrationTypes.TRANS_WILL:
        error_msg += TRAN_WILL_NEW_OWNER
    return error_msg


def validate_transfer_cert_corp(reg_type: str, owner_json: dict) -> str:
    """For one of the death transfer types verify deleted owner death cerificate/corp num and date."""
    error_msg: str = ''
    if reg_type in (MhrRegistrationTypes.TRAND, MhrRegistrationTypes.TRANS_AFFIDAVIT):
        if owner_json.get('organizationName') and not owner_json.get('deathCorpNumber'):
            error_msg += TRAN_DEATH_CORP_NUM_MISSING
        elif not owner_json.get('organizationName') and not owner_json.get('deathCertificateNumber'):
            error_msg += TRAN_DEATH_CERT_MISSING
        if not owner_json.get('deathDateTime'):
            error_msg += TRAN_DEATH_DATE_MISSING
        elif not model_utils.date_elapsed(owner_json.get('deathDateTime')):
            error_msg += TRAN_DEATH_DATE_INVALID
    else:
        if owner_json.get('organizationName') and not owner_json.get('deathCorpNumber') and \
                owner_json.get('deathDateTime'):
            error_msg += TRAN_DEATH_CORP_NUM_MISSING
        elif not owner_json.get('organizationName') and not owner_json.get('deathCertificateNumber') and \
                owner_json.get('deathDateTime'):
            error_msg += TRAN_DEATH_CERT_MISSING
        if not owner_json.get('deathDateTime') and (owner_json.get('deathCertificateNumber') or
                                                    owner_json.get('deathCorpNumber')):
            error_msg += TRAN_DEATH_DATE_MISSING
        if owner_json.get('deathDateTime') and not model_utils.date_elapsed(owner_json.get('deathDateTime')):
            error_msg += TRAN_DEATH_DATE_INVALID
    return error_msg


def is_delete_exec_admin(reg_type: str, owner_json: dict) -> bool:
    """Evaluate if a deleted owner is an executor or an administrator for one of the death transfers types."""
    if reg_type == MhrRegistrationTypes.TRANS_WILL and owner_json.get('partyType', '') == MhrPartyTypes.EXECUTOR:
        return True
    if reg_type == MhrRegistrationTypes.TRANS_ADMIN and owner_json.get('partyType', '') == MhrPartyTypes.ADMINISTRATOR:
        return True
    return False


def validate_transfer_death_owners(reg_type: str, new_owners, delete_owners):
    """Apply owner delete/add validation rules specific to transfer due to death registration types."""
    error_msg: str = ''
    probate_count: int = 0
    death_count: int = 0
    party_count: int = 0
    for owner_json in delete_owners:
        if not existing_owner_added(new_owners, owner_json) and reg_type == MhrRegistrationTypes.TRAND:
            error_msg += validate_transfer_cert_corp(reg_type, owner_json)
        elif reg_type in (MhrRegistrationTypes.TRANS_WILL, MhrRegistrationTypes.TRANS_AFFIDAVIT,
                          MhrRegistrationTypes.TRANS_ADMIN):
            if is_delete_exec_admin(reg_type, owner_json):
                party_count += 1
            elif not owner_json.get('deathCertificateNumber') and not owner_json.get('deathDateTime') and \
                    not owner_json.get('deathCorpNumber'):
                probate_count += 1
            elif (owner_json.get('deathCertificateNumber') or owner_json.get('deathCorpNumber')) and \
                    owner_json.get('deathDateTime'):
                death_count += 1
            error_msg += validate_transfer_cert_corp(reg_type, owner_json)
    if reg_type in (MhrRegistrationTypes.TRANS_WILL, MhrRegistrationTypes.TRANS_ADMIN) and party_count < 1:
        if probate_count != 1:
            error_msg += TRAN_WILL_PROBATE if reg_type == MhrRegistrationTypes.TRANS_WILL else TRAN_ADMIN_GRANT
        if (death_count + 1) != len(delete_owners) and reg_type == MhrRegistrationTypes.TRANS_WILL:
            error_msg += TRAN_WILL_DEATH_CERT
        elif (death_count + 1) != len(delete_owners):
            error_msg += TRAN_ADMIN_DEATH_CERT
    elif reg_type == MhrRegistrationTypes.TRANS_AFFIDAVIT and death_count != len(delete_owners):
        error_msg += TRAN_EXEC_DEATH_CERT
    return error_msg


def validate_transfer_death(registration: MhrRegistration, json_data, group: str, active_group_count: int):
    """Apply validation rules specific to transfer due to death registration types."""
    error_msg: str = ''
    if not json_data.get('deleteOwnerGroups') or not json_data.get('addOwnerGroups'):
        return error_msg
    reg_type: str = json_data.get('registrationType')
    tenancy_type: str = None
    modified_group: dict = None
    if json_data.get('deleteOwnerGroups'):
        modified_group = validator_utils.get_modified_group(registration,
                                                            json_data['deleteOwnerGroups'][0].get('groupId', 0))
    if len(json_data.get('deleteOwnerGroups')) != 1 or len(json_data.get('addOwnerGroups')) != 1:
        error_msg += TRAN_DEATH_GROUP_COUNT
    if json_data['deleteOwnerGroups'][0].get('type'):
        tenancy_type = json_data['deleteOwnerGroups'][0].get('type')
        if reg_type == MhrRegistrationTypes.TRAND and tenancy_type != MhrTenancyTypes.JOINT:
            error_msg += TRAN_DEATH_JOINT_TYPE
    new_owners = json_data['addOwnerGroups'][0].get('owners')
    # check existing owners.
    error_msg += validate_transfer_death_existing_owners(reg_type, modified_group, group)
    # check new owners.
    error_msg += validate_transfer_death_new_owners(reg_type, new_owners, modified_group)
    delete_owners = json_data['deleteOwnerGroups'][0].get('owners')
    if new_owners and delete_owners:
        error_msg += validate_transfer_death_owners(reg_type, new_owners, delete_owners)
    if reg_type == MhrRegistrationTypes.TRANS_AFFIDAVIT and json_data.get('declaredValue') and \
            json_data.get('declaredValue') > 25000:
        error_msg += TRAN_AFFIDAVIT_DECLARED_VALUE
    if reg_type == MhrRegistrationTypes.TRAND and active_group_count == 1 and group == QUALIFIED_USER_GROUP and \
            len(new_owners) > 1:
        for new_owner in new_owners:
            if new_owner.get('organizationName'):
                error_msg += TRAN_DEATH_QS_JOINT
                break
    return error_msg


def delete_group(group_id: int, delete_groups):
    """Check if owner group is flagged for deletion."""
    if not delete_groups or group_id < 1:
        return False
    for group in delete_groups:
        if group.get('groupId', 0) == group_id:
            return True
    return False


def validate_manufacturer_permit(mhr_number: str, json_data: dict, current_location: dict) -> str:
    """Validate transport permit business rules specific to manufacturers."""
    error_msg = ''
    # Must be located on a dealer's/manufacturer's lot.
    if current_location and not current_location.get('dealerName'):
        error_msg += MANUFACTURER_DEALER_INVALID
    elif current_location:
        # Verify current location manufacturer name matches manufacturer service agreement name
        current_app.logger.debug(json_data.get('qsLocation'))
        current_app.logger.debug(current_location)
        if json_data.get('qsLocation') and \
                current_location.get('dealerName') != json_data['qsLocation'].get('dealerName'):
            error_msg += PERMIT_MANUFACTURER_NAME_MISMATCH
        # Verify current location address matches manufacturer service agreement location address
        error_msg += validate_permit_location_address(json_data, current_location)
    current_app.logger.debug(f'Validating manufacturer transport permit for mhr# {mhr_number}')
    # CHECK REMOVED for now: Permit can only be issued once per home by a manufacturer.
    # if mhr_number and json_data.get('submittingParty'):
    #    party = json_data.get('submittingParty')
    #    name: str = party.get('businessName')
    #    if not name and party.get('personName') and party['personName'].get('first') and \
    #            party['personName'].get('last'):
    #        name = party['personName'].get('first').strip().upper() + ' '
    #        if party['personName'].get('middle'):
    #            name += party['personName'].get('middle').strip().upper() + ' '
    #        name += party['personName'].get('last').strip().upper()
    #    if name:
    #        permit_count: int = validator_utils.get_permit_count(mhr_number, name)
    #        if permit_count > 0:
    #            error_msg += MANUFACTURER_PERMIT_INVALID
    return error_msg


def location_address_match(current_location, request_location):
    """Verify the request and current location addresses match."""
    address_1 = current_location.get('address')
    address_2 = request_location.get('address')
    if address_1 and address_2:
        city = address_2.get('city').strip().upper() if address_2.get('city') else ''
        street = address_2.get('street').strip().upper() if address_2.get('street') else ''
        region = address_2.get('region').strip().upper() if address_2.get('region') else ''
        p_code = address_2.get('postalCode').strip().upper() if address_2.get('postalCode') else ''
        if p_code and address_1.get('postalCode'):
            return p_code == address_1.get('postalCode') and city == address_1.get('city') and \
                   street == address_1.get('street') and region == address_1.get('region')
        return city == address_1.get('city') and street == address_1.get('street') and region == address_1.get('region')
    return False


def validate_owner_party_type(json_data,  # pylint: disable=too-many-branches
                              groups, new: bool,
                              active_group_count: int):
    """Verify owner groups are valid."""
    error_msg = ''
    owner_death: bool = reg_utils.is_transfer_due_to_death_staff(json_data.get('registrationType'))
    if not groups:
        return error_msg
    for group in groups:
        if not new and len(groups) > 1 and group_owners_unchanged(json_data, group):
            continue
        party_count: int = 0
        owner_count: int = 0
        group_parties_invalid: bool = False
        first_party_type: str = None
        if group.get('owners'):
            owner_count = len(group.get('owners'))
            for owner in group['owners']:
                party_type = owner.get('partyType', None)
                if party_type and party_type in (MhrPartyTypes.ADMINISTRATOR, MhrPartyTypes.EXECUTOR,
                                                 MhrPartyTypes.TRUSTEE):
                    party_count += 1
                    if not first_party_type:
                        first_party_type = party_type
                    if first_party_type and party_type != first_party_type:
                        group_parties_invalid = True
                if party_type and not owner.get('description') and \
                        party_type in (MhrPartyTypes.ADMINISTRATOR, MhrPartyTypes.EXECUTOR,
                                       MhrPartyTypes.TRUST, MhrPartyTypes.TRUSTEE):
                    error_msg += OWNER_DESCRIPTION_REQUIRED
                if not new and not owner_death and not json_data.get('transferDocumentType') and party_type and \
                        party_type in (MhrPartyTypes.ADMINISTRATOR, MhrPartyTypes.EXECUTOR,
                                       MhrPartyTypes.TRUST, MhrPartyTypes.TRUSTEE):
                    error_msg += TRANSFER_PARTY_TYPE_INVALID
        if active_group_count < 2 and group.get('type', '') == MhrTenancyTypes.NA and owner_count == 1:
            error_msg += TENANCY_TYPE_NA_INVALID  # SOLE owner cannot be NA
        elif active_group_count > 1 and party_count > 0 and group.get('type', '') != MhrTenancyTypes.NA:
            error_msg += TENANCY_PARTY_TYPE_INVALID  # COMMON scenario
        elif active_group_count == 1 and owner_count > 1 and party_count > 0 and \
                group.get('type', '') != MhrTenancyTypes.NA:
            error_msg += TENANCY_PARTY_TYPE_INVALID  # JOINT scenario
        if new and group_parties_invalid:
            error_msg += GROUP_PARTY_TYPE_INVALID
    return error_msg


def group_owners_unchanged(json_data, add_group) -> bool:
    """Check if the owners in an added group are identical to the owners in a deleted group."""
    if not json_data.get('deleteOwnerGroups') or not add_group.get('owners'):
        return False
    for group in json_data.get('deleteOwnerGroups'):
        if group.get('owners') and len(group['owners']) == len(add_group['owners']):
            identical: bool = True
            for add_owner in add_group.get('owners'):
                owner_match: bool = False
                for del_owner in group.get('owners'):
                    if owner_name_address_match(add_owner, del_owner):
                        owner_match = True
                if not owner_match:
                    identical = False
            if identical:
                return True
    return False


def owner_name_address_match(owner1, owner2) -> bool:
    """Check if 2 owner json name and addresses are identical."""
    address_match: bool = False
    name_match: bool = False
    if owner1.get('address') and owner2.get('address') and owner1.get('address') == owner2.get('address'):
        address_match = True
    if owner1.get('organizationName') and owner2.get('organizationName') and \
            owner1.get('organizationName') == owner2.get('organizationName'):
        name_match = True
    elif owner1.get('individualName') and owner2.get('individualName') and \
            owner1.get('individualName') == owner2.get('individualName'):
        name_match = True
    return address_match and name_match


def validate_active_permit(registration: MhrRegistration, account_id: str) -> str:
    """Non-staff verify an active transport permit was created by the same account."""
    error_msg = ''
    if not registration or not account_id or not registration.change_registrations:
        return error_msg
    permit_account_id: str = ''
    active_permit: bool = False
    for reg in registration.change_registrations:
        if reg.notes and reg.notes[0] and reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE and \
                reg.notes[0].document_type == MhrDocumentTypes.REG_103 and \
                not reg.notes[0].is_expired():
            permit_account_id = reg.account_id
    # If no active permit check legacy: prevent registration if legacy account created an active permit.
    if not permit_account_id and model_utils.is_legacy():
        active_permit = validator_utils.has_active_permit(registration)
    if active_permit or (permit_account_id and account_id != permit_account_id):
        error_msg += PERMIT_ACTIVE_ACCOUNT_INVALID
    return error_msg
