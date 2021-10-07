-- TEST0019 user account extra registration test data. Financing statements created with a different account id.
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000031, 'D-T-0019', 'PS00001', timestamp with time zone '2021-09-03 12:00:00-07' at time zone 'utc', 
         'PPSALIEN', 'SA', 'TEST0019', null, '{}');
INSERT INTO financing_statements(id, state_type, expire_date, life, discharged, renewed)
  VALUES(200000013, 'ACT', timestamp with time zone '2026-09-03 23:59:59-07' at time zone 'utc', 5, 'N' , null)
;
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000028, 200000013, 'TEST0019', null, 'SA', 'PPSALIEN', 
           timestamp with time zone '2021-09-03 12:00:00-07' at time zone 'utc', 200000031, 5,
           null, null, 'PS00001', 'TEST-SA-0019', null, null)
;
INSERT INTO trust_indentures(id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000010, 200000028, 200000013, 'N', null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000030, 'TEST-0019', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000063, 'RG', 200000028, 200000013, null, null, 'TEST', '19', 'REGISTERING', null,
           null, 200000030)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000064, 'DB', 200000028, 200000013, null, null, null, null, null, 'TEST 19 DEBTOR INC.',
           null, 200000030, searchkey_business_name('TEST 19 DEBTOR INC.'))
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000065, 'SP', 200000028, 200000013, null, null, null, null, null, 'TEST 19 SECURED PARTY',
           null, 200000030)
;
INSERT INTO general_collateral(id, registration_id, financing_id, registration_id_end, description, status)
  VALUES(200000011, 200000028, 200000013, null, 'TEST0019 GC 1', null)
;
-- one added
INSERT INTO user_extra_registrations(id, account_id, registration_number)
  VALUES(200000000, 'PS12345', 'TEST0019')
;

-- one that can be added
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000032, 'D-T-0019A', 'PS00001', timestamp with time zone '2021-09-03 11:00:00-07' at time zone 'utc', 
         'PPSALIEN', 'SA', 'TEST0019A', null, '{}');
INSERT INTO financing_statements(id, state_type, expire_date, life, discharged, renewed)
  VALUES(200000014, 'ACT', timestamp with time zone '2026-09-03 23:59:59-07' at time zone 'utc', 5, 'N' , null)
;
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000029, 200000014, 'TEST0019A', null, 'SA', 'PPSALIEN', 
           timestamp with time zone '2021-09-03 11:00:00-07' at time zone 'utc', 200000032, 5,
           null, null, 'PS00001', 'TEST-SA-0019A', null, null)
;
INSERT INTO trust_indentures(id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000011, 200000029, 200000014, 'N', null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000031, 'TEST-0019A', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000066, 'RG', 200000029, 200000014, null, null, 'TEST', '19A', 'REGISTERING', null,
           null, 200000031)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000067, 'DB', 200000029, 200000014, null, null, null, null, null, 'TEST 19A DEBTOR INC.',
           null, 200000031, searchkey_business_name('TEST 19 DEBTOR INC.'))
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000068, 'SP', 200000029, 200000014, null, null, null, null, null, 'TEST 19A SECURED PARTY',
           null, 200000031)
;
INSERT INTO general_collateral(id, registration_id, financing_id, registration_id_end, description, status)
  VALUES(200000012, 200000029, 200000014, null, 'TEST0019A GC 1', null)
;

-- Add an amendment for registration access testing
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000033, 'D-T-0019AM', 'PS00001', timestamp with time zone '2021-09-03 14:00:00-07' at time zone 'utc', 
         'PPSALIEN', 'SA', 'TEST0019', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000030, 200000013, 'TEST0019AM', 'TEST0019', 'AM', 'PPSALIEN', 
           timestamp with time zone '2021-09-03 14:00:00-07' at time zone 'utc', 200000033, null,
           null, null, 'PS00001', 'TEST-AM1-0019', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000032, 'TEST-0019AM', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000069, 'RG', 200000030, 200000013, null, null, 'TEST', '19AM', 'REGISTERING', null,
           null, 200000032)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000070, 'DB', 200000030, 200000013, null, null, null, null, null, 'TEST 19 AMEND ADD DEBTOR',
           null, 200000032, searchkey_business_name('TEST 19 AMEND ADD DEBTOR'))
;

-- TEST0019 end
