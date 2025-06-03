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

"""Tests to verify the pay-api integration.

Test-Suite to ensure that the client for the pay-api service is working as expected.
"""
import copy
import json
import os
from http import HTTPStatus

import pytest
from flask import current_app

from ppr_api.services.payment.client import SBCPaymentClient, ApiRequestError, CC_REQUEST_PAYMENT_INFO
from ppr_api.services.payment import PaymentMethods, StatusCodes, TransactionTypes
from ppr_api.services.payment.payment import Payment
from ppr_api.services.payment.exceptions import SBCPaymentException
from ppr_api.services.authz import PPR_ROLE
from tests.unit.services.utils import helper_create_jwt


MOCK_URL_NO_KEY = 'https://test.api.connect.gov.bc.ca/mockTarget/pay/api/v1/'
MOCK_URL = 'https://test.api.connect.gov.bc.ca/pay-dev/api/v1/'
PAY_DETAILS_SEARCH = {
    'label': 'Search by SERIAL_NUMBER',
    'value': '123456789'
}
PAY_DETAILS_REGISTRATION = {
    'label': 'Reg Number',
    'value': '100468B'
}
PAY_DETAILS_CC = {
    'label': 'CC TEST',
    'value': 'UNIT TESTING',
    'ccPayment': True
}
PAYMENT_REQUEST_TEMPLATE = {
    "filingInfo": {
        "filingIdentifier": "",
        "folioNumber": "",
        "filingTypes": [{"filingTypeCode": "", "priority": False, "futureEffective": False, "quantity": 1}],
    },
    "businessInfo": {"corpType": "PPR"},
    "details": [{"label": "", "value": ""}],
}

# testdata pattern is ({valid}, {filing_type}, {pay_method}, {pay_status})
TEST_PAY_METHOD_STATUS = [
    (True, 'SERCH', PaymentMethods.DRAWDOWN.value, StatusCodes.COMPLETED.value),
    (True, 'SSRCH', PaymentMethods.EJV.value, StatusCodes.COMPLETED.value),
    (True, 'PPRCD', PaymentMethods.PAD.value, StatusCodes.COMPLETED.value),
    (True, 'FSCHG', PaymentMethods.DRAWDOWN.value, StatusCodes.APPROVED.value),
    (True, 'FSREG', PaymentMethods.EJV.value, StatusCodes.APPROVED.value),
    (True, 'FSREN', PaymentMethods.PAD.value, StatusCodes.APPROVED.value),
    (True, 'FSDIS', PaymentMethods.INTERNAL.value, StatusCodes.APPROVED.value),
    (True, 'FSCHG', PaymentMethods.DRAWDOWN.value, StatusCodes.PAID.value),
    (True, 'FSREG', PaymentMethods.EJV.value, StatusCodes.PAID.value),
    (True, 'FSREN', PaymentMethods.PAD.value, StatusCodes.PAID.value),
    (True, 'FSDIS', PaymentMethods.INTERNAL.value, StatusCodes.PAID.value),
    (True, 'FSCHG', PaymentMethods.CC.value, StatusCodes.CREATED.value),
    (True, 'FSREG', PaymentMethods.CC.value, StatusCodes.CREATED.value),
    (True, 'FSREN', PaymentMethods.CC.value, StatusCodes.CREATED.value),
    (True, 'FSDIS', PaymentMethods.DIRECT_PAY.value, StatusCodes.CREATED.value),
    (True, 'FSCHG', PaymentMethods.DIRECT_PAY.value, StatusCodes.CREATED.value),
    (True, 'FSREG', PaymentMethods.DIRECT_PAY.value, StatusCodes.CREATED.value),
    (True, 'FSREN', PaymentMethods.DIRECT_PAY.value, StatusCodes.CREATED.value),
    (True, 'FSDIS', PaymentMethods.DIRECT_PAY.value, StatusCodes.CREATED.value),
    (True, 'SERCH', PaymentMethods.DIRECT_PAY.value, StatusCodes.CREATED.value),
    (True, 'SSRCH', PaymentMethods.DIRECT_PAY.value, StatusCodes.CREATED.value),
    (True, 'PPRCD', PaymentMethods.DIRECT_PAY.value, StatusCodes.CREATED.value),
    (True, 'SERCH', PaymentMethods.CC.value, StatusCodes.CREATED.value),
    (True, 'SSRCH', PaymentMethods.CC.value, StatusCodes.CREATED.value),
    (True, 'PPRCD', PaymentMethods.CC.value, StatusCodes.CREATED.value),
]
# testdata pattern is ({pay_trans_type}, {quantity}, {filing_type}, {cc})
TEST_PAY_TYPE_FILING_TYPE = [
    (TransactionTypes.FINANCING_CL.value, 5, 'CLREG', False),
    (TransactionTypes.FINANCING_LIFE_YEAR.value, 5, 'FSREG', False),
    (TransactionTypes.SEARCH.value, 1, 'SERCH', False),
    (TransactionTypes.AMENDMENT.value, 1, 'FSCHG', False),
    (TransactionTypes.CHANGE.value, 1, 'FSCHG', False),
    (TransactionTypes.DISCHARGE.value, 1, 'FSDIS', False),
    (TransactionTypes.FINANCING_FR.value, 1, 'FLREG', False),
    (TransactionTypes.FINANCING_NO_FEE.value, 1, 'NCREG', False),
    (TransactionTypes.FINANCING_INFINITE.value, 1, 'INFRG', False),
    (TransactionTypes.FINANCING_CL_INFINITE.value, 1, 'INFRG', False),
    (TransactionTypes.RENEWAL_INFINITE.value, 1, 'INFRN', False),
    (TransactionTypes.RENEWAL_LIFE_YEAR.value, 3, 'FSREN', False),
    (TransactionTypes.FINANCING_CL.value, 5, 'CLREG', True),
    (TransactionTypes.FINANCING_LIFE_YEAR.value, 5, 'FSREG', True),
    (TransactionTypes.AMENDMENT.value, 1, 'FSCHG', True),
    (TransactionTypes.FINANCING_INFINITE.value, 1, 'INFRG', True),
    (TransactionTypes.RENEWAL_INFINITE.value, 1, 'INFRN', True),
    (TransactionTypes.RENEWAL_LIFE_YEAR.value, 3, 'FSREN', True),
 ]
# testdata pattern is ({pay_trans_type}, {routingSlip}, {bcolNumber}, {datNUmber}, {waiveFees})
TEST_PAY_STAFF_SEARCH = [
    (TransactionTypes.SEARCH_STAFF_NO_FEE.value, None, None, None, True),
    (TransactionTypes.SEARCH_STAFF.value, '12345', None, None, False),
    (TransactionTypes.SEARCH_STAFF.value, None, '62345', None, False),
    (TransactionTypes.SEARCH_STAFF.value, None, '62345', '72345', False),
    (TransactionTypes.SEARCH_STAFF_CERTIFIED_NO_FEE.value, None, None, None, True),
    (TransactionTypes.SEARCH_STAFF_CERTIFIED.value, '12345', None, None, False),
    (TransactionTypes.SEARCH_STAFF_CERTIFIED.value, None, '62345', None, False),
    (TransactionTypes.SEARCH_STAFF_CERTIFIED.value, None, '62345', '72345', False)
]
# testdata pattern is ({pay_trans_type}, {routingSlip}, {bcolNumber}, {datNUmber}, {waiveFees}, {cc})
TEST_PAY_STAFF_REGISTRATION = [
    (TransactionTypes.DISCHARGE.value, None, None, None, True, False),
    (TransactionTypes.FINANCING_NO_FEE.value, None, None, None, True, False),
    (TransactionTypes.FINANCING_INFINITE.value, None, None, None, True, False),
    (TransactionTypes.FINANCING_CL_INFINITE.value, None, None, None, True, False),
    (TransactionTypes.FINANCING_LIFE_YEAR.value, None, None, None, True, False),
    (TransactionTypes.FINANCING_LIFE_YEAR.value, '12345', None, None, False, False),
    (TransactionTypes.FINANCING_LIFE_YEAR.value, None, '62345', None, False, False),
    (TransactionTypes.FINANCING_LIFE_YEAR.value, None, '62345', '72345', False, False),
    (TransactionTypes.FINANCING_CL.value, None, None, None, True, False),
    (TransactionTypes.FINANCING_CL.value, '12345', None, None, False, False),
    (TransactionTypes.FINANCING_CL.value, None, '62345', None, False, False),
    (TransactionTypes.FINANCING_CL.value, None, '62345', '72345', False, False),
    (TransactionTypes.RENEWAL_LIFE_YEAR.value, None, None, None, True, False),
    (TransactionTypes.AMENDMENT.value, '12345', None, None, False, False),
    (TransactionTypes.AMENDMENT.value, None, None, None, True, False),
    (TransactionTypes.RENEWAL_INFINITE.value, None, '62345', '72345', False, False),
    (TransactionTypes.FINANCING_INFINITE.value, None, None, None, False, True),
    (TransactionTypes.FINANCING_LIFE_YEAR.value, None, None, None, False, True),
    (TransactionTypes.RENEWAL_LIFE_YEAR.value, None, None, None, False, True),
    (TransactionTypes.RENEWAL_INFINITE.value, None, None, None, False, True),
    (TransactionTypes.AMENDMENT.value, None, None, None, False, True),
]


@pytest.mark.parametrize('pay_trans_type,routing_slip,bcol_number,dat_number,waive_fees', TEST_PAY_STAFF_SEARCH)
def test_payment_data_staff_search(client, jwt, pay_trans_type, routing_slip, bcol_number, dat_number, waive_fees):
    """Assert that the staff payment payment-request body is as expected for a pay transaction type."""
    transaction_info = {
        'transactionType': pay_trans_type,
        'accountId': '3040'
    }
    if pay_trans_type in (TransactionTypes.SEARCH_STAFF_CERTIFIED_NO_FEE.value,
                          TransactionTypes.SEARCH_STAFF_NO_FEE.value):
        transaction_info['certified'] = True
    if routing_slip:
        transaction_info['routingSlipNumber'] = routing_slip
    if bcol_number:
        transaction_info['bcolAccountNumber'] = bcol_number
    if dat_number:
        transaction_info['datNumber'] = dat_number

    # test
    data = SBCPaymentClient.create_payment_staff_search_data(transaction_info, 'UT-PAY-0001')
    # check
    assert data
    if pay_trans_type in (TransactionTypes.SEARCH_STAFF_CERTIFIED_NO_FEE.value,
                          TransactionTypes.SEARCH_STAFF_NO_FEE.value):
        assert len(data['filingInfo']['filingTypes']) == 2
    else:
        assert len(data['filingInfo']['filingTypes']) == 1
    if waive_fees:
        assert data['filingInfo']['filingTypes'][0]['waiveFees']
        if pay_trans_type == TransactionTypes.SEARCH_STAFF_CERTIFIED_NO_FEE.value:
            assert data['filingInfo']['filingTypes'][1]['waiveFees']
    else:
        assert 'waiveFees' not in data['filingInfo']['filingTypes'][0]

    if not routing_slip and not bcol_number:
        assert 'accountInfo' not in data
    elif routing_slip:
        assert 'accountInfo' in data and data['accountInfo']['routingSlip'] == routing_slip
    elif bcol_number:
        assert 'accountInfo' in data and data['accountInfo']['bcolAccountNumber'] == bcol_number
        if dat_number:
            assert data['accountInfo']['datNumber'] == dat_number


@pytest.mark.parametrize('pay_trans_type,routing_slip,bcol_number,dat_number,waive_fees', TEST_PAY_STAFF_SEARCH)
def test_payment_staff_search_mock(client, jwt, pay_trans_type, routing_slip, bcol_number, dat_number, waive_fees):
    """Assert that a pay-api staff search payment request works as expected with the mock service endpoint."""
    # setup
    token = helper_create_jwt(jwt, [PPR_ROLE])
    payment = Payment(jwt=token, account_id='PS12345', details=PAY_DETAILS_SEARCH)
    payment.api_url = MOCK_URL_NO_KEY
    transaction_info = {
        'transactionType': pay_trans_type,
        'accountId': '3040'
    }
    if pay_trans_type in (TransactionTypes.SEARCH_STAFF_CERTIFIED_NO_FEE.value,
                          TransactionTypes.SEARCH_STAFF_NO_FEE.value):
        transaction_info['certified'] = True
    if routing_slip:
        transaction_info['routingSlipNumber'] = routing_slip
    if bcol_number:
        transaction_info['bcolAccountNumber'] = bcol_number
    if dat_number:
        transaction_info['datNumber'] = dat_number

    # test
    pay_data = payment.create_payment_staff_search(transaction_info, 'UT-PAY-SEARCH-01')
    # print(pay_data)
    # check
    assert pay_data
    assert pay_data['invoiceId']
    assert pay_data['receipt']


@pytest.mark.parametrize('pay_trans_type,routing_slip,bcol_number,dat_number,waive_fees,cc', TEST_PAY_STAFF_REGISTRATION)
def test_payment_data_staff_registration(client, jwt, pay_trans_type, routing_slip, bcol_number, dat_number,
                                         waive_fees, cc):
    """Assert that the staff payment payment-request body is as expected for a pay transaction type."""
    transaction_info = {
        'transactionType': pay_trans_type,
        'feeQuantity': 1,
        'accountId': '3040'
    }
    if waive_fees:
        transaction_info['waiveFees'] = True
    if routing_slip:
        transaction_info['routingSlipNumber'] = routing_slip
    if bcol_number:
        transaction_info['bcolAccountNumber'] = bcol_number
    if dat_number:
        transaction_info['datNumber'] = dat_number
 
    token = helper_create_jwt(jwt, [PPR_ROLE])
    details: dict = PAY_DETAILS_REGISTRATION if not cc else PAY_DETAILS_CC
    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345', details=details)
 
    # test
    data = pay_client.create_payment_staff_registration_data(transaction_info, 'UT-PAY-0001')
    data = pay_client.update_payload_data(data)

    # check
    assert data
    assert len(data['filingInfo']['filingTypes']) == 1
    assert data['filingInfo']['filingTypes'][0]['filingTypeCode']
    assert data['filingInfo']['folioNumber'] == 'UT-PAY-0001'
    if waive_fees:
        assert 'waiveFees' in data['filingInfo']['filingTypes'][0]
    else:
        assert 'waiveFees' not in data['filingInfo']['filingTypes'][0]

    if not routing_slip and not bcol_number:
        assert 'accountInfo' not in data
    elif routing_slip:
        assert 'accountInfo' in data and data['accountInfo']['routingSlip'] == routing_slip
    elif bcol_number:
        assert 'accountInfo' in data and data['accountInfo']['bcolAccountNumber'] == bcol_number
        if dat_number:
            assert data['accountInfo']['datNumber'] == dat_number
    if cc:
        assert data.get("paymentInfo") == CC_REQUEST_PAYMENT_INFO
    else:
        assert not data.get("paymentInfo")


@pytest.mark.parametrize('pay_trans_type,routing_slip,bcol_number,dat_number,waive_fees,cc', TEST_PAY_STAFF_REGISTRATION)
def test_payment_staff_registration_mock(client, jwt, pay_trans_type, routing_slip, bcol_number, dat_number,
                                         waive_fees,cc):
    """Assert that a pay-api staff registration payment request works as expected with the mock service endpoint."""
    # setup
    token = helper_create_jwt(jwt, [PPR_ROLE])
    details: dict = PAY_DETAILS_REGISTRATION if not cc else PAY_DETAILS_CC
    payment = Payment(jwt=token, account_id=None, details=details)
    payment.api_url = MOCK_URL_NO_KEY
    transaction_info = {
        'transactionType': pay_trans_type,
        'feeQuantity': 1,
        'accountId': '3040'
    }
    if waive_fees:
        transaction_info['waiveFees'] = True
    if routing_slip:
        transaction_info['routingSlipNumber'] = routing_slip
    if bcol_number:
        transaction_info['bcolAccountNumber'] = bcol_number
    if dat_number:
        transaction_info['datNumber'] = dat_number

    # test
    pay_data = payment.create_payment_staff_registration(transaction_info, 'UT-PAY-SEARCH-01')
    # print(pay_data)
    # check
    assert pay_data
    assert pay_data['invoiceId']
    assert pay_data['receipt']
    if cc:
        assert pay_data.get("ccPayment")
        assert "paymentActionRequired" in pay_data
        assert "paymentPortalURL" in pay_data
    else:
        assert "ccPayment" not in pay_data
        assert "paymentActionRequired" not in pay_data
        assert "paymentPortalURL" not in pay_data


@pytest.mark.parametrize('pay_trans_type,quantity,filing_type,cc', TEST_PAY_TYPE_FILING_TYPE)
def test_payment_filing_type(client, jwt, pay_trans_type, quantity, filing_type, cc):
    """Assert that the payment-request body filing type is as expected for a pay transaction type."""
    # setup
    token = helper_create_jwt(jwt, [PPR_ROLE])
    details: dict = PAY_DETAILS_REGISTRATION if not cc else PAY_DETAILS_CC
    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345', details=details)

    # test
    data = pay_client.create_payment_data(pay_trans_type, quantity, '200000000', 'UT-PAY-0001')
    data = pay_client.update_payload_data(data)
    # check
    assert data
    assert data['filingInfo']['filingIdentifier'] == '200000000'
    assert data['filingInfo']['folioNumber'] == 'UT-PAY-0001'
    assert len(data['filingInfo']['filingTypes']) == 1
    assert data['filingInfo']['filingTypes'][0]['quantity'] == quantity
    assert data['filingInfo']['filingTypes'][0]['filingTypeCode'] == filing_type
    assert data['businessInfo']['corpType'] == 'PPR'
    if cc:
        assert data.get("paymentInfo") == CC_REQUEST_PAYMENT_INFO
    else:
        assert not data.get("paymentInfo")


def test_payment_data_all(client, jwt):
    """Assert that the payment-request body content is as expected with all properties."""
    # setup

    # test
    data = SBCPaymentClient.create_payment_data(TransactionTypes.SEARCH.value, 1, '200000000', 'UT-PAY-0001')
    print(json.dumps(data))
    # check
    assert data
    assert data['filingInfo']['filingIdentifier'] == '200000000'
    assert data['filingInfo']['folioNumber'] == 'UT-PAY-0001'
    assert len(data['filingInfo']['filingTypes']) == 1
    assert data['filingInfo']['filingTypes'][0]['quantity'] == 1
    assert data['filingInfo']['filingTypes'][0]['filingTypeCode'] == 'SERCH'
    assert data['businessInfo']['corpType'] == 'PPR'


def test_payment_data_no_trans_id(client, jwt):
    """Assert that the payment-request body content is as expected with no transaction id."""
    # setup

    # test
    data = SBCPaymentClient.create_payment_data(TransactionTypes.SEARCH.value, 1, None, 'UT-PAY-0001')

    # check
    assert data
    assert 'filingIdentifier' not in data['filingInfo']
    assert data['filingInfo']['folioNumber'] == 'UT-PAY-0001'
    assert len(data['filingInfo']['filingTypes']) == 1
    assert data['filingInfo']['filingTypes'][0]['quantity'] == 1
    assert data['filingInfo']['filingTypes'][0]['filingTypeCode'] == 'SERCH'
    assert data['businessInfo']['corpType'] == 'PPR'


def test_payment_data_no_client_ref(client, jwt):
    """Assert that the payment-request body content is as expected with no client reference id."""
    # no setup
    # test
    data = SBCPaymentClient.create_payment_data(TransactionTypes.SEARCH.value, 1, '200000000', None)

    # check
    assert data
    assert data['filingInfo']['filingIdentifier'] == '200000000'
    assert 'folioNumber' not in data['filingInfo']
    assert len(data['filingInfo']['filingTypes']) == 1
    assert data['filingInfo']['filingTypes'][0]['quantity'] == 1
    assert data['filingInfo']['filingTypes'][0]['filingTypeCode'] == 'SERCH'
    assert data['businessInfo']['corpType'] == 'PPR'


def test_payment_data_no_trans_id_or_client_ref(client, jwt):
    """Assert that the payment-request body is as expected with no client reference id and no transaction id."""
    # no setup
    # test
    data = SBCPaymentClient.create_payment_data(TransactionTypes.SEARCH.value, 1, None, None)

    # check
    assert data
    assert 'filingIdentifier' not in data['filingInfo']
    assert 'folioNumber' not in data['filingInfo']
    assert len(data['filingInfo']['filingTypes']) == 1
    assert data['filingInfo']['filingTypes'][0]['quantity'] == 1
    assert data['filingInfo']['filingTypes'][0]['filingTypeCode'] == 'SERCH'
    assert data['businessInfo']['corpType'] == 'PPR'


def test_client_search_mock(client, jwt):
    """Assert that a pay-api client works as expected with the mock service endpoint."""
    # setup
    token = helper_create_jwt(jwt, [PPR_ROLE])
    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345')
    pay_client.api_url = MOCK_URL_NO_KEY

    # test
    pay_data = pay_client.create_payment(TransactionTypes.SEARCH.value, 1, '200000001', 'UT-PAY-SEARCH-01')

    # print(pay_data)
    # check
    assert pay_data
    assert pay_data['invoiceId']
    assert pay_data['receipt']


def test_client_search_pay_details_mock(client, jwt):
    """Assert that a pay-api client with payment details works as expected with the mock service endpoint."""
    # setup
    token = helper_create_jwt(jwt, [PPR_ROLE])
    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345', details=PAY_DETAILS_SEARCH)
    pay_client.api_url = MOCK_URL_NO_KEY

    # test
    pay_data = pay_client.create_payment(TransactionTypes.SEARCH.value, 1, '200000001', 'UT-PAY-SEARCH-01')

    # print(pay_data)
    # check
    assert pay_data
    assert pay_data['invoiceId']
    assert pay_data['receipt']


def test_client_exception(client, jwt):
    """Assert that the pay-api client works as expected with an unuathorized exception."""
    # setup
    token = helper_create_jwt(jwt, [PPR_ROLE])
    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345')
    pay_client.api_url = MOCK_URL

    # test
    with pytest.raises(ApiRequestError) as request_err:
        pay_client.create_payment(TransactionTypes.SEARCH.value, 1, '200000001', 'UT-PAY-SEARCH-01')

    assert request_err


def test_payment_search_mock(client, jwt):
    """Assert that a pay-api search payment request works as expected with the mock service endpoint."""
    # setup
    token = helper_create_jwt(jwt, [PPR_ROLE])
    payment = Payment(jwt=token, account_id='PS12345')
    payment.api_url = MOCK_URL_NO_KEY

    # test
    pay_data = payment.create_payment(TransactionTypes.SEARCH.value, 1, '200000001', 'UT-PAY-SEARCH-01')
    # print(pay_data)
    # check
    assert pay_data
    assert pay_data['invoiceId']
    assert pay_data['receipt']


def test_payment_with_details_search_mock(client, jwt):
    """Assert that a pay-api search payment request with details works as expected with the mock service endpoint."""
    # setup
    token = helper_create_jwt(jwt, [PPR_ROLE])
    payment = Payment(jwt=token, account_id='PS12345', details=PAY_DETAILS_SEARCH)
    payment.api_url = MOCK_URL_NO_KEY

    # test
    pay_data = payment.create_payment(TransactionTypes.SEARCH.value, 1, '200000001', 'UT-PAY-SEARCH-01')
    # print(pay_data)
    # check
    assert pay_data
    assert pay_data['invoiceId']
    assert pay_data['receipt']


def test_payment_exception(client, jwt):
    """Assert that a pay-api payment request works as expected with a 401 exception."""
    # setup
    token = helper_create_jwt(jwt, [PPR_ROLE])
    payment = Payment(jwt=token, account_id='PS12345')
    payment.api_url = MOCK_URL

    # test
    with pytest.raises(SBCPaymentException) as request_err:
        payment.create_payment(TransactionTypes.SEARCH.value, 1, '200000001', 'UT-PAY-SEARCH-01')

    assert request_err
    assert request_err.value.status_code == HTTPStatus.UNAUTHORIZED


def test_payment_apikey(client, jwt):
    """Assert that a gateway pay-api payment request works as expected."""
    # setup
    apikey = os.getenv('PAYMENT_GATEWAY_APIKEY_TEST')
    if apikey:
        token = helper_create_jwt(jwt, [PPR_ROLE])
        payment = Payment(jwt=token, account_id='PS12345', api_key=apikey)
        payment.api_url = MOCK_URL

        # test
        pay_data = payment.create_payment(TransactionTypes.SEARCH.value, 1, '200000001', 'UT-PAY-SEARCH-01')
        print(pay_data)
        # check
        assert pay_data
        assert pay_data['invoiceId']
        assert pay_data['receipt']


def test_sa_get_token(client, jwt):
    """Assert that an OIDC get token request with valid SA credentials works as expected."""
    # setup
    if is_ci_testing():
        return
    token = helper_create_jwt(jwt, [PPR_ROLE])
    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345')

    # test
    jwt = pay_client.get_sa_token()

    # check
    assert jwt
    assert len(jwt) > 0


@pytest.mark.parametrize('valid, filing_type, pay_method, pay_status', TEST_PAY_METHOD_STATUS)
def test_verify_pay_status(session, client, jwt, valid, filing_type, pay_method, pay_status):
    """Assert that checking the response status works as expected."""
    token = helper_create_jwt(jwt, [PPR_ROLE])
    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345')
    req_json = copy.deepcopy(PAYMENT_REQUEST_TEMPLATE)
    req_json["filingInfo"]["filingTypes"][0]["filingTypeCode"] = filing_type
    result = pay_client.valid_payment_status(pay_method, pay_status, req_json)
    assert result == valid


def is_ci_testing() -> bool:
    """Check unit test environment: exclude most reports for CI testing."""
    return  current_app.config.get("DEPLOYMENT_ENV", "testing") == "testing"


# def test_refund(client, jwt):
#    """Assert that a payment refund works as expected: requires a valid invoice id."""
#    # setup
#    token = helper_create_jwt(jwt, [PPR_ROLE])
#    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345')
#
    # test
#    refund_response = pay_client.cancel_payment(9628)
#
    # check
#    print(refund_response)
#    assert refund_response is None
