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

    APP_DB_USER = os.getenv('APP_DATABASE_USERNAME', '')
    APP_DB_PASSWORD = os.getenv('APP_DATABASE_PASSWORD', '')
    APP_DB_NAME = os.getenv('APP_DATABASE_NAME', '')
    APP_DB_HOST = os.getenv('APP_DATABASE_HOST', '')
    APP_DB_PORT = os.getenv('APP_DATABASE_PORT', '5432')
    START_DATE_OFFSET = os.getenv('START_DATE_OFFSET', '32')
    # POSTGRESQL
        # POSTGRESQL
    if (APP_DB_UNIX_SOCKET := os.getenv('APP_DATABASE_UNIX_SOCKET', None)):
        APP_DATABASE_URI = f'postgresql://{APP_DB_USER}:{APP_DB_PASSWORD}@/{APP_DB_NAME}?host={APP_DB_UNIX_SOCKET}'
    else:
        APP_DATABASE_URI = f'postgresql://{APP_DB_USER}:{APP_DB_PASSWORD}@{APP_DB_HOST}:{APP_DB_PORT}/{APP_DB_NAME}'
