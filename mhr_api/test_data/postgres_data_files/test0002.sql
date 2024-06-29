-- UT serial number search begin PostgreSQL only
-- UT-0003
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000003, '000902', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0003')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000013, '1234 TEST-0003', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000010, 'SUBMITTING', 'ACTIVE', 200000003, 200000003, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000013, 'test@gmail.com', '6041234567', '123', null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000014, '1234 TEST-0003', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000003, 'STRATA', 'ACTIVE', 200000003, 200000003, 190000014,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437', 
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000003, 'ACTIVE', 200000003, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000003)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000003, 200000003, 'ACTIVE', mhr_serial_compressed_key('03A001644'), '03A001644', 60, 10, 14, 11,
           200000003)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000004, 200000003, 'ACTIVE', mhr_serial_compressed_key('WIN24440204003A'), 'WIN24440204003A', 60, 10, 14, 11,
           200000003)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000005, 200000003, 'ACTIVE', mhr_serial_compressed_key('WIN24440204003B'), 'WIN24440204003B', 60, 10, 14, 11,
           200000003)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000003, 'REG_101', 200000003, 'UT000003', '90499003', 'attn', NULL, NULL, 'Y', null, null, null, 200000003)
;

INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000004, 1, 200000003, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000003, 1)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000015, '1234 TEST-0003', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000011, 'OWNER_IND', 'ACTIVE', 200000003, 200000003, 'JOHN', NULL, 'RAMMOND', null, 
           mhr_name_compressed_key('RAMMOND JOHN'), 190000015, null, NULL, null, 200000004)
;
-- UT-0004
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000004, '000903', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0004')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000016, '1234 TEST-0004', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000012, 'SUBMITTING', 'ACTIVE', 200000004, 200000004, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000016, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000017, '1234 TEST-0004', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000004, 'STRATA', 'ACTIVE', 200000004, 200000004, 190000017,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437', 
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000004, 'ACTIVE', 200000004, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000004)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000006, 200000004, 'ACTIVE', mhr_serial_compressed_key('S60009493'), 'S60009493', 60, 10, 14, 11,
           200000004)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000007, 200000004, 'ACTIVE', mhr_serial_compressed_key('003000ZA002773B'), '003000ZA002773B', 60, 10, 14, 11,
           200000004)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000008, 200000004, 'ACTIVE', mhr_serial_compressed_key('PHH310OR1812828CRCM'), 'PHH310OR1812828CRCM', 60, 10, 14, 11,
           200000004)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000009, 200000004, 'ACTIVE', mhr_serial_compressed_key('681323'), '681323', 60, 10, 14, 11,
           200000004)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000004, 'REG_101', 200000004, 'UT000004', '90499004', 'attn', NULL, NULL, 'Y', null, null, null, 200000004)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000005, 1, 200000004, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000004, 1)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000018, '1234 TEST-0004', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000013, 'OWNER_IND', 'ACTIVE', 200000004, 200000004, 'JAMES', NULL, 'GALTRAM', null, 
           mhr_name_compressed_key('GALTRAM JAMES'), 190000018, null, NULL, null, 200000005)
;
-- UT-0005
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000005, '000904', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0005')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000019, '1234 TEST-0005', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000014, 'SUBMITTING', 'ACTIVE', 200000005, 200000005, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000019, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000020, '1234 TEST-0005', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000005, 'MANUFACTURER', 'ACTIVE', 200000005, 200000005, 190000020,
           NULL, 'additional', 'DEALER NAME HERE', NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000005, 'ACTIVE', 200000005, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000005)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000010, 200000005, 'ACTIVE', mhr_serial_compressed_key('9493'), '9493', 60, 10, 14, 11,
           200000005)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000011, 200000005, 'ACTIVE', mhr_serial_compressed_key('0310282AB'), '0310282AB', 60, 10, 14, 11,
           200000005)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000012, 200000005, 'ACTIVE', mhr_serial_compressed_key('A4820717A'), 'A4820717A', 60, 10, 14, 11,
           200000005)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000005, 'REG_101', 200000005, 'UT000005', '90499005', 'attn', NULL, NULL, 'Y', null, null, null, 200000005)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000006, 1, 200000005, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000005, 1)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000021, '1234 TEST-0005', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000015, 'OWNER_IND', 'ACTIVE', 200000005, 200000005, 'JENNY', NULL, 'GALTRESH', null, 
           mhr_name_compressed_key('GALTRESH JENNY'), 190000021, null, NULL, null, 200000006)
;
-- UT-0006
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000006, '000905', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0006')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000022, '1234 TEST-0006', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000016, 'SUBMITTING', 'ACTIVE', 200000006, 200000006, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000022, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000023, '1234 TEST-0006', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000006, 'OTHER', 'ACTIVE', 200000006, 200000006, 190000023,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437',
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000006, 'ACTIVE', 200000006, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000006)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000013, 200000006, 'ACTIVE', mhr_serial_compressed_key('681324'), '681324', 60, 10, 14, 11,
           200000006)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000014, 200000006, 'ACTIVE', mhr_serial_compressed_key('A4820717B'), 'A4820717B', 60, 10, 14, 11,
           200000006)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000006, 'REG_101', 200000006, 'UT000006', '90499006', 'attn', NULL, NULL, 'Y', null, null, null, 200000006)
;

INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000007, 1, 200000006, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000006, 1)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000024, '1234 TEST-0006', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000017, 'OWNER_IND', 'ACTIVE', 200000006, 200000006, 'MAX', NULL, 'KALTREX', null, 
           mhr_name_compressed_key('KALTREX MAX'), 190000024, null, NULL, null, 200000007)
;
-- UT serial number search end PostgreSQL only
