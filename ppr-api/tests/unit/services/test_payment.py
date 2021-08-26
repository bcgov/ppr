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
import json
import os
from http import HTTPStatus

import pytest

from ppr_api.services.payment.client import SBCPaymentClient, ApiRequestError
from ppr_api.services.payment.payment import Payment, TransactionTypes
from ppr_api.services.payment.exceptions import SBCPaymentException
from ppr_api.services.authz import PPR_ROLE
from tests.unit.services.utils import helper_create_jwt


MOCK_URL_NO_KEY = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/pay/api/v1/'
MOCK_URL = 'https://bcregistry-bcregistry-mock.apigee.net/pay/api/v1/'
PAY_DETAILS_SEARCH = {
    'label': 'Search by SERIAL_NUMBER',
    'value': '123456789'
}
# testdata pattern is ({pay_trans_type}, {quantity}, {filing_type})
TEST_PAY_TYPE_FILING_TYPE = [
    (TransactionTypes.FINANCING_LIFE_YEAR.value, 5, 'FSREG'),
    (TransactionTypes.SEARCH.value, 1, 'SERCH'),
    (TransactionTypes.AMENDMENT.value, 1, 'FSCHG'),
    (TransactionTypes.CHANGE.value, 1, 'FSCHG'),
    (TransactionTypes.DISCHARGE.value, 1, 'FSDCH'),
    (TransactionTypes.FINANCING_FR.value, 1, 'FLREG'),
    (TransactionTypes.FINANCING_NO_FEE.value, 1, 'NCREG'),
    (TransactionTypes.FINANCING_INFINITE.value, 1, 'INFRG'),
    (TransactionTypes.RENEWAL_INFINITE.value, 1, 'INFRN'),
    (TransactionTypes.RENEWAL_LIFE_YEAR.value, 3, 'FSREN')
]


@pytest.mark.parametrize('pay_trans_type,quantity,filing_type', TEST_PAY_TYPE_FILING_TYPE)
def test_payment_filing_type(client, jwt, pay_trans_type, quantity, filing_type):
    """Assert that the payment-request body filing type is as expected for a pay transaction type."""
    # setup

    # test
    data = SBCPaymentClient.create_payment_data(pay_trans_type, quantity, '200000000', 'UT-PAY-0001')
    # check
    assert data
    assert data['filingInfo']['filingIdentifier'] == '200000000'
    assert data['filingInfo']['folioNumber'] == 'UT-PAY-0001'
    assert len(data['filingInfo']['filingTypes']) == 1
    assert data['filingInfo']['filingTypes'][0]['quantity'] == quantity
    assert data['filingInfo']['filingTypes'][0]['filingTypeCode'] == filing_type
    assert data['businessInfo']['corpType'] == 'PPR'


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

    print(pay_data)
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

    print(pay_data)
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
    print(pay_data)
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
    print(pay_data)
    # check
    assert pay_data
    assert pay_data['invoiceId']
    assert pay_data['receipt']


def test_payment_exception(client, jwt):
    """Assert that a pay-api payment request works as expected with a 500 exception."""
    # setup
    token = helper_create_jwt(jwt, [PPR_ROLE])
    payment = Payment(jwt=token, account_id='PS12345')
    payment.api_url = MOCK_URL

    # test
    with pytest.raises(SBCPaymentException) as request_err:
        payment.create_payment(TransactionTypes.SEARCH.value, 1, '200000001', 'UT-PAY-SEARCH-01')

    assert request_err
    assert request_err.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR


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
    token = helper_create_jwt(jwt, [PPR_ROLE])
    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345')

    # test
    jwt = pay_client.get_sa_token()

    # check
    assert jwt
    assert len(jwt) > 0


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
