# Copyright © 2021 Province of British Columbia
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

# pylint: disable=too-few-public-methods

"""The simple pay-api client is defined here."""
from enum import Enum
from functools import wraps
import json
import copy
import os

from flask import current_app

import requests

# Follow env variable names from other API's
# Service endpoint with or without trailing backslash.
PAYMENT_SVC_URL = os.getenv('PAYMENT_SVC_URL')
PAYMENT_SVC_PREFIX = os.getenv('PAYMENT_SVC_PREFIX', 'api/v1/')


MSG_CLIENT_CREDENTIALS_REQ_FAILED = 'Client credentials request failed'
MSG_INVALID_HTTP_VERB = 'Invalid HTTP verb'

# Mapping from PPR transaction to Pay API filing type
TRANSACTION_TO_FILING_TYPE = {
    'AMENDMENT': '',
    'CHANGE': '',
    'DISCHARGE': '',
    'FINANCING_LIFE_YEAR': 'FSREG',
    'FINANCING_INFINITE': 'INFRG',
    'RENEWAL_LIFE_YEAR': '',
    'SEARCH': 'SERCH'
}

PAYMENT_REQUEST_TEMPLATE = {
    'filingInfo': {
        'filingIdentifier': '',
        'folioNumber': '',
        'filingTypes': [
            {
                'filingTypeCode': '',
                'priority': False,
                'futureEffective': False,
                'quantity': 1
            }
        ]
    },
    'businessInfo': {
        'corpType': 'PPR'
    }
}

PATH_PAYMENT = 'payment-requests'
PATH_REFUND = 'payment-requests/{invoice_id}/refunds'
PATH_INVOICE = 'payment-requests/{invoice_id}'
PATH_RECEIPT = 'payment-requests/{invoice_id}/receipts'

STATUS_COMPLETED = 'COMPLETED'
STATUS_CREATED = 'CREATED'
STATUS_PAID = 'PAID'
STATUS_APPROVED = 'APPROVED'


class ApiClientException(Exception):
    """Capture api request call error information."""

    def __init__(self, wrapped_err=None, body=None, message='Exception', status_code=500):
        """Set up the exception."""
        self.body = body
        self.err = wrapped_err
        if wrapped_err:
            self.message = '{msg}\r\n\r\n{desc}'.format(msg=message, desc=str(wrapped_err))
        else:
            self.message = message
        # Map HTTP status if the wrapped error has an HTTP status code
        self.status_code = wrapped_err.status if wrapped_err and hasattr(wrapped_err, 'status') else status_code
        super().__init__(self.message)


class ApiRequestError(Exception):
    """Capture api request call error information."""

    def __init__(self, response=None, message='API request failed'):
        """Set up the exception."""
        self.status_code = response.status_code
        info = json.loads(response.text)
        self.detail = detail = info.get('detail')
        self.title = title = info.get('title')
        self.invalid_params = info.get('invalidParams')

        error_msg = None
        if title and detail and (title != detail):
            error_msg = '{title}: {detail}'.format(title=self.title, detail=self.detail)
        if title and not detail or (title and title == detail):
            error_msg = '{title}'.format(title=title)
        else:
            error_msg = message

        super().__init__(error_msg)


class HttpVerbs(Enum):
    """Enumeration of HTTP verbs."""

    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'
    PATCH = 'patch'
    OPTIONS = 'options'
    HEAD = 'head'


class BaseClient:
    """Base class for common api call properties and functions."""

    def __init__(self, jwt=None, account_id=None, api_key=None):
        """Set the API URL from the env variables PAYMENT_SVC_PREFIX and PAYMENT_SVC_URL."""
        self.api_prefix = PAYMENT_SVC_PREFIX + '/' if PAYMENT_SVC_PREFIX[-1] != '/' else PAYMENT_SVC_PREFIX
        self.api_url = PAYMENT_SVC_URL + '/' if PAYMENT_SVC_URL[-1] != '/' else PAYMENT_SVC_URL
        self.api_url += self.api_prefix
        self.jwt = jwt
        self.account_id = account_id
        self.api_key = api_key

    def call_api(self, method, relative_path, data=None):
        """Call the Pay API."""
        try:
            headers = {
                'Authorization': 'Bearer ' + self.jwt,
                'Content-Type': 'application/json'
            }
            if self.account_id:
                headers['Account-Id'] = self.account_id
            if self.api_key:
                headers['x-apikey'] = self.api_key

            url = self.api_url + relative_path
            # current_app.logger.debug('url=' + url)
            if data:
                response = requests.request(
                    method.value,
                    url,
                    params=None,
                    json=data,
                    headers=headers
                )
            else:
                response = requests.request(
                    method.value,
                    url,
                    params=None,
                    headers=headers
                )

            if response:
                current_app.logger.info('Account ' + self.account_id + ' pay api response=' + response.text)
            if not response or not response.ok:
                raise ApiRequestError(response)

            return json.loads(response.text)

        except (ApiRequestError) as err:
            current_app.logger.error(repr(err))
            raise err


class SBCPaymentClient(BaseClient):
    """Pay API client implementation."""

    @staticmethod
    def create_payment_data(transaction_type, quantity=1, ppr_id=None, client_reference_id=None):
        """Build the payment-request body formatted as JSON."""
        data = copy.deepcopy(PAYMENT_REQUEST_TEMPLATE)
        filing_type = TRANSACTION_TO_FILING_TYPE[transaction_type]
        data['filingInfo']['filingTypes'][0]['filingTypeCode'] = filing_type
        if quantity != 1:
            data['filingInfo']['filingTypes'][0]['quantity'] = quantity
        if ppr_id:
            data['filingInfo']['filingIdentifier'] = ppr_id
        else:
            del data['filingInfo']['filingIdentifier']

        if client_reference_id:
            data['filingInfo']['folioNumber'] = client_reference_id
        else:
            del data['filingInfo']['folioNumber']

        return data

    def create_payment(self, transaction_type, quantity=1, ppr_id=None, client_reference_id=None):
        """Submit a payment request for the PPR API transaction."""
        data = SBCPaymentClient.create_payment_data(transaction_type, quantity, ppr_id, client_reference_id)
        invoice_data = self.call_api(HttpVerbs.POST, PATH_PAYMENT, data)
        invoice_id = str(invoice_data['id'])
        receipt_path = '/' + self.api_prefix + PATH_RECEIPT.format(invoice_id=invoice_id)
        # Return the pay reference to include in the API response.
        pay_reference = {
            'invoiceId': invoice_id,
            'receipt': receipt_path
        }

        return pay_reference

    def cancel_payment(self, invoice_id):
        """Immediately cancel or refund the transaction payment as a state rollback."""
        invoice_data = self.get_payment(invoice_id)

        if invoice_data['statusCode'] == STATUS_PAID:
            current_app.logger.info('Calling pay api to refund payment')
            return self.refund_payment(invoice_id, invoice_data)

        if invoice_data['statusCode'] in (STATUS_APPROVED, STATUS_CREATED, STATUS_COMPLETED):
            current_app.logger.info('Calling pay api to cancel payment')
            request_path = PATH_INVOICE.format(invoice_id=invoice_id)
            return self.call_api(HttpVerbs.DELETE, request_path)

        return None

    def get_payment(self, invoice_id):
        """Fetch the current state of the payment invoice."""
        request_path = PATH_INVOICE.format(invoice_id=invoice_id)
        return self.call_api(HttpVerbs.GET, request_path)

    def refund_payment(self, invoice_id, invoice_data):
        """Refund the transaction payment. Invoice_data returned by get_payment."""
        request_path = PATH_REFUND.format(invoice_id=invoice_id)
        return self.call_api(HttpVerbs.POST, request_path, data=invoice_data)
