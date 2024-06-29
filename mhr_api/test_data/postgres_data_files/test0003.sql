-- UT search results active/historical counts, notes with cancellations
-- UT-0007 000906 org name collapse
-- UT-0008 000907 individual name collapse
-- UT-0009 000908 serial number collapse
-- UT-0010 000909 search results registration with caution unit note and cancel unit note. 
-- UT-0011 000910 search results registration with TAXN unit note and cancel unit note. 
-- UT-0007 000906 org name collapse
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000007, '000906', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0007')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000025, '1234 TEST-0007', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000018, 'SUBMITTING', 'ACTIVE', 200000007, 200000007, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000025, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000026, '1234 TEST-0007', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000007, 'OTHER', 'ACTIVE', 200000007, 200000007, 190000026,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437',
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000007, 'ACTIVE', 200000007, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000007)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000015, 200000007, 'ACTIVE', mhr_serial_compressed_key('998765'), '998765', 60, 10, 14, 11,
           200000007)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000007, 'REG_101', 200000007, 'UT000007', '90499007', 'attn', NULL, NULL, 'Y', null, null, null, 200000007)
;

INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000008, 1, 200000007, 'PREVIOUS', 'JOINT', NULL, 'Y', NULL, NULL, 200000007, 1)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000027, '1234 TEST-0007', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000019, 'OWNER_BUS', 'PREVIOUS', 200000007, 200000007, NULL, NULL, NULL, 'TEST ONLY SERAPHIC HOMES', 
           mhr_name_compressed_key('TEST ONLY SERAPHIC HOMES'), 190000027, null, NULL, null, 200000008)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000020, 'OWNER_BUS', 'PREVIOUS', 200000007, 200000007, NULL, NULL, NULL, 'TEST ONLY SERAPHIC HOMES', 
           mhr_name_compressed_key('TEST ONLY SERAPHIC HOMES'), 190000027, null, NULL, null, 200000008)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000009, 1, 200000007, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000007, 1)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000021, 'OWNER_BUS', 'ACTIVE', 200000007, 200000007, NULL, NULL, NULL, 'TEST ONLY SERAPHIC HOMES', 
           mhr_name_compressed_key('TEST ONLY SERAPHIC HOMES'), 190000027, null, NULL, null, 200000009)
;
-- UT-0008 Individual name collapse
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000008, '000907', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0008')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000028, '1234 TEST-0008', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000022, 'SUBMITTING', 'ACTIVE', 200000008, 200000008, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000028, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000029, '1234 TEST-0008', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000008, 'OTHER', 'ACTIVE', 200000008, 200000008, 190000029,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437',
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000008, 'ACTIVE', 200000008, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000008)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000016, 200000008, 'ACTIVE', mhr_serial_compressed_key('998765'), '998765', 60, 10, 14, 11,
           200000008)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000008, 'REG_101', 200000008, 'UT000008', '90499008', 'attn', NULL, NULL, 'Y', null, null, null, 200000008)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000010, 1, 200000008, 'PREVIOUS', 'SOLE', NULL, 'Y', NULL, NULL, 200000008, 1)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000030, '1234 TEST-0008', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000023, 'OWNER_IND', 'PREVIOUS', 200000008, 200000008, 'GAYLEX', NULL, 'ZAXOD', NULL, 
           mhr_name_compressed_key('ZAXOD GAYLEX'), 190000030, null, NULL, null, 200000010)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000011, 1, 200000008, 'EXEMPT', 'SOLE', NULL, 'Y', NULL, NULL, 200000008, 1)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000024, 'OWNER_IND', 'EXEMPT', 200000008, 200000008, 'GAYLEX', NULL, 'ZAXOD', NULL, 
           mhr_name_compressed_key('ZAXOD GAYLEX'), 190000030, null, NULL, null, 200000011)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000012, 1, 200000008, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000008, 1)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000025, 'OWNER_IND', 'ACTIVE', 200000008, 200000008, 'GAYLEX', null, 'ZAXOD', NULL, 
           mhr_name_compressed_key('ZAXOD GAYLEX'), 190000030, null, NULL, null, 200000012)
;
-- UT-0009 serial number collapse
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000009, '000908', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0009')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000031, '1234 TEST-0009', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000026, 'SUBMITTING', 'ACTIVE', 200000009, 200000009, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000031, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000032, '1234 TEST-0009', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000009, 'OTHER', 'ACTIVE', 200000009, 200000009, 190000032,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437',
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000009, 'ACTIVE', 200000009, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000009)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000017, 200000009, 'HISTORICAL', mhr_serial_compressed_key('000060'), '000060', 60, 10, 14, 11,
           200000009)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000018, 200000009, 'ACTIVE', mhr_serial_compressed_key('000060'), '000060', 60, 10, 14, 11,
           200000009)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000019, 200000009, 'ACTIVE', mhr_serial_compressed_key('000060'), '000060', 60, 10, 14, 11,
           200000009)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000020, 200000009, 'ACTIVE', mhr_serial_compressed_key('000060'), '000060', 60, 10, 14, 11,
           200000009)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000009, 'REG_101', 200000009, 'UT000009', '90499009', 'attn', NULL, NULL, 'Y', null, null, null, 200000009)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000013, 1, 200000009, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000009, 1)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000033, '1234 TEST-0009', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000027, 'OWNER_BUS', 'ACTIVE', 200000009, 200000009, null, null, null, 'TEST SERIAL NINE', 
           mhr_name_compressed_key('TEST SERIAL NINE'), 190000033, null, NULL, null, 200000013)
;
-- UT-0010 search results registration with caution unit note and cancel unit note. 
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000010, '000909', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0010')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000034, '1234 TEST-0010', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000028, 'SUBMITTING', 'ACTIVE', 200000010, 200000010, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000034, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000035, '1234 TEST-0010', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000010, 'OTHER', 'ACTIVE', 200000010, 200000010, 190000035,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437',
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000010, 'ACTIVE', 200000010, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000010)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000021, 200000010, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000010)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000010, 'REG_101', 200000010, 'UT000010', '90499010', 'attn', NULL, NULL, 'Y', null, null, null, 200000010)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000014, 1, 200000010, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000010, 1)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000036, '1234 TEST-0010', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000029, 'OWNER_BUS', 'ACTIVE', 200000010, 200000010, null, null, null, 'TEST NOTE CAU CANCEL', 
           mhr_name_compressed_key('TEST NOTE CAU CANCEL'), 190000036, null, NULL, null, 200000014)
;
-- UT-0010 CAU unit note 
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000011, '000909', 'PS12345', 'REG_STAFF_ADMIN', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0010')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000037, '1234 TEST-0010', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000030, 'SUBMITTING', 'ACTIVE', 200000011, 200000011, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000037, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000031, 'CONTACT', 'ACTIVE', 200000011, 200000011, null, null, null, 'PERSON GIVING NOTICE',
           mhr_name_compressed_key('PERSON GIVING NOTICE'), 190000037, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000011, 'CAU', 200000011, 'UT000011', '90499011', 'attn', NULL, NULL, 'Y', null, null, null, 200000011)
;
INSERT INTO mhr_notes(id, document_type, registration_id, document_id, status_type, remarks, destroyed,
                      change_registration_id, expiry_date, effective_ts)
    VALUES(200000011, 'CAU', 200000011, 200000011, 'ACTIVE', 'unit test remarks', 'N', 200000011,
           now() at time zone 'UTC' + interval '90 days', now() at time zone 'UTC')
;
-- UT-0010 NCAN unit note 
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000012, '000909', 'PS12345', 'REG_STAFF_ADMIN', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0010')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000038, '1234 TEST-0010', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000032, 'SUBMITTING', 'ACTIVE', 200000012, 200000012, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000038, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000033, 'CONTACT', 'ACTIVE', 200000012, 200000012, null, null, null, 'PERSON GIVING NOTICE',
           mhr_name_compressed_key('PERSON GIVING NOTICE'), 190000038, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000012, 'NCAN', 200000012, 'UT000012', '90499012', 'attn', NULL, NULL, 'Y', null, null, null, 200000012)
;
INSERT INTO mhr_notes(id, document_type, registration_id, document_id, status_type, remarks, destroyed,
                      change_registration_id, expiry_date, effective_ts)
    VALUES(200000012, 'NCAN', 200000012, 200000012, 'ACTIVE', 'unit test remarks', 'N', 200000012,
           null, now() at time zone 'UTC')
;
UPDATE mhr_notes
   SET status_type = 'CANCELLED', change_registration_id = 200000012
WHERE registration_id = 200000011
;
-- UT-0011 search results registration with TAXN unit note and cancel unit note. 
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000013, '000910', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0011')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000039, '1234 TEST-0011', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000034, 'SUBMITTING', 'ACTIVE', 200000013, 200000013, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000039, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000040, '1234 TEST-0011', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000013, 'OTHER', 'ACTIVE', 200000013, 200000013, 190000040,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437',
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000013, 'ACTIVE', 200000013, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000013)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000022, 200000013, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000013)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000013, 'REG_101', 200000013, 'UT000013', '90499013', 'attn', NULL, NULL, 'Y', null, null, null, 200000013)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000015, 1, 200000013, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000013, 1)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000041, '1234 TEST-0011', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000035, 'OWNER_BUS', 'ACTIVE', 200000013, 200000013, null, null, null, 'TEST NOTE TAXN CANCEL', 
           mhr_name_compressed_key('TEST NOTE TAXN CANCEL'), 190000041, null, NULL, null, 200000015)
;
-- UT-0011 TAXN unit note 
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000014, '000910', 'PS12345', 'REG_STAFF_ADMIN', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0011')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000042, '1234 TEST-0011', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000036, 'SUBMITTING', 'ACTIVE', 200000014, 200000014, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000042, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000037, 'CONTACT', 'ACTIVE', 200000014, 200000014, null, null, null, 'PERSON GIVING NOTICE',
           mhr_name_compressed_key('PERSON GIVING NOTICE'), 190000042, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000014, 'TAXN', 200000014, 'UT000014', '90499014', 'attn', NULL, NULL, 'Y', null, null, null, 200000014)
;
INSERT INTO mhr_notes(id, document_type, registration_id, document_id, status_type, remarks, destroyed,
                      change_registration_id, expiry_date, effective_ts)
    VALUES(200000014, 'TAXN', 200000014, 200000014, 'ACTIVE', 'unit test remarks', 'N', 200000014,
           null, now() at time zone 'UTC')
;
-- UT-0011 NRED unit note 
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000015, '000910', 'PS12345', 'REG_STAFF_ADMIN', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0011')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000043, '1234 TEST-0011', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000038, 'SUBMITTING', 'ACTIVE', 200000015, 200000015, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000043, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000039, 'CONTACT', 'ACTIVE', 200000015, 200000015, null, null, null, 'PERSON GIVING NOTICE',
           mhr_name_compressed_key('PERSON GIVING NOTICE'), 190000043, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000015, 'NRED', 200000015, 'UT000015', '90499015', 'attn', NULL, NULL, 'Y', null, null, null, 200000015)
;
INSERT INTO mhr_notes(id, document_type, registration_id, document_id, status_type, remarks, destroyed,
                      change_registration_id, expiry_date, effective_ts)
    VALUES(200000015, 'NRED', 200000015, 200000015, 'ACTIVE', 'unit test remarks', 'N', 200000015,
           null, now() at time zone 'UTC')
;
UPDATE mhr_notes
   SET status_type = 'CANCELLED', change_registration_id = 200000015
WHERE registration_id = 200000014
;

