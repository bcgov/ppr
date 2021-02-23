-- TEST0009 Change Statement secured party transfer on TEST0001. 
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000013, 'D-T-00C9', 'PS12345', sysdate, 'CHANGE', 'ST', 'TEST0001', null, '{}');
INSERT INTO registration(registration_id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, document_number, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000010, 200000000, 'TEST0009', 'TEST0001', 'ST', 'CHANGE', sysdate + 15/1440, 'D-T-00C9', null,
           null, null, 'PS12345', 'TEST-CH-0009', null, null)
;
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000012, 'TEST-00C9', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000025, 'RG', 200000010, 200000000, null, null, 'TEST-CHANGE-DT', '9', 'REGISTERING', null,
           null, 200000012)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000026, 'SP', 200000010, 200000000, null, null, null, null, null, 'TEST 9 CHANGE TRANSFER SECURED PARTY',
           null, 200000012)
;
UPDATE party
   SET registration_id_end = 200000010
 WHERE party_id = 200000022
   AND party_type_cd = 'SP'
;
UPDATE draft
   SET registration_id = 200000010
 WHERE draft_id = 200000013
;
-- TEST0009 end
