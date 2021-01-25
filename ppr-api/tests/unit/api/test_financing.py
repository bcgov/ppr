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
from registry_schemas.example_data.ppr import FINANCING_STATEMENT

from ppr_api.services.authz import STAFF_ROLE, COLIN_ROLE
from tests.unit.services.utils import create_header_account, create_header

# prep sample post financing statement data
SAMPLE_JSON = copy.deepcopy(FINANCING_STATEMENT)


#def test_financing_invalid_type_400(session, client, jwt):
def test_financing_create_invalid_type_400(client, jwt):
    """Assert that create statement with an invalid type returns a 400 error."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['type'] = 'XX'
    del json_data['createDateTime']
    del json_data['baseRegistrationNumber']
    del json_data['payment']
    del json_data['lifeInfinite']
    del json_data['lienAmount']
    del json_data['surrenderDate']
    del json_data['documentId']

    # test
    rv = client.post(f'/api/v1/financing-statements',
                     json=json_data,
                     headers=create_header_account(jwt, [STAFF_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST

def test_financing_create_valid_SA_201(client, jwt):
    """Assert that a valid SA type financing statement returns a 201 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['type'] = 'SA'
    del json_data['createDateTime']
    del json_data['baseRegistrationNumber']
    del json_data['payment']
    del json_data['lifeInfinite']
    del json_data['lienAmount']
    del json_data['surrenderDate']
    del json_data['documentId']

    # test
    rv = client.post(f'/api/v1/financing-statements',
                     json=json_data,
                     headers=create_header_account(jwt, [STAFF_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED

def test_financing_create_valid_RL_201(client, jwt):
    """Assert that a valid RL type financing statement returns a 201 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['type'] = 'RL'
    del json_data['createDateTime']
    del json_data['baseRegistrationNumber']
    del json_data['payment']
    del json_data['lifeInfinite']
    del json_data['trustIndenture']
    del json_data['generalCollateral']
    del json_data['documentId']
 
    # test
    rv = client.post(f'/api/v1/financing-statements',
                     json=json_data,
                     headers=create_header_account(jwt, [STAFF_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED


def test_financing_get_list_200(client, jwt):
    """Assert that a get financing statement summary list for an account returns a 200 status."""
    # setup
 
    # test
    rv = client.get(f'/api/v1/financing-statements',
                    headers=create_header_account(jwt, [STAFF_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.OK


def test_financing_valid_get_statement_200(client, jwt):
    """Assert that a valid get financing statement by registration number returns a 200 status."""
    # setup
 
    # test
    rv = client.get(f'/api/v1/financing-statements/TEST0001',
                    headers=create_header_account(jwt, [STAFF_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.OK

def test_financing_invalid_get_statement_404(client, jwt):
    """Assert that a get statement by invalid registration number returns a 404 status."""
    # setup
 
    # test
    rv = client.get(f'/api/v1/financing-statements/X12345X',
                    headers=create_header_account(jwt, [STAFF_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_financing_nonstaff_missing_account_400(client, jwt):
    """Assert that a create financing statement request with a non-staff jwt and no account ID returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['type'] = 'SA'
    del json_data['createDateTime']
    del json_data['baseRegistrationNumber']
    del json_data['payment']
    del json_data['lifeInfinite']
    del json_data['lienAmount']
    del json_data['surrenderDate']
    del json_data['documentId']

    # test
    rv = client.post(f'/api/v1/financing-statements',
                     json=json_data,
                     headers=create_header(jwt, [COLIN_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_financing_staff_missing_account_201(client, jwt):
    """Assert that a create financing statement request with a staff jwt and no account ID returns a 201 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['type'] = 'SA'
    del json_data['createDateTime']
    del json_data['baseRegistrationNumber']
    del json_data['payment']
    del json_data['lifeInfinite']
    del json_data['lienAmount']
    del json_data['surrenderDate']
    del json_data['documentId']

    # test
    rv = client.post(f'/api/v1/financing-statements',
                     json=json_data,
                     headers=create_header(jwt, [STAFF_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.CREATED


def test_financing_list_nonstaff_missing_account_400(client, jwt):
    """Assert that a list financing statements request with a non-staff jwt and no account ID returns a 400 status."""
    # setup

    # test
    rv = client.get(f'/api/v1/financing-statements',
                    headers=create_header(jwt, [COLIN_ROLE]))

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST

def test_financing_list_staff_missing_account_400(client, jwt):
    """Assert that a list financing statements request with a staff jwt and no account ID returns a 400 status."""
    # setup

    # test
    rv = client.get(f'/api/v1/financing-statements',
                    headers=create_header(jwt, [STAFF_ROLE]))

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_financing_get_nonstaff_missing_account_400(client, jwt):
    """Assert that a get financing statement request with a non-staff jwt and no account ID returns a 400 status."""
    # setup

    # test
    rv = client.get(f'/api/v1/financing-statements/TEST0001',
                    headers=create_header(jwt, [COLIN_ROLE]))

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST

def test_financing_get_staff_missing_account_200(client, jwt):
    """Assert that a get financing statement request with a staff jwt and no account ID returns a 200 status."""
    # setup

    # test
    rv = client.get(f'/api/v1/financing-statements/TEST0001',
                    headers=create_header(jwt, [STAFF_ROLE]))

    # check
    assert rv.status_code == HTTPStatus.OK


def test_financing_nonstaff_unauthorized_404(client, jwt):
    """Assert that a create financing statement request with a non-ppr role and account ID returns a 404 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['type'] = 'SA'
    del json_data['createDateTime']
    del json_data['baseRegistrationNumber']
    del json_data['payment']
    del json_data['lifeInfinite']
    del json_data['lienAmount']
    del json_data['surrenderDate']
    del json_data['documentId']

    # test
    rv = client.post(f'/api/v1/financing-statements',
                     json=json_data,
                     headers=create_header_account(jwt, [COLIN_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED

def test_financing_list_nonstaff_unauthorized_404(client, jwt):
    """Assert that a list financing statements request with a non-ppr role and account ID returns a 404 status."""
    # setup

    # test
    rv = client.get(f'/api/v1/financing-statements',
                    headers=create_header_account(jwt, [COLIN_ROLE]))

    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED

def test_financing_get_nonstaff_unauthorized_404(client, jwt):
    """Assert that a get financing statement request with a non-ppr role and account ID returns a 404 status."""
    # setup

    # test
    rv = client.get(f'/api/v1/financing-statements/TEST0001',
                    headers=create_header_account(jwt, [COLIN_ROLE]))

    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED

