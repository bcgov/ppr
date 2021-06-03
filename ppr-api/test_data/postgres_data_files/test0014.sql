-- TEST0014 discharged more than 30 days excluded search test on all search types.
-- draft statement CLOB empty for testing.
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000018, 'D-T-0014', 'PS12345', CURRENT_TIMESTAMP, 'PPSALIEN', 'SA', 'TEST0014', null, '{}');
INSERT INTO financing_statements(id, state_type, expire_date, life, discharged, renewed)
  VALUES(200000008, 'HDC', CURRENT_TIMESTAMP + interval '1500 days', 5, 'Y' , null)
;
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000015, 200000008, 'TEST0014', null, 'SA', 'PPSALIEN', CURRENT_TIMESTAMP - interval '60 days', 200000018, 1,
           null, null, 'PS12345', 'TEST-SA-0014', null, null)
;
INSERT INTO trust_indentures(id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000006, 200000015, 200000008, 'Y', null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000017, 'TEST-0014', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000038, 'RG', 200000015, 200000008, null, null, 'TEST', '14', 'REGISTERING', null,
           null, 200000017)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, first_name_key, last_name_key)
    VALUES(200000039, 'DI', 200000015, 200000008, null, null, 'TEST IND DEBTOR', '14', 'ZZZZZ99', null,
           null, 200000017, searchkey_first_name('TEST IND DEBTOR'), searchkey_last_name('ZZZZZ99'))
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000040, 'DB', 200000015, 200000008, null, null, null, null, null, 'ZZZZZ99',
           null, 200000017, searchkey_business_name('ZZZZZ99'))
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000041, 'SP', 200000015, 200000008, null, null, null, null, null, 'TEST 14 SECURED PARTY',
           null, 200000017)
;
INSERT INTO serial_collateral(id, serial_type, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000018, 'MV', 200000015, 200000008, null, 2012, 'DISCHARGED MV', 'MODEL', 'ZZZZZ999999', null,
         searchkey_vehicle('ZZZZZ999999'))
;
INSERT INTO serial_collateral(id, serial_type, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000019, 'MH', 200000015, 200000008, null, 2012, 'DISCHARGED MH', 'MODEL', 'ZZZZZ999999', '399999',
        searchkey_mhr('399999'))
;
INSERT INTO serial_collateral(id, serial_type, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000020, 'AC', 200000015, 200000008, null, 2012, 'DISCHARGED AC', 'MODEL', 'ZZZZZ999999', null,
         searchkey_aircraft('ZZZZZ999999'))
;
-- Create discharge
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000019, 'D-T-0D14', 'PS12345', CURRENT_TIMESTAMP, 'DISCHARGE', 'DC', 'TEST0D14', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000016, 200000008, 'TEST0D14', 'TEST0014', 'DC', 'DISCHARGE', CURRENT_TIMESTAMP - interval '45 days', 200000019, 0,
           null, null, 'PS12345', 'TEST-DIS-0014', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000018, 'TEST-0D14', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000042, 'RG', 200000016, 200000008, null, null, 'TEST-DISCHARGE', '14', 'REGISTERING', null,
           null, 200000018)
;
-- TEST0014 end
