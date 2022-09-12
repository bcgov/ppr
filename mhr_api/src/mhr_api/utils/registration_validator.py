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
from mhr_api.models.utils import is_legacy
from mhr_api.utils import valid_charset


OWNERS_NOT_ALLOWED = 'Owners not allowed with new registrations: use ownerGroups instead. '
DOC_ID_REQUIRED = 'Document ID is required for staff registrations. '
SUBMITTING_REQUIRED = 'Submitting Party is required for MH registrations. '
OWNER_GROUPS_REQUIRED = 'At least one owner group is required for staff registrations. '
DOC_ID_EXISTS = 'Document ID must be unique: provided value already exists. '
DOC_ID_INVALID_CHECKSUM = 'Document ID is invalid: checksum failed. '
LEGACY_ADDRESS_STREET_TOO_LONG = '{add_desc} address street length is too long: maximum length 31 characters. '
LEGACY_ADDRESS_CITY_TOO_LONG = '{add_desc} address city length is too long: maximum length 20 characters. '
CHARACTER_SET_UNSUPPORTED = 'The character set is not supported for {desc} value {value}. '


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
    error_msg += validate_registration_legacy(json_data)
    return error_msg


def validate_doc_id(json_data):
    """Validate the registration document id."""
    doc_id = json_data.get('documentId')
    current_app.logger.debug(f'Validating doc_id={doc_id}.')
    error_msg = ''
    if not doc_id:
        error_msg += DOC_ID_REQUIRED
    elif not checksum_valid(doc_id):
        error_msg += DOC_ID_INVALID_CHECKSUM
    else:
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


def validate_registration_legacy(json_data):
    """Perform new registration legacy specifc extra validation here."""
    error_msg = ''
    if not is_legacy():
        return error_msg
    location = json_data.get('location')
    if location and location.get('address'):
        address = location.get('address')
        if address.get('street') and len(address.get('street')) > 31:
            error_msg = LEGACY_ADDRESS_STREET_TOO_LONG.format(add_desc='Location')
        if address.get('city') and len(address.get('city')) > 20:
            error_msg += LEGACY_ADDRESS_CITY_TOO_LONG.format(add_desc='Location')

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
