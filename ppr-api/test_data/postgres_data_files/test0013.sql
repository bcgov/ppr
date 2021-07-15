-- TEST0013 expired more than 30 days excluded search test on all search types.
-- draft statement CLOB empty for testing.
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000017, 'D-T-0013', 'PS12345', CURRENT_TIMESTAMP, 'PPSALIEN', 'SA', 'TEST0013', null, '{}');
INSERT INTO financing_statements(id, state_type, expire_date, life, discharged, renewed)
  VALUES(200000007, 'HEX', CURRENT_TIMESTAMP - interval '100 days', 1, null , null)
;
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000014, 200000007, 'TEST0013', null, 'SA', 'PPSALIEN', CURRENT_TIMESTAMP, 200000017, 1,
           null, null, 'PS12345', 'TEST-SA-0013', null, null)
;
INSERT INTO trust_indentures(id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000005, 200000014, 200000007, 'Y', null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000016, 'TEST-0013', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000034, 'RG', 200000014, 200000007, null, null, 'TEST', '13', 'REGISTERING', null,
           null, 200000016)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, first_name_key, last_name_key)
    VALUES(200000035, 'DI', 200000014, 200000007, null, null, 'TEST IND DEBTOR', '13', 'XXXXX99', null,
           null, 200000016, searchkey_first_name('TEST IND DEBTOR'), searchkey_last_name('XXXXX99'))
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000036, 'DB', 200000014, 200000007, null, null, null, null, null, 'XXXXX99',
           null, 200000016, searchkey_business_name('XXXXX99'))
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000037, 'SP', 200000014, 200000007, null, null, null, null, null, 'TEST 13 SECURED PARTY',
           null, 200000016)
;
INSERT INTO serial_collateral(id, serial_type, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000014, 'MV', 200000014, 200000007, null, 2012, 'EXPIRED MV', 'MODEL', 'XXXXX999999', null,
         searchkey_vehicle('XXXXX999999'))
;
INSERT INTO serial_collateral(id, serial_type, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000015, 'MH', 200000014, 200000007, null, 2012, 'EXPIRED MH', 'MODEL', 'XXXXX999999', searchkey_mhr('299999'),
         searchkey_vehicle('safsfsf299999'))
;
INSERT INTO serial_collateral(id, serial_type, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000016, 'AC', 200000014, 200000007, null, 2012, 'EXPIRED AC', 'MODEL', 'XXXXX999999', null,
         searchkey_aircraft('XXXXX999999'))
;
INSERT INTO serial_collateral(id, serial_type, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000017, 'AF', 200000014, 200000007, null, 2012, 'EXPIRED AF', 'MODEL', 'XXXXX999999', null,
         searchkey_aircraft('XXXXX999999'))
;
-- TEST0013 end
