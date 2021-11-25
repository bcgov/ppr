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
import copy
import json
from enum import Enum
from functools import wraps

import requests
from flask import current_app

from ppr_api.services.payment import TransactionTypes


MSG_CLIENT_CREDENTIALS_REQ_FAILED = 'Client credentials request failed'
MSG_INVALID_HTTP_VERB = 'Invalid HTTP verb'

# Mapping from PPR transaction to Pay API filing type
TRANSACTION_TO_FILING_TYPE = {
    'AMENDMENT': 'FSCHG',
    'AMENDMENT_NO_FEE': 'NCCHG',
    'CHANGE': 'FSCHG',
    'DISCHARGE': 'FSDIS',  # No charge fee.
    'FINANCING_FR': 'FLREG',  # Special flat rate fee for the FR registration type.
    'FINANCING_NO_FEE': 'NCREG',  # No Charge fee for LT, MH, MISCLIEN class, CROWNLIEN class.
    'FINANCING_LIFE_YEAR': 'FSREG',
    'FINANCING_INFINITE': 'INFRG',
    'RENEWAL_LIFE_YEAR': 'FSREN',
    'RENEWAL_INFINITE': 'INFRN',
    'SEARCH': 'SERCH',
    'SEARCH_STAFF': 'SSRCH',
    'SEARCH_STAFF_NO_FEE': 'SSRCH',
    'SEARCH_STAFF_CERTIFIED': 'PPRCD',
    'SEARCH_STAFF_CERTIFIED_NO_FEE': 'PPRCD'
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
    },
    'details': [
        {
            'label': '',
            'value': ''
        }
    ]
}
PAYMENT_STAFF_SEARCH_REQUEST_TEMPLATE = {
    'filingInfo': {
        'folioNumber': '',
        'filingTypes': [
            {
                'filingTypeCode': 'SSRCH',
                'priority': False,
                'futureEffective': False,
                'quantity': 1
            }
        ]
    },
    'businessInfo': {
        'corpType': 'PPR'
    },
    'details': [
        {
            'label': '',
            'value': ''
        }
    ]
}
PAYMENT_CERTIFIED_STAFF_SEARCH_REQUEST_TEMPLATE = {
    'filingInfo': {
        'folioNumber': '',
        'filingTypes': [
            {
                'filingTypeCode': 'SSRCH',
                'priority': False,
                'futureEffective': False,
                'quantity': 1
            },
            {
                'filingTypeCode': 'PPRCD',
                'priority': False,
                'futureEffective': False,
                'quantity': 1
            }
        ]
    },
    'businessInfo': {
        'corpType': 'PPR'
    },
    'details': [
        {
            'label': '',
            'value': ''
        }
    ]
}

PAYMENT_REFUND_TEMPLATE = {
    'reason': 'Immediate transaction rollback.'
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
            self.message = '{msg}: {desc}'.format(msg=message, desc=str(wrapped_err))
        else:
            self.message = message
        # Map HTTP status if the wrapped error has an HTTP status code
        self.status_code = wrapped_err.status if wrapped_err and hasattr(wrapped_err, 'status') else status_code
        super().__init__(self.message)


class ApiRequestError(Exception):
    """Capture api request call error information."""

    def __init__(self, response=None, message='API request failed'):
        """Set up the exception."""
        if response:
            self.status_code = response.status_code
            info = json.loads(response.text)
            self.detail = info.get('detail')
            self.title = info.get('title')
            self.invalid_params = info.get('invalidParams')
            self.message = message + ': ' + str(response.statuscode) + ': ' + info
        else:
            self.message = message

        super().__init__(self.message)


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

    def __init__(self, jwt=None, account_id=None, api_key=None, details=None):
        """Set the API URL from the env variables PAYMENT_SVC_PREFIX and PAYMENT_SVC_URL."""
        service_url = current_app.config.get('PAYMENT_SVC_URL')
        self.api_url = service_url + '/' if service_url[-1] != '/' else service_url
        self.jwt = jwt
        self.account_id = account_id
        self.api_key = api_key
        if details and 'label' in details and 'value' in details:
            self.detail_label = details['label']
            self.detail_value = details['value']
        else:
            self.detail_label = None
            self.detail_value = None

    def call_api(self,  # pylint: disable=too-many-arguments
                 method,
                 relative_path,
                 data=None,
                 token=None,
                 include_account: bool = True):
        """Call the Pay API."""
        try:
            headers = {
                'Authorization': 'Bearer ' + token if token is not None else 'Bearer ' + self.jwt,
                'Content-Type': 'application/json'
            }
            if include_account and self.account_id:
                headers['Account-Id'] = self.account_id
            if self.api_key:
                headers['x-apikey'] = self.api_key

            # current_app.logger.debug(json.dumps(headers))
            url = self.api_url + relative_path
            # current_app.logger.debug(method.value + ' url=' + url)
            if data:
                # current_app.logger.debug(json.dumps(data))
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
            if not response.ok:
                raise ApiRequestError(response, str(response.status_code) + ': ' + response.text)

            return json.loads(response.text)

        except (ApiRequestError) as err:
            current_app.logger.error(err.message)
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

    @staticmethod
    def create_payment_staff_search_data(transaction_info, client_reference_id=None):
        """Build the staff search payment-request body formatted as JSON."""
        data = copy.deepcopy(PAYMENT_STAFF_SEARCH_REQUEST_TEMPLATE)
        if 'certified' in transaction_info and transaction_info['certified']:
            data = copy.deepcopy(PAYMENT_CERTIFIED_STAFF_SEARCH_REQUEST_TEMPLATE)
        if transaction_info['transactionType'] in (TransactionTypes.SEARCH_STAFF_CERTIFIED_NO_FEE.value,
                                                   TransactionTypes.SEARCH_STAFF_NO_FEE.value):
            data['filingInfo']['filingTypes'][0]['waiveFees'] = True
            if transaction_info['transactionType'] == TransactionTypes.SEARCH_STAFF_CERTIFIED_NO_FEE.value:
                data['filingInfo']['filingTypes'][1]['waiveFees'] = True

        # set up FAS payment
        if 'routingSlipNumber' in transaction_info:
            account_info = {
                'routingSlip': transaction_info['routingSlipNumber']
            }
            data['accountInfo'] = account_info
        # setup BCOL account payment
        elif 'bcolAccountNumber' in transaction_info:
            account_info = {
                'bcolAccountNumber': transaction_info['bcolAccountNumber']
            }
            if 'datNumber' in transaction_info:
                account_info['datNumber'] = transaction_info['datNumber']
            data['accountInfo'] = account_info

        if client_reference_id:
            data['filingInfo']['folioNumber'] = client_reference_id
        else:
            del data['filingInfo']['folioNumber']

        return data

    def create_payment(self, transaction_type, quantity=1, ppr_id=None, client_reference_id=None):
        """Submit a payment request for the PPR API transaction."""
        data = SBCPaymentClient.create_payment_data(transaction_type, quantity, ppr_id, client_reference_id)
        if self.detail_label and self.detail_value:
            data['details'][0]['label'] = self.detail_label
            data['details'][0]['value'] = self.detail_value
        else:
            del data['details']
        # current_app.logger.debug('create paymnent payload:')
        # current_app.logger.debug(json.dumps(data))
        invoice_data = self.call_api(HttpVerbs.POST, PATH_PAYMENT, data)
        invoice_id = str(invoice_data['id'])
        receipt_path = self.api_url.replace('https://', '')
        receipt_path = receipt_path[receipt_path.find('/'): None] + PATH_RECEIPT.format(invoice_id=invoice_id)
        # Return the pay reference to include in the API response.
        pay_reference = {
            'invoiceId': invoice_id,
            'receipt': receipt_path
        }

        return pay_reference

    def create_payment_staff_search(self, transaction_info, client_reference_id=None):
        """Submit a staff search payment request for the PPR API transaction."""
        data = SBCPaymentClient.create_payment_staff_search_data(transaction_info, client_reference_id)
        if self.detail_label and self.detail_value:
            data['details'][0]['label'] = self.detail_label
            data['details'][0]['value'] = self.detail_value
        else:
            del data['details']
        current_app.logger.debug('staff search create payment payload for account: ' + self.account_id)
        current_app.logger.debug(json.dumps(data))
        # self.account_id = None
        invoice_data = self.call_api(HttpVerbs.POST, PATH_PAYMENT, data, include_account=False)
        return SBCPaymentClient.build_pay_reference(invoice_data, self.api_url)

    def cancel_payment(self, invoice_id):
        """Immediately cancel or refund the transaction payment as a state rollback."""
        # Payment status does not matter with immediate refunds: always use the refund endpoint.
        current_app.logger.info('Calling pay api to refund payment')
        request_path = PATH_REFUND.format(invoice_id=invoice_id)
        return self.call_api(HttpVerbs.POST,
                             request_path,
                             data=PAYMENT_REFUND_TEMPLATE,
                             token=SBCPaymentClient.get_sa_token())

    def get_payment(self, invoice_id):
        """Fetch the current state of the payment invoice."""
        request_path = PATH_INVOICE.format(invoice_id=invoice_id)
        return self.call_api(HttpVerbs.GET, request_path)

    @staticmethod
    def get_sa_token():
        """Refunds must be submitted with a PPR service account token. Request one from the OIDC service."""
        oidc_token_url = current_app.config.get('JWT_OIDC_TOKEN_URL')
        client_id = current_app.config.get('ACCOUNT_SVC_CLIENT_ID')
        client_secret = current_app.config.get('ACCOUNT_SVC_CLIENT_SECRET')
        current_app.logger.info(f'Calling OIDC api to get token: URL = {oidc_token_url}, client_id={client_id}.')
        try:
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = f'grant_type=client_credentials&scope=openid&client_id={client_id}&client_secret={client_secret}'
            response = requests.request(
                HttpVerbs.POST.value,
                oidc_token_url,
                data=data,
                params=None,
                headers=headers
            )

            if not response or not response.ok:
                raise ApiRequestError(response)

            response_json = json.loads(response.text)
            token = response_json['access_token']
            current_app.logger.info('Have new sa token from OIDC.')
            return token

        except (ApiRequestError) as err:
            current_app.logger.error(err.message)
            raise err

    @staticmethod
    def build_pay_reference(invoice_data, api_url: str):
        """Build a payment reference from the pay api response invoice info."""
        invoice_id = str(invoice_data['id'])
        receipt_path = api_url.replace('https://', '')
        receipt_path = receipt_path[receipt_path.find('/'): None] + PATH_RECEIPT.format(invoice_id=invoice_id)
        # Return the pay reference to include in the API response.
        pay_reference = {
            'invoiceId': invoice_id,
            'receipt': receipt_path
        }

        return pay_reference
