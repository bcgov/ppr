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
"""The PPR API service.

This module is the API for the BC Registries Personal Property Registry system.
"""
import asyncio
import logging
import logging.config
import os
from http import HTTPStatus

import sentry_sdk  # noqa: I001; pylint: disable=ungrouped-imports; conflicts with Flake8
from sentry_sdk.integrations.flask import FlaskIntegration  # noqa: I001
from flask import redirect, Flask  # noqa: I001
from registry_schemas import __version__ as registry_schemas_version
from registry_schemas.flask import SchemaServices  # noqa: I001

from ppr_api import config, errorhandlers, models
from ppr_api.models import db
from ppr_api.resources import API_BLUEPRINT, OPS_BLUEPRINT
from ppr_api.schemas import rsbc_schemas
from ppr_api.services import flags
from ppr_api.translations import babel
from ppr_api.utils.auth import jwt
from ppr_api.utils.logging import setup_logging
from ppr_api.utils.run_version import get_run_version
# noqa: I003; the sentry import creates a bad line count in isort

setup_logging(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'logging.conf'))  # important to do this first


def create_app(run_mode=os.getenv('FLASK_ENV', 'production')):
    """Return a configured Flask App using the Factory method."""
    app = Flask(__name__)
    app.config.from_object(config.CONFIGURATION[run_mode])

    # Configure Sentry
    if app.config.get('SENTRY_DSN', None):
        sentry_sdk.init(  # pylint: disable=E0110
            dsn=app.config.get('SENTRY_DSN'),
            integrations=[FlaskIntegration()]
            )

    errorhandlers.init_app(app)
    db.init_app(app)
    rsbc_schemas.init_app(app)
    flags.init_app(app)
#    queue.init_app(app)
    babel.init_app(app)

    app.register_blueprint(API_BLUEPRINT)
    app.register_blueprint(OPS_BLUEPRINT)
    setup_jwt_manager(app, jwt)

    @app.route('/')
    def be_nice_swagger_redirect():  # pylint: disable=unused-variable
        return redirect('/api/v1', code=HTTPStatus.MOVED_PERMANENTLY)

    @app.after_request
    def add_version(response):  # pylint: disable=unused-variable
        version = get_run_version()
        response.headers['API'] = f'ppr_api/{version}'
        response.headers['SCHEMAS'] = f'registry_schemas/{registry_schemas_version}'
        return response

    register_shellcontext(app)

    return app


def setup_jwt_manager(app, jwt_manager):
    """Use flask app to configure the JWTManager to work for a particular Realm."""
    def get_roles(a_dict):
        return a_dict['realm_access']['roles']  # pragma: no cover
    app.config['JWT_ROLE_CALLBACK'] = get_roles

    jwt_manager.init_app(app)


def register_shellcontext(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {
            'app': app,
            'jwt': jwt,
            'db': db,
            'models': models}  # pragma: no cover

    app.shell_context_processor(shell_context)
