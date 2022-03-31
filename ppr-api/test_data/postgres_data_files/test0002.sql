-- TEST0002 financing statement repairer's lien base test
-- draft statement CLOB empty for testing.
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000001, 'D-T-0002', 'PS12345', CURRENT_TIMESTAMP, 'PPSALIEN', 'RL', 'TEST0002', null, '{}');
INSERT INTO financing_statements(id, state_type, expire_date, life, discharged, renewed)
  VALUES(200000001, 'ACT', CURRENT_TIMESTAMP + interval '90 days', 0, null , null)
;
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000001, 200000001, 'TEST0002', null, 'RL', 'PPSALIEN', CURRENT_TIMESTAMP, 200000001, 2,
           '2000.00', CURRENT_TIMESTAMP + interval '90 days', 'PS12345', 'TEST-RL-0001', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000003, 'TEST-0002', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000005, 'RG', 200000001, 200000001, null, null, 'TEST', '2', 'REGISTERING', null,
           null, 200000003)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id,
                  business_srch_key, bus_name_base, bus_name_key_char1)
    VALUES(200000006, 'DB', 200000001, 200000001, null, null, null, null, null, 'TEST BUS 2 DEBTOR',
           null, 200000003, searchkey_business_name('TEST BUS 2 DEBTOR'), 'TEST BUS 2 DEBTOR', 'T')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000007, 'SP', 200000001, 200000001, null, 200000000, null, null, null, null,
           null, 200000003)
;
INSERT INTO serial_collateral(id, serial_type, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000002, 'MV', 200000001, 200000001, null, 2014, 'HYUNDAI', 'TUSCON', 'KX8J3CA46JU622994', null,
         searchkey_vehicle('KX8J3CA46JU622994'))
;
-- TEST0002 end
