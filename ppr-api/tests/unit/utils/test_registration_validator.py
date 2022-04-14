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

from ppr_api.models import FinancingStatement, utils as model_utils
from ppr_api.models.registration import CrownChargeTypes
from ppr_api.utils.validators import registration_validator as validator


AMENDMENT_VALID = {
  'statementType': 'AMENDMENT_STATEMENT',
  'baseDebtor': {
      'businessName': 'DEBTOR 1 INC.'
  },
  'authorizationReceived': True,
  'registeringParty': {
      'code': '200000001',
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
  'changeType': 'AM',
  'deleteDebtors': [
    {
        'businessName': 'Brawn Window Cleaning Inc.',
        'address': {
            'street': '1234 Blanshard St',
            'city': 'Victoria',
            'region': 'BC',
            'country': 'CA',
            'postalCode': 'V8S 3J5'
        },
        'partyId': 1321961
    }
  ],
  'addDebtors': [
    {
        'businessName': 'Brown Window Cleaning Inc.',
        'address': {
            'street': '1234 Blanshard St',
            'city': 'Victoria',
            'region': 'BC',
            'country': 'CA',
            'postalCode': 'V8S 3J5'
        }
    }
  ],
  'deleteSecuredParties': [
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
  'addSecuredParties': [
    {
      'code': '200000000',
      'businessName': 'BANK OF BRITISH COLUMBIA',
      'address': {
          'street': '3721 BEACON AVENUE',
          'city': 'SIDNEY',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V7R 1R7'
      }
    }
  ],
  'deleteVehicleCollateral': [
    {
      'type': 'MV',
      'serialNumber': 'KNADM5A39E6904135',
      'year': 2014,
      'make': 'KIA',
      'model': 'RIO',
      'vehicleId': 974124
    }
  ],
  'addVehicleCollateral': [
    {
      'type': 'MV',
      'serialNumber': 'KM8J3CA46JU622994',
      'year': 2018,
      'make': 'HYUNDAI',
      'model': 'TUCSON'
    }
  ],
  'deleteGeneralCollateral': [
    {
      'description': 'Fridges and stoves. Proceeds: Accts Receivable.'
    }
  ],
  'addGeneralCollateral': [
    {
      'description': '1985 white Fender Stratocaster Guitar #1234'
    }
  ]
}

AMENDMENT_INVALID = {
  'statementType': 'AMENDMENT_STATEMENT',
  'baseDebtor': {
      'businessName': 'DEBTOR 1 INC.'
  },
  'authorizationReceived': True,
  'registeringParty': {
      'code': '300000001',
      'businessName': 'ABC SEARCHING COMPANY',
      'address': {
          'street': '222 SUMMER STREET',
          'city': 'VICTORIA',
          'region': 'BC',
          'country': 'XX',
          'postalCode': 'V8W 2V8'
      },
      'emailAddress': 'bsmith@abc-search.com'
  },
  'changeType': 'AM',
  'deleteDebtors': [
    {
        'businessName': 'Brawn Window Cleaning Inc.',
        'address': {
            'street': '1234 Blanshard St',
            'city': 'Victoria',
            'region': 'BC',
            'country': 'CA',
            'postalCode': 'V8S 3J5'
        }
    }
  ],
  'addDebtors': [
    {
        'businessName': 'Brown Window Cleaning Inc.',
        'address': {
            'street': '1234 Blanshard St',
            'city': 'Victoria',
            'region': 'BC',
            'country': 'US',
            'postalCode': 'V8S 3J5'
          }
    }
  ],
  'deleteSecuredParties': [
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
  ],
  'addSecuredParties': [
    {
      'code': '300000000',
      'businessName': 'BANK OF BRITISH COLUMBIA',
      'address': {
          'street': '3721 BEACON AVENUE',
          'city': 'SIDNEY',
          'region': 'BX',
          'country': 'CA',
          'postalCode': 'V7R 1R7'
      }
    }
  ],
  'deleteVehicleCollateral': [
    {
      'type': 'MV',
      'serialNumber': 'KNADM5A39E6904135',
      'year': 2014,
      'make': 'KIA',
      'model': 'RIO'
    }
  ],
  'addVehicleCollateral': [
    {
      'type': 'MV',
      'serialNumber': 'KM8J3CA46JU622994',
      'year': 2018,
      'make': 'HYUNDAI',
      'model': 'TUCSON'
    }
  ],
  'deleteGeneralCollateral': [
    {
      'description': 'Fridges and stoves. Proceeds: Accts Receivable.'
    }
  ],
  'addGeneralCollateral': [
    {
      'description': '1985 white Fender Stratocaster Guitar #1234'
    }
  ]
}
RENEWAL_SA_VALID = {
    'baseRegistrationNumber': 'TEST0001',
    'clientReferenceId': 'A-00000402',
    'authorizationReceived': True,
    'debtorName': {
        'businessName': 'TEST BUS 2 DEBTOR'
    },
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
    'lifeYears': 5
}
RENEWAL_SA_INFINITE_VALID = {
    'baseRegistrationNumber': 'TEST0001',
    'clientReferenceId': 'A-00000402',
    'authorizationReceived': True,
    'debtorName': {
        'businessName': 'TEST BUS 2 DEBTOR'
    },
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
    'lifeInfinite': True
}
RENEWAL_SA_LIFE_INVALID = {
    'baseRegistrationNumber': 'TEST0001',
    'clientReferenceId': 'A-00000402',
    'authorizationReceived': True,
    'debtorName': {
        'businessName': 'TEST BUS 2 DEBTOR'
    },
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
    'lifeYears': 5,
    'lifeInfinite': True
}
RENEWAL_SA_LIFE_MISSING = {
    'baseRegistrationNumber': 'TEST0001',
    'clientReferenceId': 'A-00000402',
    'authorizationReceived': True,
    'debtorName': {
        'businessName': 'TEST BUS 2 DEBTOR'
    },
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
    }
}
RENEWAL_SA_INVALID = {
    'baseRegistrationNumber': 'TEST0001',
    'clientReferenceId': 'A-00000402',
    'authorizationReceived': True,
    'debtorName': {
        'businessName': 'TEST BUS 2 DEBTOR'
    },
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
    'lifeYears': 5,
    'courtOrderInformation': {
      'courtName': 'Supreme Court of British Columbia.',
      'courtRegistry': 'VICTORIA',
      'fileNumber': 'BC123495',
      'orderDate': '2021-09-05T07:01:00+00:00',
      'effectOfOrder': 'Court Order to renew Repairers Lien.'
    }
}
RENEWAL_RL_VALID = {
    'baseRegistrationNumber': 'TEST0017',
    'clientReferenceId': 'A-00000402',
    'authorizationReceived': True,
    'debtorName': {
        'businessName': 'TEST BUS 2 DEBTOR'
    },
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
    'courtOrderInformation': {
      'courtName': 'Supreme Court of British Columbia.',
      'courtRegistry': 'VICTORIA',
      'fileNumber': 'BC123495',
      'orderDate': '2021-09-05T07:01:00+00:00',
      'effectOfOrder': 'Court Order to renew Repairers Lien.'
    }
}
RENEWAL_RL_MISSING = {
    'baseRegistrationNumber': 'TEST0017',
    'clientReferenceId': 'A-00000402',
    'authorizationReceived': True,
    'debtorName': {
        'businessName': 'TEST BUS 2 DEBTOR'
    },
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
    }
}
RENEWAL_RL_INVALID_DATE = {
    'baseRegistrationNumber': 'TEST0017',
    'clientReferenceId': 'A-00000402',
    'authorizationReceived': True,
    'debtorName': {
        'businessName': 'TEST BUS 2 DEBTOR'
    },
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
    'lifeYears': 5,
    'courtOrderInformation': {
      'courtName': 'Supreme Court of British Columbia.',
      'courtRegistry': 'VICTORIA',
      'fileNumber': 'BC123495',
      'orderDate': '2021-08-05T07:01:00+00:00',
      'effectOfOrder': 'Court Order to renew Repairers Lien.'
    }
}
RENEWAL_RL_LIFE_INFINITE = {
    'baseRegistrationNumber': 'TEST0017',
    'clientReferenceId': 'A-00000402',
    'authorizationReceived': True,
    'debtorName': {
        'businessName': 'TEST BUS 2 DEBTOR'
    },
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
    'lifeInfinite': True,
    'courtOrderInformation': {
      'courtName': 'Supreme Court of British Columbia.',
      'courtRegistry': 'VICTORIA',
      'fileNumber': 'BC123495',
      'orderDate': '2021-09-05T07:01:00+00:00',
      'effectOfOrder': 'Court Order to renew Repairers Lien.'
    }
}


DESC_MISSING_AC = 'Missing authorizaton received'
DESC_INVALID_AC = 'Invalid authorizaton received'

# testdata pattern is ({description}, {registration data}, {valid}, {message contents})
TEST_COLLATERAL_IDS_DATA = [
    ('Valid collateral IDs', AMENDMENT_VALID, True, None),
    ('Missing delete vehicle id', AMENDMENT_INVALID, False, validator.DELETE_MISSING_ID_VEHICLE)
]
# testdata pattern is ({description}, {valid}, {message content})
TEST_AUTHORIZATION_DATA = [
    (DESC_MISSING_AC, False, validator.AUTHORIZATION_INVALID),
    (DESC_INVALID_AC, False, validator.AUTHORIZATION_INVALID)
]
# testdata pattern is ({base_reg_num}, {json_data}, {valid}, {message content})
TEST_RENEWAL_DATA = [
    ('TEST0001', RENEWAL_SA_VALID, True, None),
    ('TEST0001', RENEWAL_SA_INFINITE_VALID, True, None),
    ('TEST0017', RENEWAL_RL_VALID, True, None),
    ('TEST0001', RENEWAL_SA_INVALID, False, 'CourtOrderInformation is not allowed'),
    ('TEST0012', RENEWAL_SA_VALID, False, validator.RENEWAL_INVALID),
    ('TEST0001', RENEWAL_SA_LIFE_MISSING, False, validator.LIFE_MISSING),
    ('TEST0001', RENEWAL_SA_LIFE_INVALID, False, validator.LIFE_INVALID),
    ('TEST0017', RENEWAL_RL_MISSING, False, validator.COURT_ORDER_MISSING),
    ('TEST0017', RENEWAL_RL_LIFE_INFINITE, False, validator.LI_NOT_ALLOWED),
    ('TEST0017', RENEWAL_RL_INVALID_DATE, False, validator.COURT_ORDER_INVALID_DATE)
]


@pytest.mark.parametrize('desc,json_data,valid,message_content', TEST_COLLATERAL_IDS_DATA)
def test_validate_collateral(session, desc, json_data, valid, message_content):
    """Assert that registration delete collateral id provided validation works as expected."""
    error_msg = validator.validate_collateral(json_data)
    if valid:
        assert error_msg == ''
    elif message_content:
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


def test_actual_collateral_ids(session):
    """Assert that delete collateral id validation works as expected on an existing financing statement."""
    json_data = copy.deepcopy(AMENDMENT_VALID)
    statement = FinancingStatement.find_by_registration_number('TEST0001', False)
    # example registration collateral ID's are bogus
    error_msg = validator.validate_collateral(json_data, statement)
    assert error_msg != ''
    assert error_msg.find('Invalid vehicleId') != -1
    json_data['deleteVehicleCollateral'][0]['vehicleId'] = statement.vehicle_collateral[0].id
    error_msg = validator.validate_collateral(json_data, statement)
    if error_msg != '':
        print(error_msg)
    assert error_msg == ''


@pytest.mark.parametrize('desc,valid,message_content', TEST_AUTHORIZATION_DATA)
def test_validate_authorization(session, desc, valid, message_content):
    """Assert that financing statement authorization received validation works as expected."""
    # setup
    json_data = copy.deepcopy(AMENDMENT_VALID)
    if desc == DESC_MISSING_AC:
        del json_data['authorizationReceived']
    elif desc == DESC_INVALID_AC:
        json_data['authorizationReceived'] = False

    # test
    error_msg = validator.validate_registration(json_data)
    if valid:
        assert error_msg == ''
    elif message_content:
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


# testdata pattern is ({base_reg_num}, {json_data}, {valid}, {message content})
@pytest.mark.parametrize('base_reg_num,json_data,valid,message_content', TEST_RENEWAL_DATA)
def test_validate_renewal(session, base_reg_num, json_data, valid, message_content):
    """Assert that renewal registration extra validation works as expected."""
    # setup
    statement = FinancingStatement.find_by_registration_number(base_reg_num, 'PS12345')
    if base_reg_num == 'TEST0012':
        statement.life = model_utils.LIFE_INFINITE
    # test
    error_msg = validator.validate_renewal(json_data, statement)
    if valid:
        assert error_msg == ''
    elif message_content:
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


def test_validate_sc_ap(session):
    """Assert that financing statement serial collateral AP type validation works as expected."""
    # setup
    json_data = copy.deepcopy(AMENDMENT_VALID)
    json_data['addVehicleCollateral'][0]['type'] = 'AP'
    error_msg = validator.validate_registration(json_data)
    # print(error_msg)
    assert error_msg != ''
    assert error_msg.find(validator.VC_AP_NOT_ALLOWED) != -1


def test_amend_crown_charge_sc(session):
    """Assert that crown charge amdendments that add/remove serial collateral pass validation."""
    statement = FinancingStatement.find_by_registration_number('TEST0001', False)
    json_data = copy.deepcopy(AMENDMENT_VALID)
    json_data['deleteVehicleCollateral'][0]['vehicleId'] = statement.vehicle_collateral[0].id
    for reg_type in CrownChargeTypes:
        statement.type = reg_type.value 
        error_msg = validator.validate_collateral(json_data, statement)
        if error_msg != '':
            print(error_msg)
        assert error_msg == ''
