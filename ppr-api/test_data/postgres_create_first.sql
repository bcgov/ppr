-- Intended to run after test_reset.sql. Put any statements that should run first here if sequence matters.

INSERT INTO users(id, creation_date, username, sub, account_id, firstname, lastname, email, iss, idp_userid, login_source)
  VALUES(200000000, current_timestamp, 'TESTUSER', 'subject', 'PS12345', 'TEST', 'USER', null, 'issuer', '123', 'IDIR')
;
INSERT INTO user_profiles(id, payment_confirmation, search_selection_confirmation, default_drop_downs, default_table_filters,
                          registrations_table, misc_preferences)
  VALUES (200000000, 'Y', 'Y', 'Y', 'Y', null, null)
;

-- Client Party Addresses
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000000, 'TEST 200000000', 'line 2', 'city', 'BC', 'V8R3A5', 'CA');
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000001, 'TEST 200000001', 'line 2', 'city', 'BC', 'V8R3A5', 'CA');

-- Client Party code names and addresses
INSERT INTO client_codes(HEAD_ID, ID, ADDRESS_ID, NAME, BCONLINE_ACCOUNT, CONTACT_NAME,CONTACT_AREA_CD,
			            CONTACT_PHONE_NUMBER, EMAIL_ADDRESS, USERS_ID, USER_ID, DATE_TS)
  VALUES (200000000,200000000,200000000,'TEST PARTY CODE 1', 200000000,'TEST SP CONTACT NAME','604','2171234',
          'test-sp-client@gmail.com',null,'SPUSER',null);
INSERT INTO client_codes(HEAD_ID, ID, ADDRESS_ID, NAME, BCONLINE_ACCOUNT, CONTACT_NAME,CONTACT_AREA_CD,
			            CONTACT_PHONE_NUMBER, EMAIL_ADDRESS, USERS_ID, USER_ID, DATE_TS)
  VALUES (200000001,200000001,200000001,'TEST PARTY CODE 2',200000001,'TEST RP CONTACT NAME','604','2171234',
          'test-rp-client@gmail.com',null,'RPUSER',null);
INSERT INTO client_codes(HEAD_ID, ID, ADDRESS_ID, NAME, BCONLINE_ACCOUNT, CONTACT_NAME,CONTACT_AREA_CD,
			            CONTACT_PHONE_NUMBER, EMAIL_ADDRESS, USERS_ID, USER_ID, DATE_TS)
  VALUES (200000002,200000002,200000001,'TEST PARTY CODE 3',200000002,'TEST 3 CONTACT NAME','604','2171234',
          'test-3-client@gmail.com',null,'T3USER',null);
-- Name matches auth mock service org name
INSERT INTO client_codes(HEAD_ID, ID, ADDRESS_ID, NAME, BCONLINE_ACCOUNT, CONTACT_NAME,CONTACT_AREA_CD,
			            CONTACT_PHONE_NUMBER, EMAIL_ADDRESS, USERS_ID, USER_ID, DATE_TS)
  VALUES (200000003,200000003,200000001,'PH Testing PPR with PAD',200000002,'TEST 4 CONTACT NAME','604','2171234',
          'test-4-client@gmail.com',null,'T4USER',null);


-- Account ID BCOL Account Number mapping
INSERT INTO account_bcol_ids(id, account_id, bconline_account, crown_charge_ind)
  VALUES (200000000, 'PS12345', 200000000, 'Y');
INSERT INTO account_bcol_ids(id, account_id, bconline_account, crown_charge_ind)
  VALUES (200000001, 'PS12345', 200000001, 'Y');
INSERT INTO account_bcol_ids(id, account_id, bconline_account, crown_charge_ind)
  VALUES (200000002, 'PS00001', 200000002, null);

-- Add code_historical when Bob provides examples of how name/address changes work.

-- Spec example royal bank
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(99990001, '1079 Douglas St', null, 'Victoria', 'BC', 'V8W2C5', 'CA');
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(99990002, '1625 Hillside Ave', null, 'Victoria', 'BC', 'V8T2C3', 'CA');
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(99990003, '3541 Blanshard St', null, 'Victoria', 'BC', 'V8Z0B9', 'CA');
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(99990004, '1153 Esquimalt Rd', null, 'Victoria', 'BC', 'V9A3N7', 'CA');

INSERT INTO client_codes(HEAD_ID, ID, ADDRESS_ID, NAME, BCONLINE_ACCOUNT, CONTACT_NAME,CONTACT_AREA_CD,
			            CONTACT_PHONE_NUMBER, EMAIL_ADDRESS, USERS_ID, USER_ID, DATE_TS)
  VALUES (9999,99990001,99990001,'RBC ROYAL BANK',12345,'TEST BRANCH 1 CONTACT NAME','250',
          '3564500','test-1@test-rbc.com',null,null,null);
INSERT INTO client_codes(HEAD_ID, ID, ADDRESS_ID, NAME, BCONLINE_ACCOUNT, CONTACT_NAME,CONTACT_AREA_CD,
			            CONTACT_PHONE_NUMBER, EMAIL_ADDRESS, USERS_ID, USER_ID, DATE_TS)
  VALUES (9999,99990002,99990002,'RBC ROYAL BANK',12345,'TEST BRANCH 2 CONTACT NAME','250','3564660',
          'test-2@test-rbc.com',null,null,null);
INSERT INTO client_codes(HEAD_ID, ID, ADDRESS_ID, NAME, BCONLINE_ACCOUNT, CONTACT_NAME,CONTACT_AREA_CD,
			            CONTACT_PHONE_NUMBER, EMAIL_ADDRESS, USERS_ID, USER_ID, DATE_TS)
  VALUES (9999,99990003,99990003,'RBC ROYAL BANK',12345,'TEST BRANCH 3 CONTACT NAME','250','2208424',
          'test-3@test-rbc.com',null,null,null);
INSERT INTO client_codes(HEAD_ID, ID, ADDRESS_ID, NAME, BCONLINE_ACCOUNT, CONTACT_NAME,CONTACT_AREA_CD,
			            CONTACT_PHONE_NUMBER, EMAIL_ADDRESS, USERS_ID, USER_ID, DATE_TS)
  VALUES (9999,99990004,99990004,'RBC ROYAL BANK',12345,'TEST BRANCH 4 CONTACT NAME','250','3564670',
          'test-4@test-rbc.com',null,null,null);
