-- TEST0012 serial number MHR almost match, AC test match data:
-- draft statement CLOB empty for testing.
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000016, 'D-T-0012', 'PS12345', CURRENT_TIMESTAMP, 'PPSALIEN', 'SA', 'TEST0012', null, '{}');
INSERT INTO financing_statements(id, state_type_cd, expire_date, life, discharged, renewed)
  VALUES(200000006, 'ACT', CURRENT_TIMESTAMP + interval '365 days', 1, null , null)
;
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000013, 200000006, 'TEST0012', null, 'SA', 'PPSALIEN', CURRENT_TIMESTAMP, 200000016, 1,
           null, null, 'PS12345', 'TEST-SA-0012', null, null)
;
INSERT INTO trust_indentures(id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000004, 200000013, 200000006, 'Y', null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000015, 'TEST-0012', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000031, 'RG', 200000013, 200000006, null, null, 'TEST', '12', 'REGISTERING', null,
           null, 200000015)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, first_name_key, last_name_key)
    VALUES(200000032, 'DI', 200000013, 200000006, null, null, 'TEST IND', '12', 'DEBTOR', null,
           null, 200000015, searchkey_first_name('TEST IND'), searchkey_last_name('DEBTOR'))
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000033, 'SP', 200000013, 200000006, null, null, null, null, null, 'TEST 12 SECURED PARTY',
           null, 200000015)
;
INSERT INTO serial_collateral(id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000011, 'MH', 200000013, 200000006, null, 2012, 'HOMCO IND. LTD DIPLOMAT', null, '9999', '22000',
         searchkey_mhr('22000'))
;
INSERT INTO serial_collateral(id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000012, 'AC', 200000013, 200000006, null, 1998, 'CESSNA', '172R SKYHAWK', 'CFYX', null,
         searchkey_aircraft('CFYX'))
;
INSERT INTO serial_collateral(id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000013, 'AF', 200000013, 200000006, null, 1998, 'AIRFRAME make', 'AIRFRAME model', 'AF16031', null,
         searchkey_aircraft('AF16031'))
;
-- TEST0012 end
