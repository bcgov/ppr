-- Miscellaneous transort Permit, exemption reg test registrations. 
-- UT-0027 000926 Manufacturer registration with existing transport permit registration.
-- UT-0028 000927 new MH registration for a manufacturer
-- UT-0029 000928 EXEMPT non-residential MH registration
-- UT-0030 000929 COMMON registration 1 ADMINISTRATOR.
-- UT-0031 000930 Registration with expired transport permit registration.
-- UT-0032 000931 Non-manufacturer registration with active transport permit registration.

-- UT-0027 000926 Manufacturer registration with existing transport permit registration.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000037, '000926', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0027')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000099, '1234 TEST-0027', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000088, 'SUBMITTING', 'ACTIVE', 200000037, 200000037, null, null, null, 'REAL ENGINEERED HOMES INC',
           mhr_name_compressed_key('REAL ENGINEERED HOMES INC'), 190000099, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000100, '1234 TEST-0027', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000037, 'MANUFACTURER', 'ACTIVE', 200000037, 200000037, 190000100,
           NULL, 'additional', 'REAL ENGINEERED HOMES INC', NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000037, 'ACTIVE', 200000037, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'REAL ENGINEERED HOMES INC', 'make', 'model', 'rebuilt', 'other', 200000037)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000038, 200000037, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000037)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000037, 'REG_101', 200000037, 'UT000037', '90499037', 'attn', NULL, NULL, 'Y', null, null, null, 200000037)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000035, 1, 200000037, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000037, 1)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000101, '1234 TEST-0027', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000089, 'OWNER_BUS', 'ACTIVE', 200000037, 200000037, null, null, null, 'REAL ENGINEERED HOMES INC', 
           mhr_name_compressed_key('REAL ENGINEERED HOMES INC'), 190000101, null, '6041234567', null, 200000035)
;
-- Transport permit registration
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000038, '000926', 'PS12345', 'PERMIT', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0027')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000102, '1234 TEST-0027', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000090, 'SUBMITTING', 'ACTIVE', 200000038, 200000038, null, null, null, 'REAL ENGINEERED HOMES INC',
           mhr_name_compressed_key('REAL ENGINEERED HOMES INC'), 190000102, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000103, '1234 TEST-0027', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000038, 'MH_PARK', 'ACTIVE', 200000038, 200000038, 190000103,
           NULL, 'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', 'PARK NAME', '1234', NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000038, 'REG_103', 200000038, 'UT000038', '90499038', 'attn', NULL, NULL, 'Y', null, null, null, 200000038)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000104, '1234 TEST-0027', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000091, 'CONTACT', 'ACTIVE', 200000038, 200000038, null, null, null, 'PERSON GIVING NOTICE',
           mhr_name_compressed_key('PERSON GIVING NOTICE'), 190000104, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_notes(id, document_type, registration_id, document_id, status_type, remarks, destroyed,
                      change_registration_id, expiry_date, effective_ts)
    VALUES(200000030, 'REG_103', 200000038, 200000038, 'ACTIVE', null, 'N', 200000038,
           (now() at time zone 'UTC') + interval '30 days', now() at time zone 'UTC')
;
UPDATE mhr_locations
   SET status_type = 'HISTORICAL', change_registration_id = 200000038
 WHERE id = 200000037
;
-- UT-0028 000927 new MH registration for a manufacturer
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000039, '000927', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0028')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000105, '1234 TEST-0028', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000092, 'SUBMITTING', 'ACTIVE', 200000039, 200000039, null, null, null, 'REAL ENGINEERED HOMES INC',
           mhr_name_compressed_key('REAL ENGINEERED HOMES INC'), 190000105, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000106, '1234 TEST-0028', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000039, 'MANUFACTURER', 'ACTIVE', 200000039, 200000039, 190000106,
           NULL, 'additional', 'REAL ENGINEERED HOMES INC', NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000039, 'ACTIVE', 200000039, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'REAL ENGINEERED HOMES INC', 'make', 'model', 'rebuilt', 'other', 200000039)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000039, 200000039, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000039)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000039, 'REG_101', 200000039, 'UT000039', '90499039', 'attn', NULL, NULL, 'Y', null, null, null, 200000039)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000036, 1, 200000039, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000039, 1)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000107, '1234 TEST-0028', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000093, 'OWNER_BUS', 'ACTIVE', 200000039, 200000039, null, null, null, 'REAL ENGINEERED HOMES INC', 
           mhr_name_compressed_key('REAL ENGINEERED HOMES INC'), 190000107, null, '6041234567', null, 200000036)
;
-- UT-0029 000928 EXEMPT non-residential MH registration
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000040, '000928', 'PS12345', 'MHREG', now() at time zone 'UTC', 'EXEMPT', 200000001, null, null, 'TESTUSER', 'UT-0029')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000108, '1234 TEST-0029', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000094, 'SUBMITTING', 'ACTIVE', 200000040, 200000040, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000108, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000109, '1234 TEST-0029', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000040, 'OTHER', 'ACTIVE', 200000040, 200000040, 190000109,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437',
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000040, 'ACTIVE', 200000040, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000040)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000040, 200000040, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000040)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000040, 'REG_101', 200000040, 'UT000040', '90499040', 'attn', NULL, NULL, 'Y', null, null, null, 200000040)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000037, 1, 200000040, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000040, 1)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000110, '1234 TEST-0029', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000095, 'OWNER_BUS', 'ACTIVE', 200000040, 200000040, null, null, null, 'TEST EXNR ACTIVE', 
           mhr_name_compressed_key('TEST EXNR ACTIVE'), 190000110, null, NULL, null, 200000037)
;
-- UT-0029 000928 non-residential MH registration
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000041, '000928', 'PS12345', 'EXEMPTION_NON_RES', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0029')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000111, '1234 TEST-0029', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000096, 'SUBMITTING', 'ACTIVE', 200000041, 200000041, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000111, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000041, 'EXNR', 200000041, 'UT000041', '90499041', 'attn', NULL, NULL, 'Y', null, null, null, 200000041)
;
INSERT INTO mhr_notes(id, document_type, registration_id, document_id, status_type, remarks, destroyed,
                      change_registration_id, expiry_date, effective_ts)
    VALUES(200000031, 'EXNR', 200000041, 200000041, 'ACTIVE', 'NON-RESIDENTIAL REMARKS', 'N', 200000041,
           null, now() at time zone 'UTC')
;
UPDATE mhr_registrations
   SET status_type = 'EXEMPT'
 WHERE id = 200000040
;
-- UT-0030 000929 COMMON registration 1 ADMINISTRATOR.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000042, '000929', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0030')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000112, '1234 TEST-0030', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000097, 'SUBMITTING', 'ACTIVE', 200000042, 200000042, 'DONNA', null, 'IVERSON', null,
           mhr_name_compressed_key('SUBMITTING'), 190000112, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000113, '1234 TEST-0030', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000042, 'MH_PARK', 'ACTIVE', 200000042, 200000042, 190000113,
           NULL, 'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', 'park name', '1234', NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000042, 'ACTIVE', 200000042, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000042)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000041, 200000042, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000042)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000042, 'REG_101', 200000042, 'UT000042', '90499042', 'attn', NULL, NULL, 'Y', null, null, null, 200000042)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000038, 1, 200000042, 'ACTIVE', 'NA', 'UNDIVIDED', 'Y', 1, 2, 200000042, 1)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000039, 2, 200000042, 'ACTIVE', 'COMMON', 'UNDIVIDED', 'Y', 1, 2, 200000042, 2)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000114, '1234 TEST-0030', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000115, '1234 TEST-0030', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id, description)
    VALUES(200000098, 'ADMINISTRATOR', 'ACTIVE', 200000042, 200000042, 'DENNIS', null, 'HALL', NULL, 
           mhr_name_compressed_key('HALL DENNIS'), 190000114, null, '6041234567', null, 200000038,
           'ADMINISTRATOR OF THE ESTATE OF BEVERLY JOY STROM, DECEASED')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id, description)
    VALUES(200000099, 'OWNER_IND', 'ACTIVE', 200000042, 200000042, 'SHARON', null, 'HALL', NULL, 
           mhr_name_compressed_key('HALL SHARON'), 190000115, null, '6041234567', null, 200000039,
           null)
;
-- UT-0031 000930 Registration with expired transport permit registration.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000043, '000930', 'PS12345', 'MHREG', (now() at time zone 'UTC') - interval '2 days', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0031')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000116, '1234 TEST-0031', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000100, 'SUBMITTING', 'ACTIVE', 200000043, 200000043, null, null, null, 'REAL ENGINEERED HOMES INC',
           mhr_name_compressed_key('REAL ENGINEERED HOMES INC'), 190000116, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000117, '1234 TEST-0031', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000043, 'MANUFACTURER', 'ACTIVE', 200000043, 200000043, 190000117,
           NULL, 'additional', 'REAL ENGINEERED HOMES INC', NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000043, 'ACTIVE', 200000043, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'REAL ENGINEERED HOMES INC', 'make', 'model', 'rebuilt', 'other', 200000043)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000042, 200000043, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000043)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000043, 'REG_101', 200000043, 'UT000043', '90499043', 'attn', NULL, NULL, 'Y', null, null, null, 200000043)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000040, 1, 200000043, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000043, 1)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000118, '1234 TEST-0031', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000101, 'OWNER_BUS', 'ACTIVE', 200000043, 200000043, null, null, null, 'TEST EXPIRED PERMIT', 
           mhr_name_compressed_key('TEST EXPIRED PERMIT'), 190000118, null, '6041234567', null, 200000040)
;
-- Expired transport permit registration
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000044, '000930', 'PS12345', 'PERMIT', (now() at time zone 'UTC') - interval '1 days', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0031')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000119, '1234 TEST-0031', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000102, 'SUBMITTING', 'ACTIVE', 200000044, 200000044, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000119, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000120, '1234 TEST-0031', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000044, 'MH_PARK', 'ACTIVE', 200000044, 200000044, 190000120,
           NULL, 'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', 'PARK NAME', '1234', NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000044, 'REG_103', 200000044, 'UT000044', '90499044', 'attn', NULL, NULL, 'Y', null, null, null, 200000044)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000121, '1234 TEST-0031', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000103, 'CONTACT', 'ACTIVE', 200000044, 200000044, null, null, null, 'PERSON GIVING NOTICE',
           mhr_name_compressed_key('PERSON GIVING NOTICE'), 190000121, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_notes(id, document_type, registration_id, document_id, status_type, remarks, destroyed,
                      change_registration_id, expiry_date, effective_ts)
    VALUES(200000032, 'REG_103', 200000044, 200000044, 'ACTIVE', null, 'N', 200000044,
           (now() at time zone 'UTC') - interval '1 days', now() at time zone 'UTC')
;
UPDATE mhr_locations
   SET status_type = 'HISTORICAL', change_registration_id = 200000044
 WHERE id = 200000043
;
-- UT-0032 000931 Non-manufacturer registration with active transport permit registration.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000045, '000931', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0032')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000122, '1234 TEST-0032', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000104, 'SUBMITTING', 'ACTIVE', 200000045, 200000045, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000122, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000123, '1234 TEST-0032', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000045, 'OTHER', 'ACTIVE', 200000045, 200000045, 190000123,
           NULL, 'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000045, 'ACTIVE', 200000045, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'REAL ENGINEERED HOMES INC', 'make', 'model', 'rebuilt', 'other', 200000045)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000043, 200000045, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000045)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000045, 'REG_101', 200000045, 'UT000045', '90499045', 'attn', NULL, NULL, 'Y', null, null, null, 200000045)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000041, 1, 200000045, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000045, 1)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000124, '1234 TEST-0032', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000105, 'OWNER_BUS', 'ACTIVE', 200000045, 200000045, null, null, null, 'TEST ACTIVE PERMIT', 
           mhr_name_compressed_key('TEST ACTIVE PERMIT'), 190000124, null, '6041234567', null, 200000041)
;
-- Active transport permit registration
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000046, '000931', 'PS12345', 'PERMIT', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0032')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000125, '1234 TEST-0032', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000106, 'SUBMITTING', 'ACTIVE', 200000046, 200000046, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000125, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000126, '1234 TEST-0032', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000046, 'OTHER', 'ACTIVE', 200000046, 200000046, 190000126,
           NULL, 'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000046, 'REG_103', 200000046, 'UT000046', '90499046', 'attn', NULL, NULL, 'Y', null, null, null, 200000046)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000127, '1234 TEST-0032', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000107, 'CONTACT', 'ACTIVE', 200000046, 200000046, null, null, null, 'PERSON GIVING NOTICE',
           mhr_name_compressed_key('PERSON GIVING NOTICE'), 190000127, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_notes(id, document_type, registration_id, document_id, status_type, remarks, destroyed,
                      change_registration_id, expiry_date, effective_ts)
    VALUES(200000033, 'REG_103', 200000046, 200000046, 'ACTIVE', null, 'N', 200000046,
           (now() at time zone 'UTC') + interval '30 days', now() at time zone 'UTC')
;
UPDATE mhr_locations
   SET status_type = 'HISTORICAL', change_registration_id = 200000046
 WHERE id = 200000045
;


