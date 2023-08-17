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

"""Tests to verify the manufacturers endpoints.

Test-Suite to ensure that the /manufacturers/* endpoints are working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app

from mhr_api.models import MhrManufacturer
from mhr_api.services.authz import COLIN_ROLE, MHR_ROLE, STAFF_ROLE
from tests.unit.services.utils import create_header_account, create_header
from tests.unit.utils.test_registration_data import MANUFACTURER_VALID

MANUFACTURER_UPDATE = {
    'dbaName': 'DBA NAME',
    'authorizationName': 'John Smith',
    'termsAccepted': True,
    'description': {
        'manufacturer': 'NEW REAL ENGINEERED HOMES INC'
    }, 
  'location': {
    'address': {
      'city': 'VICTORIA', 
      'country': 'CA', 
      'postalCode': 'V2R 7A1', 
      'region': 'BC', 
      'street': 'NEW 1725 GOVERNMENT ST.'
    }, 
    'dealerName': 'NEW REAL ENGINEERED HOMES INC', 
    'locationType': 'MANUFACTURER'
  }, 
  'ownerGroups': [
    {
      'groupId': 1, 
      'owners': [
        {
          'address': {
            'city': 'VICTORIA',
            'country': 'CA', 
            'postalCode': 'V2R 7A1', 
            'region': 'BC', 
            'street': 'NEW 1725 GOVERNMENT ST.'
          }, 
          'organizationName': 'NEW REAL ENGINEERED HOMES INC', 
          'partyType': 'OWNER_BUS'
        }
      ], 
      'type': 'SOLE'
    }
  ], 
  'submittingParty': {
    'address': {
      'city': 'PENTICTON', 
      'country': 'CA', 
      'postalCode': 'V2A 7A1', 
      'region': 'BC', 
      'street': '1704 GOVERNMENT ST.'
    }, 
    'businessName': 'REAL ENGINEERED HOMES INC', 
    'phoneNumber': '2507701067'
  }
}

# testdata pattern is ({desc}, {roles}, {account_id}, {status}, {size})
TEST_ACCOUNT_DATA = [
    ('Valid', [MHR_ROLE], '2523', HTTPStatus.OK, 1),
    ('Valid no results', [MHR_ROLE], '1234', HTTPStatus.NOT_FOUND, 0),
    ('Non-staff no account', [MHR_ROLE], None, HTTPStatus.BAD_REQUEST, 0),
    ('Staff no account', [MHR_ROLE, STAFF_ROLE], None, HTTPStatus.BAD_REQUEST, 0),
    ('Unauthorized', [COLIN_ROLE], '1234', HTTPStatus.UNAUTHORIZED, 0)
]
# testdata pattern is ({desc}, {roles}, {account_id}, {status}, {has_submitting})
TEST_CREATE_DATA = [
    ('Valid', [MHR_ROLE], 'TEST', HTTPStatus.OK, True),
    ('Invalid exists', [MHR_ROLE], '2523', HTTPStatus.BAD_REQUEST, True),
    ('Invalid validation error', [MHR_ROLE], 'TEST', HTTPStatus.BAD_REQUEST, False)
]
# testdata pattern is ({desc}, {roles}, {account_id}, {status}, {size})
TEST_DELETE_DATA = [
    ('Valid', [MHR_ROLE], '2523', HTTPStatus.NO_CONTENT),
    ('Valid no results', [MHR_ROLE], '1234', HTTPStatus.NO_CONTENT),
    ('Staff no account', [MHR_ROLE, STAFF_ROLE], None, HTTPStatus.BAD_REQUEST),
    ('Unauthorized', [COLIN_ROLE], '1234', HTTPStatus.UNAUTHORIZED)
]
# testdata pattern is ({desc}, {roles}, {account_id}, {status}, {has_submitting})
TEST_UPDATE_DATA = [
    ('Invalid does not exist', [MHR_ROLE], 'JUNK-TEST', HTTPStatus.NOT_FOUND, True),
    ('Invalid validation error', [MHR_ROLE], '2523', HTTPStatus.BAD_REQUEST, False),
    ('Valid', [MHR_ROLE], '2523', HTTPStatus.OK, True)
]


@pytest.mark.parametrize('desc,roles,account_id,status,size', TEST_ACCOUNT_DATA)
def test_get_account_manufacturer(session, client, jwt, desc, roles, account_id, status, size):
    """Assert that the GET account manufacturer info endpoint behaves as expected."""
    # setup
    headers = create_header_account(jwt, roles, 'test-user', account_id) if account_id else create_header(jwt, roles)

    # test
    rv = client.get('/api/v1/manufacturers', headers=headers)

    # check
    assert rv.status_code == status
    if status == HTTPStatus.OK:
        json_data = rv.json
        assert json_data
        assert json_data.get('submittingParty')
        assert json_data['submittingParty'].get('businessName')
        assert json_data['submittingParty'].get('address')
        assert json_data['submittingParty'].get('phoneNumber')
        assert json_data.get('ownerGroups')
        assert json_data['ownerGroups'][0].get('groupId') == 1
        assert json_data['ownerGroups'][0].get('type') == 'SOLE'
        assert json_data['ownerGroups'][0].get('owners')
        owner = json_data['ownerGroups'][0]['owners'][0]
        assert owner.get('organizationName')
        assert owner.get('address')
        assert json_data.get('location')
        assert json_data['location'].get('locationType')
        assert json_data['location'].get('dealerName')
        assert json_data['location'].get('address')
        assert json_data.get('description')
        assert json_data['description'].get('manufacturer')


@pytest.mark.parametrize('desc,roles,account,status,has_submitting', TEST_CREATE_DATA)
def test_create(session, client, jwt, desc, roles, account, status, has_submitting):
    """Assert that the POST manufacturer information endpoint works as expected."""
    # setup
    headers = None
    json_data = copy.deepcopy(MANUFACTURER_VALID)
    if not has_submitting:
        del json_data['submittingParty']
    if account:
        headers = create_header_account(jwt, roles, 'UT-TEST', account)
    else:
        headers = create_header(jwt, roles)
    # test
    response = client.post('/api/v1/manufacturers',
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    current_app.logger.debug(response.json)
    assert response.status_code == status
    if response.status_code == HTTPStatus.OK:
        manufacturer: MhrManufacturer = MhrManufacturer.find_by_account_id(account)
        assert manufacturer


@pytest.mark.parametrize('desc,roles,account_id,status', TEST_DELETE_DATA)
def test_delete_account_manufacturer(session, client, jwt, desc, roles, account_id, status):
    """Assert that the DELETE account manufacturer info endpoint behaves as expected."""
    # setup
    headers = create_header_account(jwt, roles, 'test-user', account_id) if account_id else create_header(jwt, roles)
    # test
    rv = client.delete('/api/v1/manufacturers', headers=headers)
    # check
    assert rv.status_code == status


@pytest.mark.parametrize('desc,roles,account,status,has_submitting', TEST_UPDATE_DATA)
def test_update_account_manufacturer(session, client, jwt, desc, roles, account, status, has_submitting):
    """Assert that the PUT manufacturer info endpoint works as expected."""
    # setup
    headers = None
    json_data = copy.deepcopy(MANUFACTURER_UPDATE)
    if not has_submitting:
        del json_data['submittingParty']
    if account:
        headers = create_header_account(jwt, roles, 'UT-TEST', account)
    else:
        headers = create_header(jwt, roles)
    # test
    response = client.put('/api/v1/manufacturers',
                          json=json_data,
                          headers=headers,
                          content_type='application/json')

    # check
    # current_app.logger.debug(response.json)
    assert response.status_code == status
    if response.status_code == HTTPStatus.OK:
        response_data = response.json
        assert response_data
        assert json_data.get('dbaName') == response_data.get('dbaName')
        assert json_data.get('authorizationName') == response_data.get('authorizationName')
        assert json_data.get('termsAccepted') == response_data.get('termsAccepted')
        owner1 = json_data['ownerGroups'][0]['owners'][0]
        owner2 = response_data['ownerGroups'][0]['owners'][0]
        assert owner1.get('organizationName') == owner2.get('organizationName')
        name: str = owner1.get('organizationName') + ' / ' + json_data.get('dbaName')
        assert owner1.get('address') == owner2.get('address')
        assert name == response_data['description']['manufacturer']
        assert name == response_data['location']['dealerName']
        assert json_data['location']['address'] == response_data['location']['address']
