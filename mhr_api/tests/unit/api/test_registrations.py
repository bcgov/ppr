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

from mhr_api.models import MhrRegistration, registration_utils as reg_utils, utils as model_utils
from mhr_api.resources.registration_utils import notify_man_reg_config, email_batch_man_report_data
from mhr_api.services.authz import COLIN_ROLE, MHR_ROLE, STAFF_ROLE, BCOL_HELP, ASSETS_HELP
from mhr_api.services.authz import REGISTER_MH, TRANSFER_SALE_BENEFICIARY, MANUFACTURER_GROUP

from tests.unit.services.utils import create_header, create_header_account


MOCK_AUTH_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
MOCK_PAY_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/pay/api/v1/'
LOCATION = {
    'locationType': 'MH_PARK',
    'address': {
      'street': '1117 GLENDALE AVENUE',
      'city': 'SALMO',
      'region': 'BC',
      'country': 'CA',
      'postalCode': ''
    },
    'leaveProvince': False,
    'parkName': 'GLENDALE TRAILER PARK',
    'pad': '2',
    'additionalDescription': 'TEST PARK'
}
MANUFACTURER_VALID = {
  'clientReferenceId': 'EX-MH001234',
  'attentionReference': 'GWB14768.100',
  'description': {
    'manufacturer': 'REAL ENGINEERED HOMES INC',
    'baseInformation': {
      'year': 2023,
      'make': 'WATSON IND. (ALTA)',
      'model': 'DUCHESS'
    },
    'sectionCount': 1,
    'sections': [
      {
        'serialNumber': '52D70556',
        'lengthFeet': 52,
        'lengthInches': 0,
        'widthFeet': 12,
        'widthInches': 0
      }
    ],
    'csaNumber': '786356',
    'csaStandard': 'Z240'
  }, 
  'location': {
    'address': {
      'city': 'PENTICTON', 
      'country': 'CA', 
      'postalCode': 'V2A 7A1', 
      'region': 'BC', 
      'street': '1704 GOVERNMENT ST.'
    }, 
    'dealerName': 'REAL ENGINEERED HOMES INC', 
    'leaveProvince': False, 
    'locationType': 'MANUFACTURER'
  }, 
  'ownerGroups': [
    {
      'groupId': 1, 
      'owners': [
        {
          'address': {
            'city': 'PENTICTON', 
            'country': 'CA', 
            'postalCode': 'V2A 7A1', 
            'region': 'BC', 
            'street': '1704 GOVERNMENT ST.'
          }, 
          'organizationName': 'REAL ENGINEERED HOMES INC', 
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
MANUFACTURER_ROLES = [MHR_ROLE, TRANSFER_SALE_BENEFICIARY, REGISTER_MH]
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
# testdata pattern is ({description}, {year_offset}, {status}, {account_id})
TEST_CREATE_MANUFACTURER_DATA = [
    ('Valid', 0, HTTPStatus.CREATED, '2523'),
    ('Invalid account id', 0, HTTPStatus.BAD_REQUEST, 'JUNK'),
    ('Invalid MH year', -2, HTTPStatus.BAD_REQUEST, '2523')
]
# testdata pattern is ({description}, {roles}, {status}, {account}, {mhr_num})
TEST_GET_REGISTRATION = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, None, '150062'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, '2523', '150062'),
    ('Valid Request', [MHR_ROLE], HTTPStatus.OK, '2523', '150062'),
    ('Valid Request reg staff', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, STAFF_ROLE, '150062'),
    ('Valid Request bcol helpdesk', [MHR_ROLE, BCOL_HELP], HTTPStatus.OK, ASSETS_HELP, '150062'),
    ('Valid Request other account', [MHR_ROLE], HTTPStatus.OK, 'PS12345', '150062'),
    ('Invalid MHR Number', [MHR_ROLE], HTTPStatus.NOT_FOUND, '2523', 'TESTXXXX'),
    ('Invalid request Staff no account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, None, '150062')
]
# testdata pattern is ({description}, {start_ts}, {end_ts}, {status}, {has_key}, {download_link})
TEST_BATCH_MANUFACTURER_MHREG_DATA = [
    ('Unauthorized', None, None, HTTPStatus.UNAUTHORIZED, False, False),
    ('Valid no data', '2023-02-25T07:01:00+00:00', '2023-02-26T07:01:00+00:00', HTTPStatus.NO_CONTENT, True, False),
    ('Valid no data download', '2023-02-25T07:01:00+00:00', '2023-02-26T07:01:00+00:00', HTTPStatus.NO_CONTENT, True,
     True),
    ('Valid data', '2023-05-25T07:01:00+00:00', '2023-05-26T07:01:00+00:00', HTTPStatus.OK, True, False),
    ('Valid data download', '2023-05-25T07:01:00+00:00', '2023-05-26T07:01:00+00:00', HTTPStatus.OK, True, True),
    ('Valid default interval may have data', None, None, HTTPStatus.OK, True, False)
]
# testdata pattern is ({desc}, {roles}, {status}, {sort_criteria}, {sort_direction})
TEST_GET_ACCOUNT_DATA_SORT2 = [
    ('Sort mhr number', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.MHR_NUMBER_PARAM, None)
]
TEST_GET_ACCOUNT_DATA_SORT = [
    ('Sort mhr number', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.MHR_NUMBER_PARAM, None),
    ('Sort reg type asc', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.REG_TYPE_PARAM, reg_utils.SORT_ASCENDING),
    ('Sort reg status desc', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.STATUS_PARAM, reg_utils.SORT_DESCENDING),
    ('Sort reg ts asc', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.REG_TS_PARAM, reg_utils.SORT_ASCENDING),
    ('Sort client ref', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.CLIENT_REF_PARAM, None),
    ('Sort user name', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.USER_NAME_PARAM, None),
    ('Sort submitting name', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.SUBMITTING_NAME_PARAM, None),
    ('Sort owner name', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.OWNER_NAME_PARAM, None)
]
# testdata pattern is ({desc}, {roles}, {status}, {filter_name}, {filter_value})
TEST_GET_ACCOUNT_DATA_FILTER = [
    ('Filter mhr number', '2523', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.MHR_NUMBER_PARAM, '098487'),
    ('Filter reg type', '2523', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.REG_TYPE_PARAM, 'REGISTER NEW UNIT'),
    ('Filter reg status', '2523', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.STATUS_PARAM, 'ACTIVE'),
    ('Filter client ref', '2523', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.CLIENT_REF_PARAM, 'a000873'),
    ('Filter user name', '2523', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.USER_NAME_PARAM, 'BCREG2'),
    ('Filter submitting bus name', '2523', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.SUBMITTING_NAME_PARAM,
     'champion'),
    ('Filter submitting last name', '2523', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.SUBMITTING_NAME_PARAM,
     'iverson'),
    ('Filter submitting first name', '2523', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.SUBMITTING_NAME_PARAM,
     'donna')
]
# testdata pattern is ({desc}, {roles}, {status}, {collapse}, {filter_start}, {filter_end})
TEST_GET_ACCOUNT_DATA_FILTER_DATE = [
    ('Filter reg date range', '2523', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, False,
     '2021-10-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53'),
    ('Filter reg date range', '2523', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, True,
     '2021-10-14T09:53:57-07:53', '2021-10-17T09:53:57-07:53')
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
            if registration['registrationDescription'] == 'REGISTER NEW UNIT':
                assert 'lienRegistrationType' in registration


@pytest.mark.parametrize('desc,has_submitting,roles,status,has_account', TEST_CREATE_DATA)
def test_create(session, client, jwt, desc, has_submitting, roles, status, has_account):
    """Assert that a post MH registration works as expected."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    json_data = copy.deepcopy(REGISTRATION)
    json_data['location'] = copy.deepcopy(LOCATION)
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
        response_json = response.json
        assert response_json.get('mhrNumber')
        if model_utils.is_legacy():
            assert not str(response_json.get('mhrNumber')).startswith('15')
        registration: MhrRegistration = MhrRegistration.find_by_mhr_number(response_json.get('mhrNumber'),
                                                                           'PS12345')
        assert registration


@pytest.mark.parametrize('desc,year_offset,status,account_id', TEST_CREATE_MANUFACTURER_DATA)
def test_create_man(session, client, jwt, desc, year_offset, status, account_id):
    """Assert that a post MH registration for a manufacturer works as expected."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    json_data = copy.deepcopy(MANUFACTURER_VALID)
    now = model_utils.now_ts()
    json_data['description']['baseInformation']['year'] = now.year + year_offset
    headers = create_header_account(jwt, MANUFACTURER_ROLES, 'test-user', account_id)

    # test
    response = client.post('/api/v1/registrations',
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    assert response.status_code == status
    if response.status_code == HTTPStatus.CREATED:
        registration: MhrRegistration = MhrRegistration.find_by_mhr_number(response.json['mhrNumber'],
                                                                           account_id)
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


@pytest.mark.parametrize('desc,roles,status,sort_criteria,sort_direction', TEST_GET_ACCOUNT_DATA_SORT)
def test_get_account_registrations_sort(session, client, jwt, desc, roles, status, sort_criteria, sort_direction):
    """Assert that a get account registrations summary list endpoint with sorting works as expected."""
    headers = None
    # setup
    headers = create_header_account(jwt, roles)
    params = f'?sortCriteriaName={sort_criteria}'
    if sort_direction:
        params += f'&sortDirection={sort_direction}'
    # test
    current_app.logger.debug('params=' + params)
    rv = client.get('/api/v1/registrations' + params,
                    headers=headers)
    # check
    assert rv.status_code == status
    assert rv.json
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


@pytest.mark.parametrize('desc,account_id,roles,status,filter_name,filter_value', TEST_GET_ACCOUNT_DATA_FILTER)
def test_get_account_registrations_filter(session, client, jwt, desc, account_id, roles, status, filter_name,
                                          filter_value):
    """Assert that a get account registrations summary list endpoint with filtering works as expected."""
    # setup
    headers = create_header_account(jwt, roles, 'test-user', account_id)
    params = f'?{filter_name}={filter_value}'
    # test
    rv = client.get('/api/v1/registrations' + params,
                    headers=headers)
    # check
    assert rv.status_code == status
    assert rv.json
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


@pytest.mark.parametrize('desc,account_id,roles,status,collapse,filter_start,filter_end',
                         TEST_GET_ACCOUNT_DATA_FILTER_DATE)
def test_get_account_registrations_filter_date(session, client, jwt, desc, account_id, roles, status, collapse,
                                               filter_start, filter_end):
    """Assert that a get account registrations summary list endpoint with filtering works as expected."""
    # setup
    headers = create_header_account(jwt, roles, 'test-user', account_id)
    start_ts: str = reg_utils.START_TS_PARAM
    end_ts: str = reg_utils.END_TS_PARAM
    params = f'?{start_ts}={filter_start}&{end_ts}={filter_end}'
    if collapse:
        params += '&collapse=true'
    # test
    rv = client.get('/api/v1/registrations' + params,
                    headers=headers)
    # check
    assert rv.status_code == status
    assert rv.json
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


@pytest.mark.parametrize('desc,start_ts,end_ts,status,has_key,download_link',TEST_BATCH_MANUFACTURER_MHREG_DATA)
def test_get_batch_mhreg_manufacturer_report(session, client, jwt, desc, start_ts, end_ts, status, has_key, download_link):
    """Assert that requesting a batch manufacturer registration report works as expected."""
    # setup
    apikey = current_app.config.get('SUBSCRIPTION_API_KEY')
    params: str = ''
    if has_key:
        params += '?x-apikey=' + apikey
    if start_ts and end_ts:
        start: str = reg_utils.START_TS_PARAM
        end: str = reg_utils.END_TS_PARAM
        if has_key:
            params += f'&{start}={start_ts}&{end}={end_ts}'
        else:
            params += f'?{start}={start_ts}&{end}={end_ts}'
    if download_link:
        params += '&downloadLink=true'
    # test
    rv = client.get('/api/v1/registrations/batch/manufacturer' + params)
    # check
    if desc == 'Valid default interval may have data':
        assert rv.status_code == status or rv.status_code == HTTPStatus.NO_CONTENT
    else:
        assert rv.status_code == status
    if download_link and rv.status_code == HTTPStatus.OK:
        assert rv.json
        assert rv.json.get('reportDownloadUrl')


def test_batch_manufacturer_notify_config(session, client, jwt):
    """Assert that building the batch manufacturer registration report notify configuration works as expected."""
    config = notify_man_reg_config()
    assert config
    assert config.get('url')
    assert config.get('recipients')
    assert config.get('subject')
    assert config.get('body')
    assert config.get('bodyNone')
    assert config.get('filename')


def test_batch_manufacturer_notify_email_data(session, client, jwt):
    """Assert that building the batch manufacturer registration report email data works as expected."""
    config = notify_man_reg_config()
    email_data = email_batch_man_report_data(config, None)
    assert email_data
    assert email_data.get('recipients')
    assert email_data.get('content')
    assert email_data['content'].get('subject')
    assert email_data['content'].get('body')
    current_app.logger.debug(email_data)
    email_data = email_batch_man_report_data(config, 'junk-link')
    current_app.logger.debug(email_data)

