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

from mhr_api.utils import admin_validator as validator, validator_utils
from mhr_api.models import MhrRegistration, utils as model_utils
from mhr_api.models.type_tables import MhrDocumentTypes, MhrRegistrationStatusTypes
from mhr_api.services.authz import STAFF_ROLE


DOC_ID_EXISTS = 'UT000010'
DOC_ID_VALID = '63166035'
DOC_ID_INVALID_CHECKSUM = '63166034'
INVALID_TEXT_CHARSET = 'TEST \U0001d5c4\U0001d5c6/\U0001d5c1 INVALID'
INVALID_CHARSET_MESSAGE = 'The character set is not supported'
ADMIN_REGISTRATION = {
  'clientReferenceId': 'EX-TP001234',
  'attentionReference': 'JOHN SMITH',
  'documentType': 'NRED',
  'documentId': '62133670',
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
    'documentType': 'NRED',
    'documentId': '62133670',
    'remarks': 'REMARKS',
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


# testdata pattern is ({description}, {valid}, {doc_type}, {doc_id}, {mhr_num}, {account}, {message content})
TEST_REG_DATA = [
    ('Invalid missing submitting party', False, 'NRED', DOC_ID_VALID, '000914', 'PS12345',
     validator_utils.SUBMITTING_REQUIRED),
    ('Invalid FROZEN', False, 'NRED', DOC_ID_VALID, '000917', 'PS12345', validator_utils.STATE_NOT_ALLOWED),
    ('Invalid EXEMPT', False, 'NRED', DOC_ID_VALID, '000912', 'PS12345', validator_utils.STATE_NOT_ALLOWED),
    ('Invalid CANCELLED', False, 'NRED', DOC_ID_VALID, '000913', 'PS12345', validator_utils.STATE_NOT_ALLOWED),
    ('Invalid missing doc id', False, 'NRED', None, '000914', 'PS12345', validator.DOC_ID_REQUIRED),
    ('Invalid doc id checksum', False, 'NRED', DOC_ID_INVALID_CHECKSUM, '000914', 'PS12345',
     validator.DOC_ID_INVALID_CHECKSUM),
    ('Invalid doc id exists', False, 'NRED', DOC_ID_EXISTS, '000914', 'PS12345', validator.DOC_ID_EXISTS)
]


# test data pattern is ({description}, {valid}, {update_doc_id}, {mhr_num}, {account}, {message_content})
TEST_NOTE_DATA_NRED = [
    ('Valid TAXN', True, 'UT000020', '000914', 'PS12345', None),
    ('Invalid no doc id', False, None, '000914', 'PS12345', validator.UPDATE_DOCUMENT_ID_REQUIRED),
    ('Invalid status', False, 'UT000014', '000910', 'PS12345', validator.UPDATE_DOCUMENT_ID_STATUS),
    ('Invalid doc type REST', False, 'UT000022', '000915', 'PS12345', validator.NRED_INVALID_TYPE)
]
# test data pattern is ({description}, {valid}, {doc_type}, {notice}, {mhr_num}, {account}, {message_content})
TEST_NOTE_DATA_NOTICE = [
    ('Invalid required', False, 'NRED', None, '000914', 'PS12345', validator.NOTICE_REQUIRED),
    ('Invalid no name', False, 'NRED', NOTICE_NO_NAME, '000914', 'PS12345', validator.NOTICE_NAME_REQUIRED),
    ('Invalid person no address', False, 'NRED', NOTICE_NO_ADDRESS, '000914', 'PS12345',
     validator.NOTICE_ADDRESS_REQUIRED),
    ('Invalid business no address', False, 'NRED', NOTICE_NO_ADDRESS2, '000914', 'PS12345',
     validator.NOTICE_ADDRESS_REQUIRED)
]
# test data pattern is ({description}, {valid}, {update_doc_id}, {mhr_num}, {account}, {message_content})
TEST_DATA_EXRE = [
    ('Invalid FROZEN', False, None, '000917', 'PS12345', validator_utils.STATE_NOT_ALLOWED),
    ('Invalid ACTIVE', False, 'UT000020', '000914', 'PS12345', validator_utils.STATE_NOT_ALLOWED),
    ('Invalid CANCELLED', False, 'UT000018', '000913', 'PS12345', validator_utils.STATE_NOT_ALLOWED),
    ('Valid state', True, 'UT000023', '000912', 'PS12345', None),
    ('Valid no note', True, 'UT000023', '000912', 'PS12345', None)
]
# test data pattern is ({description}, {valid}, {update_doc_id}, {mhr_num}, {account}, {message_content})
TEST_NOTE_DATA_NCAN = [
    ('Valid REST', True, 'UT000022', '000915', 'PS12345', None),
    ('Invalid no doc id', False, None, '000915', 'PS12345', validator.NCAN_DOCUMENT_ID_REQUIRED),
    ('Invalid status', False, 'UT000011', '000909', 'PS12345', validator.NCAN_DOCUMENT_ID_STATUS),
    ('Invalid doc type TAXN', False, 'UT000020', '000914', 'PS12345', validator.NCAN_NOT_ALLOWED)
]


@pytest.mark.parametrize('desc,valid,update_doc_id,mhr_num,account,message_content', TEST_DATA_EXRE)
def test_validate_exre(session, desc, valid, update_doc_id, mhr_num, account, message_content):
    """Assert that EXRE document type validation works as expected."""
    # setup
    json_data = get_valid_registration()
    if update_doc_id:
        json_data['updateDocumentId'] = update_doc_id
    json_data['documentType'] = MhrDocumentTypes.EXRE
    if desc == 'Valid no note':
        del json_data['note']
    if json_data.get('note'):
        json_data['note']['documentType'] = MhrDocumentTypes.EXRE
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account)
    error_msg = validator.validate_admin_reg(registration, json_data)
    current_app.logger.debug(error_msg)
    if valid:
        assert error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,update_doc_id,mhr_num,account,message_content', TEST_NOTE_DATA_NRED)
def test_validate_nred(session, desc, valid, update_doc_id, mhr_num, account, message_content):
    """Assert that NRED document type validation works as expected."""
    # setup
    json_data = get_valid_registration()
    if update_doc_id:
        json_data['updateDocumentId'] = update_doc_id
    json_data['documentType'] = MhrDocumentTypes.NRED
    if json_data.get('note'):
        json_data['note']['documentType'] = MhrDocumentTypes.NRED
    registration: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, account)
    error_msg = validator.validate_admin_reg(registration, json_data)
    current_app.logger.debug(error_msg)
    if valid:
        assert error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,update_doc_id,mhr_num,account,message_content', TEST_NOTE_DATA_NCAN)
def test_validate_ncan(session, desc, valid, update_doc_id, mhr_num, account, message_content):
    """Assert that NCAN document type validation works as expected."""
    # setup
    json_data = get_valid_registration()
    if update_doc_id:
        json_data['updateDocumentId'] = update_doc_id
    json_data['documentType'] = MhrDocumentTypes.NCAN
    if json_data.get('note'):
        json_data['note']['documentType'] = MhrDocumentTypes.NCAN
    registration: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, account)
    error_msg = validator.validate_admin_reg(registration, json_data)
    current_app.logger.debug(error_msg)
    if valid:
        assert error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            if message_content == validator.NCAN_NOT_ALLOWED:
                msg: str = validator.NCAN_NOT_ALLOWED.format(doc_type='TAXN')
                assert error_msg.find(msg) != -1
            else:
                assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,doc_type,notice,mhr_num,account,message_content', TEST_NOTE_DATA_NOTICE)
def test_validate_note_notice(session, desc, valid, doc_type, notice, mhr_num, account, message_content):
    """Assert that note giving notice party validation works as expected."""
    # setup
    json_data = get_valid_registration()
    json_data['documentType'] = doc_type
    if mhr_num == '000914':
        json_data['updateDocumentId'] = 'UT000020'
    if json_data.get('note'):
        json_data['note']['documentType'] = doc_type
        if notice:
            json_data['note']['givingNoticeParty'] = notice
        else:
            del json_data['note']['givingNoticeParty']
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account)
    error_msg = validator.validate_admin_reg(registration, json_data)
    current_app.logger.debug(error_msg)
    if valid:
        assert error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,doc_type,doc_id,mhr_num,account,message_content', TEST_REG_DATA)
def test_validate_admin_reg(session, desc, valid, doc_type, doc_id, mhr_num, account, message_content):
    """Assert that basic admin registration validation works as expected."""
    # setup
    json_data = copy.deepcopy(ADMIN_REGISTRATION)
    if desc == 'Invalid missing submitting party':
        del json_data['submittingParty']
    if doc_id:
        json_data['documentId'] = doc_id
    else:
        del json_data['documentId']
    if mhr_num == '000914':
        json_data['updateDocumentId'] = 'UT000020'
    json_data['documentType'] = doc_type
    if json_data.get('note'):
        json_data['note']['documentType'] = doc_type
        del json_data['note']['documentId']

    registration: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, account)
    error_msg = validator.validate_admin_reg(registration, json_data)
    current_app.logger.debug(error_msg)
    if valid:
        assert error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


def get_valid_registration():
    """Build a valid registration"""
    json_data = copy.deepcopy(ADMIN_REGISTRATION)
    json_data['documentId'] = DOC_ID_VALID
    json_data['note']['documentId'] = DOC_ID_VALID
    return json_data
