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

from ppr_api.services.authz import BCOL_HELP, PPR_ROLE, STAFF_ROLE
from tests.unit.services.utils import create_header, create_header_account


MOCK_AUTH_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/'
MOCK_PAY_URL = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/pay/api/v1/'

# Valid test search criteria
AIRCRAFT_DOT_JSON = {
    'type': 'AIRCRAFT_DOT',
    'criteria': {
        'value': 'BB2007'
    },
    'clientReferenceId': 'HISTORICAL SEARCH',
    'accountName': 'UT HISTORICAL SEARCH',
    'searchDateTime': '2022-01-01T07:59:59+00:00'
}
MHR_NUMBER_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'value': '106284'
    },
    'clientReferenceId': 'HISTORICAL SEARCH',
    'accountName': 'UT HISTORICAL SEARCH',
    'searchDateTime': '2022-01-01T07:59:59+00:00'
}
REG_NUMBER_JSON = {
    'type': 'REGISTRATION_NUMBER',
    'criteria': {
        'value': '502420N'
    },
    'clientReferenceId': 'HISTORICAL SEARCH',
    'accountName': 'UT HISTORICAL SEARCH',
    'searchDateTime': '2023-04-30T06:59:59+00:00'
}
SERIAL_NUMBER_JSON = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'value': '1G1YL2D73K5105174'
    },
    'clientReferenceId': 'HISTORICAL SEARCH',
    'accountName': 'UT HISTORICAL SEARCH',
    'searchDateTime': '2022-09-26T06:59:59+00:00'
}
INVALID_SERIAL_NUMBER_JSON = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'value': '1G1YL2D73K5105174'
    },
    'clientReferenceId': 'HISTORICAL SEARCH',
    'accountName': 'UT HISTORICAL SEARCH'
}
INVALID_SCHEMA_JSON = {
    'type': 'XX',
    'criteria': {
        'value': '1G1YL2D73K5105174'
    },
    'clientReferenceId': 'HISTORICAL SEARCH',
    'accountName': 'UT HISTORICAL SEARCH',
    'searchDateTime': '2022-09-26T06:59:59+00:00'
}
INDIVIDUAL_DEBTOR_JSON = {
    'type': 'INDIVIDUAL_DEBTOR',
    'criteria': {
        'debtorName': {
            'last': 'BITTNER',
            'first': 'GAIL'
        }
    },
    'clientReferenceId': 'HISTORICAL SEARCH',
    'accountName': 'UT HISTORICAL SEARCH',
    'searchDateTime': '2021-12-16T07:59:59+00:00'
}
BUSINESS_DEBTOR_JSON = {
    'type': 'BUSINESS_DEBTOR',
    'criteria': {
        'debtorName': {
            'business': '0996357 B.C. LTD.'
        }
    },
    'clientReferenceId': 'HISTORICAL SEARCH',
    'accountName': 'UT HISTORICAL SEARCH',
    'searchDateTime': '2022-05-16T06:59:59+00:00'
}
# testdata pattern is ({desc} ,{role}, {payload}, {status})
TEST_SEARCH_DATA = [
    ('Valid serial number', STAFF_ROLE, SERIAL_NUMBER_JSON, HTTPStatus.CREATED),
    ('Valid registration number', STAFF_ROLE, REG_NUMBER_JSON, HTTPStatus.CREATED),
    ('Valid mhr number', STAFF_ROLE, MHR_NUMBER_JSON, HTTPStatus.CREATED),
    ('Valid aircraft DOT number', STAFF_ROLE, AIRCRAFT_DOT_JSON, HTTPStatus.CREATED),
    ('Valid business debtor name', STAFF_ROLE, BUSINESS_DEBTOR_JSON, HTTPStatus.CREATED),
    ('Valid individual debtor name', STAFF_ROLE, INDIVIDUAL_DEBTOR_JSON, HTTPStatus.CREATED),
    ('Non-staff role', BCOL_HELP, SERIAL_NUMBER_JSON, HTTPStatus.UNAUTHORIZED),
    ('Missing account id', STAFF_ROLE, SERIAL_NUMBER_JSON, HTTPStatus.BAD_REQUEST),
    ('Schema validation error', STAFF_ROLE, INVALID_SCHEMA_JSON, HTTPStatus.BAD_REQUEST),
    ('Missing startDateTime', STAFF_ROLE, INVALID_SERIAL_NUMBER_JSON, HTTPStatus.BAD_REQUEST)
]


@pytest.mark.parametrize('desc, role, payload, status', TEST_SEARCH_DATA)
def test_search(session, client, jwt, desc, role, payload, status):
    """Assert that staff search requests returns the correct status."""
    if not is_ci_testing():
        # setup
        current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
        current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
        headers = None
        roles = [PPR_ROLE, role]
        if desc == 'Missing account id':
            headers = create_header(jwt, roles)
        elif role == STAFF_ROLE:
            headers = create_header_account(jwt, roles, 'test-user', STAFF_ROLE)
            headers['Staff-Account-Id'] = '3040'
        else:
            headers = create_header_account(jwt, roles, 'test-user', 'PS12345')

        rv = client.post('/api/v1/historical-searches',
                        json=payload,
                        headers=headers,
                        content_type='application/json')
        # check
        # current_app.logger.debug(rv.json)
        assert rv.status_code == status


def is_ci_testing() -> bool:
    """Check unit test environment: exclude most reports for CI testing."""
    return  current_app.config.get("DEPLOYMENT_ENV", "testing") == "testing"
