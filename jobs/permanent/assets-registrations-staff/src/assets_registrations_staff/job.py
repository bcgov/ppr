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
import sys
from contextlib import suppress
from typing import Final

import psycopg2

from assets_registrations_staff.config import Config
from assets_registrations_staff.utils.logging import logger

COUNT_QUERY: Final = """
SELECT (select count(mer.id)
         from mhr_extra_registrations mer
        where mer.account_id = 'ppr_staff'
          and (mer.removed_ind is null or mer.removed_ind != 'Y')
          and not exists (select r.id
                            from mhr_registrations r
                           where r.mhr_number = mer.mhr_number
                             and r.account_id = mer.account_id
                             and r.registration_ts > now() - interval '14 days')) AS other_delete_count,
      (select count(r.mhr_number)
         from mhr_registrations r
        where r.account_id = 'ppr_staff'
          and r.registration_type = 'MHREG'
         and not exists (select er.id
                           from mhr_extra_registrations er
                          where er.account_id = 'ppr_staff'
                            and er.mhr_number = r.mhr_number
                            and er.removed_ind = 'Y')
         and not exists (select r2.id
                           from mhr_registrations r2
                          where r2.account_id = r.account_id
                            and r2.mhr_number = r.mhr_number
                            and r2.account_id = r.account_id
                            and r2.registration_ts > now() - interval '14 days')) as staff_remove_count,
      (select string_agg(r.mhr_number, ',')
         from mhr_registrations r
        where r.account_id = 'ppr_staff'
          and r.registration_type = 'MHREG'
          and not exists (select er.id
                            from mhr_extra_registrations er
                           where er.account_id = 'ppr_staff'
                             and er.mhr_number = r.mhr_number
                             and er.removed_ind = 'Y')
          and not exists (select r2.id
                            from mhr_registrations r2
                           where r2.account_id = r.account_id
                             and r2.mhr_number = r.mhr_number
                             and r2.account_id = r.account_id
                             and r2.registration_ts > now() - interval '14 days')) as staff_reg_nums
"""
MHR_DELETE_OTHER_QUERY: Final = """
delete
  from mhr_extra_registrations mer
 where mer.account_id = 'ppr_staff'
   and (mer.removed_ind is null or mer.removed_ind != 'Y')
   and not exists (select r.id
                     from mhr_registrations r
                    where r.mhr_number = mer.mhr_number
                      and r.registration_ts > now() - interval '14 days')
"""
INSERT_EXTRA_REG: Final = """
INSERT INTO mhr_extra_registrations(id, account_id, mhr_number, removed_ind)
  VALUES(nextval('mhr_extra_registration_seq'), 'ppr_staff','{mhr_number}', 'Y')
"""


def delete_mhr_other(db_conn: psycopg2.extensions.connection, db_cursor: psycopg2.extensions.cursor):
    """Remove stale registrations created by non-staff from the mhr_other_registrations table."""
    try:
        if not db_conn or not db_cursor:
            return
        sql_statement = MHR_DELETE_OTHER_QUERY
        db_cursor.execute(sql_statement)
        db_conn.commit()
        logger.info("Delete stale other account registrations successful.")
    except (psycopg2.Error, Exception) as err:
        logger.error(f"Delete stale other account registrations failed: {err}.")


def remove_mhr_registration(
    db_conn: psycopg2.extensions.connection,
    db_cursor: psycopg2.extensions.cursor,
    mhr_num: str,
):
    """Create a record for a staff created new MH registration to be removed from the staff table as stale."""
    try:
        if not db_conn or not db_cursor:
            return
        sql_statement = INSERT_EXTRA_REG.format(mhr_number=mhr_num)
        db_cursor.execute(sql_statement)
        db_conn.commit()
    except (psycopg2.Error, Exception) as err:
        error_message = f"Error attempting mhr_extra_registrations insert MHR#={mhr_num}: {err}"
        logger.error(error_message)


def remove_mhr_staff_reg(
    db_conn: psycopg2.extensions.connection, db_cursor: psycopg2.extensions.cursor, count_data: dict
):
    """Revert MHR drafts in a payment pending state to the regular draft state."""
    try:
        if not db_conn or not db_cursor:
            return
        if not count_data.get("staff_reg_count") or not count_data.get("staff_reg_nums"):
            logger.info("remove_mhr_staff_reg no staff registrations to remove: step skipped.")
            return
        staff_mhr_nums: str = count_data.get("staff_reg_nums")
        mhr_numbers: list = staff_mhr_nums.split(",")
        for mhr_num in mhr_numbers:
            remove_mhr_registration(db_conn, db_cursor, mhr_num)
        logger.info(f"Remove staff MHR registrations completed for MHR numbers {staff_mhr_nums}")
    except (psycopg2.Error, Exception) as err:
        error_message = f"Remove staff MHR registrations failed: {err}"
        logger.error(error_message)


def run_count_query(db_conn: psycopg2.extensions.connection, db_cursor: psycopg2.extensions.cursor) -> dict:
    """Execute the count staff registrations query."""
    count_data: dict = {}
    try:
        sql_statement = COUNT_QUERY
        logger.info(f"Executing count query: {sql_statement}")
        db_cursor.execute(sql_statement)
        row = db_cursor.fetchone()
        count_data["other_reg_count"] = int(row[0])
        count_data["staff_reg_count"] = int(row[1])
        count_data["staff_reg_nums"] = str(row[2]) if row[2] else ""
        logger.info(f"Count query results: {str(count_data)}")
    except (psycopg2.Error, Exception) as err:
        error_message = f"Error attempting to run status query: {err}"
        logger.error(error_message)
    return count_data


def job(config: Config):
    """Execute the job."""
    db_conn: psycopg2.extensions.connection
    db_cursor: psycopg2.extensions.cursor
    try:
        logger.info("Getting database connection and cursor.")
        db_conn = psycopg2.connect(dsn=config.APP_DATABASE_URI)
        db_cursor = db_conn.cursor()
        count_data = run_count_query(db_conn, db_cursor)
        if not count_data.get("other_reg_count") or count_data.get("other_reg_count") < 1:
            logger.info("MHR no stale other account registrations: skipping MHR delete other account registrations.")
        else:
            delete_mhr_other(db_conn, db_cursor)
        remove_mhr_staff_reg(db_conn, db_cursor, count_data)
        logger.info("Run completed.")
    except (psycopg2.Error, Exception) as err:
        job_message: str = f"Run failed: {str(err)}."
        logger.error(job_message)
        sys.exit(1)  # Retry Job Task by exiting the process
    finally:
        # Clean up: Close the database cursor and connection
        with suppress(Exception):
            db_cursor.close()
        with suppress(Exception):
            db_conn.close()
