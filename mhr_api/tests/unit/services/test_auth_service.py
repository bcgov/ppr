# Copyright © 2019 Province of British Columbia
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
"""Google Storage token tests."""
import base64
import json
import os

from flask import current_app

from mhr_api.services.gcp_auth.auth_service import GoogleAuthService


def test_get_token(session, client, jwt):
    """Assert that the configuration to get a google storage token works as expected (no exceptions)."""
    token = GoogleAuthService.get_token()
    print(token)
    assert token


def test_get_credentials(session, client, jwt):
    """Assert that the configuration to get a google storage token works as expected (no exceptions)."""
    credentials = GoogleAuthService.get_credentials()
    assert credentials


def test_security_account(session, client, jwt):
    """Assert that the configuration to get the GCP service account from the environment works as expected."""
    decoded_sa = None
    encoded_sa: bytes = None
    default_sa = os.getenv('GOOGLE_DEFAULT_SERVICE_ACCOUNT')
    if default_sa:
        encoded_sa = bytes(default_sa, 'utf-8')
    if not encoded_sa:
        current_app.logger.info('No GOOGLE_DEFAULT_SERVICE_ACCOUNT env var.')
        sa_project_id = os.getenv('GCP_CS_PROJECT_ID')
        sa_client_email = os.getenv('GCP_CS_SA_CLIENT_EMAIL')
        sa_client_id = os.getenv('GCP_CS_SA_CLIENT_ID')
        sa_private_key  = os.getenv('GCP_CS_SA_PRIVATE_KEY')
        sa_private_key_id = os.getenv('GCP_CS_SA_PRIVATE_KEY_ID')
        sa_cert_url = os.getenv('GCP_CS_SA_CERT_URL')
        service_account_info = {
            'type': 'service_account',
            'project_id': sa_project_id,
            'private_key_id': sa_private_key_id,
            'private_key': str(sa_private_key).replace('\\n', '\n'),
            'client_email': sa_client_email,
            'client_id': sa_client_id,
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
            'client_x509_cert_url': sa_cert_url
        }
        encoded_sa = base64.b64encode(json.dumps(service_account_info).encode('utf-8'))
        current_app.logger.debug(encoded_sa)

    assert encoded_sa
    decoded_sa = json.loads(base64.b64decode(encoded_sa.decode('utf-8')))
    # current_app.logger.debug(decoded_sa)
    assert decoded_sa
    assert decoded_sa.get('type')
    assert decoded_sa.get('project_id')
    assert decoded_sa.get('private_key_id')
    assert decoded_sa.get('private_key')
    assert decoded_sa.get('client_email')
    assert decoded_sa.get('client_id')
    assert decoded_sa.get('auth_uri')
    assert decoded_sa.get('token_uri')
    assert decoded_sa.get('auth_provider_x509_cert_url')
    assert decoded_sa.get('client_x509_cert_url')
