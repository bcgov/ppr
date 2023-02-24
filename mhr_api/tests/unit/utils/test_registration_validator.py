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
"""MH Registration and common validator tests."""
import copy

from flask import current_app
import pytest
from registry_schemas import utils as schema_utils
from registry_schemas.example_data.mhr import REGISTRATION, TRANSFER, EXEMPTION

from mhr_api.utils import registration_validator as validator
from mhr_api.models import MhrRegistration
from mhr_api.models.type_tables import MhrRegistrationStatusTypes, MhrTenancyTypes, MhrDocumentTypes, MhrLocationTypes, MhrRegistrationTypes
from mhr_api.models.type_tables import MhrPartyTypes
from mhr_api.models.utils import is_legacy


DESC_VALID = 'Valid'
DESC_MISSING_DOC_ID = 'Missing document id'
DESC_MISSING_SUBMITTING = 'Missing submitting party'
DESC_MISSING_OWNER_GROUP = 'Missing owner group'
DESC_DOC_ID_EXISTS = 'Invalid document id exists'
DESC_INVALID_GROUP_ID = 'Invalid delete owner group id'
DESC_INVALID_GROUP_TYPE = 'Invalid delete owner group type'
DESC_NONEXISTENT_GROUP_ID = 'Invalid nonexistent delete owner group id'
DOC_ID_EXISTS = '80038730'
DOC_ID_VALID = '63166035'
DOC_ID_INVALID_CHECKSUM = '63166034'
INVALID_TEXT_CHARSET = 'TEST \U0001d5c4\U0001d5c6/\U0001d5c1 INVALID'
INVALID_CHARSET_MESSAGE = 'The character set is not supported'
SO_VALID = [
    {
        'groupId': 2,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'SOLE'
    }
]
JT_VALID = [
    {
        'groupId': 2,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            },
            {
            'individualName': {
                'first': 'John',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'JOINT'
    }
]
SO_OWNER_MULTIPLE = [
    {
        'groupId': 2,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            },
            {
            'individualName': {
                'first': 'John',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'SOLE'
    }
]
SO_GROUP_MULTIPLE = [
    {
        'groupId': 2,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'SOLE'
    },
    {
        'groupId': 3,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'SOLE'
    }
]
JT_OWNER_SINGLE = [
    {
        'groupId': 2,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'JOINT'
    }
]
TC_GROUPS_VALID = [
    {
        'groupId': 1,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'COMMON',
        'interest': 'UNDIVIDED 1/2',
        'interestNumerator': 1,
        'interestDenominator': 2
    },
    {
        'groupId': 2,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }, {
            'individualName': {
                'first': 'Jane',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'JOINT',
        'interest': 'UNDIVIDED',
        'interestNumerator': 1,
        'interestDenominator': 2
    }
]
TC_GROUP_VALID = {
    'owners': [
        {
        'individualName': {
            'first': 'James',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
        },
        'phoneNumber': '6041234567'
        }, {
        'individualName': {
            'first': 'Jane',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
        }
        }
    ],
    'type': 'JOINT',
    'interest': 'UNDIVIDED',
    'interestNumerator': 1,
    'interestDenominator': 2
}
INTEREST_VALID_1 = [
    { 'numerator': 1, 'denominator': 2 }, { 'numerator': 1, 'denominator': 2 }
]
INTEREST_VALID_2 = [
    { 'numerator': 1, 'denominator': 2 }, { 'numerator': 1, 'denominator': 4 }, { 'numerator': 1, 'denominator': 4 }
]
INTEREST_VALID_3 = [
    { 'numerator': 1, 'denominator': 10 }, { 'numerator': 1, 'denominator': 2 }, { 'numerator': 2, 'denominator': 5 }
]
INTEREST_INVALID_1 = [
    { 'numerator': 1, 'denominator': 2 }, { 'numerator': 1, 'denominator': 4 }
]
INTEREST_INVALID_2 = [
    { 'numerator': 1, 'denominator': 2 }, { 'numerator': 2, 'denominator': 4 }, { 'numerator': 1, 'denominator': 4 }
]
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
    ('Valid location street long', True, '01234567890123456789012345678901', 'KAMLOOPS', None),
    ('Valid location city long', True, '1234 Front St.', '012345678901234567890', None)
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
# testdata pattern is ({description}, {park_name}, {dealer}, {additional}, {except_plan}, {band_name}, {message content})
TEST_LOCATION_DATA = [
    ('Invalid park name', INVALID_TEXT_CHARSET, None, None, None, None, INVALID_CHARSET_MESSAGE),
    ('Invalid dealer name', None, INVALID_TEXT_CHARSET, None, None, None, INVALID_CHARSET_MESSAGE),
    ('Invalid additional description', None, None, INVALID_TEXT_CHARSET, None, None, INVALID_CHARSET_MESSAGE),
    ('Invalid exception plan', None, None, None, INVALID_TEXT_CHARSET, None, INVALID_CHARSET_MESSAGE),
    ('Invalid band name', None, None, None, None, INVALID_TEXT_CHARSET, INVALID_CHARSET_MESSAGE)
]
# testdata pattern is ({description}, {valid}, {staff}, {doc_id}, {message content}, {status})
TEST_EXEMPTION_DATA = [
    (DESC_VALID, True, True, None, None, MhrRegistrationStatusTypes.ACTIVE),
    ('Valid no doc id not staff', True, False, None, None, None),
    ('Invalid EXEMPT', False, False, None, validator.STATE_NOT_ALLOWED, MhrRegistrationStatusTypes.EXEMPT),
    ('Invalid HISTORICAL', False, False, None, validator.STATE_NOT_ALLOWED, MhrRegistrationStatusTypes.HISTORICAL),
    ('Invalid note doc type', False, False, None, validator.NOTE_DOC_TYPE_INVALID, MhrRegistrationStatusTypes.ACTIVE)
]
# testdata pattern is ({description}, {valid}, {numerator}, {denominator}, {groups}, {message content})
TEST_REG_DATA_GROUP = [
    ('Valid TC', True, 1, 2, TC_GROUPS_VALID, None),
    ('Valid SO', True, None, None, SO_VALID, None),
    ('Valid JT', True, None, None, JT_VALID, None),
    ('Invalid TC no owner', False, 1, 2, TC_GROUPS_VALID, validator.OWNERS_COMMON_INVALID),
    ('Invalid TC only 1 group', False, 2, 2, TC_GROUPS_VALID, validator.GROUP_COMMON_INVALID),
    ('Invalid TC numerator missing', False, None, 2, TC_GROUPS_VALID, validator.GROUP_NUMERATOR_MISSING),
    ('Invalid TC numerator < 1', False, 0, 2, TC_GROUPS_VALID, validator.GROUP_NUMERATOR_MISSING),
    ('Invalid TC denominator missing', False, 1, None, TC_GROUPS_VALID, validator.GROUP_DENOMINATOR_MISSING),
    ('Invalid TC denominator < 1', False, 1, 0, TC_GROUPS_VALID, validator.GROUP_DENOMINATOR_MISSING),
    ('Invalid JT 1 owner', False, None, None, JT_OWNER_SINGLE, validator.OWNERS_JOINT_INVALID),
    ('Invalid SO 2 groups', False, None, None, SO_GROUP_MULTIPLE, validator.ADD_SOLE_OWNER_INVALID),
    ('Invalid SO 2 owners', False, None, None, SO_OWNER_MULTIPLE, validator.ADD_SOLE_OWNER_INVALID)
]
# testdata pattern is ({description}, {valid}, {interest_data}, {common_denominator}, {message content})
TEST_DATA_GROUP_INTEREST = [
    ('Valid 2 groups', True, INTEREST_VALID_1, 2, None),
    ('Valid 3 groups', True, INTEREST_VALID_2, 4, None),
    ('Valid 3 groups', True, INTEREST_VALID_3, 10, None),
    ('Invalid numerator sum low', False, INTEREST_INVALID_1, 4, validator.GROUP_INTEREST_MISMATCH),
    ('Inalid numerator sum high', False, INTEREST_INVALID_2, 4, validator.GROUP_INTEREST_MISMATCH)
]
# testdata pattern is ({description}, {mhr_number}, {message content})
TEST_DATA_LIEN_COUNT = [
    ('Valid request', '100000', '')
]
# testdata pattern is ({description}, {valid}, {band name}, {reserve_number}, {message content})
TEST_DATA_LOCATION_RESERVE = [
    ('Valid request', True, 'band name', 'test_num', None),
    ('Missing band name', False, '', 'test_num', validator.BAND_NAME_REQUIRED),
    ('Missing band name', False, None, 'test_num', validator.BAND_NAME_REQUIRED),
    ('Missing reserve number', False, 'band name', '', validator.RESERVE_NUMBER_REQUIRED),
    ('Missing reserve number', False, 'band name', None, validator.RESERVE_NUMBER_REQUIRED)
]


@pytest.mark.parametrize('desc,valid,staff,doc_id,message_content', TEST_REG_DATA)
def test_validate_registration(session, desc, valid, staff, doc_id, message_content):
    """Assert that new MH registration validation works as expected."""
    # setup
    json_data = get_valid_registration(MhrTenancyTypes.SOLE)
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


@pytest.mark.parametrize('desc,valid,numerator,denominator, groups, message_content', TEST_REG_DATA_GROUP)
def test_validate_registration_group(session, desc, valid, numerator, denominator, groups, message_content):
    """Assert that new MH registration owner group validation works as expected."""
    # setup
    json_data = copy.deepcopy(REGISTRATION)
    json_data['ownerGroups'] = copy.deepcopy(groups)
    if json_data.get('documentId'):
        del json_data['documentId']
    if desc == 'Invalid TC only 1 group':
        del json_data['ownerGroups'][1]
    elif desc == 'Invalid TC no owner':
        json_data['ownerGroups'][0]['owners'] = []
    elif groups[0].get('type') == MhrTenancyTypes.COMMON:
        for group in json_data.get('ownerGroups'):
            if not numerator:
                if 'interestNumerator' in group:
                    del group['interestNumerator']
                else:
                    group['interestNumerator'] = numerator
            if not denominator:
                if 'interestDenominator' in group:
                    del group['interestDenominator']
                else:
                    group['interestDenominator'] = denominator
    valid_format, errors = schema_utils.validate(json_data, 'registration', 'mhr')
    # Additional validation not covered by the schema.
    error_msg = validator.validate_registration(json_data, False)
    if errors:
        current_app.logger.debug(errors)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,staff,doc_id,message_content,status', TEST_EXEMPTION_DATA)
def test_validate_exemption(session, desc, valid, staff, doc_id, message_content, status):
    """Assert that MH exemption validation works as expected."""
    # setup
    json_data = copy.deepcopy(EXEMPTION)
    if staff and doc_id:
        json_data['documentId'] = doc_id
    elif json_data.get('documentId'):
        del json_data['documentId']
    if desc == 'Invalid note doc type':
        json_data['note']['documentType'] = MhrDocumentTypes.CAUC
    del json_data['submittingParty']['phoneExtension']
    # current_app.logger.info(json_data)
    valid_format, errors = schema_utils.validate(json_data, 'exemption', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number('045349', 'PS12345')
    if status:
        registration.status_type = status
    error_msg = validator.validate_exemption(registration, json_data, staff)
    if errors:
        for err in errors:
            current_app.logger.debug(err.message)
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


@pytest.mark.parametrize('desc,park_name,dealer,additional,except_plan,band_name,message_content', TEST_LOCATION_DATA)
def test_validate_reg_location(session, desc, park_name, dealer, additional, except_plan, band_name, message_content):
    """Assert that location invalid character set validation works as expected."""
    # setup
    json_data = get_valid_registration(MhrTenancyTypes.SOLE)
    location = json_data.get('location')
    if park_name:
        location['parkName'] = park_name
    elif dealer:
        location['dealerName'] = dealer
    elif additional:
        location['additionalDescription'] = additional
    elif except_plan:
        location['exceptionPlan'] = except_plan
    elif band_name:
        location['bandName'] = band_name
    error_msg = validator.validate_registration(json_data, False)
    assert error_msg != ''
    if message_content:
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,street,city,message_content', TEST_LEGACY_REG_DATA)
def test_validate_registration_legacy(session, desc, valid, street, city, message_content):
    """Assert that new MH registration legacy validation works as expected."""
    if is_legacy():
        # setup
        json_data = get_valid_registration(MhrTenancyTypes.SOLE)
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


@pytest.mark.parametrize('desc, valid, interest_data, common_den, message_content', TEST_DATA_GROUP_INTEREST)
def test_validate_group_interest(session, desc, valid, interest_data, common_den, message_content):
    """Assert that the group interest validation works as expected."""
    json_data = []
    for interest in interest_data:
        group = copy.deepcopy(TC_GROUP_VALID)
        group['interestNumerator'] = interest.get('numerator')
        group['interestDenominator'] = interest.get('denominator')
        json_data.append(group)
    error_msg = validator.validate_group_interest(json_data, common_den)
    if valid:
        assert error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


def get_valid_registration(o_type):
    """Build a valid registration"""
    json_data = copy.deepcopy(REGISTRATION)
    if o_type == MhrTenancyTypes.COMMON:
        json_data['ownerGroups'] = TC_GROUPS_VALID
    else:
        for group in json_data.get('ownerGroups'):
            if group.get('type', '') in ('TC', 'COMMON'):
                group['interestNumerator'] = 1
                group['interestDenominator'] = 2
    return json_data


@pytest.mark.parametrize('desc, mhr_number, message_content', TEST_DATA_LIEN_COUNT)
def test_validate_ppr_lien(session, desc, mhr_number, message_content):
    """Assert that the PPR lien check validation works as expected."""
    error_msg = validator.validate_ppr_lien(mhr_number)
    assert error_msg == message_content


@pytest.mark.parametrize('desc,valid,band_name,reserve_num,message_content', TEST_DATA_LOCATION_RESERVE)
def test_validate_location_reserve(session, desc, valid, band_name, reserve_num, message_content):
    """Assert that location RESERVE location type validation works as expected."""
    # setup
    json_data = get_valid_registration(MhrTenancyTypes.SOLE)
    location = json_data.get('location')
    location['locationType'] = MhrLocationTypes.RESERVE
    if band_name:
        location['bandName'] = band_name
    if reserve_num:
        location['reserveName'] = reserve_num
    error_msg = validator.validate_registration(json_data, False)
    assert error_msg != ''
    if message_content:
        assert error_msg.find(message_content) != -1
