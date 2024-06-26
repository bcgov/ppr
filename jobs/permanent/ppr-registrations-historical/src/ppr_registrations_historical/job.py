import sys
from contextlib import suppress
from http import HTTPStatus
from typing import Final

import psycopg2

from .services.logging import logging


EVENT_JOB_ID = 777777001
UPDATE_ACCOUNT_DISCHARGED = """
UPDATE registrations
   SET account_id = account_id || '_HIS'
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
   SET account_id = account_id || '_HIS'
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
  VALUES(nextval('event_tracking_id_seq'), {job_id}, CURRENT_TIMESTAMP  at time zone 'utc', 'REG_HIST_JOB',
         {job_status}, '{job_message}')
"""

def track_event(db_conn: psycopg2.extensions.connection,
                db_cursor: psycopg2.extensions.cursor,
                status: int,
                message: str):
    """Capture the job run in the event tracking table."""
    try:
        if not db_conn or not db_cursor:
            return
        sql_statement = INSERT_EVENT.format(job_id=EVENT_JOB_ID, job_status=status, job_message=message)
        db_cursor.execute(sql_statement)
        db_conn.commit()
    except (psycopg2.Error, Exception) as err:
        error_message = f"Error attempting event_tracking insert: {err}"
        logging.error(error_message)

# Start job
def job(config):

    db_conn: psycopg2.extensions.connection
    db_cursor: psycopg2.extensions.cursor
    job_message: str = '1. Update account discharged registrations.'
    try:
        logging.info('Getting database connection and cursor.')
        db_conn = psycopg2.connect(dsn=config.APP_DATABASE_URI)
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
    except (psycopg2.Error, Exception) as err:
        track_event(db_conn, db_cursor, HTTPStatus.INTERNAL_SERVER_ERROR, job_message + '\n' + str(err))
        logging.error(f'Job run failed: {err}', err)
        sys.exit(1)  # Retry Job Task by exiting the process
    finally:
        # Clean up: Close the database cursor and connection
        with suppress(Exception):
            db_cursor.close()
        with suppress(Exception):
            db_conn.close()
