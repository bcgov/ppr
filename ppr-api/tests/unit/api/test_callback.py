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

import pytest
from flask import current_app

from ppr_api.models import FinancingStatement, Registration
from ppr_api.resources.utils import get_payment_details, get_payment_details_financing, \
     get_payment_type_financing
from ppr_api.services.authz import COLIN_ROLE, PPR_ROLE, STAFF_ROLE, BCOL_HELP, GOV_ACCOUNT_ROLE
from ppr_api.services.payment import TransactionTypes
from tests.unit.services.utils import create_header, create_header_account, create_header_account_report


MOCK_URL_NO_KEY = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
MOCK_PAY_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/pay/api/v1/'
# testdata pattern is ({desc}, {status}, {registration_id}, {party_id})
TEST_MAIL_CALLBACK_DATA = [
    ('Missing reg id', HTTPStatus.BAD_REQUEST, None, 9999999),
    ('Invalid reg id', HTTPStatus.NOT_FOUND, 300000005, 200000024),
    ('Missing party id', HTTPStatus.BAD_REQUEST, 200000004, None),
    ('Invalid party id', HTTPStatus.NOT_FOUND, 200000004, 9999999),
    ('Already exists', HTTPStatus.OK, 200000004, 200000013),
    ('Unauthorized', HTTPStatus.UNAUTHORIZED, 200000008, 200000023)
]
# testdata pattern is ({desc}, {status}, {start_ts}, {end_ts})
TEST_MAIL_LIST_DATA = [
    ('Missing start ts', HTTPStatus.BAD_REQUEST, None, None),
    ('Invalid start ts', HTTPStatus.BAD_REQUEST, '2023-01-31TXX:00:01-08:00', None),
    ('Invalid range', HTTPStatus.BAD_REQUEST, '2023-01-31T00:00:01-08:00', '2023-01-30T00:00:01-08:00'),
    ('Invalid end ts', HTTPStatus.BAD_REQUEST, None, '2023-01-31TXX:00:01-08:00'),
    ('Valid start', HTTPStatus.OK, '2023-01-31T00:00:01-08:00', None),
    ('Unauthorized', HTTPStatus.UNAUTHORIZED, None, None)
]


@pytest.mark.parametrize('desc,status,reg_id,party_id', TEST_MAIL_CALLBACK_DATA)
def test_callback_mail_report(session, client, jwt, desc, status, reg_id, party_id):
    """Assert that a mail report callback request returns the expected status."""
    # setup
    json_data = {
        'registrationId': reg_id,
        'partyId': party_id
    }
    if reg_id is None:
        del json_data['registrationId']
    if party_id is None:
        del json_data['partyId']
    headers = None
    if status != HTTPStatus.UNAUTHORIZED:
        apikey = current_app.config.get('SUBSCRIPTION_API_KEY')
        if apikey:
            headers = {
                'x-apikey': apikey
            }

    # test
    rv = client.post('/api/v1/callbacks/mail-report',
                     json=json_data,
                     headers=headers,
                     content_type='application/json')
    # check
    assert rv.status_code == status


@pytest.mark.parametrize('desc,status,start_ts,end_ts', TEST_MAIL_LIST_DATA)
def test_list_mail_report(session, client, jwt, desc, status, start_ts, end_ts):
    """Assert that list mail reports by timestamp request returns the expected status."""
    # setup
    params = ''
    if start_ts:
        params += f'?startDateTime={start_ts}'
        if end_ts:
            params += f'&endDateTime={end_ts}'
    elif end_ts:
        params += f'?endDateTime={end_ts}'

    headers = None
    if status != HTTPStatus.UNAUTHORIZED:
        apikey = current_app.config.get('SUBSCRIPTION_API_KEY')
        if apikey:
            headers = {
                'x-apikey': apikey
            }

    # test
    rv = client.get('/api/v1/callbacks/mail-report' + params,
                     headers=headers)
    # check
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        assert rv.json
        for result in rv.json:
            assert result.get('id')
            assert result.get('dateTime')
            assert result.get('docStorageRef')
