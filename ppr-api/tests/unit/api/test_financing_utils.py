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

"""Tests to verify the financing utils.

Test-Suite to ensure that the financing/registration helper methods are working as expected.
"""
from http import HTTPStatus

import pytest
from flask import current_app

from ppr_api.models import Registration, FinancingStatement, VerificationReport, utils as model_utils
from ppr_api.reports import ReportTypes
from ppr_api.resources import financing_utils as fs_utils
from ppr_api.services.payment.client import SBCPaymentClient


CC_PAYREF = {"invoiceId": "88888888", "receipt": "receipt", "ccPayment": True}
# testdata pattern is ({desc}, {status}, {reg_id}, is_create)
TEST_REGISTRATION_GET_DATA = [
    ('Valid POST', HTTPStatus.CREATED, 200000011, True),
    ('Valid GET', HTTPStatus.OK, 200000011, False),
    ('Pending', HTTPStatus.ACCEPTED, 200000000, False),
    ('Pending', HTTPStatus.ACCEPTED, 200000000, True),
]
# testdata pattern is ({pay_ref}, {account_id}, {username}, {usergroup})
TEST_SETUP_CC_PAYMENT= [
    (CC_PAYREF, "1234", "username", "ppr_staff")
]


@pytest.mark.parametrize('desc,status,reg_id,is_create', TEST_REGISTRATION_GET_DATA)
def test_get_registration_report(session, client, jwt, desc, status, reg_id, is_create):
    """Assert that a get registration report request returns the expected response."""
    # setup
    if is_ci_testing():
        return
    token = SBCPaymentClient.get_sa_token()
    registration: Registration = Registration.find_by_id(reg_id)
    valid_status: int = HTTPStatus.CREATED if is_create else HTTPStatus.OK
    report_data = registration.verification_json('changeRegistrationNumber')
    if reg_id == 200000000:
        report_info: VerificationReport = VerificationReport.find_by_registration_id(reg_id)
        if report_info:
            report_info.create_ts = model_utils.now_ts()
            report_info.save()

    # test
    raw_data, resp_status, headers = fs_utils.get_registration_report(registration,
                                                                      report_data,
                                                                      ReportTypes.FINANCING_STATEMENT_REPORT.value,
                                                                      token,
                                                                      valid_status)
    # check
    assert resp_status == status
    if resp_status in (HTTPStatus.CREATED, HTTPStatus.OK):
        assert raw_data


def test_get_registration_callback_report(session, client, jwt):
    """Assert that a valid get registration callback report request returns the expected response."""
    # setup
    if is_ci_testing():
        return
    statement: FinancingStatement = FinancingStatement.find_by_registration_number('TEST0001', 'PS12345', True)
    statement.include_changes_json = False
    statement.current_view_json = False
    registration: Registration = statement.registration[0]
    registration.verification_report.report_data = statement.json

    # test
    response_data, status = fs_utils.get_registration_callback_report(registration)
    # check
    assert status == HTTPStatus.OK
    assert response_data == {}


@pytest.mark.parametrize('pay_ref, account_id, username, usergroup',TEST_SETUP_CC_PAYMENT)
def test_cc_payment_setup(session, client, jwt, pay_ref, account_id, username, usergroup):
    """Assert that setting up the pay api invoice information by doc type works as expected."""
    reg_json = {}
    reg_json = fs_utils.setup_cc_draft(reg_json, pay_ref, account_id, username)
    assert reg_json.get("payment")
    assert reg_json["payment"] == pay_ref
    assert reg_json.get("accountId") == account_id
    assert reg_json.get("username") == username


def is_ci_testing() -> bool:
    """Check unit test environment: exclude most reports for CI testing."""
    return  current_app.config.get("DEPLOYMENT_ENV", "testing") == "testing"
