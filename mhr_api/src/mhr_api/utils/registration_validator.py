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


OWNERS_NOT_ALLOWED = 'Owners not allowed with new registrations: use ownerGroups instead.'
DOC_ID_REQUIRED = 'Document ID is required for staff registrations.'
SUBMITTING_REQUIRED = 'Submitting Party is required for MH registrations.'
OWNER_GROUPS_REQUIRED = 'At least one owner group is required for staff registrations.'
OWNER_GROUPS_REQUIRED = 'At least one owner group is required for staff registrations.'
DOC_ID_EXISTS = 'Document ID must be unique: provided value already exists.'
DOC_ID_INVALID_CHECKSUM = 'Document ID is invalid: checksum failed.'


def validate_registration(json_data, is_staff: bool = False):
    """Perform all registration data validation checks not covered by schema validation."""
    error_msg = ''
    if is_staff:
        error_msg += validate_doc_id(json_data)
        if not json_data.get('ownerGroups'):
            error_msg += OWNER_GROUPS_REQUIRED
    if json_data.get('owners'):
        error_msg += OWNERS_NOT_ALLOWED
    if not json_data.get('submittingParty'):
        error_msg += SUBMITTING_REQUIRED
    return error_msg


def validate_doc_id(json_data):
    """Validate the registration document id."""
    error_msg = ''
    if not json_data.get('documentId'):
        error_msg += DOC_ID_REQUIRED
    elif not checksum_valid(json_data.get('documentId')):
        error_msg += DOC_ID_INVALID_CHECKSUM
    else:
        exists_count = MhrRegistration.get_doc_id_count(json_data.get('documentId'))
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
