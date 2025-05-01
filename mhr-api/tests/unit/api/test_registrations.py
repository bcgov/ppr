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

from mhr_api.models import MhrRegistration, registration_utils as reg_utils, utils as model_utils, MhrRegistrationReport
from mhr_api.models.type_tables import (
    MhrDocumentTypes,
    MhrOwnerStatusTypes,
    MhrRegistrationTypes,
    MhrRegistrationStatusTypes,
    MhrStatusTypes
)
from mhr_api.resources.registration_utils import (
    notify_man_reg_config,
    email_batch_man_report_data,
    email_batch_location_data,
    notify_location_config,
    get_pay_details,
    get_pay_details_doc,
    setup_cc_draft
)
from mhr_api.services.authz import COLIN_ROLE, MHR_ROLE, STAFF_ROLE, BCOL_HELP_ROLE, ASSETS_HELP
from mhr_api.services.authz import REGISTER_MH, TRANSFER_SALE_BENEFICIARY, MANUFACTURER_GROUP

from tests.unit.services.utils import create_header, create_header_account


MOCK_AUTH_URL = 'https://test.api.connect.gov.bc.ca/mockTarget/auth/api/v1/'
MOCK_PAY_URL = 'https://test.api.connect.gov.bc.ca/mockTarget/pay/api/v1/'
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
      'city': 'VICTORIA', 
      'country': 'CA', 
      'postalCode': 'V8R 7A3', 
      'region': 'BC', 
      'street': '1722 GOVERNMENT ST.'
    }, 
    'businessName': 'REAL ENGINEERED HOMES', 
    'phoneNumber': '2507701066'
  }
}
CC_PAYREF = {"invoiceId": "88888888", "receipt": "receipt", "ccPayment": True, "ccURL": ""}
MANUFACTURER_ROLES = [MHR_ROLE, TRANSFER_SALE_BENEFICIARY, REGISTER_MH]
# testdata pattern is ({desc}, {roles}, {status}, {has_account}, {results_size})
TEST_GET_ACCOUNT_DATA = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, False, 0),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 0),
    ('Valid request', [MHR_ROLE], HTTPStatus.OK, True, 1),
    ('Invalid request staff no account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, 0)
]
# testdata pattern is ({description}, {has_submitting}, {roles}, {status}, {has_account}, {mhr_num})
TEST_CREATE_DATA = [
    ('Invalid schema validation no submitting', False, [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, True, None),
    ('Missing account', True, [MHR_ROLE], HTTPStatus.BAD_REQUEST, False, None),
    ('Staff missing account', True, [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, None),
    ('Invalid BCOL helpdesk role', True, [MHR_ROLE, BCOL_HELP_ROLE], HTTPStatus.UNAUTHORIZED, True, None),
    ('Invalid role', True, [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, None),
    ('Invalid non-staff role', True, [MHR_ROLE], HTTPStatus.UNAUTHORIZED, True, None),
    ('Valid staff', True, [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, True, None),
    ('Valid staff mhr', True, [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, True, '000899'),
    ('Invalid staff mhr', False, [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, True, '000900')
]
# testdata pattern is ({description}, {year_offset}, {status}, {account_id})
TEST_CREATE_MANUFACTURER_DATA = [
    ('Valid', 0, HTTPStatus.CREATED, 'PS12345'),
    ('Invalid account id', 0, HTTPStatus.BAD_REQUEST, 'JUNK'),
    ('Invalid MH year', -2, HTTPStatus.BAD_REQUEST, 'PS12345')
]
# testdata pattern is ({description}, {roles}, {status}, {account}, {mhr_num}, {current})
TEST_GET_REGISTRATION = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, None, '000900', False),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345', '000900', False),
    ('Valid Request', [MHR_ROLE], HTTPStatus.OK, 'PS12345', '000900', False),
    ('Valid Request exempt', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, STAFF_ROLE, '000912', True),
    ('Valid Request reg staff', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, STAFF_ROLE, '000900', True),
    ('Valid Request bcol helpdesk', [MHR_ROLE, BCOL_HELP_ROLE], HTTPStatus.OK, ASSETS_HELP, '000900', False),
    ('Valid Request other account', [MHR_ROLE], HTTPStatus.OK, 'PS12345', '000900', False),
    ('Invalid MHR Number', [MHR_ROLE], HTTPStatus.NOT_FOUND, 'PS12345', 'TESTXXXX', False),
    ('Invalid request Staff no account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, None, '000900', False)
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
    ('Filter mhr number', 'PS12345', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.MHR_NUMBER_PARAM, '000930'),
    ('Filter reg type desc', 'PS12345', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.REG_TYPE_PARAM,
     'MANUFACTURED HOME REGISTRATION'),
    ('Filter reg type doc type', 'PS12345', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.REG_TYPE_PARAM, 'REG_101'),
    ('Filter reg status', 'PS12345', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.STATUS_PARAM, 'EXEMPT'),
    ('Filter client ref', 'PS12345', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.CLIENT_REF_PARAM, 'UT-0029'),
    ('Filter user name', 'PS12345', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.USER_NAME_PARAM, 'TEST USER'),
    ('Filter submitting bus name', 'PS12345', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.SUBMITTING_NAME_PARAM,
     'real engineered'),
    ('Filter submitting last name', 'PS12345', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.SUBMITTING_NAME_PARAM,
     'iverson'),
    ('Filter submitting first name', 'PS12345', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, reg_utils.SUBMITTING_NAME_PARAM,
     'donna')
]
# testdata pattern is ({desc}, {roles}, {status}, {collapse}, {filter_start}, {filter_end})
TEST_GET_ACCOUNT_DATA_FILTER_DATE = [
    ('Filter reg date range', 'PS12345', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, False,
     '2023-09-01T00:00:01-07:00', '2035-09-01T00:00:01-07:00'),
    ('Filter reg date range', 'PS12345', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, True,
     '2023-09-01T00:00:01-07:00', '2035-09-01T00:00:01-07:00')
]
# testdata pattern is ({description}, {start_ts}, {end_ts}, {status}, {has_key}, {download_link})
TEST_BATCH_NOC_LOCATION_DATA = [
    ('Unauthorized', None, None, HTTPStatus.UNAUTHORIZED, False, False),
    ('Valid no data', '2023-02-25T07:01:00+00:00', '2023-02-26T07:01:00+00:00', HTTPStatus.NO_CONTENT, True, False),
    ('Valid no data download', '2023-02-25T07:01:00+00:00', '2023-02-26T07:01:00+00:00', HTTPStatus.NO_CONTENT, True,
     True),
    ('Valid may have data download', '2023-12-01T08:01:00+00:00', '2023-12-02T08:01:00+00:00', HTTPStatus.OK,
     True, True),
    ('Valid default interval may have data', None, None, HTTPStatus.OK, True, False)
]
# testdata pattern is ({description}, {roles}, {status}, {account}, {start_ts}, {end_ts})
TEST_GET_BATCH_REGISTRATIONS = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, None, None, None),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345', None, None),
    ('Valid Request', [MHR_ROLE], HTTPStatus.OK, 'PS12345', '2023-12-15T08:01:00%2B00:00', '2023-12-22T08:01:00%2B00:00'),
    ('Valid Default Request', [MHR_ROLE], HTTPStatus.OK, 'PS12345', None, None)
]
# testdata pattern is ({reg_type}, {trans_id})
TEST_GET_PAY_DETAIL = [
    (MhrRegistrationTypes.MHREG, None),
    (MhrRegistrationTypes.TRANS, None),
    (MhrRegistrationTypes.TRAND, None),
    (MhrRegistrationTypes.TRANS_AFFIDAVIT, None),
    (MhrRegistrationTypes.TRANS_ADMIN, None),
    (MhrRegistrationTypes.PERMIT, None),
    (MhrRegistrationTypes.EXEMPTION_NON_RES, None),
    (MhrRegistrationTypes.EXEMPTION_RES, None)
]
# testdata pattern is ({doc_type}, {trans_id})
TEST_GET_PAY_DETAIL_NOTE = [
    (MhrDocumentTypes.CAU, None),
    (MhrDocumentTypes.CAUC, None),
    (MhrDocumentTypes.CAUE, None),
    (MhrDocumentTypes.NCAN, None),
    (MhrDocumentTypes.TAXN, None),
    (MhrDocumentTypes.REST, None),
    (MhrDocumentTypes.NPUB, None),
    (MhrDocumentTypes.NCON, None)
]
# testdata pattern is ({description}, {roles}, {status}, {account}, {mhr_num})
TEST_GET_HISTORY = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, None, '000900'),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345', '000900'),
    ('Invalid MHR not staff', [MHR_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345', '000912'),
    ('Invalid role bcol helpdesk', [MHR_ROLE, BCOL_HELP_ROLE], HTTPStatus.UNAUTHORIZED, ASSETS_HELP, '000900'),
    ('Invalid MHR Number', [MHR_ROLE], HTTPStatus.NOT_FOUND, 'PS12345', 'TESTXXXX'),
    ('Invalid request Staff no account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, None, '000900'),
    ('Valid Request reg staff', [MHR_ROLE, STAFF_ROLE], HTTPStatus.OK, 'PS12345', '000912')
]
# testdata pattern is ({pay_ref}, {account_id}, {username}, {usergroup})
TEST_SETUP_CC_PAYMENT= [
    (CC_PAYREF, "1234", "username", "ppr_staff")
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


@pytest.mark.parametrize('desc,has_submitting,roles,status,has_account,mhr_num', TEST_CREATE_DATA)
def test_create(session, client, jwt, desc, has_submitting, roles, status, has_account, mhr_num):
    """Assert that a post MH registration works as expected."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    json_data = copy.deepcopy(REGISTRATION)
    del json_data['mhrNumber']
    json_data['description']['baseInformation']['year'] = model_utils.now_ts().year
    json_data['location'] = copy.deepcopy(LOCATION)
    if not has_submitting:
        del json_data['submittingParty']
    if mhr_num:
        json_data['mhrNumber'] = mhr_num
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
        registration: MhrRegistration = MhrRegistration.find_by_mhr_number(response_json.get('mhrNumber'),
                                                                           'PS12345')
        assert registration
        reg_report: MhrRegistrationReport = MhrRegistrationReport.find_by_registration_id(registration.id)
        assert reg_report
        assert reg_report.batch_registration_data


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


@pytest.mark.parametrize('desc,roles,status,account_id,mhr_num,current', TEST_GET_REGISTRATION)
def test_get_registration(session, client, jwt, desc, roles, status, account_id, mhr_num, current):
    """Assert that a get account registration by MHR number works as expected."""
    # setup
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    if account_id:
        headers = create_header_account(jwt, roles, 'test-user', account_id)
    else:
        headers = create_header(jwt, roles)
    req_path = '/api/v1/registrations/' + mhr_num
    if current:
        req_path += '?current=true'
    # test
    response = client.get(req_path,
                          headers=headers)
    # check
    if status == HTTPStatus.NOT_FOUND:
        assert response.status_code in (status, HTTPStatus.UNAUTHORIZED)
    else:
        assert response.status_code == status
    if status == HTTPStatus.OK:
        response_json = response.json
        assert response_json
        assert response_json.get('status')
        if response_json.get('status') == MhrRegistrationStatusTypes.EXEMPT:
            assert response_json.get('exemptDateTime')


@pytest.mark.parametrize('desc,roles,status,account_id,mhr_num', TEST_GET_HISTORY)
def test_get_history(session, client, jwt, desc, roles, status, account_id, mhr_num):
    """Assert that a get home history by MHR number works as expected."""
    # setup
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    if account_id:
        headers = create_header_account(jwt, roles, 'test-user', account_id)
    else:
        headers = create_header(jwt, roles)
    req_path = '/api/v1/registrations/history/' + mhr_num
    # test
    response = client.get(req_path, headers=headers)
    # check
    if status == HTTPStatus.NOT_FOUND:
        assert response.status_code in (status, HTTPStatus.UNAUTHORIZED)
    else:
        assert response.status_code == status
    if status == HTTPStatus.OK:
        history_json = response.json
        assert history_json
        assert history_json.get('statusType')
        assert history_json.get('mhrNumber') == mhr_num
        assert history_json.get('descriptions')
        assert history_json.get('locations')
        assert history_json.get('owners')
        for description in history_json.get('descriptions'):
            assert description.get('createDateTime')
            assert description.get('registrationDescription')
            assert description.get('status')
            if description.get('status') != MhrStatusTypes.ACTIVE:
                assert 'endDateTime' in description
                assert 'endRegistrationDescription' in description
            else:
                assert 'endDateTime' not in description
                assert 'endRegistrationDescription' not in description
        for location in history_json.get('locations'):
            assert location.get('createDateTime')
            assert location.get('registrationDescription')
            assert location.get('status')
            if location.get('status') != MhrStatusTypes.ACTIVE:
                assert 'endDateTime' in location
                assert 'endRegistrationDescription' in location
            else:
                assert 'endDateTime' not in location
                assert 'endRegistrationDescription' not in location
        for owner in history_json.get('owners'):
            assert owner.get('createDateTime')
            assert owner.get('registrationDescription')
            assert owner.get('status')
            if owner.get('status') not in (MhrOwnerStatusTypes.ACTIVE, MhrOwnerStatusTypes.EXEMPT):
                assert 'endDateTime' in owner
                assert 'endRegistrationDescription' in owner
            else:
                assert 'endDateTime' not in owner
                assert 'endRegistrationDescription' not in owner
            assert owner.get('ownerId')
            assert owner.get('groupOwnerCount')



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
    filter_now_end = model_utils.format_ts(model_utils.now_ts())
    params = f'?{start_ts}={filter_start}&{end_ts}={filter_now_end}'
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
    if not apikey:
        return
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
        params += '&downloadLink=true&notify=false'
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


@pytest.mark.parametrize('desc,start_ts,end_ts,status,has_key,download_link',TEST_BATCH_NOC_LOCATION_DATA)
def test_post_batch_location_report(session, client, jwt, desc, start_ts, end_ts, status, has_key, download_link):
    """Assert that requesting a batch noc location registration report works as expected."""
    # setup
    apikey = current_app.config.get('SUBSCRIPTION_API_KEY')
    if not apikey:
        return
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
        params += '&downloadLink=true&notify=false'
    # test
    rv = client.post('/api/v1/registrations/batch/noclocation' + params)
    # check
    if desc in ('Valid default interval may have data', 'Valid may have data download'):
        assert rv.status_code == status or rv.status_code == HTTPStatus.NO_CONTENT
    else:
        assert rv.status_code == status
    if download_link and rv.status_code == HTTPStatus.OK:
        assert rv.json
        assert rv.json.get('reportDownloadUrl')


@pytest.mark.parametrize('desc,roles,status,account_id,start_ts,end_ts', TEST_GET_BATCH_REGISTRATIONS)
def test_get_batch_registrations(session, client, jwt, desc, roles, status, account_id, start_ts, end_ts):
    """Assert that a get account registration by MHR number works as expected."""
    # setup
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    if account_id:
        headers = create_header_account(jwt, roles, 'test-user', account_id)
    else:
        headers = create_header(jwt, roles)
    params: str = ''
    if start_ts and end_ts:
        start: str = reg_utils.START_TS_PARAM
        end: str = reg_utils.END_TS_PARAM
        params += f'?{start}={start_ts}&{end}={end_ts}'

    # test
    response = client.get('/api/v1/registrations/batch' + params,
                          headers=headers)
    # check
    if status == HTTPStatus.OK:
        assert response.status_code in (status, HTTPStatus.NO_CONTENT)
    else:
        assert response.status_code == status


def test_batch_manufacturer_notify_config(session, client, jwt):
    """Assert that building the batch manufacturer registration report notify configuration works as expected."""
    if not current_app.config.get("NOTIFY_MAN_REG_CONFIG"):
        return
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
    if not current_app.config.get("NOTIFY_MAN_REG_CONFIG"):
        return
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


@pytest.mark.parametrize('reg_type, trans_id',TEST_GET_PAY_DETAIL)
def test_get_pay_details(session, client, jwt, reg_type, trans_id):
    """Assert that setting up the pay api invoice information by reg type works as expected."""
    details: dict = get_pay_details(reg_type, trans_id)
    assert details.get('label')
    assert details.get('value')


@pytest.mark.parametrize('doc_type, trans_id',TEST_GET_PAY_DETAIL_NOTE)
def test_get_pay_details_doc(session, client, jwt, doc_type, trans_id):
    """Assert that setting up the pay api invoice information by doc type works as expected."""
    details: dict = get_pay_details_doc(doc_type, trans_id)
    assert details.get('label')
    assert details.get('value')


def test_batch_location_notify_config(session, client, jwt):
    """Assert that building the batch noc location registration report notify configuration works as expected."""
    if not current_app.config.get("NOTIFY_LOCATION_CONFIG"):
        return
    config = notify_location_config()
    assert config
    assert config.get('url')
    assert config.get('recipients')
    assert config.get('subject')
    assert config.get('subjectNone')
    assert config.get('body')
    assert config.get('bodyNone')
    assert config.get('filename')


def test_batch_location_notify_email_data(session, client, jwt):
    """Assert that building the batch noc location registration report email data works as expected."""
    if not current_app.config.get("NOTIFY_LOCATION_CONFIG"):
        return
    config = notify_location_config()
    email_data = email_batch_location_data(config, None)
    assert email_data
    assert email_data.get('recipients')
    assert email_data.get('content')
    assert email_data['content'].get('subject')
    assert email_data['content'].get('body')
    current_app.logger.debug(email_data)
    email_data = email_batch_location_data(config, 'junk-link')
    current_app.logger.debug(email_data)

# testdata pattern is ({pay_ref}, {account_id}, {username}, {usergroup})
@pytest.mark.parametrize('pay_ref, account_id, username, usergroup',TEST_SETUP_CC_PAYMENT)
def test_cc_payment_setup(session, client, jwt, pay_ref, account_id, username, usergroup):
    """Assert that setting up the pay api invoice information by doc type works as expected."""
    reg_json = {}
    reg_json = setup_cc_draft(reg_json, pay_ref, account_id, username, usergroup)
    assert reg_json.get("payment")
    assert reg_json["payment"] == pay_ref
    assert reg_json.get("accountId") == account_id
    assert reg_json.get("username") == username
    assert reg_json.get("usergroup") == usergroup
