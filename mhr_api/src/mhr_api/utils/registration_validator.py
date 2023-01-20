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

from mhr_api.models import MhrRegistration, Db2Owngroup, Db2Owner, registration_utils as reg_utils
from mhr_api.models.type_tables import MhrRegistrationStatusTypes, MhrDocumentTypes, MhrLocationTypes, MhrStatusTypes
from mhr_api.models.type_tables import MhrOwnerStatusTypes, MhrTenancyTypes, MhrPartyTypes
from mhr_api.models.db2.owngroup import NEW_TENANCY_LEGACY
from mhr_api.models.db2.utils import get_db2_permit_count
from mhr_api.models.utils import is_legacy, to_db2_ind_name, now_ts, ts_from_iso_format, valid_tax_cert_date
from mhr_api.services.authz import MANUFACTURER_GROUP
from mhr_api.services import ltsa
from mhr_api.utils import valid_charset


STATE_NOT_ALLOWED = 'The MH registration is not in a state where changes are allowed. '
OWNERS_NOT_ALLOWED = 'Owners not allowed with new registrations: use ownerGroups instead. '
DOC_ID_REQUIRED = 'Document ID is required for staff registrations. '
SUBMITTING_REQUIRED = 'Submitting Party is required for MH registrations. '
OWNER_GROUPS_REQUIRED = 'At least one owner group is required for staff registrations. '
DOC_ID_EXISTS = 'Document ID must be unique: provided value already exists. '
DOC_ID_INVALID_CHECKSUM = 'Document ID is invalid: checksum failed. '
CHARACTER_SET_UNSUPPORTED = 'The character set is not supported for {desc} value {value}. '
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
PPR_LIEN_EXISTS = 'This registration is not allowed to complete as an outstanding Personal Property Registry lien ' + \
    'exists on the manufactured home. '
BAND_NAME_REQUIRED = 'The location Indian Reserve band name is required for this registration. '
RESERVE_NUMBER_REQUIRED = 'The location Indian Reserve number is required for this registration. '
OWNERS_JOINT_INVALID = 'The owner group must contain at least 2 owners. '
OWNERS_COMMON_INVALID = 'Each owner group must contain at least 1 owner. '
LOCATION_DEALER_REQUIRED = 'The location dealer name is required for this registration. '
STATUS_CONFIRMATION_REQUIRED = 'The land status confirmation is required for this registration. '
LOCATION_PARK_NAME_REQUIRED = 'The location park name is required for this registration. '
LOCATION_ADDRESS_MISMATCH = 'The existing location address must match the current location address. '
OWNER_NAME_MISMATCH = 'The existing owner name must match exactly a current owner name for this registration. '
MANUFACTURER_DEALER_INVALID = 'The existing location must be a dealer or manufacturer lot for this registration. '
MANUFACTURER_PERMIT_INVALID = 'A manufacturer can only submit a transport permit once for a home. '
LOCATION_TAX_DATE_INVALID = 'Location tax certificate date is invalid. '
LOCATION_TAX_CERT_REQUIRED = 'Location tax certificate and tax certificate expiry date is required. '
LOCATION_PID_INVALID = 'Location PID verification failed: either the PID is invalid or the LTSA service is ' + \
                       'unavailable. '
PARTY_TYPE_INVALID = 'Death of owner requires an executor, trustee, administrator owner party type. '
GROUP_PARTY_TYPE_INVALID = 'Death of owner all owner party types within the group must be identical. '
OWNER_DESCRIPTION_REQUIRED = 'Death of owner description of owner party type is required. '
TRANSFER_PARTY_TYPE_INVALID = 'Owner party type of administrator, executor, trustee not allowed for this registration. '


def validate_registration(json_data, staff: bool = False):
    """Perform all registration data validation checks not covered by schema validation."""
    error_msg = ''
    try:
        if staff:
            error_msg += validate_doc_id(json_data)
            if not json_data.get('ownerGroups'):
                error_msg += OWNER_GROUPS_REQUIRED
        error_msg += validate_submitting_party(json_data)
        error_msg += validate_owner_groups(json_data.get('ownerGroups'), True)
        error_msg += validate_location(json_data)
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_registration exception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


def validate_transfer(registration: MhrRegistration, json_data, staff: bool = False):
    """Perform all transfer data validation checks not covered by schema validation."""
    error_msg = ''
    try:
        if staff:
            error_msg += validate_doc_id(json_data)
        if registration:
            error_msg += validate_ppr_lien(registration.mhr_number)
        error_msg += validate_submitting_party(json_data)
        error_msg += validate_owner_groups(json_data.get('addOwnerGroups'),
                                           False,
                                           registration,
                                           json_data.get('deleteOwnerGroups'))
        error_msg += validate_owner_party_type(json_data, json_data.get('addOwnerGroups'), False)
        error_msg += validate_registration_state(registration)
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
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_transfer exception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


def validate_exemption(registration: MhrRegistration, json_data, staff: bool = False):
    """Perform all exemption data validation checks not covered by schema validation."""
    error_msg = ''
    try:
        if staff:
            error_msg += validate_doc_id(json_data)
        if registration:
            error_msg += validate_ppr_lien(registration.mhr_number)
        error_msg += validate_submitting_party(json_data)
        error_msg += validate_registration_state(registration)
        if json_data.get('note'):
            if json_data['note'].get('documentType') and \
                    json_data['note'].get('documentType') not in (MhrDocumentTypes.EXRS, MhrDocumentTypes.EXNR):
                error_msg += NOTE_DOC_TYPE_INVALID
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_exemption exception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


def validate_permit(registration: MhrRegistration, json_data, staff: bool = False, group_name: str = None):
    """Perform all transport permit data validation checks not covered by schema validation."""
    error_msg = ''
    try:
        current_location = get_existing_location(registration)
        if staff:
            error_msg += validate_doc_id(json_data)
        elif registration and group_name and group_name == MANUFACTURER_GROUP:
            error_msg += validate_manufacturer_permit(registration.mhr_number, json_data.get('submittingParty'),
                                                      current_location)
        if registration:
            error_msg += validate_ppr_lien(registration.mhr_number)
        error_msg += validate_submitting_party(json_data)
        error_msg += validate_registration_state(registration)
        error_msg += validate_location(json_data)
        if json_data.get('newLocation'):
            location = json_data.get('newLocation')
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
                error_msg += validate_pid(location.get('pidNumber'))
        if current_location and json_data.get('existingLocation') and \
                not location_address_match(current_location, json_data.get('existingLocation')):
            error_msg += LOCATION_ADDRESS_MISMATCH
        if registration and json_data.get('owner') and not owner_name_match(registration, json_data.get('owner')):
            error_msg += OWNER_NAME_MISMATCH
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_transfer exception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


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


def validate_registration_state(registration: MhrRegistration):
    """Validate registration state: changes are only allowed on active homes."""
    error_msg = ''
    if not registration:
        return error_msg
    if registration.status_type and registration.status_type != MhrRegistrationStatusTypes.ACTIVE:
        error_msg += STATE_NOT_ALLOWED
    elif is_legacy() and registration.manuhome and \
            registration.manuhome.mh_status != registration.manuhome.StatusTypes.REGISTERED:
        error_msg += STATE_NOT_ALLOWED
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
                            existing.tenancy_type != NEW_TENANCY_LEGACY.get(tenancy_type):
                        error_msg += DELETE_GROUP_TYPE_INVALID.format(group_id=group_id)
            if not found:
                error_msg += DELETE_GROUP_ID_NONEXISTENT.format(group_id=group_id)
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


def validate_owner(owner):
    """Verify owner names are valid."""
    error_msg = ''
    if not owner:
        return error_msg
    desc: str = 'owner'
    if owner.get('organizationName'):
        error_msg += validate_text(owner.get('organizationName'), desc + ' organization name')
    elif owner.get('individualName'):
        error_msg += validate_individual_name(owner.get('individualName'), desc)
    return error_msg


def validate_owner_group(group, int_required: bool = False):
    """Verify owner group is valid."""
    error_msg = ''
    if not group:
        return error_msg
    tenancy_type: str = NEW_TENANCY_LEGACY.get(group.get('type', ''), '')
    if tenancy_type == Db2Owngroup.TenancyTypes.COMMON or int_required:
        if not group.get('interestNumerator') or group.get('interestNumerator', 0) < 1:
            error_msg += GROUP_NUMERATOR_MISSING
        if not group.get('interestDenominator') or group.get('interestDenominator', 0) < 1:
            error_msg += GROUP_DENOMINATOR_MISSING
    if tenancy_type == Db2Owngroup.TenancyTypes.JOINT and (not group.get('owners') or len(group.get('owners')) < 2):
        error_msg += OWNERS_JOINT_INVALID
    return error_msg


def delete_group(group_id: int, delete_groups):
    """Check if owner group is flagged for deletion."""
    if not delete_groups or group_id < 1:
        return False
    for group in delete_groups:
        if group.get('groupId', 0) == group_id:
            return True
    return False


def validate_group_interest(groups, denominator: int, registration: MhrRegistration = None, delete_groups=None):
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
        # current_app.logger.debug(f'existing numerator_sum={numerator_sum}, denominator={denominator}')
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
    # current_app.logger.debug(f'final numerator_sum={numerator_sum}, denominator={denominator}')
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


def common_tenancy(groups, new: bool) -> bool:
    """Determine if the owner groups is a tenants in common scenario."""
    if new and groups and len(groups) == 1:
        return False
    for group in groups:
        tenancy_type: str = NEW_TENANCY_LEGACY.get(group.get('type', ''), '') if groups else ''
        if tenancy_type != Db2Owngroup.TenancyTypes.SOLE:
            return True
    return False


def validate_owner_groups(groups, new: bool, registration: MhrRegistration = None, delete_groups=None):
    """Verify owner groups are valid."""
    error_msg = ''
    if not groups:
        return error_msg
    so_count: int = 0
    if common_tenancy(groups, new):
        return validate_owner_groups_common(groups, registration, delete_groups)
    for group in groups:
        tenancy_type: str = NEW_TENANCY_LEGACY.get(group.get('type', ''), '') if groups else ''
        if new and tenancy_type == Db2Owngroup.TenancyTypes.COMMON:
            error_msg += GROUP_COMMON_INVALID
        error_msg += validate_owner_group(group, False)
        for owner in group.get('owners'):
            if tenancy_type == Db2Owngroup.TenancyTypes.SOLE:
                so_count += 1
            error_msg += validate_owner(owner)
    if so_count > 1 or (so_count == 1 and len(groups) > 1):
        error_msg += ADD_SOLE_OWNER_INVALID
    # Adjust COMMON type when multiple owners: remove after UI change made.
    for group in groups:
        if group.get('type') and group.get('type') == MhrTenancyTypes.COMMON and group.get('owners') and \
                len(group.get('owners')) > 1:
            group['type'] = MhrTenancyTypes.JOINT
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


def validate_location(json_data):
    """Verify location values are valid."""
    error_msg = ''
    if not json_data.get('location') and not json_data.get('newLocation'):
        return error_msg
    location = json_data.get('location')
    if not location:
        location = json_data.get('newLocation')
    desc: str = 'location'
    error_msg += validate_text(location.get('parkName'), desc + ' park name')
    error_msg += validate_text(location.get('dealerName'), desc + ' dealer name')
    error_msg += validate_text(location.get('additionalDescription'), desc + ' additional description')
    error_msg += validate_text(location.get('exceptionPlan'), desc + ' exception plan')
    error_msg += validate_text(location.get('bandName'), desc + ' band name')
    if location.get('locationType') and location['locationType'] == MhrLocationTypes.RESERVE:
        if not location.get('bandName'):
            error_msg += BAND_NAME_REQUIRED
        if not location.get('reserveNumber'):
            error_msg += RESERVE_NUMBER_REQUIRED
    elif location.get('locationType') and location['locationType'] == MhrLocationTypes.MANUFACTURER:
        if not location.get('dealerName'):
            error_msg += LOCATION_DEALER_REQUIRED
    elif location.get('locationType') and location['locationType'] == MhrLocationTypes.MH_PARK:
        if not location.get('parkName'):
            error_msg += LOCATION_PARK_NAME_REQUIRED
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
            permit_count: int = get_permit_count(mhr_number, name)
            if permit_count > 0:
                error_msg += MANUFACTURER_PERMIT_INVALID
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


def get_permit_count(mhr_number: str, name: str) -> int:
    """Execute a query to count existing transport permit registrations on a home."""
    if is_legacy():
        return get_db2_permit_count(mhr_number, name)
    return 0


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


def validate_pid(pid: str):
    """Validate location pid exists with an LTSA lookup."""
    error_msg = ''
    if not pid:
        return error_msg
    lookup_result = ltsa.pid_lookup(pid)
    if not lookup_result:
        error_msg = LOCATION_PID_INVALID
    return error_msg


def validate_owner_party_type(json_data, groups, new: bool):
    """Verify owner groups are valid."""
    error_msg = ''
    owner_death: bool = json_data.get('deathOfOwner', False)
    if not groups:
        return error_msg
    for group in groups:
        if group.get('owners'):
            valid_type: bool = True
            first_type: str = None
            if group['owners'][0].get('partyType'):
                first_type = group['owners'][0].get('partyType')
            for owner in group['owners']:
                party_type = owner.get('partyType', None)
                if not new and owner_death:
                    if not party_type or party_type not in (MhrPartyTypes.ADMINISTRATOR, MhrPartyTypes.EXECUTOR,
                                                            MhrPartyTypes.TRUST, MhrPartyTypes.TRUSTEE):
                        error_msg += PARTY_TYPE_INVALID
                    if not first_type or party_type != first_type:
                        valid_type = False
                    if not owner.get('description'):
                        error_msg += OWNER_DESCRIPTION_REQUIRED
                elif not new and not owner_death and party_type in (MhrPartyTypes.ADMINISTRATOR, MhrPartyTypes.EXECUTOR,
                                                                    MhrPartyTypes.TRUST, MhrPartyTypes.TRUSTEE):
                    error_msg += TRANSFER_PARTY_TYPE_INVALID
            if not valid_type and len(group['owners']) > 1:
                error_msg += GROUP_PARTY_TYPE_INVALID
    return error_msg
