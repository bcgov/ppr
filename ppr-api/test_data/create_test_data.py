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
"""Create all unit test data.
   The scripts run in the following order:
   1. ./test_reset.sql
   2. ./create_first.sql
   3. All the files in ./test_data sorted by name.
"""
import os

from sqlalchemy.sql import text

from ppr_api import create_app
from ppr_api.models import db
#from test_data.test_single import execute_file


def execute_script(session, file_name):
    print('Executing SQL statements in file ' + file_name)
    with open(file_name, 'r') as sql_file:
        sql_command = ''
        # Iterate over all lines in the sql file
        for line in sql_file:
            # Ignore commented lines
            if not line.startswith('--') and line.strip('\n'):
                # Append line to the command string
                sql_command += line.strip('\n')

                # If the command string ends with ';', it is a full statement
                if sql_command.endswith(';'):
                    sql_command = sql_command.replace(';', '')
                    # print('Executing SQL: ' + sql_command)
                    # Try to execute statement and commit it
                    try:
                        session.execute(text(sql_command))

                    # Assert in case of error
                    except Exception as ex:
                        print(repr(ex))

                    # Finally, clear command string
                    finally:
                        sql_command = ''

        session.commit()
        sql_file.close()


app = create_app('testing')
with app.app_context():
    conn = db.engine.connect()
    options = dict(bind=conn, binds={})
    session = db.create_scoped_session(options=options)

    execute_script(session, 'test_data/postgres_test_reset.sql')
    execute_script(session, 'test_data/postgres_create_first.sql')
    filenames = os.listdir(os.path.join(os.getcwd(), 'test_data/postgres_data_files'))
    sorted_names =  sorted(filenames)
    for filename in sorted_names:
        execute_script(session, os.path.join(os.getcwd(), ('test_data/postgres_data_files/' + filename)))

    conn.close()
