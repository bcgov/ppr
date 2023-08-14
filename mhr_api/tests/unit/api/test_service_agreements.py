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

"""Tests to verify the service agreement endpoints.

Test-Suite to ensure that the /service-agreements/* endpoints are working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app

from mhr_api.services.authz import COLIN_ROLE, MHR_ROLE, STAFF_ROLE

from tests.unit.services.utils import create_header, create_header_account


TEST_JSON = {
    'agreementType': 'DEFAULT',
    'version': 'v1',
    'accepted': True
}
# testdata pattern is ({desc}, {roles}, {status}, {has_account})
TEST_GET_DATA_LIST = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, False),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True),
    ('Valid request MHR', [MHR_ROLE], HTTPStatus.OK, True)
]
# testdata pattern is ({desc}, {roles}, {status}, {has_account}, {version})
TEST_GET_DATA_VERSION = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, False, 'v1'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 'v1'),
    ('Invalid request JUNK', [MHR_ROLE], HTTPStatus.NOT_FOUND, True, 'JUNK'),
    ('Valid request v1', [MHR_ROLE], HTTPStatus.OK, True, 'v1'),
    ('Valid request V1', [MHR_ROLE], HTTPStatus.OK, True, 'V1'),
    ('Valid request latest', [MHR_ROLE], HTTPStatus.OK, True, 'latest'),
    ('Valid request CURRENT', [MHR_ROLE], HTTPStatus.OK, True, 'CURRENT')
]
# testdata pattern is ({desc}, {roles}, {status}, {account_id}, {version}, {username})
TEST_POST_DATA_VERSION = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, None, 'v1', 'UT-test-man'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, '2617', 'v1', 'UT-test-man'),
    ('Invalid request JUNK', [MHR_ROLE], HTTPStatus.NOT_FOUND, '2617', 'JUNK', 'UT-test-man'),
    ('Invalid request no version', [MHR_ROLE], HTTPStatus.BAD_REQUEST, '2617', 'v1', 'UT-test-man'),
    ('Invalid request not accepted', [MHR_ROLE], HTTPStatus.BAD_REQUEST, '2617', 'v1', 'UT-test-man'),
    ('Invalid request account id non-existent', [MHR_ROLE], HTTPStatus.BAD_REQUEST, 'abcdef', 'v1', 'UT-test-man'),
    ('Valid request manufacturer', [MHR_ROLE], HTTPStatus.OK, '2617', 'v1', 'UT-test-man'),
    ('Valid request lawyer', [MHR_ROLE], HTTPStatus.OK, '3026', 'v1', 'UT-test-qa')
]


@pytest.mark.parametrize('desc,roles,status,has_account', TEST_GET_DATA_LIST)
def test_get_agreement_list(session, client, jwt, desc, roles, status, has_account):
    """Assert that a get service agreements summary info list works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    # test
    response = client.get('/api/v1/service-agreements', headers=headers)

    # check
    # print(rv.json)
    assert response.status_code == status
    if response.status_code == HTTPStatus.OK:
        agreements_json = response.json
        assert agreements_json
        for agreement in agreements_json:
            assert agreement.get('agreementType')
            assert agreement.get('version')
            assert agreement.get('createDateTime')
            assert agreement.get('latestVersion')


@pytest.mark.parametrize('desc,roles,status,has_account,version', TEST_GET_DATA_VERSION)
def test_get_agreement_version(session, client, jwt, desc, roles, status, has_account, version):
    """Assert that a get service agreement version information works as expected."""
    headers = None
    # setup
    if has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    # test
    response = client.get('/api/v1/service-agreements/' + version, headers=headers)

    # check
    # print(rv.json)
    assert response.status_code == status
    if response.status_code == HTTPStatus.OK:
        agreement= response.json
        assert agreement
        assert agreement.get('agreementType')
        assert agreement.get('version')
        assert agreement.get('createDateTime')
        assert agreement.get('latestVersion')


@pytest.mark.parametrize('desc,roles,status,account_id,version,username', TEST_POST_DATA_VERSION)
def test_post_agreement_version(session, client, jwt, desc, roles, status, account_id, version, username):
    """Assert that a submit service agreement acceptance works as expected."""
    headers = None
    json_data = copy.deepcopy(TEST_JSON)
    if desc == 'Invalid request no version':
        del json_data['version']
    elif desc == 'Invalid request not accepted':
        json_data['accepted'] = False
    # setup
    if account_id:
        headers = create_header_account(jwt, roles, username, account_id)
    else:
        headers = create_header(jwt, roles)
    # test
    response = client.post('/api/v1/service-agreements/' + version,
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    # print(rv.json)
    assert response.status_code == status
    if response.status_code == HTTPStatus.OK:
        agreement= response.json
        assert agreement
        assert agreement.get('agreementType')
        assert agreement.get('version')
        assert agreement.get('accepted')
        assert agreement.get('acceptedDateTime')
