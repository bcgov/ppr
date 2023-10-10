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
INSERT INTO addresses (id, street, street_additional, city, region, postal_code, country)
(SELECT id, street, street_additional, city, region, postal_code, country
   FROM staging_mhr_addresses
  WHERE id BETWEEN 5100001 AND 5400000) 
;
INSERT INTO addresses (id, street, street_additional, city, region, postal_code, country)
(SELECT id, street, street_additional, city, region, postal_code, country
   FROM staging_mhr_addresses
  WHERE id BETWEEN 5400001 AND 5700000) 
;
INSERT INTO addresses (id, street, street_additional, city, region, postal_code, country)
(SELECT id, street, street_additional, city, region, postal_code, country
   FROM staging_mhr_addresses
  WHERE id >= 5700001) 
;

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

-- Set sequences
SELECT setval('mhr_registration_id_seq', (SELECT MAX(id) + 1 from mhr_registrations WHERE id < 100000000));
SELECT setval('mhr_description_id_seq', (SELECT MAX(id) + 1 from mhr_descriptions WHERE id < 100000000));
SELECT setval('mhr_document_id_seq', (SELECT MAX(id) + 1 from mhr_documents WHERE id < 100000000));
SELECT setval('mhr_location_id_seq', (SELECT MAX(id) + 1 from mhr_locations WHERE id < 100000000));
SELECT setval('mhr_note_id_seq', (SELECT MAX(id) + 1 from mhr_notes WHERE id < 100000000));
SELECT setval('mhr_owner_group_id_seq', (SELECT MAX(id) + 1 from mhr_owner_groups WHERE id < 100000000));
SELECT setval('mhr_party_id_seq', (SELECT MAX(id) + 1 from mhr_parties WHERE id < 100000000));
SELECT setval('mhr_section_id_seq', (SELECT MAX(id) + 1 from mhr_sections WHERE id < 100000000));
--SELECT setval('address_id_seq', (SELECT MAX(id) + 1 FROM addresses WHERE id < 99990000));
SELECT setval('mhr_number_seq', (SELECT CAST(MAX(mhr_number) AS INT) + 1 FROM mhr_registrations));
