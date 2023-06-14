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

from mhr_api.models import MhrRegistration, Db2Owngroup, Db2Owner
from mhr_api.models import registration_utils as reg_utils, utils as model_utils
from mhr_api.models.type_tables import MhrDocumentTypes, MhrLocationTypes
from mhr_api.models.type_tables import MhrOwnerStatusTypes, MhrTenancyTypes, MhrPartyTypes, MhrRegistrationTypes
from mhr_api.models.db2.owngroup import NEW_TENANCY_LEGACY
from mhr_api.models.utils import is_legacy, to_db2_ind_name, now_ts, ts_from_iso_format, valid_tax_cert_date
from mhr_api.services.authz import MANUFACTURER_GROUP, QUALIFIED_USER_GROUP
from mhr_api.utils import validator_utils


OWNERS_NOT_ALLOWED = 'Owners not allowed with new registrations: use ownerGroups instead. '
OWNER_GROUPS_REQUIRED = 'At least one owner group is required for staff registrations. '
DELETE_GROUP_ID_INVALID = 'The owner group with ID {group_id} is not active and cannot be changed. '
DELETE_GROUP_ID_NONEXISTENT = 'No owner group with ID {group_id} exists. '
DELETE_GROUP_TYPE_INVALID = 'The owner group tenancy type with ID {group_id} is invalid. '
DECLARED_VALUE_REQUIRED = 'Declared value is required and must be greater than 0 for this registration. '
CONSIDERATION_REQUIRED = 'Consideration is required for this registration. '
TRANSFER_DATE_REQUIRED = 'Transfer date is required for this registration. '
ADD_SOLE_OWNER_INVALID = 'Only one sole owner and only one sole owner group can be added. '
GROUP_COMMON_INVALID = 'More than 1 group is required with the Tenants in Common owner group type. '
GROUP_NUMERATOR_MISSING = 'The owner group interest numerator is required and must be an integer greater than 0. '
GROUP_DENOMINATOR_MISSING = 'The owner group interest denominator is required and must be an integer greater than 0. '
GROUP_INTEREST_MISMATCH = 'The owner group interest numerator sum does not equal the interest common denominator. '
VALIDATOR_ERROR = 'Error performing extra validation. '
NOTE_DOC_TYPE_INVALID = 'The note document type is invalid for the registration type. '
BAND_NAME_REQUIRED = 'The location Indian Reserve band name is required for this registration. '
RESERVE_NUMBER_REQUIRED = 'The location Indian Reserve number is required for this registration. '
OWNERS_JOINT_INVALID = 'The owner group must contain at least 2 owners. '
OWNERS_COMMON_INVALID = 'Each COMMON owner group must contain exactly 1 owner. '
OWNERS_COMMON_SOLE_INVALID = 'SOLE owner group tenancy type is not allowed when there is more than 1 ' \
    'owner group. Use COMMON instead. '
LOCATION_DEALER_REQUIRED = 'Location dealer/manufacturer name is required for this registration. '
STATUS_CONFIRMATION_REQUIRED = 'The land status confirmation is required for this registration. '
LOCATION_PARK_NAME_REQUIRED = 'Location park name is required for this registration. '
LOCATION_PARK_PAD_REQUIRED = 'Location park PAD is required for this registration. '
LOCATION_STRATA_REQUIRED = 'Location parcel ID or all of lot, plan, land district are required for this registration. '
LOCATION_OTHER_REQUIRED = 'Location parcel ID or all of lot, plan, land district or all of land district, district ' \
    'lot are required for this registration. '
LOCATION_ADDRESS_MISMATCH = 'The existing location address must match the current location address. '
OWNER_NAME_MISMATCH = 'The existing owner name must match exactly a current owner name for this registration. '
MANUFACTURER_DEALER_INVALID = 'The existing location must be a dealer or manufacturer lot for this registration. '
MANUFACTURER_PERMIT_INVALID = 'A manufacturer can only submit a transport permit once for a home. '
LOCATION_TAX_DATE_INVALID = 'Location tax certificate date is invalid. '
LOCATION_TAX_CERT_REQUIRED = 'Location tax certificate and tax certificate expiry date is required. '
PARTY_TYPE_INVALID = 'Death of owner requires an executor, trustee, administrator owner party type. '
GROUP_PARTY_TYPE_INVALID = 'For TRUSTEE, ADMINISTRATOR, or EXECUTOR, all owner party types within the group ' + \
                            'must be identical. '
OWNER_DESCRIPTION_REQUIRED = 'Owner description is required for the owner party type. '
TRANSFER_PARTY_TYPE_INVALID = 'Owner party type of administrator, executor, trustee not allowed for this registration. '
TENANCY_PARTY_TYPE_INVALID = 'Owner group tenancy type must be NA for executors, trustees, or administrators. '
TENANCY_TYPE_NA_INVALID = 'Tenancy type NA is not allowed when there is 1 active owner group with 1 owner. '
TENANCY_TYPE_NA_INVALID2 = 'Tenancy type NA is only allowed when all owners are ADMINISTRATOR, EXECUTOR, ' \
    'or TRUSTEE party types. '
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
TRAN_DEATH_DATE_MISSING = 'A death date and time is required with this registration. '
TRAN_DEATH_DATE_INVALID = 'A death date and time must be in the past. '
TRAN_AFFIDAVIT_DECLARED_VALUE = 'Declared value must be cannot be greater than 25000 for this registration. '
TRAN_WILL_PROBATE = 'One (and only one) deceased owner must have a probate document (no death certificate). '
TRAN_WILL_DEATH_CERT = 'Deceased owners without a probate document must have a death certificate. '
TRAN_WILL_NEW_OWNER = 'The new owners must be executors for this registration. '
TRAN_EXEC_DEATH_CERT = 'All deceased owners must have a death certificate. '
TRAN_ADMIN_GRANT = 'One (and only one) deceased owner must have a grant document (no death certificate). '
TRAN_ADMIN_DEATH_CERT = 'Deceased owners without a grant document must have a death certificate. '
LOCATION_MANUFACTURER_ALLOWED = 'Park name, PAD, band name, reserve number, parcel ID, and LTSA details are ' \
    'not allowed with a MANUFACTURER location type. '
LOCATION_PARK_ALLOWED = 'Dealer/manufacturer name, band name, reserve number, parcel ID, and LTSA details are ' \
    'not allowed with a MH_PARK location type. '
LOCATION_RESERVE_ALLOWED = 'Dealer/manufacturer name, park name, and PAD are not allowed with a RESERVE location type. '
LOCATION_STRATA_ALLOWED = 'Dealer/manufacturer name, park name, PAD, band name, and reserve number are not allowed ' \
    'with a STRATA location type. '
LOCATION_OTHER_ALLOWED = 'Dealer/manufacturer name, park name, PAD, band name, and reserve number are not allowed ' \
    'with an OTHER location type. '
TRAN_QUALIFIED_DELETE = 'Qualified suppliers mut either delete one owner group or all owner groups. '
NOTICE_NAME_REQUIRED = 'The giving notice party person or business name is required. '
NOTICE_ADDRESS_REQUIRED = 'The giving notice address is required. '
DESTROYED_FUTURE = 'The destroyed date and time cannot be in the future. '


def validate_registration(json_data, staff: bool = False):
    """Perform all registration data validation checks not covered by schema validation."""
    error_msg = ''
    try:
        if staff:
            error_msg += validator_utils.validate_doc_id(json_data)
            if not json_data.get('ownerGroups'):
                error_msg += OWNER_GROUPS_REQUIRED
        error_msg += validator_utils.validate_submitting_party(json_data)
        owner_count: int = len(json_data.get('ownerGroups')) if json_data.get('ownerGroups') else 0
        error_msg += validate_owner_groups(json_data.get('ownerGroups'), True, None, None, owner_count)
        error_msg += validate_owner_party_type(json_data, json_data.get('ownerGroups'), True, owner_count)
        error_msg += validate_location(json_data.get('location'))
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_registration exception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


def validate_transfer(registration: MhrRegistration, json_data, staff: bool, group: str):
    """Perform all transfer data validation checks not covered by schema validation."""
    error_msg = ''
    try:
        current_app.logger.info(f'Validating transfer staff={staff}, group={group}')
        if not staff and reg_utils.is_transfer_due_to_death_staff(json_data.get('registrationType')):
            return REG_STAFF_ONLY
        if registration:
            error_msg += validator_utils.validate_ppr_lien(registration.mhr_number)
        active_group_count: int = get_active_group_count(json_data, registration)
        error_msg += validator_utils.validate_submitting_party(json_data)
        error_msg += validate_owner_groups(json_data.get('addOwnerGroups'),
                                           False,
                                           registration,
                                           json_data.get('deleteOwnerGroups'),
                                           active_group_count)
        error_msg += validate_owner_party_type(json_data, json_data.get('addOwnerGroups'), False, active_group_count)
        reg_type: str = json_data.get('registrationType', MhrRegistrationTypes.TRANS)
        error_msg += validator_utils.validate_registration_state(registration, staff, reg_type)
        error_msg += validator_utils.validate_draft_state(json_data)
        if is_legacy() and registration and registration.manuhome and json_data.get('deleteOwnerGroups'):
            error_msg += validate_delete_owners_legacy(registration, json_data)
        if not staff:
            if not isinstance(json_data.get('declaredValue', 0), int) or not json_data.get('declaredValue') or \
                    json_data.get('declaredValue') < 0:
                error_msg += DECLARED_VALUE_REQUIRED
            if not json_data.get('consideration'):
                error_msg += CONSIDERATION_REQUIRED
            if not json_data.get('transferDate'):
                error_msg += TRANSFER_DATE_REQUIRED
            if json_data.get('deleteOwnerGroups') and len(json_data.get('deleteOwnerGroups')) != 1 and \
                    group == QUALIFIED_USER_GROUP and \
                    len(json_data.get('deleteOwnerGroups')) != validator_utils.get_existing_group_count(registration):
                error_msg += TRAN_QUALIFIED_DELETE
        if reg_utils.is_transfer_due_to_death(json_data.get('registrationType')):
            error_msg += validate_transfer_death(registration, json_data)
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
        if registration:
            error_msg += validator_utils.validate_ppr_lien(registration.mhr_number)
        error_msg += validator_utils.validate_submitting_party(json_data)
        error_msg += validator_utils.validate_registration_state(registration, staff,
                                                                 MhrRegistrationTypes.EXEMPTION_RES)
        error_msg += validator_utils.validate_draft_state(json_data)
        if json_data.get('note'):
            if json_data['note'].get('documentType') and \
                    json_data['note'].get('documentType') not in (MhrDocumentTypes.EXRS, MhrDocumentTypes.EXNR):
                error_msg += NOTE_DOC_TYPE_INVALID
            if json_data['note'].get('givingNoticeParty'):
                notice = json_data['note'].get('givingNoticeParty')
                if not notice.get('address'):
                    error_msg += NOTICE_ADDRESS_REQUIRED
                if not notice.get('personName') and not notice.get('businessName'):
                    error_msg += NOTICE_NAME_REQUIRED
            if json_data['note'].get('effectiveDateTime'):
                effective = json_data['note'].get('effectiveDateTime')
                effective_ts = model_utils.ts_from_iso_format(effective)
                now = model_utils.now_ts()
                if effective_ts > now:
                    error_msg += DESTROYED_FUTURE
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_exemption exception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


def validate_permit(registration: MhrRegistration, json_data, staff: bool = False, group_name: str = None):
    """Perform all transport permit data validation checks not covered by schema validation."""
    error_msg = ''
    try:
        current_app.logger.info(f'Validating permit staff={staff}')
        current_location = validator_utils.get_existing_location(registration)
        if registration and group_name and group_name == MANUFACTURER_GROUP:
            error_msg += validate_manufacturer_permit(registration.mhr_number, json_data.get('submittingParty'),
                                                      current_location)
        if registration:
            error_msg += validator_utils.validate_ppr_lien(registration.mhr_number)
        error_msg += validator_utils.validate_submitting_party(json_data)
        error_msg += validator_utils.validate_registration_state(registration, staff, MhrRegistrationTypes.PERMIT)
        error_msg += validator_utils.validate_draft_state(json_data)
        if json_data.get('newLocation'):
            location = json_data.get('newLocation')
            error_msg += validate_location(location)
            error_msg += validate_tax_certificate(location, current_location)
            if not json_data.get('landStatusConfirmation'):
                if location.get('locationType') and \
                        location['locationType'] in (MhrLocationTypes.STRATA,
                                                     MhrLocationTypes.RESERVE,
                                                     MhrLocationTypes.OTHER):
                    error_msg += STATUS_CONFIRMATION_REQUIRED
                elif location.get('locationType') and location['locationType'] == MhrLocationTypes.MH_PARK and \
                        current_location and location.get('parkName'):
                    existing_name: str = current_location.get('parkName')
                    if not existing_name or location.get('parkName').strip().upper() != existing_name:
                        error_msg += STATUS_CONFIRMATION_REQUIRED
            if location.get('pidNumber'):
                error_msg += validator_utils.validate_pid(location.get('pidNumber'))
        if current_location and json_data.get('existingLocation') and \
                not location_address_match(current_location, json_data.get('existingLocation')):
            error_msg += LOCATION_ADDRESS_MISMATCH
        if registration and json_data.get('owner') and not owner_name_match(registration, json_data.get('owner')):
            error_msg += OWNER_NAME_MISMATCH
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_transfer exception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


def validate_delete_owners_legacy(registration: MhrRegistration, json_data):
    """Check groups id's and owners are valid for deleted groups."""
    error_msg = ''
    for deleted in json_data['deleteOwnerGroups']:
        if deleted.get('groupId'):
            group_id = deleted['groupId']
            found: bool = False
            for existing in registration.manuhome.reg_owner_groups:
                if existing.group_id == group_id:
                    found = True
                    tenancy_type = deleted.get('type')
                    if existing.status != Db2Owngroup.StatusTypes.ACTIVE:
                        error_msg += DELETE_GROUP_ID_INVALID.format(group_id=group_id)
                    if tenancy_type and NEW_TENANCY_LEGACY.get(tenancy_type) and \
                            existing.tenancy_type != NEW_TENANCY_LEGACY.get(tenancy_type) and \
                            tenancy_type != MhrTenancyTypes.NA:
                        error_msg += DELETE_GROUP_TYPE_INVALID.format(group_id=group_id)
            if not found:
                error_msg += DELETE_GROUP_ID_NONEXISTENT.format(group_id=group_id)
    return error_msg


def get_modified_group(registration: MhrRegistration, group_id: int):
    """Find the existing owner group matching the group id."""
    group = {}
    if not registration:
        return group
    if is_legacy() and registration.manuhome:
        for existing in registration.manuhome.reg_owner_groups:
            if existing.group_id == group_id:
                group = existing.json
                break
    return group


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


def validate_transfer_death_existing_owners(reg_type: str, modified_group):
    """Apply existing owner validation rules specific to transfer due to death registration types."""
    error_msg: str = ''
    if not modified_group or not modified_group.get('owners'):
        return error_msg
    owners = modified_group.get('owners')
    for owner_json in owners:
        if reg_type == MhrRegistrationTypes.TRAND and \
                owner_json.get('partyType') not in (MhrPartyTypes.OWNER_BUS, MhrPartyTypes.OWNER_IND):
            error_msg += TRAN_DEATH_OWNER_INVALID
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


def validate_transfer_death_owners(reg_type: str, new_owners, delete_owners):  # pylint: disable=too-many-branches
    """Apply owner delete/add validation rules specific to transfer due to death registration types."""
    error_msg: str = ''
    probate_count: int = 0
    death_count: int = 0
    party_count: int = 0
    for owner_json in delete_owners:
        if not existing_owner_added(new_owners, owner_json) and reg_type == MhrRegistrationTypes.TRAND:
            if not owner_json.get('deathCertificateNumber'):
                error_msg += TRAN_DEATH_CERT_MISSING
            if not owner_json.get('deathDateTime'):
                error_msg += TRAN_DEATH_DATE_MISSING
            elif not model_utils.date_elapsed(owner_json.get('deathDateTime')):
                error_msg += TRAN_DEATH_DATE_INVALID
        elif reg_type in (MhrRegistrationTypes.TRANS_WILL, MhrRegistrationTypes.TRANS_AFFIDAVIT,
                          MhrRegistrationTypes.TRANS_ADMIN):
            if reg_type == MhrRegistrationTypes.TRANS_WILL and \
                    owner_json.get('partyType', '') == MhrPartyTypes.EXECUTOR:
                party_count += 1
            elif reg_type == MhrRegistrationTypes.TRANS_ADMIN and \
                    owner_json.get('partyType', '') == MhrPartyTypes.ADMINISTRATOR:
                party_count += 1
            elif not owner_json.get('deathCertificateNumber') and not owner_json.get('deathDateTime'):
                probate_count += 1
            elif owner_json.get('deathCertificateNumber') and owner_json.get('deathDateTime'):
                death_count += 1
                if not model_utils.date_elapsed(owner_json.get('deathDateTime')):
                    error_msg += TRAN_DEATH_DATE_INVALID
            if not owner_json.get('deathCertificateNumber') and owner_json.get('deathDateTime'):
                error_msg += TRAN_DEATH_CERT_MISSING
            if not owner_json.get('deathDateTime') and owner_json.get('deathCertificateNumber'):
                error_msg += TRAN_DEATH_DATE_MISSING
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


def validate_transfer_death(registration: MhrRegistration, json_data):
    """Apply validation rules specific to transfer due to death registration types."""
    error_msg: str = ''
    if not json_data.get('deleteOwnerGroups') or not json_data.get('addOwnerGroups'):
        return error_msg
    reg_type: str = json_data.get('registrationType')
    tenancy_type: str = None
    modified_group = get_modified_group(registration, json_data['deleteOwnerGroups'][0].get('groupId', 0))
    if len(json_data.get('deleteOwnerGroups')) != 1 or len(json_data.get('addOwnerGroups')) != 1:
        error_msg += TRAN_DEATH_GROUP_COUNT
    if json_data['deleteOwnerGroups'][0].get('type'):
        tenancy_type = json_data['deleteOwnerGroups'][0].get('type')
        if reg_type == MhrRegistrationTypes.TRAND and tenancy_type != MhrTenancyTypes.JOINT:
            error_msg += TRAN_DEATH_JOINT_TYPE
    new_owners = json_data['addOwnerGroups'][0].get('owners')
    # check existing owners.
    error_msg += validate_transfer_death_existing_owners(reg_type, modified_group)
    # check new owners.
    error_msg += validate_transfer_death_new_owners(reg_type, new_owners, modified_group)
    delete_owners = json_data['deleteOwnerGroups'][0].get('owners')
    if new_owners and delete_owners:
        error_msg += validate_transfer_death_owners(reg_type, new_owners, delete_owners)
    if reg_type == MhrRegistrationTypes.TRANS_AFFIDAVIT and json_data.get('declaredValue') and \
            json_data.get('declaredValue') > 25000:
        error_msg += TRAN_AFFIDAVIT_DECLARED_VALUE
    return error_msg


def validate_owner(owner):
    """Verify owner names are valid."""
    error_msg = ''
    if not owner:
        return error_msg
    desc: str = 'owner'
    if owner.get('organizationName'):
        error_msg += validator_utils.validate_text(owner.get('organizationName'), desc + ' organization name')
    elif owner.get('individualName'):
        error_msg += validator_utils.validate_individual_name(owner.get('individualName'), desc)
    return error_msg


def validate_owner_group(group, int_required: bool = False):
    """Verify owner group is valid."""
    error_msg = ''
    if not group:
        return error_msg
    orig_type: str = group.get('type', '')
    tenancy_type: str = NEW_TENANCY_LEGACY.get(orig_type, '')
    if tenancy_type == (Db2Owngroup.TenancyTypes.COMMON and orig_type != MhrTenancyTypes.NA) or int_required:
        if not group.get('interestNumerator') or group.get('interestNumerator', 0) < 1:
            error_msg += GROUP_NUMERATOR_MISSING
        if not group.get('interestDenominator') or group.get('interestDenominator', 0) < 1:
            error_msg += GROUP_DENOMINATOR_MISSING
    if orig_type == MhrTenancyTypes.NA and group.get('owners') and len(group.get('owners')) > 1:
        owner_count: int = 0
        for owner in group.get('owners'):
            if not owner.get('partyType') or \
                    owner.get('partyType') in (MhrPartyTypes.OWNER_BUS, MhrPartyTypes.OWNER_IND):
                owner_count += 1
        if owner_count != 0:
            error_msg += TENANCY_TYPE_NA_INVALID2
    if tenancy_type == Db2Owngroup.TenancyTypes.JOINT and (not group.get('owners') or len(group.get('owners')) < 2):
        error_msg += OWNERS_JOINT_INVALID
    elif orig_type != 'NA' and tenancy_type == Db2Owngroup.TenancyTypes.COMMON and \
            (not group.get('owners') or len(group.get('owners')) > 1):
        error_msg += OWNERS_COMMON_INVALID
    elif orig_type == MhrTenancyTypes.SOLE and int_required:
        error_msg += OWNERS_COMMON_SOLE_INVALID
    return error_msg


def delete_group(group_id: int, delete_groups):
    """Check if owner group is flagged for deletion."""
    if not delete_groups or group_id < 1:
        return False
    for group in delete_groups:
        if group.get('groupId', 0) == group_id:
            return True
    return False


def validate_group_interest(groups,  # pylint: disable=too-many-branches
                            denominator: int,
                            registration: MhrRegistration = None,
                            delete_groups=None):
    """Verify owner group interest values are valid."""
    error_msg = ''
    numerator_sum: int = 0
    group_count: int = len(groups)  # Verify interest if multiple groups or existing interest.
    if is_legacy() and registration and registration.manuhome and registration.manuhome.reg_owner_groups:
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


def interest_required(groups, registration: MhrRegistration = None, delete_groups=None):
    """Determine if group interest is required."""
    group_count: int = len(groups)  # Verify interest if multiple groups or existing interest.
    if group_count > 1:
        return True
    if is_legacy() and registration and registration.manuhome and registration.manuhome.reg_owner_groups:
        for existing in registration.manuhome.reg_owner_groups:
            if existing.status == Db2Owngroup.StatusTypes.ACTIVE and \
                    existing.tenancy_type != Db2Owngroup.TenancyTypes.SOLE and \
                    not delete_group(existing.group_id, delete_groups) and \
                    existing.get_interest_fraction(False) > 0:
                group_count += 1
    return group_count > 1


def common_tenancy(groups, new: bool, active_count: int = 0) -> bool:
    """Determine if the owner groups is a tenants in common scenario."""
    if new and groups and len(groups) == 1:
        return False
    for group in groups:
        group_type = group.get('type', '')
        tenancy_type: str = NEW_TENANCY_LEGACY.get(group_type, '') if groups else ''
        if tenancy_type != Db2Owngroup.TenancyTypes.SOLE and active_count > 1:
            return True
    return False


def validate_owner_groups(groups,
                          new: bool,
                          registration: MhrRegistration = None,
                          delete_groups=None,
                          active_count: int = 0):
    """Verify owner groups are valid."""
    error_msg = ''
    if not groups:
        return error_msg
    so_count: int = 0
    if common_tenancy(groups, new, active_count):
        return validate_owner_groups_common(groups, registration, delete_groups)
    for group in groups:
        tenancy_type: str = NEW_TENANCY_LEGACY.get(group.get('type', ''), '') if groups else ''
        if new and tenancy_type == Db2Owngroup.TenancyTypes.COMMON and group.get('type', '') != MhrTenancyTypes.NA:
            error_msg += GROUP_COMMON_INVALID
        error_msg += validate_owner_group(group, False)
        for owner in group.get('owners'):
            if tenancy_type == Db2Owngroup.TenancyTypes.SOLE:
                so_count += 1
            error_msg += validate_owner(owner)
    if so_count > 1 or (so_count == 1 and len(groups) > 1):
        error_msg += ADD_SOLE_OWNER_INVALID
    if not new and active_count == 1 and groups[0].get('type', '') in (MhrTenancyTypes.COMMON, MhrTenancyTypes.NA):
        error_msg += GROUP_COMMON_INVALID
    return error_msg


def validate_owner_groups_common(groups, registration: MhrRegistration = None, delete_groups=None):
    """Verify tenants in common owner groups are valid."""
    error_msg = ''
    tc_owner_count_invalid: bool = False
    common_denominator: int = 0
    int_required: bool = interest_required(groups, registration, delete_groups)
    for group in groups:
        if common_denominator == 0:
            common_denominator = group.get('interestDenominator', 0)
        elif group.get('interestDenominator', 0) > common_denominator:
            common_denominator = group.get('interestDenominator', 0)
        if not group.get('owners'):
            tc_owner_count_invalid = True
        error_msg += validate_owner_group(group, int_required)
        for owner in group.get('owners'):
            error_msg += validate_owner(owner)
    error_msg += validate_group_interest(groups, common_denominator, registration, delete_groups)
    if tc_owner_count_invalid:
        error_msg += OWNERS_COMMON_INVALID
    return error_msg


def validate_location(location):  # pylint: disable=too-many-branches
    """Verify the combination of location values is valid."""
    error_msg = ''
    # No point validating if no no required locationType.
    if not location or not location.get('locationType'):
        return error_msg
    loc_type = location['locationType']
    if loc_type == MhrLocationTypes.RESERVE:
        if not location.get('bandName'):
            error_msg += BAND_NAME_REQUIRED
        if not location.get('reserveNumber'):
            error_msg += RESERVE_NUMBER_REQUIRED
    elif loc_type == MhrLocationTypes.MANUFACTURER:
        if not location.get('dealerName'):
            error_msg += LOCATION_DEALER_REQUIRED
    elif loc_type == MhrLocationTypes.MH_PARK:
        if not location.get('parkName'):
            error_msg += LOCATION_PARK_NAME_REQUIRED
        if not location.get('pad'):
            error_msg += LOCATION_PARK_PAD_REQUIRED
    elif loc_type == MhrLocationTypes.STRATA:
        if not location.get('pidNumber') and \
                (not location.get('lot') or not location.get('plan') or not location.get('landDistrict')):
            error_msg += LOCATION_STRATA_REQUIRED
    elif loc_type == MhrLocationTypes.OTHER and not location.get('pidNumber'):
        if not location.get('landDistrict'):
            error_msg += LOCATION_OTHER_REQUIRED
        elif location.get('plan') and location.get('lot'):
            error_msg += ''
        elif not location.get('districtLot'):
            error_msg += LOCATION_OTHER_REQUIRED
    error_msg += validate_location_allowed(location, loc_type)
    return error_msg


def validate_location_allowed(location, loc_type):
    """Verify the allowed location values by location type."""
    error_msg = ''
    if loc_type == MhrLocationTypes.MANUFACTURER:
        if location.get('bandName') or location.get('parkName') or location.get('reserveNumber') or \
                location.get('pad') or has_location_ltsa_details(location):
            error_msg = LOCATION_MANUFACTURER_ALLOWED
    elif loc_type == MhrLocationTypes.MH_PARK and \
            (location.get('bandName') or location.get('reserveNumber') or
             location.get('dealerName') or has_location_ltsa_details(location)):
        error_msg = LOCATION_PARK_ALLOWED
    elif loc_type == MhrLocationTypes.RESERVE and \
            (location.get('dealerName') or location.get('parkName') or location.get('pad')):
        error_msg = LOCATION_RESERVE_ALLOWED
    elif loc_type in (MhrLocationTypes.STRATA, MhrLocationTypes.OTHER):
        if location.get('dealerName') or location.get('parkName') or location.get('pad') or \
                location.get('bandName') or location.get('reserveNumber'):
            if loc_type == MhrLocationTypes.STRATA:
                error_msg = LOCATION_STRATA_ALLOWED
            else:
                error_msg = LOCATION_OTHER_ALLOWED
    return error_msg


def has_location_ltsa_details(location) -> bool:
    """Verify the location has ltsa detail properties."""
    if location.get('lot') or location.get('parcel') or location.get('block') or location.get('districtLot') or\
            location.get('partOf'):
        return True
    if location.get('section') or location.get('township') or location.get('range') or location.get('plan') or \
            location.get('meridian'):
        return True
    if location.get('pidNumber') or location.get('legalDescription') or location.get('landDistrict'):
        return True
    return False


def validate_manufacturer_permit(mhr_number: str, party, current_location):
    """Validate transport permit business rules specific to manufacturers."""
    error_msg = ''
    # Must be located on a dealer's/manufacturer's lot.
    if current_location and not current_location.get('dealerName'):
        error_msg += MANUFACTURER_DEALER_INVALID
    # Permit can only be issued once per home by a manufacturer.
    if mhr_number and party:
        name: str = party.get('businessName')
        if not name and party.get('personName') and party['personName'].get('first') and \
                party['personName'].get('last'):
            name = party['personName'].get('first').strip().upper() + ' '
            if party['personName'].get('middle'):
                name += party['personName'].get('middle').strip().upper() + ' '
            name += party['personName'].get('last').strip().upper()
        if name:
            permit_count: int = validator_utils.get_permit_count(mhr_number, name)
            if permit_count > 0:
                error_msg += MANUFACTURER_PERMIT_INVALID
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


def owner_name_match(registration: MhrRegistration,  # pylint: disable=too-many-branches
                     request_owner):
    """Verify the request owner name matches one of the current owner names."""
    if not registration or not request_owner:
        return False
    request_name: str = ''
    first_name: str = ''
    last_name: str = ''
    match: bool = False
    is_business = request_owner.get('organizationName')
    if is_business:
        request_name = request_owner.get('organizationName').strip().upper()
    elif request_owner.get('individualName') and request_owner['individualName'].get('first') and \
            request_owner['individualName'].get('last'):
        request_name = to_db2_ind_name(request_owner.get('individualName')).strip()
        first_name = request_owner['individualName'].get('first').strip().upper()
        last_name = request_owner['individualName'].get('last').strip().upper()
    if not request_name:
        return False
    if is_legacy() and registration.manuhome and registration.manuhome.reg_owner_groups:
        for group in registration.manuhome.reg_owner_groups:
            if group.status == Db2Owngroup.StatusTypes.ACTIVE:
                for owner in group.owners:
                    if owner.owner_type == Db2Owner.OwnerTypes.BUSINESS and is_business and \
                            owner.name.strip() == request_name:
                        return True
                    if owner.owner_type == Db2Owner.OwnerTypes.INDIVIDUAL and not is_business and \
                            owner.name.strip() == request_name:
                        return True
    if registration.owner_groups:
        for group in registration.owner_groups:
            if group.status_type == MhrOwnerStatusTypes.ACTIVE:
                for owner in group.owners:
                    if is_business and owner.business_name == request_name:
                        match = True
                    elif not is_business and owner.first_name == first_name and owner.last_name == last_name:
                        match = True
    if not match and registration.change_registrations:  # pylint: disable=too-many-nested-blocks
        for reg in registration.change_registrations:
            for group in reg.owner_groups:
                if group.status_type == MhrOwnerStatusTypes.ACTIVE:
                    for owner in group.owners:
                        if is_business and owner.business_name == request_name:
                            match = True
                        elif not is_business and owner.first_name == first_name and owner.last_name == last_name:
                            match = True
    return match


def validate_tax_certificate(request_location, current_location):
    """Validate transport permit business rules specific to a tax certificate."""
    error_msg = ''
    if request_location and request_location.get('taxExpiryDate'):
        tax_ts = ts_from_iso_format(request_location.get('taxExpiryDate'))
        if not valid_tax_cert_date(now_ts(), tax_ts):
            error_msg += LOCATION_TAX_DATE_INVALID
        elif not request_location.get('taxCertificate'):
            error_msg += LOCATION_TAX_CERT_REQUIRED
    else:
        if current_location and current_location.get('dealerName'):
            return error_msg
        if current_location.get('parkName') and request_location.get('parkName'):
            park_1 = current_location.get('parkName').strip().upper()
            park_2 = current_location.get('parkName').strip().upper()
            if park_1 == park_2:
                return error_msg
        error_msg += LOCATION_TAX_CERT_REQUIRED
    return error_msg


def validate_owner_party_type(json_data,  # pylint: disable=too-many-branches
                              groups, new: bool,
                              active_group_count: int):
    """Verify owner groups are valid."""
    error_msg = ''
    owner_death: bool = reg_utils.is_transfer_due_to_death_staff(json_data.get('registrationType'))
    if not groups:
        return error_msg
    for group in groups:
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
                if not new and not owner_death and party_type and \
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


def get_active_group_count(json_data, registration: MhrRegistration) -> int:
    """Count number of active owner groups."""
    group_count: int = 0
    if json_data.get('ownerGroups'):
        group_count += len(json_data.get('ownerGroups'))
    else:
        if json_data.get('addOwnerGroups'):
            group_count += len(json_data.get('addOwnerGroups'))
        if json_data.get('deleteOwnerGroups'):
            group_count -= len(json_data.get('deleteOwnerGroups'))
        group_count += validator_utils.get_existing_group_count(registration)
    return group_count
