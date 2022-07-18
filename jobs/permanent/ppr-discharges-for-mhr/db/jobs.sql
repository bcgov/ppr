
create database jobs;
create user job_runner WITH PASSWORD 'jw8s0F4';
create user job_owner WITH PASSWORD 'jownSF124';


CREATE SCHEMA jobs;

GRANT CONNECT ON DATABASE jobs TO job_owner;
GRANT USAGE ON SCHEMA public TO job_owner;
GRANT USAGE ON SCHEMA jobs TO job_owner;
GRANT ALL PRIVILEGES ON DATABASE jobs to job_owner;


GRANT CONNECT ON DATABASE jobs TO job_runner;
GRANT USAGE ON SCHEMA public TO job_runner;
GRANT USAGE ON SCHEMA jobs TO job_runner;

ALTER DEFAULT PRIVILEGES
FOR USER job_runner
IN SCHEMA jobs
GRANT SELECT, INSERT, UPDATE ON TABLES TO job_runner;

\c jobs job_owner

CREATE TYPE state_type AS ENUM('DONE', 'ERROR', 'RUNNING');

create table programs (
    name VARCHAR ( 250 ) PRIMARY KEY,
	description VARCHAR ( 2048 ) NULL
);

create table jobs (
    id serial PRIMARY KEY,
    name VARCHAR ( 250 ) NOT NULL,
    program_name VARCHAR ( 250 ) NOT NULL,
	description VARCHAR ( 2048 ) NULL,
    schedule VARCHAR ( 20 ),
    FOREIGN KEY (program_name)
      REFERENCES programs (name),
    UNIQUE (program_name, name)
);

CREATE TABLE error_codes (
    id serial PRIMARY KEY,
	code VARCHAR ( 50 ) NOT NULL,
	program_name VARCHAR ( 250 ),
	description VARCHAR ( 2048 ) NULL,
    FOREIGN KEY (program_name)
      REFERENCES programs (name),
    UNIQUE (program_name, code)
);

create table job_runs (
    id serial PRIMARY KEY,
    job_id int4 NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NULL,
    state state_type NOT NULL,
    FOREIGN KEY (job_id)
      REFERENCES jobs (id)
);

CREATE TABLE job_run_errors (
	id serial PRIMARY KEY,
    job_run_id int4 NOT NULL,
    error_id int4 NOT NULL,
    details TEXT,
	created_on TIMESTAMP NOT NULL,
    FOREIGN KEY (job_run_id)
      REFERENCES job_runs (id),
    FOREIGN KEY (error_id)
      REFERENCES error_codes (id)
);

GRANT SELECT on programs to job_runner;
GRANT SELECT on error_codes to job_runner;
GRANT SELECT on jobs to job_runner;
GRANT SELECT, INSERT, UPDATE on job_runs to job_runner;
GRANT SELECT, INSERT, UPDATE on job_run_errors to job_runner;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA jobs TO job_runner;
GRANT USAGE, SELECT ON SEQUENCE job_runs_id_seq TO job_runner;
GRANT USAGE, SELECT ON SEQUENCE job_run_errors_id_seq TO job_runner;

insert into programs (name, description)
values ('assets', 'the assets family of programs');

insert into error_codes (id, code, program_name, description)
values (nextval('error_codes_id_seq'::regclass), '001', 'assets', 'catch all error class');

DO $$
DECLARE
  example_job_id INTEGER;
  erro_job_id INTEGER;
BEGIN
  insert into jobs (id, name, program_name, description, schedule)
  values (nextval('jobs_id_seq'::regclass), 'ppr_mhr_dissolutions', 'assets', 'daily csv file of ppr dissolutions of mobile homes', '0 1 * * *')
  returning id into example_job_id;

  insert into job_runs (id, job_id, start_time, end_time, state)
  values (nextval('job_runs_id_seq'::regclass), example_job_id, now(), null, 'DONE');

  insert into job_runs (id, job_id, start_time, end_time, state)
  values (nextval('job_runs_id_seq'::regclass), example_job_id, now(), null, 'ERROR')
  returning id into erro_job_id;

  insert into job_run_errors (id, job_run_id, error_id, details, created_on)
  values( nextval('job_run_errors_id_seq'::regclass),
        erro_job_id,
        (select id from error_codes where program_name='assets' and code='001'),
        'something went wrong, don''t know why',
        now()
);

END $$;
