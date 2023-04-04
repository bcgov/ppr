# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests to verify the endpoints for maintaining MH transfers.

Test-Suite to ensure that the /transfers endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app
from registry_schemas.example_data.mhr import TRANSFER

from mhr_api.models import MhrRegistration
from mhr_api.models.type_tables import MhrPartyTypes, MhrRegistrationTypes
from mhr_api.services.authz import MHR_ROLE, STAFF_ROLE, COLIN_ROLE, \
                                   TRANSFER_DEATH_JT, TRANSFER_SALE_BENEFICIARY
from tests.unit.services.utils import create_header, create_header_account


MOCK_AUTH_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
MOCK_PAY_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/pay/api/v1/'
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
AFFIDAVIT_DELETE_GROUPS = [
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
                'deathCertificateNumber': '232432434',
                'deathDateTime': '2021-02-21T18:56:00+00:00',
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
AFFIDAVIT_ADD_GROUPS = [
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
WILL_ADD_GROUPS = [
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


# testdata pattern is ({description}, {mhr_num}, {roles}, {status}, {account})
TEST_CREATE_DATA = [
    ('Invalid schema validation missing submitting', '098666', [MHR_ROLE, TRANSFER_SALE_BENEFICIARY],
     HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Missing account', '098666', [MHR_ROLE, TRANSFER_SALE_BENEFICIARY], HTTPStatus.BAD_REQUEST, None),
    ('Staff missing account', '098666', [MHR_ROLE, STAFF_ROLE, TRANSFER_SALE_BENEFICIARY],
     HTTPStatus.BAD_REQUEST, None),
    ('Invalid role product', '098666', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Invalid non-transfer role', '098666', [MHR_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Invalid transfer death role', '098666', [MHR_ROLE, TRANSFER_SALE_BENEFICIARY], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Valid staff', '098666', [MHR_ROLE, STAFF_ROLE, TRANSFER_SALE_BENEFICIARY], HTTPStatus.CREATED, 'PS12345'),
    ('Valid non-staff new', '150081', [MHR_ROLE, TRANSFER_DEATH_JT, TRANSFER_SALE_BENEFICIARY],
     HTTPStatus.CREATED, '2523'),
    ('Invalid mhr num', '300655', [MHR_ROLE, TRANSFER_SALE_BENEFICIARY], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Invalid exempt', '098655', [MHR_ROLE, TRANSFER_SALE_BENEFICIARY], HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Invalid historical', '099942', [MHR_ROLE, TRANSFER_SALE_BENEFICIARY], HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Invalid non-staff missing declared value', '098666', [MHR_ROLE, TRANSFER_DEATH_JT, TRANSFER_SALE_BENEFICIARY],
     HTTPStatus.BAD_REQUEST, 'PS12345')
]
# testdata pattern is ({description}, {mhr_num}, {roles}, {status}, {account}, {reg_type})
TEST_CREATE_TRANS_DEATH_DATA = [
    ('Invalid TRANS_ADMIN non-staff', '001019', [MHR_ROLE, TRANSFER_DEATH_JT], HTTPStatus.BAD_REQUEST, '2523',
     MhrRegistrationTypes.TRANS_ADMIN),
    ('Invalid TRANS_AFFIDAVIT non-staff', '001020', [MHR_ROLE, TRANSFER_DEATH_JT], HTTPStatus.BAD_REQUEST, '2523',
     MhrRegistrationTypes.TRANS_AFFIDAVIT),
    ('Invalid TRANS_WILL non-staff', '001020', [MHR_ROLE, TRANSFER_DEATH_JT], HTTPStatus.BAD_REQUEST, '2523',
     MhrRegistrationTypes.TRANS_WILL),
    ('Valid TRANS_ADMIN staff', '001020', [MHR_ROLE, STAFF_ROLE, TRANSFER_DEATH_JT], HTTPStatus.CREATED, '2523',
     MhrRegistrationTypes.TRANS_ADMIN),
    ('Valid TRAND staff', '001004', [MHR_ROLE, STAFF_ROLE, TRANSFER_DEATH_JT], HTTPStatus.CREATED, '2523',
     MhrRegistrationTypes.TRAND),
    ('Valid TRAND non-staff', '001004', [MHR_ROLE, TRANSFER_DEATH_JT], HTTPStatus.CREATED, '2523',
     MhrRegistrationTypes.TRAND),
    ('Valid TRANS_AFFIDAVIT staff', '001020', [MHR_ROLE, STAFF_ROLE, TRANSFER_DEATH_JT], HTTPStatus.CREATED, '2523',
     MhrRegistrationTypes.TRANS_AFFIDAVIT),
    ('Valid TRANS_WILL staff', '001020', [MHR_ROLE, STAFF_ROLE, TRANSFER_DEATH_JT], HTTPStatus.CREATED, '2523',
     MhrRegistrationTypes.TRANS_WILL)
]


@pytest.mark.parametrize('desc,mhr_num,roles,status,account', TEST_CREATE_DATA)
def test_create(session, client, jwt, desc, mhr_num, roles, status, account):
    """Assert that a post MH registration works as expected."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    json_data = copy.deepcopy(TRANSFER)
    del json_data['documentId']
    del json_data['documentDescription']
    del json_data['createDateTime']
    del json_data['payment']
    json_data['mhrNumber'] = mhr_num
    if desc == 'Invalid schema validation missing submitting':
        del json_data['submittingParty']
    elif desc == 'Invalid non-staff missing declared value':
        del json_data['declaredValue']
    elif desc == 'Invalid transfer death role':
        json_data['registrationType'] = MhrRegistrationTypes.TRAND

    if account:
        headers = create_header_account(jwt, roles, 'UT-TEST', account)
    else:
        headers = create_header(jwt, roles)
    # test
    response = client.post('/api/v1/transfers/' + mhr_num,
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    assert response.status_code == status
    if response.status_code == HTTPStatus.CREATED:
        registration: MhrRegistration = MhrRegistration.find_by_mhr_number(response.json['mhrNumber'],
                                                                           account)
        assert registration


@pytest.mark.parametrize('desc,mhr_num,roles,status,account,reg_type', TEST_CREATE_TRANS_DEATH_DATA)
def test_create_transfer_death(session, client, jwt, desc, mhr_num, roles, status, account, reg_type):
    """Assert that a post MH registration works as expected."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    json_data = copy.deepcopy(TRANSFER)
    del json_data['documentId']
    del json_data['documentDescription']
    del json_data['createDateTime']
    del json_data['payment']
    json_data['mhrNumber'] = mhr_num
    json_data['registrationType'] = reg_type
    if reg_type == MhrRegistrationTypes.TRAND:
        json_data['deleteOwnerGroups'] = copy.deepcopy(TRAND_DELETE_GROUPS)
        json_data['addOwnerGroups'] = copy.deepcopy(TRAND_ADD_GROUPS)
    elif reg_type == MhrRegistrationTypes.TRANS_ADMIN:
        json_data['deleteOwnerGroups'] = copy.deepcopy(ADMIN_DELETE_GROUPS)
        json_data['addOwnerGroups'] = copy.deepcopy(ADMIN_ADD_GROUPS)
    elif reg_type == MhrRegistrationTypes.TRANS_WILL:
        json_data['deleteOwnerGroups'] = copy.deepcopy(WILL_DELETE_GROUPS)
        json_data['addOwnerGroups'] = copy.deepcopy(WILL_ADD_GROUPS)
    else:
        json_data['deleteOwnerGroups'] = copy.deepcopy(AFFIDAVIT_DELETE_GROUPS)
        json_data['addOwnerGroups'] = copy.deepcopy(AFFIDAVIT_ADD_GROUPS)
    if reg_type == MhrRegistrationTypes.TRANS_AFFIDAVIT:
        json_data['declaredValue'] = 25000
    if account:
        headers = create_header_account(jwt, roles, 'UT-TEST', account)
    else:
        headers = create_header(jwt, roles)
    # test
    response = client.post('/api/v1/transfers/' + mhr_num,
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    # current_app.logger.info(response.json)
    assert response.status_code == status
