-- Transfer test registrations. 
-- UT-0018 000917 active TRANS_AFFIDAVIT FROZEN.
-- UT-0019 000918 QS FROZEN NCON unit note
-- UT-0020 000919 SOLE registration
-- UT-0021 000920 JOINT registration with middle names
-- UT-0022 000921 JOINT registration with no middle names
-- UT-0023 000922 SOLE ADMIN registration
-- UT-0024 000923 JOINT registration EXECUTOR party types.
-- UT-0025 000924 COMMON registration 1 EXECUTOR.
-- UT-0026 000925 COMMON registration 3 groups.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000026, '000917', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0018')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000066, '1234 TEST-0018', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000060, 'SUBMITTING', 'ACTIVE', 200000026, 200000026, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000066, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000067, '1234 TEST-0018', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000026, 'OTHER', 'ACTIVE', 200000026, 200000026, 190000067,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437',
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000026, 'ACTIVE', 200000026, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000026)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000029, 200000026, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000026)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000026, 'REG_101', 200000026, 'UT000026', '90499026', 'attn', NULL, NULL, 'Y', null, null, null, 200000026)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000022, 1, 200000026, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000026)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000068, '1234 TEST-0018', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000061, 'OWNER_IND', 'ACTIVE', 200000026, 200000026, 'JOAN', null, 'RAMMOND', null, 
           mhr_name_compressed_key('RAMMOND JOAN'), 190000068, null, NULL, null, 200000022)
;
-- UT-0018 000917 TRANS_AFFIDAVIT
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000027, '000917', 'PS12345', 'TRANS_AFFIDAVIT', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0018')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000069, '1234 TEST-0018', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000062, 'SUBMITTING', 'ACTIVE', 200000027, 200000027, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000069, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000027, 'AFFE', 200000027, 'UT000027', '90499027', 'attn', 1000, '$1000.00', 'Y', now() at time zone 'UTC', null, null, 200000027)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000023, 1, 200000027, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000027)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000070, '1234 TEST-0018', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id, description)
    VALUES(200000063, 'EXECUTOR', 'ACTIVE', 200000027, 200000027, 'JACKSON', null, 'EXECUTOR', null, 
           mhr_name_compressed_key('EXECUTOR JACKSON'), 190000070, null, NULL, null, 200000023,
           'EXECUTOR OF THE ESTATE OF JOAN RAMMOND')
;
UPDATE mhr_parties
   SET change_registration_id = 200000027, status_type = 'PREVIOUS'
 WHERE registration_id = 200000026
   AND party_type = 'OWNER_IND'
;
UPDATE mhr_owner_groups
   SET change_registration_id = 200000027, status_type = 'PREVIOUS'
 WHERE registration_id = 200000026
;
-- UT-0019 000918 QS FROZEN NCON registration
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000028, '000918', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0019')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000071, '1234 TEST-0019', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000064, 'SUBMITTING', 'ACTIVE', 200000028, 200000028, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000071, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000072, '1234 TEST-0019', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000028, 'OTHER', 'ACTIVE', 200000028, 200000028, 190000072,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437',
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000028, 'ACTIVE', 200000028, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000028)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000030, 200000028, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000028)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000028, 'REG_101', 200000028, 'UT000028', '90499028', 'attn', NULL, NULL, 'Y', null, null, null, 200000028)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000024, 1, 200000028, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000028)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000073, '1234 TEST-0019', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000065, 'OWNER_BUS', 'ACTIVE', 200000028, 200000028, null, null, null, 'TEST NOTE ACTIVE NCON', 
           mhr_name_compressed_key('TEST NOTE ACTIVE NCON'), 190000073, null, NULL, null, 200000024)
;
-- UT-0019 000918 QS FROZEN NCON unit note
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000029, '000918', 'PS12345', 'REG_STAFF_ADMIN', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0019')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000074, '1234 TEST-0019', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000066, 'SUBMITTING', 'ACTIVE', 200000029, 200000029, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000074, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000067, 'CONTACT', 'ACTIVE', 200000029, 200000029, null, null, null, 'PERSON GIVING NOTICE',
           mhr_name_compressed_key('PERSON GIVING NOTICE'), 190000065, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000029, 'NCON', 200000029, 'UT000029', '90499029', 'attn', NULL, NULL, 'Y', null, null, null, 200000029)
;
INSERT INTO mhr_notes(id, document_type, registration_id, document_id, status_type, remarks, destroyed,
                      change_registration_id, expiry_date, effective_ts)
    VALUES(200000029, 'NCON', 200000029, 200000029, 'ACTIVE', 'unit test remarks', 'N', 200000029,
           null, now() at time zone 'UTC')
;
-- UT-0020 000919 SOLE registration
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000030, '000919', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0020')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000075, '1234 TEST-0020', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000068, 'SUBMITTING', 'ACTIVE', 200000030, 200000030, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000075, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000076, '1234 TEST-0020', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000030, 'MH_PARK', 'ACTIVE', 200000030, 200000030, 190000076,
           NULL, 'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', 'park name', '1234', NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000030, 'ACTIVE', 200000030, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000030)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000031, 200000030, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000030)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000030, 'REG_101', 200000030, 'UT000030', '90499030', 'attn', NULL, NULL, 'Y', null, null, null, 200000030)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000025, 1, 200000030, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000030)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000077, '1234 TEST-0020', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000069, 'OWNER_IND', 'ACTIVE', 200000030, 200000030, 'JANE', null, 'SMITH', NULL, 
           mhr_name_compressed_key('SMITH JANE'), 190000077, null, NULL, null, 200000025)
;
-- UT-0021 000920 JOINT registration with middle names
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000031, '000920', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0021')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000078, '1234 TEST-0021', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000070, 'SUBMITTING', 'ACTIVE', 200000031, 200000031, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000078, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000079, '1234 TEST-0021', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000031, 'MH_PARK', 'ACTIVE', 200000031, 200000031, 190000079,
           NULL, 'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', 'park name', '1234', NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000031, 'ACTIVE', 200000031, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000031)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000032, 200000031, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000031)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000031, 'REG_101', 200000031, 'UT000031', '90499031', 'attn', NULL, NULL, 'Y', null, null, null, 200000031)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000026, 1, 200000031, 'ACTIVE', 'JOINT', NULL, 'Y', NULL, NULL, 200000031)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000080, '1234 TEST-0021', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000071, 'OWNER_IND', 'ACTIVE', 200000031, 200000031, 'ROBERT', 'JOHN', 'MOWAT', NULL, 
           mhr_name_compressed_key('MOWAT ROBERT JOHN'), 190000080, null, '6041234567', null, 200000026)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000072, 'OWNER_IND', 'ACTIVE', 200000031, 200000031, 'KAREN', 'PATRICIA', 'MOWAT', NULL, 
           mhr_name_compressed_key('MOWAT KAREN PATRICIA'), 190000080, null, '6041234567', null, 200000026)
;
-- UT-0022 000921 JOINT registration with no middle names
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000032, '000921', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0022')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000081, '1234 TEST-0022', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000073, 'SUBMITTING', 'ACTIVE', 200000032, 200000032, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000081, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000082, '1234 TEST-0022', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000032, 'MH_PARK', 'ACTIVE', 200000032, 200000032, 190000082,
           NULL, 'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', 'park name', '1234', NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000032, 'ACTIVE', 200000032, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000032)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000033, 200000032, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000032)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000032, 'REG_101', 200000032, 'UT000032', '90499032', 'attn', NULL, NULL, 'Y', null, null, null, 200000032)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000027, 1, 200000032, 'ACTIVE', 'JOINT', NULL, 'Y', NULL, NULL, 200000032)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000083, '1234 TEST-0022', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000074, 'OWNER_IND', 'ACTIVE', 200000032, 200000032, 'DENNIS', NULL, 'HALL', NULL, 
           mhr_name_compressed_key('HALL DENNIS'), 190000083, null, '6041234567', null, 200000027)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000075, 'OWNER_IND', 'ACTIVE', 200000032, 200000032, 'SHARON', NULL, 'HALL', NULL, 
           mhr_name_compressed_key('HALL SHARON'), 190000083, null, '6041234567', null, 200000027)
;
-- UT-0023 000922 SOLE ADMIN registration
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000033, '000922', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0023')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000084, '1234 TEST-0023', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000076, 'SUBMITTING', 'ACTIVE', 200000033, 200000033, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000084, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000085, '1234 TEST-0023', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000033, 'MH_PARK', 'ACTIVE', 200000033, 200000033, 190000085,
           NULL, 'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', 'park name', '1234', NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000033, 'ACTIVE', 200000033, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000033)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000034, 200000033, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000033)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000033, 'REG_101', 200000033, 'UT000033', '90499033', 'attn', NULL, NULL, 'Y', null, null, null, 200000033)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000028, 1, 200000033, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000033)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000086, '1234 TEST-0023', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id, description)
    VALUES(200000077, 'ADMINISTRATOR', 'ACTIVE', 200000033, 200000033, 'JOHN', 'TALBOT', 'KIDDER', NULL, 
           mhr_name_compressed_key('KIDDER JOHN TALBOT'), 190000086, null, '6041234567', null, 200000028,
           'ADMINISTRATOR OF THE ESTATE OF BEVERLY JOY STROM, DECEASED')
;
-- UT-0024 000923 JOINT registration EXECUTOR party types.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000034, '000923', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0024')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000087, '1234 TEST-0024', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000078, 'SUBMITTING', 'ACTIVE', 200000034, 200000034, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000087, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000088, '1234 TEST-0024', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000034, 'MH_PARK', 'ACTIVE', 200000034, 200000034, 190000088,
           NULL, 'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', 'park name', '1234', NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000034, 'ACTIVE', 200000034, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000034)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000035, 200000034, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000034)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000034, 'REG_101', 200000034, 'UT000034', '90499034', 'attn', NULL, NULL, 'Y', null, null, null, 200000034)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000029, 1, 200000034, 'ACTIVE', 'JOINT', NULL, 'Y', NULL, NULL, 200000034)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000089, '1234 TEST-0024', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id, description)
    VALUES(200000079, 'EXECUTOR', 'ACTIVE', 200000034, 200000034, 'DENNIS', null, 'HALL', NULL, 
           mhr_name_compressed_key('HALL DENNIS'), 190000089, null, '6041234567', null, 200000029,
           'EXECUTOR OF THE ESTATE OF BEVERLY JOY STROM, DECEASED')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id, description)
    VALUES(200000080, 'EXECUTOR', 'ACTIVE', 200000034, 200000034, 'SHARON', null, 'HALL', NULL, 
           mhr_name_compressed_key('HALL SHARON'), 190000089, null, '6041234567', null, 200000029,
           'EXECUTOR OF THE ESTATE OF BEVERLY JOY STROM, DECEASED')
;
-- UT-0025 000924 COMMON registration 1 EXECUTOR.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000035, '000924', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0025')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000090, '1234 TEST-0025', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000081, 'SUBMITTING', 'ACTIVE', 200000035, 200000035, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000090, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000091, '1234 TEST-0025', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000035, 'MH_PARK', 'ACTIVE', 200000035, 200000035, 190000091,
           NULL, 'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', 'park name', '1234', NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000035, 'ACTIVE', 200000035, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000035)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000036, 200000035, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000035)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000035, 'REG_101', 200000035, 'UT000035', '90499035', 'attn', NULL, NULL, 'Y', null, null, null, 200000035)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000030, 1, 200000035, 'ACTIVE', 'NA', 'UNDIVIDED', 'Y', 1, 2, 200000035)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000031, 2, 200000035, 'ACTIVE', 'COMMON', 'UNDIVIDED', 'Y', 1, 2, 200000035)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000092, '1234 TEST-0025', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000093, '1234 TEST-0025', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id, description)
    VALUES(200000082, 'EXECUTOR', 'ACTIVE', 200000035, 200000035, 'DENNIS', null, 'HALL', NULL, 
           mhr_name_compressed_key('HALL DENNIS'), 190000092, null, '6041234567', null, 200000030,
           'EXECUTOR OF THE ESTATE OF BEVERLY JOY STROM, DECEASED')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id, description)
    VALUES(200000083, 'OWNER_IND', 'ACTIVE', 200000035, 200000035, 'SHARON', null, 'HALL', NULL, 
           mhr_name_compressed_key('HALL SHARON'), 190000093, null, '6041234567', null, 200000031,
           null)
;
-- UT-0026 000925 COMMON registration 3 groups.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000036, '000925', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0026')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000094, '1234 TEST-0026', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000084, 'SUBMITTING', 'ACTIVE', 200000036, 200000036, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000094, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000095, '1234 TEST-0026', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000036, 'MH_PARK', 'ACTIVE', 200000036, 200000036, 190000095,
           NULL, 'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', 'park name', '1234', NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000036, 'ACTIVE', 200000036, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000036)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000037, 200000036, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000036)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000036, 'REG_101', 200000036, 'UT000036', '90499036', 'attn', NULL, NULL, 'Y', null, null, null, 200000036)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000032, 1, 200000036, 'ACTIVE', 'COMMON', 'UNDIVIDED', 'Y', 1, 3, 200000036)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000033, 2, 200000036, 'ACTIVE', 'COMMON', 'UNDIVIDED', 'Y', 1, 3, 200000036)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000034, 3, 200000036, 'ACTIVE', 'COMMON', 'UNDIVIDED', 'Y', 1, 3, 200000036)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000096, '1234 TEST-0026', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000097, '1234 TEST-0026', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000098, '1234 TEST-0026', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id, description)
    VALUES(200000085, 'OWNER_IND', 'ACTIVE', 200000036, 200000036, 'DENNIS', null, 'HALL', NULL, 
           mhr_name_compressed_key('HALL DENNIS'), 190000096, null, '6041234567', null, 200000032, null)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id, description)
    VALUES(200000086, 'OWNER_IND', 'ACTIVE', 200000036, 200000036, 'SHARON', null, 'HALL', NULL, 
           mhr_name_compressed_key('HALL SHARON'), 190000097, null, '6041234567', null, 200000033,
           null)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id, description)
    VALUES(200000087, 'OWNER_IND', 'ACTIVE', 200000036, 200000036, 'SHELLEY', null, 'HALL', NULL, 
           mhr_name_compressed_key('HALL SHELLEY'), 190000098, null, '6041234567', null, 200000034,
           null)
;
