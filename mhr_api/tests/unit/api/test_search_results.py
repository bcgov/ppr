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

"""Tests to verify the searches endpoint.

Test-Suite to ensure that the /searches endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app

from mhr_api.models import SearchResult, SearchRequest
from mhr_api.resources.v1.search_results import get_payment_details
from mhr_api.services.authz import COLIN_ROLE, MHR_ROLE, STAFF_ROLE, BCOL_HELP, GOV_ACCOUNT_ROLE

from tests.unit.services.utils import create_header, create_header_account, create_header_account_report


MHR_NUMBER_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'value': '022911'
    },
    'clientReferenceId': 'T-SQ-MH-1'
}
ORG_NAME_JSON = {
    'type': 'ORGANIZATION_NAME',
    'criteria': {
        'value': 'GUTHRIE HOLDINGS LTD.'
    },
    'clientReferenceId': 'T-SQ-MO-1'
}
OWNER_NAME_JSON = {
    'type': 'OWNER_NAME',
    'criteria': {
        'ownerName': {
            'first': 'David',
            'last': 'Hamm'
        }
    },
    'clientReferenceId': 'T-SQ-MI-1'
}
SERIAL_NUMBER_JSON = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'value': '4551'
    },
    'clientReferenceId': 'T-SQ-MS-1'
}

SELECTED_JSON_NONE = []
SELECTED_JSON = [
    {'baseInformation': {
        'make': 'GLENDALE', 'model': '', 'year': 1968
    },
    'createDateTime': '1995-11-14T00:00:01+00:00',
    'homeLocation': 'FORT NELSON',
    'mhrNumber': '022911',
    'ownerName': {
        'first': 'PRITNAM',
        'last': 'SANDHU'
    },
    'serialNumber': '2427',
    'status': 'EXEMPT'}
]
SELECTED_JSON_INVALID = [
    {'baseInformation': {
        'make': 'GLENDALE', 'model': '', 'year': 1968
    },
    'createDateTime': '1995-11-14T00:00:01+00:00',
    'homeLocation': 'FORT NELSON',
    'ownerName': {
        'first': 'PRITNAM',
        'last': 'SANDHU'
    },
    'serialNumber': '2427',
    'status': 'EXEMPT'}
]
SELECTED_JSON_COMBO = [
    {'mhrNumber': '022911', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
     'homeLocation': 'FORT NELSON', 'includeLienInfo': True, 'serialNumber': '2427',
     'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
     'ownerName': {'first': 'PRITNAM', 'last': 'SANDHU'}}
]


MOCK_AUTH_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
MOCK_PAY_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/pay/api/v1/'
TEST_SEARCH_REPORT_FILE = 'tests/unit/api/test-get-search-report.pdf'

# testdata pattern is ({desc}, {json_data}, {search_id}, {roles}, {account_id}, {status})
TEST_SELECTED_DATA = [
    ('Valid no selection', SELECTED_JSON_NONE, None, [MHR_ROLE], '1234', HTTPStatus.OK),
    ('Valid selection', SELECTED_JSON, None, [MHR_ROLE], '1234', HTTPStatus.OK),
    ('Invalid missing MHR number', SELECTED_JSON_INVALID, 200000004, [MHR_ROLE], '1234', HTTPStatus.BAD_REQUEST),
    ('Non-staff no account', SELECTED_JSON, 200000004, [MHR_ROLE], None, HTTPStatus.BAD_REQUEST),
    ('Staff no account', SELECTED_JSON, 200000004, [MHR_ROLE, STAFF_ROLE], None, HTTPStatus.BAD_REQUEST),
    ('Invalid search id', SELECTED_JSON, 300000004, [MHR_ROLE], '1234', HTTPStatus.NOT_FOUND),
    ('Unauthorized', SELECTED_JSON, 200000004, [COLIN_ROLE], '1234', HTTPStatus.UNAUTHORIZED)
]

# testdata pattern is ({desc}, {roles}, {status}, {has_account}, {search_id}, {is_report})
TEST_GET_DATA = [
    ('Missing account', [MHR_ROLE], HTTPStatus.BAD_REQUEST, False, 200000005, False),
    ('Invalid role', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, True, 200000005, False),
    ('Invalid request too old', [MHR_ROLE], HTTPStatus.BAD_REQUEST, True, 200000006, False),
    ('Valid request', [MHR_ROLE], HTTPStatus.OK, True, 200000005, False),
    ('Invalid no search selection', [MHR_ROLE], HTTPStatus.BAD_REQUEST, True, 200000001, False),
    ('Invalid search Id', [MHR_ROLE], HTTPStatus.NOT_FOUND, True, 300000006, False),
    ('Invalid request staff no account', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, False, 200000005, False)
]

# testdata pattern is ({description}, {type}, {search_data}, {select_data}, {label}, {value})
TEST_PAYMENT_DETAILS_DATA = [
    ('MHR number', 'MM', MHR_NUMBER_JSON, SELECTED_JSON, 'MHR Search', '022911'),
    ('Combo MHR number', 'MM', MHR_NUMBER_JSON, SELECTED_JSON_COMBO, 'Combined Search', '022911'),
    ('Owner Name', 'MI', OWNER_NAME_JSON, SELECTED_JSON, 'MHR Search', 'Hamm, David'),
    ('Org Name', 'MO', ORG_NAME_JSON, SELECTED_JSON, 'MHR Search', 'GUTHRIE HOLDINGS LTD.'),
    ('Serial number', 'MS', SERIAL_NUMBER_JSON, SELECTED_JSON, 'MHR Search', '4551')
]

# testdata pattern is ({role}, {routingSlip}, {bcolNumber}, {datNUmber}, {priority}, {status}, {certified})
TEST_STAFF_SEARCH_DATA = [
    (STAFF_ROLE, None, None, None, False, HTTPStatus.OK, False),
    (STAFF_ROLE, None, None, None, False, HTTPStatus.OK, True),
    (STAFF_ROLE, '12345', None, None, True, HTTPStatus.OK, False),
    (STAFF_ROLE, '12345', None, None, True, HTTPStatus.OK, True),
    (STAFF_ROLE, None, '654321', '111111', False, HTTPStatus.OK, False),
    (STAFF_ROLE, '12345', '654321', '111111', False, HTTPStatus.BAD_REQUEST, False),
    (BCOL_HELP, None, None, None, False, HTTPStatus.OK, False),
    (GOV_ACCOUNT_ROLE, None, None, None, False, HTTPStatus.OK, False)
]
# testdata pattern is ({description}, {JSON data}, {mhr_num}, {client_ref_id}, {match_count})
TEST_PPR_SEARCH_DATA = [
    ('Combo no match mhr number', SELECTED_JSON_COMBO, '022911', 'UT-0002', 0),
    ('Not combo no ppr registration info', SELECTED_JSON, '022911', None, 0),
    ('Double match mhr number', SELECTED_JSON_COMBO, '022000', None, 1)
]


@pytest.mark.parametrize('desc,json_data,search_id,roles,account_id,status', TEST_SELECTED_DATA)
def test_post_selected(session, client, jwt, desc, json_data, search_id, roles, account_id, status):
    """Assert that valid search criteria returns a 201 status."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = create_header_account(jwt, roles) if account_id else create_header(jwt, roles)

    if search_id and status != HTTPStatus.OK:
        rv = client.post('/api/v1/search-results/' + str(search_id),
                         json=json_data,
                         headers=headers,
                         content_type='application/json')
        # check
        assert rv.status_code == status
    else:
        rv = client.post('/api/v1/searches',
                        json=MHR_NUMBER_JSON,
                        headers=create_header_account(jwt, [MHR_ROLE]),
                        content_type='application/json')
        test_search_id = rv.json['searchId']
        rv = client.post('/api/v1/search-results/' + test_search_id,
                         json=json_data,
                         headers=headers,
                         content_type='application/json')
        # check
        assert rv.status_code == status


@pytest.mark.parametrize('role,routing_slip,bcol_number,dat_number,priority,status,certified', TEST_STAFF_SEARCH_DATA)
def test_staff_search(session, client, jwt, role, routing_slip, bcol_number, dat_number, priority, status, certified):
    """Assert that staff search requests returns the correct status."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    params = ''
    if routing_slip:
        params = '?routingSlipNumber=' + str(routing_slip)
    if bcol_number:
        if len(params) > 0:
            params += '&bcolAccountNumber=' + str(bcol_number)
        else:
            params = '?bcolAccountNumber=' + str(bcol_number)
    if dat_number:
        if len(params) > 0:
            params += '&datNumber=' + str(dat_number)
        else:
            params += '?datNumber=' + str(dat_number)
    if priority:
        if len(params) > 0:
            params += '&priority=true'
        else:
            params += '?priority=true'
    if certified:
        if len(params) > 0:
            params += '&certified=true'
        else:
            params += '?certified=true'
    # print('params=' + params)
    roles = [MHR_ROLE, role]
    account_id = role
    if role == GOV_ACCOUNT_ROLE:
        account_id = '1234'
    headers=create_header_account(jwt, roles, 'test-user', account_id)
    rv = client.post('/api/v1/searches',
                    json=MHR_NUMBER_JSON,
                    headers=headers,
                    content_type='application/json')
    test_search_id = rv.json['searchId']
    rv = client.post('/api/v1/search-results/' + test_search_id + params,
                     json=SELECTED_JSON,
                     headers=headers,
                     content_type='application/json')
    # check
    assert rv.status_code == status


@pytest.mark.parametrize('desc,roles,status,has_account, search_id, is_report', TEST_GET_DATA)
def test_get_search_detail(session, client, jwt, desc, roles, status, has_account, search_id, is_report):
    """Assert that a get search detail info by search id works as expected."""
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    # setup
    if is_report:
        headers = create_header_account_report(jwt, roles)
    elif has_account:
        headers = create_header_account(jwt, roles)
    else:
        headers = create_header(jwt, roles)
    # test
    rv = client.get('/api/v1/search-results/' + str(search_id),
                    headers=headers)

    # check
    # print(rv.json)
    assert rv.status_code == status


@pytest.mark.parametrize('desc,type,search_data,select_data,label,value', TEST_PAYMENT_DETAILS_DATA)
def test_get_payment_details(session, client, jwt, desc, type, search_data, select_data, label, value):
    """Assert that a valid search request payment details setup works as expected."""
    # setup
    search: SearchRequest = SearchRequest(id=1, search_type=type, search_criteria=search_data)
    result: SearchResult = SearchResult(search_id=1, search=search)

    # test
    details = get_payment_details(result, select_data)

    # check
    assert details
    assert details['label'] == label
    assert details['value'] == value


@pytest.mark.parametrize('desc,json_data,mhr_num,client_ref_id,match_count', TEST_PPR_SEARCH_DATA)
def test_post_selected_combo(session, client, jwt, desc, json_data, mhr_num, client_ref_id, match_count):
    """Assert that valid search criteria with PPR search returns a 201 status."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = create_header_account(jwt, [MHR_ROLE])
    search_criteria = copy.deepcopy(MHR_NUMBER_JSON)
    search_criteria['criteria']['value'] = mhr_num
    select_data = copy.deepcopy(json_data)
    select_data[0]['mhrNumber'] = mhr_num

    # test
    rv = client.post('/api/v1/searches',
                     json=search_criteria,
                     headers=headers,
                     content_type='application/json')
    test_search_id = rv.json['searchId']
    path = '/api/v1/search-results/' + test_search_id
    if client_ref_id:
        path += '?clientReferenceId=' + client_ref_id
    rv = client.post(path,
                     json=select_data,
                     headers=headers,
                     content_type='application/json')
    # check
    # current_app.logger.debug(rv.json)
    assert rv.status_code == HTTPStatus.OK
    response_json = rv.json
    if client_ref_id:
        assert response_json['searchQuery']['clientReferenceId'] == client_ref_id
    if json_data[0].get('includeLienInfo', False) and response_json.get('details'):
        assert 'pprRegistrations' in response_json['details'][0]
        if match_count > 0:
            assert len(response_json['details'][0]['pprRegistrations']) >= match_count
            for ppr_result in response_json['details'][0]['pprRegistrations']:
                assert ppr_result['financingStatement']
                statement = ppr_result['financingStatement']
                assert statement['type']
                assert statement['baseRegistrationNumber']
                assert statement['createDateTime']
                assert statement['registeringParty']
                assert statement['securedParties']
                assert statement['debtors']
                assert statement['vehicleCollateral'] or statement['generalCollateral']
        else:
            assert not response_json['details'][0]['pprRegistrations']
    elif 'details' in response_json and response_json['details']:
        assert 'pprRegistrations' not in response_json['details'][0]
