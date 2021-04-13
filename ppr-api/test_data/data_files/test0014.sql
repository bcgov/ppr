-- TEST0014 discharged more than 30 days excluded search test on all search types.
-- draft statement CLOB empty for testing.
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000018, 'D-T-0014', 'PS12345', sysdate, 'PPSALIEN', 'SA', 'TEST0014', null, '{}');
INSERT INTO financing_statement(financing_id, state_type_cd, expire_date, life, discharged, renewed, registration_number)
  VALUES(200000008, 'HDC', sysdate + 1500, 5, 'Y' , null, 'TEST0014')
;
INSERT INTO registration(registration_id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, document_number, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000015, 200000008, 'TEST0014', null, 'SA', 'PPSALIEN', sysdate - 60, 'D-T-0014', 1,
           null, null, 'PS12345', 'TEST-SA-0014', null, null)
;
INSERT INTO trust_indenture(trust_id, registration_id, financing_id, trust_indenture, registration_id_end)
  VALUES(200000006, 200000015, 200000008, 'Y', null)
;
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000017, 'TEST-0014', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_branch_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000038, 'RG', 200000015, 200000008, null, null, 'TEST', '14', 'REGISTERING', null,
           null, 200000017)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_branch_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id, first_name_key, last_name_key)
    VALUES(200000039, 'DI', 200000015, 200000008, null, null, 'TEST IND DEBTOR', '14', 'ZZZZZ99', null,
           null, 200000017, search_key_pkg.lastname('TEST IND DEBTOR'), search_key_pkg.firstname('ZZZZZ99'))
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_branch_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id, business_srch_key)
    VALUES(200000040, 'DB', 200000015, 200000008, null, null, null, null, null, 'ZZZZZ99',
           null, 200000017, search_key_pkg.businame('ZZZZZ99'))
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_branch_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000041, 'SP', 200000015, 200000008, null, null, null, null, null, 'TEST 14 SECURED PARTY',
           null, 200000017)
;
INSERT INTO serial_collateral(serial_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000018, 'MV', 200000015, 200000008, null, 2012, 'DISCHARGED MV', 'MODEL', 'ZZZZZ999999', null,
         search_key_pkg.vehicle('ZZZZZ999999'))
;
INSERT INTO serial_collateral(serial_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000019, 'MH', 200000015, 200000008, null, 2012, 'DISCHARGED MH', 'MODEL', 'ZZZZZ999999', '399999',
        search_key_pkg.mhr('399999'))
;
INSERT INTO serial_collateral(serial_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number, srch_vin)
  VALUES(200000020, 'AC', 200000015, 200000008, null, 2012, 'DISCHARGED AC', 'MODEL', 'ZZZZZ999999', null,
         search_key_pkg.aircraft('ZZZZZ999999'))
;
UPDATE draft
   SET registration_id = 200000015
 WHERE draft_id = 200000018
;
-- Create discharge
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000019, 'D-T-0D14', 'PS12345', sysdate, 'DISCHARGE', 'DC', 'TEST0D14', null, '{}');
INSERT INTO registration(registration_id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, registration_ts, document_number, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000016, 200000008, 'TEST0D14', 'TEST0014', 'DC', 'DISCHARGE', sysdate - 45, 'D-T-0D14', 0,
           null, null, 'PS12345', 'TEST-DIS-0014', null, null)
;
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000018, 'TEST-0D14', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_branch_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000042, 'RG', 200000016, 200000008, null, null, 'TEST-DISCHARGE', '14', 'REGISTERING', null,
           null, 200000018)
;
UPDATE draft
   SET registration_id = 200000016
 WHERE draft_id = 200000019
;
-- TEST0014 end
