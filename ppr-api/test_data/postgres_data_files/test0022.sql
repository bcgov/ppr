-- New securities act registration, amendment, discharge.
-- Secured party should match account ID.
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000041, 'D-T-0022', 'PS00002', now() at time zone 'utc', 'MISCLIEN', 'SE', 'TEST0022', null, '{}');
INSERT INTO financing_statements(id, state_type, expire_date, life, discharged, renewed)
  VALUES(200000017, 'ACT', null, 99, 'N' , null)
;
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000038, 200000017, 'TEST0022', null, 'SE', 'MISCLIEN', 
           now() at time zone 'utc', 200000041, 99,
           null, null, 'PS00002', 'TEST-SE-0022', null, null)
;
INSERT INTO securities_act_notices(id, registration_id, registration_id_end, securities_act_type, effective_ts, detail_description)
     VALUES (200000000, 200000038, null, 'PRESERVATION', (now() at time zone 'utc') - interval '1 days', 'UNIT TEST PRESERVATION ORDER');
INSERT INTO securities_act_orders(id, registration_id, registration_id_end, securities_act_notice_id, court_order_ind,
                                  order_date, court_name, court_registry, file_number, effect_of_order)
     VALUES (200000000, 200000038, null, 200000000, 'Y',  (now() at time zone 'utc') - interval '1 days', 'COURT NAME',
             'COURT REGISTRY', 'FILE# 00001', 'UNIT TEST');
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000038, 'TEST-0022', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000083, 'SP', 200000038, 200000017, null, 99980001, null, null, null, null, null, null)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000084, 'RG', 200000038, 200000017, null, 99980001, null, null, null, null, null, null)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000085, 'DB', 200000038, 200000017, null, null, null, null, null, 'TEST 22 DEBTOR INC.',
           null, 200000038, searchkey_business_name('TEST 22 DEBTOR INC.'))
;
INSERT INTO general_collateral(id, registration_id, financing_id, registration_id_end, description, status)
  VALUES(200000015, 200000038, 200000017, null, 'TEST0022 GC 1', null)
;
-- Add an amendment.

-- Discharge.
