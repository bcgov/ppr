# Copyright © 2025 Province of British Columbia
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

"""Tests to verify the notification integration.

Test-Suite to ensure that the notification service is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app

from mhr_api.services.notify import Notify

TEST_TRANSFER = {
    'mhrNumber': '125234',
    'registrationType': 'TRANS_WILL',
    'documentDescription': 'TRANSFER TO EXECUTOR - GRANT OF PROBATE WITH WILL',
    'reviewPending': True,
    'clientReferenceId': 'EX-TRANS-001',
    'submittingParty': {
        'businessName': 'ABC SEARCHING COMPANY',
        'address': {
        'street': '222 SUMMER STREET',
        'city': 'VICTORIA',
        'region': 'BC',
        'country': 'CA',
        'postalCode': 'V8W 2V8'
        },
        'emailAddress': 'bsmith-ut@abc-search.com',
        'phoneNumber': '6041234567',
        'phoneExtension': '546'
    },
    'deleteOwnerGroups': [
        {
        'groupId': 1,
        'owners': [
            {
            'individualName': {
                'first': 'Jane',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'SOLE'
        }
    ],
    'addOwnerGroups': [
        {
        'groupId': 2,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'SOLE',
        'status': 'ACTIVE'
        }
    ],
    'payment': {
        'invoiceId': '52870',
        'receipt': '/api/v1/payment-requests/52870/receipts',
        'priority': True
    },
}
# testdata pattern is ({description}, {has_env_var}, {configured})
TEST_REVIEW_CONFIGURED_DATA = [
    ('Service configured', False, False),
    ('Service not configured', True, True),
]
# testdata pattern is ({description}, {has_env_var}, {has_email}, {status}, {approved})
TEST_REVIEW_NOTIFY_DATA = [
    ('Approved no service', False, True, HTTPStatus.SERVICE_UNAVAILABLE, True),
    ('Declined no service', False, True, HTTPStatus.SERVICE_UNAVAILABLE, False),
    ('Approved no email', True, False, HTTPStatus.BAD_REQUEST, True),
    ('Declined no email', True, False, HTTPStatus.BAD_REQUEST, False),
    ('Approved valid', True, True, HTTPStatus.BAD_REQUEST, True),
    ('Declined valid', True, True, HTTPStatus.BAD_REQUEST, False),
]


@pytest.mark.parametrize('desc,has_env_var,has_email,status,approved', TEST_REVIEW_NOTIFY_DATA)
def test_review_notify(session, jwt, desc, has_env_var, has_email, status, approved):
    """Assert that staff review notifications work as expected."""
    if is_ci_testing():
        return
    env_var = current_app.config.get("NOTIFY_REVIEW_CONFIG")
    if not has_env_var:
        current_app.config.update(NOTIFY_REVIEW_CONFIG="")
    reg_data = copy.deepcopy(TEST_TRANSFER)
    if not has_email:
        del reg_data["submittingParty"]["emailAddress"]
    notify: Notify = Notify(**{"review": True})
    n_status = HTTPStatus.OK
    if approved:
        n_status = notify.send_review_approved(reg_data, "verify_url")
    else:
        n_status = notify.send_review_declined(reg_data, "declined reason here")
    if env_var:
        current_app.config.update(NOTIFY_REVIEW_CONFIG=env_var)
    assert n_status == status


@pytest.mark.parametrize('desc,has_env_var,configured', TEST_REVIEW_CONFIGURED_DATA)
def test_review_configured(session, jwt, desc, has_env_var, configured):
    """Assert that service configuration check returns the expected result."""
    if is_ci_testing():
        return
    env_var = current_app.config.get("NOTIFY_REVIEW_CONFIG")
    if not env_var and has_env_var:
       current_app.config.update(NOTIFY_REVIEW_CONFIG="junk config")
    elif not has_env_var:
       current_app.config.update(NOTIFY_REVIEW_CONFIG="")

    has_config = Notify.is_staff_review_configured()
    if env_var:
       current_app.config.update(NOTIFY_REVIEW_CONFIG=env_var)
    assert has_config == configured


def is_ci_testing() -> bool:
    """Check unit test environment: exclude most reports for CI testing."""
    return  current_app.config.get("DEPLOYMENT_ENV", "testing") == "testing"
