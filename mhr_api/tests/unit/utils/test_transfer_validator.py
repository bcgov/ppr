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

from mhr_api.utils import registration_validator as validator
from mhr_api.models import MhrRegistration, utils as model_utils
from mhr_api.models.type_tables import MhrRegistrationStatusTypes, MhrTenancyTypes, MhrRegistrationTypes
from mhr_api.models.type_tables import MhrPartyTypes


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

# testdata pattern is ({description}, {valid}, {staff}, {doc_id}, {message content}, {status})
TEST_TRANSFER_DATA = [
    (DESC_VALID, True, True, None, None, MhrRegistrationStatusTypes.ACTIVE),
    ('Valid staff FROZEN', True, True, None, None, MhrRegistrationStatusTypes.ACTIVE),
    ('Valid no doc id not staff', True, False, None, None, None),
    ('Invalid EXEMPT', False, False, None, validator.STATE_NOT_ALLOWED, MhrRegistrationStatusTypes.EXEMPT),
    ('Invalid HISTORICAL', False, False, None, validator.STATE_NOT_ALLOWED, MhrRegistrationStatusTypes.HISTORICAL),
    ('Invalid FROZEN', False, False, None, validator.STATE_NOT_ALLOWED, MhrRegistrationStatusTypes.ACTIVE),
    ('Invalid draft', False, False, None, validator.DRAFT_NOT_ALLOWED, MhrRegistrationStatusTypes.ACTIVE),
    (DESC_INVALID_GROUP_ID, False, False, None, validator.DELETE_GROUP_ID_INVALID, MhrRegistrationStatusTypes.ACTIVE),
    (DESC_NONEXISTENT_GROUP_ID, False, False, None, validator.DELETE_GROUP_ID_NONEXISTENT,
     MhrRegistrationStatusTypes.ACTIVE),
    (DESC_INVALID_GROUP_TYPE, False, False, None, validator.DELETE_GROUP_TYPE_INVALID,
     MhrRegistrationStatusTypes.ACTIVE)
]
# testdata pattern is ({description}, {valid}, {staff}, {tran_dt}, {dec_val}, {consideration}, {message content})
TEST_TRANSFER_DATA_EXTRA = [
    ('Valid staff exists', True, True, True, True, True, None),
    ('Valid staff missing', True, True, False, False, False, None),
    ('Valid non-staff exists', True, False, True, True, True, None),
    ('Invalid non-staff missing transfer date', False, False, False, True, True, validator.TRANSFER_DATE_REQUIRED),
    ('Invalid non-staff missing declared value', False, False, True, False, True, validator.DECLARED_VALUE_REQUIRED),
    ('Invalid non-staff missing consideration', False, False, True, True, False, validator.CONSIDERATION_REQUIRED)
]
# testdata pattern is ({description}, {valid}, {numerator}, {denominator}, {add_group}, {message content})
TEST_TRANSFER_DATA_GROUP = [
    ('Valid', True, 1, 2, None, None),
    ('Invalid add TC no owner', False, None, None, TC_GROUP_TRANSFER_ADD2, validator.OWNERS_COMMON_INVALID),
    ('Invalid add JT 1 owner', False, None, None, JT_OWNER_SINGLE, validator.OWNERS_JOINT_INVALID),
    ('Invalid TC numerator missing', False, None, 2, TC_GROUPS_VALID, validator.GROUP_NUMERATOR_MISSING),
    ('Invalid TC numerator < 1', False, 0, 2, TC_GROUPS_VALID, validator.GROUP_NUMERATOR_MISSING),
    ('Invalid TC denominator missing', False, 1, None, TC_GROUPS_VALID, validator.GROUP_DENOMINATOR_MISSING),
    ('Invalid TC denominator < 1', False, 1, 0, TC_GROUPS_VALID, validator.GROUP_DENOMINATOR_MISSING),
    ('Invalid add SO 2 groups', False, None, None, SO_GROUP_MULTIPLE, validator.ADD_SOLE_OWNER_INVALID),
    ('Invalid add SO 2 owners', False, None, None, SO_OWNER_MULTIPLE, validator.ADD_SOLE_OWNER_INVALID),
    ('Invalid add TC > 1 owner', False, None, None, TC_GROUP_TRANSFER_ADD, validator.OWNERS_COMMON_INVALID)
]
# testdata pattern is ({description},{valid},{mhr_num},{account_id},{delete_groups},{add_groups},{message content})
TEST_TRANSFER_DATA_TRAND = [
    ('Valid', True,  '001004', '2523', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS, None),
    ('Valid with no/empty middle name', True,  '001020', '2523', TRAND_DELETE_GROUPS2, TRAND_ADD_GROUPS2, None),
    ('Invalid FROZEN', False,  '003936', '2523', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     validator.STATE_NOT_ALLOWED),
    ('Invalid staff FROZEN', False,  '003936', '2523', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     validator.STATE_FROZEN_AFFIDAVIT),
    ('Invalid party type', False,  '001004', '2523', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     validator.TRAN_DEATH_NEW_OWNER),
    ('Invalid add owner', False,  '001004', '2523', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     validator.TRAN_DEATH_ADD_OWNER),
    ('Invalid no cert number', False,  '001004', '2523', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     validator.TRAN_DEATH_CERT_MISSING),
    ('Invalid no death ts', False,  '001004', '2523', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     validator.TRAN_DEATH_DATE_MISSING),
    ('Invalid tenancy type', False,  '001004', '2523', SO_GROUP, TRAND_ADD_GROUPS,
     validator.TRAN_DEATH_JOINT_TYPE),
    ('Invalid add 2 groups', False,  '001004', '2523', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     validator.TRAN_DEATH_GROUP_COUNT),
    ('Invalid delete 2 groups', False,  '001004', '2523', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     validator.TRAN_DEATH_GROUP_COUNT),
    ('Invalid future death ts', False,  '001004', '2523', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS,
     validator.TRAN_DEATH_DATE_INVALID)
]
# testdata pattern is ({description},{valid},{mhr_num},{account_id},{delete_groups},{add_groups},{message content},{staff})
TEST_TRANSFER_DATA_ADMIN = [
    ('Valid', True,  '001020', '2523', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS, None, True),
    ('Invalid non-staff', False,  '001020', '2523', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS,
     validator.REG_STAFF_ONLY, False),
    ('Valid party type EXECUTOR', True,  '001020', '2523', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS, None, True),
    ('Valid party type TRUSTEE', True,  '001020', '2523', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS, None, True),
    ('Valid party type ADMINISTRATOR', True,  '001020', '2523', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS, None, True),
    ('Invalid party type add', False,  '001020', '2523', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS,
     validator.TRAN_ADMIN_NEW_OWNER, True),
    ('Invalid administrator missing', False,  '001020', '2523', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS,
     validator.TRAN_ADMIN_NEW_OWNER, True),
    ('Invalid no grant', False,  '001020', '2523', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS,
     validator.TRAN_ADMIN_GRANT, True),
    ('Invalid no death info', False,  '001020', '2523', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS,
     validator.TRAN_ADMIN_DEATH_CERT, True),
    ('Invalid add 2 groups', False,  '001020', '2523', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS,
     validator.TRAN_DEATH_GROUP_COUNT, True),
    ('Invalid delete 2 groups', False,  '001020', '2523', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS,
     validator.TRAN_DEATH_GROUP_COUNT, True)
]
# testdata pattern is ({description},{valid},{mhr_num},{account_id},{delete_groups},{add_groups},{message content},{staff})
TEST_TRANSFER_DATA_AFFIDAVIT = [
    ('Valid', True,  '001020', '2523', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS, None, True),
    ('Invalid non-staff', False,  '001020', '2523', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.REG_STAFF_ONLY, False),
    ('Valid party type EXECUTOR', True,  '001020', '2523', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS, None, True),
    ('Valid party type TRUSTEE', True,  '001020', '2523', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS, None, True),
    ('Valid party type ADMINISTRATOR', True,  '001020', '2523', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS, None, True),
    ('Invalid party type add', False,  '001020', '2523', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_AFFIDAVIT_NEW_OWNER, True),
    ('Invalid declared value', False,  '001020', '2523', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_AFFIDAVIT_DECLARED_VALUE, True),
    ('Invalid executor missing', False,  '001020', '2523', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS_INVALID,
     validator.TRAN_AFFIDAVIT_NEW_OWNER, True),
    ('Invalid no death info', False,  '001020', '2523', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_EXEC_DEATH_CERT, True),
    ('Invalid no death number', False,  '001020', '2523', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_DEATH_CERT_MISSING, True),
    ('Invalid no death date', False,  '001020', '2523', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_DEATH_DATE_MISSING, True),
    ('Invalid add 2 groups', False,  '001020', '2523', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_DEATH_GROUP_COUNT, True),
    ('Invalid delete 2 groups', False,  '001020', '2523', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_DEATH_GROUP_COUNT, True)
]
# testdata pattern is ({description},{valid},{mhr_num},{account_id},{delete_groups},{add_groups},{message content},{staff})
TEST_TRANSFER_DATA_WILL = [
    ('Valid', True,  '001020', '2523', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS, None, True),
    ('Invalid non-staff', False,  '001020', '2523', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.REG_STAFF_ONLY, False),
    ('Invalid add owner', False,  '001020', '2523', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_WILL_NEW_OWNER, True),
    ('Valid party type EXECUTOR', True,  '001020', '2523', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS, None, True),
    ('Valid party type TRUSTEE', True,  '001020', '2523', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS, None, True),
    ('Valid party type ADMINISTRATOR', True,  '001020', '2523', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS, None, True),
    ('Invalid party type add', False,  '001020', '2523', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_WILL_NEW_OWNER, True),
    ('Invalid executor missing', False,  '001020', '2523', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS_INVALID,
     validator.TRAN_WILL_NEW_OWNER, True),
    ('Invalid no probate', False,  '001020', '2523', WILL_DELETE_GROUPS1, EXEC_ADD_GROUPS,
     validator.TRAN_WILL_PROBATE, True),
    ('Invalid no death info', False,  '001020', '2523', WILL_DELETE_GROUPS2, EXEC_ADD_GROUPS,
     validator.TRAN_WILL_DEATH_CERT, True),
    ('Invalid add 2 groups', False,  '001020', '2523', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_DEATH_GROUP_COUNT, True),
    ('Invalid delete 2 groups', False,  '001020', '2523', WILL_DELETE_GROUPS, EXEC_ADD_GROUPS,
     validator.TRAN_DEATH_GROUP_COUNT, True)
]
# testdata pattern is ({description}, {valid}, {mhr_num}, {tenancy_type}, {add_group}, {message content})
TEST_TRANSFER_DEATH_NA_DATA = [
   ('Invalid JOINT tenancy-party type', False, '045349', MhrTenancyTypes.JOINT, TC_GROUP_TRANSFER_ADD,
     validator.TENANCY_PARTY_TYPE_INVALID),
    ('Invalid tenancy type - party type', False, '080282', MhrTenancyTypes.JOINT, TC_GROUP_TRANSFER_ADD,
     validator.TENANCY_PARTY_TYPE_INVALID)
]
# testdata pattern is ({description}, {valid}, {numerator}, {denominator}, {message content})
TEST_TRANSFER_DATA_GROUP_INTEREST = [
    ('Valid add', True, 1, 2, None),
    ('Invalid numerator < 1', False, 1, 4, validator.GROUP_INTEREST_MISMATCH),
    ('Invalid numerator sum high', False, 3, 4, validator.GROUP_INTEREST_MISMATCH)
]


@pytest.mark.parametrize('desc,valid,staff,doc_id,message_content,status', TEST_TRANSFER_DATA)
def test_validate_transfer(session, desc, valid, staff, doc_id, message_content, status):
    """Assert that MH transfer validation works as expected."""
    # setup
    json_data = copy.deepcopy(TRANSFER)
    mhr_num: str = '045349'
    account_id: str = 'PS12345'
    if doc_id:
        json_data['documentId'] = doc_id
    elif json_data.get('documentId'):
        del json_data['documentId']
    if valid:
        json_data['deleteOwnerGroups'][0]['groupId'] = 2
        json_data['deleteOwnerGroups'][0]['type'] = 'JOINT'
    elif desc == DESC_NONEXISTENT_GROUP_ID:
        json_data['deleteOwnerGroups'][0]['groupId'] = 10
    elif desc == DESC_NONEXISTENT_GROUP_ID:
        json_data['deleteOwnerGroups'][0]['type'] = 'SOLE'
    elif desc in ('Invalid FROZEN', 'Valid staff FROZEN'):
        mhr_num = '003936'
        account_id = '2523'
    elif desc == 'Invalid draft':
        mhr_num = '100377'
        account_id = 'ppr_staff'
        json_data['mhrNumber'] = '100377'
        json_data['draftNumber'] = '101421'
    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    if status:
        registration.status_type = status
    error_msg = validator.validate_transfer(registration, json_data, staff)
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
    if not trans_dt:
        del json_data['transferDate']
    if not dec_value:
        del json_data['declaredValue']
    if not consideration:
        del json_data['consideration']
    if valid:
        json_data['deleteOwnerGroups'][0]['groupId'] = 2
        json_data['deleteOwnerGroups'][0]['type'] = 'JOINT'
        if staff:
            json_data['documentId'] = '63166035'
    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number('045349', 'PS12345')
    error_msg = validator.validate_transfer(registration, json_data, staff)
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
    json_data['deleteOwnerGroups'][0]['groupId'] = 2
    json_data['deleteOwnerGroups'][0]['type'] = 'JOINT'
    if add_group:
        json_data['addOwnerGroups'] = copy.deepcopy(add_group)
        if desc == 'Invalid add TC no owner':
            json_data['addOwnerGroups'][0]['owners'] = []
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
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number('045349', 'PS12345')
    error_msg = validator.validate_transfer(registration, json_data, False)
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
    json_data['registrationType'] = MhrRegistrationTypes.TRAND
    json_data['deleteOwnerGroups'] = copy.deepcopy(delete_groups)
    json_data['addOwnerGroups'] = copy.deepcopy(add_groups)
    staff: bool = False
    if desc == 'Invalid party type':
        json_data['addOwnerGroups'][0]['owners'][0]['partyType'] = MhrPartyTypes.TRUSTEE
    elif desc == 'Invalid add owner':
        json_data['addOwnerGroups'][0]['owners'].append(ADD_OWNER)
    elif desc == 'Invalid no cert number':
        del json_data['deleteOwnerGroups'][0]['owners'][1]['deathCertificateNumber']
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
    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    error_msg = validator.validate_transfer(registration, json_data, staff)
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
    error_msg = validator.validate_transfer(registration, json_data, staff)
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
    elif desc == 'Invalid no death number':
        del json_data['deleteOwnerGroups'][0]['owners'][0]['deathCertificateNumber']
    elif desc == 'Invalid no death date':
        del json_data['deleteOwnerGroups'][0]['owners'][0]['deathDateTime']

    if desc == 'Invalid declared value':
        json_data['declaredValue'] = 25001
    else:
        json_data['declaredValue'] = 25000

    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    error_msg = validator.validate_transfer(registration, json_data, staff)
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
    elif desc == 'Invalid add owner':
        json_data['addOwnerGroups'][0]['owners'].append(ADD_OWNER)
    elif desc == 'Invalid executor missing':
        del json_data['addOwnerGroups'][0]['owners'][1]['partyType']
        del json_data['addOwnerGroups'][0]['owners'][1]['description']
    elif desc == 'Invalid add 2 groups':
        json_data['addOwnerGroups'].append(ADD_GROUP)
    elif desc == 'Invalid delete 2 groups':
        json_data['deleteOwnerGroups'].append(ADD_GROUP)

    valid_format, errors = schema_utils.validate(json_data, 'transfer', 'mhr')
    # Additional validation not covered by the schema.
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    error_msg = validator.validate_transfer(registration, json_data, staff)
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
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, '2523')
    error_msg = validator.validate_transfer(registration, json_data, False)
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
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number('088912', 'PS12345')
    error_msg = validator.validate_transfer(registration, json_data, False)
    if errors:
        current_app.logger.debug(errors)
    if valid:
        assert valid_format and error_msg == ''
    else:
        assert error_msg != ''
        if message_content:
            assert error_msg.find(message_content) != -1
