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

from mhr_api.models import MhrRegistration, Db2Owngroup
from mhr_api.models.type_tables import MhrRegistrationStatusTypes
from mhr_api.models.db2.owngroup import NEW_TENANCY_LEGACY
from mhr_api.models.utils import is_legacy
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
CONSIDERATION_REQUIRED = 'Consideration required for this registration. '
TRANSFER_DATE_REQUIRED = 'Transfer date is required for this registration. '


def validate_registration(json_data, is_staff: bool = False):
    """Perform all registration data validation checks not covered by schema validation."""
    error_msg = ''
    if is_staff:
        error_msg += validate_doc_id(json_data)
        if not json_data.get('ownerGroups'):
            error_msg += OWNER_GROUPS_REQUIRED
    error_msg += validate_submitting_party(json_data)
    if json_data.get('ownerGroups'):
        for group in json_data.get('ownerGroups'):
            for owner in group.get('owners'):
                error_msg += validate_owner(owner)
    error_msg += validate_location(json_data)
    return error_msg


def validate_transfer(registration: MhrRegistration, json_data, is_staff: bool = False):
    """Perform all transfer data validation checks not covered by schema validation."""
    error_msg = ''
    if is_staff:
        error_msg += validate_doc_id(json_data)
    error_msg += validate_submitting_party(json_data)
    if json_data.get('addOwnerGroups'):
        for group in json_data.get('addOwnerGroups'):
            for owner in group.get('owners'):
                error_msg += validate_owner(owner)
    error_msg += validate_registration_state(registration)
    if is_legacy() and registration and registration.manuhome and json_data.get('deleteOwnerGroups'):
        error_msg += validate_delete_owners_legacy(registration, json_data)
    if not is_staff:
        if not json_data.get('declaredValue') or json_data.get('declaredValue') < 0:
            error_msg += DECLARED_VALUE_REQUIRED
        if not json_data.get('consideration'):
            error_msg += CONSIDERATION_REQUIRED
        if not json_data.get('transferDate'):
            error_msg += TRANSFER_DATE_REQUIRED
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


def validate_location(json_data):
    """Verify location values are valid."""
    error_msg = ''
    if not json_data.get('location'):
        return error_msg
    location = json_data.get('location')
    desc: str = 'location'
    error_msg += validate_text(location.get('parkName'), desc + ' park name')
    error_msg += validate_text(location.get('dealerName'), desc + ' dealer name')
    error_msg += validate_text(location.get('additionalDescription'), desc + ' additional description')
    error_msg += validate_text(location.get('exceptionPlan'), desc + ' exception plan')
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
