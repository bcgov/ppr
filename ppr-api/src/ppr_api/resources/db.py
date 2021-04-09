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
"""Create Oracle database connection pool.

These will get initialized by the application.
"""
import cx_Oracle
from flask import _app_ctx_stack, current_app


class OracleDB:
    """Oracle database connection object for re-use in application."""

    def __init__(self, app=None):
        """initializer, supports setting the app context on instantiation."""
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Create setup for the extension.

        :param app: Flask app
        :return: naked
        """
        self.app = app
        app.teardown_appcontext(self.teardown)

    @staticmethod
    def teardown():
        """Oracle session pool cleans up after itself."""
        ctx = _app_ctx_stack.top
        if hasattr(ctx, 'oracle_pool'):
            ctx.oracle_pool.close()

    @staticmethod
    def _create_pool():
        """Create the cx_oracle connection pool from the Flask Config Environment.

        :return: an instance of the OCI Session Pool
        """
        # this uses the builtin session / connection pooling provided by
        # the Oracle OCI driver
        # setting threaded =True wraps the underlying calls in a Mutex
        # so we don't have to do that here

        # Do we need this? All API dates and times are DB default UTC.
        def init_session(conn, *args):  # pylint: disable=unused-argument; Extra var being passed with call
            cursor = conn.cursor()
            cursor.execute("alter session set TIME_ZONE = 'UTC'")
        return cx_Oracle.SessionPool(user=current_app.config.get('DB_USER'),  # pylint:disable=c-extension-no-member
                                     password=current_app.config.get('DB_PASSWORD'),
                                     dsn='{0}:{1}/{2}'.format(current_app.config.get('DB_HOST'),
                                                              current_app.config.get('DB_PORT'),
                                                              current_app.config.get('DB_NAME')),
                                     min=5,
                                     max=20,
                                     increment=1,
                                     connectiontype=cx_Oracle.Connection,  # pylint:disable=c-extension-no-member
                                     threaded=True,
                                     getmode=cx_Oracle.SPOOL_ATTRVAL_NOWAIT,  # pylint:disable=c-extension-no-member
                                     waitTimeout=1500,
                                     timeout=3600,
                                     sessionCallback=init_session,
                                     encoding='UTF-8',
                                     nencoding='UTF-8')

    @staticmethod
    def create_engine_pool(db_pool_config):
        """Create the SQLAlchemy engine cx_oracle connection pool from the Flask Config Environment.

        :return: an instance of the OCI Session Pool. DB_NAME will append .bcgov if it contains no domain.
        """
        # this uses the builtin session / connection pooling provided by
        # the Oracle OCI driver
        # setting threaded =True wraps the underlying calls in a Mutex
        # so we don't have to do that here

        # Do we need this? All API dates and times are DB default UTC.
        def init_session(conn, *args):  # pylint: disable=unused-argument; Extra var being passed with call
            cursor = conn.cursor()
            cursor.execute("alter session set TIME_ZONE = 'UTC'")
        database_name = db_pool_config['name']
        if database_name.find('.') < 1:
            database_name += '.bcgov'
        return cx_Oracle.SessionPool(user=db_pool_config['user'],  # pylint:disable=c-extension-no-member
                                     password=db_pool_config['password'],
                                     dsn='{0}:{1}/{2}'.format(db_pool_config['host'],
                                                              db_pool_config['port'],
                                                              database_name),
                                     min=db_pool_config['min_pool_size'],
                                     max=db_pool_config['max_pool_size'],
                                     increment=1,
                                     connectiontype=cx_Oracle.Connection,  # pylint:disable=c-extension-no-member
                                     threaded=True,
                                     getmode=cx_Oracle.SPOOL_ATTRVAL_NOWAIT,  # pylint:disable=c-extension-no-member
                                     waitTimeout=db_pool_config['wait_timeout'],
                                     timeout=db_pool_config['timeout'],
                                     sessionCallback=init_session,
                                     encoding='UTF-8',
                                     nencoding='UTF-8')

    @property
    def connection(self):  # pylint: disable=inconsistent-return-statements
        """Create connection property for the API.

        If this is running in a Flask context,
        then either get the existing connection pool or create a new one
        and then return an acquired session
        :return: cx_Oracle.connection type
        """
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'oracle_pool'):
                ctx._oracle_pool = self._create_pool()  # pylint: disable = protected-access; need this method
            return ctx._oracle_pool.acquire()  # pylint: disable = protected-access; need this method


# export instance of this class
DB = OracleDB()
