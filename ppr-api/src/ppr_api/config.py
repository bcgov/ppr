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
"""All of the configuration for the service is captured here.

All items are loaded, or have Constants defined here that
are loaded into the Flask configuration.
All modules and lookups get their configuration from the
Flask config, rather than reading environment variables directly
or by accessing this configuration directly.
"""
import json
import os
import sys

import requests


def get_mock_auth() -> str:
    """For CI unit tests get mock auth value."""
    try:
        url: str = "https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/testing/mock-sa-ppr"
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers, timeout=10.0)
        if response and response.text:
            resp_json = json.loads(response.text)
            return resp_json.get("response", "")
        return ""
    except Exception:
        return ""


def get_named_config(config_name: str = "production"):
    """Return the configuration object based on the name.

    :raise: KeyError: if an unknown configuration is requested
    """
    if config_name in ["production", "staging", "default"]:
        configuration = ProdConfig()
    elif config_name == "sandbox":
        configuration = SandboxConfig()
    elif config_name == "testing":
        configuration = TestConfig()
    elif config_name == "development":
        configuration = DevConfig()
    else:
        raise KeyError(f"Unknown configuration: {config_name}")
    return configuration


class Config:  # pylint: disable=too-few-public-methods
    """Base class configuration that should set reasonable defaults.

    Used as the base for all the other configurations.
    """

    DEBUG = False
    TESTING = False
    DEVELOPMENT = False

    DEPLOYMENT_PLATFORM = os.getenv("DEPLOYMENT_PLATFORM", "gcp")
    DEPLOYMENT_PROJECT = os.getenv("DEPLOYMENT_PROJECT", "eogruh-dev")
    FLASK_PYDANTIC_VALIDATION_ERROR_RAISE = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALEMBIC_INI = "migrations/alembic.ini"

    PAYMENT_SVC_URL = os.getenv("PAYMENT_SVC_URL", "https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1")
    AUTH_SVC_URL = os.getenv("AUTH_SVC_URL", "https://auth-api-dev.apps.silver.devops.gov.bc.ca/api/v1")
    REPORT_SVC_URL = os.getenv("REPORT_SVC_URL", "https://gotenberg-p56lvhvsqa-nn.a.run.app")
    REPORT_TEMPLATE_PATH = os.getenv("REPORT_TEMPLATE_PATH", "report-templates")

    LD_SDK_KEY = os.getenv("LD_SDK_KEY", None)
    SECRET_KEY = "a secret"

    DB_USER = os.getenv("DATABASE_USERNAME", "")
    DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
    DB_NAME = os.getenv("DATABASE_NAME", "")
    DB_HOST = os.getenv("DATABASE_HOST", "")
    DB_PORT = os.getenv("DATABASE_PORT", "5432")  # POSTGRESQL
    # POSTGRESQL
    if DB_UNIX_SOCKET := os.getenv("DATABASE_UNIX_SOCKET", None):
        SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}?host={DB_UNIX_SOCKET}"
    else:
        SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Connection pool settings
    DB_MIN_POOL_SIZE = os.getenv("DATABASE_MIN_POOL_SIZE", "2")
    DB_MAX_POOL_SIZE = os.getenv("DATABASE_MAX_POOL_SIZE", "10")
    DB_CONN_WAIT_TIMEOUT = os.getenv("DATABASE_CONN_WAIT_TIMEOUT", "5")
    DB_CONN_TIMEOUT = os.getenv("DATABASE_CONN_TIMEOUT", "900")

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        # 'echo_pool': 'debug',
        "pool_size": int(DB_MIN_POOL_SIZE),
        "max_overflow": (int(DB_MAX_POOL_SIZE) - int(DB_MIN_POOL_SIZE)),
        "pool_recycle": int(DB_CONN_TIMEOUT),
        "pool_timeout": int(DB_CONN_WAIT_TIMEOUT),
    }

    # JWT_OIDC Settings
    JWT_OIDC_WELL_KNOWN_CONFIG = os.getenv("JWT_OIDC_WELL_KNOWN_CONFIG")
    JWT_OIDC_ALGORITHMS = os.getenv("JWT_OIDC_ALGORITHMS")
    JWT_OIDC_JWKS_URI = os.getenv("JWT_OIDC_JWKS_URI")
    JWT_OIDC_ISSUER = os.getenv("JWT_OIDC_ISSUER")
    JWT_OIDC_AUDIENCE = os.getenv("JWT_OIDC_AUDIENCE")
    JWT_OIDC_CLIENT_SECRET = os.getenv("JWT_OIDC_CLIENT_SECRET")
    JWT_OIDC_CACHING_ENABLED = os.getenv("JWT_OIDC_CACHING_ENABLED")
    JWT_OIDC_TOKEN_URL = os.getenv("JWT_OIDC_TOKEN_URL")
    try:
        JWT_OIDC_JWKS_CACHE_TIMEOUT = int(os.getenv("JWT_OIDC_JWKS_CACHE_TIMEOUT"))
        if not JWT_OIDC_JWKS_CACHE_TIMEOUT:
            JWT_OIDC_JWKS_CACHE_TIMEOUT = 300
    except (TypeError, ValueError):
        JWT_OIDC_JWKS_CACHE_TIMEOUT = 300

    # service accounts
    ACCOUNT_SVC_AUTH_URL = os.getenv("ACCOUNT_SVC_AUTH_URL")
    ACCOUNT_SVC_CLIENT_ID = os.getenv("ACCOUNT_SVC_CLIENT_ID")
    ACCOUNT_SVC_CLIENT_SECRET = os.getenv("ACCOUNT_SVC_CLIENT_SECRET")
    # ACCOUNT_SVC_TIMEOUT = os.g

    # DB Query limits on result set sizes
    ACCOUNT_REGISTRATIONS_MAX_RESULTS = os.getenv("ACCOUNT_REGISTRATIONS_MAX_RESULTS", "100")
    ACCOUNT_DRAFTS_MAX_RESULTS = os.getenv("ACCOUNT_DRAFTS_MAX_RESULTS", "1000")
    ACCOUNT_SEARCH_MAX_RESULTS = os.getenv("ACCOUNT_SEARCH_MAX_RESULTS", "1000")

    # DEBTOR search trgram similarity quotients
    SIMILARITY_QUOTIENT_BUSINESS_NAME: float = float(os.getenv("SIMILARITY_QUOTIENT_BUSINESS_NAME", "0.6"))
    SIMILARITY_QUOTIENT_FIRST_NAME: float = float(os.getenv("SIMILARITY_QUOTIENT_FIRST_NAME", "0.4"))
    SIMILARITY_QUOTIENT_LAST_NAME: float = float(os.getenv("SIMILARITY_QUOTIENT_LAST_NAME", "0.29"))
    SIMILARITY_QUOTIENT_DEFAULT: float = float(os.getenv("SIMILARITY_QUOTIENT_DEFAULT", "0.5"))

    # Search results report number of financing statements threshold for async requests.
    SEARCH_PDF_ASYNC_THRESHOLD: int = int(os.getenv("SEARCH_PDF_ASYNC_THRESHOLD", "75"))

    # UI callbackURL for large reports: signal API to skip notification for UI requests.
    UI_SEARCH_CALLBACK_URL = os.getenv("UI_SEARCH_CALLBACK_URL", "PPR_UI")

    # Event tracking max retries before human intervention.
    EVENT_MAX_RETRIES: int = int(os.getenv("EVENT_MAX_RETRIES", "3"))

    # Google APIs and cloud storage
    GOOGLE_DEFAULT_SA = os.getenv("GOOGLE_DEFAULT_SA")
    GCP_CS_SA_SCOPES = os.getenv("GCP_CS_SA_SCOPES", "https://www.googleapis.com/auth/cloud-platform")
    # Storage of search reports
    GCP_CS_BUCKET_ID = os.getenv("GCP_CS_BUCKET_ID", "ppr_search_results_dev")
    # Storage of verification mail reports
    GCP_CS_BUCKET_ID_VERIFICATION = os.getenv("GCP_CS_BUCKET_ID_VERIFICATION", "ppr_verification_report_dev")
    # Storage of registration verification reports
    GCP_CS_BUCKET_ID_REGISTRATION = os.getenv("GCP_CS_BUCKET_ID_REGISTRATION", "ppr_registration_report_dev")
    # Storage of mail verification reports
    GCP_CS_BUCKET_ID_MAIL = os.getenv("GCP_CS_BUCKET_ID_MAIL", "ppr_mail_report_dev")

    # Pub/Sub
    GCP_PS_PROJECT_ID = os.getenv("DEPLOYMENT_PROJECT", "eogruh-dev")
    GCP_PS_SEARCH_REPORT_TOPIC = os.getenv("GCP_PS_SEARCH_REPORT_TOPIC", "ppr-search-report")
    GCP_PS_NOTIFICATION_TOPIC = os.getenv("GCP_PS_NOTIFICATION_TOPIC", "ppr-api-notification")
    GCP_PS_VERIFICATION_REPORT_TOPIC = os.getenv("GCP_PS_VERIFICATION_REPORT_TOPIC", "ppr-mail-report")
    GCP_PS_REGISTRATION_REPORT_TOPIC = os.getenv("GCP_PS_REGISTRATION_REPORT_TOPIC", "ppr-registration-report")

    GATEWAY_URL = os.getenv("GATEWAY_URL", "https://bcregistry-dev.apigee.net")
    SUBSCRIPTION_API_KEY = os.getenv("SUBSCRIPTION_API_KEY")
    # Host name/IP of mail out service for file transfer: only in TEST and PROD.
    SURFACE_MAIL_HOST = os.getenv("SURFACE_MAIL_HOST", "")
    SURFACE_MAIL_TARGET_PATH = os.getenv("SURFACE_MAIL_TARGET_PATH", "FIN_PPR/TEST")

    # Search results data size threshold for real time reports.
    MAX_SIZE_SEARCH_RT: int = int(os.getenv("MAX_SIZE_SEARCH_RT", "225000"))
    # Default 2, set to 1 to revert to original report api client
    REPORT_VERSION = os.getenv("REPORT_VERSION", "2")
    REPORT_API_AUDIENCE = os.getenv("REPORT_API_AUDIENCE", "https://gotenberg-p56lvhvsqa-nn.a.run.app")
    # Number of registrations threshold for search report light format.
    REPORT_SEARCH_LIGHT: int = int(os.getenv("REPORT_SEARCH_LIGHT", "700"))

    DEPLOYMENT_ENV = os.getenv("DEPLOYMENT_ENV", "development")
    if not GOOGLE_DEFAULT_SA and DEPLOYMENT_ENV in ("unitTesting", "testing"):
        GOOGLE_DEFAULT_SA = get_mock_auth()


class DevConfig(Config):  # pylint: disable=too-few-public-methods
    """Creates the Development Config object."""

    DEVELOPMENT = True
    TESTING = False
    DEBUG = True


class TestConfig(Config):  # pylint: disable=too-few-public-methods
    """Config object for testing(staging) environment."""

    DEVELOPMENT = True
    DEBUG = True


class UnitTestingConfig(Config):  # pylint: disable=too-few-public-methods
    """In support of testing only.

    Used by the py.test suite
    """

    DEBUG = True
    TESTING = True

    # POSTGRESQL
    DB_USER = os.getenv("DATABASE_TEST_USERNAME", "")
    DB_PASSWORD = os.getenv("DATABASE_TEST_PASSWORD", "")
    DB_NAME = os.getenv("DATABASE_TEST_NAME", "")
    DB_HOST = os.getenv("DATABASE_TEST_HOST", "")
    DB_PORT = os.getenv("DATABASE_TEST_PORT", "5432")
    # SQLALCHEMY_DATABASE_URI = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # JWT OIDC settings
    # JWT_OIDC_TEST_MODE will set jwt_manager to use
    JWT_OIDC_TEST_MODE = True
    JWT_OIDC_TEST_AUDIENCE = "example"
    JWT_OIDC_TEST_ISSUER = "https://example.localdomain/auth/realms/example"
    JWT_OIDC_TEST_KEYS = {
        "keys": [
            {
                "kid": "flask-jwt-oidc-test-client",
                "kty": "RSA",
                "alg": "RS256",
                "use": "sig",
                "n": "AN-fWcpCyE5KPzHDjigLaSUVZI0uYrcGcc40InVtl-rQRDmAh-C2W8H4_Hxhr5VLc6crsJ2LiJTV_E72S03pzpOOaaYV6-TzAjCou2GYJIXev7f6Hh512PuG5wyxda_TlBSsI-gvphRTPsKCnPutrbiukCYrnPuWxX5_cES9eStR",  # noqa: E501
                "e": "AQAB",
            }
        ]
    }

    JWT_OIDC_TEST_PRIVATE_KEY_JWKS = {
        "keys": [
            {
                "kid": "flask-jwt-oidc-test-client",
                "kty": "RSA",
                "alg": "RS256",
                "use": "sig",
                "n": "AN-fWcpCyE5KPzHDjigLaSUVZI0uYrcGcc40InVtl-rQRDmAh-C2W8H4_Hxhr5VLc6crsJ2LiJTV_E72S03pzpOOaaYV6-TzAjCou2GYJIXev7f6Hh512PuG5wyxda_TlBSsI-gvphRTPsKCnPutrbiukCYrnPuWxX5_cES9eStR",  # noqa: E501
                "e": "AQAB",
                "d": "C0G3QGI6OQ6tvbCNYGCqq043YI_8MiBl7C5dqbGZmx1ewdJBhMNJPStuckhskURaDwk4-8VBW9SlvcfSJJrnZhgFMjOYSSsBtPGBIMIdM5eSKbenCCjO8Tg0BUh_xa3CHST1W4RQ5rFXadZ9AeNtaGcWj2acmXNO3DVETXAX3x0",  # noqa: E501
                "p": "APXcusFMQNHjh6KVD_hOUIw87lvK13WkDEeeuqAydai9Ig9JKEAAfV94W6Aftka7tGgE7ulg1vo3eJoLWJ1zvKM",
                "q": "AOjX3OnPJnk0ZFUQBwhduCweRi37I6DAdLTnhDvcPTrrNWuKPg9uGwHjzFCJgKd8KBaDQ0X1rZTZLTqi3peT43s",
                "dp": "AN9kBoA5o6_Rl9zeqdsIdWFmv4DB5lEqlEnC7HlAP-3oo3jWFO9KQqArQL1V8w2D4aCd0uJULiC9pCP7aTHvBhc",
                "dq": "ANtbSY6njfpPploQsF9sU26U0s7MsuLljM1E8uml8bVJE1mNsiu9MgpUvg39jEu9BtM2tDD7Y51AAIEmIQex1nM",
                "qi": "XLE5O360x-MhsdFXx8Vwz4304-MJg-oGSJXCK_ZWYOB_FGXFRTfebxCsSYi0YwJo-oNu96bvZCuMplzRI1liZw",
            }
        ]
    }

    JWT_OIDC_TEST_PRIVATE_KEY_PEM = """
-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDfn1nKQshOSj8xw44oC2klFWSNLmK3BnHONCJ1bZfq0EQ5gIfg
tlvB+Px8Ya+VS3OnK7Cdi4iU1fxO9ktN6c6TjmmmFevk8wIwqLthmCSF3r+3+h4e
ddj7hucMsXWv05QUrCPoL6YUUz7Cgpz7ra24rpAmK5z7lsV+f3BEvXkrUQIDAQAB
AoGAC0G3QGI6OQ6tvbCNYGCqq043YI/8MiBl7C5dqbGZmx1ewdJBhMNJPStuckhs
kURaDwk4+8VBW9SlvcfSJJrnZhgFMjOYSSsBtPGBIMIdM5eSKbenCCjO8Tg0BUh/
xa3CHST1W4RQ5rFXadZ9AeNtaGcWj2acmXNO3DVETXAX3x0CQQD13LrBTEDR44ei
lQ/4TlCMPO5bytd1pAxHnrqgMnWovSIPSShAAH1feFugH7ZGu7RoBO7pYNb6N3ia
C1idc7yjAkEA6Nfc6c8meTRkVRAHCF24LB5GLfsjoMB0tOeEO9w9Ous1a4o+D24b
AePMUImAp3woFoNDRfWtlNktOqLel5PjewJBAN9kBoA5o6/Rl9zeqdsIdWFmv4DB
5lEqlEnC7HlAP+3oo3jWFO9KQqArQL1V8w2D4aCd0uJULiC9pCP7aTHvBhcCQQDb
W0mOp436T6ZaELBfbFNulNLOzLLi5YzNRPLppfG1SRNZjbIrvTIKVL4N/YxLvQbT
NrQw+2OdQACBJiEHsdZzAkBcsTk7frTH4yGx0VfHxXDPjfTj4wmD6gZIlcIr9lZg
4H8UZcVFN95vEKxJiLRjAmj6g273pu9kK4ymXNEjWWJn
-----END RSA PRIVATE KEY-----"""


class SandboxConfig(Config):  # pylint: disable=too-few-public-methods
    """Config object for sandbox environment."""

    TESTING = False
    DEBUG = False


class ProdConfig(Config):  # pylint: disable=too-few-public-methods
    """Production environment configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", None)

    if not SECRET_KEY:
        SECRET_KEY = os.urandom(24)
        print("WARNING: SECRET_KEY being set as a one-shot", file=sys.stderr)

    TESTING = False
    DEBUG = False


config = {
    "development": DevConfig,
    "test": TestConfig,
    "sandbox": SandboxConfig,
    "production": ProdConfig,
    "unitTesting": UnitTestingConfig,
    "default": ProdConfig,
}
