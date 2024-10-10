-- TEST0020 Financing statements crown charge registering and secured party with only client codes.
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000034, 'D-T-0020', 'PS00002', timestamp with time zone '2021-09-03 12:00:00-07' at time zone 'utc', 
         'CROWNLIEN', 'IP', 'TEST0020', null, '{}');
INSERT INTO financing_statements(id, state_type, expire_date, life, discharged, renewed)
  VALUES(200000015, 'ACT', timestamp with time zone '2026-09-03 23:59:59-07' at time zone 'utc', 5, 'N' , null)
;
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000031, 200000015, 'TEST0020', null, 'IP', 'CROWNLIEN', 
           timestamp with time zone '2021-09-03 12:00:00-07' at time zone 'utc', 200000034, 99,
           null, null, 'PS00002', 'TEST-SA-0020', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000033, 'TEST-0020', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000071, 'RG', 200000031, 200000015, null, 200000000, null, null, null, null, null, null)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000072, 'SP', 200000031, 200000015, null, 200000001, null, null, null, null, null, null)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000073, 'DB', 200000031, 200000015, null, null, null, null, null, 'TEST 20 DEBTOR INC.',
           null, 200000033, searchkey_business_name('TEST 20 DEBTOR INC.'))
;
INSERT INTO general_collateral(id, registration_id, financing_id, registration_id_end, description, status)
  VALUES(200000013, 200000031, 200000015, null, 'TEST0020 GC 1', null)
;
