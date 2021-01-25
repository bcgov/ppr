-- TEST0012 Use to test search by aircraft DOT with multiple matches
INSERT INTO financing_statement(financing_id, financing_type_cd, state_type_cd, lien_amount, surrender_dt)
  VALUES(200000006, 'SA', 'A', null, null);
INSERT INTO registration(registration_id, registration_num, registration_type_cd, registration_ts, financing_id,
                         account_id, change_type_cd, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000013, 'TEST0012', 'FS', systimestamp, 200000006, 'PS12345', null, 'TEST-FS-12', null, null);
-- Expiry
INSERT INTO expiry(expiry_id, registration_id, financing_id, expiry_dt, life_years, life_infinite, registration_id_end)
  VALUES(200000008, 200000013, 200000006, sysdate + 365, 1, 'N', null)
;
-- Trust Indenture
INSERT INTO trust_indenture(trust_id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000006, 200000013, 200000006, 'N', null)
;
-- Addresses
INSERT INTO address(address_id, street_line1, street_line2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000012, 'TEST 200000012', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
-- Parties
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000026, 'RP', 200000013, 200000006, null, null, 'TEST', '1', 'REGISTERING', null, 'TEST1REGISTERING',
           'test12rp@gmail.com', null, 200000012)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000027, 'DI', 200000013, 200000006, null, null, 'TEST IND', '1', 'DEBTOR', null, 'TESTIND1DEBTOR',
           'test12di@gmail.com', null, 200000012)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, search_name, email_id, birth_dt, address_id)
    VALUES(200000028, 'SP', 200000013, 200000006, null, null, null, null, null, 'TEST 1 SECURED PARTY', 'TEST1SECUREDPARTY',
           'test12sp@gmail.com', null, 200000012)
;
-- Collateral
INSERT INTO vehicle_collateral(vehicle_collateral_id, vehicle_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number)
  VALUES(200000010, 'AC', 200000013, 200000006, null, 2002, 'CESSNA', '172R SKYHAWK 2', 'CFYXW1', null)
;
