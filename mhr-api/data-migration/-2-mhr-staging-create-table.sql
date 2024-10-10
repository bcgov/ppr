-- Pre-migration
-- The first DB2 to PostgreSQL MHR data migration task: create the staging tables.
-- The table column names, data types, and lengths exactly match the DB2 definition.
-- DB2 legacy values are loaded as is into the staging tables.
-- Data transformation occurs after the staging tables are loaded.
-- DB2 table docdes is not needed: mhr_document_types contains the same data.
-- staging_mhr_addresses is used after the staging table load as part of the later data transformation step.
--
-- 1. Create table staging_mhr_manufacturer with the same definition as the DB2 manufact table.
-- 2. Create table staging_mhr_manuhome with the same definition as the DB2 manuhome table.
-- 3. Create table staging_mhr_owngroup with the same definition as the DB2 owngroup table.
-- 4. Create table staging_mhr_owner with the same definition as the DB2 owner table.
-- 5. Create table staging_mhr_note with the same definition as the DB2 mhomnote table.
-- 6. Create table staging_mhr_location with the same definition as the DB2 location table.
-- 7. Create table staging_mhr_description with the same definition as the DB2 descript table.
-- 8. Create table staging_mhr_document with the same definition as the DB2 document table.
-- 9. Create table staging_mhr_addresses with the same definition as the PosgreSQL addresses table.
--    Use a temp sequence to generate the primary keys while testing. Use the actual addresses sequence when ready for the final load.

CREATE TABLE public.staging_mhr_manuhome (
 MANHOMID INTEGER PRIMARY KEY,
 MHREGNUM VARCHAR (6),
 MHSTATUS VARCHAR (1),
 REGDOCID VARCHAR (8),
 EXEMPTFL VARCHAR (1),
 PRESOLD  VARCHAR (1),
 UPDATECT INTEGER,
 UPDATEID VARCHAR (8),
 UPDATEDA VARCHAR (10),
 UPDATETI VARCHAR (8),
 ACCNUM   INTEGER,
 BOXNUM   INTEGER    
);

CREATE TABLE public.staging_mhr_owngroup (
 MANHOMID INTEGER NOT NULL,
 OWNGRPID INTEGER NOT NULL,
 COPGRPID INTEGER,
 GRPSEQNO INTEGER,
 STATUS   VARCHAR (1),
 PENDING  VARCHAR (1),
 REGDOCID VARCHAR (8),
 CANDOCID VARCHAR (8),
 TENYTYPE VARCHAR (2),
 LESSEE   VARCHAR (1),
 LESSOR   VARCHAR (1),
 INTEREST VARCHAR (20),
 INTNUMER INTEGER,
 TENYSPEC VARCHAR (1),
 PRIMARY KEY(MANHOMID, OWNGRPID)
);

CREATE TABLE public.staging_mhr_note (
 MANHOMID INTEGER  NOT NULL,
 MHNOTEID INTEGER NOT NULL,
 MHNOTENO INTEGER NOT NULL,
 REGDOCID VARCHAR (8),
 CANDOCID VARCHAR (8),
 DOCUTYPE VARCHAR (10),
 STATUS   VARCHAR (1),
 DESTROYD VARCHAR (1),
 EXPIRYDA VARCHAR (10),
 PHONE    VARCHAR (10),
 NAME     VARCHAR (40),
 ADDRESS  VARCHAR (160),
 REMARKS  VARCHAR (420),
 PRIMARY KEY (MANHOMID, MHNOTEID, MHNOTENO)
);

CREATE TABLE public.staging_mhr_owner (
 MANHOMID INTEGER NOT NULL,
 OWNGRPID INTEGER NOT NULL,
 OWNERID  INTEGER NOT NULL,
 OWNSEQNO INTEGER,
 VERIFIED VARCHAR (1),
 OWNRTYPE VARCHAR (1),
 COMPNAME VARCHAR (30),
 OWNRFONE VARCHAR (10),
 OWNRPOCO VARCHAR (10),
 OWNRNAME VARCHAR (70),
 OWNRSUFF VARCHAR (70),
 OWNRADDR VARCHAR (160),
 PRIMARY KEY (MANHOMID, OWNGRPID, OWNERID)
);

CREATE TABLE public.staging_mhr_location (
 MANHOMID INTEGER NOT NULL,
 LOCATNID INTEGER NOT NULL,
 STATUS   VARCHAR (1),
 REGDOCID VARCHAR (8),
 CANDOCID VARCHAR (8),
 STNUMBER VARCHAR (6),
 STNAME   VARCHAR (25),
 TOWNCITY VARCHAR (20),
 PROVINCE VARCHAR (2),
 BCAAAREA VARCHAR (2),
 BCAAJURI VARCHAR (3),
 BCAAROLL VARCHAR (20),
 MAHPNAME VARCHAR (40),
 MAHPPAD  VARCHAR (6),
 PIDNUMB  VARCHAR (9),
 LOT      VARCHAR (10),
 PARCEL   VARCHAR (10),
 BLOCK    VARCHAR (10),
 DISTLOT  VARCHAR (17),
 PARTOF   VARCHAR (10),
 SECTION  VARCHAR (10),
 TOWNSHIP VARCHAR (2),
 RANGE    VARCHAR (2),
 MERIDIAN VARCHAR (3),
 LANDDIST VARCHAR (20),
 PLAN     VARCHAR (12),
 TAXCERT  VARCHAR (1),
 TAXDATE  VARCHAR (10),
 LEAVEBC  VARCHAR (1),
 EXCPLAN  VARCHAR (80),
 MHDEALER VARCHAR (60),
 ADDDESC  VARCHAR (80),
 PRIMARY KEY (MANHOMID, LOCATNID)
);

CREATE TABLE public.staging_mhr_description (
 MANHOMID INTEGER NOT NULL,
 DESCRNID INTEGER NOT NULL,
 STATUS   VARCHAR (1),
 REGDOCID VARCHAR (8),
 CANDOCID VARCHAR (8),
 CSANUMBR VARCHAR (10),
 CSASTAND VARCHAR (4),
 NUMBSECT INTEGER,
 SQARFEET INTEGER ,
 YEARMADE VARCHAR (4),
 CIRCA    VARCHAR (1),
 SERNUMB1 VARCHAR (20),
 SERNUMB2 VARCHAR (20),
 SERNUMB3 VARCHAR (20),
 SERNUMB4 VARCHAR (20),
 LENGTH1  INTEGER,
 LENGTH2  INTEGER,
 LENGTH3  INTEGER,
 LENGTH4  INTEGER,
 LENGIN1  INTEGER,
 LENGIN2  INTEGER,
 LENGIN3  INTEGER,
 LENGIN4  INTEGER,
 WIDTH1   INTEGER,
 WIDTH2   INTEGER,
 WIDTH3   INTEGER,
 WIDTH4   INTEGER,
 WIDIN1   INTEGER,
 WIDIN2   INTEGER,
 WIDIN3   INTEGER,
 WIDIN4   INTEGER,
 ENGIDATE VARCHAR (10),
 ENGINAME VARCHAR (30),
 MANUNAME VARCHAR (65),
 MAKEMODL VARCHAR (65),
 REBUILTR VARCHAR (280),
 OTHERREM VARCHAR (140),
 PRIMARY KEY (MANHOMID, DESCRNID)
);

CREATE TABLE public.staging_mhr_document (
 DOCUMTID  VARCHAR (8)  PRIMARY KEY,
 MHREGNUM  VARCHAR (6),
 DRAFDATE  VARCHAR (30),
 REGIDATE  VARCHAR (30),
 DOCUTYPE  VARCHAR (10),
 DOCUREGI  VARCHAR (8),
 INTERIMD  VARCHAR (1),
 OWNRXREF  VARCHAR (5),
 INTDENOM  INTEGER,
 DECVALUE  INTEGER,
 OWNLAND   VARCHAR (1),
 RSLIPNUM  VARCHAR (9),
 LASTSERV  VARCHAR (1),
 BCOLACCT  VARCHAR (6),
 DATNUMBR  VARCHAR (8),
 EXAMINID  VARCHAR (8),
 UPDATEID  VARCHAR (8),
 PHONE     VARCHAR (10),
 ATTNREF   VARCHAR  (40),
 NAME      VARCHAR  (40),
 ADDRESS   VARCHAR  (160),
 NUMPAGES  INTEGER,
 DATEOFEX  VARCHAR (10),
 CONVALUE  VARCHAR (80),
 AFFIRMBY  VARCHAR (40),
 CONSENT   VARCHAR (60),
 OLBCFOLI  VARCHAR (30)
);

--SELECT nextval('address_id_seq');
-- set initially to current address sequence + 5000
CREATE SEQUENCE staging_mhr_address_id_seq INCREMENT 1 START 4800000;
SELECT setval('staging_mhr_address_id_seq', (SELECT MAX(id) + 10000 from addresses where id < 99990001));
CREATE TABLE public.staging_mhr_addresses (
  id INTEGER PRIMARY KEY,
  street VARCHAR (50) NULL,  
  street_additional VARCHAR (50) NULL,
  city VARCHAR (40) NULL,
  region VARCHAR (2) NULL,
  postal_code VARCHAR (15) NULL,
  country VARCHAR (2) NULL
);
CREATE SEQUENCE staging_mhr_reg_id_seq INCREMENT 1 START 1;

