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
"""Transfer registration test data defined here."""


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
TC_GROUP_TRANSFER_DELETE = [
    {
        'groupId': 4,
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
    }
]
TC_GROUP_TRANSFER_ADD = [
    {
        'groupId': 5,
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
TC_GROUP_TRANSFER_ADD2 = [
    {
        'groupId': 5,
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
    }, {
        'groupId': 6,
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
        'interest': 'UNDIVIDED',
        'interestNumerator': 1,
        'interestDenominator': 2
    }
]
TC_GROUP_TRANSFER_DELETE_2 = [
    {
        'groupId': 3,
        'owners': [
            {
            'organizationName': 'BRANDON CONSTRUCTION MANAGEMENT LTD.',
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
        'interest': 'UNDIVIDED',
        'interestNumerator': 4,
        'interestDenominator': 10
    }
]

TRAND_DELETE_GROUPS = [
    {
        'groupId': 3,
        'owners': [
            {
                'individualName': {
                    'first': 'ROBERT',
                    'middle': 'JOHN',
                    'last': 'MOWAT'
                },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567'
            }, {
                'individualName': {
                    'first': 'KAREN',
                    'middle': 'PATRICIA',
                    'last': 'MOWAT'
                },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567',
                'deathCertificateNumber': '232432432',
                'deathDateTime': '2021-02-21T18:56:00+00:00'
            }
        ],
        'type': 'JOINT'
    }
]
TRAND_ADD_GROUPS = [
    {
        'groupId': 4,
        'owners': [
            {
            'individualName': {
                'first': 'ROBERT',
                'middle': 'JOHN',
                'last': 'MOWAT'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': 'V8S 4I6',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'SOLE'
    }
]
TRAND_DELETE_GROUPS2 = [
    {
        'groupId': 1,
        'owners': [
            {
                'individualName': {
                    'first': 'DENNIS',
                    'last': 'HALL'
                },
                'address': {
                    'street': 'SS 2, COMP. 2, SITE 19',
                    'city': 'FORT ST. JOH',
                    'region': 'BC',
                    'postalCode': ' ',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567'
            }, {
                'individualName': {
                    'first': 'SHARON',
                    'last': 'HALL'
                },
                'address': {
                    'street': 'SS 2, COMP. 2, SITE 19',
                    'city': 'FORT ST. JOH',
                    'region': 'BC',
                    'postalCode': ' ',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567',
                'deathCertificateNumber': '232432432',
                'deathDateTime': '2021-02-21T18:56:00+00:00'
            }
        ],
        'type': 'JOINT'
    }
]
TRAND_ADD_GROUPS2 = [
    {
        'groupId': 4,
        'owners': [
            {
                'individualName': {
                    'first': 'DENNIS',
                    'middle': '',
                    'last': 'HALL'
                },
                'address': {
                    'street': 'SS 2, COMP. 2, SITE 19',
                    'city': 'FORT ST. JOH',
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
EXEC_DELETE_GROUPS = [
    {
        'groupId': 1,
        'owners': [
            {
                'individualName': {
                    'first': 'SHARON',
                    'last': 'HALL'
                 },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567',
                'deathCertificateNumber': '232432488',
                'deathDateTime': '2023-03-14T18:56:00+00:00'
            }, {
                'individualName': {
                    'first': 'DENNIS',
                    'last': 'HALL'
                },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567',
                'deathCertificateNumber': '232432432',
                'deathDateTime': '2023-03-14T18:56:00+00:00'
            }
        ],
        'type': 'JOINT'
    }
]
EXEC_ADD_GROUPS = [
    {
        'groupId': 2,
        'owners': [
            {
                'individualName': {
                    'first': 'APPOINTED',
                    'last': 'EXECUTOR'
                },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567',
                'partyType': 'EXECUTOR',
                'description': 'EXECUTOR of the deceased.'
            }
        ],
        'type': 'SOLE'
    }
]
EXEC_ADD_GROUPS_INVALID = [
    {
        'groupId': 2,
        'owners': [
            {
                'individualName': {
                    'first': 'SHARON',
                    'last': 'HALL'
                },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567',
                'partyType': 'OWNER_IND'
            }, {
                'individualName': {
                    'first': 'APPOINTED',
                    'last': 'EXECUTOR'
                },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567',
                'partyType': 'EXECUTOR',
                'description': 'EXECUTOR of the deceased.'
            }
        ],
        'type': 'NA'
    }
]
WILL_DELETE_GROUPS = [
    {
        'groupId': 1,
        'owners': [
            {
                'individualName': {
                    'first': 'SHARON',
                    'last': 'HALL'
                 },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567'
            }, {
                'individualName': {
                    'first': 'DENNIS',
                    'last': 'HALL'
                },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567',
                'deathCertificateNumber': '232432432',
                'deathDateTime': '2021-02-21T18:56:00+00:00'
            }
        ],
        'type': 'JOINT'
    }
]
WILL_DELETE_GROUPS1 = [
    {
        'groupId': 1,
        'owners': [
            {
                'individualName': {
                    'first': 'SHARON',
                    'last': 'HALL'
                 },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567',
                'deathCertificateNumber': '232432432',
                'deathDateTime': '2021-02-21T18:56:00+00:00'
            }, {
                'individualName': {
                    'first': 'DENNIS',
                    'last': 'HALL'
                },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567',
                'deathCertificateNumber': '232432432',
                'deathDateTime': '2021-02-21T18:56:00+00:00'
            }
        ],
        'type': 'JOINT'
    }
]
WILL_DELETE_GROUPS2 = [
    {
        'groupId': 1,
        'owners': [
            {
                'individualName': {
                    'first': 'SHARON',
                    'last': 'HALL'
                 },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567'
            }, {
                'individualName': {
                    'first': 'DENNIS',
                    'last': 'HALL'
                },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567'
            }
        ],
        'type': 'JOINT'
    }
]
ADMIN_DELETE_GROUPS = WILL_DELETE_GROUPS
ADMIN_ADD_GROUPS = [
    {
        'groupId': 2,
        'owners': [
            {
                'individualName': {
                    'first': 'APPOINTED',
                    'last': 'ADMINISTRATOR'
                },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567',
                'partyType': 'ADMINISTRATOR',
                'description': 'ADMINISTRATOR of the deceased.'
            }
        ],
        'type': 'SOLE'
    }
]
ADD_OWNER = {
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
SO_GROUP = [
    {
        'groupId': 2,
        'owners': [
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
ADD_GROUP = {
        'groupId': 2,
        'owners': [
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
            },
            {
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
        'type': 'JOINT'
}
TRANS_QS_1 = {
  'mhrNumber': '125234',
  'registrationType': 'TRANS',
  'submittingParty': {
    'businessName': 'ABC SEARCHING COMPANY',
    'address': {
      'street': '222 SUMMER STREET',
      'city': 'VICTORIA',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V8W 2V8'
    }
  },
  'deleteOwnerGroups': [
    {
      'groupId': 4,
      'owners': [
        {
          'individualName': {
            'first': 'JANE',
            'middle': 'ANN',
            'last': 'HUFF'
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
        'type': 'COMMON',
        'interest': 'UNDIVIDED 34/100',
        'interestNumerator': 34,
        'interestDenominator': 100
    }
  ],
  'addOwnerGroups': [
    {
      'groupId': 7,
      'owners': [
        {
          'individualName': {
            'first': 'JANET',
            'middle': 'ALICE',
            'last': 'HUFF'
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
        'type': 'COMMON',
        'interest': 'UNDIVIDED 34/100',
        'interestNumerator': 34,
        'interestDenominator': 100
    }
  ],
  'declaredValue': 78766,
  'consideration': '$78766.00',
  'transferDate': '2022-10-04T20:29:36+00:00'
}
TRANS_QS_2 = {
  'mhrNumber': '125234',
  'registrationType': 'TRANS',
  'submittingParty': {
    'businessName': 'ABC SEARCHING COMPANY',
    'address': {
      'street': '222 SUMMER STREET',
      'city': 'VICTORIA',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V8W 2V8'
    }
  },
  'deleteOwnerGroups': [
    {
      'groupId': 4,
      'owners': [
        {
          'individualName': {
            'first': 'JANE',
            'middle': 'ANN',
            'last': 'HUFF'
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
        'type': 'COMMON',
        'interest': 'UNDIVIDED 34/100',
        'interestNumerator': 34,
        'interestDenominator': 100
    }, {
      'groupId': 5,
      'owners': [
        {
          'individualName': {
            'first': 'JANE',
            'middle': 'ELIZABETH',
            'last': 'HUFF'
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
        'type': 'COMMON',
        'interest': 'UNDIVIDED 33/100',
        'interestNumerator': 33,
        'interestDenominator': 100
    }
  ],
  'addOwnerGroups': [
    {
      'groupId': 7,
      'owners': [
        {
          'individualName': {
            'first': 'JANET',
            'middle': 'ALICE',
            'last': 'HUFF'
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
        'type': 'COMMON',
        'interest': 'UNDIVIDED 34/100',
        'interestNumerator': 34,
        'interestDenominator': 100
    }, {
      'groupId': 8,
      'owners': [
        {
          'individualName': {
            'first': 'JAMES',
            'middle': 'JOYCE',
            'last': 'HUFF'
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
        'type': 'COMMON',
        'interest': 'UNDIVIDED 33/100',
        'interestNumerator': 33,
        'interestDenominator': 100
    }
  ],
  'declaredValue': 78766,
  'consideration': '$78766.00',
  'transferDate': '2022-10-04T20:29:36+00:00'
}
TRANS_QS_3 = {
  'mhrNumber': '125234',
  'registrationType': 'TRANS',
  'submittingParty': {
    'businessName': 'ABC SEARCHING COMPANY',
    'address': {
      'street': '222 SUMMER STREET',
      'city': 'VICTORIA',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V8W 2V8'
    }
  },
  'deleteOwnerGroups': [
    {
      'groupId': 4,
      'owners': [
        {
          'individualName': {
            'first': 'JANE',
            'middle': 'ANN',
            'last': 'HUFF'
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
        'type': 'COMMON',
        'interest': 'UNDIVIDED 34/100',
        'interestNumerator': 34,
        'interestDenominator': 100
    }, {
      'groupId': 5,
      'owners': [
        {
          'individualName': {
            'first': 'JANE',
            'middle': 'ELIZABETH',
            'last': 'HUFF'
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
        'type': 'COMMON',
        'interest': 'UNDIVIDED 33/100',
        'interestNumerator': 33,
        'interestDenominator': 100
    }, {
      'groupId': 6,
      'owners': [
        {
          'individualName': {
            'first': 'ERIN',
            'middle': 'SUZANNE',
            'last': 'SANTORO'
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
        'type': 'COMMON',
        'interest': 'UNDIVIDED 33/100',
        'interestNumerator': 33,
        'interestDenominator': 100
    }
  ],
  'addOwnerGroups': [
    {
      'groupId': 7,
      'owners': [
        {
          'individualName': {
            'first': 'JANET',
            'middle': 'ALICE',
            'last': 'HUFF'
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
        'type': 'COMMON',
        'interest': 'UNDIVIDED 34/100',
        'interestNumerator': 34,
        'interestDenominator': 100
    }, {
      'groupId': 8,
      'owners': [
        {
          'individualName': {
            'first': 'JAMES',
            'middle': 'JOYCE',
            'last': 'HUFF'
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
        'type': 'COMMON',
        'interest': 'UNDIVIDED 33/100',
        'interestNumerator': 33,
        'interestDenominator': 100
    }, {
      'groupId': 9,
      'owners': [
        {
          'individualName': {
            'first': 'MARY',
            'middle': 'JANE',
            'last': 'HUFF'
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
        'type': 'COMMON',
        'interest': 'UNDIVIDED 33/100',
        'interestNumerator': 33,
        'interestDenominator': 100
    }
  ],
  'declaredValue': 78766,
  'consideration': '$78766.00',
  'transferDate': '2022-10-04T20:29:36+00:00'
}


