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

"""Test Suite to ensure the db2 connection is working.

Verify the DB2 driver and connection are working correctly.
"""
import os

from flask import current_app

import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, scoped_session

import ibm_db
import ibm_db_sa


SQL:str = "SELECT COUNT(ownerid) FROM AMHRTDB.OWNER"


def test_db2_direct(session, client, jwt):
    """Assert that the DB2 driver and connectivity are performing as expected."""
    name:str = str(os.getenv('DB2_DATABASE_NAME'))  # 'mhr'
    host:str = str(os.getenv('DB2_DATABASE_HOST'))  # 'localhost'
    port:int = int(os.getenv('DB2_DATABASE_PORT'))  # 50000
    user:str = str(os.getenv('DB2_DATABASE_USERNAME'))  # 'db2inst1'
    pwd:str = str(os.getenv('DB2_DATABASE_PASSWORD'))  # 'mhrdb2'
    conn_string:str = f'DATABASE={name};HOSTNAME={host};PORT={port};PROTOCOL=TCPIP;UID={user};PWD={pwd};'
    current_app.logger.info('Connect string=' + conn_string)
    conn = ibm_db.connect(conn_string, '', '')
    stmt = ibm_db.exec_immediate(conn, SQL)
    result = ibm_db.fetch_both(stmt)
    assert result
    assert result[0]
    current_app.logger.info('OWNER table count=' + str(result[0]))


def test_db2_sqlalchemy(session, client, jwt):
    """Assert that the DB2 driver and SQLAlchemy connectivity are performing as expected."""
    name:str = str(os.getenv('DB2_DATABASE_NAME'))  # 'mhr'
    host:str = str(os.getenv('DB2_DATABASE_HOST'))  # 'localhost'
    port:int = int(os.getenv('DB2_DATABASE_PORT'))  # 50000
    user:str = str(os.getenv('DB2_DATABASE_USERNAME'))  # 'db2inst1'
    pwd:str = str(os.getenv('DB2_DATABASE_PASSWORD'))  # 'mhrdb2'
    engine_conn = f'ibm_db_sa://{user}:{pwd}@{host}:{port}/{name}'
    current_app.logger.info('SQLAlchemy engine connect string=' + engine_conn)
    db2 = sqlalchemy.create_engine(engine_conn)
    result = db2.execute(sqlalchemy.text(SQL))
    assert result
    if result:
        row = result.first()
        count = int(row[0])
        current_app.logger.info('OWNER table count=' + str(count))
