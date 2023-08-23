-- Final migration step: load staging table data into mhr* tables, preserving key order:
-- Assumes the following:
-- a. API gateway MHR api proxy is set to unavailable.
-- b. Existing registrations created in MHR are preserved as is. 
-- c. There are change registrations in the legacy application on registrations created in MHR.
-- d. There are change registrations in MHR on registrations created in in the legacy application.
--
-- 1. Optional: disable contraints on existing tables while bulk inserting.
-- 2. Truncate all mhr* tables.
-- 3. Reset sequences for primary keys except for registration id's.
-- 4. load all migrated addresses into the addresses table from the staging_mhr_address table.
-- 5. Use a database function to load registration data 10000 registrations at a time, preserving order in the primary keys.
-- 6. Set change_registration_id values for migrated records.
-- 7. Update sequences for primary keys.
-- 8. Merge migration records with existing PostgreSQL MHR table records in the temp_mhr* tables. 
--    i.  Matching on registrations by mhr_documents.document_id, update all temp_mhr* table primary and foreign keys.  
--    ii. Update all mhr* table non-key column values with those in the corresponding temp_mhr* table, matching on registration
--        id and type.
-- 9. Update location ltsa_description from table ltsa_descriptions.
-- 10. Optional: enable constraints
-- 11. Run mhr_manufacturers table load script: ./mhr_manufacturers.sql

/*
-- Optional disable constraints if administrator
ALTER TABLE mhr_registrations DISABLE TRIGGER ALL;
ALTER TABLE mhr_descriptions DISABLE TRIGGER ALL;
ALTER TABLE mhr_documents DISABLE TRIGGER ALL;
ALTER TABLE mhr_locations DISABLE TRIGGER ALL;
ALTER TABLE mhr_notes DISABLE TRIGGER ALL;
ALTER TABLE mhr_owner_groups DISABLE TRIGGER ALL;
ALTER TABLE mhr_parties DISABLE TRIGGER ALL;
ALTER TABLE mhr_registration_reports DISABLE TRIGGER ALL;
ALTER TABLE mhr_sections DISABLE TRIGGER ALL;
*/

-- Truncate mhr* tables
TRUNCATE TABLE public.mhr_sections;
TRUNCATE TABLE public.mhr_registration_reports;
TRUNCATE TABLE public.mhr_manufacturers;
TRUNCATE TABLE public.mhr_parties CASCADE;
TRUNCATE TABLE public.mhr_owner_groups CASCADE;
TRUNCATE TABLE public.mhr_notes;
TRUNCATE TABLE public.mhr_locations;
TRUNCATE TABLE public.mhr_descriptions;
TRUNCATE TABLE public.mhr_documents CASCADE;
TRUNCATE TABLE public.mhr_registrations CASCADE;

-- Reset sequences for mhr_* tables
SELECT setval('mhr_registration_id_seq', 1);
SELECT setval('mhr_description_id_seq', 1);
SELECT setval('mhr_document_id_seq', 1);
SELECT setval('mhr_location_id_seq', 1);
SELECT setval('mhr_note_id_seq', 1);
SELECT setval('mhr_owner_group_id_seq', 1);
SELECT setval('mhr_party_id_seq', 1);
SELECT setval('mhr_section_id_seq', 1);

-- Load data, preserving order with the primary key values.
select min(id), max(id), count(id)
  from staging_mhr_addresses
;
-- Replace min(id), max(id) and adjust ranges
INSERT INTO addresses (id, street, street_additional, city, region, postal_code, country)
(SELECT id, street, street_additional, city, region, postal_code, country
   FROM staging_mhr_addresses
  WHERE id BETWEEN min(id) AND max(id)) 
;
COMMIT;
INSERT INTO addresses (id, street, street_additional, city, region, postal_code, country)
(SELECT id, street, street_additional, city, region, postal_code, country
   FROM staging_mhr_addresses
  WHERE id BETWEEN 5100001 AND 5400000) 
;
COMMIT;
INSERT INTO addresses (id, street, street_additional, city, region, postal_code, country)
(SELECT id, street, street_additional, city, region, postal_code, country
   FROM staging_mhr_addresses
  WHERE id BETWEEN 5400001 AND 5700000) 
;
COMMIT;
INSERT INTO addresses (id, street, street_additional, city, region, postal_code, country)
(SELECT id, street, street_additional, city, region, postal_code, country
   FROM staging_mhr_addresses
  WHERE id >= 5700001) 
;
COMMIT;

-- To satisfy integrity constraint.
select *
  from mhr_drafts
where id = 0
;
INSERT INTO mhr_drafts(id, draft_number, account_id, registration_type, create_ts, draft, mhr_number, update_ts, user_id)
     VALUES (0, 'CONV-1', '0', 'MHREG', now() at time zone 'UTC', '{}',null, null, 'TESTUSER')
;
COMMIT;

-- Run the final load from staging tables here
SELECT mhr_conversion_registration(1, 10000);
SELECT mhr_conversion_registration(10001, 20000);
SELECT mhr_conversion_registration(20001, 30000);
SELECT mhr_conversion_registration(30001, 40000);
SELECT mhr_conversion_registration(40001, 50000);

SELECT mhr_conversion_registration(50001, 60000);
SELECT mhr_conversion_registration(60001, 70000);
SELECT mhr_conversion_registration(70001, 80000);
SELECT mhr_conversion_registration(80001, 90000);
SELECT mhr_conversion_registration(90001, 100000);

SELECT mhr_conversion_registration(100001, 110000);
SELECT mhr_conversion_registration(110001, 120000);
SELECT mhr_conversion_registration(120001, 130000);
SELECT mhr_conversion_registration(130001, 140000);
SELECT mhr_conversion_registration(140001, 150000);

SELECT mhr_conversion_registration(150001, 160000);
SELECT mhr_conversion_registration(160001, 170000);
SELECT mhr_conversion_registration(170001, 180000);
SELECT mhr_conversion_registration(180001, 190000);
SELECT mhr_conversion_registration(190001, 200000);

SELECT mhr_conversion_registration(200001, 210000);
SELECT mhr_conversion_registration(210001, 220000);
SELECT mhr_conversion_registration(220001, 230000);
SELECT mhr_conversion_registration(230001, 240000);
SELECT mhr_conversion_registration(240001, 250000);

SELECT mhr_conversion_registration(250001, 260000);
SELECT mhr_conversion_registration(260001, 270000);
SELECT mhr_conversion_registration(270001, 280000);
SELECT mhr_conversion_registration(280001, 290000);
SELECT mhr_conversion_registration(290001, 300000);

SELECT mhr_conversion_registration(300001, 310000);
SELECT mhr_conversion_registration(310001, 320000);
SELECT mhr_conversion_registration(320001, 330000);
SELECT mhr_conversion_registration(330001, 340000);
SELECT mhr_conversion_registration(340001, 350000);

SELECT mhr_conversion_registration(350001, 360000);
SELECT mhr_conversion_registration(360001, 370000);
SELECT mhr_conversion_registration(370001, 380000);
SELECT mhr_conversion_registration(380001, 390000);
SELECT mhr_conversion_registration(390001, 400000);

SELECT mhr_conversion_registration(400001, 410000);
SELECT mhr_conversion_registration(410001, 420000);
SELECT mhr_conversion_registration(420001, 430000);
SELECT mhr_conversion_registration(430001, 440000);
SELECT mhr_conversion_registration(440001, 450000);

SELECT mhr_conversion_registration(450001, 460000);
SELECT mhr_conversion_registration(460001, 470000);
SELECT mhr_conversion_registration(470001, 480000);
SELECT mhr_conversion_registration(480001, 490000);
SELECT mhr_conversion_registration(490001, 500000);

-- Update mhr* table change_registration_id's.
UPDATE mhr_notes
   SET change_registration_id = staging_mhr_note.change_registration_id
  FROM staging_mhr_note
 WHERE mhr_notes.registration_id = staging_mhr_note.registration_id
   AND staging_mhr_note.change_registration_id IS NOT NULL
;
UPDATE mhr_sections
   SET change_registration_id = staging_mhr_description.change_registration_id
  FROM staging_mhr_description
 WHERE mhr_sections.registration_id = staging_mhr_description.registration_id
   AND staging_mhr_description.change_registration_id IS NOT NULL
;
UPDATE mhr_descriptions
   SET change_registration_id = staging_mhr_description.change_registration_id
  FROM staging_mhr_description
 WHERE mhr_descriptions.registration_id = staging_mhr_description.registration_id
   AND staging_mhr_description.change_registration_id IS NOT NULL
;
UPDATE mhr_locations
   SET change_registration_id = staging_mhr_location.change_registration_id
  FROM staging_mhr_location
 WHERE mhr_locations.registration_id = staging_mhr_location.registration_id
   AND staging_mhr_location.change_registration_id IS NOT NULL
;
UPDATE mhr_parties
   SET change_registration_id = staging_mhr_owner.change_registration_id
  FROM staging_mhr_owner
 WHERE mhr_parties.registration_id = staging_mhr_owner.registration_id
   AND mhr_parties.party_type NOT IN ('SUBMITTING', 'MANUFACTURER', 'CONTACT')
   AND staging_mhr_owner.change_registration_id IS NOT NULL
;
UPDATE mhr_parties
   SET change_registration_id = staging_mhr_note.change_registration_id
  FROM staging_mhr_note
 WHERE mhr_parties.registration_id = staging_mhr_note.registration_id
   AND mhr_parties.party_type = 'CONTACT'
   AND staging_mhr_note.change_registration_id IS NOT NULL
;
UPDATE mhr_owner_groups
   SET change_registration_id = staging_mhr_owngroup.change_registration_id
  FROM staging_mhr_owngroup
 WHERE mhr_owner_groups.registration_id = staging_mhr_owngroup.registration_id
   AND staging_mhr_owngroup.change_registration_id IS NOT NULL
;
COMMIT;

-- Set sequences
SELECT setval('mhr_registration_id_seq', (SELECT MAX(id) + 1 from mhr_registrations WHERE id < 100000000));
SELECT setval('mhr_description_id_seq', (SELECT MAX(id) + 1 from mhr_descriptions WHERE id < 100000000));
SELECT setval('mhr_document_id_seq', (SELECT MAX(id) + 1 from mhr_documents WHERE id < 100000000));
SELECT setval('mhr_location_id_seq', (SELECT MAX(id) + 1 from mhr_locations WHERE id < 100000000));
SELECT setval('mhr_note_id_seq', (SELECT MAX(id) + 1 from mhr_notes WHERE id < 100000000));
SELECT setval('mhr_owner_group_id_seq', (SELECT MAX(id) + 1 from mhr_owner_groups WHERE id < 100000000));
SELECT setval('mhr_party_id_seq', (SELECT MAX(id) + 1 from mhr_parties WHERE id < 100000000));
SELECT setval('mhr_section_id_seq', (SELECT MAX(id) + 1 from mhr_sections WHERE id < 100000000));
SELECT setval('address_id_seq', (SELECT MAX(id) + 1 FROM addresses WHERE id < 99990000));
SELECT setval('mhr_registration_report_id_seq', (SELECT MAX(id) + 1 FROM mhr_registration_reports WHERE id < 100000000));

-- Merge extract registrations with existing PostgreSQL registrations here.
-- Requires some registrations created in PROD to unit test.
-- First, update existing registration record temp_mhr* table keys.
UPDATE temp_mhr_registrations
   SET id = mhr_documents.registration_id
  FROM mhr_documents, temp_mhr_documents
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
;
UPDATE temp_mhr_locations
   SET id = mhr_locations.id, registration_id = mhr_documents.registration_id, change_registration_id = mhr_locations.change_registration_id
  FROM mhr_documents, temp_mhr_documents, mhr_locations
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
   and mhr_locations.registration_id = mhr_documents.registration_id
;
UPDATE temp_mhr_descriptions
   SET id = mhr_descriptions.id, registration_id = mhr_documents.registration_id, change_registration_id = mhr_descriptions.change_registration_id
  FROM mhr_documents, temp_mhr_documents, mhr_descriptions
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
   and mhr_descriptions.registration_id = mhr_documents.registration_id
;
UPDATE temp_mhr_notes
   SET id = mhr_notes.id, registration_id = mhr_documents.registration_id, change_registration_id = mhr_notes.change_registration_id
  FROM mhr_documents, temp_mhr_documents, mhr_notes
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
   and mhr_notes.registration_id = mhr_documents.registration_id
;
UPDATE temp_mhr_registration_reports
   SET id = mhr_registration_reports.id, registration_id = mhr_documents.registration_id
  FROM mhr_documents, temp_mhr_documents, mhr_registration_reports
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
   and mhr_registration_reports.registration_id = mhr_documents.registration_id
;
COMMIT;
UPDATE temp_mhr_owner_groups
   SET id = mhr_owner_groups.id, registration_id = mhr_documents.registration_id, change_registration_id = mhr_owner_groups.change_registration_id
  FROM mhr_documents, temp_mhr_documents, mhr_owner_groups
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
   and mhr_owner_groups.registration_id = mhr_documents.registration_id
   and mhr_owner_groups.sequence_number = temp_mhr_owner_groups.sequence_number
;
COMMIT;
UPDATE temp_mhr_sections
   SET id = mhr_sections.id, registration_id = mhr_documents.registration_id, change_registration_id = mhr_sections.change_registration_id
  FROM mhr_documents, temp_mhr_documents, mhr_sections
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
   and mhr_sections.registration_id = mhr_documents.registration_id
   and mhr_sections.serial_number = temp_mhr_sections.serial_number
   and mhr_sections.length_feet = temp_mhr_sections.length_feet
   and mhr_sections.width_feet = temp_mhr_sections.width_feet
;
COMMIT;
UPDATE temp_mhr_parties
   SET id = mhr_parties.id, registration_id = mhr_documents.registration_id, change_registration_id = mhr_parties.change_registration_id
  FROM mhr_documents, temp_mhr_documents, mhr_parties
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
   and mhr_parties.registration_id = mhr_documents.registration_id
   and mhr_parties.party_type = temp_mhr_sections.party_type
   and mhr_parties.compressed_name = temp_mhr_sections.compressed_name
;
COMMIT;
-- Must be the last update.
UPDATE temp_mhr_documents
   SET id = mhr_documents.id, registration_id = mhr_documents.registration_id, change_registration_id = mhr_documents.change_registration_id
  FROM mhr_documents
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
;
COMMIT;

-- Merge original record data with loaded record data.
UPDATE mhr_registrations
    SET registration_ts = temp_mhr_registrations.registration_ts,
        account_id = temp_mhr_registrations.account_id,
        draft_id = temp_mhr_registrations.draft_id,
        pay_invoice_id = temp_mhr_registrations.pay_invoice_id,
        pay_path = temp_mhr_registrations.pay_path,
        user_id = temp_mhr_registrations.user_id,
        client_reference_id = temp_mhr_registrations.client_reference_id
  FROM temp_mhr_registrations
 WHERE mhr_registrations.id = temp_mhr_registrations.id
;
COMMIT;
UPDATE mhr_locations
   SET address_id = temp_mhr_locations.address_id,
       location_type = temp_mrh_locations.location_type,
       ltsa_description = temp_mhr_locations.ltsa_description,
       additional_description = temp_mhr_locations.additional_description,
       dealer_name = temp_mhr_locations.dealer_name,
       exception_plan = temp_mhr_locations.exception_plan,
       tax_certification_date = temp_mhr_locations.tax_certification_date,
       park_name = temp_mhr_locations.park_name,
       park_pad = temp_mhr_locations.park_pad,
       pid_number = temp_mhr_locations.pid_number,
       lot = temp_mhr_locations.lot,
       parcel = temp_mhr_locations.parcel,
       block = temp_mhr_locations.block,
       district_lot = temp_mhr_locations.district_lot,
       part_of = temp_mhr_locations.part_of,
       section = temp_mhr_locations.section,
       township = temp_mhr_locations.township,
       range = temp_mhr_locations.range,
       meridian = temp_mhr_locations.meridian,
       land_district = temp_mhr_locations.land_district,
       plan = temp_mhr_locations.plan,
       band_name = temp_mhr_locations.band_name,
       reserve_number = temp_mhr_locations.reserve_number
  FROM temp_mhr_locations
 WHERE mhr_locations.id = temp_mhr_locations.id
   AND mhr_locations.registration_id = temp_mhr_locations.registration_id
;
COMMIT;
UPDATE mhr_parties
   SET address_id = temp_mhr_parties.address_id,
       email_address = temp_mhr_parties.email_address,
       phone_number = temp_mhr_parties.phone_number,
       phone_extension = temp_mhr_parties.phone_extension,
       description = temp_mhr_parties.description,
       death_cert_number = temp_mhr_parties.death_cert_number,
       death_ts = temp_mhr_parties.death_ts,
       suffix = temp_mhr_parties.suffix
  FROM temp_mhr_parties
 WHERE mhr_parties.id = temp_mhr_parties.id
   AND mhr_parties.registration_id = temp_mhr_parties.registration_id
;
COMMIT;
UPDATE mhr_documents
   SET attention_reference = temp_mhr_documents.attention_reference,
       declared_value = temp_mhr_documents.declared_value,
       consideration_value = temp_mhr_documents.consideration_value,
       own_land = temp_mhr_documents.own_land,
       transfer_date = temp_mhr_documents.transfer_date,
       affirm_by = temp_mhr_documents.affirm_by
  FROM temp_mhr_documents
 WHERE mhr_documents.id = temp_mhr_documents.id
   AND mhr_documents.registration_id = temp_mhr_documents.registration_id
;
COMMIT;
UPDATE mhr_descriptions
   SET csa_number = temp_mhr_descriptions.csa_number,
       csa_standard = temp_mhr_descriptions.csa_standard,
       number_of_sections = temp_mhr_descriptions.number_of_sections,
       year_made = temp_mhr_descriptions.year_made,
       engineer_date = temp_mhr_descriptions.engineer_date,
       engineer_name = temp_mhr_descriptions.engineer_name,
       manufacturer_name = temp_mhr_descriptions.manufacturer_name,
       make = temp_mhr_descriptions.make,
       model = temp_mhr_descriptions.model,
       rebuilt_remarks = temp_mhr_descriptions.rebuilt_remarks,
       other_remarks = temp_mhr_descriptions.other_remarks
  FROM temp_mhr_descriptions
 WHERE mhr_descriptions.id = temp_mhr_descriptions.id
   AND mhr_descriptions.registration_id = temp_mhr_descriptions.registration_id
;
COMMIT;
SELECT *
  INTO TABLE mhr_regisration_reports
  FROM temp_mhr_registration_reports;
;
COMMIT;

-- Update location ltsa_description from table ltsa_descriptions.
UPDATE mhr_locations
   SET ltsa_description = ltsa_descriptions.ltsa_description
  FROM ltsa_descriptions
 WHERE mhr_locations.ltsa_description IS NULL
   AND mhr_locations.pid_number IS NOT NULL
   AND mhr_locations.pid_number = ltsa_descriptions.pid_number
;
COMMIT;

-- Optional enable constraints if administrator
/*
ALTER TABLE mhr_registrations ENABLE TRIGGER ALL;
ALTER TABLE mhr_descriptions ENABLE TRIGGER ALL;
ALTER TABLE mhr_documents ENABLE TRIGGER ALL;
ALTER TABLE mhr_locations ENABLE TRIGGER ALL;
ALTER TABLE mhr_notes ENABLE TRIGGER ALL;
ALTER TABLE mhr_owner_groups ENABLE TRIGGER ALL;
ALTER TABLE mhr_parties ENABLE TRIGGER ALL;
ALTER TABLE mhr_registration_reports ENABLE TRIGGER ALL;
ALTER TABLE mhr_sections ENABLE TRIGGER ALL;
*/

-- Run manufacturers load script ./mhr_manufacturers.sql.

-- Enable mhr api in the gateway.
-- Non prod adjust the db2 sequence number for MHR numbers
/*
select *
  from amhrtdb.contnumb
;

update amhrtdb.contnumb
  set contnum = 107706
where contkey = 'SERMREG'
;
*/
