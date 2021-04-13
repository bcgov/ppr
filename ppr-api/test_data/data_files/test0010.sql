-- TEST0010 Change Statement collateral subsitution on TEST0001. 
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000014, 'D-T-0010', 'PS12345', sysdate, 'CHANGE', 'SU', 'TEST0001', null, '{}');
INSERT INTO registration(registration_id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, document_number, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000011, 200000000, 'TEST0010', 'TEST0001', 'SU', 'CHANGE', sysdate, 'D-T-0010', null,
           null, null, 'PS12345', 'TEST-CH-0010', null, null)
;
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000013, 'TEST-0010', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_branch_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000027, 'RG', 200000011, 200000000, null, null, 'TEST-CHANGE-SU', '10', 'REGISTERING', null,
           null, 200000013)
;
INSERT INTO serial_collateral(serial_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000007, 'MV', 200000011, 200000000, null, 2014, 'BMW', 'Z4', 'JU622994', null,
         search_key_pkg.vehicle('JU622994'))
;
INSERT INTO serial_collateral(serial_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000008, 'MH', 200000011, 200000000, null, 2012, 'HOMCO IND. LTD DIPLOMAT', null, '999999', '220000',
         search_key_pkg.mhr('220000'))
;
INSERT INTO general_collateral(general_collateral_id, registration_id, financing_id, registration_id_end, description)
  VALUES(200000003, 200000011, 200000000, null, 'TEST GENERAL COLLATERAL CHANGE ADD.')
;
UPDATE general_collateral
  SET registration_id_end = 200000011
WHERE general_collateral_id = 200000002
;
UPDATE serial_collateral
  SET registration_id_end = 200000011
WHERE serial_id = 200000006
;
UPDATE draft
   SET registration_id = 200000011
 WHERE draft_id = 200000014
;
-- TEST0010 end
