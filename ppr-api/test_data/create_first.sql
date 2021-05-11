-- Intended to run after test_rest.sql. Put any statements that should run first here if sequence matters.

-- Client Party Addresses
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000000, 'TEST 200000000', 'line 2', 'city', 'BC', 'V8R3A5', 'CA');
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000001, 'TEST 200000001', 'line 2', 'city', 'BC', 'V8R3A5', 'CA');

-- Client Party code names and addresses
INSERT INTO client_code(HEAD_ID, BRANCH_ID, ADDRESS_ID, NAME, BCONLINE_ACCOUNT, CONTACT_NAME,CONTACT_AREA_CD,
			            CONTACT_PHONE_NUMBER, EMAIL_ADDRESS, ID, USER_ID, DATE_TS)
  VALUES (200000000,200000000,200000000,'TEST PARTY CODE 1', 12345,'TEST SP CONTACT NAME','604','2171234',
          'test-sp-client@gmail.com',null,'SPUSER',null);
INSERT INTO client_code(HEAD_ID, BRANCH_ID, ADDRESS_ID, NAME, BCONLINE_ACCOUNT, CONTACT_NAME,CONTACT_AREA_CD,
			            CONTACT_PHONE_NUMBER, EMAIL_ADDRESS, ID, USER_ID, DATE_TS)
  VALUES (200000001,200000001,200000001,'TEST PARTY CODE 2',12345,'TEST RP CONTACT NAME','604','2171234',
          'test-rp-client@gmail.com',null,'RPUSER',null);

-- Add code_historical when Bob provides examples of how name/address changes work.

-- Spec example royal bank
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(99990001, '1079 Douglas St', null, 'Victoria', 'BC', 'V8W2C5', 'CA');
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(99990002, '1625 Hillside Ave', null, 'Victoria', 'BC', 'V8T2C3', 'CA');
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(99990003, '3541 Blanshard St', null, 'Victoria', 'BC', 'V8Z0B9', 'CA');
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(99990004, '1153 Esquimalt Rd', null, 'Victoria', 'BC', 'V9A3N7', 'CA');

INSERT INTO client_code(HEAD_ID, BRANCH_ID, ADDRESS_ID, NAME, BCONLINE_ACCOUNT, CONTACT_NAME,CONTACT_AREA_CD,
			            CONTACT_PHONE_NUMBER, EMAIL_ADDRESS, ID, USER_ID, DATE_TS)
  VALUES (9999,99990001,99990001,'RBC ROYAL BANK',12345,'TEST BRANCH 1 CONTACT NAME','250',
          '3564500','test-1@test-rbc.com',null,null,null);
INSERT INTO client_code(HEAD_ID, BRANCH_ID, ADDRESS_ID, NAME, BCONLINE_ACCOUNT, CONTACT_NAME,CONTACT_AREA_CD,
			            CONTACT_PHONE_NUMBER, EMAIL_ADDRESS, ID, USER_ID, DATE_TS)
  VALUES (9999,99990002,99990002,'RBC ROYAL BANK',12345,'TEST BRANCH 2 CONTACT NAME','250','3564660',
          'test-2@test-rbc.com',null,null,null);
INSERT INTO client_code(HEAD_ID, BRANCH_ID, ADDRESS_ID, NAME, BCONLINE_ACCOUNT, CONTACT_NAME,CONTACT_AREA_CD,
			            CONTACT_PHONE_NUMBER, EMAIL_ADDRESS, ID, USER_ID, DATE_TS)
  VALUES (9999,99990003,99990003,'RBC ROYAL BANK',12345,'TEST BRANCH 3 CONTACT NAME','250','2208424',
          'test-3@test-rbc.com',null,null,null);
INSERT INTO client_code(HEAD_ID, BRANCH_ID, ADDRESS_ID, NAME, BCONLINE_ACCOUNT, CONTACT_NAME,CONTACT_AREA_CD,
			            CONTACT_PHONE_NUMBER, EMAIL_ADDRESS, ID, USER_ID, DATE_TS)
  VALUES (9999,99990004,99990004,'RBC ROYAL BANK',12345,'TEST BRANCH 4 CONTACT NAME','250','3564670',
          'test-4@test-rbc.com',null,null,null);
