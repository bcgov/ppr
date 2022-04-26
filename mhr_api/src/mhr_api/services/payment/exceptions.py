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
"""Define top level pay api exceptions here."""


class PaymentException(Exception):
    """Base class for Payment exceptions."""

    def __init__(self, wrapped_err=None, message='Payment exception.', status_code=500):
        """Initialize the exceptions."""
        self.err = wrapped_err
        if wrapped_err:
            self.message = '{msg}: {desc}'.format(msg=message, desc=str(wrapped_err))
        else:
            self.message = message
        # Map HTTP status if the wrapped error has an HTTP status code
        self.status_code = wrapped_err.status if wrapped_err and hasattr(wrapped_err, 'status') else status_code
        super().__init__(self.message)


class SBCPaymentException(Exception):
    """Used for general / unknown Service BC Payment API exceptions when calling the Service BC Payment API."""

    def __init__(self, message: str = 'Payment Error', json_data=None):
        """Initialize the exceptions."""
        self.message = message
        self.json_data = json_data
        if self.json_data and 'status_code' in self.json_data:
            self.status_code = self.json_data['status_code']
        else:
            self.status_code = 500
        super().__init__(self.message)


class SBCPaymentError(PaymentException):
    """Used for known Service BC Payment API errors when calling the Service BC Payment API.

    Used when the response contains a specific error message / code.
    """

    def __init__(self, wrapped_err=None, message='SBC Pay API error'):
        """Initialize the exceptions."""
        super().__init__(wrapped_err, message)
