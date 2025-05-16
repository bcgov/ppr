# Copyright © 2025 Province of British Columbia
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

"""The simple pay-api client with only cancel payment invoice is defined here."""
import json
from functools import wraps

import requests

from assets_payment.config import Config
from assets_payment.utils.base import BaseEnum
from assets_payment.utils.logging import logger

PATH_INVOICE = "payment-requests/{invoice_id}"


class HttpVerbs(BaseEnum):
    """Enumeration of HTTP verbs."""

    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    OPTIONS = "options"
    HEAD = "head"


class SBCPaymentClient:
    """Base class for common api call properties and functions."""

    def __init__(self, config: Config, jwt: str = None):
        """Set the API URL from the env variables PAYMENT_SVC_PREFIX and PAYMENT_SVC_URL."""
        service_url = config.PAYMENT_SVC_URL
        self.api_url = service_url + "/" if service_url[-1] != "/" else service_url
        if jwt:
            self.jwt = jwt
        else:
            self.jwt = get_sa_token(config)

    def call_api(self, relative_path: str) -> str:
        """Call the Pay API."""
        try:
            headers = {
                "Authorization": "Bearer " + self.jwt,
                "Content-Type": "application/json",
            }
            url = self.api_url + relative_path
            logger.info(f"Submitting DELETE {url}")
            response = requests.request(HttpVerbs.DELETE.value, url, params=None, headers=headers, timeout=30.0)
            if response.text:
                logger.info(f"Pay api response: {response.text}")
            return response.status_code
        except Exception as err:
            logger.error(f"call_api error: {str(err)}")
            raise err

    def delete_pending_payment(self, invoice_id: str):
        """Cancel a credit card payment pending transaction."""
        request_path = PATH_INVOICE.format(invoice_id=invoice_id)
        return self.call_api(request_path)


def get_sa_token(config: Config):
    """Refunds must be submitted with a PPR service account token. Request one from the OIDC service."""
    oidc_token_url = config.JWT_OIDC_TOKEN_URL
    client_id = config.ACCOUNT_SVC_CLIENT_ID
    client_secret = config.ACCOUNT_SVC_CLIENT_SECRET
    logger.info(f"Calling OIDC api to get token: URL = {oidc_token_url}, client_id={client_id}.")
    try:
        headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
        data = f"grant_type=client_credentials&scope=openid&client_id={client_id}&client_secret={client_secret}"
        response = requests.request(
            HttpVerbs.POST, oidc_token_url, data=data, params=None, headers=headers, timeout=30.0
        )

        if not response or not response.ok:
            logger.info(f"Get SA token failed {response.status_code} {response.text}")
            return None

        response_json = json.loads(response.text)
        token = response_json["access_token"]
        logger.info("Have new sa token from OIDC.")
        return token

    except Exception as err:
        logger.error(f"get_sa_token error: {str(err)}")
        return None
