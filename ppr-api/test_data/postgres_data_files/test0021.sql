-- TEST0019 extended: renewal, discharge created with another account; base reg added to test account.
-- No match on registering, secured party names, so test account GETs are unauthorized.
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000035, 'D-T-0019RE', 'PS00001', timestamp with time zone '2021-09-03 15:00:00-07' at time zone 'utc', 
         'RENEWAL', 'RE', 'TEST0019', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000032, 200000013, 'TEST0019RE', 'TEST0019', 'RE', 'RENEWAL', 
           timestamp with time zone '2021-09-03 15:00:00-07' at time zone 'utc', 200000035, 5,
           null, null, 'PS00001', 'TEST-RE-0019', null, null)
;
-- simulate bad legacy address
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000034, 'TEST-0019RE', null, 'city', null, null, null)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000074, 'RG', 200000032, 200000013, null, null, 'TEST-RENEWAL', '19', 'REGISTERING', null,
           null, 200000034)
;

INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000036, 'D-T-0019DC', 'PS00001', CURRENT_TIMESTAMP at time zone 'utc', 
         'DISCHARGE', 'DC', 'TEST0019', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000033, 200000013, 'TEST0019DC', 'TEST0019', 'DC', 'DISCHARGE', 
           CURRENT_TIMESTAMP at time zone 'utc', 200000036, 0,
           null, null, 'PS00001', 'TEST-DC-0019', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000035, 'TEST-0019DC', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000075, 'RG', 200000033, 200000013, null, null, 'TEST-DISCHARGE', '19', 'REGISTERING', null,
           null, 200000035)
;

-- Now create a financing statement, amendment, renewal, discharge on another account with matching registering party
-- or secured party name, and add it to the test account.
-- Financing statement secured party should match user account name
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000037, 'D-T-0021', 'PS00001', timestamp with time zone '2021-09-03 12:00:00-07' at time zone 'utc', 
         'PPSALIEN', 'SA', 'TEST0021', null, '{}');
INSERT INTO financing_statements(id, state_type, expire_date, life, discharged, renewed)
  VALUES(200000016, 'ACT', timestamp with time zone '2026-09-03 23:59:59-07' at time zone 'utc', 5, 'N' , null)
;
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000034, 200000016, 'TEST0021', null, 'SA', 'PPSALIEN', 
           timestamp with time zone '2021-09-03 12:00:00-07' at time zone 'utc', 200000037, 5,
           null, null, 'PS00001', 'TEST-SA-0021', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000036, 'TEST-0021', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000076, 'SP', 200000034, 200000016, null, 200000003, null, null, null, null, null, null)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000077, 'RG', 200000034, 200000016, null, 200000001, null, null, null, null, null, null)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000078, 'DB', 200000034, 200000016, null, null, null, null, null, 'TEST 21 DEBTOR INC.',
           null, 200000036, searchkey_business_name('TEST 21 DEBTOR INC.'))
;
INSERT INTO general_collateral(id, registration_id, financing_id, registration_id_end, description, status)
  VALUES(200000014, 200000034, 200000016, null, 'TEST0021 GC 1', null)
;

-- Add an amendment with matching reg party name.
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000038, 'D-T-0021AM', 'PS00001', timestamp with time zone '2021-09-03 14:00:00-07' at time zone 'utc', 
         'PPSALIEN', 'SA', 'TEST0021', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000035, 200000016, 'TEST0021AM', 'TEST0021', 'AM', 'AMENDMENT',
           timestamp with time zone '2021-09-03 14:00:00-07' at time zone 'utc', 200000038, null,
           null, null, 'PS00001', 'TEST-AM1-0021', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000037, 'TEST-0021AM', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000079, 'RG', 200000035, 200000016, null, null, null, null, null, 'PH Testing PPR with PAD',
           null, 200000037);
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000080, 'DB', 200000035, 200000016, null, null, null, null, null, 'TEST 21 AMEND ADD DEBTOR',
           null, 200000037, searchkey_business_name('TEST 21 AMEND ADD DEBTOR'))
;

INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000039, 'D-T-0021RE', 'PS00001', timestamp with time zone '2021-09-03 15:00:00-07' at time zone 'utc', 
         'RENEWAL', 'RE', 'TEST0021', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000036, 200000016, 'TEST0021RE', 'TEST0021', 'RE', 'RENEWAL', 
           timestamp with time zone '2021-09-03 15:00:00-07' at time zone 'utc', 200000039, 5,
           null, null, 'PS00001', 'TEST-RE-0021', null, null)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000081, 'RG', 200000036, 200000016, null, 200000003, null, null, null, null,
           null, null)
;

INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000040, 'D-T-0021DC', 'PS00001', CURRENT_TIMESTAMP at time zone 'utc', 
         'DISCHARGE', 'DC', 'TEST0021', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000037, 200000016, 'TEST0021DC', 'TEST0021', 'DC', 'DISCHARGE', 
           CURRENT_TIMESTAMP at time zone 'utc', 200000040, 0,
           null, null, 'PS00001', 'TEST-DC-0021', null, null)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000082, 'RG', 200000037, 200000016, null, 200000003, null, null, null, null,
           null, null)
;


INSERT INTO user_extra_registrations(id, account_id, registration_number, removed_ind)
  VALUES(200000003, 'PS12345', 'TEST0021', null)
;
