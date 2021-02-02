-- TEST0002 financing statement repairer's lien base test
-- draft statement CLOB empty for testing.
INSERT INTO draft(draft_id, document_number, account_id, create_ts, registration_type_cl, registration_type_cd,
                  registration_number, update_ts, draft)
  VALUES(200000001, 'D-T-0002', 'PS12345', sysdate, 'PPSALIEN', 'RL', 'TEST0002', null, '{}');
INSERT INTO financing_statement(financing_id, state_type_cd, expire_date, life, discharged, renewed, registration_number)
  VALUES(200000001, 'ACT', sysdate + 90, 0, null , null, 'TEST0002')
;
INSERT INTO registration(registration_id, financing_id, registration_number, base_reg_number, registration_type_cd,
                         registration_type_cl, reg_date, document_number, life, lien_value,
                         surrender_date, account_id, client_reference_id, pay_invoice_id, pay_path)
    VALUES(200000001, 200000001, 'TEST0002', null, 'RL', 'PPSALIEN', sysdate, 'D-T-0002', 2,
           '2000.00', sysdate + 90, 'PS12345', 'TEST-RL-0001', null, null)
;
INSERT INTO address_ppr(address_id, street_line_1, street_line_2, city, province_type_cd, postal_cd, country_type_cd)
  VALUES(200000003, 'TEST-0002', 'line 2', 'city', 'BC', 'V8R3A5', 'CA')
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id, email_id)
    VALUES(200000005, 'RP', 200000001, 200000001, null, null, 'TEST', '2', 'REGISTERING', null,
           null, 200000003, 'testrp2@gmail.com')
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id)
    VALUES(200000006, 'DC', 200000001, 200000001, null, null, null, null, null, 'TEST BUS DEBTOR',
           null, 200000003)
;
INSERT INTO party(party_id, party_type_cd, registration_id, financing_id, registration_id_end, client_party_id, first_name,
                  middle_name, last_name, business_name, birth_date, address_id, email_id)
    VALUES(200000007, 'SP', 200000001, 200000001, null, 200000000, null, null, null, null,
           null, 200000003, null)
;
INSERT INTO serial_collateral(serial_collateral_id, serial_type_cd, registration_id, financing_id, registration_id_end,
                              year, make, model, serial_number, mhr_number)
  VALUES(200000002, 'MV', 200000001, 200000001, null, 2014, 'HYUNDAI', 'TUSCON', 'KX8J3CA46JU622994', null)
;
-- TEST0002 end
