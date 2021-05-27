-- TEST0004 discharge financing statement base test: create financing statement, then discharge statement
-- draft statement CLOB empty for testing.
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000006, 'D-T-0004', 'PS12345', CURRENT_TIMESTAMP, 'PPSALIEN', 'SA', 'TEST0004', null, '{}');
INSERT INTO financing_statements(id, state_type_cd, expire_date, life, discharged, renewed)
  VALUES(200000003, 'ACT', CURRENT_TIMESTAMP + interval '730 days', 2, null , null)
;
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000003, 200000003, 'TEST0004', null, 'SA', 'PPSALIEN', CURRENT_TIMESTAMP, 200000006, 2,
           null, null, 'PS12345', 'TEST-SA-0004', null, null)
;
INSERT INTO trust_indentures(id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000001, 200000003, 200000003, 'Y', null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000005, 'TEST-0004', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000011, 'RG', 200000003, 200000003, null, null, 'TEST', '4', 'REGISTERING', null,
           null, 200000005)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, first_name_key, last_name_key)
    VALUES(200000012, 'DI', 200000003, 200000003, null, null, 'TEST IND', '4', 'DEBTOR', null,
           null, 200000005, searchkey_first_name('TEST IND'), searchkey_last_name('DEBTOR'))
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000013, 'SP', 200000003, 200000003, null, null, null, null, null, 'TEST 4 SECURED PARTY',
           null, 200000005)
;
INSERT INTO serial_collateral(id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000004, 'MV', 200000003, 200000003, null, 2018, 'HONDA', 'CIVIC', 'JU622994', null,
         searchkey_vehicle('JU622994'))
;
-- Create discharge
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000007, 'D-T-00D4', 'PS12345', CURRENT_TIMESTAMP, 'DISCHARGE', 'DC', 'TEST0004', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000004, 200000003, 'TEST00D4', 'TEST0004', 'DC', 'DISCHARGE', CURRENT_TIMESTAMP + interval '1 day', 200000007, 0,
           null, null, 'PS12345', 'TEST-DIS-0004', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000006, 'TEST-00D4', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000014, 'RG', 200000004, 200000003, null, null, 'TEST-DISCHARGE', '4', 'REGISTERING', null,
           null, 200000006)
;
UPDATE financing_statements
   SET state_type_cd = 'HDC', discharged = 'Y'
 WHERE id = 200000003
;
-- TEST0004 end
