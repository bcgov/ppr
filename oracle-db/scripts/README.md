# Scripts to create the ppr_mgr schema

Connect as sys with the sysdba role to create the tablespaces and ppr_mgr schema user.
Run the script create-table-space-schema.sql

Run the rest of the scripts as the ppr_mgr user in the following order.

1. create_type_tables_ddl.sql
1. create_tables_ddl.sql
1. sqlalchemy_ddl.sql
1. create_sequences_ddl.sql
1. create_views_ddl.sql
1. create_plsql_functions_ddl.sql
1. insert_types.sql
1. insert_country_types.sql
1. insert_province_types.sql

## Note
The insert type scripts do not contain COMMIT statements.

See the ppr-api/test_data readme to insert API unit test data.
Update the followling ppr-api/.env file variables:

DATABASE_PASSWORD

DATABASE_URL

DATABASE_USERNAME

DATABASE_NAME

DATABASE_HOST

DATABASE_PORT
