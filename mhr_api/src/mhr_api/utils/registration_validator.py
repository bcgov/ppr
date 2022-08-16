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
# from mhr_api.models import utils as model_utils


OWNERS_NOT_ALLOWED = 'Owners not allowed with new registrations: use ownerGroups instead.'
DOC_ID_REQUIRED = 'Document Number is required for staff registrations.'
SUBMITTING_REQUIRED = 'Submitting Party is required for MH registrations.'
OWNER_GROUPS_REQUIRED = 'At least one owner group is required for staff registrations.'


def validate_registration(json_data, is_staff: bool = False):
    """Perform all registration data validation checks not covered by schema validation."""
    error_msg = ''
    if is_staff and not json_data.get('documentId'):
        error_msg += DOC_ID_REQUIRED
    if json_data.get('owners'):
        error_msg += OWNERS_NOT_ALLOWED
    if not json_data.get('submittingParty'):
        error_msg += SUBMITTING_REQUIRED
    if is_staff and not json_data.get('ownerGroups'):
        error_msg += OWNER_GROUPS_REQUIRED
    return error_msg
