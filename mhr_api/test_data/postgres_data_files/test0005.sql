-- Unit note test registrations. 
-- UT-0015 000914 active TAXN.
-- UT-0016 000915 active REST.
-- UT-0013 000912 active EXRS unit note.
-- UT-0017 000916 active CAU.

-- UT-0015 000914 active TAXN.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000019, '000914', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0015')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000053, '1234 TEST-0015', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000046, 'SUBMITTING', 'ACTIVE', 200000019, 200000019, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000053, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000054, '1234 TEST-0015', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000019, 'OTHER', 'ACTIVE', 200000019, 200000019, 190000054,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437',
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000019, 'ACTIVE', 200000019, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000019)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000026, 200000019, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000019)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000019, 'REG_101', 200000019, 'UT000019', '90499019', 'attn', NULL, NULL, 'Y', null, null, null, 200000019)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000019, 1, 200000019, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000019)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000055, '1234 TEST-0015', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000047, 'OWNER_BUS', 'ACTIVE', 200000019, 200000019, null, null, null, 'TEST NOTE ACTIVE TAXN', 
           mhr_name_compressed_key('TEST NOTE ACTIVE TAXN'), 190000055, null, NULL, null, 200000019)
;
-- UT-0015 TAXN unit note 
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000020, '000914', 'PS12345', 'REG_STAFF_ADMIN', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0015')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000056, '1234 TEST-0015', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000048, 'SUBMITTING', 'ACTIVE', 200000020, 200000020, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000056, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000049, 'CONTACT', 'ACTIVE', 200000020, 200000020, null, null, null, 'PERSON GIVING NOTICE',
           mhr_name_compressed_key('PERSON GIVING NOTICE'), 190000056, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000020, 'TAXN', 200000020, 'UT000020', '90499020', 'attn', NULL, NULL, 'Y', null, null, null, 200000020)
;
INSERT INTO mhr_notes(id, document_type, registration_id, document_id, status_type, remarks, destroyed,
                      change_registration_id, expiry_date, effective_ts)
    VALUES(200000020, 'TAXN', 200000020, 200000020, 'ACTIVE', 'unit test remarks', 'N', 200000020,
           null, now() at time zone 'UTC')
;
-- UT-0016 000915 active REST.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000021, '000915', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0016')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000057, '1234 TEST-0016', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000050, 'SUBMITTING', 'ACTIVE', 200000021, 200000021, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000057, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000058, '1234 TEST-0016', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000021, 'OTHER', 'ACTIVE', 200000021, 200000021, 190000058,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437',
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000021, 'ACTIVE', 200000021, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000021)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000027, 200000021, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000021)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000021, 'REG_101', 200000021, 'UT000021', '90499021', 'attn', NULL, NULL, 'Y', null, null, null, 200000021)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000020, 1, 200000021, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000021)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000059, '1234 TEST-0016', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000051, 'OWNER_BUS', 'ACTIVE', 200000021, 200000021, null, null, null, 'TEST NOTE ACTIVE REST', 
           mhr_name_compressed_key('TEST NOTE ACTIVE REST'), 190000059, null, NULL, null, 200000020)
;
-- UT-0016 REST unit note 
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000022, '000915', 'PS12345', 'REG_STAFF_ADMIN', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0016')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000060, '1234 TEST-0016', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000052, 'SUBMITTING', 'ACTIVE', 200000022, 200000022, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000060, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000053, 'CONTACT', 'ACTIVE', 200000022, 200000022, null, null, null, 'PERSON GIVING NOTICE',
           mhr_name_compressed_key('PERSON GIVING NOTICE'), 190000060, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000022, 'REST', 200000022, 'UT000022', '90499022', 'attn', NULL, NULL, 'Y', null, null, null, 200000022)
;
INSERT INTO mhr_notes(id, document_type, registration_id, document_id, status_type, remarks, destroyed,
                      change_registration_id, expiry_date, effective_ts)
    VALUES(200000022, 'REST', 200000022, 200000022, 'ACTIVE', 'unit test remarks', 'N', 200000022,
           null, now() at time zone 'UTC')
;
-- UT-0013 EXRS unit note 
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000023, '000912', 'PS12345', 'REG_STAFF_ADMIN', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0013')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000061, '1234 TEST-0013', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000054, 'SUBMITTING', 'ACTIVE', 200000023, 200000023, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000061, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000055, 'CONTACT', 'ACTIVE', 200000023, 200000023, null, null, null, 'PERSON GIVING NOTICE',
           mhr_name_compressed_key('PERSON GIVING NOTICE'), 190000061, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000023, 'EXRS', 200000023, 'UT000023', '90499023', 'attn', NULL, NULL, 'Y', null, null, null, 200000023)
;
INSERT INTO mhr_notes(id, document_type, registration_id, document_id, status_type, remarks, destroyed,
                      change_registration_id, expiry_date, effective_ts)
    VALUES(200000023, 'EXRS', 200000023, 200000023, 'ACTIVE', 'unit test remarks', 'N', 200000023,
           null, now() at time zone 'UTC')
;
-- UT-0017 000916 active CAU registration.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000024, '000916', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0017')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000062, '1234 TEST-0017', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000056, 'SUBMITTING', 'ACTIVE', 200000024, 200000024, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000062, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000063, '1234 TEST-0017', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000024, 'OTHER', 'ACTIVE', 200000024, 200000024, 190000063,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437',
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000024, 'ACTIVE', 200000024, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000024)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000028, 200000024, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000024)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000024, 'REG_101', 200000024, 'UT000024', '90499024', 'attn', NULL, NULL, 'Y', null, null, null, 200000024)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000021, 1, 200000024, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000024)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000064, '1234 TEST-0017', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000057, 'OWNER_BUS', 'ACTIVE', 200000024, 200000024, null, null, null, 'TEST NOTE ACTIVE CAU', 
           mhr_name_compressed_key('TEST NOTE ACTIVE CAU'), 190000064, null, NULL, null, 200000021)
;
-- UT-0017 000916 active CAU unit note.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000025, '000916', 'PS12345', 'REG_STAFF_ADMIN', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0017')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000065, '1234 TEST-0017', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000058, 'SUBMITTING', 'ACTIVE', 200000025, 200000025, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000065, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000059, 'CONTACT', 'ACTIVE', 200000025, 200000025, null, null, null, 'PERSON GIVING NOTICE',
           mhr_name_compressed_key('PERSON GIVING NOTICE'), 190000065, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000025, 'CAU', 200000025, 'UT000025', '90499025', 'attn', NULL, NULL, 'Y', null, null, null, 200000025)
;
INSERT INTO mhr_notes(id, document_type, registration_id, document_id, status_type, remarks, destroyed,
                      change_registration_id, expiry_date, effective_ts)
    VALUES(200000025, 'CAU', 200000025, 200000025, 'ACTIVE', 'unit test remarks', 'N', 200000025,
           (now() at time zone 'UTC' + interval '89 days'), now() at time zone 'UTC')
;
