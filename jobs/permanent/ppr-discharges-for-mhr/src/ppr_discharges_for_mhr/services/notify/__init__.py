# Copyright © 2022 Province of British Columbia
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
"""This module contains the services used by the Delivery Service."""
from http import HTTPStatus
import json

# Don't need GCP tokens until completetly off of OpenShift
# import google.auth.transport.requests
# import google.oauth2.id_token
import requests

from ppr_discharges_for_mhr.services.logging import logging


class Notify:
    """Notify calls the GCNotify service."""

    def __init__(self, **kwargs):
        """Create the notify service."""
        if kwargs:
            self.setup(**kwargs)
    
    def setup(self, **kwargs):
        """Setup the attributes needed for notify to work."""
        self.notify_url = kwargs.get('url')
        self.oidc_url = kwargs.get('oidc_url')
        self.client_id = kwargs.get('sa_client_id')
        self.secret = kwargs.get('sa_secret') 

    def send_email(self, payload: dict) -> HTTPStatus:
        """Create and send the email payload to the Notify service."""

        # auth_req = google.auth.transport.requests.Request()
        # id_token = google.oauth2.id_token.fetch_id_token(auth_req, self.notify_url)
        id_token = self.get_oidc_sa_token()  # Use the PPR/MHR service account to create a JWT.

        headers = {'Authorization': 'Bearer ' + id_token,
                    'Content-Type': 'application/json'}

        res = requests.post(url=self.notify_url,
                            headers=headers,
                            json=payload)

        return res.status_code

    def get_oidc_sa_token(self) -> str:
        """Generate an OIDC PPR service account token (JWT). Request one from the OIDC service."""
        logging.info(f'Calling OIDC api to get token: URL = {self.oidc_url}, client_id={self.client_id}.')
        token = ''
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = f'grant_type=client_credentials&scope=openid&client_id={self.client_id}&client_secret={self.secret}'
        response = requests.request('post',
                                    self.oidc_url,
                                    data=data,
                                    params=None,
                                    headers=headers)

        if not response or not response.ok:
            logging.error(f'No sa token from OIDC: return status {response.status_code}.')
            return token

        response_json = json.loads(response.text)
        token = response_json.get('access_token')
        logging.info(f'Have new sa token from OIDC: {token}')
        return token
