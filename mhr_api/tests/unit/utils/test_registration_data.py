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
"""New MH registration test data defined here."""


SO_VALID = [
    {
        'groupId': 2,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'SOLE'
    }
]
JT_VALID = [
    {
        'groupId': 2,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            },
            {
            'individualName': {
                'first': 'John',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'JOINT'
    }
]
SO_OWNER_MULTIPLE = [
    {
        'groupId': 2,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            },
            {
            'individualName': {
                'first': 'John',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'SOLE'
    }
]
SO_GROUP_MULTIPLE = [
    {
        'groupId': 2,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'SOLE'
    },
    {
        'groupId': 3,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'SOLE'
    }
]
JT_OWNER_SINGLE = [
    {
        'groupId': 2,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'JOINT'
    }
]
TC_GROUPS_VALID = [
    {
        'groupId': 1,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'COMMON',
        'interest': 'UNDIVIDED 1/2',
        'interestNumerator': 1,
        'interestDenominator': 2
    },
    {
        'groupId': 2,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }, {
            'individualName': {
                'first': 'Jane',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'JOINT',
        'interest': 'UNDIVIDED',
        'interestNumerator': 1,
        'interestDenominator': 2
    }
]
TC_GROUP_VALID = {
    'owners': [
        {
        'individualName': {
            'first': 'James',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
        },
        'phoneNumber': '6041234567'
        }, {
        'individualName': {
            'first': 'Jane',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
        }
        }
    ],
    'type': 'JOINT',
    'interest': 'UNDIVIDED',
    'interestNumerator': 1,
    'interestDenominator': 2
}
INTEREST_VALID_1 = [
    { 'numerator': 1, 'denominator': 2 }, { 'numerator': 1, 'denominator': 2 }
]
INTEREST_VALID_2 = [
    { 'numerator': 1, 'denominator': 2 }, { 'numerator': 1, 'denominator': 4 }, { 'numerator': 1, 'denominator': 4 }
]
INTEREST_VALID_3 = [
    { 'numerator': 1, 'denominator': 10 }, { 'numerator': 1, 'denominator': 2 }, { 'numerator': 2, 'denominator': 5 }
]
INTEREST_INVALID_1 = [
    { 'numerator': 1, 'denominator': 2 }, { 'numerator': 1, 'denominator': 4 }
]
INTEREST_INVALID_2 = [
    { 'numerator': 1, 'denominator': 2 }, { 'numerator': 2, 'denominator': 4 }, { 'numerator': 1, 'denominator': 4 }
]
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
    'pad': '2',
    'additionalDescription': 'TEST PARK'
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
    'leaveProvince': False,
    'additionalDescription': 'TEST RESERVE'
}
LOCATION_OTHER = {
    'locationType': 'OTHER',
    'address': {
        'street': '7612 LUDLOM RD.',
        'city': 'DEKA LAKE',
        'region': 'BC',
        'country': 'CA',
        'postalCode': ''
    },
    'pidNumber': '007351119',
    'leaveProvince': False,
    'additionalDescription': 'TEST OTHER'
}
LOCATION_STRATA = {
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
    'taxExpiryDate': '2035-01-31T08:00:00+00:00',
    'additionalDescription': 'TEST STRATA'
}
LOCATION_MANUFACTURER = {
    'locationType': 'MANUFACTURER',
    'address': {
      'street': '1117 GLENDALE AVENUE',
      'city': 'SALMO',
      'region': 'BC',
      'country': 'CA',
      'postalCode': ''
    },
    'leaveProvince': False,
    'dealerName': 'DEALER-MANUFACTURER NAME',
    'additionalDescription': 'TEST MANUFACTURER'
}
SO_VALID_EXEC = {
    'groupId': 1,
    'owners': [
        {
        'individualName': {
            'first': 'James',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
        },
        'phoneNumber': '6041234567',
        'partyType': 'EXECUTOR',
        'description': 'EXECUTOR of the deceased.'
    }
    ],
    'type': 'SOLE'
}
SO_VALID_TRUSTEE = {
    'groupId': 1,
    'owners': [
        {
        'individualName': {
            'first': 'James',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
        },
        'phoneNumber': '6041234567',
        'partyType': 'TRUSTEE',
        'description': 'Trustee of the deceased, a bankrupt.'
    }
    ],
    'type': 'SOLE'
}
SO_VALID_ADMIN = {
    'groupId': 1,
    'owners': [
        {
        'individualName': {
            'first': 'James',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
        },
        'phoneNumber': '6041234567',
        'partyType': 'ADMINISTRATOR',
        'description': 'ADMINISTRATOR of the deceased.'
    }
    ],
    'type': 'SOLE'
}
JT_VALID_EXEC = {
    'groupId': 1,
    'owners': [
        {
        'individualName': {
            'first': 'James',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
        },
        'phoneNumber': '6041234567',
        'partyType': 'EXECUTOR',
        'description': 'EXECUTOR of the deceased.'
    }, {
        'individualName': {
            'first': 'Jane',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
        },
        'phoneNumber': '6041234567',
        'partyType': 'EXECUTOR',
        'description': 'EXECUTOR of the deceased.'
    }
    ],
    'type': 'NA'
}
JT_VALID_TRUSTEE = {
    'groupId': 1,
    'owners': [
        {
        'individualName': {
            'first': 'James',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
        },
        'phoneNumber': '6041234567',
        'partyType': 'TRUSTEE',
        'description': 'Trustee of the deceased, a bankrupt.'
    },{
        'individualName': {
            'first': 'Jane',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
        },
        'phoneNumber': '6041234567',
        'partyType': 'TRUSTEE',
        'description': 'Trustee of the deceased, a bankrupt.'
    }
    ],
    'type': 'NA'
}
JT_VALID_ADMIN = {
    'groupId': 1,
    'owners': [
        {
        'individualName': {
            'first': 'James',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
        },
        'phoneNumber': '6041234567',
        'partyType': 'ADMINISTRATOR',
        'description': 'ADMINISTRATOR of the deceased.'
    },{
        'individualName': {
            'first': 'Jane',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
        },
        'phoneNumber': '6041234567',
        'partyType': 'ADMINISTRATOR',
        'description': 'ADMINISTRATOR of the deceased.'
    }
    ],
    'type': 'NA'
}
TC_VALID_EXEC = {
    'groupId': 2,
    'owners': [
        {
        'individualName': {
            'first': 'James',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
        },
        'phoneNumber': '6041234567',
        'partyType': 'EXECUTOR',
        'description': 'EXECUTOR of the deceased.'
    }
    ],
    'type': 'NA'
}
TC_VALID_TRUSTEE = {
    'groupId': 2,
    'owners': [
        {
        'individualName': {
            'first': 'James',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
        },
        'phoneNumber': '6041234567',
        'partyType': 'TRUSTEE',
        'description': 'Trustee of the deceased, a bankrupt.'
    }
    ],
    'type': 'NA'
}
TC_VALID_ADMIN = {
    'groupId': 2,
    'owners': [
        {
        'individualName': {
            'first': 'James',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
        },
        'phoneNumber': '6041234567',
        'partyType': 'ADMINISTRATOR',
        'description': 'ADMINISTRATOR of the deceased.'
    }
    ],
    'type': 'NA'
}
