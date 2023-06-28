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

from mhr_api.utils import note_validator as validator
from mhr_api.models import MhrRegistration, utils as model_utils
from mhr_api.services.authz import STAFF_ROLE


DOC_ID_EXISTS = '80038730'
DOC_ID_VALID = '63166035'
DOC_ID_INVALID_CHECKSUM = '63166034'
INVALID_TEXT_CHARSET = 'TEST \U0001d5c4\U0001d5c6/\U0001d5c1 INVALID'
INVALID_CHARSET_MESSAGE = 'The character set is not supported'
NOTE_REGISTRATION = {
  'clientReferenceId': 'EX-TP001234',
  'attentionReference': 'JOHN SMITH',
  'submittingParty': {
    'businessName': 'BOB PATERSON HOMES INC.',
    'address': {
      'street': '1200 S. MACKENZIE AVE.',
      'city': 'WILLIAMS LAKE',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V2G 3Y1'
    },
    'phoneNumber': '6044620279'
  },
  'note': {
    'documentType': 'CAU',
    'documentId': '62133670',
    'effectiveDateTime': '2023-02-21T18:56:00+00:00',
    'remarks': 'NOTICE OF ACTION COMMENCED MARCH 1 2022 WITH CRANBROOK COURT REGISTRY COURT FILE NO. 3011.',
    'givingNoticeParty': {
      'personName': {
        'first': 'JOHNNY',
        'middle': 'B',
        'last': 'SMITH'
      },
      'address': {
        'street': '222 SUMMER STREET',
        'city': 'VICTORIA',
        'region': 'BC',
        'country': 'CA',
        'postalCode': 'V8W 2V8'
      },
      'phoneNumber': '2504930122'
    }
  }
}
NOTICE_VALID = {
      'personName': {
        'first': 'JOHNNY',
        'middle': 'B',
        'last': 'SMITH'
      },
      'address': {
        'street': '222 SUMMER STREET',
        'city': 'VICTORIA',
        'region': 'BC',
        'country': 'CA',
        'postalCode': 'V8W 2V8'
      },
      'phoneNumber': '2504930122'
}
NOTICE_NO_NAME = {
    'address': {
        'street': '222 SUMMER STREET',
        'city': 'VICTORIA',
        'region': 'BC',
        'country': 'CA',
        'postalCode': 'V8W 2V8'
    }
}
NOTICE_NO_ADDRESS = {
    'personName': {
        'first': 'JOHNNY',
        'middle': 'B',
        'last': 'SMITH'
    }
}
NOTICE_NO_ADDRESS2 = {
    'businessName': 'SMITH'
}

# test data pattern is ({description}, {valid}, {doc_type}, {ts_offset}, {mhr_num}, {account}, {message_content})
TEST_NOTE_DATA_EFFECTIVE = [
    ('Invalid future', False, 'CAU', 30, '102876', 'ppr_staff', validator.EFFECTIVE_FUTURE),
    ('Valid past', True, 'CAUE', -30, '080104', 'ppr_staff', None),
    ('Valid no effective', True, 'CAUC', None, '080104', 'ppr_staff', None),
    ('Invalid past', False, 'REGC', -30, '102876', 'ppr_staff', validator.EFFECTIVE_PAST),
    ('Invalid not allowed', False, 'NCAN', -1, '102876', 'ppr_staff', validator.EFFECTIVE_NOT_ALLOWED)
]
# test data pattern is ({description}, {valid}, {doc_type}, {ts_offset}, {mhr_num}, {account}, {message_content})
TEST_NOTE_DATA_EXPIRY = [
    ('Invalid doc type', False, 'CAU', -30, '102876', 'ppr_staff', validator.EXPIRY_NOT_ALLOWED),
    ('Valid CAUC no expiry', True, 'CAUC', None, '080104', 'ppr_staff', None),
    ('Invalid past', False, 'CAUE', -30, '080104', 'ppr_staff', validator.EXPIRY_PAST),
    ('Invalid required', False, 'CAUE', None, '080104', 'ppr_staff', validator.EXPIRY_REQUIRED),
    ('Invalid before current', False, 'CAUE', +1, '080104', 'ppr_staff', validator.EXPIRY_BEFORE_CURRENT),
    ('Valid expiry elapsed', True, 'CAUE', +1, '046315', 'ppr_staff', None)
]
# test data pattern is ({description}, {valid}, {doc_type}, {remarks}, {mhr_num}, {account}, {message_content})
TEST_NOTE_DATA_REMARKS = [
    ('Invalid required', False, 'CAU', None, '102876', 'ppr_staff', validator.REMARKS_REQUIRED),
    ('Invalid not allowed', False, 'NCAN', 'REMARKS', '102876', 'ppr_staff', validator.REMARKS_NOT_ALLOWED),
    ('Valid optional', True, 'NPUB', None, '102876', 'ppr_staff', None)
]
# test data pattern is ({description}, {valid}, {doc_type}, {notice}, {mhr_num}, {account}, {message_content})
TEST_NOTE_DATA_NOTICE = [
    ('Invalid required', False, 'REST', None, '102876', 'ppr_staff', validator.NOTICE_REQUIRED),
    ('Invalid no name', False, 'NCAN', NOTICE_NO_NAME, '102876', 'ppr_staff', validator.NOTICE_NAME_REQUIRED),
    ('Invalid person no address', False, 'NCAN', NOTICE_NO_ADDRESS, '102876', 'ppr_staff',
     validator.NOTICE_ADDRESS_REQUIRED),
    ('Invalid business no address', False, 'NCAN', NOTICE_NO_ADDRESS2, '102876', 'ppr_staff',
     validator.NOTICE_ADDRESS_REQUIRED),
    ('Valid optional', True, 'NPUB', None, '102876', 'ppr_staff', None),
    ('Valid', True, 'TAXN', NOTICE_VALID, '102876', 'ppr_staff', None)
]


@pytest.mark.parametrize('desc,valid,doc_type,ts_offset,mhr_num,account,message_content', TEST_NOTE_DATA_EFFECTIVE)
def test_validate_effective_ts(session, desc, valid, doc_type, ts_offset, mhr_num, account, message_content):
    """Assert that effective date time validation works as expected."""
    # setup
    json_data = get_valid_registration()
    json_data['note']['documentType'] = doc_type
    if not ts_offset:
        del json_data['note']['effectiveDateTime']
    elif ts_offset != 0:
        effective_ts = model_utils.now_ts_offset(ts_offset, True)
        json_data['note']['effectiveDateTime'] = model_utils.format_ts(effective_ts)
        # current_app.logger.debug(json_data['note']['effectiveDateTime'])
    if doc_type == 'CAUE':
        expiry_ts = model_utils.now_ts_offset(3000, True)
        json_data['note']['expiryDateTime'] = model_utils.format_ts(expiry_ts)
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account)
    valid_format, errors = schema_utils.validate(json_data, 'noteRegistration', 'mhr')
    error_msg = validator.validate_note(registration, json_data, True, STAFF_ROLE)
    # current_app.logger.debug(error_msg)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            err_msg:str = message_content
            if desc == 'Invalid past':
                err_msg = validator.EFFECTIVE_PAST.format(doc_type=doc_type)
            elif desc == 'Invalid not allowed':
                err_msg = validator.EFFECTIVE_NOT_ALLOWED.format(doc_type=doc_type)
            assert error_msg.find(err_msg) != -1


@pytest.mark.parametrize('desc,valid,doc_type,ts_offset,mhr_num,account,message_content', TEST_NOTE_DATA_EXPIRY)
def test_validate_expiry_ts(session, desc, valid, doc_type, ts_offset, mhr_num, account, message_content):
    """Assert that expiry date time validation works as expected."""
    # setup
    json_data = get_valid_registration()
    json_data['note']['documentType'] = doc_type
    effective_ts = model_utils.now_ts_offset(-30, True)
    json_data['note']['effectiveDateTime'] = model_utils.format_ts(effective_ts)
    if ts_offset:
        expiry_ts = model_utils.now_ts_offset(ts_offset, True)
        json_data['note']['expiryDateTime'] = model_utils.format_ts(expiry_ts)
        # current_app.logger.debug(json_data['note']['effectiveDateTime'])
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account)
    valid_format, errors = schema_utils.validate(json_data, 'noteRegistration', 'mhr')
    error_msg = validator.validate_note(registration, json_data, True, STAFF_ROLE)
    current_app.logger.debug(error_msg)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,doc_type,remarks,mhr_num,account,message_content', TEST_NOTE_DATA_REMARKS)
def test_validate_remarks(session, desc, valid, doc_type, remarks, mhr_num, account, message_content):
    """Assert that remarks validation works as expected."""
    # setup
    json_data = get_valid_registration()
    json_data['note']['documentType'] = doc_type
    if remarks:
        json_data['note']['remarks'] = remarks
    else:
        del json_data['note']['remarks']
    del json_data['note']['effectiveDateTime']
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account)
    error_msg = validator.validate_note(registration, json_data, True, STAFF_ROLE)
    current_app.logger.debug(error_msg)
    if valid:
        assert error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,doc_type,notice,mhr_num,account,message_content', TEST_NOTE_DATA_NOTICE)
def test_validate_notice(session, desc, valid, doc_type, notice, mhr_num, account, message_content):
    """Assert that giving notice party validation works as expected."""
    # setup
    json_data = get_valid_registration()
    json_data['note']['documentType'] = doc_type
    if notice:
        json_data['note']['givingNoticeParty'] = notice
    else:
        del json_data['note']['givingNoticeParty']
    del json_data['note']['effectiveDateTime']
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account)
    error_msg = validator.validate_note(registration, json_data, True, STAFF_ROLE)
    current_app.logger.debug(error_msg)
    if valid:
        assert error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


def get_valid_registration():
    """Build a valid registration"""
    json_data = copy.deepcopy(NOTE_REGISTRATION)
    json_data['note']['documentId'] = DOC_ID_VALID
    return json_data
