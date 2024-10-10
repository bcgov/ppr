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
"""The MHR API service.

This module is the API for the BC Registries Manufactured Home Registry system.
"""
import os

from flask import Flask, redirect  # noqa: I001
from flask_migrate import Migrate, upgrade
from registry_schemas import __version__ as registry_schemas_version
from sqlalchemy.sql import text

from mhr_api import errorhandlers, models
from mhr_api.config import config
from mhr_api.metadata import APP_RUNNING_ENVIRONMENT, APP_VERSION
from mhr_api.models import db
from mhr_api.resources import endpoints
from mhr_api.schemas import rsbc_schemas
from mhr_api.services import auth_service, queue_service, storage_service
from mhr_api.translations import babel
from mhr_api.utils.auth import jwt
from mhr_api.utils.logging import logger, setup_logging

setup_logging(os.path.join(os.path.abspath(os.path.dirname(__file__)), "logging.yaml"))  # important to do this first


def create_app(service_environment=APP_RUNNING_ENVIRONMENT, **kwargs):
    """Return a configured Flask App using the Factory method."""
    app = Flask(__name__)
    app.config.from_object(config[service_environment])
    app.url_map.strict_slashes = False

    errorhandlers.init_app(app)

    db.init_app(app)
    Migrate(app, db)
    if app.config.get("DEPLOYMENT_ENV", "") == "testing":  # CI only run upgrade for unit testing.
        logger.info("Running db upgrade.")
        with app.app_context():
            upgrade(directory="migrations", revision="head", sql=False, tag=None)
        # Alembic has it's own logging config, we'll need to restore our logging here.
        setup_logging(os.path.join(os.path.abspath(os.path.dirname(__file__)), "logging.yaml"))
        logger.info("Finished db upgrade.")
    else:
        logger.info("Logging, migrate set up.")

    rsbc_schemas.init_app(app)
    babel.init_app(app)
    auth_service.init_app(app)
    storage_service.init_app(app)
    endpoints.init_app(app)
    queue_service.init_app(app)

    setup_jwt_manager(app, jwt)

    @app.after_request
    def add_version(response):  # pylint: disable=unused-variable
        response.headers["API"] = f"mhr_api/{APP_VERSION}"
        response.headers["SCHEMAS"] = f"registry_schemas/{registry_schemas_version}"
        return response

    register_shellcontext(app)

    if app.config.get("DEPLOYMENT_ENV", "") == "testing":  # CI only create test data.
        with app.app_context():
            setup_test_data()

    return app


def setup_jwt_manager(app, jwt_manager):
    """Use flask app to configure the JWTManager to work for a particular Realm."""

    def get_roles(a_dict):
        return a_dict["realm_access"]["roles"]  # pragma: no cover

    app.config["JWT_ROLE_CALLBACK"] = get_roles

    jwt_manager.init_app(app)


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {"app": app, "jwt": jwt, "db": db, "models": models}  # pragma: no cover

    app.shell_context_processor(shell_context)


def setup_test_data():
    """Load unit test data in the dev/local environment. Delete all existing test data as a first step."""
    try:
        test_path = os.getcwd()
        logger.info(f"Executing DB scripts to create test data from test data dir {test_path}...")
        # execute_script(db.session, os.path.join(test_path, "test_data/postgres_test_reset.sql"))
        execute_script(db.session, "test_data/postgres_create_first.sql")
        filenames = os.listdir(os.path.join(test_path, "test_data/postgres_data_files"))
        sorted_names = sorted(filenames)
        for filename in sorted_names:
            execute_script(db.session, os.path.join(test_path, ("test_data/postgres_data_files/" + filename)))
        # execute_script(db.session, "test_data/postgres_test_reset_ppr.sql")
        execute_script(db.session, "test_data/postgres_create_first_ppr.sql")
        filenames = os.listdir(os.path.join(os.getcwd(), "test_data/postgres_data_files_ppr"))
        sorted_names = sorted(filenames)
        for filename in sorted_names:
            execute_script(db.session, os.path.join(os.getcwd(), ("test_data/postgres_data_files_ppr/" + filename)))
    except Exception as err:  # pylint: disable=broad-except # noqa F841;
        logger.error(f"setup_test_data failed: {str(err)}")


def execute_script(session, file_name):
    """Execute a SQL script as one or more SQL statements in a single file."""
    logger.info(f"Executing SQL statements in file {file_name}")
    with open(file_name, "r") as sql_file:
        sql_command = ""
        # Iterate over all lines in the sql file
        for line in sql_file:
            # Ignore commented lines
            if not line.startswith("--") and line.strip("\n"):
                # Append line to the command string
                sql_command += line.strip("\n")

                # If the command string ends with ';', it is a full statement
                if sql_command.endswith(";"):
                    sql_command = sql_command.replace(";", "")
                    # print('Executing SQL: ' + sql_command)
                    # Try to execute statement and commit it
                    try:
                        session.execute(text(sql_command))

                    # Assert in case of error
                    except Exception as ex:
                        print(repr(ex))

                    # Finally, clear command string
                    finally:
                        sql_command = ""

        session.commit()
        sql_file.close()
