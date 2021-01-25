-- All test id's start at 200000000

-- Addresses
INSERT INTO address(address_id, street_line1, street_line2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000000, 'TEST 200000000', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;

INSERT INTO address(address_id, street_line1, street_line2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000001, 'TEST 200000001', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;

INSERT INTO address(address_id, street_line1, street_line2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000002, '200000002', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;

-- Client parties
INSERT INTO client_party(CLIENT_PARTY_ID,PARTY_TYPE_CD,ACCOUNT_ID,CONTACT_NAME,CONTACT_AREA_CD,CONTACT_PHONE_NUMBER,
			 CONTACT_EMAIL_ID,FIRST_NAME,MIDDLE_NAME,LAST_NAME,BUSINESS_NAME,SEARCH_NAME,EMAIL_ID,ADDRESS_ID)
  VALUES (200000000,'SP','PS12345','TEST SECURED PARTY','604','2171234','testsp@gmail.com',null,null,null,
	  'SECURED PARTY','SECUREDPARTY',null,200000000);
INSERT INTO client_party(CLIENT_PARTY_ID,PARTY_TYPE_CD,ACCOUNT_ID,CONTACT_NAME,CONTACT_AREA_CD,CONTACT_PHONE_NUMBER,
			 CONTACT_EMAIL_ID,FIRST_NAME,MIDDLE_NAME,LAST_NAME,BUSINESS_NAME,SEARCH_NAME,EMAIL_ID,ADDRESS_ID)
  VALUES(200000001,'RP','PS12345','TEST REGISTERING PARTY','604','2171234','testrp@gmail.com',null,null,null,
  	 'REGISTERING PARTY','REGISTERINGPARTY',null,200000001);
COMMIT;


-- Financing statements
INSERT INTO financing_statement(financing_id, financing_type_cd, state_type_cd, lien_amount, surrender_dt)
  VALUES(200000000, 'SA', 'A', null, null)
;
INSERT INTO financing_statement(financing_id, financing_type_cd, state_type_cd, lien_amount, surrender_dt)
  VALUES(200000001, 'RL', 'A', 2000.00, sysdate + 90)
;
INSERT INTO financing_statement(financing_id, financing_type_cd, state_type_cd, lien_amount, surrender_dt)
  VALUES(200000002, 'SA', 'H', null, null)
;
commit;


-- Registrations
INSERT INTO registration(registration_id, registration_num, registration_type_cd, registration_ts, financing_id,
                         account_id, change_type_cd, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000000, 'TEST0001', 'FS', systimestamp, 200000000, 'PS12345', null, 'TEST-SA-1', null, null)
;
INSERT INTO registration(registration_id, registration_num, registration_type_cd, registration_ts, financing_id,
                         account_id, change_type_cd, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000001, 'TEST0002', 'FS', systimestamp, 200000001, 'PS12345', null, 'TEST-RL-1', null, null)
;
INSERT INTO registration(registration_id, registration_num, registration_type_cd, registration_ts, financing_id,
                         account_id, change_type_cd, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000002, 'TEST0003', 'FS', systimestamp, 200000002, 'PS12345', null, 'TEST-SA-2-HIST', null, null)
;
COMMIT;

- Expiry records (financing and renewal)
INSERT INTO expiry(expiry_id, registration_id, financing_id, expiry_dt, life_years, life_infinite, registration_id_end)
  VALUES(200000000, 200000000, 200000000, sysdate + 700, 2, 'N', null)
;
INSERT INTO expiry(expiry_id, registration_id, financing_id, expiry_dt, life_years, life_infinite, registration_id_end)
  VALUES(200000001, 200000001, 200000001, sysdate + 90, 0, 'N', null)
;
INSERT INTO expiry(expiry_id, registration_id, financing_id, expiry_dt, life_years, life_infinite, registration_id_end)
  VALUES(200000002, 200000002, 200000002, sysdate + 700, 2, 'N', null)
;

- Trust indenture records (financing and amendment)
INSERT INTO trust_indenture(trust_id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000000, 200000000, 200000000, 'Y', null)
;
INSERT INTO trust_indenture(trust_id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000001, 200000001, 200000001, 'N', null)
;
INSERT INTO trust_indenture(trust_id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000002, 200000002, 200000001, 'Y', null)
;


-- Parties
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000000, 'RP', 200000000, 200000000, null, null, 'TEST', '1', 'REGISTERING', null, 'TEST1REGISTERING',
           'test1rp@gmail.com', null, 200000000)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000001, 'DI', 200000000, 200000000, null, null, 'TEST IND', '1', 'DEBTOR', null, 'TESTIND1DEBTOR',
           'test1di@gmail.com', null, 200000000)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000002, 'DC', 200000000, 200000000, null, null, null, null, null, 'TEST BUS 2 DEBTOR', 'TESTBUS2DEBTOR',
           'test2dc@gmail.com', null, 200000000)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000003, 'SP', 200000000, 200000000, null, null, null, null, null, 'TEST 1 SECURED PARTY', 'TEST1SECUREDPARTY',
           'test1sp@gmail.com', null, 200000000)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000004, 'SP', 200000000, 200000000, null, 200000000, null, null, null, null, 'SECUREDPARTY', null, null, null)
;

INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000005, 'DC', 200000001, 200000001, null, null, null, null, null, 'TEST BUS 2 DEBTOR', 'TESTBUS2DEBTOR',
           'test2dc@gmail.com', null, 200000000)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000006, 'SP', 200000001, 200000001, null, null, null, null, null, 'TEST 3 SECURED PARTY', 'TEST3SECUREDPARTY',
           'test3sp@gmail.com', null, 200000000)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000007, 'RP', 200000001, 200000001, null, null, 'TEST', '2', 'REGISTERING', null, 'TEST2REGISTERING',
           'test2rp@gmail.com', null, 200000000)
;
COMMIT;

-- Collateral
INSERT INTO general_collateral(general_collateral_id, registration_id, financing_id, registration_id_end, description)
  VALUES(200000000, 200000000, 200000000, null, 'TEST GENERAL COLLATERAL 1.')
;
INSERT INTO general_collateral(general_collateral_id, registration_id, financing_id, registration_id_end, description)
  VALUES(200000001, 200000000, 200000000, null, 'TEST GENERAL COLLATERAL 2.')
;
INSERT INTO general_collateral(general_collateral_id, registration_id, financing_id, registration_id_end, description)
  VALUES(200000002, 200000001, 200000001, null, 'TEST GENERAL COLLATERAL 3.')
;

INSERT INTO vehicle_collateral(vehicle_collateral_id, vehicle_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number)
  VALUES(200000000, 'MV', 200000000, 200000000, null, 2018, 'HYUNDAI', 'TUSCON', 'KM8J3CA46JU622994', null)
;
INSERT INTO vehicle_collateral(vehicle_collateral_id, vehicle_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number)
  VALUES(200000001, 'MH', 200000000, 200000000, null, 2001, 'HOMCO IND. LTD DIPLOMAT', null, '9407', '21324')
;
INSERT INTO vehicle_collateral(vehicle_collateral_id, vehicle_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number)
  VALUES(200000002, 'MV', 200000001, 200000001, null, 2014, 'HYUNDAI', 'TUSCON', 'KX8J3CA46JU622994', null)
;
commit;

-- Drafts
INSERT INTO draft(draft_id, draft_type_cd, document_id, account_id, create_ts,
                  type_cd, draft, registration_num, update_ts, registration_id)
    VALUES(200000000, 'FSD', 'TEST-FSD1', 'PS12345', systimestamp, 'SA',
'{
  "type": "FINANCING_STATEMENT",
  "financingStatement": {
    "type": "SA",
    "clientReferenceId": "A-00000402",
    "registeringParty": {
      "businessName": "ABC SEARCHING COMPANY",
      "address": {
        "street": "222 SUMMER STREET",
        "city": "VICTORIA",
        "region": "BC",
        "country": "CA",
        "postalCode": "V8W 2V8"
      },
      "emailAddress": "bsmith@abc-search.com"
    },
    "debtors": [
      {
        "businessName": "Debtor 1 Inc.",
        "address": {
          "street": "721 Debtor Ave",
          "city": "Victoria",
          "region": "BC",
          "country": "CA",
          "postalCode": "A1A 1A1"
        },
        "birthDate": "1990-06-15",
        "emailAddress": "dsmith@debtor1.com"
      }
    ],
    "vehicleCollateral": [
      {
        "type": "MV",
        "serialNumber": "KM8J3CA46JU622994",
        "year": 2018,
        "make": "HYUNDAI",
        "model": "TUCSON"
      }
    ],
    "lifeYears": 5,
    "securedParties": [
      {
        "businessName": "BANK OF BRITISH COLUMBIA",
        "address": {
          "street": "3721 BEACON AVENUE",
          "city": "SIDNEY",
          "region": "BC",
          "country": "CA",
          "postalCode": "V7R 1R7"
        },
        "emailAddress": "asmith@bobc.com"
      }
    ]
  }
}',
null, null, null);

INSERT INTO draft(draft_id, draft_type_cd, document_id, account_id, create_ts,
                  type_cd, draft, registration_num, update_ts, registration_id)
    VALUES(200000001, 'AMD', 'TEST-AMD1', 'PS12345', systimestamp, 'AM',
'{
  "type": "AMENDMENT_STATEMENT",
  "amendmentStatement": {
    "baseRegistrationNumber": "023003B",
    "documentId": "D0034002",
    "description": "Amendment to correct spelling mistake in debtor name. Name changed from \"Brawn\" to \"Brown\".",
    "changeType": "AM",
    "clientReferenceId": "A-00000402",
    "baseDebtor": {
      "businessName": "DEBTOR 1 INC."
    },
    "registeringParty": {
      "businessName": "ABC SEARCHING COMPANY",
      "address": {
        "street": "222 SUMMER STREET",
        "city": "VICTORIA",
        "region": "BC",
        "country": "CA",
        "postalCode": "V8W 2V8"
      },
      "emailAddress": "bsmith@abc-search.com"
    },
    "deleteDebtors": [
      {
        "businessName": "Brawn Window Cleaning Inc.",
        "partyId": 1321065
      }
    ],
    "addDebtors": [
      {
        "businessName": "Brown Window Cleaning Inc.",
        "address": {
          "street": "1234 Blanshard St",
          "city": "Victoria",
          "region": "BC",
          "country": "CA",
          "postalCode": "V8S 3J5"
        },
        "emailAddress": "csmith@bwc.com"
      }
    ]
  }
}',
'023003B', null, null);

INSERT INTO draft(draft_id, draft_type_cd, document_id, account_id, create_ts,
                  type_cd, draft, registration_num, update_ts, registration_id)
    VALUES(200000002, 'CHD', 'TEST-CHD1', 'PS12345', systimestamp, 'DT',
'{
  "type": "CHANGE_STATEMENT",
  "changeStatement": {
    "baseRegistrationNumber": "023010B",
    "documentId": "D0034003",
    "changeType": "DT",
    "baseDebtor": {
      "businessName": "DEBTOR 1 INC."
    },
    "registeringParty": {
      "businessName": "ABC SEARCHING COMPANY",
      "address": {
        "street": "222 SUMMER STREET",
        "city": "VICTORIA",
        "region": "BC",
        "country": "CA",
        "postalCode": "V8W 2V8"
      },
      "emailAddress": "bsmith@abc-search.com"
    },
    "addDebtors": [
      {
        "businessName": "Brown Window Cleaning Inc.",
        "address": {
          "street": "1234 Blanshard St",
          "city": "Victoria",
          "region": "BC",
          "country": "CA",
          "postalCode": "V8S 3J5"
        },
        "emailAddress": "csmith@bwc.com"
      }
    ],
    "deleteDebtors": [
      {
        "businessName": "Brawn Window Cleaning Inc.",
        "partyId": 1321065
      }
    ]
  }
}',
'023010B', null, null);
commit;


-- To test fetching for a discharge statement type, create a dedicated financing statement.
INSERT INTO financing_statement(financing_id, financing_type_cd, state_type_cd, lien_amount, surrender_dt)
  VALUES(200000003, 'SA', 'A', null, null)
;
INSERT INTO registration(registration_id, registration_num, registration_type_cd, registration_ts, financing_id,
                         account_id, change_type_cd, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000003, 'TEST0004', 'FS', systimestamp, 200000003, 'PS12345', null, 'TEST-SA-1', null, null)
;

-- Expiry
INSERT INTO expiry(expiry_id, registration_id, financing_id, expiry_dt, life_years, life_infinite, registration_id_end)
  VALUES(200000003, 200000003, 200000003, sysdate + 700, 2, 'N', null)
;
-- Trust Indenture
INSERT INTO trust_indenture(trust_id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000003, 200000003, 200000003, 'Y', null)
;

-- Addresses
INSERT INTO address(address_id, street_line1, street_line2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000004, 'TEST 200000003', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;

-- Parties
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000008, 'RP', 200000003, 200000003, null, null, 'TEST', '1', 'REGISTERING', null, 'TEST1REGISTERING',
           'test1rp@gmail.com', null, 200000004)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000009, 'DI', 200000003, 200000003, null, null, 'TEST IND', '1', 'DEBTOR', null, 'TESTIND1DEBTOR',
           'test1di@gmail.com', null, 200000004)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000010, 'SP', 200000003, 200000003, null, null, null, null, null, 'TEST 1 SECURED PARTY', 'TEST1SECUREDPARTY',
           'test1sp@gmail.com', null, 200000004)
;

-- Collateral
INSERT INTO vehicle_collateral(vehicle_collateral_id, vehicle_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number)
  VALUES(200000003, 'MV', 200000003, 200000003, null, 2018, 'HONDA', 'CIVIC', 'JU622994', null)
;
COMMIT;

-- Discharge statement: registration, secured party, update finanancing_statement.state_type_cd
INSERT INTO registration(registration_id, registration_num, registration_type_cd, registration_ts, financing_id,
                         account_id, change_type_cd, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000004, 'TEST0005-D', 'DS', systimestamp, 200000003, 'PS12345', null, 'TEST-DISCHARGE-1', null, null)
;
-- Addresses
INSERT INTO address(address_id, street_line1, street_line2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000005, 'TEST 200000004', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;

-- Parties
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000011, 'RP', 200000004, 200000003, null, null, 'TEST', '1', 'REGISTERING', null, 'TEST1REGISTERING',
           'test1rp@gmail.com', null, 200000005)
;

UPDATE financing_statement
   SET state_type_cd = 'H'
 WHERE financing_id = 200000003
;

COMMIT;


-- To test fetching for a renewal statement type, create a dedicated financing statement.
INSERT INTO financing_statement(financing_id, financing_type_cd, state_type_cd, lien_amount, surrender_dt)
  VALUES(200000004, 'SA', 'A', null, null)
;
INSERT INTO registration(registration_id, registration_num, registration_type_cd, registration_ts, financing_id,
                         account_id, change_type_cd, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000005, 'TEST0005', 'FS', systimestamp, 200000004, 'PS12345', null, 'TEST-RS-BASE', null, null)
;

-- Expiry
INSERT INTO expiry(expiry_id, registration_id, financing_id, expiry_dt, life_years, life_infinite, registration_id_end)
  VALUES(200000004, 200000005, 200000004, sysdate + 365, 1, 'N', null)
;
-- Trust Indenture
INSERT INTO trust_indenture(trust_id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000004, 200000005, 200000004, 'N', null)
;

-- Addresses
INSERT INTO address(address_id, street_line1, street_line2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000006, 'TEST 200000004', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;

-- Parties
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000012, 'RP', 200000005, 200000004, null, null, 'TEST', '1', 'REGISTERING', null, 'TEST1REGISTERING',
           'test1rp@gmail.com', null, 200000006)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000013, 'DI', 200000005, 200000004, null, null, 'TEST IND', '1', 'DEBTOR', null, 'TESTIND1DEBTOR',
           'test1di@gmail.com', null, 200000006)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000014, 'SP', 200000005, 200000004, null, null, null, null, null, 'TEST 1 SECURED PARTY', 'TEST1SECUREDPARTY',
           'test1sp@gmail.com', null, 200000006)
;

-- Collateral
INSERT INTO vehicle_collateral(vehicle_collateral_id, vehicle_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number)
  VALUES(200000004, 'MV', 200000005, 200000004, null, 2018, 'TESLA', 'MODEL 3', 'YJ46JU622994', null)
;
COMMIT;

- Renewal inserts into registration, expiry. It updates expiry.registration_id_end
INSERT INTO registration(registration_id, registration_num, registration_type_cd, registration_ts, financing_id,
                         account_id, change_type_cd, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000006, 'TEST0006-R', 'RS', systimestamp, 200000004, 'PS12345', null, 'TEST-RS-1', null, null)
;
INSERT INTO expiry(expiry_id, registration_id, financing_id, expiry_dt, life_years, life_infinite, registration_id_end)
  VALUES(200000005, 200000006, 200000004, sysdate + 700, 0, 'N', null)
;
UPDATE expiry
   SET expiry.registration_id_end = 200000006
  WHERE expiry.expiry_id = 200000004
;

-- Renewal on a repairer's lien financing statement
INSERT INTO registration(registration_id, registration_num, registration_type_cd, registration_ts, financing_id,
                         account_id, change_type_cd, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000007, 'TEST0007-R', 'RS', systimestamp, 200000001, 'PS12345', null, 'TEST-RS-RL-1', null, null)
;
INSERT INTO expiry(expiry_id, registration_id, financing_id, expiry_dt, life_years, life_infinite, registration_id_end)
  VALUES(200000006, 200000007, 200000001, sysdate + 180, 0, 'N', null)
;
UPDATE expiry
   SET expiry.registration_id_end = 200000007
  WHERE expiry.expiry_id = 200000001
;
INSERT INTO court_order(court_order_id, registration_id, court_dt, court_name, court_registry, file_number, effect_of_order)
  VALUES(200000000, 200000007, sysdate + 200, 'Supreme Court of British Columbia', 'Victoria', 'BC123495',
         'Court Order to renew Repairer''s Lien.')
;
COMMIT;


-- Amendment on TEST0001. Update all possible entities.
INSERT INTO registration(registration_id, registration_num, registration_type_cd, registration_ts, financing_id,
                         account_id, change_type_cd, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000008, 'TEST0007-AM', 'AS', systimestamp, 200000000, 'PS12345', 'CO', 'TEST-AM-001', null, null)
;

-- Addresses
INSERT INTO address(address_id, street_line1, street_line2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000007, 'TEST 200000004', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;

-- Parties
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000015, 'RP', 200000008, 200000000, null, null, 'TEST', '1', 'REGISTERING', null, 'TEST1REGISTERING',
           'test1rp@gmail.com', null, 200000007)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000016, 'DI', 200000008, 200000000, null, null, 'TEST IND', '3', 'DEBTOR', null, 'TESTIND3DEBTOR',
           'test1di@gmail.com', null, 200000007)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000017, 'SP', 200000008, 200000000, null, null, null, null, null, 'TEST 3 SECURED PARTY', 'TEST3SECUREDPARTY',
           'test3sp@gmail.com', null, 200000007)
;
-- Delete parties
UPDATE party
   SET registration_id_end = 200000008
 WHERE party_id IN (200000001, 200000003)
;
-- Add Collateral
INSERT INTO vehicle_collateral(vehicle_collateral_id, vehicle_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number)
  VALUES(200000005, 'MV', 200000008, 200000000, null, 2018, 'FORD', 'FIESTA', 'T346JU622994', null)
;
INSERT INTO general_collateral(general_collateral_id, registration_id, financing_id, registration_id_end, description)
  VALUES(200000003, 200000008, 200000000, null, 'TEST GENERAL COLLATERAL 3.')
;
-- Delete collateral
UPDATE general_collateral
  SET registration_id_end = 200000008
WHERE general_collateral_id = 200000001
;
UPDATE vehicle_collateral
  SET registration_id_end = 200000008
WHERE vehicle_collateral_id = 200000001
;

INSERT INTO court_order(court_order_id, registration_id, court_dt, court_name, court_registry, file_number, effect_of_order)
  VALUES(200000001, 200000008, sysdate + 200, 'Supreme Court of British Columbia', 'Victoria', 'BC123495',
         'Court Order to renew Repairer''s Lien.')
;

COMMIT;

-- Change Statement debtor transfer on TEST0001.
INSERT INTO registration(registration_id, registration_num, registration_type_cd, registration_ts, financing_id,
                         account_id, change_type_cd, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000009, 'TEST0008-DT', 'CS', systimestamp, 200000000, 'PS12345', 'DT', 'TEST-CS-DT-001', null, null)
;
-- Addresses
INSERT INTO address(address_id, street_line1, street_line2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000008, 'TEST 200000008', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
-- Parties
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000018, 'RP', 200000009, 200000000, null, null, 'TEST', '1', 'REGISTERING', null, 'TEST1REGISTERING',
           'test1rp@gmail.com', null, 200000008)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000019, 'DI', 200000009, 200000000, null, null, 'TEST IND DT', '4', 'DEBTOR', null, 'TESTINDDT4DEBTOR',
           'test4di@gmail.com', null, 200000008)
;
-- Delete parties
UPDATE party
   SET registration_id_end = 200000009
 WHERE party_id = 200000016
   AND party_type_cd = 'DI'
;
COMMIT;


-- Change Statement secured party transfer on TEST0001.
INSERT INTO registration(registration_id, registration_num, registration_type_cd, registration_ts, financing_id,
                         account_id, change_type_cd, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000010, 'TEST0009-ST', 'CS', systimestamp, 200000000, 'PS12345', 'ST', 'TEST-CS-ST-001', null, null)
;
-- Addresses
INSERT INTO address(address_id, street_line1, street_line2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000009, 'TEST 200000009', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
-- Parties
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000020, 'RP', 200000010, 200000000, null, null, 'TEST', '1', 'REGISTERING', null, 'TEST1REGISTERING',
           'test1rp@gmail.com', null, 200000009)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000021, 'SP', 200000010, 200000000, null, null, null, null, null, 'TEST 4 SECURED PARTY ST', 'TEST4SECUREDPARTYST',
           'test4sp@gmail.com', null, 200000009)
;
-- Delete parties
UPDATE party
   SET registration_id_end = 200000010
 WHERE party_id = 200000017
   AND party_type_cd = 'SP'
;
COMMIT;


-- Change Statement collateral substitution on TEST0001.
INSERT INTO registration(registration_id, registration_num, registration_type_cd, registration_ts, financing_id,
                         account_id, change_type_cd, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000011, 'TEST0010-SU', 'CS', systimestamp, 200000000, 'PS12345', 'SU', 'TEST-CS-SU-001', null, null)
;
-- Addresses
INSERT INTO address(address_id, street_line1, street_line2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000010, 'TEST 200000010', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
-- Parties
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000022, 'RP', 200000011, 200000000, null, null, 'TEST', '1', 'REGISTERING', null, 'TEST1REGISTERING',
           'test1rp@gmail.com', null, 200000010)
;
-- Add Collateral
INSERT INTO vehicle_collateral(vehicle_collateral_id, vehicle_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number)
  VALUES(200000006, 'MV', 200000011, 200000000, null, 2014, 'BMW', 'Z4', 'JU622994', null)
;
INSERT INTO vehicle_collateral(vehicle_collateral_id, vehicle_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number)
  VALUES(200000007, 'MH', 200000011, 200000000, null, 2012, 'HOMCO IND. LTD DIPLOMAT', null, '999999', 'T200000000')
;
INSERT INTO general_collateral(general_collateral_id, registration_id, financing_id, registration_id_end, description)
  VALUES(200000004, 200000011, 200000000, null, 'TEST GENERAL COLLATERAL 4.')
;
-- Delete collateral
UPDATE general_collateral
  SET registration_id_end = 200000011
WHERE general_collateral_id = 200000003
;
UPDATE vehicle_collateral
  SET registration_id_end = 200000011
WHERE vehicle_collateral_id = 200000005
;

COMMIT;


-- Use to test search by MHR number with multiple matches
INSERT INTO financing_statement(financing_id, financing_type_cd, state_type_cd, lien_amount, surrender_dt)
  VALUES(200000005, 'SA', 'A', null, null)
;
INSERT INTO registration(registration_id, registration_num, registration_type_cd, registration_ts, financing_id,
                         account_id, change_type_cd, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000012, 'TEST0011', 'FS', systimestamp, 200000005, 'PS12345', null, 'TEST-FS-11', null, null)
;
-- Expiry
INSERT INTO expiry(expiry_id, registration_id, financing_id, expiry_dt, life_years, life_infinite, registration_id_end)
  VALUES(200000007, 200000012, 200000005, sysdate + 365, 1, 'N', null)
;
-- Trust Indenture
INSERT INTO trust_indenture(trust_id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000005, 200000012, 200000005, 'N', null)
;
-- Addresses
INSERT INTO address(address_id, street_line1, street_line2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000011, 'TEST 200000011', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
-- Parties
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000023, 'RP', 200000012, 200000005, null, null, 'TEST', '1', 'REGISTERING', null, 'TEST1REGISTERING',
           'test1rp@gmail.com', null, 200000011)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000024, 'DI', 200000012, 200000005, null, null, 'TEST IND', '1', 'DEBTOR', null, 'TESTIND1DEBTOR',
           'test1di@gmail.com', null, 200000011)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000025, 'SP', 200000012, 200000005, null, null, null, null, null, 'TEST 1 SECURED PARTY', 'TEST1SECUREDPARTY',
           'test1sp@gmail.com', null, 200000011)
;
-- Collateral
INSERT INTO vehicle_collateral(vehicle_collateral_id, vehicle_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number)
  VALUES(200000008, 'MH', 200000012, 200000005, null, 2012, 'HOMCO IND. LTD DIPLOMAT', null, '999999', 'T200000000')
;
INSERT INTO vehicle_collateral(vehicle_collateral_id, vehicle_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number)
  VALUES(200000009, 'AC', 200000012, 200000005, null, 1998, 'CESSNA', '172R SKYHAWK', 'CFYXW', null)
;
COMMIT;


INSERT INTO search_audit(search_id, search_ts, search_type_cd, search_criteria, search_response,
                         account_id, pay_invoice_id, pay_path, client_reference_id, total_results_size, returned_results_size)
  VALUES(200000000, systimestamp, 'RN',
         '{"type": "REGISTRATION_NUMBER", "criteria": {"value": "TEST0001"}, "clientReferenceId": "T-S-RN-001"}',
         '[{"matchType": "EXACT", "registrationNumber": "TEST0001", "baseRegistrationNumber": "TEST0001", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
         'PS12345', null, null, 'UT-SQ-RN-001', 1, 1)
;
INSERT INTO search_audit_detail(search_detail_id, search_id, search_select, search_response)
   VALUES(200000000, 200000000,
          '[{"baseRegistrationNumber": "TEST0001", "matchType": "EXACT", "registrationType": "SA"}]',
'UNIT TEST RESPONSE CONTENT NOT EXAMINED')
;
INSERT INTO search_audit(search_id, search_ts, search_type_cd, search_criteria, search_response,
                         account_id, pay_invoice_id, pay_path, client_reference_id, total_results_size, returned_results_size)
  VALUES(200000001, systimestamp, 'RN',
         '{"type": "REGISTRATION_NUMBER", "criteria": {"value": "TEST0001"}, "clientReferenceId": "T-S-RN-001"}',
         '[{"matchType": "EXACT", "registrationNumber": "TEST0001", "baseRegistrationNumber": "TEST0001", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
         'PS12345', null, null, 'UT-SQ-RN-001', 1, 1)
;
COMMIT;


-- OAS example data
INSERT INTO address(address_id, street_line1, street_line2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000003, '3721 BEACON AVENUE', null, 'SIDNEY', 'BC', 'V7R 1R7', 'CA')
;
INSERT INTO client_party(CLIENT_PARTY_ID,PARTY_TYPE_CD,ACCOUNT_ID,CONTACT_NAME,CONTACT_AREA_CD,CONTACT_PHONE_NUMBER,
			 CONTACT_EMAIL_ID,FIRST_NAME,MIDDLE_NAME,LAST_NAME,BUSINESS_NAME,SEARCH_NAME,EMAIL_ID,ADDRESS_ID)
  VALUES (5000009,'SP','PS12345','ROBERT JONES','250','7244404','rbjones@bobc.com',null,null,null,
	  'BANK OF BRITISH COLUMBIA','BANKOFBRITISH','asmith@bobc.com',200000003);
INSERT INTO client_party(CLIENT_PARTY_ID,PARTY_TYPE_CD,ACCOUNT_ID,CONTACT_NAME,CONTACT_AREA_CD,CONTACT_PHONE_NUMBER,
			 CONTACT_EMAIL_ID,FIRST_NAME,MIDDLE_NAME,LAST_NAME,BUSINESS_NAME,SEARCH_NAME,EMAIL_ID,ADDRESS_ID)
  VALUES(3000001,'RP','PS12345','BILL HARRIS','604','2794790','bharris@abc-search.com',null,null,null,
  	 'ABC SEARCHING COMPANY','ABCSEARCHINGCO','bsmith@abc-search.com',200000003);
commit;


