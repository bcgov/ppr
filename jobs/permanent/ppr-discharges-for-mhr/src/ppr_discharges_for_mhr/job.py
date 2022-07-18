import io
import sys
from contextlib import suppress
from http import HTTPStatus
from typing import Final, Optional, Tuple

import psycopg2
import requests

from .common.datetime import datetime
from .services.job_tracking import JobStateEnum, JobTracker
from .services.logging import logging
from .services.notify import Notify
from .services.secrets.google_secrets import GoogleSecretService
from .services.storage import AbstractStorageService, GoogleCloudStorage, StorageDocumentTypes


QUERY: Final ="""select r.registration_ts, r.base_reg_number, sc.mhr_number, sc.serial_number
from registrations r, serial_collateral sc
where r.registration_ts >= (TO_TIMESTAMP('{start_time}', 'YYYY-MM-DD HH24:MI:SS') at time zone 'utc')
  and r.registration_ts <= (TO_TIMESTAMP('{end_time}', 'YYYY-MM-DD HH24:MI:SS') at time zone 'utc')
  and r.registration_type = 'DC'
  and r.financing_id = sc.financing_id
  and sc.serial_type = 'MH'
  and sc.registration_id_end IS NULL    
"""

START_TIME_NAME: Final = 'ppr_mhr_dissolutions_start_test'
END_TIME_NAME: Final = 'ppr_mhr_dissolutions_end_test'

PROGRAM_NAME: Final = 'assets'
JOB_NAME: Final = 'ppr_mhr_dissolutions'

EMAIL_SUBJECT: Final = '[BC Registries and Online Services] CSV File GENERATED {0}'
EMAIL_BODY: Final = '**Your csv file from PPR at the Business Registry has been generated.**\n\nTo access the file,.\n\n[[{0}]]({1})'

def csv_export(db_conn: psycopg2.extensions.connection, query: str) -> Tuple[Optional[str], Optional[io.StringIO]]:
    """Export a supplied query as CSV output and return a Tuple(error, Buffered StringIO)
    
    Use postgres COPY command to export a SQL query as a CSV file.
    Write the output to a IO Buffer and return that.
    """
    try:
        db_cursor = db_conn.cursor()
        sql_copy_str = f'COPY ({query}) TO STDOUT WITH CSV HEADER'
        buffered_output = io.StringIO()
        db_cursor.copy_expert(sql_copy_str, buffered_output)
        return None, buffered_output
    except (psycopg2.Error, Exception) as err:
        error_message = "Error: {err}, for query {query}".format(err=err, query=sql_copy_str)
        logging.debug(error_message)
        return error_message, None
    finally:
        # Clean up: Close the database cursor and connection
        with suppress(Exception):
            db_cursor.close()
        with suppress(Exception):
            db_conn.close()

# Start script
def job(config):

    # Start the job tracker
    job_tracker = JobTracker(**{'uri': config.TRACKER_DATABASE_URI})
    running_job_id = job_tracker.start_job(program_name=PROGRAM_NAME, job_name=JOB_NAME, job_state=JobStateEnum.RUNNING)

    try:
        # Get the secrets that provide the params for the SQL used in the Job
        logging.info(f'Get the secrets for {START_TIME_NAME}, {END_TIME_NAME}.')
        secrets = GoogleSecretService()
        secrets.connect(**{'project_id': config.PROJECT_ID})
        start = secrets.get_secret_version(START_TIME_NAME)
        if not (end := secrets.get_secret_version(END_TIME_NAME)) or (end == 'None'):
            end = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        # Build query
        query = QUERY.format(start_time=start, end_time=end)
        logging.info(f'Format query: {query}')

        # Connect to the app database and do a CSV COPY of the query
        db_conn = psycopg2.connect(dsn=config.APP_DATABASE_URI)
        err, csv_buffer = csv_export(db_conn, query)
        logging.info('Completed the CSV Extract')

        # setup the filename to store the CSV file
        filename = config.FILENAME_TEMPLATE.format(date=datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S'))
        if config.STORAGE_FILEPATH:
            filename = config.STORAGE_FILEPATH + filename

        # store the CSV to google cloud storage
        storage = GoogleCloudStorage(config)
        storage.connect()
        storage.save_document(bucket_name=config.STORAGE_BUCKET_NAME,
                              filename=filename,
                              raw_data=csv_buffer.getvalue(),
                              doc_type=StorageDocumentTypes.TEXT.value)
        logging.info(f'Stored the filename: {filename}')
        
        # Create hte time limited, signed URL
        doc_url = storage.generate_download_signed_url(bucket_name=config.STORAGE_BUCKET_NAME,
                                                       blob_name=filename,
                                                       available_days=2)
        logging.info('Doc URL created.')
        
        email_data = {"recipients": config.EMAIL_RECIPIENTS,
                     "content": {
                        'subject': EMAIL_SUBJECT.format(filename),
                        'body': EMAIL_BODY.format(filename, doc_url)
                     }
                    }

        # Send email
        notify = Notify(**{'url': config.NOTIFY_URL})
        ret = notify.send_email(email_data)
        logging.info(f'Email sent, return code: {ret}')
        if ret != HTTPStatus.OK:
            raise Exception('email not sent')

        # Update the secrets.
        secrets.add_secret_version(START_TIME_NAME, end)
        logging.info('Secret updated.')

        # Close off the job
        job_tracker.stop_job(running_job_id, JobStateEnum.DONE)

    except Exception as err:
        job_tracker.stop_job(running_job_id, JobStateEnum.ERROR, error_code='001', error_additional_details=err)
        logging.error(f'Job failed: {err}', err)
        sys.exit(1)  # Retry Job Task by exiting the process
