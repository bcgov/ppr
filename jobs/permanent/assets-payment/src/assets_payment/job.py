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
from http import HTTPStatus
from typing import Final

import psycopg2

from assets_payment.config import Config
from assets_payment.services.notify import Notify
from assets_payment.services.payment_client import SBCPaymentClient
from assets_payment.utils.logging import logger

PPR_TRACKING_TYPE: str = "PPR_PAYMENT"
MHR_TRACKING_TYPE: str = "MHR_PAYMENT"
STATUS_TRACKING_TYPE: str = "PAYMENT_STATUS_JOB"
STATUS_JOB_ID: int = 1  # Does not matter as tracking type is only used by this job.
TRACKING_MESSAGE_EXPIRED = "07: draft pending status EXPIRED for draft {draft_id} invoice id={invoice_id}."
NOTIFY_STATUS_DATA = {
    "ppr_complete": -1,
    "ppr_errors": -1,
    "ppr_expired": -1,
    "mhr_complete": -1,
    "mhr_errors": -1,
    "mhr_expired": -1,
}

STATUS_QUERY = """
SELECT (SELECT COUNT(e.id)
          FROM event_tracking e
         WHERE e.event_tracking_type = 'PPR_PAYMENT'
           AND e.status = 200
           AND e.event_ts > now() - interval '1 days'
           AND LEFT(e.message, 2) = '09') AS ppr_completed,
       (SELECT COUNT(e.id)
          FROM event_tracking e
         WHERE e.event_tracking_type = 'PPR_PAYMENT'
           AND e.event_ts > now() - interval '1 days'
           AND LEFT(e.message, 2) IN ('02', '03', '04')) AS ppr_errors,
       (SELECT COUNT(e.id)
          FROM event_tracking e
         WHERE e.event_tracking_type = 'PPR_PAYMENT'
           AND e.event_ts > now() - interval '10 days'
           AND LEFT(e.message, 2) = '01'
           AND NOT EXISTS (SELECT e2.id
                             FROM event_tracking e2
                            WHERE e2.key_id = e.key_id
                              AND e2.event_tracking_type = e.event_tracking_type
                              AND LEFT(e2.message, 2) IN ('05', '06', '07', '09'))
          AND e.event_ts < (now() at time zone 'utc') - interval '{ppr_expiry_client} hours') AS ppr_expired,
       (SELECT COUNT(e.id)
          FROM event_tracking e
         WHERE e.event_tracking_type = 'MHR_PAYMENT'
           AND e.status = 200
           AND e.event_ts > now() - interval '1 days'
           AND LEFT(e.message, 2) = '09') AS mhr_completed,
       (SELECT COUNT(e.id)
          FROM event_tracking e
         WHERE e.event_tracking_type = 'MHR_PAYMENT'
           AND e.event_ts > now() - interval '1 days'
           AND LEFT(e.message, 2) IN ('02', '03', '04')) AS mhr_errors,
       (SELECT COUNT(e.id)
          FROM event_tracking e
         WHERE e.event_tracking_type = 'MHR_PAYMENT'
           AND e.event_ts > now() - interval '10 days'
           AND LEFT(e.message, 2) = '01'
           AND NOT EXISTS (SELECT e2.id
                             FROM event_tracking e2
                            WHERE e2.key_id = e.key_id
                              AND e2.event_tracking_type = e.event_tracking_type
                              AND LEFT(e2.message, 2) IN ('05', '06', '07', '09'))
          AND e.event_ts < (now() at time zone 'utc') - interval '{mhr_expiry_client} hours') AS mhr_expired
"""
MHR_EXPIRED_QUERY = """
SELECT id, user_id, mhr_number
  FROM mhr_drafts
 WHERE user_id IN
 (SELECT Distinct CAST(e.key_id as text)
  FROM event_tracking e
 WHERE e.event_tracking_type = 'MHR_PAYMENT'
   AND e.event_ts > now() - interval '10 days'
   AND LEFT(e.message, 2) = '01'
   AND NOT EXISTS (SELECT e2.id
                     FROM event_tracking e2
                    WHERE e2.key_id = e.key_id
                      AND e2.event_tracking_type = e.event_tracking_type
                      AND LEFT(e2.message, 2) IN ('05', '06', '07', '09'))
  AND e.event_ts < (now() at time zone 'utc') - interval '{expire_hours} hours')
 ORDER BY id
"""
MHR_RESTORE_STATUS = """
UPDATE mhr_registrations SET status_type = CAST(mhr_drafts.draft ->> 'status' AS mhr_registration_status_type)
  FROM mhr_drafts
 WHERE mhr_drafts.id IN ({draft_ids})
   AND mhr_drafts.mhr_number IS NOT NULL
   AND mhr_drafts.draft ->> 'status' IS NOT NULL
   AND mhr_drafts.mhr_number = mhr_registrations.mhr_number
   AND mhr_registrations.registration_type IN ('MHREG', 'MHREG_CONVERSION')
   AND mhr_registrations.status_type = 'DRAFT'
"""
MHR_UPDATE_DRAFT = """
UPDATE mhr_drafts
   SET user_id = NULL, draft_number = SUBSTR(draft_number, 2)
 WHERE id IN ({draft_ids})
   AND LEFT(draft_number, 1) = 'P'
"""
PPR_EXPIRED_QUERY = """
SELECT id, user_id, registration_number
  FROM drafts
 WHERE user_id IN
 (SELECT Distinct CAST(e.key_id as text)
  FROM event_tracking e
 WHERE e.event_tracking_type = 'PPR_PAYMENT'
   AND e.event_ts > now() - interval '10 days'
   AND LEFT(e.message, 2) = '01'
   AND NOT EXISTS (SELECT e2.id
                     FROM event_tracking e2
                    WHERE e2.key_id = e.key_id
                      AND e2.event_tracking_type = e.event_tracking_type
                      AND LEFT(e2.message, 2) IN ('05', '06', '07', '09'))
  AND e.event_ts < (now() at time zone 'utc') - interval '{expire_hours} hours')
 ORDER BY id
"""
PPR_RESTORE_STATUS = """
UPDATE registrations SET ver_pybassed = 'Y'
  FROM drafts
 WHERE drafts.id IN ({draft_ids})
   AND drafts.registration_number IS NOT NULL
   AND drafts.registration_number = registrations.registration_number
   AND registrations.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')
   AND registrations.ver_bypassed = 'L'
"""
PPR_UPDATE_DRAFT = """
UPDATE drafts
   SET user_id = draft->>'username', document_number = SUBSTR(document_number, 2)
 WHERE id IN ({draft_ids})
   AND LEFT(document_number, 1) = 'P'
"""
INSERT_EVENT: Final = """
INSERT INTO event_tracking(id, key_id, event_ts, event_tracking_type, status, message)
  VALUES(nextval('event_tracking_id_seq'), {job_id}, CURRENT_TIMESTAMP  at time zone 'utc', '{tracking_type}',
         {job_status}, '{job_message}')
"""


def track_event(  # pylint: disable=too-many-positional-arguments,too-many-arguments
    db_conn: psycopg2.extensions.connection,
    db_cursor: psycopg2.extensions.cursor,
    job_id: int,
    tracking_type: str,
    status: int,
    message: str,
):
    """Capture the job run in the event tracking table."""
    try:
        if not db_conn or not db_cursor:
            return
        sql_statement = INSERT_EVENT.format(
            job_id=job_id, tracking_type=tracking_type, job_status=status, job_message=message[0:7999]
        )
        db_cursor.execute(sql_statement)
        db_conn.commit()
    except (psycopg2.Error, Exception) as err:
        error_message = f"Error attempting event_tracking insert: {err}"
        logger.error(error_message)


def restore_mhr_status(
    db_conn: psycopg2.extensions.connection, db_cursor: psycopg2.extensions.cursor, mhr_numbers: str, draft_ids: str
):
    """Revert MHR home registrations locked due to a payment pending status to the previous active status."""
    try:
        if not db_conn or not db_cursor:
            return
        if not mhr_numbers or not draft_ids:
            logger.info("restore_mhr_status no mhr_numbers to update: step skipped.")
            return
        sql_statement = MHR_RESTORE_STATUS.format(draft_ids=draft_ids)
        db_cursor.execute(sql_statement)
        db_conn.commit()
        logger.info(f"Restore MHR home status updated for draft ID's {draft_ids} mhr numbers {mhr_numbers}")
    except (psycopg2.Error, Exception) as err:
        error_message = f"Error attempting restore mhr base registration status {err}"
        logger.error(error_message)


def restore_mhr_draft(db_conn: psycopg2.extensions.connection, db_cursor: psycopg2.extensions.cursor, draft_ids: str):
    """Revert MHR drafts in a payment pending state to the regular draft state."""
    try:
        if not db_conn or not db_cursor:
            return
        if not draft_ids:
            logger.info("restore_mhr_draft no drafts to update: step skipped.")
            return
        sql_statement = MHR_UPDATE_DRAFT.format(draft_ids=draft_ids)
        db_cursor.execute(sql_statement)
        db_conn.commit()
        logger.info(f"Restore MHR draft state updated for draft ID's {draft_ids}")
    except (psycopg2.Error, Exception) as err:
        error_message = f"Error attempting restore mhr draft state {err}"
        logger.error(error_message)


def restore_ppr_status(
    db_conn: psycopg2.extensions.connection, db_cursor: psycopg2.extensions.cursor, reg_numbers: str, draft_ids: str
):
    """Unlock PPR base registrations locked due to a payment pending status."""
    try:
        if not db_conn or not db_cursor:
            return
        if not reg_numbers or not draft_ids:
            logger.info("restore_ppr_status no reg_numbers to update: step skipped.")
            return
        sql_statement = PPR_RESTORE_STATUS.format(draft_ids=draft_ids)
        db_cursor.execute(sql_statement)
        db_conn.commit()
        logger.info(f"Restore MHR home status updated for draft ID's {draft_ids} base reg numbers {reg_numbers}")
    except (psycopg2.Error, Exception) as err:
        error_message = f"Error attempting restore mhr base registration status {err}"
        logger.error(error_message)


def restore_ppr_draft(db_conn: psycopg2.extensions.connection, db_cursor: psycopg2.extensions.cursor, draft_ids: str):
    """Revert PPR drafts in a payment pending state to the regular draft state."""
    try:
        if not db_conn or not db_cursor:
            return
        if not draft_ids:
            logger.info("restore_ppr_draft no drafts to update: step skipped.")
            return
        sql_statement = PPR_UPDATE_DRAFT.format(draft_ids=draft_ids)
        db_cursor.execute(sql_statement)
        db_conn.commit()
        logger.info(f"Restore PPR draft state updated for draft ID's {draft_ids}")
    except (psycopg2.Error, Exception) as err:
        error_message = f"Error attempting restore ppr draft state {err}"
        logger.error(error_message)


def run_status_query(
    db_conn: psycopg2.extensions.connection, db_cursor: psycopg2.extensions.cursor, config: Config
) -> dict:
    """Execute the summary information status query."""
    status_data: dict = copy.deepcopy(NOTIFY_STATUS_DATA)
    try:
        ppr_expiry = config.PPR_EXPIRY_CLIENT_HOURS
        mhr_expiry = config.MHR_EXPIRY_CLIENT_HOURS
        sql_statement = STATUS_QUERY.format(ppr_expiry_client=ppr_expiry, mhr_expiry_client=mhr_expiry)
        logger.info(f"Executing status query: {sql_statement}")
        db_cursor.execute(sql_statement)
        row = db_cursor.fetchone()
        status_data["ppr_complete"] = int(row[0])
        status_data["ppr_errors"] = int(row[1])
        status_data["ppr_expired"] = int(row[2])
        status_data["mhr_complete"] = int(row[3])
        status_data["mhr_errors"] = int(row[4])
        status_data["mhr_expired"] = int(row[5])
        logger.info(f"Status query results: {str(status_data)}")
    except (psycopg2.Error, Exception) as err:
        error_message = f"Error attempting to run status query: {err}"
        logger.error(error_message)
    return status_data


def cancel_ppr_expired(  # pylint: disable=too-many-locals
    db_conn: psycopg2.extensions.connection,
    db_cursor: psycopg2.extensions.cursor,
    config: Config,
    status_data: dict,
    pay_client: SBCPaymentClient,
) -> dict:
    """Revert draft status and delete payment for expired ppr pending payment registrations."""
    cancel_count: int = 0
    if not status_data.get("ppr_expired") or status_data.get("ppr_expired") < 1:
        logger.info("No expired PPR pending payments to cancel")
        return cancel_count
    draft_ids: str = ""
    invoice_ids: str = ""
    error_draft_ids: str = ""
    reg_numbers: str = ""
    try:
        if not db_conn or not db_cursor:
            return cancel_count
        sql_statement = PPR_EXPIRED_QUERY.format(expire_hours=config.PPR_EXPIRY_CLIENT_HOURS)
        db_cursor.execute(sql_statement)
        rows = db_cursor.fetchall()
        for row in rows:
            cancel_count += 1
            draft_id: int = int(row[0])
            invoice_id: str = int(row[1])
            reg_number: str = str(row[2]) if row[2] else ""
            if invoice_ids:
                invoice_ids += ","
            invoice_ids += str(invoice_id)
            if draft_ids:
                draft_ids += ","
            draft_ids += str(draft_id)
            if reg_number:
                if reg_numbers:
                    reg_numbers += ","
                reg_numbers += reg_number
            logger.info(f"Cancelling payment invoice id={invoice_id}, draft id={draft_id} base reg={reg_number}")
            pay_status: int = pay_client.delete_pending_payment(invoice_id)
            logger.info(f"Invoice {invoice_id} delete pending payment status={pay_status}")
            if pay_status >= 300:
                if error_draft_ids:
                    error_draft_ids += ","
                error_draft_ids += str(draft_id)
            event_msg: str = TRACKING_MESSAGE_EXPIRED.format(draft_id=draft_id, invoice_id=invoice_id)
            track_event(db_conn, db_cursor, int(invoice_id), PPR_TRACKING_TYPE, pay_status, event_msg)
        status_data["ppr_cancel_count"] = cancel_count
        status_data["ppr_invoice_ids"] = invoice_ids
        status_data["ppr_draft_ids"] = draft_ids
        status_data["ppr_reg_numbers"] = reg_numbers
        status_data["ppr_error_ids"] = error_draft_ids
        restore_ppr_status(db_conn, db_cursor, reg_numbers, draft_ids)
        restore_ppr_draft(db_conn, db_cursor, draft_ids)
    except (psycopg2.Error, Exception) as err:
        error_message = f"Error attempting event_tracking insert: {err}"
        logger.error(error_message)
    return cancel_count


def cancel_mhr_expired(  # pylint: disable=too-many-locals
    db_conn: psycopg2.extensions.connection,
    db_cursor: psycopg2.extensions.cursor,
    config: Config,
    status_data: dict,
    pay_client: SBCPaymentClient,
) -> dict:
    """Revert draft status and delete payment for expired ppr pending payment registrations."""
    cancel_count: int = 0
    if not status_data.get("mhr_expired") or status_data.get("mhr_expired") < 1:
        logger.info("No expired MHR pending payments to cancel")
        return cancel_count
    draft_ids: str = ""
    invoice_ids: str = ""
    error_draft_ids: str = ""
    mhr_numbers: str = ""
    try:
        if not db_conn or not db_cursor:
            return cancel_count
        sql_statement = MHR_EXPIRED_QUERY.format(expire_hours=config.MHR_EXPIRY_CLIENT_HOURS)
        db_cursor.execute(sql_statement)
        rows = db_cursor.fetchall()
        for row in rows:
            cancel_count += 1
            draft_id: int = int(row[0])
            invoice_id: str = int(row[1])
            mhr_number: str = str(row[2]) if row[2] else ""
            if invoice_ids:
                invoice_ids += ","
            invoice_ids += str(invoice_id)
            if draft_ids:
                draft_ids += ","
            draft_ids += str(draft_id)
            if mhr_number:
                if mhr_numbers:
                    mhr_numbers += ","
                mhr_numbers += mhr_number
            logger.info(f"Cancelling payment invoice id={invoice_id}, draft id={draft_id} mhr={mhr_number}")
            pay_status: int = pay_client.delete_pending_payment(invoice_id)
            logger.info(f"Invoice {invoice_id} delete pending payment status={pay_status}")
            if pay_status >= 300:
                if error_draft_ids:
                    error_draft_ids += ","
                error_draft_ids += str(draft_id)
            event_msg: str = TRACKING_MESSAGE_EXPIRED.format(draft_id=draft_id, invoice_id=invoice_id)
            track_event(db_conn, db_cursor, int(invoice_id), MHR_TRACKING_TYPE, pay_status, event_msg)
        status_data["mhr_cancel_count"] = cancel_count
        status_data["mhr_invoice_ids"] = invoice_ids
        status_data["mhr_draft_ids"] = draft_ids
        status_data["mhr_numbers"] = mhr_numbers
        status_data["mhr_error_ids"] = error_draft_ids
        restore_mhr_status(db_conn, db_cursor, mhr_numbers, draft_ids)
        restore_mhr_draft(db_conn, db_cursor, draft_ids)
    except (psycopg2.Error, Exception) as err:
        error_message = f"Error attempting event_tracking insert: {err}"
        logger.error(error_message)
    return cancel_count


def job(config: Config, sa_token=None):
    """Execute the job."""
    pay_client: SBCPaymentClient = SBCPaymentClient(config, sa_token)
    notify_client = Notify(config, sa_token)
    db_conn: psycopg2.extensions.connection
    db_cursor: psycopg2.extensions.cursor
    try:
        logger.info("Getting database connection and cursor.")
        db_conn = psycopg2.connect(dsn=config.APP_DATABASE_URI)
        db_cursor = db_conn.cursor()

        status_data = run_status_query(db_conn, db_cursor, config)

        if not config.MHR_EXPIRY_CLIENT_HOURS or int(config.MHR_EXPIRY_CLIENT_HOURS) < 1:
            logger.info("MHR client expiry hours not configured: skipping MHR cancellations.")
        else:
            cancel_mhr_expired(db_conn, db_cursor, config, status_data, pay_client)
        if not config.PPR_EXPIRY_CLIENT_HOURS or int(config.PPR_EXPIRY_CLIENT_HOURS) < 1:
            logger.info("PPR client expiry hours not configured: skipping PPR cancellations.")
        else:
            cancel_ppr_expired(db_conn, db_cursor, config, status_data, pay_client)

        logger.info("Run completed: sending email.")
        notify_client.send_status(status_data)
        job_message: str = f"Run successful: status info {json.dumps(status_data)}."
        track_event(db_conn, db_cursor, STATUS_JOB_ID, STATUS_TRACKING_TYPE, HTTPStatus.OK, job_message)
    except (psycopg2.Error, Exception) as err:
        job_message: str = f"Run failed: {str(err)}."
        logger.error(job_message)
        notify_client.send_status_error(str(err))
        track_event(
            db_conn, db_cursor, STATUS_JOB_ID, STATUS_TRACKING_TYPE, HTTPStatus.INTERNAL_SERVER_ERROR, job_message
        )
        sys.exit(1)  # Retry Job Task by exiting the process
    finally:
        # Clean up: Close the database cursor and connection
        with suppress(Exception):
            db_cursor.close()
        with suppress(Exception):
            db_conn.close()
