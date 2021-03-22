-- TEST0001 financing statement security agreement base test
-- draft statement CLOB empty for testing.
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000000, 'D-T-0001', 'PS12345', sysdate, 'PPSALIEN', 'SA', 'TEST0001', null, '{}');
INSERT INTO financing_statement(financing_id, state_type_cd, expire_date, life, discharged, renewed, registration_number)
  VALUES(200000000, 'ACT', sysdate + 730, 2, null , null, 'TEST0001')
;
INSERT INTO registration(registration_id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, document_number, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000000, 200000000, 'TEST0001', null, 'SA', 'PPSALIEN', sysdate, 'D-T-0001', 2,
           null, null, 'PS12345', 'TEST-SA-0001', null, null)
;
INSERT INTO trust_indenture(trust_id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000000, 200000000, 200000000, 'Y', null)
;
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000002, 'TEST-0001', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000000, 'RG', 200000000, 200000000, null, null, 'TEST', '1', 'REGISTERING', null,
           null, 200000002)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id, first_name_key, last_name_key)
    VALUES(200000001, 'DI', 200000000, 200000000, null, null, 'TEST IND', '1', 'DEBTOR', null,
           null, 200000002, search_key_pkg.lastname('TEST IND'), search_key_pkg.lastname('DEBTOR'))
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000002, 'DB', 200000000, 200000000, null, null, null, null, null, 'TEST BUS 2 DEBTOR',
           null, 200000002, search_key_pkg.businame('TEST BUS 2 DEBTOR'))
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000003, 'SP', 200000000, 200000000, null, null, null, null, null, 'TEST 1 SECURED PARTY',
           null, 200000002)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000004, 'SP', 200000000, 200000000, null, 200000000, null, null, null, null,
           null, 200000002)
;
INSERT INTO general_collateral(general_collateral_id, registration_id, financing_id, registration_id_end, description)
  VALUES(200000000, 200000000, 200000000, null, 'TEST0001 GC 1')
;
INSERT INTO general_collateral(general_collateral_id, registration_id, financing_id, registration_id_end, description)
  VALUES(200000001, 200000000, 200000000, null, 'TEST0001 GC 2')
;
INSERT INTO serial_collateral(serial_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000000, 'MV', 200000000, 200000000, null, 2018, 'HYUNDAI', 'TUSCON', 'KM8J3CA46JU622994', null,
         search_key_pkg.vehicle('KM8J3CA46JU622994'))
;
INSERT INTO serial_collateral(serial_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000001, 'MH', 200000000, 200000000, null, 2001, 'HOMCO IND. LTD DIPLOMAT', null, '9407', '21324', 
         search_key_pkg.mhr('9407'))
;
UPDATE draft
   SET registration_id = 200000000
 WHERE draft_id = 200000000
;
-- TEST0001 end
