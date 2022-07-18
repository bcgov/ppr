# Copyright © 2022 Province of British Columbia
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
"""This module contains the services used by the Job Tracking Service."""
from contextlib import suppress

import psycopg2

from ppr_discharges_for_mhr.common.enum import BaseEnum, auto
from ppr_discharges_for_mhr.services.logging import logging


class JobStateEnum(BaseEnum):
    DONE = auto()
    ERROR = auto()
    RUNNING = auto()


class JobTracker:
    """JobTracker logs job activity to a database."""

    def __init__(self, **options):
        """Initialize the job tracker."""
        self.conn = None
        if options:
            self.setup(**options)

    def setup(self, **options):
        """Set the configuration for the job tracker."""
        self.host = options.get('host')
        self.port = int(options.get('port', '5432'))
        self.dbname = options.get('dbname')
        self.user = options.get('user')
        self.password = options.get('password')
        self.uri = options.get('uri')

    def _connect(self) -> psycopg2.extensions.connection:
        """Internal function to create the database connection.
        
        The underlying mechanism is a pool, so we can freely open/close without significant overhead.
        """
        if not self.conn:
            if self.uri:
                opts = {'dsn': self.uri}
            else:
                opts = {'host': self.host,
                        'port': self.port,
                        'dbname': self.dbname,
                        'user': self.user,
                        'password': self.password}
            self.conn = psycopg2.connect(**opts)
        return self.conn

    def _get_job_id(self, program_name: str, job_name: str) -> int:
        """Get the id of the job."""
        try:
            conn = self._connect()
            cursor = conn.cursor()

            query = """select id from jobs where program_name = %s and name = %s"""

            cursor.execute(query, (program_name, job_name))
            job_id = cursor.fetchone()[0]

            return job_id

        except (Exception, psycopg2.Error) as error:
            logging.error("Error while fetching data from PostgreSQL", error)

        finally:
            # closing database connection.
            if conn:
                with suppress(Exception):
                    cursor.close()
    
    def start_job(self, program_name: str, job_name: str, job_state: JobStateEnum) -> int:
        """ insert a new vendor into the vendors table """
        sql = """insert into job_runs (id, job_id, start_time, end_time, state)
                 values (nextval('job_runs_id_seq'::regclass), %s, now(), null, %s)
                 RETURNING id;"""
        conn = None

        job_id = self._get_job_id(program_name, job_name)
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(sql, (job_id, job_state))
            
            running_job_id = cursor.fetchone()[0]
            conn.commit()

            return running_job_id

        except (Exception, psycopg2.DatabaseError) as error:
            logging.error("Error while creating job run record", error)
        finally:
            if cursor is not None:
                cursor.close()

    def stop_job(self,
                 running_id: int,
                 job_state: JobStateEnum,
                 error_code: str = None,
                 error_additional_details: str = None):
        """Update the job to it's final state."""

        sql = """update job_runs set end_time=now(), state=%s where id=%s"""

        err_sql = """insert into job_run_errors (id, job_run_id, error_id, details, created_on)
                     values( nextval('job_run_errors_id_seq'::regclass), %s,
                     (select id from error_codes where program_name=
                             (select program_name from jobs as j join job_runs as jr on j.id=jr.job_id where jr.id = %s)
                             and code=%s),%s,now())"""

        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(sql, (job_state, running_id))

            if job_state == JobStateEnum.ERROR:
                cursor.execute(err_sql, (running_id, running_id, error_code, error_additional_details))
            
            conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            logging.error("Error while closing the job run record", error)
        finally:
            if cursor is not None:
                cursor.close()


# Start script
if __name__ == "__main__":
    opts = {'host': 'localhost', 'port': 5432, 'dbname': 'jobs', 'user': 'job_runner', 'password': 'jw8s0F4'}
    job = JobTracker(**opts)
    job_id = job._get_job_id('assets', 'ppr_mhr_dissolutions')

    running_id = job.start_job('assets', 'ppr_mhr_dissolutions', JobStateEnum.RUNNING)

    job.stop_job(running_id, JobStateEnum.DONE)

    running_id = job.start_job('assets', 'ppr_mhr_dissolutions', JobStateEnum.RUNNING)

    job.stop_job(running_id, JobStateEnum.ERROR, '001', 'some general error info')

    print(job_id)
