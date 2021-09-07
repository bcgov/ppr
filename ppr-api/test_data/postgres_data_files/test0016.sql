-- TEST0016 SA and RL expiry date tests: financing statements with multiple renewals. 
-- SA begin
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000021, 'D-T-0016', 'PS12345', timestamp with time zone '2021-09-03 12:00:00-07' at time zone 'utc', 
         'PPSALIEN', 'SA', 'TEST0016', null, '{}');
INSERT INTO financing_statements(id, state_type, expire_date, life, discharged, renewed)
  VALUES(200000010, 'ACT', timestamp with time zone '2026-09-03 23:59:59-07' at time zone 'utc', 5, 'N' , null)
;
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000018, 200000010, 'TEST0016', null, 'SA', 'PPSALIEN', 
           timestamp with time zone '2021-09-03 12:00:00-07' at time zone 'utc', 200000021, 5,
           null, null, 'PS12345', 'TEST-SA-0016', null, null)
;
INSERT INTO trust_indentures(id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000008, 200000018, 200000010, 'Y', null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000020, 'TEST-0016', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000047, 'RG', 200000018, 200000010, null, null, 'TEST', '16', 'REGISTERING', null,
           null, 200000020)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000048, 'DB', 200000018, 200000010, null, null, null, null, null, 'TEST 16 DEBTOR INC.',
           null, 200000020, searchkey_business_name('TEST 16 DEBTOR INC.'))
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000049, 'SP', 200000018, 200000010, null, null, null, null, null, 'TEST 16 SECURED PARTY',
           null, 200000020)
;
INSERT INTO serial_collateral(id, serial_type, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000022, 'MV', 200000018, 200000010, null, 2012, 'JAGUAR', 'S-TYPE', 'VIN123434344', null,
         searchkey_vehicle('VIN123434344'))
;

-- Renewal #1 10 years
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000022, 'D-T-0016R1', 'PS12345', timestamp with time zone '2021-09-03 13:00:00-07' at time zone 'utc', 
         'RENEWAL', 'RE', 'TEST0016R1', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000019, 200000010, 'TEST0016R1', 'TEST0016', 'RE', 'RENEWAL', 
           timestamp with time zone '2021-09-03 13:00:00-07' at time zone 'utc', 200000022, 10,
           null, null, 'PS12345', 'TEST-REN-0016-1', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000021, 'TEST-0016R1', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000050, 'RG', 200000019, 200000010, null, null, 'TEST-0016-RENEWAL', '16-1', 'REGISTERING', null,
           null, 200000021)
;

-- Renewal #2 5 years
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000023, 'D-T-0016R2', 'PS12345', timestamp with time zone '2021-09-03 14:00:00-07' at time zone 'utc', 
         'RENEWAL', 'RE', 'TEST0016R2', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000020, 200000010, 'TEST0016R2', 'TEST0016', 'RE', 'RENEWAL', 
           timestamp with time zone '2021-09-03 14:00:00-07' at time zone 'utc', 200000023, 5,
           null, null, 'PS12345', 'TEST-REN-0016-2', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000022, 'TEST-00R5', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000051, 'RG', 200000020, 200000010, null, null, 'TEST-0016-RENEWAL', '16-2', 'REGISTERING', null,
           null, 200000022)
;

UPDATE financing_statements
   SET expire_date = expire_date + interval '15 years', life = 20
 WHERE id = 200000010
;

-- SA end

-- RL begin
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000024, 'D-T-0017', 'PS12345', timestamp with time zone '2021-08-31 12:00:00-07' at time zone 'utc', 
         'PPSALIEN', 'RL', 'TEST0017', null, '{}');
INSERT INTO financing_statements(id, state_type, expire_date, life, discharged, renewed)
  VALUES(200000011, 'ACT', timestamp with time zone '2022-02-27 23:59:59-07' at time zone 'utc', 0, 'N' , null)
;
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000021, 200000011, 'TEST0017', null, 'RL', 'PPSALIEN', 
           timestamp with time zone '2021-08-31 12:00:00-07' at time zone 'utc', 200000024, 0,
           '1000.00', current_timestamp, 'PS12345', 'TEST-RL-0017', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000023, 'TEST-0017', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000052, 'RG', 200000021, 200000011, null, null, 'TEST', '17', 'REGISTERING', null,
           null, 200000023)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000053, 'DB', 200000021, 200000011, null, null, null, null, null, 'TEST 17 DEBTOR INC.',
           null, 200000023, searchkey_business_name('TEST 17 DEBTOR INC.'))
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000054, 'SP', 200000021, 200000011, null, null, null, null, null, 'TEST 17 SECURED PARTY',
           null, 200000023)
;
INSERT INTO serial_collateral(id, serial_type, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000023, 'MV', 200000021, 200000011, null, 2012, 'JAGUAR', 'R-TYPE', 'VIN123434366', null,
         searchkey_vehicle('VIN123434366'))
;

-- Renewal #1
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000025, 'D-T-0017R1', 'PS12345', timestamp with time zone '2021-08-31 13:00:00-07' at time zone 'utc', 
         'RENEWAL', 'RE', 'TEST0017R1', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000022, 200000011, 'TEST0017R1', 'TEST0017', 'RE', 'RENEWAL', 
           timestamp with time zone '2021-08-31 13:00:00-07' at time zone 'utc', 200000025, 0,
           null, null, 'PS12345', 'TEST-REN-0017-1', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000024, 'TEST-0017R1', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000055, 'RG', 200000022, 200000011, null, null, 'TEST-0017-RENEWAL', '17-1', 'REGISTERING', null,
           null, 200000024)
;

-- Renewal #2
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000026, 'D-T-0017R2', 'PS12345', timestamp with time zone '2021-08-31 14:00:00-07' at time zone 'utc', 
         'RENEWAL', 'RE', 'TEST0017R2', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000023, 200000011, 'TEST0017R2', 'TEST0017', 'RE', 'RENEWAL', 
           timestamp with time zone '2021-08-31 14:00:00-07' at time zone 'utc', 200000026, 0,
           null, null, 'PS12345', 'TEST-REN-0017-2', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000025, 'TEST-0017R2', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000056, 'RG', 200000023, 200000011, null, null, 'TEST-0017-RENEWAL', '17-2', 'REGISTERING', null,
           null, 200000025)
;

UPDATE financing_statements
   SET expire_date = expire_date + interval '360 days'
 WHERE id = 200000011
;
UPDATE financing_statements
   SET expire_date = expire_date + interval '1 hours'
 WHERE id = 200000011
;

-- RL end

-- TEST0016 end
