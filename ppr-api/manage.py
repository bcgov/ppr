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

"""Manage the database and some other items required to run the API
"""
import logging
import os

from flask.cli import FlaskGroup  # replaces flask_script Manager
from sqlalchemy.sql import text

# models included so that migrate can build the database migrations
from ppr_api import models  # pylint: disable=unused-import
from ppr_api import create_app
from ppr_api.models import db

APP = create_app()
CLI = FlaskGroup(APP)  # replaces MANAGER


def execute_script(session, file_name):
    """Execute a SQL script as one or more SQL statements in a single file."""
    print("Executing SQL statements in file " + file_name)
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
                    # print(sql_command)
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


@CLI.command("create_test_data")
def create_test_data():
    """Load unit test data in the dev/local environment. Delete all existing test data as a first step."""
    execute_script(db.session, "test_data/postgres_test_reset.sql")
    execute_script(db.session, "test_data/postgres_create_first.sql")
    filenames = os.listdir(os.path.join(os.getcwd(), "test_data/postgres_data_files"))
    sorted_names = sorted(filenames)
    for filename in sorted_names:
        execute_script(db.session, os.path.join(os.getcwd(), ("test_data/postgres_data_files/" + filename)))


if __name__ == "__main__":
    logging.log(logging.INFO, "Running the Flask CLI")
    CLI()
