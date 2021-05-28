-- TEST0003 Historical/discharged financing statement base test
-- draft statement CLOB empty for testing.
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000002, 'D-T-0003', 'PS12345', CURRENT_TIMESTAMP, 'PPSALIEN', 'RL', 'TEST0003', null, '{}');
INSERT INTO financing_statements(id, state_type, expire_date, life, discharged, renewed)
  VALUES(200000002, 'HDC', CURRENT_TIMESTAMP + interval '90 days', 0, 'Y' , null)
;
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000002, 200000002, 'TEST0003', null, 'RL', 'PPSALIEN', CURRENT_TIMESTAMP, 200000002, 2,
           '2000.00', CURRENT_TIMESTAMP - interval '10 days', 'PS12345', 'TEST-RL-0002', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000004, 'TEST-0002', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000008, 'RG', 200000002, 200000002, null, null, 'TEST', '3', 'REGISTERING', null,
           null, 200000004)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000009, 'DB', 200000002, 200000002, null, null, null, null, null, 'TEST BUS 3 DEBTOR',
           null, 200000004, searchkey_business_name('TEST BUS 3 DEBTOR'))
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000010, 'SP', 200000002, 200000002, null, 200000000, null, null, null, null,
           null, 200000004)
;
INSERT INTO serial_collateral(id, serial_type, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000003, 'MV', 200000002, 200000002, null, 2014, 'HYUNDAI', 'TUSCON', 'KX8J3CA46JU622994', null,
         searchkey_vehicle('KX8J3CA46JU622994'))
;
-- TEST0003 end
