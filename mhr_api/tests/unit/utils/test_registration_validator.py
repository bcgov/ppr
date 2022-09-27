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
from registry_schemas.example_data.mhr import REGISTRATION, TRANSFER

from mhr_api.utils import registration_validator as validator
from mhr_api.models import MhrRegistration
from mhr_api.models.type_tables import MhrRegistrationStatusTypes
from mhr_api.models.utils import is_legacy


DESC_VALID = 'Valid'
DESC_MISSING_DOC_ID = 'Missing document id'
DESC_MISSING_SUBMITTING = 'Missing submitting party'
DESC_MISSING_OWNER_GROUP = 'Missing owner group'
DESC_DOC_ID_EXISTS = 'Invalid document id exists'
DOC_ID_EXISTS = '80038730'
DOC_ID_VALID = '63166035'
DOC_ID_INVALID_CHECKSUM = '63166034'
INVALID_TEXT_CHARSET = 'TEST \U0001d5c4\U0001d5c6/\U0001d5c1 INVALID'
INVALID_CHARSET_MESSAGE = 'The character set is not supported'
# testdata pattern is ({description}, {valid}, {staff}, {doc_id}, {message content})
TEST_REG_DATA = [
    (DESC_VALID, True, True, DOC_ID_VALID, None),
    ('Valid no doc id not staff', True, False, None, None),
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
# testdata pattern is ({description}, {valid}, {street}, {city}, {message content})
TEST_LEGACY_REG_DATA = [
    (DESC_VALID, True, '0123456789012345678901234567890', '01234567890123456789', None),
    ('Valid location street long', True, '01234567890123456789012345678901', 'KAMLOOPS',
     validator.LEGACY_ADDRESS_STREET_TOO_LONG.format(add_desc='Location')),
    ('Valid location city long', True, '1234 Front St.', '012345678901234567890',
     validator.LEGACY_ADDRESS_CITY_TOO_LONG.format(add_desc='Location'))
]
# testdata pattern is ({description}, {bus_name}, {first}, {middle}, {last}, {message content})
TEST_PARTY_DATA = [
    ('Reg invalid org/bus name', INVALID_TEXT_CHARSET, None, None, None, INVALID_CHARSET_MESSAGE, REGISTRATION),
    ('Reg invalid first name', None, INVALID_TEXT_CHARSET, 'middle', 'last', INVALID_CHARSET_MESSAGE, REGISTRATION),
    ('Reg invalid middle name', None, 'first', INVALID_TEXT_CHARSET, 'last', INVALID_CHARSET_MESSAGE, REGISTRATION),
    ('Reg invalid last name', None, 'first', 'middle', INVALID_TEXT_CHARSET, INVALID_CHARSET_MESSAGE, REGISTRATION),
    ('Trans invalid org/bus name', INVALID_TEXT_CHARSET, None, None, None, INVALID_CHARSET_MESSAGE, TRANSFER),
    ('Trans invalid first name', None, INVALID_TEXT_CHARSET, 'middle', 'last', INVALID_CHARSET_MESSAGE, TRANSFER),
    ('Trans invalid middle name', None, 'first', INVALID_TEXT_CHARSET, 'last', INVALID_CHARSET_MESSAGE, TRANSFER),
    ('Trans invalid last name', None, 'first', 'middle', INVALID_TEXT_CHARSET, INVALID_CHARSET_MESSAGE, TRANSFER)
]
# testdata pattern is ({description}, {park_name}, {dealer}, {additional}, {except_plan}, {message content})
TEST_LOCATION_DATA = [
    ('Invalid park name', INVALID_TEXT_CHARSET, None, None, None, INVALID_CHARSET_MESSAGE),
    ('Invalid dealer name', None, INVALID_TEXT_CHARSET, None, None, INVALID_CHARSET_MESSAGE),
    ('Invalid additional description', None, None, INVALID_TEXT_CHARSET, None, INVALID_CHARSET_MESSAGE),
    ('Invalid exception plan', None, None, None, INVALID_TEXT_CHARSET, INVALID_CHARSET_MESSAGE)
]
# testdata pattern is ({description}, {valid}, {staff}, {doc_id}, {message content}, {status})
TEST_TRANSFER_DATA = [
    (DESC_VALID, True, True, DOC_ID_VALID, None, MhrRegistrationStatusTypes.ACTIVE),
    ('Valid no doc id not staff', True, False, None, None, None),
    (DESC_MISSING_DOC_ID, False, True, None, validator.DOC_ID_REQUIRED, None),
    (DESC_DOC_ID_EXISTS, False, True, DOC_ID_EXISTS, validator.DOC_ID_EXISTS, None),
    ('Invalid EXEMPT', False, False, None, validator.STATE_NOT_ALLOWED, MhrRegistrationStatusTypes.EXEMPT),
    ('Invalid HISTORICAL', False, False, None, validator.STATE_NOT_ALLOWED, MhrRegistrationStatusTypes.HISTORICAL)
]


@pytest.mark.parametrize('desc,valid,staff,doc_id,message_content', TEST_REG_DATA)
def test_validate_registration(session, desc, valid, staff, doc_id, message_content):
    """Assert that new MH registration validation works as expected."""
    # setup
    json_data = copy.deepcopy(REGISTRATION)
    if desc == DESC_MISSING_OWNER_GROUP:
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


@pytest.mark.parametrize('desc,valid,staff,doc_id,message_content,status', TEST_TRANSFER_DATA)
def test_validate_transfer(session, desc, valid, staff, doc_id, message_content, status):
    """Assert that MH transfer validation works as expected."""
    # setup
    json_data = copy.deepcopy(TRANSFER)
    if doc_id:
        json_data['documentId'] = doc_id
    elif json_data.get('documentId'):
        del json_data['documentId']
    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = None
    if status:
        registration = MhrRegistration(status_type=status)
    error_msg = validator.validate_transfer(registration, json_data, staff)
    if errors:
        current_app.logger.debug(errors)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,bus_name,first,middle,last,message_content,data', TEST_PARTY_DATA)
def test_validate_submitting(session, desc, bus_name, first, middle, last, message_content, data):
    """Assert that submitting party invalid character set validation works as expected."""
    # setup
    json_data = copy.deepcopy(data)
    party = json_data.get('submittingParty')
    if bus_name:
        party['businessName'] = bus_name
    else:
        del party['businessName']
        party['personName'] = {
            'first': first,
            'middle': middle,
            'last': last
        }
    error_msg = ''
    if desc.startswith('Reg'):
        error_msg = validator.validate_registration(json_data, False)
    else:
        error_msg = validator.validate_transfer(None, json_data, False)
    assert error_msg != ''
    if message_content:
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,bus_name,first,middle,last,message_content,data', TEST_PARTY_DATA)
def test_validate_owner(session, desc, bus_name, first, middle, last, message_content, data):
    """Assert that owner invalid character set validation works as expected."""
    # setup
    json_data = copy.deepcopy(data)
    group = None
    if json_data.get('ownerGroups'):
        group = json_data['ownerGroups'][0]
    else:
        group = json_data['addOwnerGroups'][0]
    party = group['owners'][0]
    if bus_name:
        party['organizationName'] = bus_name
        del party['individualName']
    else:
        party['individualName'] = {
            'first': first,
            'middle': middle,
            'last': last
        }
    error_msg = ''
    if desc.startswith('Reg'):
        error_msg = validator.validate_registration(json_data, False)
    else:
        error_msg = validator.validate_transfer(None, json_data, False)
    assert error_msg != ''
    if message_content:
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,park_name,dealer,additional,except_plan,message_content', TEST_LOCATION_DATA)
def test_validate_reg_location(session, desc, park_name, dealer, additional, except_plan, message_content):
    """Assert that location invalid character set validation works as expected."""
    # setup
    json_data = copy.deepcopy(REGISTRATION)
    location = json_data.get('location')
    if park_name:
        location['parkName'] = park_name
    elif dealer:
        location['dealerName'] = dealer
    elif additional:
        location['additionalDescription'] = additional
    elif except_plan:
        location['exceptionPlan'] = except_plan
    error_msg = validator.validate_registration(json_data, False)
    assert error_msg != ''
    if message_content:
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,street,city,message_content', TEST_LEGACY_REG_DATA)
def test_validate_registration_legacy(session, desc, valid, street, city, message_content):
    """Assert that new MH registration legacy validation works as expected."""
    if is_legacy():
        # setup
        json_data = copy.deepcopy(REGISTRATION)
        json_data['location']['address']['street'] = street
        json_data['location']['address']['city'] = city
        valid_format, errors = schema_utils.validate(json_data, 'registration', 'mhr')
        # Additional validation not covered by the schema.
        error_msg = validator.validate_registration(json_data, False)
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
