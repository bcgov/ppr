-- TEST0007 Amendment on TEST0001. Update all possible entities.
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000011, 'D-T-00A7', 'PS12345', CURRENT_TIMESTAMP, 'AMENDMENT', 'CO', 'TEST0001', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path, detail_description)
    VALUES(200000008, 200000000, 'TEST0007', 'TEST0001', 'CO', 'AMENDMENT', CURRENT_TIMESTAMP + interval '5 minutes', 200000011, null,
           null, null, 'PS12345', 'TEST-AM-0007', null, null, 'Description of court order.')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000010, 'TEST-00A7', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000020, 'RG', 200000008, 200000000, null, null, 'TEST-AMEND-CO', '7', 'REGISTERING', null,
           null, 200000010)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000021, 'DB', 200000008, 200000000, null, null, null, null, null, 'TEST 7 AMEND DEBTOR',
           null, 200000010, searchkey_business_name('TEST 7 AMEND DEBTOR'))
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000022, 'SP', 200000008, 200000000, null, null, null, null, null, 'TEST 7 AMEND SECURED PARTY',
           null, 200000010)
;
INSERT INTO serial_collateral(id, serial_type, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000006, 'MV', 200000008, 200000000, null, 2018, 'FORD', 'FIESTA', 'T346JU622994', null,
         searchkey_vehicle('T346JU622994'))
;
INSERT INTO general_collateral(id, registration_id, financing_id, registration_id_end, description)
  VALUES(200000002, 200000008, 200000000, null, 'TEST GENERAL COLLATERAL AMEND ADD.')
;
INSERT INTO court_orders(id, registration_id, order_date, court_name, court_registry, file_number, effect_of_order)
  VALUES(200000001, 200000008, CURRENT_TIMESTAMP + interval '200 days', 'Supreme Court of British Columbia', 'Victoria', 'BC123495',
         'Court Order to change something.')
;
UPDATE parties
   SET registration_id_end = 200000008
 WHERE id IN (200000001, 200000003)
;
UPDATE general_collateral
  SET registration_id_end = 200000008
WHERE id = 200000001
;
UPDATE serial_collateral
  SET registration_id_end = 200000008
WHERE id = 200000001
;
-- TEST0007 end
