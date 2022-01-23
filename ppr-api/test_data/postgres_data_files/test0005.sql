-- TEST0005 renewal statement base test: create financing statement, then renewal statement
-- draft statement CLOB empty for testing.
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000008, 'D-T-0005', 'PS12345', CURRENT_TIMESTAMP, 'PPSALIEN', 'SA', 'TEST0005', null, '{}');
INSERT INTO financing_statements(id, state_type, expire_date, life, discharged, renewed)
  VALUES(200000004, 'ACT', CURRENT_TIMESTAMP + interval '365 days', 1, null , null)
;
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000005, 200000004, 'TEST0005', null, 'SA', 'PPSALIEN', CURRENT_TIMESTAMP, 200000008, 1,
           null, null, 'PS12345', 'TEST-SA-0005', null, null)
;
INSERT INTO trust_indentures(id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000002, 200000005, 200000003, 'Y', null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000007, 'TEST-0005', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000015, 'RG', 200000005, 200000004, null, null, 'TEST', '5', 'REGISTERING', null,
           null, 200000007)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, first_name_key, last_name_key,
                  last_name_split1, last_name_split2, last_name_split3, first_name_split1, first_name_split2,
                  first_name_char1, first_name_key_char1)
    VALUES(200000016, 'DI', 200000005, 200000004, null, null, 'TEST IND', '5', 'DEBTOR', null,
           null, 200000007, searchkey_individual('DEBTOR', 'TEST IND'), null,
           individual_split_1('DEBTOR'), individual_split_2('DEBTOR'), individual_split_3('DEBTOR'),
           individual_split_1('TEST IND'), individual_split_2('TEST IND'), 'T', 'T')            
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000017, 'SP', 200000005, 200000004, null, null, null, null, null, 'TEST 5 SECURED PARTY',
           null, 200000007)
;
INSERT INTO serial_collateral(id, serial_type, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000005, 'MV', 200000005, 200000004, null, 2018, 'TESLA', 'MODEL 3', 'YJ46JU622994', null,
         searchkey_vehicle('YJ46JU622994'))
;
-- Create renewal
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000009, 'D-T-00R5', 'PS12345', CURRENT_TIMESTAMP, 'RENEWAL', 'RE', 'TEST0005', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000006, 200000004, 'TEST00R5', 'TEST0005', 'RE', 'RENEWAL', CURRENT_TIMESTAMP + interval '5 minutes', 200000009, 2,
           null, null, 'PS12345', 'TEST-REN-0005', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000008, 'TEST-00R5', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000018, 'RG', 200000006, 200000004, null, null, 'TEST-RENEWAL', '5', 'REGISTERING', null,
           null, 200000008)
;
UPDATE financing_statements
   SET expire_date = CURRENT_TIMESTAMP + interval '730 days', life = 2
 WHERE id = 200000004
;
-- TEST0005 end
