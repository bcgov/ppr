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
from flask import current_app

from ppr_api.callback.auth.token_service import GoogleStorageTokenService
from ppr_api.utils.logging import logger


def test_get_token(session, client, jwt):
    """Assert that config to get a google storage token works as expected."""
    token = GoogleStorageTokenService.get_token()
    if current_app.config.get("GOOGLE_DEFAULT_SA"):
        logger.debug(token)
        assert token
    else:
        assert not token


def test_get_credentials(session, client, jwt):
    """Assert that the configuration to get a google storage token works as expected (no exceptions)."""
    credentials = GoogleStorageTokenService.get_credentials()
    if current_app.config.get("GOOGLE_DEFAULT_SA"):
        assert credentials
        assert credentials.token
        assert credentials.service_account_email
    else:
        assert not credentials


def test_get_cs_signed_credentials(session, client, jwt):
    """Assert that the configuration to get a google storage token works as expected (no exceptions)."""
    if current_app.config.get("GOOGLE_DEFAULT_SA"):
        credentials = GoogleStorageTokenService.get_cs_signed_credentials()
        assert credentials
        assert credentials.token
        assert credentials.service_account_email
