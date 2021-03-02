-- TEST0013 expired more than 30 days excluded search test on all search types.
-- draft statement CLOB empty for testing.
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000017, 'D-T-0013', 'PS12345', sysdate, 'PPSALIEN', 'SA', 'TEST0013', null, '{}');
INSERT INTO financing_statement(financing_id, state_type_cd, expire_date, life, discharged, renewed, registration_number)
  VALUES(200000007, 'HEX', sysdate - 100, 1, null , null, 'TEST0013')
;
INSERT INTO registration(registration_id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, document_number, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000014, 200000007, 'TEST0013', null, 'SA', 'PPSALIEN', sysdate, 'D-T-0013', 1,
           null, null, 'PS12345', 'TEST-SA-0013', null, null)
;
INSERT INTO trust_indenture(trust_id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000005, 200000014, 200000007, 'Y', null)
;
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000016, 'TEST-0013', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000034, 'RG', 200000014, 200000007, null, null, 'TEST', '13', 'REGISTERING', null,
           null, 200000016)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000035, 'DI', 200000014, 200000007, null, null, 'TEST IND', '13', 'DEBTOR', null,
           null, 200000016)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000036, 'SP', 200000014, 200000007, null, null, null, null, null, 'TEST 13 SECURED PARTY',
           null, 200000016)
;
INSERT INTO serial_collateral(serial_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000014, 'MV', 200000014, 200000007, null, 2012, 'EXPIRED MV', 'MODEL', 'XXXXX999999', null,
         search_key_pkg.vehicle('XXXXX999999'))
;
INSERT INTO serial_collateral(serial_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000015, 'MH', 200000014, 200000007, null, 2012, 'EXPIRED MH', 'MODEL', 'XXXXX999999', '299999',
         search_key_pkg.mhr('299999'))
;
INSERT INTO serial_collateral(serial_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000016, 'AC', 200000014, 200000007, null, 2012, 'EXPIRED AC', 'MODEL', 'XXXXX999999', null,
         search_key_pkg.aircraft('XXXXX999999'))
;
INSERT INTO serial_collateral(serial_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000017, 'AF', 200000014, 200000007, null, 2012, 'EXPIRED AF', 'MODEL', 'XXXXX999999', null,
         search_key_pkg.aircraft('XXXXX999999'))
;
UPDATE draft
   SET registration_id = 200000014
 WHERE draft_id = 200000017
;
-- TEST0013 end
