# Copyright © 2021 Province of British Columbia
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
import os
import sys

from dotenv import find_dotenv, load_dotenv


# this will load all the envars from a .env file located in the project root (api)
load_dotenv(find_dotenv())

CONFIGURATION = {
    'development': 'search_tester.config.DevConfig',
    'testing': 'search_tester.config.TestConfig',
    'production': 'search_tester.config.ProdConfig',
    'default': 'search_tester.config.ProdConfig'
}


def get_named_config(config_name: str = 'production'):
    """Return the configuration object based on the name.

    :raise: KeyError: if an unknown configuration is requested
    """
    if config_name in ['production', 'staging', 'default']:
        config = ProdConfig()
    elif config_name == 'testing':
        config = TestConfig()
    elif config_name == 'development':
        config = DevConfig()
    else:
        raise KeyError(f'Unknown configuration: {config_name}')
    return config


class _Config():  # pylint: disable=too-few-public-methods
    """Base class configuration that should set reasonable defaults.

    Used as the base for all the other configurations.
    """

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    POD_NAMESPACE = os.getenv('POD_NAMESPACE', '')

    PAUSE = os.getenv('PAUSE', False)
    CSV = os.getenv('CSV', False)
    FILE_NAME = os.getenv('FILE_NAME', 'SEARCH_RESULTS.csv')
    SEARCH_DATE = os.getenv('SEARCH_DATE', None)
    SEARCH_TIME = os.getenv('SEARCH_TIME', None)

    SIM_VAL_BUSINESS = os.getenv('SIM_VAL_BUSINESS', 0.5)
    SIM_VAL_FIRST = os.getenv('SIM_VAL_FIRST', 0.5)
    SIM_VAL_LAST = os.getenv('SIM_VAL_LAST', 0.5)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_USER = os.getenv('DATABASE_USERNAME', '')
    DB_PASSWORD = os.getenv('DATABASE_PASSWORD', '')
    DB_NAME = os.getenv('DATABASE_NAME', '')
    DB_HOST = os.getenv('DATABASE_HOST', '')
    DB_PORT = os.getenv('DATABASE_PORT', '5432')  # POSTGRESQL
    # POSTGRESQL
    SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{password}@{host}:{port}/{name}'.format(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        name=DB_NAME,
    )

    # Connection pool settings
    DB_MIN_POOL_SIZE = os.getenv('DATABASE_MIN_POOL_SIZE', '5')
    DB_MAX_POOL_SIZE = os.getenv('DATABASE_MAX_POOL_SIZE', '5')
    DB_CONN_WAIT_TIMEOUT = os.getenv('DATABASE_CONN_WAIT_TIMEOUT', '5')
    DB_CONN_TIMEOUT = os.getenv('DATABASE_CONN_TIMEOUT', '900')

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        # 'echo_pool': 'debug',
        'pool_size': int(DB_MIN_POOL_SIZE),
        'max_overflow': (int(DB_MAX_POOL_SIZE) - int(DB_MIN_POOL_SIZE)),
        'pool_recycle': int(DB_CONN_TIMEOUT),
        'pool_timeout': int(DB_CONN_WAIT_TIMEOUT)
    }

    TESTING = False
    DEBUG = False

    # DB Query limits on result set sizes
    ACCOUNT_REGISTRATIONS_MAX_RESULTS = os.getenv('ACCOUNT_REGISTRATIONS_MAX_RESULTS', '1000')
    ACCOUNT_DRAFTS_MAX_RESULTS = os.getenv('ACCOUNT_DRAFTS_MAX_RESULTS', '1000')
    ACCOUNT_SEARCH_MAX_RESULTS = os.getenv('ACCOUNT_SEARCH_MAX_RESULTS', '1000')


class DevConfig(_Config):  # pylint: disable=too-few-public-methods
    """Creates the Development Config object."""

    TESTING = False
    DEBUG = True


class TestConfig(_Config):  # pylint: disable=too-few-public-methods
    """In support of testing only.

    Used by the py.test suite
    """

    DEBUG = True
    TESTING = True
    # POSTGRESQL
    DB_USER = os.getenv('DATABASE_TEST_USERNAME', '')
    DB_PASSWORD = os.getenv('DATABASE_TEST_PASSWORD', '')
    DB_NAME = os.getenv('DATABASE_TEST_NAME', '')
    DB_HOST = os.getenv('DATABASE_TEST_HOST', '')
    DB_PORT = os.getenv('DATABASE_TEST_PORT', '5432')
    DB_PORT = os.getenv('DATABASE_TEST_PORT', '1521')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{password}@{host}:{port}/{name}'.format(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        name=DB_NAME,
    )


class ProdConfig(_Config):  # pylint: disable=too-few-public-methods
    """Production environment configuration."""

    SECRET_KEY = os.getenv('SECRET_KEY', None)

    if not SECRET_KEY:
        SECRET_KEY = os.urandom(24)
        print('WARNING: SECRET_KEY being set as a one-shot', file=sys.stderr)

    TESTING = False
    DEBUG = False
