-- TEST0006 renewal statement on repairer's lien financing statement TEST0002
-- draft statement CLOB empty for testing.
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000010, 'D-T-00R6', 'PS12345', CURRENT_TIMESTAMP, 'RENEWAL', 'RE', 'TEST0002', null, '{}');
INSERT INTO registration(registration_id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, draft_id, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000007, 200000001, 'TEST00R6', 'TEST0002', 'RE', 'RENEWAL', CURRENT_TIMESTAMP + interval '5 minutes', 200000010, 0,
           null, null, 'PS12345', 'TEST-REN-0006', null, null)
;
INSERT INTO address(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000009, 'TEST-00R6', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000019, 'RG', 200000007, 200000001, null, null, 'TEST-RENEWAL-RL', '6', 'REGISTERING', null,
           null, 200000009)
;
INSERT INTO court_order(court_order_id, registration_id, court_date, court_name, court_registry, file_number, effect_of_order)
  VALUES(200000000, 200000007, CURRENT_TIMESTAMP + interval '200 days', 'Supreme Court of British Columbia', 'Victoria', 'BC123495',
         'Court Order to renew Repairer''s Lien.')
;

UPDATE financing_statement
   SET expire_date = CURRENT_TIMESTAMP + interval '90 days', life = 0
 WHERE financing_id = 200000001
;
-- TEST0006 end
