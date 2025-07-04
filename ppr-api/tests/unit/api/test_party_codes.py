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

"""Tests to verify the party-codes endpoint.

Test-Suite to ensure that the /party-codes endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest

from ppr_api.services.authz import STAFF_ROLE, PPR_ROLE, COLIN_ROLE
from tests.unit.services.utils import create_header_account, create_header

TEST_CODE_NEW1 =   {
    "businessName": "PETERBILT TRUCKS PACIFIC INC.",
    "address": {
      "street": "1079 DOUGLAS ST",
      "city": "VICTORIA",
      "region": "BC",
      "country": "CA",
      "postalCode": "V8W 2C5"
    },
    "emailAddress": "test-1@test-ptc.com",
    "contact": {
      "name": "Example Contact 1",
      "areaCode": "250",
      "phoneNumber": "3564500"
    }
}
TEST_CODE_NEW2 =   {
    "accountId": "1234",
    "businessName": "PETERBILT TRUCKS PACIFIC INC.",
    "address": {
      "street": "1079 DOUGLAS ST",
      "city": "VICTORIA",
      "region": "BC",
      "country": "CA",
      "postalCode": "V8W 2C5"
    },
    "emailAddress": "test-1@test-ptc.com",
    "contact": {
      "name": "Example Contact 1",
      "areaCode": "250",
      "phoneNumber": "3564500"
    }
}
TEST_CODE_NEW3 =   {
    "address": {
      "street": "1079 DOUGLAS ST",
      "city": "VICTORIA",
      "region": "BC",
      "country": "CA",
      "postalCode": "V8W 2C5"
    },
    "contact": {
      "name": "Example Contact 1",
      "areaCode": "250",
      "phoneNumber": "3564500"
    }
}
TEST_CODE_NAME1 =   {
    "businessName": "PETERBILT TRUCKS PACIFIC INC.",
}
TEST_CODE_NAME2 =   {
    "accountId": "PS00002",
    "businessName": "PETERBILT TRUCKS PACIFIC INC.",
}
TEST_CODE_NAME3 =   {
    "accountId": "PS00002",
    "businessName": "CC \U0001d5c4\U0001d5c6/\U0001d5c1",
}

ROLES_STAFF = [PPR_ROLE, STAFF_ROLE]
ROLES_PPR = [PPR_ROLE]
ROLES_INVALID = [COLIN_ROLE]
# testdata pattern is ({description}, {is staff}, {include account}, {response status}, {role}, {search_value})
TEST_DATA_PARTY_CODE = [
    ('Valid non-staff non-existent', False, True, HTTPStatus.NOT_FOUND, PPR_ROLE, '12345'),
    ('Valid non-staff exists', False, True, HTTPStatus.OK, PPR_ROLE, '200000000'),
    ('Non-staff missing account ID', False, False, HTTPStatus.BAD_REQUEST, PPR_ROLE, '200000000'),
    ('Staff missing account ID', True, False, HTTPStatus.OK, PPR_ROLE, '200000000'),
    ('Valid data but unauthorized', False, True, HTTPStatus.UNAUTHORIZED, COLIN_ROLE, '200000000')
]
# testdata pattern is ({description}, {is staff}, {include account}, {response status}, {role}, {search_value})
TEST_DATA_HEAD_OFFICE = [
    ('Valid non-staff code exists', False, True, HTTPStatus.OK, PPR_ROLE, '999'),
    ('Valid non-staff name exists', False, True, HTTPStatus.OK, PPR_ROLE, 'rbc royal bank'),
    ('Valid non-staff non-existent', False, True, HTTPStatus.OK, PPR_ROLE, '8999'),
    ('Non-staff missing account ID', False, False, HTTPStatus.BAD_REQUEST, PPR_ROLE, '9999'),
    ('Staff missing account ID', True, False, HTTPStatus.OK, PPR_ROLE, 'RBC Royal Bank'),
    ('Valid data but unauthorized', False, True, HTTPStatus.UNAUTHORIZED, COLIN_ROLE, '9999')
]
# testdata pattern is ({description}, {is staff}, {response status}, {role}, {account_id}, {has_data}, {sec_act}, {search_id})
TEST_DATA_ACCOUNT = [
    ('Valid non-staff non-existent', False, HTTPStatus.OK, PPR_ROLE, 'PS1234X', False, False, None),
    ('Valid non-staff CC exists', False, HTTPStatus.OK, PPR_ROLE, 'PS12345', True, False, None),
    ('Valid non-staff Securities Act exists', False, HTTPStatus.OK, PPR_ROLE, 'PS00002', True, True, None),
    ('Valid non-staff Securities Act non-existent', False, HTTPStatus.OK, PPR_ROLE, 'PS12345', False, True, None),
    ('Valid non-staff non CC exists', False, HTTPStatus.OK, PPR_ROLE, 'PS00001', False, False, None),
    ('Non-staff missing account ID', False, HTTPStatus.BAD_REQUEST, PPR_ROLE, None, False, False, None),
    ('Staff missing account ID', True, HTTPStatus.BAD_REQUEST, PPR_ROLE, None, False, False, None),
    ('Unauthorized role', False, HTTPStatus.UNAUTHORIZED, COLIN_ROLE, 'PS12345', False, False, None),
    ('Valid search id exists', False, HTTPStatus.OK, PPR_ROLE, 'PS12', True, False, 'UT0005'),
    ('Valid search id non-existent', False, HTTPStatus.OK, PPR_ROLE, 'PS12', False, False, 'UT00XX'),
]
# testdata pattern is ({description}, {include account}, {response status}, {roles}, {payload})
TEST_DATA_CREATE_CODE = [
    ('Valid non-staff', True, HTTPStatus.CREATED, ROLES_PPR, TEST_CODE_NEW1),
    ('Valid staff', True, HTTPStatus.CREATED, ROLES_STAFF, TEST_CODE_NEW2),
    ('Non-staff missing account ID', False, HTTPStatus.BAD_REQUEST, ROLES_PPR, TEST_CODE_NEW1),
    ('Staff missing account ID', False, HTTPStatus.BAD_REQUEST, ROLES_STAFF, TEST_CODE_NEW2),
    ('Unauthorized', True, HTTPStatus.UNAUTHORIZED, ROLES_INVALID, TEST_CODE_NEW1),
    ('Extra validation error', True, HTTPStatus.BAD_REQUEST, ROLES_STAFF, TEST_CODE_NEW1),
    ('Schema validation error', True, HTTPStatus.BAD_REQUEST, ROLES_PPR, TEST_CODE_NEW3),
]
# testdata pattern is ({description}, {include account}, {response status}, {roles}, {payload}, {head_code}, {branch_code})
TEST_DATA_CHANGE_NAME = [
    ('Valid non-staff branch', True, HTTPStatus.OK, ROLES_PPR, TEST_CODE_NAME1, None, "99980001"),
    ('Valid staff head', True, HTTPStatus.OK, ROLES_STAFF, TEST_CODE_NAME2, "9998", None),
    ('Non-staff missing account ID', False, HTTPStatus.BAD_REQUEST, ROLES_PPR, TEST_CODE_NAME1, None, "99980001"),
    ('Staff missing account ID', False, HTTPStatus.BAD_REQUEST, ROLES_STAFF, TEST_CODE_NAME2, None, "99980001"),
    ('Unauthorized', True, HTTPStatus.UNAUTHORIZED, ROLES_INVALID, TEST_CODE_NAME1, None, "99980001"),
    ('Extra validation error', True, HTTPStatus.BAD_REQUEST, ROLES_STAFF, TEST_CODE_NAME3, None, "99980001"),
    ('Invalid branch code', True, HTTPStatus.NOT_FOUND, ROLES_PPR, TEST_CODE_NAME1, None, "99989901"),
    ('Invalid head code', True, HTTPStatus.NOT_FOUND, ROLES_PPR, TEST_CODE_NAME1, "9910", None),
]


@pytest.mark.parametrize('desc,include_account,status,roles,payload,head_code,branch_code', TEST_DATA_CHANGE_NAME)
def test_party_code_change_name(session, client, jwt, desc, include_account, status, roles, payload, head_code, branch_code):
    """Assert that a create party code request returns the expected response code and data."""
    # setup
    headers = None
    if include_account:
        headers = create_header_account(jwt, roles, account_id='PS00002')
    else:
        headers = create_header(jwt, roles)
    test_data = copy.deepcopy(payload)
    if head_code:
        test_data["headOfficeCode"] = head_code
    if branch_code:
        test_data["code"] = branch_code

    # test
    rv = client.patch('/api/v1/party-codes/accounts/names',
                     json=test_data,
                     headers=headers,
                     content_type='application/json')
    # check
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        assert rv.json
        response_json = rv.json
        assert response_json.get('code')
        assert response_json.get('headOfficeCode')
        assert response_json.get('accountId')
        assert response_json.get('contact')
        assert response_json.get('address')
        assert response_json.get('businessName')


@pytest.mark.parametrize('desc,include_account,status,roles,payload', TEST_DATA_CREATE_CODE)
def test_create_party_code(session, client, jwt, desc, include_account, status, roles, payload):
    """Assert that a create party code request returns the expected response code and data."""
    # setup
    headers = None
    if include_account:
        headers = create_header_account(jwt, roles, account_id='UT-12345')
    else:
        headers = create_header(jwt, roles)

    # test
    rv = client.post('/api/v1/party-codes/accounts',
                     json=payload,
                     headers=headers,
                     content_type='application/json')
    # check
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.CREATED:
        assert rv.json
        response_json = rv.json
        assert response_json.get('code')
        assert response_json.get('headOfficeCode')
        assert response_json.get('accountId')
        assert response_json.get('contact')
        assert response_json.get('address')
        assert response_json.get('businessName')


@pytest.mark.parametrize('desc,staff,include_account,status,role,search_value', TEST_DATA_PARTY_CODE)
def test_get_party_codes(session, client, jwt, desc, staff, include_account, status, role, search_value):
    """Assert that a get party code returns the expected response code and data."""
    # setup
    headers = None
    if include_account:
        if staff:
            headers = create_header_account(jwt, [role, STAFF_ROLE])
        else:
            headers = create_header_account(jwt, [role])
    else:
        if staff:
            headers = create_header(jwt, [role, STAFF_ROLE])
        else:
            headers = create_header(jwt, [role])

    # test
    rv = client.get(('/api/v1/party-codes/' + search_value), headers=headers)
    # check
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        assert rv.json
        assert 'contact' in rv.json
        assert 'address' in rv.json
        assert 'businessName' in rv.json


@pytest.mark.parametrize('desc,staff,include_account,status,role,search_value', TEST_DATA_HEAD_OFFICE)
def test_get_head_office_codes(session, client, jwt, desc, staff, include_account, status, role, search_value):
    """Assert that a get head office party code information returns the expected response code and data."""
    # setup
    headers = None
    if include_account:
        if staff:
            headers = create_header_account(jwt, [role, STAFF_ROLE])
        else:
            headers = create_header_account(jwt, [role])
    else:
        if staff:
            headers = create_header(jwt, [role, STAFF_ROLE])
        else:
            headers = create_header(jwt, [role])

    # test
    rv = client.get(('/api/v1/party-codes/head-offices/' + search_value), headers=headers)
    # check
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        if search_value != '8999':
            assert rv.json
            assert len(rv.json) >= 4
        else:
            assert not rv.json


@pytest.mark.parametrize('desc,staff,status,role,account_id,has_data,sec_act,search_id', TEST_DATA_ACCOUNT)
def test_get_account_codes(session, client, jwt, desc, staff, status, role, account_id, has_data, sec_act, search_id):
    """Assert that a get party code information by account ID returns the expected response code and data."""
    # setup
    headers = None
    if account_id:
        if staff:
            headers = create_header_account(jwt, [role, STAFF_ROLE], 'test-user', account_id)
        else:
            headers = create_header_account(jwt, [role], 'test-user', account_id)
    else:
        if staff:
            headers = create_header(jwt, [role, STAFF_ROLE])
        else:
            headers = create_header(jwt, [role])
    path: str = '/api/v1/party-codes/accounts'
    if sec_act:
        path += '?securitiesActCodes=true'
    elif search_id:
        path += f'?searchAccountId={search_id}'
    # test
    rv = client.get(path, headers=headers)
    # check
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        if has_data:
            assert rv.json
            client_code_json = rv.json
            assert len(client_code_json) > 0
            for client_party in client_code_json:
                assert client_party['code']
                assert client_party['businessName']
        else:
            assert not rv.json


def test_get_head_office_fuzzy(session, client, jwt):
    """Assert that a get head office party codes by fuzzy name search returns the expected response code and data."""
    # setup
    headers = create_header_account(jwt, [PPR_ROLE])

    # test
    rv = client.get(('/api/v1/party-codes/head-offices/rbc?fuzzyNameSearch=true'), headers=headers)
    # check
    assert rv.status_code == HTTPStatus.OK
    assert rv.json
    assert len(rv.json) >= 4
