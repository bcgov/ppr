-- TEST0011 serial number MHR, AC test match data:
-- draft statement CLOB empty for testing.
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000015, 'D-T-0011', 'PS12345', sysdate, 'PPSALIEN', 'SA', 'TEST0011', null, '{}');
INSERT INTO financing_statement(financing_id, state_type_cd, expire_date, life, discharged, renewed, registration_number)
  VALUES(200000005, 'ACT', sysdate + 365, 1, null , null, 'TEST0011')
;
INSERT INTO registration(registration_id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, document_number, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000012, 200000005, 'TEST0011', null, 'SA', 'PPSALIEN', sysdate, 'D-T-0011', 1,
           null, null, 'PS12345', 'TEST-SA-0011', null, null)
;
INSERT INTO trust_indenture(trust_id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000003, 200000012, 200000005, 'Y', null)
;
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000014, 'TEST-0011', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000028, 'RG', 200000012, 200000005, null, null, 'TEST', '11', 'REGISTERING', null,
           null, 200000014)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000029, 'DI', 200000012, 200000005, null, null, 'TEST IND', '11', 'DEBTOR', null,
           null, 200000014)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000030, 'SP', 200000012, 200000005, null, null, null, null, null, 'TEST 11 SECURED PARTY',
           null, 200000014)
;
INSERT INTO serial_collateral(vehicle_collateral_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000009, 'MH', 200000012, 200000005, null, 2012, 'HOMCO IND. LTD DIPLOMAT', null, '999999', '220000',
         search_key_pkg.mhr('220000'))
;
INSERT INTO serial_collateral(vehicle_collateral_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000010, 'AC', 200000012, 200000005, null, 1998, 'CESSNA', '172R SKYHAWK', 'CFYXW', null,
         search_key_pkg.aircraft('CFYXW'))
;
UPDATE draft
   SET registration_id = 200000012
 WHERE draft_id = 200000015
;
-- TEST0011 end
