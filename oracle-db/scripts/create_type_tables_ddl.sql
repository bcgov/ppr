-- Type table definitions begin
CREATE TABLE PARTY_TYPE
(
  PARTY_TYPE_CD   CHAR(2 BYTE) NOT NULL,
  PARTY_TYPE_DESC VARCHAR2(30 BYTE) NOT NULL
)
;
ALTER TABLE party_type
  ADD CONSTRAINT party_type_pk PRIMARY KEY (party_type_cd)
  using index
  tablespace PPR_INDEX
;


CREATE TABLE REGISTRATION_TYPE_CLASS
(
 REGISTRATION_TYPE_CL    VARCHAR2(10 BYTE) NOT NULL,
 REGISTRATION_DESC       VARCHAR2(100 BYTE) NOT NULL 
)
;
ALTER TABLE registration_type_class
  ADD CONSTRAINT registration_class_pk PRIMARY KEY (registration_type_cl)
  using index
  tablespace PPR_INDEX
;


CREATE TABLE REGISTRATION_TYPE 
(
  REGISTRATION_TYPE_CL    VARCHAR2(10 BYTE) NOT NULL,
  REGISTRATION_TYPE_CD    CHAR(2 BYTE) NOT NULL,
  REGISTRATION_ACT        VARCHAR2(60 BYTE) NOT NULL,
  REGISTRATION_DESC        VARCHAR2(100 BYTE) NOT NULL
)
;
ALTER TABLE registration_type
  ADD CONSTRAINT registration_type_pk PRIMARY KEY (registration_type_cd)
  using index
  tablespace PPR_INDEX
;
ALTER TABLE registration_type
  ADD CONSTRAINT registration_class_fk FOREIGN KEY (REGISTRATION_TYPE_CL)
  REFERENCES REGISTRATION_TYPE_CLASS(REGISTRATION_TYPE_CL)
;


CREATE TABLE SEARCH_TYPE
(
  SEARCH_TYPE_CD   CHAR(2 BYTE) NOT NULL,
  SEARCH_TYPE_DESC VARCHAR2(60 BYTE) NOT NULL
)
;
ALTER TABLE search_type
  ADD CONSTRAINT search_type_pk PRIMARY KEY (search_type_cd)
  using index
  tablespace PPR_INDEX
;


CREATE TABLE STATE_TYPE
(
  STATE_TYPE_CD       CHAR(3 BYTE) NOT NULL, 
  STATE_TYPE_DESC     VARCHAR2(30 BYTE) NOT NULL
)
;
ALTER TABLE state_type
  ADD CONSTRAINT state_type_pk PRIMARY KEY (state_type_cd)
  using index
  tablespace PPR_INDEX
;


CREATE TABLE SERIAL_TYPE  
(
  SERIAL_TYPE_CD   CHAR(2 BYTE) NOT NULL,
  SERIAL_TYPE_DESC VARCHAR2(30 BYTE) NOT NULL
)
;
ALTER TABLE serial_type
  ADD CONSTRAINT serial_type_pk PRIMARY KEY (serial_type_cd)
  using index
  tablespace PPR_INDEX
;

CREATE TABLE COUNTRY_TYPES
(
  COUNTRY_TYPE_CD     CHAR(2 BYTE) NOT NULL,
  COUNTRY_DESC        VARCHAR2(75 BYTE) NOT NULL
)
;
ALTER TABLE COUNTRY_TYPES
  ADD CONSTRAINT country_type_pk PRIMARY KEY (country_type_cd)
  using index
  tablespace PPR_INDEX
;

CREATE TABLE PROVINCE_TYPES
(
  PROVINCE_TYPE_CD    CHAR(2 BYTE) NOT NULL,
  COUNTRY_TYPE_CD     CHAR(2 BYTE) NOT NULL,
  PROVINCE_DESC       VARCHAR2(75 BYTE) NOT NULL
)
;
ALTER TABLE PROVINCE_TYPES
  ADD CONSTRAINT province_type_pk PRIMARY KEY (province_type_cd)
  using index
  tablespace PPR_INDEX
;
ALTER TABLE PROVINCE_TYPES
  ADD CONSTRAINT province_country_fk FOREIGN KEY (country_type_cd)
  REFERENCES COUNTRY_TYPES(country_type_cd)
;

-- Type table definitions end
