# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Registration non-party validator tests."""
import copy

from flask import current_app
import pytest
from registry_schemas import utils as schema_utils
from registry_schemas.example_data.mhr import REGISTRATION, OWNER

from mhr_api.utils import registration_validator as validator


DESC_VALID = 'Valid'
DESC_OWNERS_INVALID = 'Invalid owners'
DESC_MISSING_DOC_ID = 'Missing document id'
DESC_MISSING_SUBMITTING = 'Missing submitting party'
DESC_MISSING_OWNER_GROUP = 'Missing owner group'
DESC_DOC_ID_EXISTS = 'Invalid document id exists'
DOC_ID_EXISTS = '80038730'
DOC_ID_VALID = '63166035'
DOC_ID_INVALID_CHECKSUM = '63166034'

# testdata pattern is ({description}, {valid}, {staff}, {doc_id}, {message content})
TEST_REG_DATA = [
    (DESC_VALID, True, True, DOC_ID_VALID, None),
    ('Valid no doc id not staff', True, False, None, None),
    (DESC_OWNERS_INVALID, False, True, DOC_ID_VALID, validator.OWNERS_NOT_ALLOWED),
    (DESC_MISSING_SUBMITTING, False, True, DOC_ID_VALID, validator.SUBMITTING_REQUIRED),
    (DESC_MISSING_SUBMITTING, False, False, DOC_ID_VALID, validator.SUBMITTING_REQUIRED),
    (DESC_MISSING_OWNER_GROUP, False, True, DOC_ID_VALID, validator.OWNER_GROUPS_REQUIRED),
    (DESC_MISSING_DOC_ID, False, True, None, validator.DOC_ID_REQUIRED),
    (DESC_DOC_ID_EXISTS, False, True, DOC_ID_EXISTS, validator.DOC_ID_EXISTS)
]
# testdata pattern is ({doc_id}, {valid})
TEST_CHECKSUM_DATA = [
    ('80048750', True),
    ('63288993', True),
    ('13288993', True),
    ('93288993', True),
    ('REG88993', True),
    ('63288994', False),
    ('X9948709', False),
    ('9948709', False),
    ('089948709', False),
]


@pytest.mark.parametrize('desc,valid,staff,doc_id,message_content', TEST_REG_DATA)
def test_validate_registration(session, desc, valid, staff, doc_id, message_content):
    """Assert that new MH registration validation works as expected."""
    # setup
    json_data = copy.deepcopy(REGISTRATION)
    if desc == DESC_OWNERS_INVALID:
        json_data['owners'] = [OWNER]
        del json_data['ownerGroups']
    elif desc == DESC_MISSING_OWNER_GROUP:
        del json_data['ownerGroups']
    elif desc == DESC_MISSING_SUBMITTING:
        del json_data['submittingParty']
    if doc_id:
        json_data['documentId'] = doc_id
    elif json_data.get('documentId'):
        del json_data['documentId']
    valid_format, errors = schema_utils.validate(json_data, 'registration', 'mhr')
    # Additional validation not covered by the schema.
    error_msg = validator.validate_registration(json_data, staff)
    if errors:
        current_app.logger.debug(errors)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('doc_id, valid', TEST_CHECKSUM_DATA)
def test_checksum_valid(session, doc_id, valid):
    """Assert that the document id checksum validation works as expected."""
    result = validator.checksum_valid(doc_id)
    assert result == valid
