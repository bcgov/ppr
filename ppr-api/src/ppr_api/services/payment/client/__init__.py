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
from http import HTTPStatus

import requests
from flask import current_app

from ppr_api.services.payment import PaymentMethods, StatusCodes, TransactionTypes
from ppr_api.services.payment.exceptions import SBCPaymentException
from ppr_api.utils.logging import logger

MSG_CLIENT_CREDENTIALS_REQ_FAILED = "Client credentials request failed"
MSG_INVALID_HTTP_VERB = "Invalid HTTP verb"

# Mapping from PPR transaction to Pay API filing type
TRANSACTION_TO_FILING_TYPE = {
    "AMENDMENT": "FSCHG",
    "AMENDMENT_NO_FEE": "NCCHG",
    "CHANGE": "FSCHG",
    "CHANGE_STAFF_PROCESS_FEE": "PRFEEA",
    "DISCHARGE": "FSDIS",  # No charge fee.
    "FINANCING_FR": "FLREG",  # Special flat rate fee for the FR registration type.
    "FINANCING_NO_FEE": "NCREG",  # No Charge fee for LT, MH, MISCLIEN class, CROWNLIEN class.
    "FINANCING_LIFE_YEAR": "FSREG",
    "FINANCING_INFINITE": "INFRG",
    "FINANCING_STAFF_PROCESS_FEE": "PRFEEB",
    "FINANCING_CL": "CLREG",  # Special flat rate fee for the CL registration type.
    "FINANCING_CL_INFINITE": "INFRG",
    "RENEWAL_LIFE_YEAR": "FSREN",
    "RENEWAL_INFINITE": "INFRN",
    "SEARCH": "SERCH",
    "SEARCH_STAFF": "SSRCH",
    "SEARCH_STAFF_NO_FEE": "SSRCH",
    "SEARCH_STAFF_CERTIFIED": "PPRCD",
    "SEARCH_STAFF_CERTIFIED_NO_FEE": "PPRCD",
    "CLIENT_CODE_CHANGE": "SPMUP",
    "CLIENT_CODE_STAFF_NO_FEE": "SSRCH",
}

# Mapping from normal filing type to staff version of filing type
TO_STAFF_FILING_TYPE = {
    "CLREG": "CLRGS",
    "FSCHG": "FSCHS",
    "FLREG": "FLRGS",
    "FSREG": "FSRGS",
    "INFRG": "INFRS",
    "FSREN": "FSRNS",
    "INFRN": "INFNS",
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
PAYMENT_STAFF_SEARCH_REQUEST_TEMPLATE = {
    "filingInfo": {
        "folioNumber": "",
        "filingTypes": [{"filingTypeCode": "SSRCH", "priority": False, "futureEffective": False, "quantity": 1}],
    },
    "businessInfo": {"corpType": "PPR"},
    "details": [{"label": "", "value": ""}],
}
PAYMENT_CERTIFIED_STAFF_SEARCH_REQUEST_TEMPLATE = {
    "filingInfo": {
        "folioNumber": "",
        "filingTypes": [
            {"filingTypeCode": "SSRCH", "priority": False, "futureEffective": False, "quantity": 1},
            {"filingTypeCode": "PPRCD", "priority": False, "futureEffective": False, "quantity": 1},
        ],
    },
    "businessInfo": {"corpType": "PPR"},
    "details": [{"label": "", "value": ""}],
}

PAYMENT_REFUND_TEMPLATE = {"reason": "Immediate transaction rollback."}
CC_REQUEST_PAYMENT_INFO = {"methodOfPayment": "DIRECT_PAY"}
EXCLUDED_CC_FILING_TYPES = []  # ["SERCH", "SSRCH", "PPRCD"]

PATH_PAYMENT = "payment-requests"
PATH_REFUND = "payment-requests/{invoice_id}/refunds"
PATH_INVOICE = "payment-requests/{invoice_id}"
PATH_RECEIPT = "payment-requests/{invoice_id}/receipts"

VALID_PAYMENT_METHOD_CC = [PaymentMethods.CC.value, PaymentMethods.DIRECT_PAY.value]
VALID_RESPONSE_STATUS = [StatusCodes.PAID.value, StatusCodes.APPROVED.value, StatusCodes.COMPLETED.value]
VALID_RESPONSE_STATUS_CC = StatusCodes.CREATED
INVALID_STATUS_JSON = {"status_code": HTTPStatus.PAYMENT_REQUIRED}
INVALID_STATUS_MSG = "Payment request failed: payment method {pay_method} returned invalid status {invoice_status}."


class ApiClientException(Exception):
    """Capture api request call error information."""

    def __init__(self, wrapped_err=None, body=None, message="Exception", status_code=500):
        """Set up the exception."""
        self.body = body
        self.err = wrapped_err
        if wrapped_err:
            self.message = "{msg}: {desc}".format(msg=message, desc=str(wrapped_err))
        else:
            self.message = message
        # Map HTTP status if the wrapped error has an HTTP status code
        self.status_code = wrapped_err.status if wrapped_err and hasattr(wrapped_err, "status") else status_code
        super().__init__(self.message)


class ApiRequestError(Exception):
    """Capture api request call error information."""

    def __init__(self, response=None, message="API request failed"):
        """Set up the exception."""
        if response is not None:
            self.status_code = response.status_code
            try:
                self.json_data = json.loads(response.text)
            except Exception:  # noqa: B902; return nicer default error
                logger.error("Pay api non-JSON response: " + response.text)
                self.json_data = {"message": "Error parsing payment error response as JSON."}
            self.json_data["status_code"] = response.status_code
            self.detail = self.json_data.get("detail", "")
            self.title = self.json_data.get("title", "")
            self.message = str(response.status_code) + ": " + self.detail
        else:
            self.message = message
            self.json_data = None

        super().__init__(self.message)


class HttpVerbs(Enum):
    """Enumeration of HTTP verbs."""

    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    OPTIONS = "options"
    HEAD = "head"


class BaseClient:
    """Base class for common api call properties and functions."""

    def __init__(self, jwt=None, account_id=None, api_key=None, details=None):
        """Set the API URL from the env variables PAYMENT_SVC_PREFIX and PAYMENT_SVC_URL."""
        service_url = current_app.config.get("PAYMENT_SVC_URL")
        self.api_url = service_url + "/" if service_url[-1] != "/" else service_url
        self.jwt = jwt
        self.account_id = account_id
        self.api_key = api_key
        self.cc_payment = False
        if details and "label" in details and "value" in details:
            self.detail_label = details["label"]
            self.detail_value = details["value"]
        else:
            self.detail_label = None
            self.detail_value = None
        if details and "ccPayment" in details:
            self.cc_payment = details.get("ccPayment")

    def valid_payment_status(self, pay_method: str, pay_status: str, data: dict) -> bool:
        """Verify the response status and payment method pair."""
        if pay_method not in VALID_PAYMENT_METHOD_CC and pay_status in VALID_RESPONSE_STATUS:
            return True
        if pay_method in VALID_PAYMENT_METHOD_CC and pay_status == VALID_RESPONSE_STATUS_CC:
            filing_type = data["filingInfo"]["filingTypes"][0].get("filingTypeCode")
            if filing_type not in EXCLUDED_CC_FILING_TYPES:
                return True
            logger.error(f"Filing type {filing_type} not allowed for credit card payments.")
        logger.error(f"Invalid response payload status code {pay_status} for payment method {pay_method}")
        return False

    def call_api(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        method,
        relative_path,
        data=None,
        token=None,
        include_account: bool = True,
    ):
        """Call the Pay API."""
        try:
            headers = {
                "Authorization": "Bearer " + token if token is not None else "Bearer " + self.jwt,
                "Content-Type": "application/json",
            }
            if include_account and self.account_id:
                headers["Account-Id"] = self.account_id
            if self.api_key:
                headers["x-apikey"] = self.api_key
            # logger.debug(json.dumps(headers))
            url = self.api_url + relative_path
            logger.debug(f"Submitting pay-api request {url} for Account-Id={self.account_id}")
            if data:
                # logger.debug(json.dumps(data))
                response = requests.request(method.value, url, params=None, json=data, headers=headers, timeout=20.0)
            else:
                response = requests.request(method.value, url, params=None, headers=headers, timeout=20.0)

            if response is not None:
                if self.account_id:
                    logger.info("Account " + self.account_id + " pay api response=" + response.text)
                else:
                    logger.info("Pay api response=" + response.text)
            if not response.ok:
                raise ApiRequestError(response, str(response.status_code) + ": " + response.text)
            if method == HttpVerbs.DELETE:
                return str(response.status_code)
            response_json = json.loads(response.text)
            pay_method: str = response_json.get("paymentMethod", "")
            invoice_status: str = response_json.get("statusCode", "")
            if method == HttpVerbs.POST and not self.valid_payment_status(pay_method, invoice_status, data):
                logger.error(f"Invalid response payload status code {invoice_status} for payment method {pay_method}")
                msg: str = INVALID_STATUS_MSG.format(pay_method=pay_method, invoice_status=invoice_status)
                error_json = INVALID_STATUS_JSON
                error_json["type"] = pay_method
                error_json["detail"] = msg
                raise SBCPaymentException(msg, error_json)
            return response_json
        except ApiRequestError as err:
            logger.error("call_api error: " + err.message)
            raise err


class SBCPaymentClient(BaseClient):
    """Pay API client implementation."""

    @staticmethod
    def create_payment_data(transaction_type, quantity=1, ppr_id=None, client_reference_id=None, processing_fee=None):
        """Build the payment-request body formatted as JSON."""
        data = copy.deepcopy(PAYMENT_REQUEST_TEMPLATE)
        filing_type = TRANSACTION_TO_FILING_TYPE[transaction_type]
        data["filingInfo"]["filingTypes"][0]["filingTypeCode"] = filing_type
        if quantity != 1:
            data["filingInfo"]["filingTypes"][0]["quantity"] = quantity
        if ppr_id:
            data["filingInfo"]["filingIdentifier"] = ppr_id
        else:
            del data["filingInfo"]["filingIdentifier"]

        if processing_fee:
            # alter fee code to staff fee code
            if filing_type in TO_STAFF_FILING_TYPE:
                data["filingInfo"]["filingTypes"][0]["filingTypeCode"] = TO_STAFF_FILING_TYPE[filing_type]
            # add processing fee item
            processing_filing_type = TRANSACTION_TO_FILING_TYPE[processing_fee]
            data["filingInfo"]["filingTypes"].append(
                {"filingTypeCode": processing_filing_type, "priority": False, "futureEffective": False, "quantity": 1}
            )

        if client_reference_id:
            data["filingInfo"]["folioNumber"] = client_reference_id
        else:
            del data["filingInfo"]["folioNumber"]

        return data

    @staticmethod
    def create_payment_staff_registration_data(transaction_info, client_reference_id=None, processing_fee=None):
        """Build the payment-request body formatted as JSON."""
        data = copy.deepcopy(PAYMENT_REQUEST_TEMPLATE)
        filing_type = TRANSACTION_TO_FILING_TYPE[transaction_info["transactionType"]]
        data["filingInfo"]["filingTypes"][0]["filingTypeCode"] = filing_type
        if transaction_info["feeQuantity"] != 1:
            data["filingInfo"]["filingTypes"][0]["quantity"] = transaction_info["feeQuantity"]
        if "transaction_id" in transaction_info:
            data["filingInfo"]["filingIdentifier"] = transaction_info["transaction_id"]
        else:
            del data["filingInfo"]["filingIdentifier"]

        if processing_fee:
            # alter fee code to staff fee code
            if filing_type in TO_STAFF_FILING_TYPE:
                data["filingInfo"]["filingTypes"][0]["filingTypeCode"] = TO_STAFF_FILING_TYPE[filing_type]
            # add processing fee item
            processing_filing_type = TRANSACTION_TO_FILING_TYPE[processing_fee]
            data["filingInfo"]["filingTypes"].append(
                {"filingTypeCode": processing_filing_type, "priority": False, "futureEffective": False, "quantity": 1}
            )

        if client_reference_id:
            data["filingInfo"]["folioNumber"] = client_reference_id
        else:
            del data["filingInfo"]["folioNumber"]

        if "waiveFees" in transaction_info and transaction_info["waiveFees"]:
            data["filingInfo"]["filingTypes"][0]["waiveFees"] = True
        # set up FAS payment
        elif "routingSlipNumber" in transaction_info:
            account_info = {"routingSlip": transaction_info["routingSlipNumber"]}
            data["accountInfo"] = account_info
        # setup BCOL account payment
        elif "bcolAccountNumber" in transaction_info:
            account_info = {"bcolAccountNumber": transaction_info["bcolAccountNumber"]}
            if "datNumber" in transaction_info:
                account_info["datNumber"] = transaction_info["datNumber"]
            data["accountInfo"] = account_info
        return data

    @staticmethod
    def create_payment_staff_search_data(transaction_info, client_reference_id=None):
        """Build the staff search payment-request body formatted as JSON."""
        data = copy.deepcopy(PAYMENT_STAFF_SEARCH_REQUEST_TEMPLATE)
        if "certified" in transaction_info and transaction_info["certified"]:
            data = copy.deepcopy(PAYMENT_CERTIFIED_STAFF_SEARCH_REQUEST_TEMPLATE)
        if transaction_info["transactionType"] in (
            TransactionTypes.SEARCH_STAFF_CERTIFIED_NO_FEE.value,
            TransactionTypes.SEARCH_STAFF_NO_FEE.value,
        ):
            data["filingInfo"]["filingTypes"][0]["waiveFees"] = True
            if transaction_info["transactionType"] == TransactionTypes.SEARCH_STAFF_CERTIFIED_NO_FEE.value:
                data["filingInfo"]["filingTypes"][1]["waiveFees"] = True

        # set up FAS payment
        if "routingSlipNumber" in transaction_info:
            account_info = {"routingSlip": transaction_info["routingSlipNumber"]}
            data["accountInfo"] = account_info
        # setup BCOL account payment
        elif "bcolAccountNumber" in transaction_info:
            account_info = {"bcolAccountNumber": transaction_info["bcolAccountNumber"]}
            if "datNumber" in transaction_info:
                account_info["datNumber"] = transaction_info["datNumber"]
            data["accountInfo"] = account_info

        if client_reference_id:
            data["filingInfo"]["folioNumber"] = client_reference_id
        else:
            del data["filingInfo"]["folioNumber"]

        return data

    @staticmethod
    def create_payment_staff_client_code_data(transaction_info):
        """Build the payment-request body formatted as JSON."""
        data = copy.deepcopy(PAYMENT_REQUEST_TEMPLATE)
        filing_type = TRANSACTION_TO_FILING_TYPE[transaction_info["transactionType"]]
        data["filingInfo"]["filingTypes"][0]["filingTypeCode"] = filing_type
        if transaction_info["feeQuantity"] != 1:
            data["filingInfo"]["filingTypes"][0]["quantity"] = transaction_info["feeQuantity"]
        del data["filingInfo"]["filingIdentifier"]
        del data["filingInfo"]["folioNumber"]

        if "waiveFees" in transaction_info and transaction_info["waiveFees"]:
            data["filingInfo"]["filingTypes"][0]["waiveFees"] = True
        # set up FAS payment
        elif "routingSlipNumber" in transaction_info:
            account_info = {"routingSlip": transaction_info["routingSlipNumber"]}
            data["accountInfo"] = account_info
        # setup BCOL account payment
        elif "bcolAccountNumber" in transaction_info:
            account_info = {"bcolAccountNumber": transaction_info["bcolAccountNumber"]}
            if "datNumber" in transaction_info:
                account_info["datNumber"] = transaction_info["datNumber"]
            data["accountInfo"] = account_info
        return data

    def update_payload_data(self, data: dict) -> dict:
        """Explicitly set payment request as CC payment if requested."""
        if self.cc_payment:
            logger.info("Setting pay api payload payment method as CC.")
            data["paymentInfo"] = CC_REQUEST_PAYMENT_INFO
        if self.detail_label and self.detail_value:
            data["details"][0]["label"] = self.detail_label
            data["details"][0]["value"] = self.detail_value
        else:
            del data["details"]
        return data

    def create_payment(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, transaction_type, quantity=1, ppr_id=None, client_reference_id=None, processing_fee=None
    ):
        """Submit a payment request for the PPR API transaction."""
        data = SBCPaymentClient.create_payment_data(
            transaction_type, quantity, ppr_id, client_reference_id, processing_fee
        )
        data = self.update_payload_data(data)
        # logger.debug('create paymnent payload:')
        # logger.debug(json.dumps(data))
        invoice_data = self.call_api(HttpVerbs.POST, PATH_PAYMENT, data)
        return SBCPaymentClient.build_pay_reference(invoice_data, self.api_url)

    def create_payment_staff_search(self, transaction_info, client_reference_id=None):
        """Submit a staff search payment request for the PPR API transaction."""
        data = SBCPaymentClient.create_payment_staff_search_data(transaction_info, client_reference_id)
        data = self.update_payload_data(data)
        logger.debug("staff search create payment payload for account: " + self.account_id)
        logger.debug(json.dumps(data))
        invoice_data = self.call_api(HttpVerbs.POST, PATH_PAYMENT, data, include_account=True)
        return SBCPaymentClient.build_pay_reference(invoice_data, self.api_url)

    def create_payment_staff_registration(self, transaction_info, client_reference_id=None, processing_fee=None):
        """Submit a staff registration payment request for the PPR API transaction."""
        data = SBCPaymentClient.create_payment_staff_registration_data(
            transaction_info, client_reference_id, processing_fee
        )
        data = self.update_payload_data(data)
        logger.info("staff registration create payment payload: ")
        logger.info(json.dumps(data))
        invoice_data = self.call_api(HttpVerbs.POST, PATH_PAYMENT, data, include_account=True)
        return SBCPaymentClient.build_pay_reference(invoice_data, self.api_url)

    def create_payment_staff_client_code(self, transaction_info):
        """Submit a staff client party code payment request."""
        data = SBCPaymentClient.create_payment_staff_client_code_data(transaction_info)
        data = self.update_payload_data(data)
        logger.info(f"staff create payment payload for account {self.account_id}: {data}")
        invoice_data = self.call_api(HttpVerbs.POST, PATH_PAYMENT, data, include_account=True)
        return SBCPaymentClient.build_pay_reference(invoice_data, self.api_url)

    def cancel_payment(self, invoice_id):
        """Immediately cancel or refund the transaction payment as a state rollback."""
        # Payment status does not matter with immediate refunds: always use the refund endpoint.
        logger.info("Calling pay api to refund payment")
        request_path = PATH_REFUND.format(invoice_id=invoice_id)
        return self.call_api(
            HttpVerbs.POST, request_path, data=PAYMENT_REFUND_TEMPLATE, token=SBCPaymentClient.get_sa_token()
        )

    def delete_pending_payment(self, invoice_id):
        """Cancel a credit card payment pending transaction."""
        request_path = PATH_INVOICE.format(invoice_id=invoice_id)
        return self.call_api(HttpVerbs.DELETE, request_path, data=None, include_account=True)

    def get_payment(self, invoice_id):
        """Fetch the current state of the payment invoice."""
        request_path = PATH_INVOICE.format(invoice_id=invoice_id)
        return self.call_api(HttpVerbs.GET, request_path)

    @staticmethod
    def get_sa_token():
        """Refunds must be submitted with a PPR service account token. Request one from the OIDC service."""
        oidc_token_url = current_app.config.get("JWT_OIDC_TOKEN_URL")
        client_id = current_app.config.get("ACCOUNT_SVC_CLIENT_ID")
        client_secret = current_app.config.get("ACCOUNT_SVC_CLIENT_SECRET")
        logger.info(f"Calling OIDC api to get token: URL = {oidc_token_url}, client_id={client_id}.")
        try:
            headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
            data = f"grant_type=client_credentials&scope=openid&client_id={client_id}&client_secret={client_secret}"
            response = requests.request(
                HttpVerbs.POST.value, oidc_token_url, data=data, params=None, headers=headers, timeout=3.0
            )

            if not response or not response.ok:
                raise ApiRequestError(response)

            response_json = json.loads(response.text)
            token = response_json["access_token"]
            logger.info("Have new sa token from OIDC.")
            return token

        except ApiRequestError as err:
            logger.error(err.message)
            raise err

    @staticmethod
    def build_pay_reference(invoice_data, api_url: str):
        """Build a payment reference from the pay api response invoice info."""
        invoice_id = str(invoice_data["id"])
        receipt_path = api_url.replace("https://", "")
        receipt_path = receipt_path[receipt_path.find("/") : None] + PATH_RECEIPT.format(invoice_id=invoice_id)
        # Return the pay reference to include in the API response.
        pay_reference = {"invoiceId": invoice_id, "receipt": receipt_path}
        if invoice_data.get("paymentMethod", "") in (PaymentMethods.CC.value, PaymentMethods.DIRECT_PAY.value):
            logger.info(f"Setting up cc payment pay reference for invoice {invoice_id}.")
            pay_reference["ccPayment"] = True
            pay_reference["paymentActionRequired"] = invoice_data.get("isPaymentActionRequired")
            # Replace with env var {PAYMENT_PORTAL_URL}
            pay_reference["paymentPortalURL"] = "{PAYMENT_PORTAL_URL}/{invoice_id}/{return_URL}"
        return pay_reference
