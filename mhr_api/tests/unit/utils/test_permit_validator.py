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

from mhr_api.utils import registration_validator as validator, validator_utils
from mhr_api.models import MhrRegistration
from mhr_api.models.type_tables import MhrRegistrationStatusTypes
from mhr_api.services.authz import REQUEST_TRANSPORT_PERMIT, STAFF_ROLE, MANUFACTURER_GROUP


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
PERMIT = {
  'documentId': '80035947',
  'clientReferenceId': 'EX-TP001234',
  'submittingParty': {
    'personName': {
       'first': 'ROBERT', 
       'last': 'BERK'
     },
    'address': {
      'street': '613 LARSEN ROAD',
      'streetAdditional': 'BOX 72',
      'city': 'SALMO',
      'region': 'BC',
      'country': 'CA',
      'postalCode': ' '
    },
    'phoneNumber': '2505058308'
  },
  'owner': {
    'individualName': {
       'first': 'ROBERT',
       'middle': 'MICHAEL', 
       'last': 'BERK'
     },
    'address': {
      'street': '613 LARSEN ROAD',
      'streetAdditional': 'BOX 72',
      'city': 'SALMO',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V0G 1Z0'
    },
    'phoneNumber': '2505058308'
  },
  'existingLocation': {
    'locationType': 'MH_PARK',
    'address': {
      'street': '1117 GLENDALE AVENUE',
      'city': 'SALMO',
      'region': 'BC',
      'country': 'CA',
      'postalCode': ''
    },
    'leaveProvince': False,
    'parkName': 'GLENDALE TRAILER PARK',
    'pad': '1'
  },
  'newLocation': {
    'locationType': 'MH_PARK',
    'address': {
      'street': '1117 GLENDALE AVENUE',
      'city': 'SALMO',
      'region': 'BC',
      'country': 'CA',
      'postalCode': ''
    },
    'leaveProvince': False,
    'parkName': 'GLENDALE TRAILER PARK',
    'pad': '2',
    'taxCertificate': True,
    'taxExpiryDate': '2035-01-31T08:00:00+00:00'
  },
  'landStatusConfirmation': True
}
MANUFACTURER_PERMIT = {
  'documentId': '80035947',
  'clientReferenceId': 'EX-TP001234',
  'submittingParty': {
    'businessName': 'CHAMPION CANADA INTERNATIONAL ULC',
    'address': {
      'street': 'PO BOX 845 #200 HIGHWAY 18 WEST',
      'city': 'ESTEVAN',
      'region': 'SK',
      'country': 'CA',
      'postalCode': 'S4A 2A7'
    },
    'phoneNumber': '2507660588'
  },
  'owner': {
    'organizationName': 'CHAMPION CANADA INTERNATIONAL ULC',
    'address': {
      'street': 'PO BOX 845 #200 HIGHWAY 18 WEST',
      'city': 'ESTEVAN',
      'region': 'SK',
      'country': 'CA',
      'postalCode': 'S4A 2A7'
    },
    'phoneNumber': '2507660588'
  },
  'existingLocation': {
    'locationType': 'MANUFACTURER',
    'address': {
      'street': '200 HIGHWAY 18 WEST',
      'city': 'ESTEVAN',
      'region': 'SK',
      'country': 'CA',
      'postalCode': ''
    },
    'leaveProvince': False,
    'dealerName': 'CHAMPION CANADA INTERNATIONAL ULC - SRI HOMES'
  },
  'newLocation': {
    'locationType': 'MH_PARK',
    'address': {
      'street': '1117 GLENDALE AVENUE',
      'city': 'SALMO',
      'region': 'BC',
      'country': 'CA',
      'postalCode': ''
    },
    'leaveProvince': False,
    'parkName': 'GLENDALE TRAILER PARK',
    'pad': '2',
    'taxCertificate': True,
    'taxExpiryDate': '2035-01-31T08:00:00+00:00'
  },
  'landStatusConfirmation': True
}

LOCATION_PARK = {
    'locationType': 'MH_PARK',
    'address': {
      'street': '1117 GLENDALE AVENUE',
      'city': 'SALMO',
      'region': 'BC',
      'country': 'CA',
      'postalCode': ''
    },
    'leaveProvince': False,
    'parkName': 'GLENDALE TRAILER PARK',
    'pad': '2'
}
LOCATION_PARK_2 = {
    'locationType': 'MH_PARK',
    'address': {
      'street': '1117 GLENDALE AVENUE',
      'city': 'SALMO',
      'region': 'BC',
      'country': 'CA',
      'postalCode': ''
    },
    'leaveProvince': False,
    'parkName': 'DIFFERENT GLENDALE TRAILER PARK',
    'pad': '2'
}
LOCATION_PARK_NO_NAME = {
    'locationType': 'MH_PARK',
    'address': {
      'street': '1117 GLENDALE AVENUE',
      'city': 'SALMO',
      'region': 'BC',
      'country': 'CA',
      'postalCode': ''
    },
    'leaveProvince': False,
    'parkName': '',
    'pad': '2'
}
LOCATION_MANUFACTURER_NO_DEALER = {
    'locationType': 'MANUFACTURER',
    'address': {
      'street': '1117 GLENDALE AVENUE',
      'city': 'SALMO',
      'region': 'BC',
      'country': 'CA',
      'postalCode': ''
    },
    'leaveProvince': False,
    'dealerName': ''
}
LOCATION_PID = {
    'locationType': 'STRATA',
    'address': {
        'street': '7612 LUDLOM RD.',
        'city': 'DEKA LAKE',
        'region': 'BC',
        'country': 'CA',
        'postalCode': ''
    },
    'leaveProvince': False,
    'pidNumber': '007351119',
    'taxCertificate': True,
    'taxExpiryDate': '2035-01-31T08:00:00+00:00'
}
LOCATION_TAX_INVALID = {
    'locationType': 'STRATA',
    'address': {
        'street': '7612 LUDLOM RD.',
        'city': 'DEKA LAKE',
        'region': 'BC',
        'country': 'CA',
        'postalCode': ''
    },
    'leaveProvince': False,
    'taxCertificate': True,
    'taxExpiryDate': '2023-01-01T08:00:00+00:00'
}
LOCATION_TAX_MISSING = {
    'locationType': 'STRATA',
    'address': {
        'street': '7612 LUDLOM RD.',
        'city': 'DEKA LAKE',
        'region': 'BC',
        'country': 'CA',
        'postalCode': ''
    },
    'leaveProvince': False
}
LOCATION_RESERVE = {
    'locationType': 'RESERVE',
    'bandName': 'BAND NAME',
    'reserveNumber': '12',
    'address': {
        'street': '7612 LUDLOM RD.',
        'city': 'DEKA LAKE',
        'region': 'BC',
        'country': 'CA',
        'postalCode': ''
    },
    'leaveProvince': False
}
LOCATION_OTHER = {
    'locationType': 'OTHER',
    'lot': '3',
    'parcel': 'A (69860M)',
    'address': {
        'street': '7612 LUDLOM RD.',
        'city': 'DEKA LAKE',
        'region': 'BC',
        'country': 'CA',
        'postalCode': ''
    },
    'leaveProvince': False
}


# testdata pattern is ({description}, {park_name}, {dealer}, {additional}, {except_plan}, {band_name}, {message content})
TEST_LOCATION_DATA = [
    ('Non utf-8 park name', INVALID_TEXT_CHARSET, None, None, None, None, None),
    ('Non utf-8 dealer name', None, INVALID_TEXT_CHARSET, None, None, None, None),
    ('Non utf-8 additional description', None, None, INVALID_TEXT_CHARSET, None, None, None),
    ('Non utf-8 exception plan', None, None, None, INVALID_TEXT_CHARSET, None, None),
    ('Non utf-8 band name', None, None, None, None, INVALID_TEXT_CHARSET, None)
]
# test data pattern is ({description}, {valid}, {staff}, {doc_id}, {message_content}, {status}, {group})
TEST_PERMIT_DATA = [
    (DESC_VALID, True, True, None, None, MhrRegistrationStatusTypes.ACTIVE, STAFF_ROLE),
    ('Valid no doc id not staff', True, False, None, None, None, REQUEST_TRANSPORT_PERMIT),
    ('Invalid FROZEN', False, False, None, validator_utils.STATE_NOT_ALLOWED, MhrRegistrationStatusTypes.ACTIVE,
     REQUEST_TRANSPORT_PERMIT),
    ('Invalid staff FROZEN', False, True, None, validator_utils.STATE_FROZEN_AFFIDAVIT, MhrRegistrationStatusTypes.ACTIVE,
     REQUEST_TRANSPORT_PERMIT),
    ('Invalid EXEMPT', False, False, None, validator_utils.STATE_NOT_ALLOWED, MhrRegistrationStatusTypes.EXEMPT,
     STAFF_ROLE),
    ('Invalid HISTORICAL', False, False, None, validator_utils.STATE_NOT_ALLOWED, MhrRegistrationStatusTypes.HISTORICAL,
     REQUEST_TRANSPORT_PERMIT)
]
# testdata pattern is ({description}, {valid}, {mhr_num}, {location}, {message content}, {group})
TEST_PERMIT_DATA_EXTRA = [
    ('Valid location no tax cert', True, '100413', LOCATION_PARK, None, REQUEST_TRANSPORT_PERMIT),
    ('Invalid MANUFACTURER no dealer', False, '100413', LOCATION_MANUFACTURER_NO_DEALER,
     validator.LOCATION_DEALER_REQUIRED, REQUEST_TRANSPORT_PERMIT),
    ('Invalid MH_PARK no name', False, '100413', LOCATION_PARK_NO_NAME, validator.LOCATION_PARK_NAME_REQUIRED,
     REQUEST_TRANSPORT_PERMIT),
    ('Invalid owner name', False, '100413', None, validator.OWNER_NAME_MISMATCH, REQUEST_TRANSPORT_PERMIT),
    ('Invalid existing location address', False, '100413', None, validator.LOCATION_ADDRESS_MISMATCH,
     REQUEST_TRANSPORT_PERMIT),
    ('Invalid location RESERVE no tax cert', False, '100413', LOCATION_RESERVE, validator.LOCATION_TAX_CERT_REQUIRED,
     REQUEST_TRANSPORT_PERMIT),
    ('Invalid location tax cert date', False, '100413', LOCATION_TAX_INVALID, validator.LOCATION_TAX_DATE_INVALID,
     REQUEST_TRANSPORT_PERMIT),
    ('Missing location tax cert', False, '100413', LOCATION_TAX_MISSING, validator.LOCATION_TAX_CERT_REQUIRED,
     REQUEST_TRANSPORT_PERMIT),
    ('Missing land status confirm OTHER', False, '100413', LOCATION_OTHER, validator.STATUS_CONFIRMATION_REQUIRED,
     REQUEST_TRANSPORT_PERMIT),
    ('Missing land status confirm MH_PARK', False, '100413', LOCATION_PARK_2, validator.STATUS_CONFIRMATION_REQUIRED,
     REQUEST_TRANSPORT_PERMIT),
    ('MANUFACTURER no existing dealer', False, '100413', None, validator.MANUFACTURER_DEALER_INVALID,
     MANUFACTURER_GROUP),
    ('MANUFACTURER existing permit', False, '102303', None, validator.MANUFACTURER_PERMIT_INVALID, MANUFACTURER_GROUP),
    ('Valid MANUFACTURER', True, '100848', None, None, MANUFACTURER_GROUP)
]
# testdata pattern is ({mhr_number}, {name}, {count})
TEST_DATA_PERMIT_COUNT = [
    ('102303', 'CHAMPION CANADA INTERNATIONAL ULC', 2),
    ('102303', 'CHAMPION CANADA', 0),
    ('105618', 'ANYTHING', 0)
]
# testdata pattern is ({description}, {pid}, {valid}, {message_content})
TEST_DATA_PID = [
    ('Valid pid', '012684597', True, None),
    ('Invalid pid',  '888684597', False, validator_utils.LOCATION_PID_INVALID)
]


@pytest.mark.parametrize('desc,valid,staff,doc_id,message_content,status,group', TEST_PERMIT_DATA)
def test_validate_permit(session, desc, valid, staff, doc_id, message_content, status, group):
    """Assert that basic MH transport permit validation works as expected."""
    # setup
    mhr_num: str = '100413'
    account_id: str = 'PS12345'
    json_data = get_valid_registration()
    if staff and doc_id:
        json_data['documentId'] = doc_id
    elif json_data.get('documentId'):
        del json_data['documentId']
    if desc in ('Invalid FROZEN', 'Invalid staff FROZEN'):
        mhr_num = '003936'
        account_id = '2523'
    # current_app.logger.info(json_data)
    valid_format, errors = schema_utils.validate(json_data, 'permit', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    if status:
        registration.status_type = status
    error_msg = validator.validate_permit(registration, json_data, staff, group)
    if errors:
        for err in errors:
            current_app.logger.debug(err.message)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,mhr_num,location,message_content,group', TEST_PERMIT_DATA_EXTRA)
def test_validate_permit_extra(session, desc, valid, mhr_num, location, message_content, group):
    """Assert that extra MH transport permit validation works as expected."""
    # setup
    json_data = get_valid_registration()
    if desc.find('Valid MANUFACTURER') != -1 or desc.find('MANUFACTURER existing permit') != -1:
        json_data = copy.deepcopy(MANUFACTURER_PERMIT)
    if json_data.get('documentId'):
        del json_data['documentId']
    if location:
        json_data['newLocation'] = location
    if desc.find('Missing land status confirm OTHER') != -1:
        del json_data['landStatusConfirmation']
    elif desc.find('Missing land status confirm') != -1:
        json_data['landStatusConfirmation'] = False
    elif desc.find('Invalid existing location address') != -1:
        json_data['existingLocation']['address']['street'] = '9999 INVALID STREET.'
    elif desc.find('Invalid owner name') != -1:
        json_data['owner']['individualName']['last'] = 'INVALID'
    # current_app.logger.info(json_data)
    valid_format, errors = schema_utils.validate(json_data, 'permit', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, 'PS12345')
    error_msg = validator.validate_permit(registration, json_data, False, group)
    if errors:
        for err in errors:
            current_app.logger.debug(err.message)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,park_name,dealer,additional,except_plan,band_name,message_content', TEST_LOCATION_DATA)
def test_validate_location(session, desc, park_name, dealer, additional, except_plan, band_name, message_content):
    """Assert that location invalid character set validation works as expected."""
    # setup
    json_data = get_valid_registration()
    location = json_data.get('newLocation')
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
    error_msg = validator.validate_location(json_data)
    if message_content:
        assert error_msg.find(message_content) != -1
    else:
        assert not error_msg


@pytest.mark.parametrize('desc,pid,valid,message_content', TEST_DATA_PID)
def test_validate_pid(session, desc, pid, valid, message_content):
    """Assert that basic MH transport permit validation works as expected."""
    # setup
    json_data = get_valid_registration()
    if json_data.get('documentId'):
        del json_data['documentId']
    json_data['newLocation'] = copy.deepcopy(LOCATION_PID)
    json_data['newLocation']['pidNumber'] = pid
    # current_app.logger.info(json_data)
    valid_format, errors = schema_utils.validate(json_data, 'permit', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number('100413', 'PS12345')
    error_msg = validator.validate_permit(registration, json_data, False, STAFF_ROLE)
    # current_app.logger.info(f'$$$$$ {error_msg}')
    if errors:
        for err in errors:
            current_app.logger.debug(err.message)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('mhr_number,name,count', TEST_DATA_PERMIT_COUNT)
def test_permit_count(session, mhr_number, name, count):
    """Assert that counting existing permits for manufacturers works as expected."""
    permit_count: int = validator_utils.get_permit_count(mhr_number, name)
    assert permit_count == count


def get_valid_registration():
    """Build a valid registration"""
    json_data = copy.deepcopy(PERMIT)
    return json_data
