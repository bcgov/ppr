-- TEST0018 legacy general collateral with legacy amendments.
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000027, 'D-T-0018', 'PS12345', timestamp with time zone '2021-09-03 12:00:00-07' at time zone 'utc', 
         'PPSALIEN', 'SA', 'TEST0018', null, '{}');
INSERT INTO financing_statements(id, state_type, expire_date, life, discharged, renewed)
  VALUES(200000012, 'ACT', timestamp with time zone '2026-09-03 23:59:59-07' at time zone 'utc', 5, 'N' , null)
;
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000024, 200000012, 'TEST0018', null, 'SA', 'PPSALIEN', 
           timestamp with time zone '2021-09-03 12:00:00-07' at time zone 'utc', 200000027, 5,
           null, null, 'PS12345', 'TEST-SA-0018', null, null)
;
INSERT INTO trust_indentures(id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000009, 200000024, 200000012, 'Y', null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000026, 'TEST-0018', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000057, 'RG', 200000024, 200000012, null, null, 'TEST', '18', 'REGISTERING', null,
           null, 200000026)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000058, 'DB', 200000024, 200000012, null, null, null, null, null, 'TEST 18 DEBTOR INC.',
           null, 200000026, searchkey_business_name('TEST 18 DEBTOR INC.'))
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000059, 'SP', 200000024, 200000012, null, null, null, null, null, 'TEST 18 SECURED PARTY',
           null, 200000026)
;
INSERT INTO general_collateral_legacy(id, registration_id, financing_id, registration_id_end, description, status)
  VALUES(200000004, 200000024, 200000012, null, 'TEST0018 GC 1', null)
;
INSERT INTO general_collateral_legacy(id, registration_id, financing_id, registration_id_end, description, status)
  VALUES(200000005, 200000024, 200000012, null, 'TEST0018 GC 2', null)
;
INSERT INTO general_collateral_legacy(id, registration_id, financing_id, registration_id_end, description, status)
  VALUES(200000006, 200000024, 200000012, null, 'TEST0018 GC 3', null)
;


-- Legacy Amendment add gc
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000028, 'D-T-0018A1', 'PS12345', timestamp with time zone '2021-09-03 13:00:00-07' at time zone 'utc', 
         'AMENDMENT', 'AM', 'TEST0018A1', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path, detail_description)
    VALUES(200000025, 200000012, 'TEST0018A1', 'TEST0018', 'AM', 'AMENDMENT', 
           timestamp with time zone '2021-09-03 13:00:00-07' at time zone 'utc', 200000028, null,
           null, null, 'PS12345', 'TEST-AM-0018-1', null, null, 'TEST add gc legacy')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000027, 'TEST-0018-AM1', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000060, 'RG', 200000025, 200000012, null, null, 'TEST-0018-AM', '18-1', 'REGISTERING', null,
           null, 200000027)
;
INSERT INTO general_collateral_legacy(id, registration_id, financing_id, registration_id_end, description, status)
  VALUES(200000007, 200000025, 200000012, null, 'TEST0018 GC 4 AMEND ADD', 'A')
;


-- Legacy Amendment remove gc
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000029, 'D-T-0018A2', 'PS12345', timestamp with time zone '2021-09-03 14:00:00-07' at time zone 'utc', 
         'AMENDMENT', 'AM', 'TEST0018A2', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path, detail_description)
    VALUES(200000026, 200000012, 'TEST0018A2', 'TEST0018', 'AM', 'AMENDMENT', 
           timestamp with time zone '2021-09-03 14:00:00-07' at time zone 'utc', 200000029, null,
           null, null, 'PS12345', 'TEST-AM-0018-2', null, null, 'TEST remove gc legacy')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000028, 'TEST-0018-AM2', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000061, 'RG', 200000026, 200000012, null, null, 'TEST-0018-AM', '18-2', 'REGISTERING', null,
           null, 200000028)
;
INSERT INTO general_collateral_legacy(id, registration_id, financing_id, registration_id_end, description, status)
  VALUES(200000008, 200000026, 200000012, null, '*** DELETED *** TEST0018 GC 1 *** DELETED *** ', 'D')
;

-- New amendment remove legacy gc 2, add gc 5
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000030, 'D-T-0018A3', 'PS12345', timestamp with time zone '2021-09-03 15:00:00-07' at time zone 'utc', 
         'AMENDMENT', 'AM', 'TEST0018A3', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path, detail_description)
    VALUES(200000027, 200000012, 'TEST0018A3', 'TEST0018', 'AM', 'AMENDMENT', 
           timestamp with time zone '2021-09-03 15:00:00-07' at time zone 'utc', 200000030, null,
           null, null, 'PS12345', 'TEST-AM-0018-3', null, null, 'TEST remove gc legacy 2, add gc 5')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000029, 'TEST-0018-AM3', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000062, 'RG', 200000027, 200000012, null, null, 'TEST-0018-AM', '18-3', 'REGISTERING', null,
           null, 200000029)
;
INSERT INTO general_collateral(id, registration_id, financing_id, registration_id_end, description, status)
  VALUES(200000009, 200000027, 200000012, null, 'TEST0018 GC 5', null)
;
UPDATE general_collateral_legacy
   SET registration_id_end = 200000027
 WHERE id = 200000005
;
-- TEST0018 end
