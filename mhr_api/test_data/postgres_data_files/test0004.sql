-- UT-0012 000911 manufacturer batch email. 
-- UT-0013 000912 MHREG EXEMPT.
-- UT-0014 000913 MHREG CANCELLED.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000016, '000911', 'PS12345', 'MHREG', 
             (TO_TIMESTAMP('2023-05-25 14:00:00', 'YYYY-MM-DD HH24:MI:SS') at time zone 'utc'),
             'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0012')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000044, '1234 TEST-0012', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000040, 'SUBMITTING', 'ACTIVE', 200000016, 200000016, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000044, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000045, '1234 TEST-0012', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000016, 'OTHER', 'ACTIVE', 200000016, 200000016, 190000045,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437',
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000016, 'ACTIVE', 200000016, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000016)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000023, 200000016, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000016)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000016, 'REG_101', 200000016, 'UT000016', '90499016', 'attn', NULL, NULL, 'Y', null, null, null, 200000016)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000016, 1, 200000016, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000016)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000046, '1234 TEST-0012', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000041, 'OWNER_BUS', 'ACTIVE', 200000016, 200000016, null, null, null, 'TEST MAN BATCH EMAIL', 
           mhr_name_compressed_key('TEST MAN BATCH EMAIL'), 190000046, null, NULL, null, 200000016)
;
INSERT INTO mhr_registration_reports (id, create_ts, report_data, registration_id, report_type, doc_storage_url, batch_storage_url)
   VALUES (200000016, (TO_TIMESTAMP('2023-05-25 14:00:00', 'YYYY-MM-DD HH24:MI:SS') at time zone 'utc'),
'{"mhrNumber": "000911", "createDateTime": "2023-05-25T18:43:36+00:00", "registrationType": "MHREG", "status": "ACTIVE", "declaredValue": 0, "documentDescription": "MANUFACTURED HOME REGISTRATION", "documentId": "103272", "documentRegistrationNumber": "00503029", "ownLand": true, "clientReferenceId": "UT-MHREG-MAN", "attentionReference": "JENNIFER SMITH", "submittingParty": {"businessName": "REAL ENGINEERED HOMES INC", "address": {"street": "1704 GOVERNMENT ST.", "city": "PENTICTON", "region": "BC", "country": "CA", "postalCode": "V2A 7A1"}, "phoneNumber": "2507701067"}, "location": {"locationId": 289, "status": "ACTIVE", "locationType": "MANUFACTURER", "address": {"street": "1704 GOVERNMENT ST.", "city": "PENTICTON", "region": "BC", "country": "CA", "postalCode": "V2A 7A1"}, "leaveProvince": false, "taxCertificate": false, "dealerName": "REAL ENGINEERED HOMES INC"}, "description": {"status": "ACTIVE", "sectionCount": 1, "baseInformation": {"make": "WATSON IND. (ALTA)", "model": "DUCHESS", "circa": false, "year": 2024}, "csaNumber": "786356", "csaStandard": "Z240", "manufacturer": "REAL ENGINEERED HOMES INC", "sections": [{"serialNumber": "73737", "lengthFeet": 60, "widthFeet": 12}]}, "ownerGroups": [{"groupId": 1, "type": "SOLE", "status": "ACTIVE", "tenancySpecified": true, "owners": [{"ownerId": 1455, "status": "ACTIVE", "partyType": "OWNER_BUS", "organizationName": "REAL ENGINEERED HOMES INC", "address": {"street": "1704 GOVERNMENT ST.", "city": "PENTICTON", "region": "BC", "country": "CA", "postalCode": "V2A 7A1"}, "type": "SOLE"}]}], "payment": {"invoiceId": "28610", "receipt": "/api/v1/payment-requests/28610/receipts"}, "usergroup": "mhr_manufacturer"}',
           200000016, 'mhrRegistration', null, null)
;
-- UT-0013 000912 MHREG EXEMPT.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000017, '000912', 'PS12345', 'MHREG', now() at time zone 'UTC', 'EXEMPT', 200000001, null, null, 'TESTUSER', 'UT-0013')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000047, '1234 TEST-0013', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000042, 'SUBMITTING', 'ACTIVE', 200000017, 200000017, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000047, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000048, '1234 TEST-0013', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000017, 'OTHER', 'ACTIVE', 200000017, 200000017, 190000048,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437',
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000017, 'ACTIVE', 200000017, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000017)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000024, 200000017, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000017)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000017, 'REG_101', 200000017, 'UT000017', '90499017', 'attn', NULL, NULL, 'Y', null, null, null, 200000017)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000017, 1, 200000017, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000017)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000049, '1234 TEST-0013', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000043, 'OWNER_BUS', 'ACTIVE', 200000017, 200000017, null, null, null, 'TEST MHREG EXEMPT', 
           mhr_name_compressed_key('TEST MHREG EXEMPT'), 190000049, null, NULL, null, 200000017)
;
-- UT-0014 000913 MHREG CANCELLED.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000018, '000913', 'PS12345', 'MHREG', now() at time zone 'UTC', 'CANCELLED', 200000001, null, null, 'TESTUSER', 'UT-0014')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000050, '1234 TEST-0014', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000044, 'SUBMITTING', 'ACTIVE', 200000018, 200000018, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000050, 'test@gmail.com', '6041234567', null, null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000051, '1234 TEST-0014', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000018, 'OTHER', 'ACTIVE', 200000018, 200000018, 190000051,
           'LOT 24 DISTRICT LOT 497 KAMLOOPS DIVISION YALE DISTRICT PLAN 25437',
           'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', NULL, NULL, '005509807', NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000018, 'ACTIVE', 200000018, '7777700000', '1234', 3, NULL, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000018)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000025, 200000018, 'ACTIVE', mhr_serial_compressed_key('888888'), '888888', 60, 10, 14, 11,
           200000018)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000018, 'REG_101', 200000018, 'UT000018', '90499018', 'attn', NULL, NULL, 'Y', null, null, null, 200000018)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id)
    VALUES(200000018, 1, 200000018, 'ACTIVE', 'SOLE', NULL, 'Y', NULL, NULL, 200000018)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000052, '1234 TEST-0014', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000045, 'OWNER_BUS', 'ACTIVE', 200000018, 200000018, null, null, null, 'TEST MHREG CANCELLED', 
           mhr_name_compressed_key('TEST MHREG CANCELLED'), 190000052, null, NULL, null, 200000018)
;
