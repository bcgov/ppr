# Copyright © 2019 Province of British Columbia
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
"""This maintains access tokens for API calls."""
import os
from abc import ABC, abstractmethod

import google.auth.transport.requests
import google.oauth2.id_token
from google.oauth2 import service_account
from flask import current_app


class TokenService(ABC):  # pylint: disable=too-few-public-methods
    """Token Service abstract class with single get_token method."""

    @classmethod
    @abstractmethod
    def get_token(cls):
        """Generate an OAuth access token with storage access."""


class GoogleStorageTokenService(TokenService):  # pylint: disable=too-few-public-methods
    """Google Cloud Storage implementation.

    Maintain access token for Google Cloud Storage API calls.
    """

    # Google APIs and cloud storage
    GCP_PROJECT_ID = os.getenv('GCP_CS_PROJECT_ID')
    GCP_SA_CLIENT_EMAIL = os.getenv('GCP_CS_SA_CLIENT_EMAIL')
    GCP_SA_CLIENT_ID = os.getenv('GCP_CS_SA_CLIENT_ID')
    GCP_SA_PRIVATE_KEY = os.getenv('GCP_CS_SA_PRIVATE_KEY')
    GCP_SA_PRIVATE_KEY_ID = os.getenv('GCP_CS_SA_PRIVATE_KEY_ID')
    GCP_SA_CERT_URL = os.getenv('GCP_CS_SA_CERT_URL')
    # https://developers.google.com/identity/protocols/oauth2/scopes
    GCP_SA_SCOPES = [os.getenv('GCP_CS_SA_SCOPES', 'https://www.googleapis.com/auth/cloud-platform')]
    service_account_info = {
        'type': 'service_account',
        'project_id': GCP_PROJECT_ID,
        'private_key_id': GCP_SA_PRIVATE_KEY_ID,
        'private_key': str(GCP_SA_PRIVATE_KEY).replace('\\n', '\n'),
        'client_email': GCP_SA_CLIENT_EMAIL,
        'client_id': GCP_SA_CLIENT_ID,
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
        'client_x509_cert_url': GCP_SA_CERT_URL
    }
    credentials = None

    @classmethod
    def get_token(cls):
        """Generate an OAuth access token with cloud storage access."""
        if cls.credentials is None:
            cls.credentials = service_account.Credentials.from_service_account_info(cls.service_account_info,
                                                                                    scopes=cls.GCP_SA_SCOPES)
        request = google.auth.transport.requests.Request()
        cls.credentials.refresh(request)
        current_app.logger.info('Call successful: obtained token.')
        return cls.credentials.token

    @classmethod
    def get_credentials(cls):
        """Generate GCP auth credentials to pass to a GCP client."""
        if cls.credentials is None:
            cls.credentials = service_account.Credentials.from_service_account_info(cls.service_account_info,
                                                                                    scopes=cls.GCP_SA_SCOPES)
        current_app.logger.info('Call successful: obtained credentials.')
        return cls.credentials

    @classmethod
    def get_report_api_token(cls):
        """Generate an OAuth access token with IAM configured auth mhr api container to report api container."""
        audience = current_app.config.get('REPORT_API_AUDIENCE')
        if not audience:
            return None
        auth_req = google.auth.transport.requests.Request()
        token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
        current_app.logger.info('Call successful: obtained token.')
        return token
