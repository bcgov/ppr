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

from ppr_api.models import UserProfile
from ppr_api.services.authz import (
    STAFF_ROLE,
    PPR_ROLE,
    COLIN_ROLE,
    REGISTER_MH,
    TRANSFER_SALE_BENEFICIARY,
    REQUEST_TRANSPORT_PERMIT,
    TRANSFER_DEATH_JT
)
from tests.unit.services.utils import create_header_account, create_header, create_header_account_idp


# Properties can be anything, using show* for testing.
REGISTRATIONS_TABLE = {
    'showColumn1': True,
    'showColumn2': False,
    'showColumn3': True,
    'showColumn4': False
}
# Properties can be anything, using misc* for testing.
MISC_PREFERENCES = {
    'preference1': 'A',
    'preference2': False,
    'preference3': 3
}
TEST_UPDATE_JSON = {
    'paymentConfirmationDialog': True,
    'selectConfirmationDialog': False
}
TEST_UPDATE_REG_TABLE_JSON = {
    'registrationsTable': REGISTRATIONS_TABLE
}
TEST_UPDATE_MISC_JSON = {
    'miscellaneousPreferences': MISC_PREFERENCES
}

TEST_INVALID_JSON = {
}
# testdata pattern is ({description}, {is staff}, {include account}, {response status}, {role})
TEST_DATA = [
    ('Valid', False, True, HTTPStatus.OK, PPR_ROLE),
    ('Missing account ID', False, False, HTTPStatus.BAD_REQUEST, PPR_ROLE),
    ('Staff missing account ID', True, False, HTTPStatus.OK, PPR_ROLE),
    ('Valid data but unauthorized', False, True, HTTPStatus.UNAUTHORIZED, COLIN_ROLE)
]
# testdata pattern is ({description}, {is staff}, {include account}, {response status}, {role}, {data})
TEST_DATA_UPDATE = [
    ('Valid default settings', False, True, HTTPStatus.OK, PPR_ROLE, TEST_UPDATE_JSON),
    ('Valid registration table', False, True, HTTPStatus.OK, PPR_ROLE, TEST_UPDATE_REG_TABLE_JSON),
    ('Valid miscellaneous preferences', False, True, HTTPStatus.OK, PPR_ROLE, TEST_UPDATE_MISC_JSON),
    ('Missing account ID', False, False, HTTPStatus.BAD_REQUEST, PPR_ROLE, TEST_UPDATE_JSON),
    ('Staff missing account ID', True, False, HTTPStatus.OK, PPR_ROLE, TEST_UPDATE_JSON),
    ('Valid data but unauthorized', False, True, HTTPStatus.UNAUTHORIZED, COLIN_ROLE, TEST_UPDATE_JSON),
    ('Schema validation error', False, True, HTTPStatus.BAD_REQUEST, PPR_ROLE, TEST_INVALID_JSON)
]
MANUFACTURER_ROLES = [PPR_ROLE, REGISTER_MH, TRANSFER_SALE_BENEFICIARY, REQUEST_TRANSPORT_PERMIT]
LAWYER_ROLES = [PPR_ROLE, TRANSFER_SALE_BENEFICIARY, TRANSFER_DEATH_JT]
DEALER_ROLES = [PPR_ROLE, REQUEST_TRANSPORT_PERMIT]
# testdata pattern is ({description}, {account_id}, {idp_userid}, {response status}, {roles}, {agreement_required})
TEST_DATA_AGREEMENT = [
    ('PPR USER', None, None, HTTPStatus.OK, [PPR_ROLE], False),
    ('MHR manufacturer not required', '2617', '190000000', HTTPStatus.OK, MANUFACTURER_ROLES, False),
    ('MHR manufacturer required', '3026', '190000001', HTTPStatus.OK, MANUFACTURER_ROLES, True),
    ('MHR lawyer not required', '2617', '190000000', HTTPStatus.OK, LAWYER_ROLES, False),
    ('MHR lawyer required', '3026', '190000001', HTTPStatus.OK, LAWYER_ROLES, True),
    ('MHR dealer not required', '2617', '190000000', HTTPStatus.OK, DEALER_ROLES, False),
    ('MHR dealer required', '3026', '190000001', HTTPStatus.OK, DEALER_ROLES, True)
]


@pytest.mark.parametrize('desc,account_id,idp_userid,status,roles,agreement_required', TEST_DATA_AGREEMENT)
def test_get_user_profile_agreement(session, client, jwt, desc, account_id, idp_userid, status, roles,
                                    agreement_required):
    """Assert that a get user profile conditionally returns the expected MHR service agreement information."""
    # setup
    headers = None
    if account_id:
        headers = create_header_account_idp(jwt, roles, idp_userid, 'test-user', account_id)
    else:
        headers = create_header_account(jwt, roles)

    if agreement_required:
        profile: UserProfile = UserProfile.find_by_id(int(idp_userid))
        if profile and not profile.service_agreements.get('acceptAgreementRequired'):
            profile.service_agreements['acceptAgreementRequired'] = True

    # test
    rv = client.get('/api/v1/user-profile', headers=headers)
    # check
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        response_data = rv.json
        assert response_data
        if agreement_required:
            assert response_data.get('acceptAgreementRequired')
        else:
            assert not response_data.get('acceptAgreementRequired')


@pytest.mark.parametrize('desc,staff,include_account,status,role', TEST_DATA)
def test_get_user_profile(session, client, jwt, desc, staff, include_account, status, role):
    """Assert that a get user profile returns the expected response code and data."""
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
    rv = client.get('/api/v1/user-profile', headers=headers)
    # check
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        response_data = rv.json
        assert response_data
        assert 'paymentConfirmationDialog' in response_data
        assert 'selectConfirmationDialog' in response_data
        assert 'defaultDropDowns' in response_data
        assert 'defaultTableFilters' in response_data
        assert 'hasSecuritiesActAccess' in response_data


@pytest.mark.parametrize('desc,staff,include_account,status,role,data', TEST_DATA_UPDATE)
def test_update_user_profile(session, client, jwt, desc, staff, include_account, status, role, data):
    """Assert that updating a user profile returns the expected response code and data."""
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
    # create profile
    client.get('/api/v1/user-profile', headers=headers)

    # test
    rv = client.patch('/api/v1/user-profile',
                      json=data,
                      headers=headers,
                      content_type='application/json')
    # check
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        response_data = rv.json
        assert response_data
        assert 'paymentConfirmationDialog' in response_data
        assert 'selectConfirmationDialog' in response_data
        assert 'defaultDropDowns' in response_data
        assert 'defaultTableFilters' in response_data
        if desc == 'Valid registration table':
            assert 'registrationsTable' in response_data
            assert response_data['registrationsTable'] == TEST_UPDATE_REG_TABLE_JSON['registrationsTable']
        elif desc == 'Valid miscellaneous preferences':
            assert 'miscellaneousPreferences' in response_data
            assert response_data['miscellaneousPreferences'] == TEST_UPDATE_MISC_JSON['miscellaneousPreferences']
