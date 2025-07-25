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

from flask import current_app
import pytest

from mhr_api.services.payment.client import (
    ApiRequestError,
    CC_REQUEST_PAYMENT_INFO,
    SBCPaymentClient,
    TRANSACTION_TO_FILING_TYPE
)
from mhr_api.services.payment import  PaymentMethods, StatusCodes, TransactionTypes
from mhr_api.services.payment.payment import Payment
from mhr_api.services.payment.exceptions import SBCPaymentException
from mhr_api.services.authz import MHR_ROLE, STAFF_ROLE
from tests.unit.services.utils import helper_create_jwt


MOCK_URL_NO_KEY = 'https://test.api.connect.gov.bc.ca/mockTarget/pay/api/v1/'
MOCK_URL = 'https://test.api.connect.gov.bc.ca/pay-dev/api/v1/'
PAY_DETAILS_SEARCH = {
    'label': 'Search by SERIAL_NUMBER',
    'value': '123456789'
}
PAY_DETAILS_REGISTRATION = {
    'label': 'MH Registration Type:',
    'value': 'New MH Registration'
}
PAY_DETAILS_CC = {
    'label': 'CC TEST',
    'value': 'UNIT TESTING',
    'ccPayment': True
}
SELECT_MHR_ONLY = [
    {'mhrNumber': '022911', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
     'homeLocation': 'FORT NELSON', 'includeLienInfo': False, 'serialNumber': '2427',
     'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
     'ownerName': {'first': 'PRITNAM', 'last': 'SANDHU'}}
]
SELECT_COMBO_ONLY = [
    {'mhrNumber': '022911', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
     'homeLocation': 'FORT NELSON', 'includeLienInfo': True, 'serialNumber': '2427',
     'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
     'ownerName': {'first': 'PRITNAM', 'last': 'SANDHU'}}
]
SELECT_BOTH = [
    {
        'baseInformation': {
            'make': 'FLASHBACK',
            'model': '',
            'year': 1984
        },
        'createDateTime': '1995-11-14T00:00:01+00:00',
        'homeLocation': 'SICAMOUS',
        'mhrNumber': '074026',
        'includeLienInfo': False,
        'ownerName': {
            'first': 'DAVID',
            'last': 'HAMM',
            'middle': 'ABRAM'
        },
        'serialNumber': '117',
        'status': 'ACTIVE'
    },
    {
        'baseInformation': {
            'make': '3 BEDROOM',
            'model': '',
            'year': 1973
        },
        'createDateTime': '1995-11-14T00:00:01+00:00',
        'homeLocation': 'INVERMERE',
        'mhrNumber': '024289',
        'includeLienInfo': True,
        'ownerName': {
            'first': 'DAVID',
            'last': 'HAMM',
            'middle': 'WAYNE'
        },
        'serialNumber': '68MA0970',
        'status': 'ACTIVE'
    }
]
PAYMENT_REQUEST_TEMPLATE = {
    "filingInfo": {
        "filingIdentifier": "",
        "folioNumber": "",
        "filingTypes": [{"filingTypeCode": "", "priority": False, "futureEffective": False, "quantity": 1}],
    },
    "businessInfo": {"corpType": "MHR"},
    "details": [{"label": "", "value": ""}],
}
# testdata pattern is ({valid}, {filing_type}, {pay_method}, {pay_status})
TEST_PAY_METHOD_STATUS = [
    (True, 'MSRCH', PaymentMethods.DRAWDOWN.value, StatusCodes.COMPLETED.value),
    (True, 'CSRCH', PaymentMethods.EJV.value, StatusCodes.COMPLETED.value),
    (True, 'MSRCS', PaymentMethods.PAD.value, StatusCodes.COMPLETED.value),
    (True, 'CSRCS', PaymentMethods.INTERNAL.value, StatusCodes.COMPLETED.value),
    (True, 'TRAPP', PaymentMethods.DRAWDOWN.value, StatusCodes.APPROVED.value),
    (True, 'INREG', PaymentMethods.EJV.value, StatusCodes.APPROVED.value),
    (True, 'NTTRF', PaymentMethods.PAD.value, StatusCodes.APPROVED.value),
    (True, 'EXEMP', PaymentMethods.INTERNAL.value, StatusCodes.APPROVED.value),
    (True, 'TRAPP', PaymentMethods.DRAWDOWN.value, StatusCodes.PAID.value),
    (True, 'INREG', PaymentMethods.EJV.value, StatusCodes.PAID.value),
    (True, 'NTTRF', PaymentMethods.PAD.value, StatusCodes.PAID.value),
    (True, 'EXEMP', PaymentMethods.INTERNAL.value, StatusCodes.PAID.value),
    (True, 'TRAPP', PaymentMethods.CC.value, StatusCodes.CREATED.value),
    (True, 'INREG', PaymentMethods.CC.value, StatusCodes.CREATED.value),
    (True, 'NTTRF', PaymentMethods.CC.value, StatusCodes.CREATED.value),
    (True, 'EXEMP', PaymentMethods.DIRECT_PAY.value, StatusCodes.CREATED.value),
    (True, 'TRAPP', PaymentMethods.DIRECT_PAY.value, StatusCodes.CREATED.value),
    (True, 'INREG', PaymentMethods.DIRECT_PAY.value, StatusCodes.CREATED.value),
    (True, 'NTTRF', PaymentMethods.DIRECT_PAY.value, StatusCodes.CREATED.value),
    (True, 'EXEMP', PaymentMethods.DIRECT_PAY.value, StatusCodes.CREATED.value),
    (True, 'MSRCH', PaymentMethods.DIRECT_PAY.value, StatusCodes.CREATED.value),
    (True, 'CSRCH', PaymentMethods.DIRECT_PAY.value, StatusCodes.CREATED.value),
    (True, 'MSRCS', PaymentMethods.DIRECT_PAY.value, StatusCodes.CREATED.value),
    (True, 'CSRCS', PaymentMethods.DIRECT_PAY.value, StatusCodes.CREATED.value),
    (True, 'MSRCH', PaymentMethods.CC.value, StatusCodes.CREATED.value),
    (True, 'CSRCH', PaymentMethods.CC.value, StatusCodes.CREATED.value),
    (True, 'MSRCS', PaymentMethods.CC.value, StatusCodes.CREATED.value),
    (True, 'CSRCS', PaymentMethods.CC.value, StatusCodes.CREATED.value),
]
# testdata pattern is ({filing_type}, {selection}, {staff})
TEST_PAY_TYPE_FILING_TYPE_SEARCH = [
    ('MSRCH', SELECT_MHR_ONLY, False),
    ('CSRCH', SELECT_COMBO_ONLY, False),
    ('MSRCS', SELECT_MHR_ONLY, True),
    ('CSRCS', SELECT_COMBO_ONLY, True)
]
# testdata pattern is ({desc}, {selection}, {trans_id}, {client_id}, {mhr_count}, {combo_count}, {staff})
TEST_PAYMENT_DATA_SEARCH = [
    ('Search MHR', SELECT_MHR_ONLY, '1234', 'UT-00001', 1, 0, False),
    ('Search Combo', SELECT_COMBO_ONLY, '1234', 'UT-00001', 0, 1, False),
    ('Search Both', SELECT_BOTH, '1234', 'UT-00001', 1, 1, False),
    ('Search No Trans ID', SELECT_MHR_ONLY, None, 'UT-00001', 1, 0, False),
    ('Search No Client Ref', SELECT_MHR_ONLY, '1234', None, 1, 0, False),
    ('Search No Trans ID or Client Ref', SELECT_MHR_ONLY, None, None, 1, 0, False),
    ('Search Staff MHR', SELECT_MHR_ONLY, '1234', 'UT-00001', 1, 0, True),
    ('Search Staff Combo', SELECT_COMBO_ONLY, '1234', 'UT-00001', 0, 1, True),
    ('Search Staff Both', SELECT_BOTH, '1234', 'UT-00001', 1, 1, True)
]
# testdata pattern is ({selection}, {routingSlip}, {bcolNumber}, {datNumber}, {waiveFees}, {priority}, {certified})
TEST_PAY_STAFF_SEARCH = [
    (SELECT_MHR_ONLY, '12345', None, None, False, False, False),
    (SELECT_MHR_ONLY, '12345', None, None, False, True, False),
    (SELECT_MHR_ONLY, '12345', None, None, False, False, True),
    (SELECT_MHR_ONLY, '12345', None, None, False, True, True),
    (SELECT_MHR_ONLY, None, '62345', None, False, False, False),
    (SELECT_MHR_ONLY, None, '62345', '72345', False, False, False),
    (SELECT_MHR_ONLY, None, None, None, True, False, False),
    (SELECT_COMBO_ONLY, '12345', None, None, False, False, False),
    (SELECT_COMBO_ONLY, '12345', None, None, False, True, False),
    (SELECT_COMBO_ONLY, None, '62345', None, False, False, False),
    (SELECT_COMBO_ONLY, None, '62345', '72345', False, False, False),
    (SELECT_COMBO_ONLY, None, None, None, True, False, False)
]
# testdata pattern is ({desc}, {selection}, {pay_url}, {details}, {error})
TEST_PAYMENT_MOCK = [
    ('Valid detail', SELECT_MHR_ONLY, MOCK_URL_NO_KEY, PAY_DETAILS_REGISTRATION, False),
    ('Valid no detail', SELECT_MHR_ONLY, MOCK_URL_NO_KEY, None, False),
    ('Unauthorized', SELECT_MHR_ONLY, MOCK_URL, None, True)
]
# testdata pattern is ({desc}, {reg_type}, {trans_id}, {client_id}, {quantity}, cc)
TEST_PAYMENT_DATA = [
    ('MHR Registration', TransactionTypes.REGISTRATION, '1234', 'UT-00001', 1, False),
    ('MHR Registration no client id', TransactionTypes.REGISTRATION, '1234', None, 1, False),
    ('MHR Registration no trans id', TransactionTypes.REGISTRATION, None, 'UT-00001', 1, False),
    ('MHR Transfer', TransactionTypes.TRANSFER, '1234', 'UT-00001', 1, False),
    ('MHR Transport Permit', TransactionTypes.TRANSPORT_PERMIT, '1234', 'UT-00001', 1, False),
    ('MHR Transport Permit Extension', TransactionTypes.TRANSPORT_PERMIT_EXT, '1234', 'UT-00001', 1, False),
    ('MHR Decal Replacement', TransactionTypes.DECAL_REPLACE, '1234', 'UT-00001', 1, False),
    ('MHR Unit Note 102', TransactionTypes.UNIT_NOTE_102, '1234', 'UT-00001', 1, False),
    ('MHR Unit Note TAXN', TransactionTypes.UNIT_NOTE_TAXN, '1234', 'UT-00001', 1, False),
    ('MHR Unit Note Other', TransactionTypes.UNIT_NOTE_OTHER, '1234', 'UT-00001', 1, False),
    ('MHR Registration CC', TransactionTypes.REGISTRATION, '1234', 'UT-00001', 1, True),
    ('MHR Transfer CC', TransactionTypes.TRANSFER, '1234', 'UT-00001', 1, True),
    ('MHR Transport Permit CC', TransactionTypes.TRANSPORT_PERMIT, '1234', 'UT-00001', 1, True)
]
# testdata pattern is ({type}, {trans_id}, {client_id}, {routingSlip}, {bcolNum}, {datNum}, {waiveFees}, {priority}, {cc})
TEST_PAYMENT_DATA_STAFF = [
    (TransactionTypes.REGISTRATION, '1234', 'UT-00001', '12345', None, None, False, False, False),
    (TransactionTypes.REGISTRATION, '1234', 'UT-00001', '12345', None, None, False, True, False),
    (TransactionTypes.REGISTRATION, '1234', None, None, '62345', None, False, False, False),
    (TransactionTypes.REGISTRATION, None, 'UT-00001', None, '62345', '72345', False, False, False),
    (TransactionTypes.REGISTRATION, '1234', 'UT-00001', None, None, None, True, False, False),
    (TransactionTypes.REGISTRATION, '1234', 'UT-00001', None, None, None, True, False, True),
]
# testdata pattern is ({pay_trans_type}, {pay_filing_type})
TEST_TRANS_TYPE_DATA = [
    (TransactionTypes.UNIT_NOTE, 'CCONT'),
    (TransactionTypes.UNIT_NOTE_OTHER, 'MHROT'),
    (TransactionTypes.ADMIN_RLCHG, 'RLCHG'),
    (TransactionTypes.CORRECTION, 'MHROT'),
    (TransactionTypes.AMENDMENT, 'MHROT'),
    (TransactionTypes.TRANSPORT_PERMIT, 'TRAPP'),
    (TransactionTypes.CANCEL_PERMIT, 'MHROT'),
    (TransactionTypes.AMEND_PERMIT, 'MHROT')
]


@pytest.mark.parametrize('selection,routing_slip,bcol_number,dat_number,waive_fees,priority,certified',
                         TEST_PAY_STAFF_SEARCH)
def test_payment_data_staff_search(client, jwt, selection, routing_slip, bcol_number, dat_number, waive_fees,
                                   priority, certified):
    """Assert that the staff payment payment-request body is as expected for a pay transaction type."""
    transaction_info = {
    }
    if routing_slip:
        transaction_info['routingSlipNumber'] = routing_slip
    if bcol_number:
        transaction_info['bcolAccountNumber'] = bcol_number
    if dat_number:
        transaction_info['datNumber'] = dat_number
    if waive_fees:
        transaction_info['waiveFees'] = True
    if priority:
        transaction_info['priority'] = True
    if certified:
        transaction_info['certified'] = True

    # test
    data = SBCPaymentClient.create_payment_staff_search_data(selection, transaction_info, 'TEST', 'UT-PAY-0001')
    # check
    assert data
    if waive_fees:
        assert data['filingInfo']['filingTypes'][0]['waiveFees']
    else:
        assert 'waiveFees' not in data['filingInfo']['filingTypes'][0]
    assert not data['filingInfo']['filingTypes'][0]['priority']
    if priority and certified:
        assert len(data['filingInfo']['filingTypes']) == 3
        assert data['filingInfo']['filingTypes'][1]['filingTypeCode'] == 'MHRCD'
        assert data['filingInfo']['filingTypes'][2]['filingTypeCode'] == 'PRIMH'
        assert data['filingInfo']['filingTypes'][2]['priority']
    elif certified:
        assert len(data['filingInfo']['filingTypes']) == 2
        assert data['filingInfo']['filingTypes'][1]['filingTypeCode'] == 'MHRCD'
    elif priority:
        assert len(data['filingInfo']['filingTypes']) == 2
        assert data['filingInfo']['filingTypes'][1]['filingTypeCode'] == 'PRIMH'
        assert data['filingInfo']['filingTypes'][1]['priority']
    else:
        assert len(data['filingInfo']['filingTypes']) == 1
    if not routing_slip and not bcol_number:
        assert 'accountInfo' not in data
    elif routing_slip:
        assert 'accountInfo' in data and data['accountInfo']['routingSlip'] == routing_slip
    elif bcol_number:
        assert 'accountInfo' in data and data['accountInfo']['bcolAccountNumber'] == bcol_number
        if dat_number:
            assert data['accountInfo']['datNumber'] == dat_number


@pytest.mark.parametrize('filing_type,selection,staff', TEST_PAY_TYPE_FILING_TYPE_SEARCH)
def test_payment_filing_type_search(client, jwt, filing_type, selection, staff):
    """Assert that the payment-request body filing type is as expected for a pay transaction type."""
    # setup

    # test
    data = SBCPaymentClient.create_payment_search_data(selection, '200000000', 'UT-PAY-0001', staff)
    # check
    assert data
    assert data['filingInfo']['filingIdentifier'] == '200000000'
    assert data['filingInfo']['folioNumber'] == 'UT-PAY-0001'
    assert len(data['filingInfo']['filingTypes']) == 1
    assert data['filingInfo']['filingTypes'][0]['quantity'] == 1
    assert data['filingInfo']['filingTypes'][0]['filingTypeCode'] == filing_type
    assert data['businessInfo']['corpType'] == 'MHR'


@pytest.mark.parametrize('desc,selection,trans_id,client_id,mhr_count,combo_count,staff',TEST_PAYMENT_DATA_SEARCH)
def test_payment_data_search(client, jwt, desc, selection, trans_id, client_id, mhr_count, combo_count, staff):
    """Assert that the payment-request body filing type is as expected for a search transactions."""
    # setup
    data = None
    # test
    data = SBCPaymentClient.create_payment_search_data(selection, trans_id, client_id, staff)
    # check
    assert data
    if trans_id:
        assert data['filingInfo']['filingIdentifier'] == trans_id
    else:
        assert 'filingIdentifier' not in data['filingInfo']
    if client_id:
        assert data['filingInfo']['folioNumber'] == client_id
    else:
        assert 'folioNumber' not in data['filingInfo']

    assert data['businessInfo']['corpType'] == 'MHR'
    assert len(data['filingInfo']['filingTypes']) == (mhr_count + combo_count)
    if mhr_count > 0:
        assert data['filingInfo']['filingTypes'][0]['quantity'] == mhr_count
    elif combo_count > 0 and mhr_count == 0:
        assert data['filingInfo']['filingTypes'][0]['quantity'] == combo_count
    if combo_count > 0 and mhr_count > 0:
        assert data['filingInfo']['filingTypes'][1]['quantity'] == combo_count

    assert data['filingInfo']['filingTypes'][0]['quantity'] == 1


@pytest.mark.parametrize('selection,routing_slip,bcol_number,dat_number,waive_fees,priority,certified',
                         TEST_PAY_STAFF_SEARCH)
def test_payment_staff_search_mock(session, client, jwt, selection, routing_slip, bcol_number, dat_number, waive_fees,
                                   priority, certified):
    """Assert that a pay-api staff search payment request works as expected with the mock service endpoint."""
    # setup
    token = helper_create_jwt(jwt, [MHR_ROLE])
    payment = Payment(jwt=token, account_id='PS12345', details=PAY_DETAILS_SEARCH)
    payment.api_url = MOCK_URL_NO_KEY
    transaction_info = {
        'accountId': '3040'
    }
    if routing_slip:
        transaction_info['routingSlipNumber'] = routing_slip
    if bcol_number:
        transaction_info['bcolAccountNumber'] = bcol_number
    if dat_number:
        transaction_info['datNumber'] = dat_number
    if waive_fees:
        transaction_info['waiveFees'] = True
 
    # test
    pay_data = payment.create_payment_staff_search(selection, transaction_info, 'TEST-MOCK', 'UT-PAY-SEARCH-01')
    # print(pay_data)
    # check
    assert pay_data
    assert pay_data['invoiceId']
    assert pay_data['receipt']


@pytest.mark.parametrize('desc,selection,pay_url,details,error', TEST_PAYMENT_MOCK)
def test_client_search_mock(session, client, jwt, desc, selection, pay_url, details, error):
    """Assert that a pay-api client works as expected with the mock service endpoint."""
    # setup
    token = helper_create_jwt(jwt, [MHR_ROLE])
    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345', details=details)
    pay_client.api_url = pay_url

    # test
    if error:
        with pytest.raises(ApiRequestError) as request_err:
            pay_data = pay_client.create_payment_search(selection, '200000001', 'UT-PAY-SEARCH-01', False)
    else:
        pay_data = pay_client.create_payment_search(selection, '200000001', 'UT-PAY-SEARCH-01', False)

    # print(pay_data)
    # check
    if error:
        assert request_err
    else:
        assert pay_data
        assert pay_data['invoiceId']
        assert pay_data['receipt']


@pytest.mark.parametrize('desc,selection,pay_url,details,error', TEST_PAYMENT_MOCK)
def test_payment_search_mock(session, client, jwt, desc, selection, pay_url, details, error):
    """Assert that a pay-api search payment request works as expected with the mock service endpoint."""
    # setup
    token = helper_create_jwt(jwt, [MHR_ROLE])
    payment = Payment(jwt=token, account_id='PS12345', details=details)
    payment.api_url = pay_url

    # test
    if error:
        with pytest.raises(SBCPaymentException) as request_err:
            pay_data = payment.create_payment_search(selection, '200000001', 'UT-PAY-SEARCH-01', False)
    else:
        pay_data = payment.create_payment_search(selection, '200000001', 'UT-PAY-SEARCH-01', False)

    # print(pay_data)
    # check
    if error:
        assert request_err
    else:
        assert pay_data
        assert pay_data['invoiceId']
        assert pay_data['receipt']


@pytest.mark.parametrize('desc,reg_type,trans_id,client_id,quantity,cc', TEST_PAYMENT_DATA)
def test_create_payment_data(session, client, jwt, desc, reg_type, trans_id, client_id, quantity, cc):
    """Assert that the payment-request body setup is as expected for a non staff transactions."""
    # setup
    token = helper_create_jwt(jwt, [MHR_ROLE])
    details: dict = PAY_DETAILS_REGISTRATION if not cc else PAY_DETAILS_CC
    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345', details=details)
    data = pay_client.create_payment_data(reg_type, quantity, trans_id, client_id)
    data = pay_client.update_payload_data(data, trans_id)
    # check
    # current_app.logger.info(data)
    assert data
    if trans_id:
        assert data['filingInfo']['filingIdentifier'] == trans_id
    else:
        assert 'filingIdentifier' not in data['filingInfo']
    if client_id:
        assert data['filingInfo']['folioNumber'] == client_id
    else:
        assert 'folioNumber' not in data['filingInfo']
    assert data['businessInfo']['corpType'] == 'MHR'
    assert len(data['filingInfo']['filingTypes']) == 1
    assert data['filingInfo']['filingTypes'][0]['quantity'] == 1
    if cc:
        assert data.get("paymentInfo") == CC_REQUEST_PAYMENT_INFO
    else:
        assert not data.get("paymentInfo")
    if trans_id:
        assert len(data.get("details")) == 2
        assert data["details"][1].get("value") == trans_id
    else:
        assert len(data.get("details")) == 1


@pytest.mark.parametrize('desc,type,trans_id,client_id,quantity,cc', TEST_PAYMENT_DATA)
def test_client_registration_mock(session, client, jwt, desc, type, trans_id, client_id, quantity, cc):
    """Assert that a pay-api client works as expected with the mock service endpoint."""
    # setup
    token = helper_create_jwt(jwt, [MHR_ROLE])
    details: dict = PAY_DETAILS_REGISTRATION if not cc else PAY_DETAILS_CC
    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345', details=details)
    pay_client.api_url = MOCK_URL_NO_KEY

    # test
    pay_data = pay_client.create_payment(type, quantity, trans_id, client_id, False)

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


@pytest.mark.parametrize('desc,type,trans_id,client_id,quantity,cc', TEST_PAYMENT_DATA)
def test_payment_registration_mock(session, client, jwt, desc, type, trans_id, client_id, quantity, cc):
    """Assert that a pay-api works as expected with the mock service endpoint."""
    # setup
    token = helper_create_jwt(jwt, [MHR_ROLE])
    details: dict = PAY_DETAILS_REGISTRATION if not cc else PAY_DETAILS_CC
    payment = Payment(jwt=token, account_id='PS12345', details=details)
    payment.api_url = MOCK_URL_NO_KEY

    # test
    pay_data = payment.create_payment(type, quantity, trans_id, client_id, False)

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


@pytest.mark.parametrize('type,trans_id,client_id,routing_slip,bcol_num,dat_num,waive_fees,priority,cc',
                         TEST_PAYMENT_DATA_STAFF)
def test_create_payment_data_staff(client, jwt, type, trans_id, client_id, routing_slip, bcol_num, dat_num,
                                   waive_fees, priority, cc):
    """Assert that the staff payment payment-request body is as expected for a pay transaction type."""
    transaction_info = {
        'transactionType': type,
        'quantity': 1,
        'accountId': '3040'
    }
    if routing_slip:
        transaction_info['routingSlipNumber'] = routing_slip
    if bcol_num:
        transaction_info['bcolAccountNumber'] = bcol_num
    if dat_num:
        transaction_info['datNumber'] = dat_num
    if waive_fees:
        transaction_info['waiveFees'] = True
    if priority:
        transaction_info['priority'] = True
    if trans_id:
        transaction_info['transactionId'] = trans_id

    token = helper_create_jwt(jwt, [MHR_ROLE])
    details: dict = PAY_DETAILS_REGISTRATION if not cc else PAY_DETAILS_CC
    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345', details=details)
 
    # test
    data = pay_client.create_payment_staff_data(transaction_info, client_id)
    data = pay_client.update_payload_data(data, transaction_info.get("transactionId"))
    # check
    assert data
    if waive_fees:
        assert data['filingInfo']['filingTypes'][0]['waiveFees']
    else:
        assert 'waiveFees' not in data['filingInfo']['filingTypes'][0]
    assert not data['filingInfo']['filingTypes'][0]['priority']
    if priority:
        assert len(data['filingInfo']['filingTypes']) == 2
        assert data['filingInfo']['filingTypes'][1]['filingTypeCode'] == 'PRIMH'
        assert data['filingInfo']['filingTypes'][1]['priority']
    else:
        assert len(data['filingInfo']['filingTypes']) == 1
    if not routing_slip and not bcol_num:
        assert 'accountInfo' not in data
    elif routing_slip:
        assert 'accountInfo' in data and data['accountInfo']['routingSlip'] == routing_slip
    elif bcol_num:
        assert 'accountInfo' in data and data['accountInfo']['bcolAccountNumber'] == bcol_num
        if dat_num:
            assert data['accountInfo']['datNumber'] == dat_num
    if trans_id:
        assert data['filingInfo']['filingIdentifier'] == trans_id
    else:
        assert 'filingIdentifier' not in data['filingInfo']
    if client_id:
        assert data['filingInfo']['folioNumber'] == client_id
    else:
        assert 'folioNumber' not in data['filingInfo']
    assert data['businessInfo']['corpType'] == 'MHR'
    if cc:
        assert data.get("paymentInfo") == CC_REQUEST_PAYMENT_INFO
    else:
        assert not data.get("paymentInfo")
    if transaction_info.get("transactionId"):
        assert len(data.get("details")) == 2
        assert data["details"][1].get("value") == trans_id
    else:
        assert len(data.get("details")) == 1


@pytest.mark.parametrize('type,trans_id,client_id,routing_slip,bcol_num,dat_num,waive_fees,priority,cc',
                         TEST_PAYMENT_DATA_STAFF)
def test_client_registration_staff_mock(session, client, jwt, type, trans_id, client_id, routing_slip, bcol_num,
                                        dat_num, waive_fees, priority, cc):
    """Assert that a staff pay-api client works as expected with the mock service endpoint."""
    # setup
    token = helper_create_jwt(jwt, [MHR_ROLE, STAFF_ROLE])
    details: dict = PAY_DETAILS_REGISTRATION if not cc else PAY_DETAILS_CC
    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345', details=details)
    pay_client.api_url = MOCK_URL_NO_KEY
    transaction_info = {
        'transactionType': type,
        'quantity': 1,
        'accountId': '3040'
    }
    if routing_slip:
        transaction_info['routingSlipNumber'] = routing_slip
    if bcol_num:
        transaction_info['bcolAccountNumber'] = bcol_num
    if dat_num:
        transaction_info['datNumber'] = dat_num
    if waive_fees:
        transaction_info['waiveFees'] = True
    if priority:
        transaction_info['priority'] = True
    if trans_id:
        transaction_info['transactionId'] = trans_id

    # test
    pay_data = pay_client.create_payment_staff(transaction_info, client_id)

    # print(pay_data)
    # check
    assert pay_data
    assert pay_data['invoiceId']
    assert pay_data['receipt']


@pytest.mark.parametrize('type,trans_id,client_id,routing_slip,bcol_num,dat_num,waive_fees,priority,cc',
                         TEST_PAYMENT_DATA_STAFF)
def test_pay_registration_staff_mock(session, client, jwt, type, trans_id, client_id, routing_slip, bcol_num,
                                     dat_num, waive_fees, priority, cc):
    """Assert that a staff pay-api works as expected with the mock service endpoint."""
    # setup
    token = helper_create_jwt(jwt, [MHR_ROLE, STAFF_ROLE])
    details: dict = PAY_DETAILS_REGISTRATION if not cc else PAY_DETAILS_CC
    payment = Payment(jwt=token, account_id='PS12345', details=details)
    payment.api_url = MOCK_URL_NO_KEY
    transaction_info = {
        'transactionType': type,
        'quantity': 1,
        'accountId': '3040'
    }
    if routing_slip:
        transaction_info['routingSlipNumber'] = routing_slip
    if bcol_num:
        transaction_info['bcolAccountNumber'] = bcol_num
    if dat_num:
        transaction_info['datNumber'] = dat_num
    if waive_fees:
        transaction_info['waiveFees'] = True
    if priority:
        transaction_info['priority'] = True
    if trans_id:
        transaction_info['transactionId'] = trans_id

    # test
    pay_data = payment.create_payment_staff(transaction_info, client_id)

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


def test_payment_apikey(session, client, jwt):
    """Assert that a gateway pay-api payment request works as expected."""
    # setup
    apikey = os.getenv('PAYMENT_GATEWAY_APIKEY_TEST')
    if apikey:
        token = helper_create_jwt(jwt, [MHR_ROLE])
        payment = Payment(jwt=token, account_id='PS12345', api_key=apikey)
        payment.api_url = MOCK_URL

        # test
        pay_data = payment.create_payment_search(SELECT_MHR_ONLY, '200000001', 'UT-PAY-SEARCH-01', False)
        # print(pay_data)
        # check
        assert pay_data
        assert pay_data['invoiceId']
        assert pay_data['receipt']


def test_sa_get_token(session, client, jwt):
    """Assert that an OIDC get token request with valid SA credentials works as expected."""
    # setup
    if is_ci_testing():
        return
    token = helper_create_jwt(jwt, [MHR_ROLE])
    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345')

    # test
    jwt = pay_client.get_sa_token()

    # check
    assert jwt
    assert len(jwt) > 0


@pytest.mark.parametrize('pay_trans_type,filing_type', TEST_TRANS_TYPE_DATA)
def test_transaction_filing_type(session, client, jwt, pay_trans_type, filing_type):
    """Assert that mapping document type to payment transaction and filing types works as expected."""
    trans_filing_type: str = TRANSACTION_TO_FILING_TYPE.get(pay_trans_type)
    assert trans_filing_type == filing_type


@pytest.mark.parametrize('valid, filing_type, pay_method, pay_status', TEST_PAY_METHOD_STATUS)
def test_verify_pay_status(session, client, jwt, valid, filing_type, pay_method, pay_status):
    """Assert that checking the response status works as expected."""
    token = helper_create_jwt(jwt, [MHR_ROLE])
    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345')
    req_json = copy.deepcopy(PAYMENT_REQUEST_TEMPLATE)
    req_json["filingInfo"]["filingTypes"][0]["filingTypeCode"] = filing_type
    result = pay_client.valid_payment_status(pay_method, pay_status, req_json)
    assert result == valid


def is_ci_testing() -> bool:
    """Check unit test environment: exclude most reports for CI testing."""
    return  current_app.config.get("DEPLOYMENT_ENV", "testing") == "testing"
