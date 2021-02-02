CREATE TABLESPACE PPR_DATA
   DATAFILE '/ORCL/ppr_data.dbf'
   SIZE 10m
   AUTOEXTEND ON NEXT 500k ONLINE;

CREATE TABLESPACE PPR_INDEX
   DATAFILE '/ORCL/ppr_index.dbf'
   SIZE 5m
   AUTOEXTEND ON NEXT 500k ONLINE;


ALTER SESSION SET CONTAINER = ORCLPDB1;

CREATE TABLESPACE PPR_DATA
   DATAFILE '/ORCL/ppr_data2.dbf'
   SIZE 10m
   AUTOEXTEND ON NEXT 500k ONLINE;

CREATE TABLESPACE PPR_INDEX
   DATAFILE '/ORCL/ppr_index2.dbf'
   SIZE 5m
   AUTOEXTEND ON NEXT 500k ONLINE;

SELECT TABLESPACE_NAME, STATUS, CONTENTS
FROM USER_TABLESPACES;

select tablespace_name, con_id from cdb_tablespaces;

EXIT;


-- Create the ppr schema object user
create user c##_ppr_mgr
  identified by pprManager
  default tablespace PPR_DATA
  TEMPORARY TABLESPACE TEMP
  profile DEFAULT
  quota unlimited on PPR_DATA
  quota unlimited on PPR_INDEX;

-- Grant/Revoke role privileges
grant resource to c##_ppr_mgr;
-- Grant/Revoke system privileges
grant all privileges to c##_ppr_mgr;

alter user c##_ppr_mgr account unlock identified by pprManager;

