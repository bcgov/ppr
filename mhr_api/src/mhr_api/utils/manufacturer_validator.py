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

from mhr_api.models import MhrManufacturer, utils as model_utils


VALIDATOR_ERROR = 'Error performing manufacturer extra validation. '
OWNER_MISMATCH = 'The request SOLE Owner name and address must match the existing manufacturer information. '
OWNER_GROUP_COUNT_INVALID = 'Only one Owner group is allowed. '
OWNER_COUNT_INVALID = 'Only one Owner is allowed. '
OWNER_GROUP_TYPE_INVALID = 'The Owner group tenancy type must be SOLE. '
SUBMITTING_MISMATCH = 'The request Submitting Party name and address must match the existing manufacturer information. '
LOCATION_TYPE_INVALID = 'The Location type must be MANUFACTURER. '
LOCATION_MISMATCH = 'The request Location dealer name and address must match the existing manufacturer information. '
DESC_MANUFACTURER_MISMATCH = 'The request Description manufacturer name must match the existing manufacturer ' + \
    'information. '
REBUILT_INVALID = 'Description rebuilt remarks are not allowed. '
OTHER_INVALID = 'Description other remarks are not allowed. '
ENGINEER_DATE_INVALID = 'Description engineer date is not allowed. '
ENGINEER_NAME_INVALID = 'Description engineer name is not allowed. '
YEAR_INVALID = 'Description manufactured home year invalid: it must be within 1 year of the current year. '
CSA_NUMBER_REQIRED = 'Description CSA number is required. '


def validate_registration(json_data, manufacturer: MhrManufacturer):
    """Perform all extra manufacturer new MH registration data validation checks not covered by schema validation."""
    error_msg = ''
    try:
        current_app.logger.debug('Performing manufacturer extra data validation.')
        man_json = manufacturer.json
        error_msg += validate_submitting_party(json_data, man_json)
        error_msg += validate_owner(json_data, man_json)
        error_msg += validate_location(json_data, man_json)
        error_msg += validate_description(json_data, man_json)
    except Exception as validation_exception:   # noqa: B902; eat all errors
        current_app.logger.error('validate_registration exception: ' + str(validation_exception))
        error_msg += VALIDATOR_ERROR
    return error_msg


def validate_submitting_party(json_data, manufacturer: MhrManufacturer):
    """Verify submitting party matches manufacturer submitting party."""
    error_msg = ''
    if not json_data.get('submittingParty'):
        return ''
    party = json_data.get('submittingParty')
    sub_man = manufacturer.get('submittingParty')
    if party.get('businessName', '') != sub_man.get('businessName') or party.get('address') != sub_man['address']:
        error_msg += SUBMITTING_MISMATCH
    return error_msg


def validate_location(json_data, manufacturer: MhrManufacturer):
    """Verify location matches manufacturer location information."""
    error_msg = ''
    if not json_data.get('location'):
        return ''
    loc = json_data.get('location')
    loc_man = manufacturer.get('location')
    if loc.get('locationType', '') != loc_man.get('locationType'):
        error_msg += LOCATION_TYPE_INVALID
    if loc.get('dealerName', '') != loc_man.get('dealerName') or loc.get('address') != loc_man['address']:
        error_msg += LOCATION_MISMATCH
    return error_msg


def validate_owner(json_data, manufacturer: MhrManufacturer):
    """Verify owner matches manufacturer owner information."""
    error_msg = ''
    if not json_data.get('ownerGroups'):
        return ''
    if len(json_data.get('ownerGroups')) != 1:
        error_msg = OWNER_GROUP_COUNT_INVALID
    group = json_data['ownerGroups'][0]
    group_man = manufacturer['ownerGroups'][0]
    owner_man = group_man['owners'][0]
    if group.get('type', '') != group_man.get('type'):
        error_msg += OWNER_GROUP_TYPE_INVALID
    if not group.get('owners'):
        return error_msg
    if len(group.get('owners')) != 1:
        error_msg += OWNER_COUNT_INVALID
    owner = group['owners'][0]
    if owner.get('organizationName', '') != owner_man.get('organizationName') or \
            owner.get('address') != owner_man['address']:
        error_msg += OWNER_MISMATCH
    return error_msg


def validate_description(json_data, manufacturer: MhrManufacturer):
    """Verify description passes manufacturer rules."""
    error_msg = ''
    if not json_data.get('description'):
        return ''
    desc = json_data.get('description')
    desc_man = manufacturer.get('description')
    if desc.get('manufacturer', '') != desc_man.get('manufacturer'):
        error_msg += DESC_MANUFACTURER_MISMATCH
    if desc.get('rebuiltRemarks'):
        error_msg += REBUILT_INVALID
    if desc.get('otherRemarks'):
        error_msg += OTHER_INVALID
    if desc.get('engineerDate'):
        error_msg += ENGINEER_DATE_INVALID
    if desc.get('engineerName'):
        error_msg += ENGINEER_NAME_INVALID
    if not desc.get('csaNumber'):
        error_msg += CSA_NUMBER_REQIRED
    if desc.get('baseInformation') and desc['baseInformation'].get('year') and \
            not model_utils.valid_manufacturer_year(desc['baseInformation'].get('year')):
        error_msg += YEAR_INVALID
    return error_msg
