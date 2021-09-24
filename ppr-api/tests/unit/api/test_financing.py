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

"""Tests to verify the financing-statement endpoint.

Test-Suite to ensure that the /financing-statement endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest

from ppr_api.models import FinancingStatement, Registration
from ppr_api.resources.financing_statements import get_payment_details, get_payment_details_financing, \
     get_payment_type_financing
from ppr_api.services.authz import COLIN_ROLE, PPR_ROLE, STAFF_ROLE
from ppr_api.services.payment.payment import TransactionTypes
from tests.unit.services.utils import create_header, create_header_account


# prep sample post financing statement data
FINANCING_VALID = {
    'type': 'SA',
    'clientReferenceId': 'A-00000402',
    'documentId': '1234567',
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
FINANCING_INVALID_TYPE = {
    'type': 'XX',
    'clientReferenceId': 'A-00000402',
    'documentId': '1234567',
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
FINANCING_INVALID_CODE = {
    'type': 'SA',
    'clientReferenceId': 'A-00000402',
    'registeringParty': {
        'code': '300000000'
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
FINANCING_INVALID_ADDRESS = {
    'type': 'SA',
    'clientReferenceId': 'A-00000402',
    'documentId': '1234567',
    'registeringParty': {
        'businessName': 'ABC SEARCHING COMPANY',
        'address': {
            'street': '222 SUMMER STREET',
            'city': 'VICTORIA',
            'region': 'XX',
            'country': 'CA',
            'postalCode': 'V8W 2V8'
        }
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

# testdata pattern is ({description}, {test data}, {roles}, {status}, {has_account})
TEST_CREATE_DATA = [
    ('Invalid type schema validation', FINANCING_INVALID_TYPE, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True),
    ('Invalid party code extra validation', FINANCING_INVALID_CODE, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True),
    ('Invalid party address extra validation', FINANCING_INVALID_ADDRESS, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True),
    ('Missing account', FINANCING_VALID, [PPR_ROLE], HTTPStatus.BAD_REQUEST, False),
    ('Invalid role', FINANCING_VALID, [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True),
    ('Valid Security Agreement', FINANCING_VALID, [PPR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, False)
]
# testdata pattern is ({description}, {roles}, {status}, {has_account})
TEST_GET_LIST = [
    ('Missing account', [PPR_ROLE], HTTPStatus.BAD_REQUEST, False),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True),
    ('Valid Request', [PPR_ROLE], HTTPStatus.OK, True),
    ('Invalid Request Staff no account', [PPR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False)
]
# testdata pattern is ({description}, {roles}, {status}, {account_id}, {reg_num})
TEST_USER_LIST = [
    ('Missing account', [PPR_ROLE], HTTPStatus.BAD_REQUEST, None, 'TEST0019A'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345', 'TEST0019A'),
    ('Valid Request', [PPR_ROLE], HTTPStatus.CREATED, 'PS12345', 'TEST0019A'),
    ('Not found', [PPR_ROLE], HTTPStatus.NOT_FOUND, 'PS12345', 'TESTXXXX'),
    ('Already exists user', [PPR_ROLE], HTTPStatus.CONFLICT, 'PS12345', 'TEST0001'),
    ('Already exists extra', [PPR_ROLE], HTTPStatus.CONFLICT, 'PS12345', 'TEST0019'),
    ('Invalid Request Staff no account', [PPR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, None, 'TEST0019A')
]
# testdata pattern is ({description}, {roles}, {status}, {account_id}, {reg_num})
TEST_USER_LIST_DELETE = [
    ('Missing account', [PPR_ROLE], HTTPStatus.BAD_REQUEST, None, 'TEST0019'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345', 'TEST0019'),
    ('Valid Request', [PPR_ROLE], HTTPStatus.NO_CONTENT, 'PS12345', 'TEST0019'),
    ('Not found', [PPR_ROLE], HTTPStatus.NOT_FOUND, 'PS12345', 'TESTXXXX'),
    ('Invalid Request Staff no account', [PPR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, None, 'TEST0019')
]
# testdata pattern is ({description}, {roles}, {status}, {has_account}, {reg_num})
TEST_GET_STATEMENT = [
    ('Missing account', [PPR_ROLE], HTTPStatus.BAD_REQUEST, False, 'TEST0001'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 'TEST0001'),
    ('Valid Request', [PPR_ROLE], HTTPStatus.OK, True, 'TEST0001'),
    ('Invalid Registration Number', [PPR_ROLE], HTTPStatus.NOT_FOUND, True, 'TESTXXXX'),
    ('Invalid expired non-staff', [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0013'),
    ('Invalid discharged non-staff', [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0014'),
    ('Valid expired staff', [PPR_ROLE, STAFF_ROLE], HTTPStatus.OK, True, 'TEST0013'),
    ('Valid discharged staff', [PPR_ROLE, STAFF_ROLE], HTTPStatus.OK, True, 'TEST0014'),
    ('Valid Request Staff no account', [PPR_ROLE, STAFF_ROLE], HTTPStatus.OK, False, 'TEST0001')
]
# testdata pattern is ({description}, {registration_number}, {current_state}, {param_value})
TEST_CURRENT_STATE = [
    ('Current Financing Statement', 'TEST0001', True, 'true'),
    ('Original Financing Statement', 'TEST0001', False, ''),
    ('Invalid Financing Statement param', 'TEST0001', False, 'junk')
]
# testdata pattern is ({description}, {roles}, {status}, {has_account}, {registration_number})
TEST_DEBTOR_NAMES = [
    ('Missing account', [PPR_ROLE], HTTPStatus.BAD_REQUEST, False, 'TEST0001'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 'TEST0001'),
    ('Valid Request', [PPR_ROLE], HTTPStatus.OK, True, 'TEST0001'),
    ('Valid Request No Data', [PPR_ROLE], HTTPStatus.OK, True, 'TESTXXXX')
]
# testdata pattern is ({reg_type}, {reg_class}, {registration_number}, {label}, {value}, {life})
TEST_PAY_DETAILS_REGISTRATION = [
    ('CO', 'COURTORDER', 'TEST0001', 'Court Order Amendment of Registration:', 'TEST0001', 1),
    ('AM', 'AMENDMENT', 'TEST0001', 'Amendment of Registration:', 'TEST0001', 1),
    ('DC', 'DISCHARGE', 'TEST0001', 'Discharge Registration:', 'TEST0001', 1),
    ('AC', 'CHANGE', 'TEST0001', 'Change Registration:', 'TEST0001', 1),
    ('RE', 'RENEWAL', 'TEST0001', 'Renew Registration:', 'TEST0001 for 1 year', 1),
    ('RE', 'RENEWAL', 'TEST0001', 'Renew Registration:', 'TEST0001 for 2 years', 2),
    ('RE', 'RENEWAL', 'TEST0001', 'Renew Registration:', 'TEST0001 for 180 days', 0),
    ('RE', 'RENEWAL', 'TEST0001', 'Renew Registration:', 'TEST0001 for infinity', 99)
]
# testdata pattern is ({reg_type}, {registration_number}, {detail_desc}, {life})
TEST_PAY_DETAILS_FINANCING = [
    ('SA', 'TEST0001', 'PPSA SECURITY AGREEMENT Length: 2 years', 2),
    ('RL', 'TEST0002', 'REPAIRERS LIEN Length: 180 days', 0)
]
# testdata pattern is ({reg_type}, {life_years}, {quantity}, {pay_trans_type})
TEST_PAY_TYPE_FINANCING = [
    ('FA', 1, 1, TransactionTypes.FINANCING_LIFE_YEAR.value),
    ('FL', 99, 1, TransactionTypes.FINANCING_INFINITE.value),
    ('FR', 1, 1, TransactionTypes.FINANCING_FR.value),
    ('FS', 2, 2, TransactionTypes.FINANCING_LIFE_YEAR.value),
    ('LT', 1, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('MH', 1, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('RL', 0, 1, TransactionTypes.FINANCING_LIFE_YEAR.value),
    ('SG', 3, 3, TransactionTypes.FINANCING_LIFE_YEAR.value),
    ('SA', 5, 5, TransactionTypes.FINANCING_LIFE_YEAR.value),
    ('SA', 99, 1, TransactionTypes.FINANCING_INFINITE.value),
    ('HN', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('ML', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('PN', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('WL', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('CC', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('CT', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('DP', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('ET', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('FO', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('FT', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('HR', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('IP', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('IT', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('LO', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('MI', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('MR', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('OT', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('PG', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('PS', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('RA', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('SS', 99, 1, TransactionTypes.FINANCING_NO_FEE.value),
    ('TL', 99, 1, TransactionTypes.FINANCING_NO_FEE.value)
]


@pytest.mark.parametrize('desc,json_data,roles,status,has_account', TEST_CREATE_DATA)
def test_create(session, client, jwt, desc, json_data, roles, status, has_account):
    """Assert that a post financing statement works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.post('/api/v1/financing-statements',
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    assert response.status_code == status


@pytest.mark.parametrize('desc,roles,status,has_account', TEST_GET_LIST)
def test_get_account_financing_list(session, client, jwt, desc, roles, status, has_account):
    """Assert that a request to get the list of financing statements by account works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.get('/api/v1/financing-statements',
                          headers=headers)

    # check
    assert response.status_code == status


@pytest.mark.parametrize('desc,roles,status,has_account', TEST_GET_LIST)
def test_get_account_registrations_list(session, client, jwt, desc, roles, status, has_account):
    """Assert that a request to get the list of registrations by account works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.get('/api/v1/financing-statements/registrations',
                          headers=headers)

    # check
    assert response.status_code == status


@pytest.mark.parametrize('desc,roles,status,account_id,reg_num', TEST_USER_LIST)
def test_account_add_registration(session, client, jwt, desc, roles, status, account_id, reg_num):
    """Assert that a request to add a registration to the user list works as expected."""
    headers = None
    # setup
    if account_id:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.post('/api/v1/financing-statements/registrations/' + reg_num,
                           headers=headers,
                           content_type='application/json')

    # check
    assert response.status_code == status


@pytest.mark.parametrize('desc,roles,status,account_id,reg_num', TEST_USER_LIST_DELETE)
def test_account_delete_registration(session, client, jwt, desc, roles, status, account_id, reg_num):
    """Assert that a request to delete a registration from the user list works as expected."""
    headers = None
    # setup
    if account_id:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.delete('/api/v1/financing-statements/registrations/' + reg_num,
                             headers=headers)

    # check
    assert response.status_code == status


@pytest.mark.parametrize('desc,roles,status,has_account, reg_num', TEST_GET_STATEMENT)
def test_get_statement(session, client, jwt, desc, roles, status, has_account, reg_num):
    """Assert that a get financing statement by registration number works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.get('/api/v1/financing-statements/' + reg_num,
                          headers=headers)

    # check
    assert response.status_code == status


# testdata pattern is ({reg_type}, {registration_number}, {detail_desc}, {life})
@pytest.mark.parametrize('reg_type,reg_num,detail_desc,life', TEST_PAY_DETAILS_FINANCING)
def test_get_payment_details_financing(session, client, jwt, reg_type, reg_num, detail_desc, life):
    """Assert that a valid financing statement request payment details setup works as expected."""
    # setup
    json_data = copy.deepcopy(FINANCING_VALID)
    json_data['type'] = reg_type
    json_data['lifeYears'] = life
    statement = FinancingStatement.create_from_json(json_data, 'PS12345', 'TESTID')
    statement.registration[0].registration_num = reg_num
    # test
    details = get_payment_details_financing(statement.registration[0])

    # check
    # print(details)
    assert details
    assert details['label'] == 'Register Financing Statement ' + reg_num + ' Type:'
    assert details['value'] == detail_desc


@pytest.mark.parametrize('reg_type,reg_class,reg_num,label,value, life', TEST_PAY_DETAILS_REGISTRATION)
def test_get_payment_details(session, client, jwt, reg_type, reg_class, reg_num, label, value, life):
    """Assert that a valid registration statement request payment details setup works as expected."""
    # setup
    registration = Registration()
    registration.base_registration_num = reg_num
    registration.registration_type = reg_type
    registration.registration_type_cl = reg_class
    registration.life = life
    # test
    details = get_payment_details(registration)

    # check
    assert details
    assert details['label'] == label
    assert details['value'] == value


@pytest.mark.parametrize('reg_type,life_years,quantity,pay_trans_type', TEST_PAY_TYPE_FINANCING)
def test_get_payment_type_financing(session, client, jwt, reg_type, life_years, quantity, pay_trans_type):
    """Assert that a valid financing statement request payment transaction type setup works as expected."""
    # setup
    json = copy.deepcopy(FINANCING_VALID)
    json['type'] = reg_type
    if life_years == 99:
        json['lifeYears'] = 1
        json['lifeInfinite'] = True
    else:
        json['lifeYears'] = life_years
    statement = FinancingStatement.create_from_json(json, 'PS12345')

    pay_type, pay_quantity = get_payment_type_financing(statement.registration[0])
    assert pay_type
    assert pay_quantity
    assert pay_type == pay_trans_type
    assert pay_quantity == quantity


def test_get_account_registrations_collapsed(session, client, jwt):
    """Assert that a request to get the collapsed list of registrations by account works as expected."""
    # setup

    # test
    response = client.get('/api/v1/financing-statements/registrations?collapse=true',
                          headers=create_header_account(jwt, [PPR_ROLE]))

    # check
    assert response.status_code == HTTPStatus.OK
    json_data = response.json
    assert json_data
    # print(json_data)
    assert len(json_data) > 0
    for statement in json_data:
        assert statement['registrationClass'] in ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN')
        if statement['registrationNumber'] == 'TEST0001':
            assert statement['changes']
            for change in statement['changes']:
                assert change['baseRegistrationNumber'] == 'TEST0001'
                assert change['registrationClass'] not in ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN')


@pytest.mark.parametrize('desc,reg_number,current_state,param_value', TEST_CURRENT_STATE)
def test_get_registration_current(session, client, jwt, desc, reg_number, current_state, param_value):
    """Assert that a request to get the current data for a registration works as expected."""
    # setup

    # test
    path = '/api/v1/financing-statements/' + reg_number
    if current_state:
        path += '?current=' + param_value
    elif param_value != '':
        path += '?current=' + param_value

    response = client.get(path,
                          headers=create_header_account(jwt, [PPR_ROLE]))

    # check
    assert response.status_code == HTTPStatus.OK
    json_data = response.json
    assert json_data
    # print(json_data)
    assert 'changes' not in json_data
    if current_state:
        assert 'courtOrderInformation' in json_data
    else:
        assert 'courtOrderInformation' not in json_data


@pytest.mark.parametrize('desc,roles,status,has_account,reg_number', TEST_DEBTOR_NAMES)
def test_get_debtor_names(session, client, jwt, desc, roles, status, has_account, reg_number):
    """Assert that a request to get the debtor names for a base registration works as expected."""
    # setup
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)

    # test
    path = '/api/v1/financing-statements/' + reg_number + '/debtorNames'

    response = client.get(path,
                          headers=headers)

    # check
    assert response.status_code == status
    if response.status_code == HTTPStatus.OK:
        json_data = response.json
        if reg_number == 'TEST0001':
            assert json_data
            assert len(json_data) > 0
        # print(json_data)
