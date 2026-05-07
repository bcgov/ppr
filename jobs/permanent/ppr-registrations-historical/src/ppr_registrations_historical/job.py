import sys
from contextlib import suppress
from http import HTTPStatus
from typing import Any, Final

from cloud_sql_connector import DBConfig, getconn
from pg8000 import dbapi as pg8000

from .services.logging import logging


DbConnection = Any
DbCursor = Any


EVENT_JOB_ID = 777777001
UPDATE_ACCOUNT_DISCHARGED = """
UPDATE registrations
   SET account_id = LEFT(account_id, 15) || '_HIS'
 WHERE financing_id IN
 (SELECT DISTINCT fs.id
    FROM registrations r, financing_statements fs
   WHERE fs.id = r.financing_id
     AND r.account_id != '0'
     AND r.account_id NOT LIKE '%_HIS'
     AND EXISTS (SELECT r3.id
                    FROM registrations r3
                    WHERE r3.financing_id = fs.id
                    AND r3.registration_type_cl = 'DISCHARGE'
                    AND r3.registration_ts BETWEEN ((now() at time zone 'utc') - interval '{start_offset} days')
                                                AND ((now() at time zone 'utc') - interval '30 days')))
"""
UPDATE_FINANCING_HEX = """
UPDATE financing_statements
   SET state_type = 'HEX'
 WHERE id IN
 (SELECT DISTINCT fs.id
    FROM registrations r, financing_statements fs
   WHERE fs.id = r.financing_id
     AND r.account_id != '0'
     AND r.account_id NOT LIKE '%_HIS'   
     AND (fs.expire_date IS NOT NULL AND 
         (fs.expire_date at time zone 'utc') BETWEEN ((now() at time zone 'utc') - interval '{start_offset} days')
                                                 AND ((now() at time zone 'utc') - interval '30 days'))
     AND NOT EXISTS (SELECT r3.id
                       FROM registrations r3
                      WHERE r3.financing_id = fs.id
                        AND r3.registration_type_cl = 'DISCHARGE'
                        AND r3.registration_ts BETWEEN ((now() at time zone 'utc') - interval '{start_offset} days')
                                                   AND ((now() at time zone 'utc') - interval '30 days')))
   AND state_type = 'ACT'
"""
UPDATE_ACCOUNT_EXPIRED = """
UPDATE registrations
   SET account_id = LEFT(account_id, 15) || '_HIS'
 WHERE financing_id IN
 (SELECT DISTINCT fs.id
    FROM registrations r, financing_statements fs
   WHERE fs.id = r.financing_id
     AND r.account_id != '0'
     AND r.account_id NOT LIKE '%_HIS'   
     AND (fs.expire_date IS NOT NULL AND 
         (fs.expire_date at time zone 'utc') BETWEEN ((now() at time zone 'utc') - interval '{start_offset} days')
                                                 AND ((now() at time zone 'utc') - interval '30 days'))
     AND NOT EXISTS (SELECT r3.id
                       FROM registrations r3
                      WHERE r3.financing_id = fs.id
                        AND r3.registration_type_cl = 'DISCHARGE'
                        AND r3.registration_ts BETWEEN ((now() at time zone 'utc') - interval '{start_offset} days')
                                                   AND ((now() at time zone 'utc') - interval '30 days')))
"""
DELETE_EXTRA_HISTORICAL = """
DELETE
  FROM user_extra_registrations uer2
 WHERE uer2.id IN (SELECT uer.id
                     FROM registrations r, user_extra_registrations uer
                    WHERE r.registration_number = uer.registration_number
                      AND r.account_id LIKE '%_HIS')
"""
INSERT_EVENT: Final = """
INSERT INTO event_tracking(id, key_id, event_ts, event_tracking_type, status, message)
    VALUES(nextval('event_tracking_id_seq'), %s, CURRENT_TIMESTAMP at time zone 'utc', 'REG_HIST_JOB',
                 %s, %s)
"""

def track_event(db_conn: DbConnection,
                db_cursor: DbCursor,
                status: int,
                message: str):
    """Capture the job run in the event tracking table."""
    try:
        if not db_conn or not db_cursor:
            return
        db_cursor.execute(INSERT_EVENT, (EVENT_JOB_ID, int(status), message))
        db_conn.commit()
    except Exception as err:
        error_message = f"Error attempting event_tracking insert: {err}"
        logging.error(error_message)

# Start job
def job(config):

    db_conn: DbConnection | None = None
    db_cursor: DbCursor | None = None
    job_message: str = '1. Update account discharged registrations.'
    try:
        logging.info('Getting database connection and cursor.')
        if config.CLOUDSQL_INSTANCE_CONNECTION_NAME:  # pragma: no cover
            db_config = DBConfig(
                instance_name=config.CLOUDSQL_INSTANCE_CONNECTION_NAME,
                database=config.APP_DB_NAME,
                user=config.APP_DB_USER,
                ip_type=config.DB_IP_TYPE,
                pool_recycle=60,
                schema='public',
            )
            db_conn = getconn(db_config)
        else:
            db_conn = pg8000.connect(
                user=config.APP_DB_USER,
                password=config.APP_DB_PASSWORD,
                host=config.APP_DB_HOST,
                port=int(config.APP_DB_PORT),
                database=config.APP_DB_NAME,
            )
        db_cursor = db_conn.cursor()

        # Update account ids for registrations discharged more than 30 days.
        sql_statement = UPDATE_ACCOUNT_DISCHARGED.format(start_offset=config.START_DATE_OFFSET)
        logging.info(f'Starting step 1: update account discharged registrations: {sql_statement}')
        db_cursor.execute(sql_statement)
        db_conn.commit()

        # Update financing statements status to HEX for statements expired more than 30 days.
        job_message += '\n2. Update financing_statements.state_type=HEX for expired registrations.'
        sql_statement = UPDATE_FINANCING_HEX.format(start_offset=config.START_DATE_OFFSET)
        logging.info(f'Starting step 2: update financing_statements.state_type=HEX: {sql_statement}')
        db_cursor.execute(sql_statement)
        db_conn.commit()

        # Update account ids for registrations expired more than 30 days.
        job_message += '\n3. Update account expired registrations.'
        sql_statement = UPDATE_ACCOUNT_EXPIRED.format(start_offset=config.START_DATE_OFFSET)
        logging.info(f'Starting step 3: update account expired registrations: {sql_statement}')
        db_cursor.execute(sql_statement)
        db_conn.commit()

        # Update account ids for registrations expired more than 30 days.
        job_message += '\n4. Delete account extra registrations historical.'
        logging.info('Starting step 4: delete account extra registrations that are now historical:')
        logging.info(DELETE_EXTRA_HISTORICAL)
        db_cursor.execute(DELETE_EXTRA_HISTORICAL)
        db_conn.commit()

        logging.info('Run completed without error.')
        track_event(db_conn, db_cursor, HTTPStatus.OK, job_message)
    except Exception as err:
        track_event(db_conn, db_cursor, HTTPStatus.INTERNAL_SERVER_ERROR, job_message + '\n' + str(err))
        logging.error(f'Job run failed: {err}')
        sys.exit(1)  # Retry Job Task by exiting the process
    finally:
        # Clean up: Close the database cursor and connection
        if db_cursor:
            with suppress(Exception):
                db_cursor.close()
        if db_conn:
            with suppress(Exception):
                db_conn.close()
