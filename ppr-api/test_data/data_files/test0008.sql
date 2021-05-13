-- TEST0008 Change Statement debtor transfer on TEST0001. 
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000012, 'D-T-00C8', 'PS12345', sysdate, 'CHANGE', 'DT', 'TEST0001', null, '{}');
INSERT INTO registration(registration_id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, document_number, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000009, 200000000, 'TEST0008', 'TEST0001', 'DT', 'CHANGE', sysdate + 10/1440, 'D-T-00C8', null,
           null, null, 'PS12345', 'TEST-CH-0008', null, null)
;
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000011, 'TEST-00C8', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000023, 'RG', 200000009, 200000000, null, null, 'TEST-CHANGE-DT', '8', 'REGISTERING', null,
           null, 200000011)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, branch_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000024, 'DB', 200000009, 200000000, null, null, null, null, null, 'TEST 8 TRANSFER DEBTOR',
           null, 200000011, search_key_pkg.businame('TEST 8 TRANSFER DEBTOR'))
;
UPDATE party
   SET registration_id_end = 200000009
 WHERE party_id = 200000021
   AND party_type_cd = 'DB'
;
UPDATE draft
   SET registration_id = 200000004
 WHERE draft_id = 200000007
;
UPDATE draft
   SET registration_id = 200000009
 WHERE draft_id = 200000012
;
-- TEST0008 end
