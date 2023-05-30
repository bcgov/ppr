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

from mhr_api.utils import registration_validator as validator, manufacturer_validator as man_validator
from mhr_api.models import MhrRegistration, MhrManufacturer
from mhr_api.models.type_tables import MhrRegistrationStatusTypes, MhrTenancyTypes, MhrDocumentTypes
from mhr_api.models.utils import is_legacy, now_ts
from mhr_api.services.authz import QUALIFIED_USER_GROUP
from tests.unit.utils.test_registration_data import (
    SO_VALID,
    JT_VALID,
    SO_OWNER_MULTIPLE,
    SO_GROUP_MULTIPLE,
    JT_OWNER_SINGLE,
    TC_GROUPS_VALID,
    TC_GROUP_VALID,
    INTEREST_VALID_1,
    INTEREST_VALID_2,
    INTEREST_VALID_3,
    INTEREST_INVALID_1,
    INTEREST_INVALID_2,
    LOCATION_PARK,
    LOCATION_RESERVE,
    LOCATION_OTHER,
    LOCATION_STRATA,
    LOCATION_MANUFACTURER,
    SO_VALID_EXEC,
    SO_VALID_TRUSTEE,
    SO_VALID_ADMIN,
    JT_VALID_EXEC,
    JT_VALID_TRUSTEE,
    JT_VALID_ADMIN,
    TC_VALID_EXEC,
    TC_VALID_TRUSTEE,
    TC_VALID_ADMIN,
    JT_GROUP_VALID,
    JT_GROUP_MIX,
    MANUFACTURER_VALID,
    MANUFACTURER_SUB_INVALID,
    MANUFACTURER_LOCATION_INVALID,
    MANUFACTURER_DESC_INVALID
)


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
# testdata pattern is ({description}, {valid}, {submitting}, {owners}, {location}, {desc}, {message content})
TEST_MANUFACTURER_DATA = [
    ('Valid', True, None, None, None, None, None),
    ('Invalid submitting party', False, MANUFACTURER_SUB_INVALID, None, None, None, man_validator.SUBMITTING_MISMATCH),
    ('Invalid owner', False, None, SO_VALID, None, None, man_validator.OWNER_MISMATCH),
    ('Invalid owner count', False, None, JT_VALID, None, None, man_validator.OWNER_COUNT_INVALID),
    ('Invalid group type', False, None, JT_VALID, None, None, man_validator.OWNER_GROUP_TYPE_INVALID),
    ('Invalid group count', False, None, TC_GROUPS_VALID, None, None, man_validator.OWNER_GROUP_COUNT_INVALID),
    ('Invalid loc type', False, None, None, MANUFACTURER_LOCATION_INVALID, None, man_validator.LOCATION_TYPE_INVALID),
    ('Invalid location', False, None, None, MANUFACTURER_LOCATION_INVALID, None, man_validator.LOCATION_MISMATCH),
    ('Invalid description', False, None, None, None, MANUFACTURER_DESC_INVALID,
     man_validator.DESC_MANUFACTURER_MISMATCH)
]
# testdata pattern is ({year_offset}, {rebuilt}, {other}, {csa}, {eng_date}, {eng_name}, {message content})
TEST_MANUFACTURER_DESC_DATA = [
    (-1, None, None, '786356', None, None, None),
    (1, None, None, '786356', None, None, None),
    (-2, None, None, '786356', None, None, man_validator.YEAR_INVALID),
    (0, 'TEST', None, '786356', None, None, man_validator.REBUILT_INVALID),
    (0, None, 'TEST', '786356', None, None, man_validator.OTHER_INVALID),
    (0, None, None, None, None, None, man_validator.CSA_NUMBER_REQIRED),
    (0, None, None, '786356', '2022-11-28T17:05:15-07:53', None, man_validator.ENGINEER_DATE_INVALID),
    (0, None, None, '786356', None, 'TEST', man_validator.ENGINEER_NAME_INVALID)
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
    ('Reg street non utf-8', None, 'first', 'middle', 'last', None, REGISTRATION),
    ('Reg streetAdditional non utf-8', None, 'first', 'middle', 'last', None, REGISTRATION),
    ('Reg city non utf-8', None, 'first', 'middle', 'last', None, REGISTRATION),
    ('Trans invalid org/bus name', INVALID_TEXT_CHARSET, None, None, None, INVALID_CHARSET_MESSAGE, TRANSFER),
    ('Trans invalid first name', None, INVALID_TEXT_CHARSET, 'middle', 'last', INVALID_CHARSET_MESSAGE, TRANSFER),
    ('Trans invalid middle name', None, 'first', INVALID_TEXT_CHARSET, 'last', INVALID_CHARSET_MESSAGE, TRANSFER),
    ('Trans invalid last name', None, 'first', 'middle', INVALID_TEXT_CHARSET, INVALID_CHARSET_MESSAGE, TRANSFER)
]
# testdata pattern is ({description}, {park_name}, {dealer}, {pad}, {reserve_num}, {band_name}, {pid_num}, {message content})
TEST_LOCATION_DATA_MANUFACTURER = [
    ('Valid manufacturer', None, 'dealer', None, None, None, None, None),
    ('Invalid manufacturer dealer', None, None, None, None, None, None, validator.LOCATION_DEALER_REQUIRED),
    ('Invalid manufacturer park', 'park', 'dealer', None, None, None, None, validator.LOCATION_MANUFACTURER_ALLOWED),
    ('Invalid manufacturer pad', None, 'dealer', '1234', None, None, None, validator.LOCATION_MANUFACTURER_ALLOWED),
    ('Invalid manufacturer reserve', None, 'dealer', None, '1234', None, None, validator.LOCATION_MANUFACTURER_ALLOWED),
    ('Invalid manufacturer band', None, 'dealer', None, None, 'band', None, validator.LOCATION_MANUFACTURER_ALLOWED),
    ('Invalid manufacturer pid', None, 'dealer', None, None, None, '123-456-789',
     validator.LOCATION_MANUFACTURER_ALLOWED)
]
# testdata pattern is ({description}, {band name}, {reserve_num}, {dealer}, {park}, {pad}, {pid}, {message content})
TEST_LOCATION_DATA_RESERVE = [
    ('Valid request', 'band', 'test', None, None, None, None, None),
    ('Valid request pid', 'band', 'test', None, None, None, '123-456-789', None),
    ('Missing band name', None, 'test', None, None, None, None, validator.BAND_NAME_REQUIRED),
    ('Missing band name', '', 'test', None, None, None, None, validator.BAND_NAME_REQUIRED),
    ('Missing reserve number', 'band name', '', None, None, None, None, validator.RESERVE_NUMBER_REQUIRED),
    ('Missing reserve number', 'band name', None, None, None, None, None, validator.RESERVE_NUMBER_REQUIRED),
    ('Invalid reserve dealer', 'band', 'test', 'dealer', None, None, None, validator.LOCATION_RESERVE_ALLOWED),
    ('Invalid reserve park', 'band', 'test', None, 'park', None, None, validator.LOCATION_RESERVE_ALLOWED),
    ('Invalid reserve pad', 'band', 'test', None, None, '1234', None, validator.LOCATION_RESERVE_ALLOWED)
]
# testdata pattern is ({description}, {park_name}, {dealer}, {pad}, {reserve_num}, {band_name}, {lot}, {message content})
TEST_LOCATION_DATA_PARK = [
    ('Valid park', 'park', None, '1234', None, None, None, None),
    ('Invalid park dealer', None, 'dealer', None, None, None, None, validator.LOCATION_PARK_ALLOWED),
    ('Invalid missing park', '', None, '1234', None, None, None, validator.LOCATION_PARK_NAME_REQUIRED),
    ('Invalid missing park', None, None, '1234', None, None, None, validator.LOCATION_PARK_NAME_REQUIRED),
    ('Invalid missing pad', 'park', None, '', None, None, None, validator.LOCATION_PARK_PAD_REQUIRED),
    ('Invalid missing pad', 'park', None, None, None, None, None, validator.LOCATION_PARK_PAD_REQUIRED),
    ('Invalid park reserve', 'park', None, '1234', '1234', None, None, validator.LOCATION_PARK_ALLOWED),
    ('Invalid park band', 'park', None, '1234', None, 'band', None, validator.LOCATION_PARK_ALLOWED),
    ('Invalid park lot', 'park', None, '1234', None, None, 'lot', validator.LOCATION_PARK_ALLOWED)
]
# testdata pattern is ({description}, {park}, {dealer}, {pad}, {reserve}, {band}, {pid}, {lot}, {plan}, {district}, 
# {message content})
TEST_LOCATION_DATA_STRATA = [
    ('Valid strata pid', None, None, None, None, None, '123-456-789', None, None, None, None),
    ('Valid strata lot', None, None, None, None, None, None, 'lot', 'plan', 'district', None),
    ('Invalid strata pid', None, None, None, None, None, None, None, None, None,
     validator.LOCATION_STRATA_REQUIRED),
    ('Invalid strata lot', None, None, None, None, None, None, None, 'plan', 'district',
     validator.LOCATION_STRATA_REQUIRED),
    ('Invalid strata plan', None, None, None, None, None, None, 'lot', None, 'district',
     validator.LOCATION_STRATA_REQUIRED),
    ('Invalid strata district', None, None, None, None, None, None, 'lot', 'plan', None,
     validator.LOCATION_STRATA_REQUIRED),
    ('Invalid strata dealer', None, 'dealer', None, None, None, '123-456-789', None, None, None,
     validator.LOCATION_STRATA_ALLOWED),
    ('Invalid strata park', 'park', None, None, None, None, '123-456-789', None, None, None,
     validator.LOCATION_STRATA_ALLOWED),
    ('Invalid strata pad', None, None, '1234', None, None, '123-456-789', None, None, None,
     validator.LOCATION_STRATA_ALLOWED),
    ('Invalid strata reserve', None, None, None, '1234', None, '123-456-789', None, None, None,
     validator.LOCATION_STRATA_ALLOWED),
    ('Invalid strata band', None, None, None, None, 'band', '123-456-789', None, None, None,
     validator.LOCATION_STRATA_ALLOWED)
]
# testdata pattern is ({description}, {park}, {dealer}, {pad}, {reserve}, {band}, {pid}, {lot}, {plan}, {district}, 
# {dlot}, {message content})
TEST_LOCATION_DATA_OTHER = [
    ('Valid other pid', None, None, None, None, None, '123-456-789', None, None, None, None, None),
    ('Valid other lot', None, None, None, None, None, None, 'lot', 'plan', 'district', None, None),
    ('Valid other dlot', None, None, None, None, None, None, None, None, 'district', 'dlot', None),
    ('Invalid other pid', None, None, None, None, None, None, None, None, None, None,
     validator.LOCATION_OTHER_REQUIRED),
    ('Invalid other lot', None, None, None, None, None, None, None, 'plan', 'district', None,
     validator.LOCATION_OTHER_REQUIRED),
    ('Invalid other plan', None, None, None, None, None, None, 'lot', None, 'district', None,
     validator.LOCATION_OTHER_REQUIRED),
    ('Invalid other district', None, None, None, None, None, None, 'lot', 'plan', None, 'dlot',
     validator.LOCATION_OTHER_REQUIRED),
    ('Invalid other dlot', None, None, None, None, None, None, None, None, 'district', None,
     validator.LOCATION_OTHER_REQUIRED),
    ('Invalid other dealer', None, 'dealer', None, None, None, '123-456-789', None, None, None, None,
     validator.LOCATION_OTHER_ALLOWED),
    ('Invalid other park', 'park', None, None, None, None, '123-456-789', None, None, None, None,
     validator.LOCATION_OTHER_ALLOWED),
    ('Invalid other pad', None, None, '1234', None, None, '123-456-789', None, None, None, None,
     validator.LOCATION_OTHER_ALLOWED),
    ('Invalid other reserve', None, None, None, '1234', None, '123-456-789', None, None, None, None,
     validator.LOCATION_OTHER_ALLOWED),
    ('Invalid other band', None, None, None, None, 'band', '123-456-789', None, None, None, None,
     validator.LOCATION_OTHER_ALLOWED)
]
# testdata pattern is ({description}, {rebuilt}, {other}, {message content})
TEST_DESCRIPTION_DATA = [
    ('Non utf-8 rebuilt remarks', INVALID_TEXT_CHARSET, None, None),
    ('Non utf-8 other remarks', None, INVALID_TEXT_CHARSET, None)
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
    ('Invalid TC SO group', False, 1, 2, TC_GROUPS_VALID, validator.OWNERS_COMMON_SOLE_INVALID),
    ('Invalid TC 2 owners', False, 1, 2, TC_GROUPS_VALID, validator.OWNERS_COMMON_INVALID),
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
# testdata pattern is ({description}, {valid}, {group1}, {group2}, {g1_type}, {o2_party_type}, {message})
TEST_PARTY_TYPE_DATA = [
    ('Valid SO exec', True, SO_VALID_EXEC, None, None, None, None),
    ('Valid SO trustee', True, SO_VALID_TRUSTEE, None, None, None, None),
    ('Valid SO admin', True, SO_VALID_ADMIN, None, None, None, None),
    ('Valid JT exec', True, JT_VALID_EXEC, None, None, None, None),
    ('Valid JT trustee', True, JT_VALID_TRUSTEE, None, None, None, None),
    ('Valid JT admin', True, JT_VALID_ADMIN, None, None, None, None),
    ('Valid TC exec', True, JT_VALID_EXEC, TC_VALID_EXEC, None, None, None),
    ('Valid TC trustee', True, JT_VALID_TRUSTEE, TC_VALID_TRUSTEE, None, None, None),
    ('Valid TC admin', True, JT_VALID_ADMIN, TC_VALID_ADMIN, None, None, None),
    ('Invalid SO type NA', False, SO_VALID_EXEC, None, 'NA', None, validator.TENANCY_TYPE_NA_INVALID),
    ('Invalid SO exec no desc', False, SO_VALID_EXEC, None, None, None, validator.OWNER_DESCRIPTION_REQUIRED),
    ('Invalid common type JOINT', False, JT_VALID_EXEC, TC_VALID_EXEC, 'JOINT', None,
     validator.TENANCY_PARTY_TYPE_INVALID),
    ('Invalid JT party types 1', False, JT_VALID_EXEC, None, None, 'ADMINISTRATOR', validator.GROUP_PARTY_TYPE_INVALID),
    ('Invalid JT party types 2', False, JT_VALID_TRUSTEE, None, None, 'EXECUTOR', validator.GROUP_PARTY_TYPE_INVALID),
    ('Invalid JT party types 3', False, JT_VALID_ADMIN, None, None, 'TRUSTEE', validator.GROUP_PARTY_TYPE_INVALID),
    ('Invalid JT type NA', False, JT_GROUP_VALID, None, 'NA', None, validator.TENANCY_TYPE_NA_INVALID2),
    ('Invalid NA type mix', False, JT_GROUP_MIX, None, None, None, validator.TENANCY_TYPE_NA_INVALID2),
    ('Invalid JT type mix', False, JT_GROUP_MIX, None, 'JT', None, validator.TENANCY_PARTY_TYPE_INVALID)
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


@pytest.mark.parametrize('desc,valid,submitting,owners,location,description,message_content', TEST_MANUFACTURER_DATA)
def test_validate_registration_man(session, desc, valid, submitting, owners, location, description, message_content):
    """Assert that new MH registration validation for a manufacturer works as expected."""
    # setup
    json_data = copy.deepcopy(MANUFACTURER_VALID)
    now = now_ts()
    json_data['description']['baseInformation']['year'] = now.year
    if submitting:
        json_data['submittingParty'] = submitting
    if owners:
        json_data['ownerGroups'] = owners
    if location:
        json_data['location'] = location
    if description:
        json_data['description'] = description
    manufacturer: MhrManufacturer = MhrManufacturer.find_by_account_id('2523')
    valid_format, errors = schema_utils.validate(json_data, 'registration', 'mhr')
    # if errors:
    #    current_app.logger.debug('Schema errors')
    #    for error in errors:
    #        current_app.logger.debug(error)
    # Additional validation not covered by the schema.
    error_msg = validator.validate_registration(json_data, False)
    error_msg += man_validator.validate_registration(json_data, manufacturer)
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
    json_data['location'] = copy.deepcopy(LOCATION_PARK)
    json_data['ownerGroups'] = copy.deepcopy(groups)
    if json_data.get('documentId'):
        del json_data['documentId']
    if desc == 'Invalid TC only 1 group':
        del json_data['ownerGroups'][1]
    elif desc == 'Invalid TC no owner':
        json_data['ownerGroups'][0]['owners'] = []
    elif desc == 'Invalid TC SO group':
        json_data['ownerGroups'][0]['type'] = 'SOLE'
    elif desc == 'Invalid TC 2 owners':
        owners = copy.deepcopy(JT_GROUP_VALID).get('owners')
        json_data['ownerGroups'][0]['owners'] = owners
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
    json_data['location'] = copy.deepcopy(LOCATION_PARK)
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
    if desc == 'Reg invalid street':
        party['address']['street'] = INVALID_TEXT_CHARSET
    elif desc == 'Reg invalid streetAdditional':
        party['address']['streetAdditional'] = INVALID_TEXT_CHARSET
    elif desc == 'Reg invalid city':
        party['address']['city'] = INVALID_TEXT_CHARSET
    error_msg = ''
    if desc.startswith('Reg'):
        error_msg = validator.validate_registration(json_data, False)
    else:
        error_msg = validator.validate_transfer(None, json_data, False, QUALIFIED_USER_GROUP)
    if message_content:
        assert error_msg.find(message_content) != -1
    else:
        assert not error_msg


@pytest.mark.parametrize('desc,bus_name,first,middle,last,message_content,data', TEST_PARTY_DATA)
def test_validate_owner(session, desc, bus_name, first, middle, last, message_content, data):
    """Assert that owner invalid character set validation works as expected."""
    # setup
    json_data = copy.deepcopy(data)
    json_data['location'] = copy.deepcopy(LOCATION_PARK)
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
    if desc == 'Reg invalid street':
        party['address']['street'] = INVALID_TEXT_CHARSET
    elif desc == 'Reg invalid streetAdditional':
        party['address']['streetAdditional'] = INVALID_TEXT_CHARSET
    elif desc == 'Reg invalid city':
        party['address']['city'] = 'Montréal'  # INVALID_TEXT_CHARSET
    error_msg = ''
    if desc.startswith('Reg'):
        error_msg = validator.validate_registration(json_data, False)
    else:
        error_msg = validator.validate_transfer(None, json_data, False, QUALIFIED_USER_GROUP)
    if message_content:
        assert error_msg.find(message_content) != -1
    else:
        assert not error_msg


@pytest.mark.parametrize('desc,park_name,dealer,pad,reserve_num,band_name,pid_num,message_content',
                         TEST_LOCATION_DATA_MANUFACTURER)
def test_validate_location_man(session, desc, park_name, dealer, pad, reserve_num, band_name, pid_num, message_content):
    """Assert that manufacturer location type validation works as expected."""
    # setup
    json_data = get_valid_registration(MhrTenancyTypes.SOLE)
    location = copy.deepcopy(LOCATION_MANUFACTURER)
    if park_name:
        location['parkName'] = park_name
    if not dealer:
        del location['dealerName']
    if pad:
        location['pad'] = pad
    if reserve_num:
        location['reserveNumber'] = reserve_num
    if band_name:
        location['bandName'] = band_name
    if pid_num:
        location['pidNumber'] = pid_num
    json_data['location'] = location
    error_msg = validator.validate_registration(json_data, False)
    if message_content:
        assert error_msg.find(message_content) != -1
    else:
        assert not error_msg


@pytest.mark.parametrize('desc,rebuilt,other,message_content', TEST_DESCRIPTION_DATA)
def test_validate_reg_description(session, desc, rebuilt, other, message_content):
    """Assert that description validation works as expected."""
    # setup
    json_data = get_valid_registration(MhrTenancyTypes.SOLE)
    description = json_data.get('description')
    if rebuilt:
        description['rebuiltRemarks'] = rebuilt
    elif other:
        description['otherRemarks'] = other
    error_msg = validator.validate_registration(json_data, False)
    if message_content:
        assert error_msg.find(message_content) != -1
    else:
        assert not error_msg


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
    json_data['location'] = copy.deepcopy(LOCATION_PARK)
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


@pytest.mark.parametrize('desc,band_name,reserve_num,dealer,park,pad,pid,message_content', TEST_LOCATION_DATA_RESERVE)
def test_validate_location_reserve(session, desc, band_name, reserve_num, dealer, park, pad, pid, message_content):
    """Assert that location RESERVE location type validation works as expected."""
    json_data = get_valid_registration(MhrTenancyTypes.SOLE)
    location = copy.deepcopy(LOCATION_RESERVE)
    if park:
        location['parkName'] = park
    if dealer:
        location['dealerName'] = dealer
    if pad:
        location['pad'] = pad
    if reserve_num:
        location['reserveNumber'] = reserve_num
    else:
        del location['reserveNumber']
    if band_name:
        location['bandName'] = band_name
    else:
        del location['bandName']
    if pid:
        location['pidNumber'] = pid
    json_data['location'] = location
    error_msg = validator.validate_registration(json_data, False)
    if message_content:
        assert error_msg.find(message_content) != -1
    else:
        assert not error_msg


@pytest.mark.parametrize('desc,park_name,dealer,pad,reserve_num,band_name,lot,message_content',
                         TEST_LOCATION_DATA_PARK)
def test_validate_location_park(session, desc, park_name, dealer, pad, reserve_num, band_name, lot, message_content):
    """Assert that park location type validation works as expected."""
    # setup
    json_data = get_valid_registration(MhrTenancyTypes.SOLE)
    location = copy.deepcopy(LOCATION_PARK)
    if park_name:
        location['parkName'] = park_name
    else:
        del location['parkName']
    if pad:
        location['pad'] = pad
    else:
        del location['pad']
    if dealer:
        location['dealerName'] = dealer
    if reserve_num:
        location['reserveNumber'] = reserve_num
    if band_name:
        location['bandName'] = band_name
    if lot:
        location['lot'] = lot
    json_data['location'] = location
    error_msg = validator.validate_registration(json_data, False)
    if message_content:
        assert error_msg.find(message_content) != -1
    else:
        assert not error_msg


@pytest.mark.parametrize('desc,park,dealer,pad,reserve,band,pid,lot,plan,district,message_content',
                         TEST_LOCATION_DATA_STRATA)
def test_validate_location_strata(session, desc, park, dealer, pad, reserve, band, pid, lot, plan, district,
                                  message_content):
    """Assert that strata location type validation works as expected."""
    # setup
    json_data = get_valid_registration(MhrTenancyTypes.SOLE)
    location = copy.deepcopy(LOCATION_STRATA)
    if park:
        location['parkName'] = park
    if pad:
        location['pad'] = pad
    if dealer:
        location['dealerName'] = dealer
    if reserve:
        location['reserveNumber'] = reserve
    if band:
        location['bandName'] = band
    if pid:
        location['pidNumber'] = pid
    else:
        del location['pidNumber']
    if lot:
        location['lot'] = lot
    if plan:
        location['plan'] = plan
    if district:
        location['landDistrict'] = district
    json_data['location'] = location
    error_msg = validator.validate_registration(json_data, False)
    if message_content:
        assert error_msg.find(message_content) != -1
    else:
        assert not error_msg


@pytest.mark.parametrize('desc,park,dealer,pad,reserve,band,pid,lot,plan,district,dlot,message_content',
                         TEST_LOCATION_DATA_OTHER)
def test_validate_location_other(session, desc, park, dealer, pad, reserve, band, pid, lot, plan, district, dlot,
                                  message_content):
    """Assert that other location type validation works as expected."""
    # setup
    json_data = get_valid_registration(MhrTenancyTypes.SOLE)
    location = copy.deepcopy(LOCATION_OTHER)
    if park:
        location['parkName'] = park
    if pad:
        location['pad'] = pad
    if dealer:
        location['dealerName'] = dealer
    if reserve:
        location['reserveNumber'] = reserve
    if band:
        location['bandName'] = band
    if pid:
        location['pidNumber'] = pid
    else:
        del location['pidNumber']
    if lot:
        location['lot'] = lot
    if plan:
        location['plan'] = plan
    if district:
        location['landDistrict'] = district
    if dlot:
        location['districtLot'] = dlot
    json_data['location'] = location
    error_msg = validator.validate_registration(json_data, False)
    if message_content:
        assert error_msg.find(message_content) != -1
    else:
        assert not error_msg


@pytest.mark.parametrize('desc,valid,group1,group2,g1_type,o1_party_type,message_content', TEST_PARTY_TYPE_DATA)
def test_validate_registration_party(session, desc, valid, group1, group2, g1_type, o1_party_type, message_content):
    """Assert that new MH registration owner group party type validation works as expected."""
    # setup
    json_data = get_valid_registration(MhrTenancyTypes.SOLE)
    owner_groups = []
    group_1 = copy.deepcopy(group1)
    group_2 = copy.deepcopy(group2) if group2 else None
    if g1_type:
        group_1['type'] = g1_type
    if o1_party_type:
        group_1['owners'][1]['partyType'] = o1_party_type
    if group_2:
        group_1['interest'] = 'UNDIVIDED'
        group_1['interestNumerator'] = 1
        group_1['interestDenominator'] = 2
    if desc == 'Invalid SO exec no desc':
        del group_1['owners'][0]['description']
    owner_groups.append(group_1)
    if group_2:
        group_2['interest'] = 'UNDIVIDED'
        group_2['interestNumerator'] = 1
        group_2['interestDenominator'] = 2
        owner_groups.append(group_2)
    json_data['ownerGroups'] = owner_groups
    valid_format, errors = schema_utils.validate(json_data, 'registration', 'mhr')
    # Additional validation not covered by the schema.
    error_msg = validator.validate_registration(json_data, False)
    # if error_msg:
    #    current_app.logger.debug(error_msg)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('year_offset,rebuilt,other,csa,eng_date,eng_name,message_content', TEST_MANUFACTURER_DESC_DATA)
def test_validate_man_desc(session, year_offset, rebuilt, other, csa, eng_date, eng_name, message_content):
    """Assert that new MH registration validation for a manufacturer description works as expected."""
    # setup
    json_data = copy.deepcopy(MANUFACTURER_VALID)
    now = now_ts()
    description = json_data['description']
    description['baseInformation']['year'] = now.year + year_offset
    if rebuilt:
        description['rebuiltRemarks'] = rebuilt
    if other:
        description['otherRemarks'] = other
    if not csa:
        del description['csaNumber']
    if eng_date:
        description['engineerDate'] = eng_date
    if eng_name:
        description['engineerName'] = eng_name
    manufacturer: MhrManufacturer = MhrManufacturer.find_by_account_id('2523')
    # Additional validation not covered by the schema.
    error_msg = man_validator.validate_registration(json_data, manufacturer)
    if not message_content:
        assert error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1
