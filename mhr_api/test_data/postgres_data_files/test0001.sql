-- MAN 1
INSERT INTO mhr_registrations(id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id)
     VALUES (200000000, 'UTMAN1', 'SYSTEM', 'MANUFACTURER', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'SYSTEM')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000000, '1704 GOVERNMENT ST.', '', 'PENTICTON', 'BC', 'V2A 7A1', 'CA')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000001, '1704 GOVERNMENT ST.', '', 'PENTICTON', 'BC', 'V2A 7A1', 'CA')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000002, '1704 GOVERNMENT ST.', '', 'PENTICTON', 'BC', 'V2A 7A1', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000000, 'SUBMITTING', 'ACTIVE', 200000000, 200000000, null, null, null, 'REAL ENGINEERED HOMES INC',
           mhr_name_compressed_key('REAL ENGINEERED HOMES INC'), 190000000, null, '2507701067', null, null)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000001, 'OWNER_BUS', 'ACTIVE', 200000000, 200000000, null, null, null, 'REAL ENGINEERED HOMES INC', 
           mhr_name_compressed_key('REAL ENGINEERED HOMES INC'), 190000001, null, '2507701067', null, null)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000002, 'MANUFACTURER', 'ACTIVE', 200000000, 200000000, null, null, null, 'REAL ENGINEERED HOMES INC',
           'REALENGINEERED', 190000002, null, null, null, null)
;
INSERT INTO mhr_manufacturers(id, registration_id, submitting_party_id, owner_party_id, dealer_party_id,
                              manufacturer_name, account_id, bcol_account)
     VALUES (200000000, 200000000, 200000000, 200000001, 200000002, 'REAL ENGINEERED HOMES INC', 'PS12345', '251256')
;
-- QS 1
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000003, '1704 GOVERNMENT ST.', '', 'PENTICTON', 'BC', 'V2A 7A1', 'CA')
;
INSERT INTO mhr_qualified_suppliers(id, party_type, first_name, middle_name, last_name, business_name, address_id,
                                    email_address, phone_number, phone_extension, account_id)
    VALUES(200000000, 'CONTACT', null, null, null, 'TEST NOTARY PUBLIC', 190000003, 'test@gmail.com', '6041234567', '123', 'PS12345')
;
-- UT 001 active, no other registrations.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000001, '000900', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0001')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000004, '1234 TEST-0001', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000003, 'SUBMITTING', 'ACTIVE', 200000001, 200000001, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000004, 'test@gmail.com', '6041234567', '123', null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000005, '1234 TEST-0001', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000001, 'MH_PARK', 'ACTIVE', 200000001, 200000001, 190000005,
           'PARCEL A (N33545) OF THE SOUTH 1/2 OF SECTION 35 TOWNSHIP 84 RANGE 20\nWEST OF THE 6TH MERIDIAN PEACE RIVER DISTRICT',
           'additional', 'dealer', 'except', 'N', 'Y', now() at time zone 'UTC', 'park name', 'pad', '008000000', 'lot', 'parcel',
           'block', 'dist lot', 'part of', 'section', 'town', 'range', 'merid', 'land district', 'plan') 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000001, 'ACTIVE', 200000001, '7777700000', '1234', 1, 2000, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000001)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000001, 200000001, 'ACTIVE', mhr_serial_compressed_key('000060'), '000060', 60, 10, 14, 11,
           200000001)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000001, 'REG_101', 200000001, 'UT000001', '90499001', 'attn', NULL, NULL, 'Y', null, null, null, 200000001)
;
-- Include just for testing
INSERT INTO mhr_notes(id, document_type, registration_id, document_id, status_type, remarks, destroyed,
                      change_registration_id, expiry_date)
    VALUES(200000001, 'REG_101', 200000001, 200000001, 'ACTIVE', 'remarks here', 'N', 200000001, null)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000001, 1, 200000001, 'ACTIVE', 'COMMON', 'UNDIVIDED', 'Y', 1, 2, 200000001, 1)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000002, 2, 200000001, 'ACTIVE', 'COMMON', 'UNDIVIDED', 'Y', 1, 2, 200000001, 2)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000006, '1234 TEST-0001', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000007, '1234 TEST-0001', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000004, 'OWNER_BUS', 'ACTIVE', 200000001, 200000001, null, null, null, 'CELESTIAL HEAVENLY HOMES', 
           mhr_name_compressed_key('CELESTIAL HEAVENLY HOMES'), 190000006, null, '2507701067', null, 200000001)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000005, 'OWNER_IND', 'ACTIVE', 200000001, 200000001, 'BOB', 'ARTHUR', 'MCKAY', null, 
           mhr_name_compressed_key('MCKAY BOB ARTHUR'), 190000007, null, '2507701067', null, 200000002)
;
INSERT INTO mhr_registration_reports (id, create_ts, report_data, registration_id, report_type, doc_storage_url)
   VALUES (200000001, now() at time zone 'UTC',
'{"mhrNumber": "000911", "createDateTime": "2023-05-25T18:43:36+00:00", "registrationType": "MHREG", "status": "ACTIVE", "declaredValue": 0, "documentDescription": "MANUFACTURED HOME REGISTRATION", "documentId": "103272", "documentRegistrationNumber": "00503029", "ownLand": true, "clientReferenceId": "UT-MHREG-MAN", "attentionReference": "JENNIFER SMITH", "submittingParty": {"businessName": "REAL ENGINEERED HOMES INC", "address": {"street": "1704 GOVERNMENT ST.", "city": "PENTICTON", "region": "BC", "country": "CA", "postalCode": "V2A 7A1"}, "phoneNumber": "2507701067"}, "location": {"locationId": 289, "status": "ACTIVE", "locationType": "MANUFACTURER", "address": {"street": "1704 GOVERNMENT ST.", "city": "PENTICTON", "region": "BC", "country": "CA", "postalCode": "V2A 7A1"}, "leaveProvince": false, "taxCertificate": false, "dealerName": "REAL ENGINEERED HOMES INC"}, "description": {"status": "ACTIVE", "sectionCount": 1, "baseInformation": {"make": "WATSON IND. (ALTA)", "model": "DUCHESS", "circa": false, "year": 2024}, "csaNumber": "786356", "csaStandard": "Z240", "manufacturer": "REAL ENGINEERED HOMES INC", "sections": [{"serialNumber": "73737", "lengthFeet": 60, "widthFeet": 12}]}, "ownerGroups": [{"groupId": 1, "type": "SOLE", "status": "ACTIVE", "tenancySpecified": true, "owners": [{"ownerId": 1455, "status": "ACTIVE", "partyType": "OWNER_BUS", "organizationName": "REAL ENGINEERED HOMES INC", "address": {"street": "1704 GOVERNMENT ST.", "city": "PENTICTON", "region": "BC", "country": "CA", "postalCode": "V2A 7A1"}, "type": "SOLE"}]}], "payment": {"invoiceId": "28610", "receipt": "/api/v1/payment-requests/28610/receipts"}, "usergroup": "mhr_manufacturer"}',
           200000001, 'mhrRegistration', null)
;
-- UT 002 active, used by owner search.
INSERT INTO mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, 
                               pay_invoice_id, pay_path, user_id, client_reference_id)
     VALUES (200000002, '000901', 'PS12345', 'MHREG', now() at time zone 'UTC', 'ACTIVE', 200000001, null, null, 'TESTUSER', 'UT-0002')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000008, '1234 TEST-0002', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000006, 'SUBMITTING', 'ACTIVE', 200000002, 200000002, null, null, null, 'SUBMITTING',
           mhr_name_compressed_key('SUBMITTING'), 190000008, 'test@gmail.com', '6041234567', '123', null)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000009, '1234 TEST-0001', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_locations(id, location_type, status_type, registration_id, change_registration_id, address_id, ltsa_description, 
                        additional_description, dealer_name, exception_plan, leave_province, tax_certification, tax_certification_date, 
                        park_name, park_pad, pid_number, lot, parcel, block, district_lot, part_of, section,
                        township, range, meridian, land_district, plan)
    VALUES(200000002, 'MH_PARK', 'ACTIVE', 200000002, 200000002, 190000009,
           NULL, 'additional', NULL, NULL, 'N', 'Y', now() at time zone 'UTC', 'park name', 'pad', NULL, NULL, NULL,
           NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) 
;
INSERT INTO mhr_descriptions(id, status_type, registration_id, csa_number, csa_standard, number_of_sections, 
                          square_feet, year_made, circa, engineer_date, engineer_name, manufacturer_name,
                          make, model, rebuilt_remarks, other_remarks, change_registration_id)
    VALUES(200000002, 'ACTIVE', 200000002, '7777700000', '1234', 1, 2000, 2015, 'Y', now() at time zone 'UTC',
           'engineer name', 'manufacturer', 'make', 'model', 'rebuilt', 'other', 200000002)
;
INSERT INTO mhr_sections(id, registration_id, status_type, compressed_key, serial_number, length_feet, length_inches,
                               width_feet, width_inches, change_registration_id)
    VALUES(200000002, 200000002, 'ACTIVE', mhr_serial_compressed_key('D1644'), 'D1644', 60, 10, 14, 11,
           200000002)
;
INSERT INTO mhr_documents(id, document_type, registration_id, document_id, document_registration_number, attention_reference, 
                          declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference, change_registration_id)
    VALUES(200000002, 'REG_101', 200000002, 'UT000002', '90499002', 'attn', NULL, NULL, 'Y', null, null, null, 200000002)
;
INSERT INTO mhr_owner_groups(id, sequence_number, registration_id, status_type, tenancy_type, interest,
                             tenancy_specified, interest_numerator, interest_denominator, change_registration_id, group_sequence_number)
    VALUES(200000003, 1, 200000002, 'ACTIVE', 'JOINT', NULL, 'Y', NULL, NULL, 200000002, 1)
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000010, '1234 TEST-0002', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000011, '1234 TEST-0002', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO addresses(id, street, street_additional, city, region, postal_code, country)
  VALUES(190000012, '1234 TEST-0002', NULL, 'CITY', 'BC', 'V8R 3A5', 'CA')
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000007, 'OWNER_IND', 'ACTIVE', 200000002, 200000002, 'BRIAN', NULL, 'RAMMOND', null, 
           mhr_name_compressed_key('RAMMOND BRIAN'), 190000010, null, '2507701067', null, 200000003)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000008, 'OWNER_IND', 'ACTIVE', 200000002, 200000002, 'ROSE', 'CHERYL', 'RAMMOND', null, 
           mhr_name_compressed_key('RAMMOND ROSE CHERYL'), 190000011, null, '2507701067', null, 200000003)
;
INSERT INTO mhr_parties(id, party_type, status_type, registration_id, change_registration_id, first_name, middle_name, 
                        last_name, business_name, compressed_name, address_id, email_address, phone_number, phone_extension, 
                        owner_group_id)
    VALUES(200000009, 'OWNER_IND', 'ACTIVE', 200000002, 200000002, 'DENISE', NULL, 'RAMMOND', null, 
           mhr_name_compressed_key('RAMMOND DENISE'), 190000012, null, '2507701067', null, 200000003)
;
