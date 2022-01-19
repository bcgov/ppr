# Copyright © 2021 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Identity and Access Management Service."""
import json

import requests

from document_delivery_service.services.logging import logging


class IAMError(Exception):
    """Exception for IAM errors."""


class JWTService:
    """The Class manages the JWT token for the service account."""

    def __init__(self, oidc_token_url: str, client_id: str, client_secret: str):
        """Initialize the JWT service."""
        self.oidc_token_url = oidc_token_url
        self.client_id = client_id
        self.client_secret = client_secret

    def get_token(self) -> str:
        """Request token from the OIDC service."""
        logging.info('Calling OIDC api to get token: URL = %s, client_id=%s.', self.oidc_token_url, self.client_id)
        if not (self.oidc_token_url and self.client_id and self.client_secret):
            raise IAMError('Invalid OIDC configuration.')

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        template = 'grant_type=client_credentials&scope=openid&client_id={client_id}&client_secret={client_secret}'
        data = template.format(client_id=self.client_id, client_secret=self.client_secret)  # length limit
        response = requests.post(
            self.oidc_token_url,
            data=data,
            params=None,
            headers=headers
        )

        if not response or not response.ok or not response.json():
            raise IAMError(f'Failed to get token from OIDC service: {response.text}')

        response_json = json.loads(response.text)
        if token := response_json.get('access_token'):
            logging.info('Have new sa token from OIDC.')
            return token

        raise IAMError('Failed to get token from OIDC service.')
