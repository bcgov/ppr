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

    PROJECT_ID = os.getenv('PROJECT_ID')
    FILENAME_TEMPLATE = os.getenv('FILENAME_TEMPLATE', 'ppr-dissolutions-{date}.csv')

    NOTIFY_URL = os.getenv('NOTIFY_URL')
    EMAIL_RECIPIENTS = os.getenv('EMAIL_RECIPIENTS')

    # Google SA account
    # create key base64.b64encode(json.dumps(auth_json).encode('utf-8'))
    GOOGLE_STORAGE_SERVICE_ACCOUNT = os.getenv('GOOGLE_STORAGE_SERVICE_ACCOUNT')
    if GOOGLE_STORAGE_SERVICE_ACCOUNT and isinstance(GOOGLE_STORAGE_SERVICE_ACCOUNT, str):
        GOOGLE_STORAGE_SERVICE_ACCOUNT = bytes(GOOGLE_STORAGE_SERVICE_ACCOUNT, 'utf-8')
    STORAGE_BUCKET_NAME = os.getenv('STORAGE_BUCKET_NAME')
    STORAGE_FILEPATH = os.getenv('STORAGE_FILEPATH')

    APP_DB_USER = os.getenv('APP_DATABASE_USERNAME', '')
    APP_DB_PASSWORD = os.getenv('APP_DATABASE_PASSWORD', '')
    APP_DB_NAME = os.getenv('APP_DATABASE_NAME', '')
    APP_DB_HOST = os.getenv('APP_DATABASE_HOST', '')
    APP_DB_PORT = os.getenv('APP_DATABASE_PORT', '5432')
    # POSTGRESQL
        # POSTGRESQL
    if APP_DB_UNIX_SOCKET := os.getenv('APP_DATABASE_UNIX_SOCKET', None):
        APP_DATABASE_URI = f'postgresql+psycopg2://{APP_DB_USER}:{APP_DB_PASSWORD}@/{APP_DB_NAME}?host={APP_DB_UNIX_SOCKET}'
    else:
        APP_DATABASE_URI = f'postgresql://{APP_DB_USER}:{APP_DB_PASSWORD}@{APP_DB_HOST}:{APP_DB_PORT}/{APP_DB_NAME}'

    TRACKER_DB_USER = os.getenv('TRACKER_DATABASE_USERNAME', '')
    TRACKER_DB_PASSWORD = os.getenv('TRACKER_DATABASE_PASSWORD', '')
    TRACKER_DB_NAME = os.getenv('TRACKER_DATABASE_NAME', '')
    TRACKER_DB_HOST = os.getenv('TRACKER_DATABASE_HOST', '')
    TRACKER_DB_PORT = os.getenv('TRACKER_DATABASE_PORT', '5432')
    # POSTGRESQL
        # POSTGRESQL
    if TRACKER_DB_UNIX_SOCKET := os.getenv('TRACKER_DATABASE_UNIX_SOCKET', None):
        TRACKER_DATABASE_URI = f'postgresql+psycopg2://{TRACKER_DB_USER}:{TRACKER_DB_PASSWORD}@/{TRACKER_DB_NAME}?host={TRACKER_DB_UNIX_SOCKET}'
    else:
        TRACKER_DATABASE_URI = f'postgresql://{TRACKER_DB_USER}:{TRACKER_DB_PASSWORD}@{TRACKER_DB_HOST}:{TRACKER_DB_PORT}/{TRACKER_DB_NAME}'
