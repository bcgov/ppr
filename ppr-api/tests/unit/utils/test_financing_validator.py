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

import pytest

from ppr_api.models import utils as model_utils
from ppr_api.models.registration import CrownChargeTypes, PPSATypes
from ppr_api.models.type_tables import RegistrationType, RegistrationTypes
from ppr_api.utils.validators import financing_validator as validator
from ppr_api.utils.logging import logger


FINANCING = {
    'type': 'SA',
    'clientReferenceId': 'A-00000402',
    'documentId': '1234567',
    'authorizationReceived': True,
    'registeringParty': {
        'businessName': 'ABC SEARCHING COMPANY',
        'address': {
            'street': '222 SUMMER STREET',
            'city': 'VICTORIA',
            'region': 'BC',
            'country': 'CA',
            'postalCode': 'V8W 2V8'
        },
        'emailAddress': 'bsmith@abc-search.com'
    },
    'securedParties': [
        {
            'businessName': 'BANK OF BRITISH COLUMBIA',
            'address': {
                'street': '3720 BEACON AVENUE',
                'city': 'SIDNEY',
                'region': 'BC',
                'country': 'CA',
                'postalCode': 'V7R 1R7'
            },
            'partyId': 1321095
        }
    ],
    'debtors': [
        {
            'businessName': 'Brown Window Cleaning Inc.',
            'address': {
                'street': '1234 Blanshard St',
                'city': 'Victoria',
                'region': 'BC',
                'country': 'CA',
                'postalCode': 'V8S 3J5'
             },
            'emailAddress': 'csmith@bwc.com',
            'partyId': 1400094
        }
    ],
    'vehicleCollateral': [
        {
            'type': 'MV',
            'serialNumber': 'KNADM5A39E6904135',
            'year': 2014,
            'make': 'KIA',
            'model': 'RIO',
            'vehicleId': 974124
        }
    ],
    'generalCollateral': [
        {
            'description': 'Fridges and stoves. Proceeds: Accts Receivable.',
            'addedDateTime': '2019-02-02T21:08:32+00:00',
            'collateralId': 123435
        }
    ],
    'lifeYears': 5,
    'trustIndenture': False,
    'lifeInfinite': False
}
FINANCING_SE = {
    'type': 'SE',
    'clientReferenceId': 'A-00000402',
    'documentId': '1234567',
    'authorizationReceived': True,
    'registeringParty': {
        'code': '99980001' 
    },
    'securedParties': [
        {
            'code': '99980001' 
        }
    ],
    'debtors': [
        {
            'businessName': 'Brown Window Cleaning Inc.',
            'address': {
                'street': '1234 Blanshard St',
                'city': 'Victoria',
                'region': 'BC',
                'country': 'CA',
                'postalCode': 'V8S 3J5'
             },
            'emailAddress': 'csmith@bwc.com'
        }
    ],
    'generalCollateral': [
        {
            'description': 'Fridges and stoves. Proceeds: Accts Receivable.'
        }
    ],
    'vehicleCollateral': [
        {
            'type': 'MV',
            'serialNumber': 'KNADM5A39E6904135',
            'year': 2014,
            'make': 'KIA',
            'model': 'RIO',
            'vehicleId': 974124
        }
    ],
    'lifeInfinite': True
}
SE_SP_INVALID = [
    {
        'code': '99990001'
    },
    {
        'businessName': 'BANK OF BRITISH COLUMBIA',
        'address': {
            'street': '3720 BEACON AVENUE',
            'city': 'SIDNEY',
            'region': 'BC',
            'country': 'CA',
            'postalCode': 'V7R 1R7'
        }
    }
]
SE_SP_INVALID1 = [
    {
        'businessName': 'BANK OF BRITISH COLUMBIA',
        'address': {
            'street': '3720 BEACON AVENUE',
            'city': 'SIDNEY',
            'region': 'BC',
            'country': 'CA',
            'postalCode': 'V7R 1R7'
        }
    }
]
SE_SP_INVALID2 = [
    {
        'code': '99990001'
    }
]
SE_RP_INVALID_1 = {
    'businessName': 'BANK OF BRITISH COLUMBIA',
    'address': {
        'street': '3720 BEACON AVENUE',
        'city': 'SIDNEY',
        'region': 'BC',
        'country': 'CA',
        'postalCode': 'V7R 1R7'
    }
}
SE_RP_INVALID_2 = {
    'code': '99990001'
}
SECURITIES_ACT_NOTICES = [
    {
        'securitiesActNoticeType': 'LIEN',
        'effectiveDateTime': '2024-04-22T06:59:59+00:00',
        'securitiesActOrders': [
            {
                'courtOrder': True,
                'courtName': 'court name',
                'courtRegistry': 'registry',
                'fileNumber': 'filenumber',
                'orderDate': '2024-04-22T06:59:59+00:00',
                'effectOfOrder': 'effect'
            }
        ]        
    }
]

DESC_VALID = 'Valid'
DESC_INCLUDES_GC = 'Includes general collateral'
DESC_MISSING_GC = 'Missing general collateral'
DESC_INCLUDES_VC = 'Includes vehicle collateral'
DESC_MISSING_VC = 'Missing vehicle collateral'
DESC_VC_MH = 'Vehicle collateral MH'
DESC_VC_NOT_MH = 'Vehicle collateral not MH'
DESC_EXCLUDES_LY = 'Life years not allowed'
DESC_INFINITY_INVALID = 'Life Infinity false'
DESC_INCLUDES_OT_DESC = 'Includes other type description'
DESC_MISSING_OT_DESC = 'Missing other type description'
DESC_INCLUDES_TI = 'Includes trust indenture'
DESC_ALL_LIFE = 'Includes life years, life infinite'
DESC_INCLUDES_LA = 'Includes lien amount'
DESC_INCLUDES_SD = 'Includes surrender date'
DESC_MISSING_AC = 'Missing authorizaton received'
DESC_INVALID_AC = 'Invalid authorizaton received'

# testdata pattern is ({description}, {valid}, {account_id}, {registering}, {secured}, {notices}, {message content})
TEST_SE_DATA = [
    (DESC_VALID, True, 'PS00002', None, None, SECURITIES_ACT_NOTICES, None),
    ('Valid no general collateral', True, 'PS00002', None, None, SECURITIES_ACT_NOTICES, None),
    ('Valid no vehicle collateral', True, 'PS00002', None, None, SECURITIES_ACT_NOTICES, None),
    ('Invalid account', False, 'PS12345', None, None, SECURITIES_ACT_NOTICES, validator.SE_ACCESS_INVALID),
    ('Invalid notices', False, 'PS00002', None, None, None, validator.SE_NOTICES_MISSING),
    ('Invalid 2 secured parties', False, 'PS00002', None, SE_SP_INVALID, SECURITIES_ACT_NOTICES,
     validator.SE_SECURED_COUNT_INVALID),
    ('Invalid secured party no code', False, 'PS00002', None, SE_SP_INVALID1, SECURITIES_ACT_NOTICES,
     validator.SE_SP_MISSING_CODE),
    ('Invalid secured party code', False, 'PS00002', None, SE_SP_INVALID2, SECURITIES_ACT_NOTICES,
     validator.SE_SP_INVALID_CODE),
    ('Invalid registering party no code', False, 'PS00002', SE_RP_INVALID_1, None, SECURITIES_ACT_NOTICES,
     validator.SE_RP_MISSING_CODE),
    ('Invalid registering party code', False, 'PS00002', SE_RP_INVALID_2, None, SECURITIES_ACT_NOTICES,
     validator.SE_RP_INVALID_CODE)
]
# testdata pattern is ({description}, {valid}, {lien_amount}, {surrender_date}, {message content})
TEST_RL_DATA = [
    (DESC_VALID, True, '1000', 'valid', None),
    ('Missing lien amount', False, None, 'valid', validator.RL_AMOUNT_REQUIRED),
    ('Missing surrender date', False, '1000', 'none', validator.RL_DATE_REQUIRED),
    ('Invalid surrender date', False, '1000', 'junk', validator.RL_DATE_INVALID),
    ('Too old surrender date', False, '1000', 'old', validator.RL_DATE_INVALID),
    ('Almost too old surrender date', True, '1000', '21', None),
    (DESC_INCLUDES_GC, False, '1000', 'valid', validator.GC_NOT_ALLOWED),
    (DESC_MISSING_VC, False, '1000', 'valid', validator.VC_REQUIRED),
    (DESC_VC_MH, False, '1000', 'valid', validator.VC_MH_NOT_ALLOWED)
]
# testdata pattern is ({description}, {valid}, {reg_type})
TEST_EXCLUDED_TYPE_DATA = [
    ('Type not allowed', False, 'SS'),
    ('Type not allowed', False, 'MR'),
    ('Type not allowed', False, 'CC'),
    ('Type not allowed', False, 'DP'),
    ('Type not allowed', False, 'HR'),
    ('Type not allowed', False, 'MI')
]
# testdata pattern is ({description}, {valid}, {reg_type}, {message content})
TEST_FR_LT_MH_MN_DATA = [
    (DESC_VALID, True, 'FR', None),
    (DESC_VALID, True, 'LT', None),
    (DESC_VALID, True, 'MH', None),
    (DESC_VALID, True, 'MN', None),
    (DESC_VC_NOT_MH, False, 'FR', validator.VC_MH_ONLY),
    (DESC_VC_NOT_MH, False, 'LT', validator.VC_MH_ONLY),
    (DESC_VC_NOT_MH, False, 'MH', validator.VC_MH_ONLY),
    (DESC_VC_NOT_MH, False, 'MN', validator.VC_MH_ONLY),
    (DESC_INCLUDES_GC, False, 'FR', validator.GC_NOT_ALLOWED),
    (DESC_INCLUDES_GC, False, 'LT', validator.GC_NOT_ALLOWED),
    (DESC_INCLUDES_GC, False, 'MH', validator.GC_NOT_ALLOWED),
    (DESC_INCLUDES_GC, False, 'MN', validator.GC_NOT_ALLOWED),
    (DESC_MISSING_VC, False, 'FR', validator.VC_REQUIRED),
    (DESC_MISSING_VC, False, 'LT', validator.VC_REQUIRED),
    (DESC_MISSING_VC, False, 'MH', validator.VC_REQUIRED),
    (DESC_MISSING_VC, False, 'MN', validator.VC_REQUIRED),
    (DESC_VC_NOT_MH, False, 'FR', validator.VC_MH_ONLY),
    (DESC_VC_NOT_MH, False, 'LT', validator.VC_MH_ONLY),
    (DESC_VC_NOT_MH, False, 'MH', validator.VC_MH_ONLY),
    (DESC_VC_NOT_MH, False, 'MN', validator.VC_MH_ONLY),
    (DESC_INFINITY_INVALID, False, 'FR', validator.LI_INVALID),
    (DESC_INFINITY_INVALID, False, 'LT', validator.LI_INVALID),
    (DESC_INFINITY_INVALID, False, 'MH', validator.LI_INVALID),
    (DESC_EXCLUDES_LY, False, 'FR', validator.LY_NOT_ALLOWED),
    (DESC_EXCLUDES_LY, False, 'LT', validator.LY_NOT_ALLOWED),
    (DESC_EXCLUDES_LY, False, 'MH', validator.LY_NOT_ALLOWED)
]
# testdata pattern is ({description}, {valid}, {message content})
TEST_PPSA_DATA = [
    (DESC_VALID, True, None),
    (DESC_INCLUDES_OT_DESC, False, validator.OT_NOT_ALLOWED),
    (DESC_INCLUDES_TI, False, validator.TI_NOT_ALLOWED),
    (DESC_ALL_LIFE, False, validator.LIFE_INVALID),
    (DESC_INCLUDES_LA, False, validator.LA_NOT_ALLOWED),
    (DESC_INCLUDES_SD, False, validator.SD_NOT_ALLOWED)
]
# testdata pattern is ({description}, {valid}, {message content})
TEST_AUTHORIZATION_DATA = [
    (DESC_MISSING_AC, False, validator.AUTHORIZATION_INVALID),
    (DESC_INVALID_AC, False, validator.AUTHORIZATION_INVALID)
]
# testdata pattern is ({description}, {valid}, {message content})
TEST_CROWN_DATA = [
    (DESC_VALID, True, None),
    (DESC_MISSING_GC, False, validator.GC_REQUIRED),
    (DESC_INCLUDES_VC, True, None),
    (DESC_INFINITY_INVALID, False, validator.LI_INVALID),
    (DESC_EXCLUDES_LY, False, validator.LY_NOT_ALLOWED),
    (DESC_INCLUDES_OT_DESC, False, validator.OT_NOT_ALLOWED),
    (DESC_MISSING_OT_DESC, False, validator.OT_MISSING_DESCRIPTION)
]
# testdata pattern is ({description}, {valid}, {reg_type}, {message content})
TEST_MD_PT_SC_DATA = [
    (DESC_VALID, True, 'MD', None),
    (DESC_VALID, True, 'PT', None),
    (DESC_VALID, True, 'SC', None),
    (DESC_VALID, True, 'TO', None),
    (DESC_VALID, True, 'SV', None),
    (DESC_MISSING_GC, False, 'MD', validator.GC_REQUIRED),
    (DESC_INCLUDES_VC, True, 'MD', None),
    (DESC_MISSING_GC, False, 'PT', validator.GC_REQUIRED),
    (DESC_INCLUDES_VC, True, 'PT', None),
    (DESC_MISSING_GC, False, 'SC', validator.GC_REQUIRED),
    (DESC_INCLUDES_VC, True, 'SC', None),
    (DESC_MISSING_GC, False, 'TO', validator.GC_REQUIRED),
    (DESC_INCLUDES_VC, True, 'TO', None),
    (DESC_MISSING_GC, False, 'SV', validator.GC_REQUIRED),
    (DESC_INCLUDES_VC, True, 'SV', None)
]
# testdata pattern is ({description}, {valid}, {reg_type}, {message content})
TEST_FL_FA_FS_HN_WL_DATA = [
    (DESC_VALID, True, 'FL', None),
    (DESC_VALID, True, 'FA', None),
    (DESC_VALID, True, 'FS', None),
    (DESC_VALID, True, 'HN', None),
    (DESC_VALID, True, 'WL', None),
    (DESC_MISSING_GC, False, 'FL', validator.GC_REQUIRED),
    (DESC_MISSING_GC, False, 'FA', validator.GC_REQUIRED),
    (DESC_MISSING_GC, False, 'FS', validator.GC_REQUIRED),
    (DESC_MISSING_GC, False, 'HN', validator.GC_REQUIRED),
    (DESC_MISSING_GC, False, 'WL', validator.GC_REQUIRED),
    (DESC_INCLUDES_VC, False, 'FL', validator.VC_NOT_ALLOWED),
    (DESC_INCLUDES_VC, False, 'FA', validator.VC_NOT_ALLOWED),
    (DESC_INCLUDES_VC, False, 'FS', validator.VC_NOT_ALLOWED),
    (DESC_INCLUDES_VC, False, 'HN', validator.VC_NOT_ALLOWED),
    (DESC_INCLUDES_VC, True, 'WL', None)
]
# testdata pattern is ({description}, {valid}, {reg_type}, {message content})
TEST_MISC_DATA = [
    (DESC_VALID, True, 'HN', None),
    (DESC_VALID, True, 'ML', None),
    (DESC_VALID, True, 'MN', None),
    (DESC_VALID, True, 'PN', None),
    (DESC_VALID, True, 'WL', None),
    (DESC_INFINITY_INVALID, False, 'HN', validator.LI_INVALID),
    (DESC_INFINITY_INVALID, False, 'ML', validator.LI_INVALID),
    (DESC_INFINITY_INVALID, False, 'MN', validator.LI_INVALID),
    (DESC_INFINITY_INVALID, False, 'PN', validator.LI_INVALID),
    (DESC_INFINITY_INVALID, False, 'WL', validator.LI_INVALID),
    (DESC_INFINITY_INVALID, False, 'SE', validator.LI_INVALID),
    (DESC_EXCLUDES_LY, False, 'HN', validator.LY_NOT_ALLOWED),
    (DESC_EXCLUDES_LY, False, 'ML', validator.LY_NOT_ALLOWED),
    (DESC_EXCLUDES_LY, False, 'MN', validator.LY_NOT_ALLOWED),
    (DESC_EXCLUDES_LY, False, 'PN', validator.LY_NOT_ALLOWED),
    (DESC_EXCLUDES_LY, False, 'SE', validator.LY_NOT_ALLOWED),
    (DESC_EXCLUDES_LY, False, 'WL', validator.LY_NOT_ALLOWED)
]
# testdata pattern is ({description}, {valid}, {reg_type}, {today_offset}, {message content})
TEST_DATA_TYPE_ENABLED = [
    ("Valid RL no act TS", True, RegistrationTypes.RL.value, None, None),
    ("Valid CL no act TS", True, RegistrationTypes.CL.value, None, None),
    ("Valid CL act TS", True, RegistrationTypes.CL.value, -1, None),
    ("Invalid CL act TS", False, RegistrationTypes.CL.value, 1, validator.CL_NOT_ALLOWED),
    ("Valid RL act TS", True, RegistrationTypes.RL.value, 1, None),
    ("Invalid RL act TS", False, RegistrationTypes.RL.value, -1, validator.RL_NOT_ALLOWED),
]


@pytest.mark.parametrize('desc,valid,account_id,registering,secured,notices,message_content', TEST_SE_DATA)
def test_validate_se(session, desc, valid, account_id, registering, secured, notices, message_content):
    """Assert that financing statement SE registration type validation works as expected."""
    # setup
    json_data = copy.deepcopy(FINANCING_SE)
    if desc == 'Valid no general collateral':
        del json_data['generalCollateral']
    elif desc == 'Valid no vehicle collateral':
        del json_data['vehicleCollateral']
    if notices:
        json_data['securitiesActNotices'] = notices
    if registering:
        json_data['registeringParty'] = registering
    if secured:
        json_data['securedParties'] = secured
    error_msg = validator.validate(json_data, account_id)
    if valid:
        assert error_msg == ''
    elif message_content:
        # print(error_msg)
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,lien_amount,surrender_date,message_content', TEST_RL_DATA)
def test_validate_rl(session, desc, valid, lien_amount, surrender_date, message_content):
    """Assert that financing statement RL registration type validation works as expected."""
    # setup
    json_data = copy.deepcopy(FINANCING)
    json_data['type'] = model_utils.REG_TYPE_REPAIRER_LIEN
    del json_data['lifeYears']
    del json_data['lifeInfinite']
    del json_data['trustIndenture']
    if lien_amount is not None:
        json_data['lienAmount'] = lien_amount
    if surrender_date == 'valid':
        json_data['surrenderDate'] = model_utils.format_ts(model_utils.now_ts())
    elif surrender_date == 'old':
        json_data['surrenderDate'] = model_utils.format_ts(model_utils.today_ts_offset(22, False))
    elif surrender_date == '21':
        json_data['surrenderDate'] = model_utils.format_ts(model_utils.now_ts_offset(21, False))
    elif surrender_date == 'junk':
        json_data['surrenderDate'] = 'invalid date'
    if desc != DESC_INCLUDES_GC:
        del json_data['generalCollateral']
    if desc == DESC_MISSING_VC:
        del json_data['vehicleCollateral']
    elif desc == DESC_VC_MH:
        json_data['vehicleCollateral'][0]['type'] = 'MH'

    error_msg = validator.validate(json_data, 'PS12345')
    if valid:
        assert error_msg == ''
    elif message_content:
        # print(error_msg)
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,reg_type', TEST_EXCLUDED_TYPE_DATA)
def test_validate_excluded_type(session, desc, valid, reg_type):
    """Assert that financing statement excluded registration type validation works as expected."""
    # setup
    json_data = copy.deepcopy(FINANCING)
    json_data['type'] = reg_type
    error_msg = validator.validate(json_data, 'PS12345')
    if valid:
        assert error_msg == ''
    else:
        # print(error_msg)
        assert error_msg != ''
        assert error_msg.find(validator.TYPE_NOT_ALLOWED) != -1


@pytest.mark.parametrize('desc,valid,reg_type,message_content', TEST_FR_LT_MH_MN_DATA)
def test_validate_fr_lt_mh_mn(session, desc, valid, reg_type, message_content):
    """Assert that financing statement specific registration type validation works as expected."""
    # setup
    json_data = copy.deepcopy(FINANCING)
    json_data['type'] = reg_type
    if desc != DESC_EXCLUDES_LY:
        del json_data['lifeYears']
    if desc != DESC_INFINITY_INVALID:
        json_data['lifeInfinite'] = True
    else:
        json_data['lifeInfinite'] = False
    del json_data['trustIndenture']
    if desc != DESC_INCLUDES_GC:
        del json_data['generalCollateral']
    if desc == DESC_MISSING_VC:
        del json_data['vehicleCollateral']
    elif desc != DESC_VC_NOT_MH:
        json_data['vehicleCollateral'][0]['type'] = 'MH'

    error_msg = validator.validate(json_data, 'PS12345')
    if valid:
        assert error_msg == ''
    elif message_content:
        # print(error_msg)
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,message_content', TEST_PPSA_DATA)
def test_validate_ppsa(session, desc, valid, message_content):
    """Assert that financing statement ppsa class registration type validation works as expected."""
    # setup
    for reg_type in PPSATypes:
        if reg_type.value != 'RL':
            json_data = copy.deepcopy(FINANCING)
            json_data['type'] = reg_type.value
            del json_data['trustIndenture']
            if desc == DESC_INCLUDES_OT_DESC:
                json_data['otherTypeDescription'] = 'TEST OTHER DESC'
            elif desc == DESC_INCLUDES_TI:
                json_data['trustIndenture'] = True
                if reg_type.value == 'SA':
                    message_content = None
            if desc != DESC_ALL_LIFE:
                del json_data['lifeYears']
            else:
                if reg_type.value in ('FR', 'LT', 'MH'):
                    message_content = validator.LY_NOT_ALLOWED
                else:
                    message_content = validator.LIFE_INVALID
            json_data['lifeInfinite'] = True

            if reg_type.value in ('FL', 'FA', 'FS'):
                del json_data['vehicleCollateral']
            else:
                del json_data['generalCollateral']
                json_data['vehicleCollateral'][0]['type'] = 'MH'

            if desc == DESC_INCLUDES_LA:
                json_data['lienAmount'] = '1000'
            if desc == DESC_INCLUDES_SD:
                json_data['surrenderDate'] = '2030-06-15T00:00:00-07:00'

            # print('REG TYPE: ' + str(json_data['type']))
            error_msg = validator.validate(json_data, 'PS12345')
            if valid:
                assert error_msg == ''
            elif message_content:
                # print(error_msg)
                assert error_msg != ''
                assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,reg_type,message_content', TEST_MD_PT_SC_DATA)
def test_validate_md_pt_sc(session, desc, valid, reg_type, message_content):
    """Assert that new MD, PT, SC registration type validation works as expected."""
    # setup
    json_data = copy.deepcopy(FINANCING)
    json_data['type'] = reg_type
    del json_data['trustIndenture']
    if desc == DESC_MISSING_GC:
        del json_data['generalCollateral']
    if desc != DESC_INCLUDES_VC:
        del json_data['vehicleCollateral']
    json_data['lifeInfinite'] = True
    del json_data['lifeYears']

    error_msg = validator.validate(json_data, 'PS12345')
    if valid:
        assert error_msg == ''
    elif message_content:
        print(error_msg)
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,message_content', TEST_CROWN_DATA)
def test_validate_crown(session, desc, valid, message_content):
    """Assert that financing statement crown charge class registration type validation works as expected."""
    # setup
    for reg_type in CrownChargeTypes:
        if validator.validate_allowed_type(reg_type.value) != '':
            continue

        json_data = copy.deepcopy(FINANCING)
        json_data['type'] = reg_type.value
        del json_data['trustIndenture']
        if reg_type.value == 'OT' and desc != DESC_MISSING_OT_DESC:
            json_data['otherTypeDescription'] = 'TEST OTHER DESC'
            message_content = None
        elif reg_type.value != 'OT' and desc == DESC_INCLUDES_OT_DESC:
            json_data['otherTypeDescription'] = 'TEST OTHER DESC'
        elif desc == DESC_MISSING_OT_DESC or desc == DESC_INCLUDES_OT_DESC:
            message_content = None
        if desc != DESC_EXCLUDES_LY:
            del json_data['lifeYears']
        if desc != DESC_INFINITY_INVALID:
            json_data['lifeInfinite'] = True
        else:
            json_data['lifeInfinite'] = False
        if desc == DESC_MISSING_GC:
            del json_data['generalCollateral']
        if desc != DESC_INCLUDES_VC:
            del json_data['vehicleCollateral']

        # print('REG TYPE: ' + str(json_data['type']))
        error_msg = validator.validate(json_data, 'PS12345')
        if valid:
            assert error_msg == ''
        elif message_content:
            # print(error_msg)
            assert error_msg != ''
            assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,reg_type,message_content', TEST_FL_FA_FS_HN_WL_DATA)
def test_validate_fl_fa_fs_hn_wl(session, desc, valid, reg_type, message_content):
    """Assert that financing statement specific registration type validation works as expected."""
    # setup
    json_data = copy.deepcopy(FINANCING)
    json_data['type'] = reg_type
    del json_data['trustIndenture']
    del json_data['lifeYears']
    json_data['lifeInfinite'] = True
    if desc == DESC_MISSING_GC:
        del json_data['generalCollateral']
    if desc != DESC_INCLUDES_VC:
        del json_data['vehicleCollateral']
    error_msg = validator.validate(json_data, 'PS12345')
    if valid:
        assert error_msg == ''
    elif message_content:
        # print(error_msg)
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,reg_type,message_content', TEST_MISC_DATA)
def test_validate_misc(session, desc, valid, reg_type, message_content):
    """Assert that financing statement miscellaneous class registration type validation works as expected."""
    # setup
    json_data = copy.deepcopy(FINANCING)
    json_data['type'] = reg_type
    del json_data['trustIndenture']
    if desc != DESC_INFINITY_INVALID:
        json_data['lifeInfinite'] = True
    else:
        json_data['lifeInfinite'] = False
    if desc != DESC_EXCLUDES_LY:
        del json_data['lifeYears']
    if reg_type != 'MN':
        del json_data['vehicleCollateral']
    else:
        del json_data['generalCollateral']
        json_data['vehicleCollateral'][0]['type'] = 'MH'

    error_msg = validator.validate(json_data, 'PS12345')
    if valid:
        assert error_msg == ''
    elif message_content:
        print(error_msg)
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,valid,message_content', TEST_AUTHORIZATION_DATA)
def test_validate_authorization(session, desc, valid, message_content):
    """Assert that financing statement authorization received validation works as expected."""
    # setup
    json_data = copy.deepcopy(FINANCING)
    if desc == DESC_MISSING_AC:
        del json_data['authorizationReceived']
    elif desc == DESC_INVALID_AC:
        json_data['authorizationReceived'] = False

    # test
    error_msg = validator.validate(json_data, 'PS12345')
    if valid:
        assert error_msg == ''
    elif message_content:
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


def test_validate_sc_ap(session):
    """Assert that financing statement serial collateral AP type validation works as expected."""
    # setup
    json_data = copy.deepcopy(FINANCING)
    json_data['vehicleCollateral'][0]['type'] = 'AP'
    error_msg = validator.validate(json_data, 'PS12345')
    # print(error_msg)
    assert error_msg != ''
    assert error_msg.find(validator.VC_AP_NOT_ALLOWED) != -1


@pytest.mark.parametrize('desc,valid,reg_type,today_offset,message_content', TEST_DATA_TYPE_ENABLED)
def test_validate_type_enabled(session, desc, valid, reg_type, today_offset, message_content):
    """Assert that financing statement registration type enabled validation works as expected."""
    if today_offset:
        now_offset = model_utils.now_ts_offset(today_offset, True)
        r_type: RegistrationType = RegistrationType.find_by_registration_type(reg_type)
        r_type.act_ts = now_offset
        session.add(r_type)
        session.commit()
        logger.info(r_type.act_ts)
    json_data = copy.deepcopy(FINANCING)
    json_data['type'] = reg_type
    del json_data['trustIndenture']
    if reg_type == RegistrationTypes.RL.value:
        del json_data['lifeYears']
        del json_data['lifeInfinite']
        del json_data['generalCollateral']
        json_data['lienAmount'] = 10000
        json_data['surrenderDate'] = model_utils.format_ts(model_utils.now_ts())
    else:
        json_data['lifeYears'] = 5
        del json_data['lifeInfinite']

    # test
    error_msg = validator.validate(json_data, 'PS12345')
    if valid:
        assert error_msg == ''
    elif message_content:
        assert error_msg != ''
        assert error_msg.find(message_content) != -1
