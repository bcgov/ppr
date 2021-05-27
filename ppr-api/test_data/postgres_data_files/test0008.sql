-- TEST0008 Change Statement debtor transfer on TEST0001. 
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000012, 'D-T-00C8', 'PS12345', CURRENT_TIMESTAMP, 'CHANGE', 'DT', 'TEST0001', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000009, 200000000, 'TEST0008', 'TEST0001', 'DT', 'CHANGE', CURRENT_TIMESTAMP + interval '10 minutes', 200000012, null,
           null, null, 'PS12345', 'TEST-CH-0008', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000011, 'TEST-00C8', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000023, 'RG', 200000009, 200000000, null, null, 'TEST-CHANGE-DT', '8', 'REGISTERING', null,
           null, 200000011)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000024, 'DB', 200000009, 200000000, null, null, null, null, null, 'TEST 8 TRANSFER DEBTOR',
           null, 200000011, searchkey_business_name('TEST 8 TRANSFER DEBTOR'))
;
UPDATE parties
   SET registration_id_end = 200000009
 WHERE id = 200000021
   AND party_type = 'DB'
;
-- TEST0008 end
