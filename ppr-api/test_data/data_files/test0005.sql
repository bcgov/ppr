-- TEST0005 renewal statement base test: create financing statement, then renewal statement
-- draft statement CLOB empty for testing.
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000008, 'D-T-0005', 'PS12345', sysdate, 'PPSALIEN', 'SA', 'TEST0005', null, '{}');
INSERT INTO financing_statement(financing_id, state_type_cd, expire_date, life, discharged, renewed, registration_number)
  VALUES(200000004, 'ACT', sysdate + 365, 1, null , null, 'TEST0005')
;
INSERT INTO registration(registration_id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, document_number, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000005, 200000004, 'TEST0005', null, 'SA', 'PPSALIEN', sysdate, 'D-T-0005', 1,
           null, null, 'PS12345', 'TEST-SA-0005', null, null)
;
INSERT INTO trust_indenture(trust_id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000002, 200000005, 200000003, 'Y', null)
;
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000007, 'TEST-0005', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000015, 'RG', 200000005, 200000004, null, null, 'TEST', '5', 'REGISTERING', null,
           null, 200000007)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000016, 'DI', 200000005, 200000004, null, null, 'TEST IND', '5', 'DEBTOR', null,
           null, 200000007)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000017, 'SP', 200000005, 200000004, null, null, null, null, null, 'TEST 5 SECURED PARTY',
           null, 200000007)
;
INSERT INTO serial_collateral(vehicle_collateral_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000005, 'MV', 200000005, 200000004, null, 2018, 'TESLA', 'MODEL 3', 'YJ46JU622994', null,
         to_char(search_key_pkg.vehicle('YJ46JU622994')))
;
-- Create renewal
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000009, 'D-T-00R5', 'PS12345', sysdate, 'RENEWAL', 'RE', 'TEST0005', null, '{}');
INSERT INTO registration(registration_id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, document_number, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000006, 200000004, 'TEST00R5', 'TEST0005', 'RE', 'RENEWAL', sysdate, 'D-T-00R5', 2,
           null, null, 'PS12345', 'TEST-REN-0005', null, null)
;
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000008, 'TEST-00R5', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000018, 'RG', 200000006, 200000004, null, null, 'TEST-RENEWAL', '5', 'REGISTERING', null,
           null, 200000008)
;
UPDATE financing_statement
   SET expire_date = sysdate + 730, life = 2
 WHERE financing_id = 200000004
;
UPDATE draft
   SET registration_id = 200000005
 WHERE draft_id = 200000008
;
UPDATE draft
   SET registration_id = 200000006
 WHERE draft_id = 200000009
;
-- TEST0005 end
