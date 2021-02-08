
# PPR API Unit Test Data Scripts 

With a SQLAlchemy session run native SQL scripts to set up unit test data.
Intended for use only in local and development environments.

## Usage
From the ppr_api directory run:
    python ./test_data/create_test_data.py

## Details
Lines with comments starting with "--" are allowed.
Do not include COMMIT statements in the scripts.

### create_test_data.py
   The scripts run in the following order:
   1. ./test_reset.sql (resets all test data).
   2. ./create_first.sql (all test data statements that should run first).
   3. All the files in ./test_data sorted by name.

### run_one_file.py
Use for ad hoc execution of SQL statements contained in a single file. Edit to 
set the file name prior to running.
   