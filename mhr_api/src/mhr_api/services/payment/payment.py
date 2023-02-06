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
"""This module exposes all pay-api operations used by the PPR api."""

from flask import current_app

from .client import ApiRequestError, SBCPaymentClient
from .exceptions import SBCPaymentException


class Payment:
    """Interface for the pay-api service."""

    def __init__(self, jwt=None, account_id=None, api_key=None, details=None):
        """Initialize, set api url from env variable."""
        self.api_url = None
        self.jwt = jwt
        self.account_id = account_id
        self.api_key = api_key
        self.details = details

    def create_payment(  # pylint: disable=too-many-arguments
            self,
            transaction_type,
            quantity,
            transaction_id=None,
            client_reference_id=None,
            processing_fee=None
    ):
        """Submit a payment request for the account_id-jwt pair.

        Quantity is by default is 1.
        Transaction type is one of the Payment TransactionTypes.
        Transaction ID is the mhr GUID reference for the payment transaction: either the
        registration_id or the search_id if available.
        Client reference ID if present maps to the pay api folio number.
        Details label and value if they exist will show up on the account transaction report.
        """
        try:
            api_instance = SBCPaymentClient(self.jwt,
                                            self.account_id,
                                            self.api_key,
                                            self.details)
            if self.api_url:
                api_instance.api_url = self.api_url
            api_response = api_instance.create_payment(transaction_type,
                                                       quantity,
                                                       transaction_id,
                                                       client_reference_id,
                                                       processing_fee)
            current_app.logger.debug(api_response)
            return api_response

        except ApiRequestError as api_err:
            raise SBCPaymentException(api_err, json_data=api_err.json_data)
        except Exception as err:  # noqa: B902; wrapping exception
            raise SBCPaymentException(err)

    def cancel_payment(self, invoice_id):
        """Submit a request to cancel a payment using the invoice ID from the create_payment response.

        Cancel_payment should only be called if a post payment database commit fails.
        """
        try:
            api_instance = SBCPaymentClient(self.jwt, self.account_id, self.api_key)
            if self.api_url:
                api_instance.api_url = self.api_url
            api_response = api_instance.cancel_payment(invoice_id)
            return api_response

        except Exception as err:   # noqa: B902; wrapping exception
            raise SBCPaymentException(err)

    def create_payment_search(self, selections, transaction_id=None, client_reference_id=None, staff_gov=False):
        """Submit a non-staff search payment request for the account_id-jwt pair.

        Quantity is by default is 1, but increments with each selected search match.
        Payment filing type(s) and quantity are dynamically derived based on the search selection.
        Possible combinations are search MHR only, search MHR and PPR only, or both.
        Selections is an array of selected search matches.
        Transaction ID is the mhr GUID reference for the payment transaction: either the
        registration_id or the search_id if available.
        Client reference ID if present maps to the pay api folio number.
        Staff_gov is the government staff flag (different filing type).
        Details label and value if they exist will show up on the account transaction report.
        """
        try:
            api_instance = SBCPaymentClient(self.jwt,
                                            self.account_id,
                                            self.api_key,
                                            self.details)
            if self.api_url:
                api_instance.api_url = self.api_url
            api_response = api_instance.create_payment_search(selections,
                                                              transaction_id,
                                                              client_reference_id,
                                                              staff_gov)
            current_app.logger.debug(api_response)
            return api_response

        except ApiRequestError as api_err:
            raise SBCPaymentException(api_err, json_data=api_err.json_data)
        except Exception as err:  # noqa: B902; wrapping exception
            raise SBCPaymentException(err)

    def create_payment_staff_search(self, selections, transaction_info, transaction_id=None, client_reference_id=None):
        """Submit a staff payment request for the transaction_info. Token must have a staff role.

        Payment info transaction type is one of the Payment TransactionTypes.
        Client reference ID if present maps to the pay api folio number.
        Details label and value if they exist will show up on the account transaction report.
        """
        try:
            api_instance = SBCPaymentClient(self.jwt,
                                            transaction_info.get('accountId'),
                                            self.api_key,
                                            self.details)
            if self.api_url:
                api_instance.api_url = self.api_url
            api_response = api_instance.create_payment_staff_search(selections,
                                                                    transaction_info,
                                                                    transaction_id,
                                                                    client_reference_id)
            current_app.logger.debug(api_response)
            return api_response

        except Exception as err:  # noqa: B902; wrapping exception
            raise SBCPaymentException(err)

    def create_payment_staff(self, transaction_info, client_reference_id=None):
        """Submit a staff payment request for the transaction_info. Token must have a staff role.

        Payment info transaction type is one of the Payment TransactionTypes.
        Client reference ID if present maps to the pay api folio number.
        Details label and value if they exist will show up on the account transaction report.
        """
        try:
            api_instance = SBCPaymentClient(self.jwt,
                                            transaction_info.get('accountId'),
                                            self.api_key,
                                            self.details)
            if self.api_url:
                api_instance.api_url = self.api_url
            api_response = api_instance.create_payment_staff(transaction_info, client_reference_id)
            current_app.logger.debug(api_response)
            return api_response

        except Exception as err:  # noqa: B902; wrapping exception
            raise SBCPaymentException(err)
