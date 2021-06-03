-- TEST0015 duplicate business name registraton number test. Only one registration should be returned 
-- in the search detail results for two matches on the same registration.
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000020, 'D-T-0015', 'PS12345', CURRENT_TIMESTAMP, 'PPSALIEN', 'SA', 'TEST0015', null, '{}');
INSERT INTO financing_statements(id, state_type, expire_date, life, discharged, renewed)
  VALUES(200000009, 'ACT', CURRENT_TIMESTAMP + interval '1500 days', 5, 'Y' , null)
;
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000017, 200000009, 'TEST0015', null, 'SA', 'PPSALIEN', CURRENT_TIMESTAMP, 200000020, 1,
           null, null, 'PS12345', 'TEST-SA-0015', null, null)
;
INSERT INTO trust_indentures(id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000007, 200000017, 200000009, 'Y', null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000019, 'TEST-0015', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000043, 'RG', 200000017, 200000009, null, null, 'TEST', '14', 'REGISTERING', null,
           null, 200000019)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000044, 'DB', 200000017, 200000009, null, null, null, null, null, 'DUPLICATE NAME',
           null, 200000019, searchkey_business_name('DUPLICATE NAME'))
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000045, 'DB', 200000017, 200000009, null, null, null, null, null, 'DUPLICATE NAME',
           null, 200000019, searchkey_business_name('DUPLICATE NAME'))
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000046, 'SP', 200000017, 200000009, null, null, null, null, null, 'TEST 14 SECURED PARTY',
           null, 200000019)
;
INSERT INTO serial_collateral(id, serial_type, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000021, 'MV', 200000017, 200000009, null, 2012, 'JAGUAR', 'F-TYPE', 'VIN123434322', null,
         searchkey_vehicle('VIN123434322'))
;
-- TEST0015 end
