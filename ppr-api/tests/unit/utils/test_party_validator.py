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
"""Party validator tests."""
import copy

import pytest

from flask import current_app

from ppr_api.models import FinancingStatement
from ppr_api.utils.validators import party_validator as validator


FINANCING_VALID = {
    'type': 'SA',
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
        },
        {
            'businessName': 'BANK OF BRITISH COLUMBIA',
            'address': {
                'street': '1234 BEACON AVENUE',
                'city': 'SIDNEY',
                'region': 'BC',
                'country': 'CA',
                'postalCode': 'V7R 1R7'
            },
            'partyId': 1321096
        },
        {
            'code': '200000000'
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
    ]
}
FINANCING_INVALID = {
    'type': 'SA',
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
    'securedParties': [
        {
            'businessName': 'BANK OF BRITISH COLUMBIA',
            'address': {
                'street': '3720 BEACON AVENUE',
                'city': 'SIDNEY',
                'region': 'BC',
                'country': 'XX',
                'postalCode': 'V7R 1R7'
            },
            'partyId': 1321095
        },
        {
            'businessName': 'BANK OF BRITISH COLUMBIA',
            'address': {
                'street': '3720 BEACON AVENUE',
                'city': 'SIDNEY',
                'region': 'BX',
                'country': 'CA',
                'postalCode': 'V7R 1R7'
            },
            'partyId': 1321096
        },
        {
            'code': '300000000'
        }
    ],
    'debtors': [
        {
            'businessName': 'Brown Window Cleaning Inc.',
            'address': {
                'street': '1234 Blanshard St',
                'city': 'Victoria',
                'region': 'BC',
                'country': 'US',
                'postalCode': 'V8S 3J5'
             },
            'emailAddress': 'csmith@bwc.com',
            'partyId': 1400094
        }
    ]
}

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
    },
    {
      'code': '200000000',
      'businessName': 'BANK OF BRITISH COLUMBIA',
      'address': {
          'street': '1234 BEACON AVENUE',
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
      'description': 'Fridges and stoves. Proceeds: Accts Receivable.',
      'collateralId': 123435
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

AMENDMENT_INVALID_NAMES = {
  'statementType': 'AMENDMENT_STATEMENT',
  'baseDebtor': {
      'businessName': 'DEBTOR 1 INC.'
  },
  'registeringParty': {
      'businessName': 'RP \U0001d5c4\U0001d5c6/\U0001d5c1',
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
  'addDebtors': [
    {
        'businessName': 'AD \U0001d5c4\U0001d5c6/\U0001d5c1',
        'address': {
            'street': '1234 Blanshard St',
            'city': 'Victoria',
            'region': 'BC',
            'country': 'CA',
            'postalCode': 'V8S 3J5'
        }
    }
  ],
  'addSecuredParties': [
    {
      'personName': {
          'first': 'FN répertoire',
          'middle': 'MN répertoire',
          'last': 'LN répertoire'
      }
    }
  ]
}

FINANCING_DUPLICATE_PARTIES_BUSINESS = {
  'securedParties': [
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
    },
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
    },
    {
      'code': '200000000',
      'personName': {
        'first': 'firstName',
        'middle': 'secondName',
        'last': 'lastName'
    },
      'address': {
          'street': '3721 BEACON AVENUE',
          'city': 'SIDNEY',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V7R 1R7'
      }
    }
  ]
}

FINANCING_DUPLICATE_PARTIES_PERSON = {
  'securedParties': [
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
    },
    {
      'code': '200000000',
      'personName': {
        'first': 'firstName',
        'middle': 'secondName',
        'last': 'lastName'
    },
      'address': {
          'street': '3721 BEACON AVENUE',
          'city': 'SIDNEY',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V7R 1R7'
      }
    },
    {
      'code': '200000000',
      'personName': {
        'first': 'firstName',
        'middle': 'secondName',
        'last': 'lastName'
    },
      'address': {
          'street': '3721 BEACON AVENUE',
          'city': 'SIDNEY',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V7R 1R7'
      }
    },
  ]
}

AMENDMENT_DUPLICATE_PARTIES_BUSINESS = {
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
    },
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
    },
    {
      'code': '200000000',
      'personName': {
        'first': 'firstName',
        'middle': 'secondName',
        'last': 'lastName'
    },
      'address': {
          'street': '3721 BEACON AVENUE',
          'city': 'SIDNEY',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V7R 1R7'
      }
    }
  ]
}

AMENDMENT_DUPLICATE_PARTIES_PERSON = {
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
    },
    {
      'code': '200000000',
      'personName': {
        'first': 'firstName',
        'middle': 'secondName',
        'last': 'lastName'
    },
      'address': {
          'street': '3721 BEACON AVENUE',
          'city': 'SIDNEY',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V7R 1R7'
      }
    },
    {
      'code': '200000000',
      'personName': {
        'first': 'firstName',
        'middle': 'secondName',
        'last': 'lastName'
    },
      'address': {
          'street': '3721 BEACON AVENUE',
          'city': 'SIDNEY',
          'region': 'BC',
          'country': 'CA',
          'postalCode': 'V7R 1R7'
      }
    }
  ]
}

FINANCING_INVALID_NAMES = {
    'type': 'SA',
    'registeringParty': {
        'businessName': 'RP \U0001d5c4\U0001d5c6/\U0001d5c1',
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
          'personName': {
              'first': 'FN répertoire',
              'middle': 'MN répertoire',
              'last': 'LN répertoire'
          },
          'address': {
              'street': '3720 BEACON AVENUE',
              'city': 'SIDNEY',
              'region': 'BC',
              'country': 'CA',
              'postalCode': 'V7R 1R7'
          },
          'partyId': 1321095
        },
    ],
    'debtors': [
        {
          'businessName': 'AD \U0001d5c4\U0001d5c6/\U0001d5c1',
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
    ]
}


# testdata pattern is ({description}, {financing statement data}, {valid}, {message contents})
TEST_CODE_FS_DATA = [
    ('Valid party codes', FINANCING_VALID, True, None),
    ('Invalid party codes', FINANCING_INVALID, False, validator.REGISTERING_CODE_MSG.format('300000001'))
]
# testdata pattern is ({description}, {financing statement data}, {valid}, {message contents})
TEST_ADDRESS_FS_DATA = [
    ('Valid addresses', FINANCING_VALID, True, None),
    ('Invalid registering address', FINANCING_INVALID, False, validator.INVALID_COUNTRY_REGISTERING.format('XX')),
    ('Invalid secured address region', FINANCING_INVALID, False, validator.INVALID_REGION_SECURED.format('BX')),
    ('Invalid secured address country', FINANCING_INVALID, False, validator.INVALID_COUNTRY_SECURED.format('XX')),
    ('Invalid debtor address', FINANCING_INVALID, False, validator.INVALID_REGION_DEBTOR.format('BC'))
]
# testdata pattern is ({description}, {financing statement data}, {valid}, {message contents})
TEST_PARTIES_FS_DATA = [
    ('Valid parties', FINANCING_VALID, True, None),
    ('Invalid party code', FINANCING_INVALID, False, validator.SECURED_CODE_MSG.format('300000000')),
    ('Invalid party address', FINANCING_INVALID, False, validator.INVALID_REGION_SECURED.format('BX'))
]
# testdata pattern is ({description}, {financing statement data}, {valid}, {message contents})
TEST_PARTY_IDS_AM_DATA = [
    ('Valid party IDs', AMENDMENT_VALID, True, None),
    ('Missing delete secured id', AMENDMENT_INVALID, False, validator.DELETE_MISSING_ID_SECURED),
    ('Missing delete debtor id', AMENDMENT_INVALID, False, validator.DELETE_MISSING_ID_DEBTOR)
]
# testdata pattern is ({description}, {financing statement data}, {valid}, {message contents})
TEST_CODE_AM_DATA = [
    ('Valid party codes', AMENDMENT_VALID, True, None),
    ('Invalid party codes', AMENDMENT_INVALID, False, validator.SECURED_CODE_MSG.format('300000000'))
]
# testdata pattern is ({description}, {financing statement data}, {valid}, {message contents})
TEST_ADDRESS_AM_DATA = [
    ('Valid addresses', AMENDMENT_VALID, True, None),
    ('Invalid registering address', AMENDMENT_INVALID, False, validator.INVALID_COUNTRY_REGISTERING.format('XX')),
    ('Invalid secured address', AMENDMENT_INVALID, False, validator.INVALID_REGION_SECURED.format('BX')),
    ('Invalid debtor address', AMENDMENT_INVALID, False, validator.INVALID_REGION_DEBTOR.format('BC'))
]
# testdata pattern is ({description}, {financing statement data}, {valid}, {message contents})
TEST_PARTIES_AM_DATA = [
    ('Valid parties', AMENDMENT_VALID, True, None),
    ('Invalid party code', AMENDMENT_INVALID, False, validator.SECURED_CODE_MSG.format('300000000')),
    ('Invalid party address', AMENDMENT_INVALID, False, validator.INVALID_REGION_SECURED.format('BX')),
    ('Missing delete debtor id', AMENDMENT_INVALID, False, validator.DELETE_MISSING_ID_DEBTOR)
]
# testdata pattern is ({description}, {amendment statement data}, {valid}, {message contents})
TEST_PARTIES_AM_NAME_DATA = [
    ('Valid names', AMENDMENT_VALID, True, None),
    ('Invalid registering party name', AMENDMENT_INVALID_NAMES, False,
     validator.CHARACTER_SET_UNSUPPORTED.format('RP \U0001d5c4\U0001d5c6/\U0001d5c1')),
    ('Invalid debtor name', AMENDMENT_INVALID_NAMES, False,
     validator.CHARACTER_SET_UNSUPPORTED.format('AD \U0001d5c4\U0001d5c6/\U0001d5c1')),
    ('Invalid secured party first name', AMENDMENT_INVALID_NAMES, False,
     validator.CHARACTER_SET_UNSUPPORTED.format('FN répertoire')),
    ('Invalid secured party middle name', AMENDMENT_INVALID_NAMES, False,
     validator.CHARACTER_SET_UNSUPPORTED.format('MN répertoire')),
    ('Invalid secured party last name', AMENDMENT_INVALID_NAMES, False,
     validator.CHARACTER_SET_UNSUPPORTED.format('LN répertoire'))
]
# testdata pattern is ({description}, {amendment statement data}, {valid}, {message contents})
TEST_PARTIES_AM_DUPLICATES = [
    ('Valid parties', AMENDMENT_VALID, True, None),
    ('Duplicate party business', AMENDMENT_DUPLICATE_PARTIES_BUSINESS, False,
     validator.DUPLICATE_SECURED_PARTY_BUSINESS),
    ('Duplicate party person', AMENDMENT_DUPLICATE_PARTIES_PERSON, False,
     validator.DUPLICATE_SECURED_PARTY_PERSON)
]
# testdata pattern is ({description}, {data}, {valid}, {sp_amend_id}, {debtor_amend_id}, {message contents})
TEST_PARTIES_AM_EDIT_DATA = [
    ('Valid parties no amend id', AMENDMENT_VALID, True, None, None, None),
    ('Valid parties amend id 0', AMENDMENT_VALID, True, 0, 0, None),
    ('Valid secured party amend id', AMENDMENT_VALID, True, 1321095, 0, None),
    ('Valid debtor amend id', AMENDMENT_VALID, True, 0, 1321961, None),
    ('Invalid secured party amend id', AMENDMENT_VALID, False, 1321099, 0, validator.INVALID_AMEND_PARTY_ID_SECURED),
    ('Invalid debtor amend id', AMENDMENT_VALID, False, 0, 1321969, validator.INVALID_AMEND_PARTY_ID_DEBTOR)
]
# testdata pattern is ({description}, {amendment statement data}, {valid}, {message contents})
TEST_PARTIES_FS_NAME_DATA = [
    ('Valid names', FINANCING_VALID, True, None),
    ('Invalid registering party name', FINANCING_INVALID_NAMES, False,
     validator.CHARACTER_SET_UNSUPPORTED.format('RP \U0001d5c4\U0001d5c6/\U0001d5c1')),
    ('Invalid debtor name', FINANCING_INVALID_NAMES, False,
     validator.CHARACTER_SET_UNSUPPORTED.format('AD \U0001d5c4\U0001d5c6/\U0001d5c1')),
    ('Invalid secured party first name', FINANCING_INVALID_NAMES, False,
     validator.CHARACTER_SET_UNSUPPORTED.format('FN répertoire')),
    ('Invalid secured party middle name', FINANCING_INVALID_NAMES, False,
     validator.CHARACTER_SET_UNSUPPORTED.format('MN répertoire')),
    ('Invalid secured party last name', FINANCING_INVALID_NAMES, False,
     validator.CHARACTER_SET_UNSUPPORTED.format('LN répertoire'))
]
# testdata pattern is ({description}, {amendment statement data}, {valid}, {message contents})
TEST_PARTIES_FS_DUPLICATES = [
    ('Valid parties', FINANCING_VALID, True, None),
    ('Duplicate party business', FINANCING_DUPLICATE_PARTIES_BUSINESS, False,
     validator.DUPLICATE_SECURED_PARTY_BUSINESS),
    ('Duplicate party person', FINANCING_DUPLICATE_PARTIES_PERSON, False,
     validator.DUPLICATE_SECURED_PARTY_PERSON)
]


@pytest.mark.parametrize('desc,json_data,valid,message_content', TEST_CODE_FS_DATA)
def test_validate_party_codes(session, desc, json_data, valid, message_content):
    """Assert that financing statement client party code validation works as expected."""
    error_msg = validator.validate_party_codes(json_data)
    if valid:
        assert error_msg == ''
    elif message_content:
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,json_data,valid,message_content', TEST_ADDRESS_FS_DATA)
def test_validate_party_addresses(session, desc, json_data, valid, message_content):
    """Assert that financing statement party address validation works as expected."""
    error_msg = validator.validate_party_addresses(json_data)
    if valid:
        assert error_msg == ''
    elif message_content:
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,json_data,valid,message_content', TEST_PARTIES_FS_DATA)
def test_validate_financing_parties(session, desc, json_data, valid, message_content):
    """Assert that financing statement party validation works as expected."""
    error_msg = validator.validate_financing_parties(json_data)
    if valid:
        assert error_msg == ''
    elif message_content:
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,json_data,valid,message_content', TEST_PARTY_IDS_AM_DATA)
def test_validate_party_ids(session, desc, json_data, valid, message_content):
    """Assert that registration delete party id provided validation works as expected."""
    error_msg = validator.validate_party_ids(json_data)
    if valid:
        assert error_msg == ''
    elif message_content:
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,json_data,valid,message_content', TEST_CODE_AM_DATA)
def test_validate_party_codes_registration(session, desc, json_data, valid, message_content):
    """Assert that registration statement client party code validation works as expected."""
    error_msg = validator.validate_party_codes(json_data)
    if valid:
        assert error_msg == ''
    elif message_content:
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,json_data,valid,message_content', TEST_ADDRESS_AM_DATA)
def test_validate_party_addresses_registration(session, desc, json_data, valid, message_content):
    """Assert that registration statement party address validation works as expected."""
    error_msg = validator.validate_party_addresses(json_data)
    if valid:
        assert error_msg == ''
    elif message_content:
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,json_data,valid,message_content', TEST_PARTIES_AM_DATA)
def test_validate_registration_parties(session, desc, json_data, valid, message_content):
    """Assert that registration statement party validation works as expected."""
    error_msg = validator.validate_registration_parties(json_data)
    current_app.logger.info(error_msg)
    if valid:
        assert error_msg == ''
    elif message_content:
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,json_data,valid,message_content', TEST_PARTIES_AM_DUPLICATES)
def test_validate_registration_party_duplicates(session, desc, json_data, valid, message_content):
    """Assert that registration statement party name validation works as expected."""
    error_msg = validator.validate_registration_parties(json_data)
    if valid:
        assert error_msg == ''
    elif message_content:
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,data,valid,sp_amend_id,debtor_amend_id,message_content', TEST_PARTIES_AM_EDIT_DATA)
def test_validate_amend_party_ids(session, desc, data, valid, sp_amend_id, debtor_amend_id, message_content):
    """Assert that amendment registration amend party id validation works as expected."""
    json_data = copy.deepcopy(data)
    if sp_amend_id:
        json_data['addSecuredParties'][0]['amendPartyId'] = sp_amend_id
    if debtor_amend_id:
        json_data['addDebtors'][0]['amendPartyId'] = debtor_amend_id
    error_msg = validator.validate_registration_parties(json_data)
    if sp_amend_id:
        assert json_data['addSecuredParties'][0]['amendPartyId'] == sp_amend_id
    else:
        assert 'amendPartyId' not in json_data['addSecuredParties'][0]
    if debtor_amend_id:
        assert json_data['addDebtors'][0]['amendPartyId'] == debtor_amend_id
    else:
        assert 'amendPartyId' not in json_data['addDebtors'][0]
          
    if valid:
        assert error_msg == ''
    elif message_content:
        assert error_msg != ''
        msg: str = ''
        if message_content == validator.INVALID_AMEND_PARTY_ID_SECURED:
            msg =  message_content.format(str(sp_amend_id))
        else:
            msg =  message_content.format(str(debtor_amend_id))
        assert error_msg.find(msg) != -1


def test_actual_party_ids(session):
    """Assert that delete party id validation works as expected on an existing financing statement."""
    json_data = copy.deepcopy(AMENDMENT_VALID)
    statement = FinancingStatement.find_by_registration_number('TEST0001', False)
    # example registration party ID's are bogus
    error_msg = validator.validate_party_ids(json_data, statement)
    assert error_msg != ''
    assert error_msg.find('Invalid partyId') != -1

    for party in statement.parties:
        if not party.registration_id_end and party.party_type == 'SP':
            json_data['deleteSecuredParties'][0]['partyId'] = party.id
        elif not party.registration_id_end and party.party_type in ('DB', 'DI'):
            json_data['deleteDebtors'][0]['partyId'] = party.id
    error_msg = validator.validate_party_ids(json_data, statement)
    if error_msg != '':
        print(error_msg)
    assert error_msg == ''


@pytest.mark.parametrize('desc,json_data,valid,message_content', TEST_PARTIES_AM_NAME_DATA)
def test_validate_am_party_names(session, desc, json_data, valid, message_content):
    """Assert that registration statement party name validation works as expected."""
    error_msg = validator.validate_party_names(json_data)
    if valid:
        assert error_msg == ''
    elif message_content:
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,json_data,valid,message_content', TEST_PARTIES_AM_DUPLICATES)
def test_validate_am_party_duplicates(session, desc, json_data, valid, message_content):
    """Assert that registration statement party name validation works as expected."""
    error_msg = validator.validate_party_names(json_data)
    if valid:
        assert error_msg == ''
    elif message_content:
        assert error_msg != ''
        assert error_msg.find(message_content) != -1


@pytest.mark.parametrize('desc,json_data,valid,message_content', TEST_PARTIES_FS_NAME_DATA)
def test_validate_fs_party_names(session, desc, json_data, valid, message_content):
    """Assert that financing statement party name validation works as expected."""
    error_msg = validator.validate_party_names(json_data)
    if valid:
        assert error_msg == ''
    elif message_content:
        assert error_msg != ''
        assert error_msg.find(message_content) != -1
