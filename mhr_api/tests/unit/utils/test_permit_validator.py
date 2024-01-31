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
from mhr_api.models import MhrRegistration, utils as model_utils
from mhr_api.services.authz import (
    REQUEST_TRANSPORT_PERMIT,
    STAFF_ROLE,
    MANUFACTURER_GROUP,
    DEALERSHIP_GROUP,
    QUALIFIED_USER_GROUP
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
PERMIT = {
  'documentId': '80035947',
  'clientReferenceId': 'EX-TP001234',
  'submittingParty': {
    'businessName': 'SUBMITTING',
    'address': {
      'street': '1234 TEST-0001',
      'city': 'CITY',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V8R 3A5'
    },
    'phoneNumber': '2505058308'
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
    'businessName': 'REAL ENGINEERED HOMES INC',
    'address': {
      'street': '1234 TEST-0027',
      'city': 'CITY',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V8R 3A5'
    },
    'phoneNumber': '2507660588'
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
MANUFACTURER_PERMIT_VALID = {
  'documentId': '80035947',
  'clientReferenceId': 'EX-TP001234',
  'submittingParty': {
    'businessName': 'REAL ENGINEERED HOMES INC',
    'address': {
      'street': '1234 TEST-0028',
      'city': 'CITY',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V8R 3A5'
    },
    'phoneNumber': '2507660588'
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
LOCATION_000931 = {
    'additionalDescription': 'additional', 
    'address': {
      'city': 'CITY', 
      'country': 'CA', 
      'postalCode': 'V8R 3A5', 
      'region': 'BC', 
      'street': '1234 TEST-0032'
    }, 
    'leaveProvince': False, 
    'locationId': 200000046, 
    'locationType': 'OTHER', 
    'status': 'ACTIVE', 
    'taxCertificate': True, 
    'taxExpiryDate': '2023-10-16T19:04:59+00:00'
}
LOCATION_OTHER = {
    'additionalDescription': 'additional other', 
    'lot': '24',
    'plan': '16',
    'landDistrict': 'CARIBOU',
    'address': {
      'city': 'CITY', 
      'country': 'CA', 
      'postalCode': 'V8R 3A5', 
      'region': 'BC', 
      'street': '1234 TEST-0032 OTHER'
    }, 
    'leaveProvince': False, 
    'locationType': 'OTHER', 
    'status': 'ACTIVE', 
    'taxCertificate': True, 
    'taxExpiryDate': '2035-10-16T19:04:59+00:00'
}

# testdata pattern is ({description}, {park_name}, {dealer}, {additional}, {except_plan}, {band_name}, {message content})
TEST_LOCATION_DATA = [
    ('Non utf-8 park name', INVALID_TEXT_CHARSET, None, None, None, None, None),
    ('Non utf-8 dealer name', None, INVALID_TEXT_CHARSET, None, None, None, None),
    ('Non utf-8 additional description', None, None, INVALID_TEXT_CHARSET, None, None, None),
    ('Non utf-8 exception plan', None, None, None, INVALID_TEXT_CHARSET, None, None),
    ('Non utf-8 band name', None, None, None, None, INVALID_TEXT_CHARSET, None)
]
# test data pattern is ({description}, {valid}, {staff}, {doc_id}, {message_content}, {mhr_num}, {account}, {group})
TEST_PERMIT_DATA = [
    (DESC_VALID, True, True, DOC_ID_VALID, None, '000900', 'PS12345', STAFF_ROLE),
    ('Valid no doc id not staff', True, False, None, None, '000900', 'PS12345', REQUEST_TRANSPORT_PERMIT),
    ('Invalid no doc id staff', False, True, None, validator_utils.DOC_ID_REQUIRED, '000900', 'PS12345', STAFF_ROLE),
    ('Invalid FROZEN', False, False, None, validator_utils.STATE_NOT_ALLOWED, '000917', 'PS12345',
     REQUEST_TRANSPORT_PERMIT),
    ('Invalid FROZEN TAXN', False, False, None, validator_utils.STATE_FROZEN_NOTE, '000914', 'PS12345',
     REQUEST_TRANSPORT_PERMIT),
    ('Invalid FROZEN REST', False, False, None, validator_utils.STATE_FROZEN_NOTE, '000915', 'PS12345',
     REQUEST_TRANSPORT_PERMIT),
    ('Invalid FROZEN NCON', False, False, None, validator_utils.STATE_FROZEN_NOTE, '000918', 'PS12345',
     REQUEST_TRANSPORT_PERMIT),
    ('Invalid staff FROZEN', False, True, DOC_ID_VALID, validator_utils.STATE_FROZEN_AFFIDAVIT, '000917', 'PS12345',
     STAFF_ROLE),
    ('Invalid EXEMPT', False, False, DOC_ID_VALID, validator_utils.STATE_NOT_ALLOWED, '000912', 'PS12345', STAFF_ROLE),
    ('Invalid CANCELLED', False, False, None, validator_utils.STATE_NOT_ALLOWED, '000913', 'PS12345',
     REQUEST_TRANSPORT_PERMIT)
]
# testdata pattern is ({description}, {valid}, {mhr_num}, {location}, {message content}, {group})
TEST_PERMIT_DATA_EXTRA = [
    ('Valid location no tax cert', True, '000900', LOCATION_PARK, None, REQUEST_TRANSPORT_PERMIT),
    ('Valid existing active PERMIT', True, '000931', None, None, REQUEST_TRANSPORT_PERMIT),
    ('Invalid MANUFACTURER no dealer', False, '000900', LOCATION_MANUFACTURER_NO_DEALER,
     validator_utils.LOCATION_DEALER_REQUIRED, REQUEST_TRANSPORT_PERMIT),
    ('Invalid MH_PARK no name', False, '000900', LOCATION_PARK_NO_NAME, validator_utils.LOCATION_PARK_NAME_REQUIRED,
     REQUEST_TRANSPORT_PERMIT),
    ('Invalid location RESERVE no tax cert', False, '000919', LOCATION_RESERVE,
     validator_utils.LOCATION_TAX_CERT_REQUIRED,
     REQUEST_TRANSPORT_PERMIT),
    ('Invalid location tax cert date', False, '000900', LOCATION_TAX_INVALID,
     validator_utils.LOCATION_TAX_DATE_INVALID,
     REQUEST_TRANSPORT_PERMIT),
    ('Missing location tax cert', False, '000919', LOCATION_TAX_MISSING,
     validator_utils.LOCATION_TAX_CERT_REQUIRED,
     REQUEST_TRANSPORT_PERMIT),
    ('Missing land status confirm OTHER', False, '000900', LOCATION_OTHER,
     validator_utils.STATUS_CONFIRMATION_REQUIRED,
     REQUEST_TRANSPORT_PERMIT),
    ('Missing land status confirm MH_PARK', False, '000900', LOCATION_PARK_2,
     validator_utils.STATUS_CONFIRMATION_REQUIRED,
     REQUEST_TRANSPORT_PERMIT),
    ('MANUFACTURER no existing lot', False, '000919', None, validator.MANUFACTURER_DEALER_INVALID,
     MANUFACTURER_GROUP),
    ('MANUFACTURER existing permit', False, '000926', None, validator.MANUFACTURER_PERMIT_INVALID, MANUFACTURER_GROUP),
    ('Valid MANUFACTURER', True, '000927', None, None, MANUFACTURER_GROUP),
    ('Valid DEALER', True, '000927', None, None, DEALERSHIP_GROUP),
    ('DEALER no existing lot', False, '000919', None, validator.MANUFACTURER_DEALER_INVALID, DEALERSHIP_GROUP),
    ('Invalid identical location', False, '000931', LOCATION_000931, validator_utils.LOCATION_INVALID_IDENTICAL,
     REQUEST_TRANSPORT_PERMIT)
]
# testdata pattern is ({mhr_number}, {name}, {count})
TEST_DATA_PERMIT_COUNT = [
    ('000926', 'REAL ENGINEERED HOMES INC', 1),
    ('000926', 'REAL ENGINEERED', 0),
    ('000900', 'ANYTHING', 0)
]
# testdata pattern is ({description}, {pid}, {valid}, {message_content})
TEST_DATA_PID = [
    ('Valid pid', '012684597', True, None),
    ('Invalid pid',  '888684597', False, validator_utils.LOCATION_PID_INVALID)
]
# test data pattern is ({description}, {valid}, {staff}, {message_content}, {mhr_num}, {account}, {group})
TEST_AMEND_PERMIT_DATA = [
    ('Valid staff', True, True, None, '000931', 'PS12345', STAFF_ROLE),
    ('Valid non-staff', True, False, None, '000931', 'PS12345', QUALIFIED_USER_GROUP),
    ('Invalid no permit', False, True, validator.AMEND_PERMIT_INVALID, '000900', 'PS12345', STAFF_ROLE),
    ('Invalid permit expired', False, True, validator.AMEND_PERMIT_INVALID, '000930', 'PS12345', STAFF_ROLE),
    ('Invalid QS location change', False, False, validator.AMEND_LOCATION_TYPE_QS, '000931', 'PS12345',
     DEALERSHIP_GROUP)
]
# test data pattern is ({description}, {valid}, {staff}, {add_days}, {message_content}, {mhr_num}, {account}, {group})
TEST_EXPIRY_DATE_DATA = [
    ('Valid staff future year', True, True, 365, None, '000900', 'PS12345', STAFF_ROLE),
    ('Invalid non-staff future year', False, False, 365, validator_utils.LOCATION_TAX_DATE_INVALID_QS, '000900',
     'PS12345', REQUEST_TRANSPORT_PERMIT),
    ('Invalid staff past', False, True, -1, validator_utils.LOCATION_TAX_DATE_INVALID, '000900', 'PS12345', STAFF_ROLE),
    ('Invalid non-staff past', False, False, -1, validator_utils.LOCATION_TAX_DATE_INVALID, '000900',
     'PS12345', REQUEST_TRANSPORT_PERMIT)
]


@pytest.mark.parametrize('desc,valid,staff,doc_id,message_content,mhr_num,account,group', TEST_PERMIT_DATA)
def test_validate_permit(session, desc, valid, staff, doc_id, message_content, mhr_num, account, group):
    """Assert that basic MH transport permit validation works as expected."""
    # setup
    json_data = get_valid_registration()
    if doc_id:
        json_data['documentId'] = doc_id
    else:
        del json_data['documentId']
    if valid and json_data['newLocation'].get('taxExpiryDate'):
        json_data['newLocation']['taxExpiryDate'] = get_valid_tax_cert_dt()
    # current_app.logger.info(json_data)
    valid_format, errors = schema_utils.validate(json_data, 'permit', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, account)
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


@pytest.mark.parametrize('desc,valid,staff,message_content,mhr_num,account,group', TEST_AMEND_PERMIT_DATA)
def test_validate_amend_permit(session, desc, valid, staff, message_content, mhr_num, account, group):
    """Assert that amend MH transport permit validation works as expected."""
    # setup
    json_data = get_valid_registration()
    json_data['documentId'] = DOC_ID_VALID
    json_data['amendment'] = True
    if desc == 'Invalid QS location change':
        json_data['newLocation'] = LOCATION_RESERVE
    elif desc == 'Valid non-staff':
        json_data['newLocation'] = LOCATION_OTHER
    if valid and json_data['newLocation'].get('taxExpiryDate'):
        json_data['newLocation']['taxExpiryDate'] = get_valid_tax_cert_dt()
    # current_app.logger.info(json_data)
    valid_format, errors = schema_utils.validate(json_data, 'permit', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, account)
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
    if desc.find('Valid MANUFACTURER') != -1:
        json_data = copy.deepcopy(MANUFACTURER_PERMIT_VALID)
    elif desc.find('MANUFACTURER existing permit') != -1:
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
        json_data['owner']['organizationName'] = 'INVALID'
    if valid and json_data['newLocation'].get('taxExpiryDate'):
        json_data['newLocation']['taxExpiryDate'] = get_valid_tax_cert_dt()
    # current_app.logger.info(json_data)
    valid_format, errors = schema_utils.validate(json_data, 'permit', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, 'PS12345')
    if desc == 'Invalid identical location':
        registration.current_view = True
        reg_json = registration.new_registration_json
        if reg_json['location'].get('taxExpiryDate'):
            json_data['newLocation']['taxExpiryDate'] = reg_json['location'].get('taxExpiryDate')

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
    error_msg = validator_utils.validate_location(json_data)
    if message_content:
        assert error_msg.find(message_content) != -1
    else:
        assert not error_msg


@pytest.mark.parametrize('desc,pid,valid,message_content', TEST_DATA_PID)
def test_validate_pid(session, desc, pid, valid, message_content):
    """Assert that basic MH transport permit validation works as expected."""
    # setup
    json_data = get_valid_registration()
    json_data['newLocation'] = copy.deepcopy(LOCATION_PID)
    json_data['newLocation']['pidNumber'] = pid
    json_data['newLocation']['taxExpiryDate'] = get_valid_tax_cert_dt()
    # current_app.logger.info(json_data)
    valid_format, errors = schema_utils.validate(json_data, 'permit', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number('000900', 'PS12345')
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


@pytest.mark.parametrize('desc,valid,staff,add_days,message_content,mhr_num,account,group', TEST_EXPIRY_DATE_DATA)
def test_validate_expiry_date(session, desc, valid, staff, add_days, message_content, mhr_num, account, group):
    """Assert that location tax expiry date validation works as expected."""
    # setup
    json_data = get_valid_registration()
    if staff:
        json_data['documentId'] = DOC_ID_VALID
    else:
        del json_data['documentId']
    if add_days:
        test_ts = model_utils.now_ts_offset(add_days, True)
        json_data['newLocation']['taxExpiryDate'] = model_utils.format_ts(test_ts)
    # current_app.logger.info(json_data)
    valid_format, errors = schema_utils.validate(json_data, 'permit', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, account)
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


def get_valid_registration():
    """Build a valid registration"""
    json_data = copy.deepcopy(PERMIT)
    json_data['documentId'] = DOC_ID_VALID
    return json_data


def get_valid_tax_cert_dt() -> str:
    """Create a valid tax certificate expiry date in the ISO format."""
    now = model_utils.now_ts()
    return model_utils.format_ts(now)
