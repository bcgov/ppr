# Copyright © 2025 Province of British Columbia
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
"""This module executes all the job steps."""
import copy
import io
import json
import sys
import zipfile
from contextlib import suppress
from datetime import datetime as _datetime

import psycopg2
import pytz

from secured_party_notification.config import Config
from secured_party_notification.services.document_storage.storage_service import GoogleStorageService
from secured_party_notification.services.notify import Notify
from secured_party_notification.utils.logging import logger

CONTENT_TYPE_CSV = "text/csv"
CONTENT_TYPE_TEXT = "text/plain"
CONTENT_TYPE_ZIP = "application/zip"
CONTENT_TYPE_PDF = "application/pdf"
BATCH_FILE_DOC_NAME = "batch-notifications-{batch_job_id}.pdf"
DELIVERY_COUNT_FILE_NAME = "PPRVER.{curr_date}.txt"
DELIVERY_ZIP_FILE_NAME = "PPRVER.{curr_date}.zip"
CSV_FILE_DOC_NAME = "batch-notifications-status-{batch_job_id}.csv"
CSV_HEADER = "reg_number,base_reg_number,reg_type,registration_id,party_id,storage_path,status\n"
CSV_LINE = '"{reg_num}","{base_reg_num}","{reg_type}",{reg_id},{party_id},"{storage_path}",{status}\n'
NOTIFY_STATUS_DATA = {
    "batch_job_id": -1,
    "total_count": -1,
    "missing_count": -1,
    "batch_file_name": -1,
    "csv_file_url": -1,
    "error_count": 0,
    "delivery_count": 0,
}
NOTIFICATION_QUERY = """
select r.registration_number, r.base_reg_number,
       r.registration_type_cl,
       mr.registration_id, mr.party_id, mr.doc_storage_url, mr.status, mr.id as mail_report_id
  from mail_reports mr, registrations r
 where r.id = mr.registration_id
   and mr.create_ts > (now() at time zone 'utc') - interval '{interval_hours} hours'
   and mr.batch_job_id is null
order by mr.id
"""
SUMMARY_QUERY = """
select min(mr.id) as batch_job_id,
       count(mr.id) as total_count,
       (select count(mr2.id)
          from mail_reports mr2
         where mr2.create_ts > (now() at time zone 'utc') - interval '{interval_hours} hours'
           and mr2.batch_job_id is null
           and mr2.doc_storage_url is null) as missing_count
  from mail_reports mr
 where mr.create_ts > (now() at time zone 'utc') - interval '{interval_hours} hours'
   and mr.batch_job_id is null
"""
UPDATE_JOB_QUERY = """
UPDATE mail_reports
   SET batch_job_id = {job_id},
       status = case when status = 200 then 201 else status end
 where create_ts > (now() at time zone 'utc') - interval '{interval_hours} hours'
   and batch_job_id is null
"""
RERUN_NOTIFICATION_QUERY = """
select r.registration_number, r.base_reg_number,
       r.registration_type_cl,
       mr.registration_id, mr.party_id, mr.doc_storage_url, mr.status, mr.id as mail_report_id
  from mail_reports mr, registrations r
 where r.id = mr.registration_id
   and mr.batch_job_id = {rerun_job_id}
order by mr.id
"""
RERUN_SUMMARY_QUERY = """
select min(mr.id) as batch_job_id,
       count(mr.id) as total_count,
       (select count(mr2.id)
          from mail_reports mr2
         where mr2.batch_job_id = {rerun_job_id}
           and mr2.doc_storage_url is null) as missing_count
  from mail_reports mr
 where mr.batch_job_id = {rerun_job_id}
"""
RERUN_UPDATE_JOB_QUERY = """
UPDATE mail_reports
   SET status = 201
 where batch_job_id = {rerun_job_id}
   and status = 200
"""
RANGE_NOTIFICATION_QUERY = """
select r.registration_number, r.base_reg_number,
       r.registration_type_cl,
       mr.registration_id, mr.party_id, mr.doc_storage_url, mr.status, mr.id as mail_report_id
  from mail_reports mr, registrations r
 where r.id = mr.registration_id
   and mr.create_ts between to_timestamp('{start_ts}', 'YYYY-MM-DD HH24:MI:SS')
                        and to_timestamp('{end_ts}', 'YYYY-MM-DD HH24:MI:SS')
order by mr.id
"""
RANGE_SUMMARY_QUERY = """
select min(mr.id) as batch_job_id,
       count(mr.id) as total_count,
       (select count(mr2.id)
          from mail_reports mr2
         where mr2.create_ts between to_timestamp('{start_ts}', 'YYYY-MM-DD HH24:MI:SS')
                                 and to_timestamp('{end_ts}', 'YYYY-MM-DD HH24:MI:SS') 
           and mr2.doc_storage_url is null) as missing_count
  from mail_reports mr
 where mr.create_ts between to_timestamp('{start_ts}', 'YYYY-MM-DD HH24:MI:SS')
                        and to_timestamp('{end_ts}', 'YYYY-MM-DD HH24:MI:SS')
"""
RANGE_UPDATE_JOB_QUERY = """
UPDATE mail_reports
   SET batch_job_id = {job_id},
       status = case when status = 200 then 201 else status end
 where create_ts between to_timestamp('{start_ts}', 'YYYY-MM-DD HH24:MI:SS')
                     and to_timestamp('{end_ts}', 'YYYY-MM-DD HH24:MI:SS')
   and batch_job_id is null
"""


def get_batch_doc_storage_name(batch_job_id: str):
    """Get a batch file document storage name in the format YYYY/MM/DD/batch-notifications-{batch_job_id}.pdf."""
    name = _datetime.now(pytz.utc).isoformat()[:10]
    name = name.replace("-", "/") + "/" + BATCH_FILE_DOC_NAME.format(batch_job_id=batch_job_id)
    return name


def get_csv_doc_storage_name(batch_job_id: str):
    """Get a csv file document storage name in the format YYYY/MM/DD/batch-notifications-status-{batch_job_id}.csv."""
    name = _datetime.now(pytz.utc).isoformat()[:10]
    name = name.replace("-", "/") + "/" + CSV_FILE_DOC_NAME.format(batch_job_id=batch_job_id)
    return name


def get_delivery_zip_name():
    """Get a document delivery zip file name in the format PPRVER.YYYYMMDD.zip."""
    now_ts = _datetime.now(pytz.utc)
    now_local = now_ts.astimezone(pytz.timezone("Canada/Pacific"))
    local_date: str = now_local.isoformat()[:10].replace("-", "")
    storage_date = now_ts.isoformat()[:10].replace("-", "/")
    name = storage_date + "/" + DELIVERY_ZIP_FILE_NAME.format(curr_date=local_date)
    return name


def get_delivery_count_name():
    """Get a document delivery document count file name in the format PPRVER.YYYYMMDD.txt."""
    now_ts = _datetime.now(pytz.utc)
    now_local = now_ts.astimezone(pytz.timezone("Canada/Pacific"))
    local_date: str = now_local.isoformat()[:10].replace("-", "")
    storage_date = now_ts.isoformat()[:10].replace("-", "/")
    name = storage_date + "/" + DELIVERY_COUNT_FILE_NAME.format(curr_date=local_date)
    return name


def run_summary_query(
    db_conn: psycopg2.extensions.connection, db_cursor: psycopg2.extensions.cursor, config: Config
) -> dict:
    """Execute the summary information query."""
    if config.RERUN_JOB_ID and config.RERUN_JOB_ID != "":
        return rerun_summary_query(db_conn, db_cursor, config)
    elif config.RANGE_START_TS and config.RANGE_START_TS != "" and config.RANGE_END_TS and config.RANGE_END_TS != "":
        return ts_range_summary_query(db_conn, db_cursor, config)
    status_data: dict = copy.deepcopy(NOTIFY_STATUS_DATA)
    try:
        sql_statement = SUMMARY_QUERY.format(interval_hours=config.JOB_INTERVAL_HOURS)
        logger.info(f"Executing summary query: {sql_statement}")
        db_cursor.execute(sql_statement)
        row = db_cursor.fetchone()
        if row[0]:  # Null if no registrations in the time interval
            status_data["batch_job_id"] = int(row[0])
        status_data["total_count"] = int(row[1])
        status_data["missing_count"] = int(row[2])
        if status_data.get("total_count") < 1:
            status_data["batch_job_id"] = "NA"
            status_data["batch_file_name"] = "NA"
            status_data["csv_file_url"] = "NA"
        else:
            status_data["csv_file_name"] = get_csv_doc_storage_name(status_data["batch_job_id"])
            status_data["batch_file_name"] = get_batch_doc_storage_name(status_data["batch_job_id"])
            status_data["delivery_count_file_name"] = get_delivery_count_name()
            status_data["delivery_zip_file_name"] = get_delivery_zip_name()
        logger.info(f"Status query results: {str(status_data)}")
    except (psycopg2.Error, Exception) as err:
        error_message = f"Error attempting to run summary query: {err}"
        logger.error(error_message)
    return status_data


def rerun_summary_query(
    db_conn: psycopg2.extensions.connection, db_cursor: psycopg2.extensions.cursor, config: Config
) -> dict:
    """Execute the summary information query for a batch rerun on the env var RERUN_JOB_ID."""
    status_data: dict = copy.deepcopy(NOTIFY_STATUS_DATA)
    try:
        job_id = int(config.RERUN_JOB_ID)
        sql_statement = RERUN_SUMMARY_QUERY.format(rerun_job_id=job_id)
        logger.info(f"Executing summary query: {sql_statement}")
        db_cursor.execute(sql_statement)
        row = db_cursor.fetchone()
        if row[0]:  # Null if no registrations for the job
            status_data["batch_job_id"] = job_id
        status_data["total_count"] = int(row[1])
        status_data["missing_count"] = int(row[2])
        if status_data.get("total_count") < 1:
            status_data["batch_job_id"] = "NA"
            status_data["batch_file_name"] = "NA"
            status_data["csv_file_url"] = "NA"
        else:
            status_data["csv_file_name"] = get_csv_doc_storage_name(status_data["batch_job_id"])
            status_data["batch_file_name"] = get_batch_doc_storage_name(status_data["batch_job_id"])
            status_data["delivery_count_file_name"] = get_delivery_count_name()
            status_data["delivery_zip_file_name"] = get_delivery_zip_name()
        logger.info(f"Status query results: {str(status_data)}")
    except (psycopg2.Error, Exception) as err:
        error_message = f"Error attempting to execute rerun job summary query: {err}"
        logger.error(error_message)
    return status_data


def ts_range_summary_query(
    db_conn: psycopg2.extensions.connection, db_cursor: psycopg2.extensions.cursor, config: Config
) -> dict:
    """Execute the summary information query for a batch timestamp range on the start and end ts env vars."""
    status_data: dict = copy.deepcopy(NOTIFY_STATUS_DATA)
    try:
        start_ts: str = str(config.RANGE_START_TS).replace("T", " ")
        end_ts: str = str(config.RANGE_END_TS).replace("T", " ")
        sql_statement = RANGE_SUMMARY_QUERY.format(start_ts=start_ts, end_ts=end_ts)
        logger.info(f"Executing summary query: {sql_statement}")
        db_cursor.execute(sql_statement)
        row = db_cursor.fetchone()
        if row[0]:  # Null if no registrations for the job
            status_data["batch_job_id"] = int(row[0])
        status_data["total_count"] = int(row[1])
        status_data["missing_count"] = int(row[2])
        if status_data.get("total_count") < 1:
            status_data["batch_job_id"] = "NA"
            status_data["batch_file_name"] = "NA"
            status_data["csv_file_url"] = "NA"
        else:
            status_data["csv_file_name"] = get_csv_doc_storage_name(status_data["batch_job_id"])
            status_data["batch_file_name"] = get_batch_doc_storage_name(status_data["batch_job_id"])
            status_data["delivery_count_file_name"] = get_delivery_count_name()
            status_data["delivery_zip_file_name"] = get_delivery_zip_name()
        logger.info(f"Status query results: {str(status_data)}")
    except (psycopg2.Error, Exception) as err:
        error_message = f"Error attempting to execute timestamp range job summary query: {err}"
        logger.error(error_message)
    return status_data


def get_csv_data(row, status: int = None) -> dict:
    """Get csv data from the mail_report record, optionally overriding the status."""
    return {
        "reg_number": str(row[0]),
        "base_reg_number": str(row[1]),
        "reg_type": str(row[2]),
        "registration_id": int(row[3]),
        "party_id": int(row[4]),
        "storage_path": str(row[5]),
        "status": status if status else int(row[6]),
    }


def generate_csv_file(csv_data: list, status_data: dict) -> dict:
    """Build csv file, saved to storage, update status data with storage link."""
    filename = status_data.get("csv_file_name")
    file_data: str = CSV_HEADER
    for row in csv_data:
        file_data += CSV_LINE.format(
            reg_num=row.get("reg_number"),
            base_reg_num=row.get("base_reg_number"),
            reg_type=row.get("reg_type"),
            reg_id=row.get("registration_id"),
            party_id=row.get("party_id"),
            storage_path=row.get("storage_path"),
            status=row.get("status"),
        )
    link = GoogleStorageService.save_document_link(filename, file_data, 4, CONTENT_TYPE_CSV)
    status_data["csv_file_url"] = link
    logger.info(f"CSV file {filename} generated and saved to doc storage.")
    return status_data


def set_job_id(
    db_conn: psycopg2.extensions.connection, db_cursor: psycopg2.extensions.cursor, config: Config, job_id: int
):
    """Update the mail_report table batch job id and status for documents included in the batch run."""
    try:
        if not db_conn or not db_cursor:
            return
        sql_statement = UPDATE_JOB_QUERY.format(job_id=job_id, interval_hours=config.JOB_INTERVAL_HOURS)
        if config.RERUN_JOB_ID and config.RERUN_JOB_ID != "":
            sql_statement = RERUN_UPDATE_JOB_QUERY.format(rerun_job_id=config.RERUN_JOB_ID)
        elif config.RANGE_START_TS and config.RANGE_START_TS != "" and config.RANGE_END_TS and config.RANGE_END_TS != "":
            start_ts: str = str(config.RANGE_START_TS).replace("T", " ")
            end_ts: str = str(config.RANGE_END_TS).replace("T", " ")
            sql_statement = RANGE_UPDATE_JOB_QUERY.format(job_id=job_id, start_ts=start_ts, end_ts=end_ts)
        db_cursor.execute(sql_statement)
        db_conn.commit()
        logger.info(f"Update mail_reports batch job id completed for job id={job_id}")
    except (psycopg2.Error, Exception) as err:
        logger.error(f"Error running update mail_reports statement for job id={job_id}: {err}")


def get_mail_report_data(db_cursor: psycopg2.extensions.cursor, config: Config):
    """Get notification mail_reports table query results."""
    sql_statement = NOTIFICATION_QUERY.format(interval_hours=config.JOB_INTERVAL_HOURS)
    if config.RERUN_JOB_ID and config.RERUN_JOB_ID != "":
        sql_statement = RERUN_NOTIFICATION_QUERY.format(rerun_job_id=config.RERUN_JOB_ID)
    elif config.RANGE_START_TS and config.RANGE_START_TS != "" and config.RANGE_END_TS and config.RANGE_END_TS != "":
        start_ts: str = str(config.RANGE_START_TS).replace("T", " ")
        end_ts: str = str(config.RANGE_END_TS).replace("T", " ")
        sql_statement = RANGE_NOTIFICATION_QUERY.format(start_ts=start_ts, end_ts=end_ts)
    logger.info(f"Executing query to get mail report data: {sql_statement}")
    db_cursor.execute(sql_statement)
    return db_cursor.fetchall()


def batch_reports(status_data: dict, rows) -> dict:
    """
    Build the document delivery ZIP file from individual reports in document storage.
    Save the zip file to doc storage along with the count file.
    Capture the status of the individual reports as a csv row. Save the csv file to doc storage
    and make available to the notfication service as a download link in status_data as csv_file_url.

    Args:
        status_data: Dictionary to store job status information.
        rows: Database query rows - record set from the mail_reports tables.

    Returns:
        Updated status_data with zip file counts zip_file_count and zip_file_error_count
    """
    count: int = 0
    zip_error_count: int = 0  # Report data exists in doc storage but error adding to zip file.
    csv_data = []
    report_data = None
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_data:
        for row in rows:
            try:
                report_id = int(row[7])
                if row[5]:
                    storage_name = str(row[5])
                    report_data = GoogleStorageService.get_document(storage_name)
                    zip_data.writestr(storage_name[11:], report_data)
                    csv_data.append(get_csv_data(row, 201))
                    count += 1
                else:
                    logger.warning(f"No mail report found for id={report_id}, status={int(row[6])}")
                    csv_data.append(get_csv_data(row, None))
            except Exception as report_err:
                logger.error(f"Notification report failed for mail_reports id={report_id}: {report_err}")
                zip_error_count += 1
                csv_data.append(get_csv_data(row, 500))
    if count > 0:
        GoogleStorageService.save_document(
            status_data.get("delivery_zip_file_name"), zip_buffer.getvalue(), CONTENT_TYPE_ZIP
        )
    GoogleStorageService.save_document(
        status_data.get("delivery_count_file_name"), str(count) + "\n", CONTENT_TYPE_TEXT
    )
    status_data = generate_csv_file(csv_data, status_data)
    status_data["zip_file_count"] = count
    status_data["zip_file_error_count"] = zip_error_count
    logger.info(f"batch_reports completed zip file count={count} error count={zip_error_count}.")
    return status_data


def job(config: Config):
    """
    Execute the job:
        Run a query to get the document storage paths for the secured party notification reports
        (already generated) to include in the job.
        Track summary status in the status_data dictionary.
        Track individual report status in the csv data.
        Build a zip file of reports with the BCMail+ naming convention.
        Save the zip file to doc storage along with the count file.
        Save the csv file to doc storage, make available to staff on request or as a email recipient.
        Send a job status email with the csv file as a link.

        There are 3 query options available by environment variables chosen in the following order: 
            1. Re-run a a previous job by setting the RERUN_JOB_ID environment variable. Use this option
               if a record with an error status has been manually updated/corrected.
            2. Run by UTC TZ timestamp range by setting the environment variables RANGE_START_TS and RANGE_END_TS.
               Use the ISO timestamp format YYYY-MM-DDTHH24:MI:SS with no tz offset: for example 2025-06-03T07:00:00.
            3. Default include all records within the last x hours at the time the job runs, where x
               is the environment variable JOB_INTERVAL_HOURS value. It is safe to include an overlap
               as this query excludes records with an existing job id. 

    TO DO:
        Use a GCP ephemeral disk to build the zip file.
        Use existing document delivery job tracking framework. Replace or in addition to status_data.
        Conditionally add BCMail+ delivery via SFTP only if sftp env vars exist (PROD only).

    Args:
        config: Job configuration containing environment variables.

    Returns:
    """
    notify_client = Notify(config)
    db_conn: psycopg2.extensions.connection
    db_cursor: psycopg2.extensions.cursor
    try:
        logger.info("Getting database connection and cursor.")
        db_conn = psycopg2.connect(dsn=config.APP_DATABASE_URI)
        db_cursor = db_conn.cursor()
        status_data = run_summary_query(db_conn, db_cursor, config)
        if status_data.get("total_count") < 1:  # Non-PROD
            if config.RERUN_JOB_ID and config.RERUN_JOB_ID != "":
                logger.info(f"No notifications found for rerun job id={config.RERUN_JOB_ID}.")
            elif config.RANGE_START_TS and config.RANGE_START_TS != "" and config.RANGE_END_TS and config.RANGE_END_TS != "":
                logger.info(f"No notifications found for ts range={config.RANGE_START_TS}-{config.RANGE_END_TS}.")
            else:
                logger.info(f"No notifications found within the last={config.JOB_INTERVAL_HOURS} hours.")
            notify_client.send_status(status_data)
            return
        rows = get_mail_report_data(db_cursor, config)
        status_data = batch_reports(status_data, rows)
        set_job_id(db_conn, db_cursor, config, status_data.get("batch_job_id"))
        logger.info("Run completed: sending email.")
        notify_client.send_status(status_data)
        job_message: str = f"Run successful: status info {json.dumps(status_data)}."
    except (psycopg2.Error, Exception) as err:
        job_message: str = f"Run failed: {str(err)}."
        logger.error(job_message)
        notify_client.send_status_error(str(err))
        sys.exit(1)  # Retry Job Task by exiting the process
    finally:
        # Clean up: Close the database cursor and connection
        with suppress(Exception):
            db_cursor.close()
        with suppress(Exception):
            db_conn.close()
