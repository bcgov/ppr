-- Intended to run after test_rest.sql. Put any statements that should run first here if sequence matters.

-- Client Party Addresses
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000000, 'TEST 200000000', 'line 2', 'city', 'BC', 'V8R3A5', 'CA');
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000001, 'TEST 200000001', 'line 2', 'city', 'BC', 'V8R3A5', 'CA');

-- Client Parties
INSERT INTO client_party(CLIENT_PARTY_ID, ACCOUNT_ID, NAME, USER_ID, ID, UPDATE_TS)
  VALUES (200000000,'PS12345','TEST SECURED PARTY','SPUSER',null, null);
INSERT INTO client_party(CLIENT_PARTY_ID, ACCOUNT_ID, NAME, USER_ID, ID, UPDATE_TS)
  VALUES(200000001,'PS12345','TEST REGISTERING PARTY','RPUSER', null, null);

-- Client Party Branches
INSERT INTO client_party_branch(CLIENT_PARTY_BRANCH_ID, CLIENT_PARTY_ID, ADDRESS_ID, BCONLINE_ACCOUNT, CONTACT_NAME,CONTACT_AREA_CD,
			 CONTACT_PHONE_NUMBER, USERID, ID, EMAIL_ID, UPDATE_TS)
  VALUES (200000000,200000000,200000000,12345,'TEST SP CONTACT NAME','604','2171234', 'SPUSER', null, 'test-sp-client@gmail.com', null);
INSERT INTO client_party_branch(CLIENT_PARTY_BRANCH_ID, CLIENT_PARTY_ID, ADDRESS_ID, BCONLINE_ACCOUNT, CONTACT_NAME,CONTACT_AREA_CD,
			 CONTACT_PHONE_NUMBER, USERID, ID, EMAIL_ID, UPDATE_TS)
  VALUES (200000001,200000001,200000001,12345,'TEST RP CONTACT NAME','604','2171234', 'RPUSER', null, 'test-rp-client@gmail.com', null);
