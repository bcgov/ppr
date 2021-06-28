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
from registry_schemas.example_data.ppr import FINANCING_STATEMENT

from ppr_api.models import FinancingStatement, Registration
from ppr_api.resources.financing_statements import get_payment_details
from ppr_api.services.authz import COLIN_ROLE, PPR_ROLE, STAFF_ROLE
from tests.unit.services.utils import create_header, create_header_account


# prep sample post renewal statement data
STATEMENT_VALID = {
    'baseRegistrationNumber': 'TEST0001',
    'clientReferenceId': 'A-00000402',
    'baseDebtor': {
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
    'baseDebtor': {
        'businessName': 'TEST BUS 3 DEBTOR'
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
    'baseDebtor': {
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
    'baseDebtor': {
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
    'baseDebtor': {
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
    'baseDebtor': {
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
    ('Invalid historical', INVALID_HISTORICAL, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0003'),
    ('Invalid party code extra validation', INVALID_CODE, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0001'),
    ('Invalid party address extra validation', INVALID_ADDRESS, [PPR_ROLE], HTTPStatus.BAD_REQUEST, True, 'TEST0001'),
    ('Missing account', STATEMENT_VALID, [PPR_ROLE], HTTPStatus.BAD_REQUEST, False, 'TEST0001'),
    ('Invalid role', STATEMENT_VALID, [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 'TEST0001')
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


def test_renewal_sa_success(session, client, jwt):
    """Assert that a valid create statement returns a 201 status."""
    # setup
    rv1 = create_financing_test(session, client, jwt, 'SA')
    assert rv1.status_code == HTTPStatus.CREATED
    assert rv1.json['baseRegistrationNumber']
    base_reg_num = rv1.json['baseRegistrationNumber']

    json_data = copy.deepcopy(STATEMENT_VALID)
    json_data['baseRegistrationNumber'] = base_reg_num
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
    del json_data['payment']

    # test
    rv = client.post('/api/v1/financing-statements/' + base_reg_num + '/renewals',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED


def test_renewal_rl_success(session, client, jwt):
    """Assert that a valid repairer's lien create statement returns a 200 status."""
    # setup
    rv1 = create_financing_test(session, client, jwt, 'RL')
    assert rv1.status_code == HTTPStatus.CREATED
    assert rv1.json['baseRegistrationNumber']
    base_reg_num = rv1.json['baseRegistrationNumber']

    json_data = copy.deepcopy(STATEMENT_VALID)
    json_data['baseRegistrationNumber'] = base_reg_num
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
    del json_data['payment']

    # test
    rv = client.post('/api/v1/financing-statements/' + base_reg_num + '/renewals',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED


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
    assert details['label'] == 'Register a Renewal Statement for Base Registration:'
    assert details['value'] == 'TEST0001'


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
        del statement['lifeYears']
    return client.post('/api/v1/financing-statements',
                       json=statement,
                       headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                       content_type='application/json')
