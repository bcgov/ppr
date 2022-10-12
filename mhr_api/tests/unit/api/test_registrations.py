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

"""Tests to verify the endpoints for maintaining MH registrations.

Test-Suite to ensure that the /registrations endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app
from registry_schemas.example_data.mhr import REGISTRATION

from mhr_api.models import MhrRegistration
from mhr_api.services.authz import COLIN_ROLE, MHR_ROLE, STAFF_ROLE, BCOL_HELP
from tests.unit.services.utils import create_header, create_header_account


MOCK_AUTH_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
MOCK_PAY_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/pay/api/v1/'

# testdata pattern is ({desc}, {roles}, {status}, {has_account}, {results_size})
TEST_GET_ACCOUNT_DATA = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, False, 0),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 0),
    ('Valid request', [MHR_ROLE], HTTPStatus.OK, True, 1),
    ('Invalid request staff no account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, 0)
]
# testdata pattern is ({description}, {has_submitting}, {roles}, {status}, {has_account})
TEST_CREATE_DATA = [
    ('Invalid schema validation no submitting', False, [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, True),
    ('Missing account', True, [MHR_ROLE], HTTPStatus.BAD_REQUEST, False),
    ('Staff missing account', True, [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False),
    ('Invalid role', True, [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True),
    ('Invalid non-staff role', True, [MHR_ROLE], HTTPStatus.UNAUTHORIZED, True),
    ('Valid staff', True, [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, True)
]
# testdata pattern is ({description}, {roles}, {status}, {account}, {mhr_num})
TEST_GET_REGISTRATION = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, None, '150062'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, '2523', '150062'),
    ('Valid Request', [MHR_ROLE], HTTPStatus.OK, '2523', '150062'),
    ('Valid Request reg staff', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, STAFF_ROLE, '150062'),
    ('Valid Request bcol helpdesk', [MHR_ROLE, BCOL_HELP], HTTPStatus.OK, BCOL_HELP, '150062'),
    ('Valid Request other account', [MHR_ROLE], HTTPStatus.OK, 'PS12345', '150062'),
    ('Invalid MHR Number', [MHR_ROLE], HTTPStatus.NOT_FOUND, '2523', 'TESTXXXX'),
    ('Invalid request Staff no account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, None, '150062')
]


@pytest.mark.parametrize('desc,roles,status,has_account,results_size', TEST_GET_ACCOUNT_DATA)
def test_get_account_registrations(session, client, jwt, desc, roles, status, has_account, results_size):
    """Assert that a get account registrations summary list endpoint works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    # test
    rv = client.get('/api/v1/registrations',
                    headers=headers)

    # check
    # print(rv.json)
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        assert rv.json
        assert len(rv.json) >= results_size
        for registration in rv.json:
            assert registration['mhrNumber']
            assert registration['registrationDescription']
            assert registration['statusType'] is not None
            assert registration['createDateTime'] is not None
            assert registration['username'] is not None
            assert registration['submittingParty'] is not None
            assert registration['clientReferenceId'] is not None
            assert registration['ownerNames'] is not None
            assert registration['path'] is not None


@pytest.mark.parametrize('desc,has_submitting,roles,status,has_account', TEST_CREATE_DATA)
def test_create(session, client, jwt, desc, has_submitting, roles, status, has_account):
    """Assert that a post MH registration works as expected."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    json_data = copy.deepcopy(REGISTRATION)
    if not has_submitting:
        del json_data['submittingParty']
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    if status == HTTPStatus.CREATED and STAFF_ROLE in roles:
        json_data['documentId'] = '80048756'

    # test
    response = client.post('/api/v1/registrations',
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    assert response.status_code == status
    if response.status_code == HTTPStatus.CREATED:
        registration: MhrRegistration = MhrRegistration.find_by_mhr_number(response.json['mhrNumber'],
                                                                           'PS12345')
        assert registration


@pytest.mark.parametrize('desc,roles,status,account_id,mhr_num', TEST_GET_REGISTRATION)
def test_get_registration(session, client, jwt, desc, roles, status, account_id, mhr_num):
    """Assert that a get account registration by MHR number works as expected."""
    # setup
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    if account_id:
        headers = create_header_account(jwt, roles, 'test-user', account_id)
    else:
        headers = create_header(jwt, roles)

    # test
    response = client.get('/api/v1/registrations/' + mhr_num,
                          headers=headers)
    # check
    if status == HTTPStatus.NOT_FOUND:
        assert response.status_code in (status, HTTPStatus.UNAUTHORIZED)
    else:
        assert response.status_code == status
