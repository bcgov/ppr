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
"""The application common configuration."""
import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class BaseConfig:
    """Base configuration."""


class Config(BaseConfig):
    """Production configuration."""

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

    # OIDC and Authorization Config
    OIDC_TOKEN_URL = os.getenv('OIDC_TOKEN_URL')
    OIDC_SA_CLIENT_ID = os.getenv('OIDC_SA_CLIENT_ID')
    OIDC_SA_CLIENT_SECRET = os.getenv('OIDC_SA_CLIENT_SECRET')

    # BCRegistry API Config
    PPR_API_URL = os.getenv('PPR_API_URL')

    # BCRegistry Service Config
    REPORT_SVC_URL = os.getenv('REPORT_SVC_URL')

    # Google SA account
    # create key base64.b64encode(json.dumps(auth_json).encode('utf-8'))
    GOOGLE_STORAGE_SERVICE_ACCOUNT = os.getenv('GOOGLE_STORAGE_SERVICE_ACCOUNT')
    STORAGE_BUCKET_NAME = os.getenv('STORAGE_BUCKET_NAME')
    STORAGE_FILEPATH = os.getenv('STORAGE_FILEPATH')

    # SFTP Config
    SFTP_STORAGE_DIRECTORY = os.getenv('SFTP_STORAGE_DIRECTORY', 'sftp/test')
    SFTP_HOST = os.getenv('SFTP_HOST', None)
    SFTP_PORT = os.getenv('SFTP_PORT', None)
    SFTP_USERNAME = os.getenv('SFTP_USERNAME', None)
    SFTP_PASSWORD = os.getenv('SFTP_PASSWORD', None)
    SFTP_PRIVATE_KEY = os.getenv('SFTP_PRIVATE_KEY', None)
    SFTP_PRIVATE_KEY_ALGORITHM = os.getenv('SFTP_PRIVATE_KEY_ALGORITHM', 'ED25519')
    SFTP_PRIVATE_KEY_PASSPHRASE = os.getenv('SFTP_PRIVATE_KEY_PASSPHRASE', None)
