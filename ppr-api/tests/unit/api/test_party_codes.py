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
from http import HTTPStatus

import pytest

from ppr_api.services.authz import STAFF_ROLE, PPR_ROLE, COLIN_ROLE
from tests.unit.services.utils import create_header_account, create_header


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
            assert len(rv.json) == 4
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
