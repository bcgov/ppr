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

from ppr_api.models import FinancingStatement
from ppr_api.utils.validators import registration_validator as validator


AMENDMENT_VALID = {
  'statementType': 'AMENDMENT_STATEMENT',
  'baseDebtor': {
      'businessName': 'DEBTOR 1 INC.'
  },
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


# testdata pattern is ({description}, {registration data}, {valid}, {message contents})
TEST_COLLATERAL_IDS_DATA = [
    ('Valid collateral IDs', AMENDMENT_VALID, True, None),
    ('Missing delete vehicle id', AMENDMENT_INVALID, False, validator.DELETE_MISSING_ID_VEHICLE)
]


@pytest.mark.parametrize('desc,json_data,valid,message_content', TEST_COLLATERAL_IDS_DATA)
def test_validate_collateral_ids(session, desc, json_data, valid, message_content):
    """Assert that registration delete collateral id provided validation works as expected."""
    error_msg = validator.validate_collateral_ids(json_data)
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
    error_msg = validator.validate_collateral_ids(json_data, statement)
    assert error_msg != ''
    assert error_msg.find('Invalid vehicleId') != -1
    json_data['deleteVehicleCollateral'][0]['vehicleId'] = statement.vehicle_collateral[0].id
    error_msg = validator.validate_collateral_ids(json_data, statement)
    if error_msg != '':
        print(error_msg)
    assert error_msg == ''
