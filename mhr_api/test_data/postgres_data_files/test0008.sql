-- UT-0033 000932 MHREG EXEMPT with NCON, TAXN notes.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000047, '000932', 'PS12345', 'MHREG', now() at time zone 'UTC', 'EXEMPT', 200000001, null, null, 'TESTUSER', 'UT-0033')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000128, '1234 TEST-0033', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000108, 'SUBMITTING', 'ACTIVE', 200000047, 200000047, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000128, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000129, '1234 TEST-0033', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000047, 'OTHER', 'ACTIVE', 200000047, 200000047, 190000129,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437',
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000047, 'ACTIVE', 200000047, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000047)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000044, 200000047, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000047)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000047, 'REG_101', 200000047, 'UT000047', '90499047', 'attn', NULL, NULL, 'Y', null, null, null, 200000047)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000042, 1, 200000047, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000047)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000130, '1234 TEST-0033', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000109, 'OWNER_BUS', 'ACTIVE', 200000047, 200000047, null, null, null, 'TEST EXRS ACTIVE', 
           mhr_name_compressed_key('TEST EXRS ACTIVE'), 190000130, null, NULL, null, 200000042)
;
-- UT-0033 000932 NCON note registration
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000048, '000932', 'PS12345', 'REG_STAFF_ADMIN', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0033')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000131, '1234 TEST-0033', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000110, 'SUBMITTING', 'ACTIVE', 200000048, 200000048, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000131, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000111, 'CONTACT', 'ACTIVE', 200000048, 200000048, null, null, null, 'PERSON GIVING NOTICE',
           mhr_name_compressed_key('PERSON GIVING NOTICE'), 190000131, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000048, 'NCON', 200000048, 'UT000048', '90499048', 'attn', NULL, NULL, 'Y', null, null, null, 200000048)
;
INSERT INTO mhr_notes(id, document_type, registration_id, document_id, status_type, remarks, destroyed,
                      change_registration_id, expiry_date, effective_ts)
    VALUES(200000034, 'NCON', 200000048, 200000048, 'ACTIVE', 'NCON NOTE REMARKS', 'N', 200000048,
           null, now() at time zone 'UTC')
;
-- UT-0033 000932 TAXN note registration
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000049, '000932', 'PS12345', 'REG_STAFF_ADMIN', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0033')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000132, '1234 TEST-0033', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000112, 'SUBMITTING', 'ACTIVE', 200000049, 200000049, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000132, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000113, 'CONTACT', 'ACTIVE', 200000049, 200000049, null, null, null, 'PERSON GIVING NOTICE',
           mhr_name_compressed_key('PERSON GIVING NOTICE'), 190000132, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000049, 'TAXN', 200000049, 'UT000049', '90499049', 'attn', NULL, NULL, 'Y', null, null, null, 200000049)
;
INSERT INTO mhr_notes(id, document_type, registration_id, document_id, status_type, remarks, destroyed,
                      change_registration_id, expiry_date, effective_ts)
    VALUES(200000035, 'TAXN', 200000049, 200000049, 'ACTIVE', 'TAXN NOTE REMARKS', 'N', 200000049,
           null, now() at time zone 'UTC')
;
-- UT-0033 000932 residential exemption registration
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000050, '000932', 'PS12345', 'EXEMPTION_RES', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0033')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000133, '1234 TEST-0033', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000114, 'SUBMITTING', 'ACTIVE', 200000050, 200000050, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000133, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000050, 'EXRS', 200000050, 'UT000050', '90499050', 'attn', NULL, NULL, 'Y', null, null, null, 200000050)
;
INSERT INTO mhr_notes(id, document_type, registration_id, document_id, status_type, remarks, destroyed,
                      change_registration_id, expiry_date, effective_ts)
    VALUES(200000036, 'EXRS', 200000050, 200000050, 'ACTIVE', 'RESIDENTIAL REMARKS', 'N', 200000050,
           null, now() at time zone 'UTC')
;
