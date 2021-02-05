-- Intended to run after test_rest.sql. Put any statements that should run first here if sequence matters.

-- Client Party Addresses
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000000, 'TEST 200000000', 'line 2', 'city', 'BC', 'V8R3A5', 'CA');
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000001, 'TEST 200000001', 'line 2', 'city', 'BC', 'V8R3A5', 'CA');

-- Client Parties
INSERT INTO client_party(CLIENT_PARTY_ID,PARTY_TYPE_CD,ACCOUNT_ID,PARTY_NAME, CONTACT_NAME,CONTACT_AREA_CD,
			 CONTACT_PHONE_NUMBER, ADDRESS_ID, USER_ID, email_id)
  VALUES (200000000,'SP','PS12345','TEST SECURED PARTY','TEST SP CONTACT NAME','604',
  	  '2171234',200000000, 'SPUSER','test-sp-client@gmail.com');
INSERT INTO client_party(CLIENT_PARTY_ID,PARTY_TYPE_CD,ACCOUNT_ID,PARTY_NAME, CONTACT_NAME,CONTACT_AREA_CD,
               		 CONTACT_PHONE_NUMBER, ADDRESS_ID, USER_ID, email_id)
  VALUES(200000001,'RG','PS12345','TEST REGISTERING PARTY','TEST RP CONTACT NAME','604',
         '2171234',200000001,'RPUSER', 'test-rg-client@gmail.com');

