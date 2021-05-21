-- TEST0011 serial number MHR, AC test match data:
-- draft statement CLOB empty for testing.
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000015, 'D-T-0011', 'PS12345', CURRENT_TIMESTAMP, 'PPSALIEN', 'SA', 'TEST0011', null, '{}');
INSERT INTO financing_statement(financing_id, state_type_cd, expire_date, life, discharged, renewed)
  VALUES(200000005, 'ACT', CURRENT_TIMESTAMP + interval '365 days', 1, null , null)
;
INSERT INTO registration(registration_id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000012, 200000005, 'TEST0011', null, 'SA', 'PPSALIEN', CURRENT_TIMESTAMP, 200000015, 1,
           null, null, 'PS12345', 'TEST-SA-0011', null, null)
;
INSERT INTO trust_indenture(trust_id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000003, 200000012, 200000005, 'Y', null)
;
INSERT INTO address(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000014, 'TEST-0011', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000028, 'RG', 200000012, 200000005, null, null, 'TEST', '11', 'REGISTERING', null,
           null, 200000014)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id, first_name_key, last_name_key)
    VALUES(200000029, 'DI', 200000012, 200000005, null, null, 'TEST IND', '11', 'DEBTOR', null,
           null, 200000014, searchkey_first_name('TEST IND'),searchkey_last_name('DEBTOR'))
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000030, 'SP', 200000012, 200000005, null, null, null, null, null, 'TEST 11 SECURED PARTY',
           null, 200000014)
;
INSERT INTO serial_collateral(serial_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000009, 'MH', 200000012, 200000005, null, 2012, 'HOMCO IND. LTD DIPLOMAT', null, '999999', '220000',
         searchkey_mhr('220000'))
;
INSERT INTO serial_collateral(serial_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000010, 'AC', 200000012, 200000005, null, 1998, 'CESSNA', '172R SKYHAWK', 'CFYXW', null,
         searchkey_aircraft('CFYXW'))
;
-- TEST0011 end
