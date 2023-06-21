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

import google.auth.transport.requests
import google.oauth2.id_token
import requests

from flask import current_app


class Notify:
    """Notify calls the GCNotify service."""

    def __init__(self, **kwargs):
        """Create the notify service."""
        if kwargs:
            self.setup(**kwargs)

    def setup(self, **kwargs):
        """Configure the minimum properties required for notify to work."""
        self.notify_url = kwargs.get('url')

    def send_email(self, payload: dict) -> HTTPStatus:
        """Create and send the email payload to the Notify service."""
        auth_req = google.auth.transport.requests.Request()
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, self.notify_url)
        current_app.logger.debug(id_token)
        headers = {'Authorization': 'Bearer ' + id_token,
                   'Content-Type': 'application/json'}

        res = requests.post(url=self.notify_url,
                            headers=headers,
                            json=payload)

        return res.status_code
