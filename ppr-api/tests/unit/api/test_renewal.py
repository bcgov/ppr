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

"""Tests to verify the financing-statement renewals endpoint.

Test-Suite to ensure that the /financing-statement/registrationNum/renewals endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app
from registry_schemas.example_data.ppr import FINANCING_STATEMENT

from ppr_api.models import FinancingStatement, Registration, utils as model_utils
from ppr_api.resources.financing_statements import get_payment_details
from ppr_api.services.authz import COLIN_ROLE, PPR_ROLE, STAFF_ROLE
from tests.unit.services.utils import create_header, create_header_account


MOCK_URL_NO_KEY = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
# prep sample post renewal statement data
STATEMENT_VALID = {
    'baseRegistrationNumber': 'TEST0001',
    'clientReferenceId': 'A-00000402',
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
    'expiryDate': '2025-02-21T23:59:59+00:00',
    'payment': {
        'receipt': '/pay/api/v1/payment-requests/2199700/receipts',
        'invoiceId': '2199700'
    }
}
MISSING_BASE_DEBTOR = {
    'baseRegistrationNumber': 'TEST0001',
    'clientReferenceId': 'A-00000402',
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
    'expiryDate': '2025-02-21T23:59:59+00:00',
    'payment': {
        'receipt': '/pay/api/v1/payment-requests/2199700/receipts',
        'invoiceId': '2199700'
    }
}
INVALID_BASE_DEBTOR = {
    'baseRegistrationNumber': 'TEST0001',
    'clientReferenceId': 'A-00000402',
    'debtorName': {
        'businessName': 'XEST BUS 3 DEBTOR'
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
    'expiryDate': '2025-02-21T23:59:59+00:00',
    'payment': {
        'receipt': '/pay/api/v1/payment-requests/2199700/receipts',
        'invoiceId': '2199700'
    }
}
INVALID_REG_NUM = {
    'baseRegistrationNumber': 'TESTXXX1',
    'clientReferenceId': 'A-00000402',
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
    'expiryDate': '2025-02-21T23:59:59+00:00',
    'payment': {
        'receipt': '/pay/api/v1/payment-requests/2199700/receipts',
        'invoiceId': '2199700'
    }
}
INVALID_HISTORICAL = {
    'baseRegistrationNumber': 'TEST0003',
    'clientReferenceId': 'A-00000402',
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
    'expiryDate': '2025-02-21T23:59:59+00:00',
    'payment': {
        'receipt': '/pay/api/v1/payment-requests/2199700/receipts',
        'invoiceId': '2199700'
    }
}
INVALID_CODE = {
    'baseRegistrationNumber': 'TEST0001',
    'clientReferenceId': 'A-00000402',
    'debtorName': {
        'businessName': 'TEST BUS 2 DEBTOR'
    },
    'registeringParty': {
        'code': '300000000'
    },
    'expiryDate': '2025-02-21T23:59:59+00:00',
    'payment': {
        'receipt': '/pay/api/v1/payment-requests/2199700/receipts',
        'invoiceId': '2199700'
    }
}
INVALID_ADDRESS = {
    'baseRegistrationNumber': 'TEST0001',
    'clientReferenceId': 'A-00000402',
    'debtorName': {
        'businessName': 'TEST BUS 2 DEBTOR'
    },
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
    'expiryDate': '2025-02-21T23:59:59+00:00',
    'payment': {
        'receipt': '/pay/api/v1/payment-requests/2199700/receipts',
        'invoiceId': '2199700'
    }
}

# testdata pattern is ({description}, {test data}, {roles}, {status}, {has_account}, {reg_num})
TEST_CREATE_DATA = [
    ('Invalid registration number', INVALID_REG_NUM, [PPR_ROLE], HTTPStatus.NOT_FOUND, True, 'TESTXXX1'),
    ('Invalid missing base debtor', MISSING_BASE_DEBTOR, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0001'),
    ('Invalid base debtor', INVALID_BASE_DEBTOR, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0001'),
    ('Invalid historical', INVALID_HISTORICAL, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0013'),
    ('Invalid party code extra validation', INVALID_CODE, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0001'),
    ('Invalid party address extra validation', INVALID_ADDRESS, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0001'),
    ('Missing account', STATEMENT_VALID, [PPR_ROLE], HTTPStatus.BAD_REQUEST, False, 'TEST0001'),
    ('Invalid role', STATEMENT_VALID, [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 'TEST0001')
]

# testdata pattern is ({description}, {roles}, {status}, {has_account}, {reg_num}, {base_reg_num})
TEST_GET_STATEMENT = [
    ('Missing account', [PPR_ROLE], HTTPStatus.BAD_REQUEST, False, 'TEST00R5', 'TEST0005'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 'TEST00R5', 'TEST0005'),
    ('Valid Request', [PPR_ROLE], HTTPStatus.OK, True, 'TEST00R5', 'TEST0005'),
    ('Valid Request other account', [PPR_ROLE], HTTPStatus.OK, True, 'TEST0021RE', 'TEST0021'),
    ('Unauthorized Request other account', [PPR_ROLE], HTTPStatus.UNAUTHORIZED, True, 'TEST0019RE', 'TEST0019'),
    ('Invalid Registration Number', [PPR_ROLE], HTTPStatus.NOT_FOUND, True, 'TESTXXXX', 'TEST0005'),
    ('Mismatch registrations non-staff', [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST00R5', 'TEST0001'),
    ('Mismatch registrations staff', [PPR_ROLE, STAFF_ROLE], HTTPStatus.OK, True, 'TEST00R5', 'TEST0001'),
    ('Missing account staff', [PPR_ROLE, STAFF_ROLE], HTTPStatus.OK, False, 'TEST00R5', 'TEST0005')
]


@pytest.mark.parametrize('desc,json_data,roles,status,has_account,reg_num', TEST_CREATE_DATA)
def test_create_renewal(session, client, jwt, desc, json_data, roles, status, has_account, reg_num):
    """Assert that a post renewal registration statement works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.post('/api/v1/financing-statements/' + reg_num + '/renewals',
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    assert response.status_code == status


@pytest.mark.parametrize('desc,roles,status,has_account,reg_num,base_reg_num', TEST_GET_STATEMENT)
def test_get_renewal(session, client, jwt, desc, roles, status, has_account, reg_num, base_reg_num):
    """Assert that a get renewal registration statement works as expected."""
    current_app.config.update(AUTH_SVC_URL=MOCK_URL_NO_KEY)
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.get('/api/v1/financing-statements/' + base_reg_num + '/renewals/' + reg_num,
                          headers=headers)

    # check
    assert response.status_code == status
    # basic verification statement data check
    if status == HTTPStatus.OK:
        json_data = response.json
        assert json_data['renewalRegistrationNumber'] == reg_num
        assert len(json_data['changes']) >= 1
        assert json_data['changes'][0]['renewalRegistrationNumber'] == reg_num
        if desc != 'Mismatch registrations staff':
            assert json_data['baseRegistrationNumber'] == base_reg_num
            assert json_data['changes'][0]['baseRegistrationNumber'] == base_reg_num


def test_renewal_sa_success(session, client, jwt):
    """Assert that a valid create statement returns a 201 status."""
    # setup
    rv1 = create_financing_test(session, client, jwt, 'SA')
    assert rv1.status_code == HTTPStatus.CREATED
    assert rv1.json['baseRegistrationNumber']
    base_reg_num = rv1.json['baseRegistrationNumber']

    json_data = copy.deepcopy(STATEMENT_VALID)
    json_data['baseRegistrationNumber'] = base_reg_num
    json_data['debtorName']['businessName'] = 'TEST BUS 2 DEBTOR'
    del json_data['payment']

    # test
    rv = client.post('/api/v1/financing-statements/' + base_reg_num + '/renewals',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED
    # basic verification statement data check
    json_data = rv.json
    assert 'renewalRegistrationNumber' in json_data
    assert len(json_data['changes']) >= 1
    assert 'renewalRegistrationNumber' in json_data['changes'][0]
    assert json_data['baseRegistrationNumber'] == base_reg_num
    assert json_data['changes'][0]['baseRegistrationNumber'] == base_reg_num


def test_renewal_rl_success(session, client, jwt):
    """Assert that a valid repairer's lien create statement returns a 200 status."""
    # setup
    rv1 = create_financing_test(session, client, jwt, 'RL')
    assert rv1.status_code == HTTPStatus.CREATED
    assert rv1.json['baseRegistrationNumber']
    base_reg_num = rv1.json['baseRegistrationNumber']

    json_data = copy.deepcopy(STATEMENT_VALID)
    json_data['baseRegistrationNumber'] = base_reg_num
    json_data['debtorName']['businessName'] = 'TEST BUS 2 DEBTOR'
    del json_data['payment']

    # test
    rv = client.post('/api/v1/financing-statements/' + base_reg_num + '/renewals',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED
    json_data = rv.json
    assert 'renewalRegistrationNumber' in json_data
    assert len(json_data['changes']) >= 1
    assert 'renewalRegistrationNumber' in json_data['changes'][0]
    assert json_data['baseRegistrationNumber'] == base_reg_num
    assert json_data['changes'][0]['baseRegistrationNumber'] == base_reg_num


def test_get_payment_details_registration(session, client, jwt):
    """Assert that a valid renewal request payment details setup works as expected."""
    # setup
    json_data = copy.deepcopy(STATEMENT_VALID)
    registration_num = 'TEST0001'
    statement = FinancingStatement.find_by_registration_number(registration_num, False)
    registration = Registration.create_from_json(json_data,
                                                 'RENEWAL',
                                                 statement,
                                                 registration_num,
                                                 'PS12345')
    # test
    details = get_payment_details(registration)

    # check
    assert details
    assert details['label'] == 'Renew Registration:'
    assert details['value'].startswith('TEST0001 for ')


def create_financing_test(session, client, jwt, type):
    """Create a financing statement for testing."""
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['debtors'][0]['businessName'] = 'TEST BUS 2 DEBTOR'
    statement['type'] = type
    del statement['createDateTime']
    del statement['baseRegistrationNumber']
    del statement['payment']
    del statement['documentId']
    del statement['lifeInfinite']
    del statement['generalCollateral']
    if type != 'RL':
        del statement['lienAmount']
        del statement['surrenderDate']
    else:
        del statement['trustIndenture']
        statement['lifeYears'] = 1
        statement['surrenderDate'] = model_utils.format_ts(model_utils.now_ts())
    return client.post('/api/v1/financing-statements',
                       json=statement,
                       headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                       content_type='application/json')
