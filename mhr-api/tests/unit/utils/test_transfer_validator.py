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
"""Transfer registration validator tests."""
import copy

from flask import current_app
import pytest
from registry_schemas import utils as schema_utils
from registry_schemas.example_data.mhr import TRANSFER

from mhr_api.utils import registration_validator as validator, validator_utils, validator_owner_utils as val_owner_utils
from mhr_api.models import MhrRegistration, utils as model_utils, MhrQualifiedSupplier
from mhr_api.models.type_tables import MhrRegistrationStatusTypes, MhrTenancyTypes, MhrRegistrationTypes
from mhr_api.models.type_tables import MhrPartyTypes
from mhr_api.services.authz import STAFF_ROLE, QUALIFIED_USER_GROUP, DEALERSHIP_GROUP
from tests.unit.utils.test_transfer_data import (
    SO_OWNER_MULTIPLE,
    SO_GROUP_MULTIPLE,
    JT_OWNER_SINGLE,
    TC_GROUPS_VALID,
    TC_GROUP_TRANSFER_DELETE,
    TC_GROUP_TRANSFER_ADD,
    TC_GROUP_TRANSFER_ADD2,
    TC_GROUP_TRANSFER_DELETE_2,
    TRAND_DELETE_GROUPS,
    TRAND_ADD_GROUPS, TRAND_ADD_GROUPS_JOINT,
    TRAND_DELETE_GROUPS2,
    TRAND_ADD_GROUPS2,
    EXEC_DELETE_GROUPS,
    EXEC_ADD_GROUPS,
    EXEC_ADD_GROUPS_INVALID,
    WILL_DELETE_GROUPS,
    WILL_DELETE_GROUPS1,
    WILL_DELETE_GROUPS2,
    WILL_DELETE_GROUPS3,
    ADMIN_ADD_GROUPS,
    ADMIN_DELETE_GROUPS,
    ADMIN_DELETE_GROUPS1,
    ADD_OWNER,
    SO_GROUP,
    ADD_GROUP,
    TRANS_QS_1,
    TRANS_QS_2,
    TRANS_QS_3,
    TRANS_QS_4,
    TRANS_TC_3,
    TRANS_TC_4,
    TRANS_TC_5,
    TRANS_TC_6
)
DESC_VALID = 'Valid'
DESC_MISSING_DOC_ID = 'Missing document id'
DESC_MISSING_SUBMITTING = 'Missing submitting party'
DESC_MISSING_OWNER_GROUP = 'Missing owner group'
DESC_DOC_ID_EXISTS = 'Invalid document id exists'
DESC_INVALID_GROUP_ID = 'Invalid delete owner group id'
DESC_INVALID_GROUP_TYPE = 'Invalid delete owner group type'
DESC_NONEXISTENT_GROUP_ID = 'Invalid nonexistent delete owner group id'
# DOC_ID_EXISTS = '80038730'
DOC_ID_EXISTS = 'UT000010'
DOC_ID_VALID = '63166035'
DOC_ID_INVALID_CHECKSUM = '63166034'

# testdata pattern is ({description}, {valid}, {staff}, {doc_id}, {message content}, {status})
TEST_TRANSFER_DATA = [
    (DESC_VALID, True, True, DOC_ID_VALID, None, MhrRegistrationStatusTypes.ACTIVE),
    ('Valid staff FROZEN', True, True, DOC_ID_VALID, None, MhrRegistrationStatusTypes.ACTIVE),
    ('Valid no doc id not staff', True, False, None, None, None),
    ('Invalid EXEMPT', False, False, None, validator_utils.STATE_NOT_ALLOWED, MhrRegistrationStatusTypes.EXEMPT),
    ('Invalid CANCELLED', False, False, None, validator_utils.STATE_NOT_ALLOWED, MhrRegistrationStatusTypes.HISTORICAL),
    ('Invalid FROZEN', False, False, None, validator_utils.STATE_NOT_ALLOWED, MhrRegistrationStatusTypes.ACTIVE),
    ('Invalid FROZEN TAXN', False, False, None, validator_utils.STATE_FROZEN_NOTE, MhrRegistrationStatusTypes.ACTIVE),
    ('Invalid FROZEN REST', False, False, None, validator_utils.STATE_FROZEN_NOTE, MhrRegistrationStatusTypes.ACTIVE),
    ('Invalid FROZEN NCON', False, False, None, validator_utils.STATE_FROZEN_NOTE, MhrRegistrationStatusTypes.ACTIVE),
    #('Invalid draft', False, False, None, validator_utils.DRAFT_NOT_ALLOWED, MhrRegistrationStatusTypes.ACTIVE),
    # (DESC_INVALID_GROUP_ID, False, False, None, validator_utils.DELETE_GROUP_ID_INVALID,
    # MhrRegistrationStatusTypes.ACTIVE),
    (DESC_NONEXISTENT_GROUP_ID, False, False, None, val_owner_utils.DELETE_GROUP_ID_NONEXISTENT,
     MhrRegistrationStatusTypes.ACTIVE),
    (DESC_INVALID_GROUP_TYPE, False, False, None, val_owner_utils.DELETE_GROUP_TYPE_INVALID,
     MhrRegistrationStatusTypes.ACTIVE)
]
# testdata pattern is ({description}, {valid}, {staff}, {tran_dt}, {dec_val}, {consideration}, {message content})
TEST_TRANSFER_DATA_EXTRA = [
    ('Valid staff exists', True, True, True, True, True, None),
    ('Valid staff missing', True, True, False, False, False, None),
    ('Valid non-staff exists', True, False, True, True, True, None),
    ('Invalid non-staff missing transfer date', False, False, False, True, True, validator.TRANSFER_DATE_REQUIRED),
    ('Invalid non-staff future transfer date', False, False, True, True, True, validator.TRANSFER_DATE_FUTURE),
    ('Invalid non-staff missing declared value', False, False, True, False, True, validator.DECLARED_VALUE_REQUIRED),
    ('Invalid non-staff missing consideration', False, False, True, True, False, validator.CONSIDERATION_REQUIRED)
]
# testdata pattern is ({description}, {valid}, {numerator}, {denominator}, {add_group}, {message content})
TEST_TRANSFER_DATA_GROUP = [
    ('Valid', True, 1, 2, None, None),
    ('Invalid add TC no owner', False, None, None, TC_GROUP_TRANSFER_ADD2, val_owner_utils.OWNERS_COMMON_INVALID),
    ('Invalid add JT 1 owner', False, None, None, JT_OWNER_SINGLE, val_owner_utils.OWNERS_JOINT_INVALID),
    ('Invalid TC numerator missing', False, None, 2, TC_GROUPS_VALID, val_owner_utils.GROUP_NUMERATOR_MISSING),
    ('Invalid TC numerator < 1', False, 0, 2, TC_GROUPS_VALID, val_owner_utils.GROUP_NUMERATOR_MISSING),
    ('Invalid TC denominator missing', False, 1, None, TC_GROUPS_VALID, val_owner_utils.GROUP_DENOMINATOR_MISSING),
    ('Invalid TC denominator < 1', False, 1, 0, TC_GROUPS_VALID, val_owner_utils.GROUP_DENOMINATOR_MISSING),
    ('Invalid add SO 2 groups', False, None, None, SO_GROUP_MULTIPLE, val_owner_utils.ADD_SOLE_OWNER_INVALID),
    ('Invalid add SO 2 owners', False, None, None, SO_OWNER_MULTIPLE, val_owner_utils.ADD_SOLE_OWNER_INVALID),
#    ('Invalid add TC > 1 owner', False, None, None, TC_GROUP_TRANSFER_ADD, validator.OWNERS_COMMON_INVALID)
]
# testdata pattern is ({description},{valid},{mhr_num},{account_id},{delete_groups},{add_groups},{message content})
TEST_TRANSFER_DATA_TRAND = [
    ('Valid', True,  '000920', 'PS12345', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS, None),
    ('Valid no transfer date', True,  '000920', 'PS12345', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS, None),
    ('Valid no consideration', True,  '000920', 'PS12345', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS, None),
    ('Valid with no/empty middle name', True,  '000921', 'PS12345', TRAND_DELETE_GROUPS2, TRAND_ADD_GROUPS2, None),
    ('Invalid FROZEN', False,  '000917', 'PS12345', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     validator_utils.STATE_NOT_ALLOWED),
    ('Invalid staff FROZEN', False,  '000917', 'PS12345', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     validator_utils.STATE_FROZEN_AFFIDAVIT),
    ('Invalid party type', False,  '000920', 'PS12345', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     validator.TRAN_DEATH_NEW_OWNER),
    ('Invalid add owner', False,  '000920', 'PS12345', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     validator.TRAN_DEATH_ADD_OWNER),
    ('Invalid no cert number', False,  '000920', 'PS12345', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     validator.TRAN_DEATH_CERT_MISSING),
    ('Invalid no corp number', False,  '000920', 'PS12345', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     validator.TRAN_DEATH_CORP_NUM_MISSING),
    ('Invalid no death ts', False,  '000920', 'PS12345', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     validator.TRAN_DEATH_DATE_MISSING),
    ('Invalid tenancy type', False,  '000920', 'PS12345', SO_GROUP, TRAND_ADD_GROUPS,
     validator.TRAN_DEATH_JOINT_TYPE),
    ('Invalid add 2 groups', False,  '000920', 'PS12345', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     val_owner_utils.TRAN_DEATH_GROUP_COUNT),
    ('Invalid delete 2 groups', False,  '000920', 'PS12345', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     val_owner_utils.TRAN_DEATH_GROUP_COUNT),
    ('Invalid future death ts', False,  '000920', 'PS12345', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     validator.TRAN_DEATH_DATE_INVALID),
    ('Valid JOINT BUS non-QS', False,  '000920', 'PS12345', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS_JOINT, None),
    ('Invalid JOINT BUS QS', False,  '000920', 'PS12345', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS_JOINT,
     validator.TRAN_DEATH_QS_JOINT),
    ('Invalid JOINT BUS QS DELETE', False,  '000900', 'PS12345', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS_JOINT,
     validator.TRAN_DEATH_QS_JOINT_REMOVE)
]

# testdata pattern is ({description},{valid},{mhr_num},{account_id},{delete_groups},{add_groups},{message content},{staff})
TEST_TRANSFER_DATA_ADMIN = [
    ('Valid', True,  '000921', 'PS12345', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS, None, True),
    ('Valid delete ADMIN', True,  '000922', 'PS12345', ADMIN_DELETE_GROUPS1, ADMIN_ADD_GROUPS, None, True),
    ('Invalid non-staff', False,  '000921', 'PS12345', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS,
     validator.REG_STAFF_ONLY, False),
    ('Valid party type EXECUTOR', True,  '000921', 'PS12345', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS, None, True),
    ('Valid party type TRUSTEE', True,  '000921', 'PS12345', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS, None, True),
    ('Valid party type ADMINISTRATOR', True,  '000921', 'PS12345', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS, None, True),
    ('Invalid party type add', False,  '000921', 'PS12345', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS,
     validator.TRAN_ADMIN_NEW_OWNER, True),
    ('Invalid administrator missing', False,  '000921', 'PS12345', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS,
     validator.TRAN_ADMIN_NEW_OWNER, True),
    ('Invalid no grant', False,  '000921', 'PS12345', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS,
     validator.TRAN_ADMIN_GRANT, True),
    ('Invalid no death info', False,  '000921', 'PS12345', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS,
     validator.TRAN_ADMIN_DEATH_CERT, True),
    ('Invalid add 2 groups', False,  '000921', 'PS12345', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS,
     val_owner_utils.TRAN_DEATH_GROUP_COUNT, True),
    ('Invalid delete 2 groups', False,  '000921', 'PS12345', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS,
     val_owner_utils.TRAN_DEATH_GROUP_COUNT, True)
]
# testdata pattern is ({description},{valid},{mhr_num},{account_id},{delete_groups},{add_groups},{message content},{staff})
TEST_TRANSFER_DATA_AFFIDAVIT = [
    ('Valid', True,  '000921', 'PS12345', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS, None, True),
    ('Invalid non-staff', False,  '000921', 'PS12345', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.REG_STAFF_ONLY, False),
    ('Valid party type EXECUTOR', True,  '000921', 'PS12345', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS, None, True),
    ('Valid party type TRUSTEE', True,  '000921', 'PS12345', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS, None, True),
    ('Valid party type ADMINISTRATOR', True,  '000921', 'PS12345', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS, None, True),
    ('Invalid party type add', False,  '000921', 'PS12345', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_AFFIDAVIT_NEW_OWNER, True),
    ('Invalid declared value', False,  '000921', 'PS12345', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_AFFIDAVIT_DECLARED_VALUE, True),
    ('Invalid executor missing', False,  '000921', 'PS12345', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS_INVALID,
     validator.TRAN_AFFIDAVIT_NEW_OWNER, True),
    ('Invalid no death info', False,  '000921', 'PS12345', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_EXEC_DEATH_CERT, True),
    ('Invalid no death cert number', False,  '000921', 'PS12345', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_DEATH_CERT_MISSING, True),
    ('Invalid no death corp number', False,  '000920', 'PS12345', TRAND_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_DEATH_CORP_NUM_MISSING, True),
    ('Invalid no death date', False,  '000921', 'PS12345', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_DEATH_DATE_MISSING, True),
    ('Invalid add 2 groups', False,  '000921', 'PS12345', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS,
     val_owner_utils.TRAN_DEATH_GROUP_COUNT, True),
    ('Invalid delete 2 groups', False,  '000921', 'PS12345', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS,
     val_owner_utils.TRAN_DEATH_GROUP_COUNT, True)
]
# testdata pattern is ({description},{valid},{mhr_num},{account_id},{delete_groups},{add_groups},{message content},{staff})
TEST_TRANSFER_DATA_WILL = [
    ('Valid', True,  '000921', 'PS12345', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS, None, True),
    ('Valid delete EXEC', True,  '000923', 'PS12345', WILL_DELETE_GROUPS3, EXEC_ADD_GROUPS, None, True),
    ('Invalid non-staff', False,  '000921', 'PS12345', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.REG_STAFF_ONLY, False),
    ('Valid add owner', True,  '000921', 'PS12345', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS, None, True),
    ('Valid party type EXECUTOR', True,  '000921', 'PS12345', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS, None, True),
    ('Valid party type TRUSTEE', True,  '000921', 'PS12345', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS, None, True),
    ('Valid party type ADMINISTRATOR', True,  '000921', 'PS12345', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS, None, True),
    ('Invalid party type add', False,  '000921', 'PS12345', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_WILL_NEW_OWNER, True),
    ('Invalid executor missing', False,  '000921', 'PS12345', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS_INVALID,
     validator.TRAN_WILL_NEW_OWNER, True),
    ('Invalid no probate', False,  '000921', 'PS12345', WILL_DELETE_GROUPS1, EXEC_ADD_GROUPS,
     validator.TRAN_WILL_PROBATE, True),
    ('Invalid no death info', False,  '000921', 'PS12345', WILL_DELETE_GROUPS2, EXEC_ADD_GROUPS,
     validator.TRAN_WILL_DEATH_CERT, True),
    ('Invalid add 2 groups', False,  '000921', 'PS12345', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS,
     val_owner_utils.TRAN_DEATH_GROUP_COUNT, True),
    ('Invalid delete 2 groups', False,  '000921', 'PS12345', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS,
     val_owner_utils.TRAN_DEATH_GROUP_COUNT, True)
]
# testdata pattern is ({description}, {valid}, {mhr_num}, {tenancy_type}, {add_group}, {message content})
TEST_TRANSFER_DEATH_NA_DATA = [
   ('Invalid JOINT tenancy-party type', False, '000919', MhrTenancyTypes.JOINT, TC_GROUP_TRANSFER_ADD,
     val_owner_utils.TENANCY_PARTY_TYPE_INVALID),
    ('Invalid tenancy type - party type', False, '000900', MhrTenancyTypes.JOINT, TC_GROUP_TRANSFER_ADD,
     val_owner_utils.TENANCY_PARTY_TYPE_INVALID)
]
# testdata pattern is ({description}, {valid}, {numerator}, {denominator}, {message content})
TEST_TRANSFER_DATA_GROUP_INTEREST = [
    ('Valid add', True, 1, 2, None),
    ('Invalid numerator < 1', False, 1, 4, val_owner_utils.GROUP_INTEREST_MISMATCH),
    ('Invalid numerator sum high', False, 3, 4, val_owner_utils.GROUP_INTEREST_MISMATCH)
]
# testdata pattern is ({description}, {valid}, {staff}, {kc_group}, {mhr_num}, {json_data}, {message content})
TEST_TRANSFER_DATA_QS = [
    ('Valid QS TC 1', True, QUALIFIED_USER_GROUP, '000900', TRANS_QS_1, None),
    ('Valid QS TC all', True, QUALIFIED_USER_GROUP, '000900', TRANS_QS_3, None),
    ('Valid 2 groups', True, QUALIFIED_USER_GROUP, '000900', TRANS_QS_2, None),
    ('Invalid QS TC groups', False, QUALIFIED_USER_GROUP, '000925', TRANS_QS_4, validator.TRAN_QUALIFIED_DELETE)
]
# testdata pattern is ({description}, {valid}, {staff}, {gtype}, {mhr_num}, {json_data}, {message content})
TEST_TRANSFER_DATA_TC = [
    ('Valid', True, True, 'SOLE', '000900', TRANS_TC_3, None),
    ('Valid existing exec', True, True, 'COMMON', '000924', TRANS_TC_4, None),
    ('Valid unchanged exec', True, True, 'COMMON', '000924', TRANS_TC_5, None),
    ('Valid split exec', True, True, 'COMMON', '000924', TRANS_TC_6, None),
    ('Invalid add TC type', False, True, 'COMMON', '000900', TRANS_TC_3, val_owner_utils.GROUP_COMMON_INVALID),
    ('Invalid add NA type', False, True, 'NA', '000900', TRANS_TC_3, val_owner_utils.TENANCY_TYPE_NA_INVALID),
    ('Invalid add exec', False, False, 'COMMON', '000924', TRANS_TC_5, val_owner_utils.TRANSFER_PARTY_TYPE_INVALID),
    ('Valid staff add exec', True, True, 'COMMON', '000924', TRANS_TC_5, None),
    ('Valid add exec staff misc.', True, True, 'COMMON', '000924', TRANS_TC_5, None)
]
# testdata pattern is ({desc}, {valid}, {doc_type}, {reg_type}, {message content})
TEST_DATA_DOC_TYPE = [
    ('Valid no type', True,  None, None, None),
    ('Valid TRANS_LAND_TITLE', True,  'TRANS_LAND_TITLE', MhrRegistrationTypes.TRANS, None),
    ('Valid TRANS_FAMILY_ACT', True,  'TRANS_FAMILY_ACT', MhrRegistrationTypes.TRANS, None),
    ('Valid TRANS_INFORMAL_SALE', True,  'TRANS_INFORMAL_SALE', MhrRegistrationTypes.TRANS, None),
    ('Valid TRANS_QUIT_CLAIM', True,  'TRANS_QUIT_CLAIM', MhrRegistrationTypes.TRANS, None),
    ('Valid TRANS_SEVER_GRANT', True,  'TRANS_SEVER_GRANT', MhrRegistrationTypes.TRANS, None),
    ('Valid TRANS_RECEIVERSHIP', True,  'TRANS_RECEIVERSHIP', MhrRegistrationTypes.TRANS, None),
    ('Valid TRANS_WRIT_SEIZURE', True,  'TRANS_WRIT_SEIZURE', MhrRegistrationTypes.TRANS, None),
    ('Valid ABAN', True, 'ABAN', MhrRegistrationTypes.TRANS, None),
    ('Valid BANK', True, 'BANK', MhrRegistrationTypes.TRANS, None),
    ('Valid COU', True, 'COU', MhrRegistrationTypes.TRANS, None),
    ('Valid FORE', True, 'FORE', MhrRegistrationTypes.TRANS, None),
    ('Valid GENT', True, 'GENT', MhrRegistrationTypes.TRANS, None),
    ('Valid REIV', True, 'REIV', MhrRegistrationTypes.TRANS, None),
    ('Valid REPV', True, 'REPV', MhrRegistrationTypes.TRANS, None),
    ('Valid SZL', True, 'SZL', MhrRegistrationTypes.TRANS, None),
    ('Valid TAXS', True, 'TAXS', MhrRegistrationTypes.TRANS, None),
    ('Valid VEST', True, 'VEST', MhrRegistrationTypes.TRANS, None),
    ('Valid EXECUTOR', True, 'TRANS_LAND_TITLE', MhrRegistrationTypes.TRANS, None),
    ('Valid EXECUTOR no doc type', True, None, MhrRegistrationTypes.TRANS, None),
    ('Valid ADMINISTRATOR', True, 'ABAN', MhrRegistrationTypes.TRANS, None),
    ('Valid TRUSTEE', True, 'TRANS_QUIT_CLAIM', MhrRegistrationTypes.TRANS, None),
    ('Invalid no type EXECUTOR', False,  None, None, val_owner_utils.TRANSFER_PARTY_TYPE_INVALID),
    ('Invalid doc type', False,  'WILL', MhrRegistrationTypes.TRANS, 'data validation errors'),
    ('Invalid reg type', False,  'TRANS_TRUST', MhrRegistrationTypes.TRAND, validator.TRANS_DOC_TYPE_INVALID),
    ('Invalid not staff', False,  'ABAN', MhrRegistrationTypes.TRANS, validator.TRANS_DOC_TYPE_NOT_ALLOWED)
]
# testdata pattern is ({desc}, {valid}, {doc_type}, {account_id}, {mhr}, {has_qs_info} {message content})
TEST_DATA_DEALER = [
    ('Invalid no QS info', False,  None, 'PS12345', '000915', False, validator.QS_DEALER_INVALID),
    ('Invalid doc type', False,  'TRANS_LAND_TITLE', 'PS12345', '000915', True, validator.TRANS_DEALER_DOC_TYPE_INVALID),
    # ('Invalid existing owner SOLE', False,  None, 'PS12345', '000915', True, validator.DEALER_TRANSFER_OWNER_INVALID),
    # ('Invalid existing owner JOINT', False,  None, 'PS12345', '000920', True, validator.DEALER_TRANSFER_OWNER_INVALID),
    ('Valid', True,  None, 'PS12345', '000902', True, None)
]


@pytest.mark.parametrize('desc,valid,staff,doc_id,message_content,status', TEST_TRANSFER_DATA)
def test_validate_transfer(session, desc, valid, staff, doc_id, message_content, status):
    """Assert that MH transfer validation works as expected."""
    # setup
    json_data = copy.deepcopy(TRANSFER)
    mhr_num: str = '000919'
    account_id: str = 'PS12345'
    if doc_id:
        json_data['documentId'] = doc_id
    elif json_data.get('documentId'):
        del json_data['documentId']
    if valid:
        json_data['deleteOwnerGroups'][0]['groupId'] = 1
        json_data['deleteOwnerGroups'][0]['type'] = 'SOLE'
    elif desc == DESC_NONEXISTENT_GROUP_ID:
        json_data['deleteOwnerGroups'][0]['groupId'] = 10
    elif desc == DESC_INVALID_GROUP_TYPE:
        json_data['deleteOwnerGroups'][0]['type'] = 'COMMON'
    elif desc in ('Invalid FROZEN', 'Valid staff FROZEN'):
        mhr_num = '000917'
    elif desc == 'Invalid draft':
        mhr_num = '000919'
        json_data['mhrNumber'] = mhr_num
        json_data['draftNumber'] = '101421'
    elif desc == 'Invalid EXEMPT':
        mhr_num = '000912'
    elif desc == 'Invalid CANCELLED':
        mhr_num = '000913'
    elif desc == 'Invalid FROZEN TAXN':
        mhr_num = '000914'
    elif desc == 'Invalid FROZEN REST':
        mhr_num = '000915'
    elif desc == 'Invalid FROZEN NCON':
        mhr_num = '000918'
    elif desc == DESC_INVALID_GROUP_ID:
        mhr_num = '000917'
        json_data['deleteOwnerGroups'][0]['groupId'] = 1
        json_data['deleteOwnerGroups'][0]['type'] = 'SOLE'

    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, account_id)
    if status:
        registration.status_type = status
    error_msg = validator.validate_transfer(registration, json_data, staff, STAFF_ROLE)
    if errors:
        current_app.logger.debug(errors)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            if desc in (DESC_INVALID_GROUP_ID, DESC_INVALID_GROUP_TYPE):
                expected = message_content.format(group_id=1)
                assert error_msg.find(expected) != -1
            elif desc == DESC_NONEXISTENT_GROUP_ID:
                expected = message_content.format(group_id=10)
                assert error_msg.find(expected) != -1
            else:
                assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,staff,trans_dt,dec_value,consideration,message_content', TEST_TRANSFER_DATA_EXTRA)
def test_validate_transfer_details(session, desc, valid, staff, trans_dt, dec_value, consideration, message_content):
    """Assert that MH transfer validation of detail information works as expected."""
    # setup
    json_data = copy.deepcopy(TRANSFER)
    if staff:
        json_data['documentId'] = DOC_ID_VALID
    elif json_data.get('documentId'):
        del json_data['documentId']
    if not trans_dt:
        del json_data['transferDate']
    elif desc == 'Valid non-staff exists':
        json_data['transferDate'] = model_utils.format_ts(model_utils.now_ts())
    elif desc == 'Invalid non-staff future transfer date':
        json_data['transferDate'] = model_utils.format_ts(model_utils.now_ts_offset(1, True))
    if not dec_value:
        del json_data['declaredValue']
    if not consideration:
        del json_data['consideration']
    if valid:
        json_data['deleteOwnerGroups'][0]['groupId'] = 1
        json_data['deleteOwnerGroups'][0]['type'] = 'SOLE'
        if staff:
            json_data['documentId'] = '63166035'
    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number('000919', 'PS12345')
    error_msg = validator.validate_transfer(registration, json_data, staff, STAFF_ROLE)
    if errors:
        current_app.logger.debug(errors)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,numerator,denominator,add_group,message_content', TEST_TRANSFER_DATA_GROUP)
def test_validate_transfer_group(session, desc, valid, numerator, denominator, add_group, message_content):
    """Assert that MH transfer validation of owner groups works as expected."""
    # setup
    json_data = copy.deepcopy(TRANSFER)
    json_data['deleteOwnerGroups'][0]['groupId'] = 1
    json_data['deleteOwnerGroups'][0]['type'] = 'SOLE'
    if add_group:
        json_data['addOwnerGroups'] = copy.deepcopy(add_group)
        if desc == 'Invalid add TC no owner':
            json_data['addOwnerGroups'][1]['owners'] = []
        elif desc == 'Invalid add TC > 1 owner':
            json_data['addOwnerGroups'][0]['type'] = 'COMMON'
        else:
            for group in json_data.get('addOwnerGroups'):
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
    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number('000919', 'PS12345')
    error_msg = validator.validate_transfer(registration, json_data, False, STAFF_ROLE)
    if errors:
        current_app.logger.debug(errors)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,mhr_num,account_id,delete_groups,add_groups,message_content',
                         TEST_TRANSFER_DATA_TRAND)
def test_validate_transfer_trand(session, desc, valid, mhr_num, account_id, delete_groups, add_groups, message_content):
    """Assert that MH transfer TRAND validation of owner groups works as expected."""
    # setup
    json_data = copy.deepcopy(TRANSFER)
    json_data['documentId'] = DOC_ID_VALID
    json_data['registrationType'] = MhrRegistrationTypes.TRAND
    json_data['deleteOwnerGroups'] = copy.deepcopy(delete_groups)
    json_data['addOwnerGroups'] = copy.deepcopy(add_groups)
    staff: bool = False
    role: str = STAFF_ROLE
    if desc == 'Invalid party type':
        json_data['addOwnerGroups'][0]['owners'][0]['partyType'] = MhrPartyTypes.TRUSTEE
    elif desc == 'Invalid add owner':
        json_data['addOwnerGroups'][0]['owners'].append(ADD_OWNER)
    elif desc == 'Invalid no cert number':
        del json_data['deleteOwnerGroups'][0]['owners'][1]['deathCertificateNumber']
    elif desc == 'Invalid no corp number':
        del json_data['deleteOwnerGroups'][0]['owners'][1]['deathCertificateNumber']
        del json_data['deleteOwnerGroups'][0]['owners'][1]['individualName']
        json_data['deleteOwnerGroups'][0]['owners'][1]['partyType'] = 'OWNER_BUS'
        json_data['deleteOwnerGroups'][0]['owners'][1]['organizationName'] = 'TEST BUS NAME'
    elif desc == 'Invalid no death ts':
        del json_data['deleteOwnerGroups'][0]['owners'][1]['deathDateTime']
    elif desc == 'Invalid add 2 groups':
        json_data['addOwnerGroups'].append(ADD_GROUP)
    elif desc == 'Invalid delete 2 groups':
        json_data['deleteOwnerGroups'].append(ADD_GROUP)
    elif desc == 'Invalid future death ts':
        future_ts = model_utils.now_ts_offset(1, True)
        json_data['deleteOwnerGroups'][0]['owners'][1]['deathDateTime'] = model_utils.format_ts(future_ts)
    elif desc == 'Invalid staff FROZEN':
        staff = True
    elif desc in ('Valid no transfer date',
                  'Valid no consideration',
                  'Invalid JOINT BUS QS',
                  'Invalid JOINT BUS QS DELETE'):
        role = QUALIFIED_USER_GROUP
        staff = False
    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, account_id)
    error_msg = validator.validate_transfer(registration, json_data, staff, role)
    # if valid and error_msg:
    #    current_app.logger.debug('UNEXPECTED ERROR: ' + error_msg)
    if errors:
        current_app.logger.debug(errors)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,mhr_num,account_id,delete_groups,add_groups,message_content,staff',
                         TEST_TRANSFER_DATA_ADMIN)
def test_validate_transfer_admin(session, desc, valid, mhr_num, account_id, delete_groups, add_groups, message_content,
                                 staff):
    """Assert that MH transfer TRANS_ADMIN validation of owner groups works as expected."""
    # setup
    json_data = copy.deepcopy(TRANSFER)
    json_data['documentId'] = DOC_ID_VALID
    json_data['registrationType'] = MhrRegistrationTypes.TRANS_ADMIN
    json_data['deleteOwnerGroups'] = copy.deepcopy(delete_groups)
    json_data['addOwnerGroups'] = copy.deepcopy(add_groups)
    if desc == 'Valid party type EXECUTOR':
        json_data['deleteOwnerGroups'][0]['owners'][0]['partyType'] = MhrPartyTypes.EXECUTOR
    elif desc == 'Valid party type TRUSTEE':
        json_data['deleteOwnerGroups'][0]['owners'][0]['partyType'] = MhrPartyTypes.TRUSTEE
    elif desc == 'Valid party type ADMINISTRATOR':
        json_data['deleteOwnerGroups'][0]['owners'][0]['partyType'] = MhrPartyTypes.ADMINISTRATOR
    elif desc == 'Invalid party type add':
        json_data['addOwnerGroups'][0]['owners'][0]['partyType'] = MhrPartyTypes.TRUSTEE
    elif desc == 'Invalid administrator missing':
        del json_data['addOwnerGroups'][0]['owners'][0]['partyType']
        del json_data['addOwnerGroups'][0]['owners'][0]['description']
    elif desc == 'Invalid no grant':
        json_data['deleteOwnerGroups'][0]['owners'][0]['deathCertificateNumber'] = '232432433'
        json_data['deleteOwnerGroups'][0]['owners'][0]['deathDateTime'] = '2021-02-21T18:56:00+00:00'
    elif desc == 'Invalid no death info': 
        del json_data['deleteOwnerGroups'][0]['owners'][1]['deathCertificateNumber']
        del json_data['deleteOwnerGroups'][0]['owners'][1]['deathDateTime']
    elif desc == 'Invalid add owner':
        json_data['addOwnerGroups'][0]['owners'].append(ADD_OWNER)
    elif desc == 'Invalid add 2 groups':
        json_data['addOwnerGroups'].append(ADD_GROUP)
    elif desc == 'Invalid delete 2 groups':
        json_data['deleteOwnerGroups'].append(ADD_GROUP)

    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    error_msg = validator.validate_transfer(registration, json_data, staff, STAFF_ROLE)
    if errors:
        current_app.logger.debug(errors)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,mhr_num,account_id,delete_groups,add_groups,message_content,staff',
                         TEST_TRANSFER_DATA_AFFIDAVIT)
def test_validate_transfer_affidavit(session, desc, valid, mhr_num, account_id, delete_groups, add_groups,
                                     message_content,
                                     staff):
    """Assert that MH transfer TRANS_AFFIDAVIT validation of owner groups works as expected."""
    # setup
    json_data = copy.deepcopy(TRANSFER)
    json_data['documentId'] = DOC_ID_VALID
    json_data['registrationType'] = MhrRegistrationTypes.TRANS_AFFIDAVIT
    json_data['deleteOwnerGroups'] = copy.deepcopy(delete_groups)
    json_data['addOwnerGroups'] = copy.deepcopy(add_groups)
    json_data['declaredValue'] = 25000
    if desc == 'Valid party type EXECUTOR':
        json_data['deleteOwnerGroups'][0]['owners'][0]['partyType'] = MhrPartyTypes.EXECUTOR
    elif desc == 'Valid party type TRUSTEE':
        json_data['deleteOwnerGroups'][0]['owners'][0]['partyType'] = MhrPartyTypes.TRUSTEE
    elif desc == 'Valid party type ADMINISTRATOR':
        json_data['deleteOwnerGroups'][0]['owners'][0]['partyType'] = MhrPartyTypes.ADMINISTRATOR
    elif desc == 'Invalid party type add':
        json_data['addOwnerGroups'][0]['owners'][0]['partyType'] = MhrPartyTypes.TRUSTEE
    elif desc == 'Invalid add owner':
        json_data['addOwnerGroups'][0]['owners'].append(ADD_OWNER)
    elif desc == 'Invalid executor missing':
        del json_data['addOwnerGroups'][0]['owners'][1]['partyType']
        del json_data['addOwnerGroups'][0]['owners'][1]['description']
    elif desc == 'Invalid add 2 groups':
        json_data['addOwnerGroups'].append(ADD_GROUP)
    elif desc == 'Invalid delete 2 groups':
        json_data['deleteOwnerGroups'].append(ADD_GROUP)
    elif desc == 'Invalid no death info':
        del json_data['deleteOwnerGroups'][0]['owners'][0]['deathCertificateNumber']
        del json_data['deleteOwnerGroups'][0]['owners'][0]['deathDateTime']
    elif desc == 'Invalid no death cert number':
        del json_data['deleteOwnerGroups'][0]['owners'][0]['deathCertificateNumber']
    elif desc == 'Invalid no death date':
        del json_data['deleteOwnerGroups'][0]['owners'][0]['deathDateTime']
    elif desc == 'Invalid no death corp number':
        del json_data['deleteOwnerGroups'][0]['owners'][1]['deathCertificateNumber']
        del json_data['deleteOwnerGroups'][0]['owners'][1]['individualName']
        json_data['deleteOwnerGroups'][0]['owners'][1]['partyType'] = 'OWNER_BUS'
        json_data['deleteOwnerGroups'][0]['owners'][1]['organizationName'] = 'TEST BUS NAME'

    if desc == 'Invalid declared value':
        json_data['declaredValue'] = 25001
    else:
        json_data['declaredValue'] = 25000

    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    error_msg = validator.validate_transfer(registration, json_data, staff, STAFF_ROLE)
    if errors:
        current_app.logger.debug(errors)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,mhr_num,account_id,delete_groups,add_groups,message_content,staff',
                         TEST_TRANSFER_DATA_WILL)
def test_validate_transfer_will(session, desc, valid, mhr_num, account_id, delete_groups, add_groups, message_content,
                                staff):
    """Assert that MH transfer TRANS_WILL validation of owner groups works as expected."""
    # setup
    json_data = copy.deepcopy(TRANSFER)
    json_data['documentId'] = DOC_ID_VALID
    json_data['registrationType'] = MhrRegistrationTypes.TRANS_WILL
    json_data['deleteOwnerGroups'] = copy.deepcopy(delete_groups)
    json_data['addOwnerGroups'] = copy.deepcopy(add_groups)
    if desc == 'Valid party type EXECUTOR':
        json_data['deleteOwnerGroups'][0]['owners'][0]['partyType'] = MhrPartyTypes.EXECUTOR
    elif desc == 'Valid party type TRUSTEE':
        json_data['deleteOwnerGroups'][0]['owners'][0]['partyType'] = MhrPartyTypes.TRUSTEE
    elif desc == 'Valid party type ADMINISTRATOR':
        json_data['deleteOwnerGroups'][0]['owners'][0]['partyType'] = MhrPartyTypes.ADMINISTRATOR
    elif desc == 'Invalid party type add':
        json_data['addOwnerGroups'][0]['owners'][0]['partyType'] = MhrPartyTypes.TRUSTEE
    elif desc == 'Valid add owner':
        json_data['addOwnerGroups'][0]['owners'].append(ADD_OWNER)
        json_data['addOwnerGroups'][0]['type'] = 'NA'
    elif desc == 'Invalid executor missing':
        del json_data['addOwnerGroups'][0]['owners'][1]['partyType']
        del json_data['addOwnerGroups'][0]['owners'][1]['description']
    elif desc == 'Invalid add 2 groups':
        json_data['addOwnerGroups'].append(ADD_GROUP)
    elif desc == 'Invalid delete 2 groups':
        json_data['deleteOwnerGroups'].append(ADD_GROUP)

    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id, staff)
    error_msg = validator.validate_transfer(registration, json_data, staff, STAFF_ROLE)
    current_app.logger.info(error_msg)
    if errors:
        current_app.logger.debug(errors)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,mhr_num,tenancy_type,add_group,message_content', TEST_TRANSFER_DEATH_NA_DATA)
def test_validate_transfer_death_na(session, desc, valid, mhr_num, tenancy_type, add_group, message_content):
    """Assert that MH transfer due to death validation of owner groups works as expected."""
    # setup
    json_data = copy.deepcopy(TRANSFER)
    json_data['documentId'] = DOC_ID_VALID
    json_data['deleteOwnerGroups'][0]['groupId'] = 2
    json_data['deleteOwnerGroups'][0]['type'] = 'JOINT'
    json_data['registrationType'] = MhrRegistrationTypes.TRAND
    json_data['addOwnerGroups'] = copy.deepcopy(add_group)
    json_data['addOwnerGroups'][0]['type'] = tenancy_type
    if desc == 'Valid':
        json_data['deleteOwnerGroups'] = TC_GROUP_TRANSFER_DELETE_2
        json_data['addOwnerGroups'][0]['interestNumerator'] = json_data['deleteOwnerGroups'][0]['interestNumerator']
        json_data['addOwnerGroups'][0]['interestDenominator'] = json_data['deleteOwnerGroups'][0]['interestDenominator']
    owners = json_data['addOwnerGroups'][0]['owners']
    owners[0]['description'] = 'EXECUTOR OF SOMEONE'
    owners[0]['partyType'] = MhrPartyTypes.EXECUTOR
    owners[1]['description'] = 'EXECUTOR OF SOMEONE'
    owners[1]['partyType'] = MhrPartyTypes.EXECUTOR
    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, 'PS12345')
    error_msg = validator.validate_transfer(registration, json_data, False, STAFF_ROLE)
    if errors:
        current_app.logger.debug(errors)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,numerator,denominator,message_content', TEST_TRANSFER_DATA_GROUP_INTEREST)
def test_validate_transfer_group_interest(session, desc, valid, numerator, denominator, message_content):
    """Assert that transfer group interest validation works as expected."""
    # setup
    json_data = copy.deepcopy(TRANSFER)
    json_data['deleteOwnerGroups'] = copy.deepcopy(TC_GROUP_TRANSFER_DELETE)
    json_data['addOwnerGroups'] = copy.deepcopy(TC_GROUP_TRANSFER_ADD)
    json_data['addOwnerGroups'][0]['interestNumerator'] = numerator
    json_data['addOwnerGroups'][0]['interestDenominator'] = denominator
    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    registration: MhrRegistration = MhrRegistration.find_all_by_mhr_number('000900', 'PS12345')
    error_msg = validator.validate_transfer(registration, json_data, False, STAFF_ROLE)
    if errors:
        current_app.logger.debug(errors)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,kc_group,mhr_num,json_data,message_content', TEST_TRANSFER_DATA_QS)
def test_validate_transfer_qs(session, desc, valid, kc_group, mhr_num, json_data, message_content):
    """Assert that MH transfer validation rules for qualified suppliers works as expected."""
    # setup
    request_data = copy.deepcopy(json_data)
    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, 'PS12345')
    error_msg = validator.validate_transfer(registration, request_data, False, kc_group)
    if errors:
        current_app.logger.debug(errors)
    if error_msg:
        current_app.logger.debug(error_msg)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,staff,gtype,mhr_num,data,message_content', TEST_TRANSFER_DATA_TC)
def test_validate_transfer_tc(session, desc, valid, staff, gtype, mhr_num, data, message_content):
    """Assert that MH transfer validation rules for COMMON to SOLE works as expected."""
    # setup
    json_data = copy.deepcopy(data)
    json_data['documentId'] = DOC_ID_VALID
    json_data['addOwnerGroups'][0]['type'] = gtype
    if desc in ('Invalid add exec', 'Valid staff add exec'):
        json_data['addOwnerGroups'][1]['owners'][0]['partyType'] = 'EXECUTOR'
        json_data['addOwnerGroups'][1]['owners'][0]['description'] = 'EXECUTOR OF THE ESTATED OF ...'
        if desc == 'Valid staff add exec':
            json_data['addOwnerGroups'][1]['type'] = 'NA'
    elif desc == 'Valid add exec staff misc.':
        json_data['transferDocumentType'] = 'TRANS_INFORMAL_SALE'
        json_data['addOwnerGroups'][1]['owners'][0]['partyType'] = 'EXECUTOR'
        json_data['addOwnerGroups'][1]['owners'][0]['description'] = 'EXECUTOR OF THE ESTATED OF ...'
        json_data['addOwnerGroups'][1]['type'] = 'NA'
    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, 'PS12345')
    error_msg = validator.validate_transfer(registration, json_data, staff, STAFF_ROLE)
    if errors:
        current_app.logger.debug(errors)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,doc_type,reg_type,message_content', TEST_DATA_DOC_TYPE)
def test_validate_transfer_doc_type(session, desc, valid, doc_type, reg_type, message_content):
    """Assert that MH transfer transferDocumentType validation works as expected."""
    # setup
    json_data = copy.deepcopy(TRANSFER)
    mhr_num: str = '000919'
    account_id: str = 'PS12345'
    staff = True
    group = STAFF_ROLE
    json_data['documentId'] = DOC_ID_VALID
    json_data['deleteOwnerGroups'][0]['groupId'] = 1
    json_data['deleteOwnerGroups'][0]['type'] = 'SOLE'
    if reg_type:
        json_data['registrationType'] = reg_type
    if doc_type:
        json_data['transferDocumentType'] = doc_type
    if desc == 'Invalid not staff':
        staff = False
        group = QUALIFIED_USER_GROUP
    elif desc in ('Invalid no type EXECUTOR', 'Valid EXECUTOR', 'Valid EXECUTOR no doc type'):
        json_data['addOwnerGroups'][0]['owners'][0]['partyType'] = 'EXECUTOR'
        json_data['addOwnerGroups'][0]['owners'][0]['description'] = 'EXECUTOR OF THE ESTATED OF ...'
        if desc == 'Invalid no type EXECUTOR':
            staff = False
            group = QUALIFIED_USER_GROUP
    elif desc == 'Valid ADMINISTRATOR':
        json_data['addOwnerGroups'][0]['owners'][0]['partyType'] = 'ADMINISTRATOR'
        json_data['addOwnerGroups'][0]['owners'][0]['description'] = 'ADMINISTRATOR OF THE ESTATED OF ...'
    elif desc == 'Valid TRUSTEE':
        json_data['addOwnerGroups'][0]['owners'][0]['partyType'] = 'TRUSTEE'
        json_data['addOwnerGroups'][0]['owners'][0]['description'] = 'TRUSTEE OF THE ESTATED OF ...'

    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, account_id)
    error_msg = validator.validate_transfer(registration, json_data, staff, group)
    # if errors:
    #    for err in errors:
    #        current_app.logger.debug(err)
    if valid:
        assert valid_format and error_msg == ''
    elif desc == 'Invalid doc type':
        assert errors and not valid_format
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,doc_type,account_id,mhr_num,has_qs,message_content', TEST_DATA_DEALER)
def test_validate_dealer(session, desc, valid, doc_type, account_id, mhr_num, has_qs, message_content):
    """Assert that MH transfer QS dealer validation works as expected."""
    # setup
    json_data = copy.deepcopy(TRANSFER)
    staff = False
    group = DEALERSHIP_GROUP
    json_data['registrationType'] = 'TRANS'
    if doc_type:
        json_data['transferDocumentType'] = doc_type
    if has_qs:
        supplier = MhrQualifiedSupplier.find_by_account_id(account_id)
        if supplier:
            json_data['supplier'] = supplier.json

    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, account_id)
    if valid:
        registration.owner_groups[0].owners[0].business_name = json_data['supplier'].get('businessName')
    error_msg = validator.validate_transfer(registration, json_data, staff, group)
    # if errors:
    #    for err in errors:
    #        current_app.logger.debug(err)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1
