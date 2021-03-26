-- TEST0004 discharge financing statement base test: create financing statement, then discharge statement
-- draft statement CLOB empty for testing.
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000006, 'D-T-0004', 'PS12345', sysdate, 'PPSALIEN', 'SA', 'TEST0004', null, '{}');
INSERT INTO financing_statement(financing_id, state_type_cd, expire_date, life, discharged, renewed, registration_number)
  VALUES(200000003, 'ACT', sysdate + 730, 2, null , null, 'TEST0004')
;
INSERT INTO registration(registration_id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, document_number, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000003, 200000003, 'TEST0004', null, 'SA', 'PPSALIEN', sysdate, 'D-T-0004', 2,
           null, null, 'PS12345', 'TEST-SA-0004', null, null)
;
INSERT INTO trust_indenture(trust_id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000001, 200000003, 200000003, 'Y', null)
;
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000005, 'TEST-0004', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000011, 'RG', 200000003, 200000003, null, null, 'TEST', '4', 'REGISTERING', null,
           null, 200000005)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id, first_name_key, last_name_key)
    VALUES(200000012, 'DI', 200000003, 200000003, null, null, 'TEST IND', '4', 'DEBTOR', null,
           null, 200000005, search_key_pkg.lastname('TEST IND'), search_key_pkg.lastname('DEBTOR'))
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000013, 'SP', 200000003, 200000003, null, null, null, null, null, 'TEST 4 SECURED PARTY',
           null, 200000005)
;
INSERT INTO serial_collateral(serial_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000004, 'MV', 200000003, 200000003, null, 2018, 'HONDA', 'CIVIC', 'JU622994', null,
         search_key_pkg.vehicle('JU622994'))
;
-- Create discharge
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000007, 'D-T-00D4', 'PS12345', sysdate, 'DISCHARGE', 'DC', 'TEST0004', null, '{}');
INSERT INTO registration(registration_id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, document_number, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000004, 200000003, 'TEST00D4', 'TEST0004', 'DC', 'DISCHARGE', sysdate + 1, 'D-T-00D4', 0,
           null, null, 'PS12345', 'TEST-DIS-0004', null, null)
;
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000006, 'TEST-00D4', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000014, 'RG', 200000004, 200000003, null, null, 'TEST-DISCHARGE', '4', 'REGISTERING', null,
           null, 200000006)
;
UPDATE financing_statement
   SET state_type_cd = 'HDC', discharged = 'Y'
 WHERE financing_id = 200000003
;
UPDATE draft
   SET registration_id = 200000003
 WHERE draft_id = 200000006
;
UPDATE draft
   SET registration_id = 200000004
 WHERE draft_id = 200000007
;
-- TEST0004 end
