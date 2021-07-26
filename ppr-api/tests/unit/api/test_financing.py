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
from http import HTTPStatus

import pytest

from ppr_api.models import FinancingStatement
from ppr_api.resources.financing_statements import get_payment_details_financing
from ppr_api.services.authz import COLIN_ROLE, PPR_ROLE, STAFF_ROLE
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


def test_get_payment_details_financing(session, client, jwt):
    """Assert that a valid financing statement request payment details setup works as expected."""
    # setup
    statement = FinancingStatement.create_from_json(FINANCING_VALID, 'PS12345')
    # test
    details = get_payment_details_financing(statement)

    # check
    assert details
    assert details['label'] == 'Create Financing Statement Type:'
    assert details['value'] == 'SA'


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
