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
"""The application common configuration."""
import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class BaseConfig:
    """Base configuration."""


class Config(BaseConfig):
    """Production configuration."""

    # API Endpoints
    AUTH_API_URL = os.getenv("AUTH_API_URL", "")
    AUTH_API_VERSION = os.getenv("AUTH_API_VERSION", "")
    PAY_API_URL = os.getenv("PAY_API_URL", "")
    PAY_API_VERSION = os.getenv("PAY_API_VERSION", "")
    NOTIFY_API_URL = os.getenv("NOTIFY_API_URL", "")
    NOTIFY_API_VERSION = os.getenv("NOTIFY_API_VERSION", "")

    AUTH_SVC_URL = f"{AUTH_API_URL + AUTH_API_VERSION}"
    PAYMENT_SVC_URL = f"{PAY_API_URL + PAY_API_VERSION}"
    NOTIFY_SVC_URL = f"{NOTIFY_API_URL + NOTIFY_API_VERSION}"

    JWT_OIDC_TOKEN_URL = os.getenv("JWT_OIDC_TOKEN_URL")
    # service accounts
    ACCOUNT_SVC_CLIENT_ID = os.getenv("ACCOUNT_SVC_CLIENT_ID")
    ACCOUNT_SVC_CLIENT_SECRET = os.getenv("ACCOUNT_SVC_CLIENT_SECRET")

    APP_DB_USER = os.getenv("APP_DATABASE_USERNAME", "")
    APP_DB_PASSWORD = os.getenv("APP_DATABASE_PASSWORD", "")
    APP_DB_NAME = os.getenv("APP_DATABASE_NAME", "")
    APP_DB_HOST = os.getenv("APP_DATABASE_HOST", "")
    APP_DB_PORT = os.getenv("APP_DATABASE_PORT", "5432")
    # POSTGRESQL
    # POSTGRESQL
    if APP_DB_UNIX_SOCKET := os.getenv("APP_DATABASE_UNIX_SOCKET", None):
        APP_DATABASE_URI = f"postgresql://{APP_DB_USER}:{APP_DB_PASSWORD}@/{APP_DB_NAME}?host={APP_DB_UNIX_SOCKET}"
    else:
        APP_DATABASE_URI = f"postgresql://{APP_DB_USER}:{APP_DB_PASSWORD}@{APP_DB_HOST}:{APP_DB_PORT}/{APP_DB_NAME}"

    # Notify config
    NOTIFY_STATUS_RECIPIENTS = os.getenv("NOTIFY_STATUS_RECIPIENTS", "")
    NOTIFY_STATUS_SUBJECT = os.getenv("NOTIFY_STATUS_SUBJECT", "")
    NOTIFY_STATUS_BODY = os.getenv("NOTIFY_STATUS_BODY", "")

    MHR_EXPIRY_CLIENT_HOURS = os.getenv("MHR_EXPIRY_CLIENT_HOURS", "")
    MHR_EXPIRY_STAFF_HOURS = os.getenv("MHR_EXPIRY_STAFF_HOURS", "")
    PPR_EXPIRY_CLIENT_HOURS = os.getenv("PPR_EXPIRY_CLIENT_HOURS", "")
    PPR_EXPIRY_STAFF_HOURS = os.getenv("PPR_EXPIRY_STAFF_HOURS", "")
