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
import json
import sys
from contextlib import suppress
from datetime import datetime as _datetime
from datetime import timezone

import psycopg2

from secured_party_notification.config import Config
from secured_party_notification.services.document_storage.storage_service import GoogleStorageService
from secured_party_notification.services.notify import Notify
from secured_party_notification.services.report.report import Report
from secured_party_notification.utils.logging import logger

CONTENT_TYPE_CSV = "text/csv"
CONTENT_TYPE_PDF = "application/pdf"
BATCH_FILE_DOC_NAME = "batch-notifications-{batch_job_id}.pdf"
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


def get_batch_doc_storage_name(batch_job_id: str):
    """Get a batch file document storage name in the format YYYY/MM/DD/batch-notifications-{batch_job_id}.pdf."""
    name = _datetime.now(timezone.utc).isoformat()[:10]
    name = name.replace("-", "/") + "/" + BATCH_FILE_DOC_NAME.format(batch_job_id=batch_job_id)
    return name


def get_csv_doc_storage_name(batch_job_id: str):
    """Get a csv file document storage name in the format YYYY/MM/DD/batch-notifications-status-{batch_job_id}.csv."""
    name = _datetime.now(timezone.utc).isoformat()[:10]
    name = name.replace("-", "/") + "/" + CSV_FILE_DOC_NAME.format(batch_job_id=batch_job_id)
    return name


def run_summary_query(
    db_conn: psycopg2.extensions.connection, db_cursor: psycopg2.extensions.cursor, config: Config
) -> dict:
    """Execute the summary information query."""
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
        logger.info(f"Status query results: {str(status_data)}")
    except (psycopg2.Error, Exception) as err:
        error_message = f"Error attempting to run summary query: {err}"
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
        db_cursor.execute(sql_statement)
        db_conn.commit()
        logger.info(f"Update mail_reports batch job id completed for job id={job_id}")
    except (psycopg2.Error, Exception) as err:
        logger.error(f"Error running update mail_reports statement for job id={job_id}: {err}")


def get_mail_report_data(db_cursor: psycopg2.extensions.cursor, config: Config):
    """Get notification mail_reports table query results."""
    sql_statement = NOTIFICATION_QUERY.format(interval_hours=config.JOB_INTERVAL_HOURS)
    db_cursor.execute(sql_statement)
    return db_cursor.fetchall()


def job(config: Config):  # pylint: disable=too-many-locals,too-many-statements
    """Execute the job."""
    notify_client = Notify(config)
    db_conn: psycopg2.extensions.connection
    db_cursor: psycopg2.extensions.cursor
    try:
        logger.info("Getting database connection and cursor.")
        db_conn = psycopg2.connect(dsn=config.APP_DATABASE_URI)
        db_cursor = db_conn.cursor()
        csv_data = []
        report_data = None
        status_data = run_summary_query(db_conn, db_cursor, config)
        if status_data.get("total_count") < 1:  # Non-PROD
            logger.info(f"No notifications within the last {config.JOB_INTERVAL_HOURS} hours.")
            notify_client.send_status(status_data)
            return
        rows = get_mail_report_data(db_cursor, config)
        merge_reports = []  # Merge in batches of 10. Could make configurable. Or remove batch file if not needed.
        merge_counter: int = 0
        for row in rows:
            try:
                report_id = int(row[7])
                if row[5]:
                    merge_reports.append(GoogleStorageService.get_document(str(row[5])))
                    csv_data.append(get_csv_data(row, 201))
                    merge_counter += 1
                else:
                    logger.warning(f"No mail report found for id={report_id}, status={int(row[6])}")
                    csv_data.append(get_csv_data(row, None))
                if merge_counter == 10:
                    report_data, status = Report.batch_merge(merge_reports)
                    logger.info(f"Batch report merge 10 status={status}")
                    merge_reports = [report_data]
                    merge_counter = 0
            except Exception as report_err:
                logger.error(f"Notification report failed for mail_reports id={report_id}: {report_err}")
                csv_data.append(get_csv_data(row, 500))
        if merge_counter > 0:  # Check for final batch report merge.
            report_data, status = Report.batch_merge(merge_reports)
            logger.info(f"Batch report final merge {merge_counter} status={status}")
        set_job_id(db_conn, db_cursor, config, status_data.get("batch_job_id"))
        if report_data:
            GoogleStorageService.save_document(status_data.get("batch_file_name"), report_data, CONTENT_TYPE_PDF)
            logger.info("Batch file saved to document storage.")
        status_data = generate_csv_file(csv_data, status_data)
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
