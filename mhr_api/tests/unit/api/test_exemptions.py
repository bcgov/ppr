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

"""Tests to verify the endpoints for maintaining MH exemptions.

Test-Suite to ensure that the /exemptions endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app
from registry_schemas.example_data.mhr import EXEMPTION

from mhr_api.models import MhrRegistration
from mhr_api.services.authz import MHR_ROLE, STAFF_ROLE, COLIN_ROLE, \
                                   REQUEST_EXEMPTION_RES, REQUEST_EXEMPTION_NON_RES, \
                                   TRANSFER_DEATH_JT, TRANSFER_SALE_BENEFICIARY
from tests.unit.services.utils import create_header, create_header_account


DOC_ID_VALID = '63166035'
MOCK_AUTH_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
MOCK_PAY_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/pay/api/v1/'

QUALIFIED_USER = [MHR_ROLE, REQUEST_EXEMPTION_NON_RES, REQUEST_EXEMPTION_RES, TRANSFER_DEATH_JT, TRANSFER_SALE_BENEFICIARY]
# testdata pattern is ({description}, {mhr_num}, {roles}, {status}, {account})
TEST_CREATE_DATA = [
    ('Invalid schema validation missing submitting', '098666', [MHR_ROLE, REQUEST_EXEMPTION_RES],
     HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Missing account', '098666', [MHR_ROLE, REQUEST_EXEMPTION_RES], HTTPStatus.BAD_REQUEST, None),
    ('Staff missing account', '098666', [MHR_ROLE, STAFF_ROLE, REQUEST_EXEMPTION_RES],
     HTTPStatus.BAD_REQUEST, None),
    ('Invalid role product', '098666', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Invalid non-exemption role', '098666', [MHR_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Valid staff', '098666', [MHR_ROLE, STAFF_ROLE, REQUEST_EXEMPTION_RES], HTTPStatus.CREATED, 'PS12345'),
    ('Valid non-staff legacy', '098666', QUALIFIED_USER, HTTPStatus.CREATED, 'PS12345'),
    ('Valid non-staff new', '150081', QUALIFIED_USER, HTTPStatus.CREATED, '2523'),
    ('Invalid mhr num', '300655', [MHR_ROLE, REQUEST_EXEMPTION_RES], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Invalid exempt', '098655', [MHR_ROLE, REQUEST_EXEMPTION_RES], HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Invalid historical', '099942', [MHR_ROLE, REQUEST_EXEMPTION_RES], HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Invalid missing note remarks', '098666', [MHR_ROLE, REQUEST_EXEMPTION_NON_RES, REQUEST_EXEMPTION_RES],
     HTTPStatus.BAD_REQUEST, 'PS12345')
]
TEST_CREATE_DATA_1 = [
    ('Valid non-staff new', '150081', QUALIFIED_USER, HTTPStatus.CREATED, '2523')
]


@pytest.mark.parametrize('desc,mhr_num,roles,status,account', TEST_CREATE_DATA)
def test_create(session, client, jwt, desc, mhr_num, roles, status, account):
    """Assert that a post MH registration works as expected."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    json_data = copy.deepcopy(EXEMPTION)
    del json_data['submittingParty']['phoneExtension']
    del json_data['documentId']
    del json_data['documentDescription']
    del json_data['documentRegistrationNumber']
    del json_data['createDateTime']
    del json_data['payment']
    json_data['mhrNumber'] = mhr_num
    if desc == 'Invalid schema validation missing submitting':
        del json_data['submittingParty']
    elif desc == 'Invalid missing note remarks':
        del json_data['note']['remarks']
    if account:
        headers = create_header_account(jwt, roles, 'UT-TEST', account)
    else:
        headers = create_header(jwt, roles)
    if status == HTTPStatus.CREATED and STAFF_ROLE in roles:
        json_data['documentId'] = DOC_ID_VALID
    # test
    response = client.post('/api/v1/exemptions/' + mhr_num,
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    assert response.status_code == status
    if response.status_code == HTTPStatus.CREATED:
        registration: MhrRegistration = MhrRegistration.find_by_mhr_number(response.json['mhrNumber'],
                                                                           account)
        assert registration
