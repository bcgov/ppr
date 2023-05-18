-- TEST0009 Change Statement secured party transfer on TEST0001. 
INSERT INTO drafts(id, document_number, account_id, create_ts, registration_type_cl, registration_type,
                  registration_number, update_ts, draft)
  VALUES(200000013, 'D-T-00C9', 'PS12345', CURRENT_TIMESTAMP, 'CHANGE', 'ST', 'TEST0001', null, '{}');
INSERT INTO registrations(id, financing_id, registration_number, base_reg_number, registration_type,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000010, 200000000, 'TEST0009', 'TEST0001', 'ST', 'CHANGE', CURRENT_TIMESTAMP + interval '15 minutes', 200000013, null,
           null, null, 'PS12345', 'TEST-CH-0009', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(200000012, 'TEST-00C9', 'LINE 2', 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000025, 'RG', 200000010, 200000000, null, null, 'TEST-CHANGE-DT', '9', 'REGISTERING', null,
           null, 200000012)
;
INSERT INTO parties(id, party_type, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_initial, last_name, business_name, birth_date, address_id)
    VALUES(200000026, 'SP', 200000010, 200000000, null, null, null, null, null, 'TEST 9 CHANGE TRANSFER SECURED PARTY',
           null, 200000012)
;
UPDATE parties
   SET registration_id_end = 200000010
 WHERE id = 200000022
   AND party_type = 'SP'
;
-- TEST0009 end
