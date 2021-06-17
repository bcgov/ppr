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

from enum import Enum

from flask import current_app

from .client import SBCPaymentClient
from .exceptions import SBCPaymentException


class TransactionTypes(Enum):
    """Derive payment request filing type from transaction type."""

    AMENDMENT = 'AMENDMENT'
    CHANGE = 'CHANGE'
    DISCHARGE = 'DISCHARGE'
    FINANCING_LIFE_YEAR = 'FINANCING_LIFE_YEAR'
    FINANCING_INFINITE = 'FINANCING_INFINITE'
    RENEWAL_LIFE_YEAR = 'RENEWAL_LIFE_YEAR'
    RENEWAL_INFINITE = 'RENEWAL_INFINITE'
    SEARCH = 'SEARCH'


class Payment:
    """Interface for the pay-api service."""

    def __init__(self, jwt=None, account_id=None, api_key=None, details=None):
        """Initialize, set api url from env variable."""
        self.api_url = None
        self.jwt = jwt
        self.account_id = account_id
        self.api_key = api_key
        self.details = details

    def create_payment(self, transaction_type, quantity, transaction_id=None, client_reference_id=None):
        """Submit a payment request for the account_id-jwt pair.

        Quantity is always 1 except for financing and renewal statements, where it is the number of life
        years.
        Transaction type is one of the Payment TransactionTypes.
        Transaction ID is the ppr GUID reference for the payment transaction: either the
        registration_id or the search_id if available.
        Client reference ID if present maps to the pay api folio number.
        Detail_label and detail_value if they exist will show up on the account transaction report.
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
                                                       client_reference_id)
            current_app.logger.debug(api_response)
            return api_response

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
