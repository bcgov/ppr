-- Optionally run this script if reloading migrated data to delete records from the previous load.
-- Requires that the previous load data is still in the staging tables.
-- 1. Either truncate all mhr* tables or delete records from previous load. In both cases
-- 2. Delete the addresses records. 

-- 1 Either truncate mhr* tables
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

-- 1 Or delete new registrations: change registrations on migrated MHR's first
DELETE
  FROM mhr_registration_reports
 WHERE registration_id IN (SELECT r.id
                              FROM mhr_registrations r, staging_mhr_manuhome m
                             WHERE r.mhr_number = m.mhregnum)
;
COMMIT;

DELETE
  FROM mhr_sections
 WHERE registration_id IN (SELECT r.id
                              FROM mhr_registrations r, staging_mhr_manuhome m
                             WHERE r.mhr_number = m.mhregnum
                               AND r.id >= 550000)
;
COMMIT;
DELETE 
  FROM mhr_sections
 WHERE registration_id BETWEEN (SELECT MIN(registration_id) FROM staging_mhr_document) AND 
                               (SELECT MAX(registration_id) FROM staging_mhr_document)
;
COMMIT;

DELETE
  FROM mhr_descriptions
 WHERE registration_id IN (SELECT r.id
                              FROM mhr_registrations r, staging_mhr_manuhome m
                             WHERE r.mhr_number = m.mhregnum
                               AND r.id >= 550000)
;
COMMIT;
DELETE 
  FROM mhr_descriptions
 WHERE registration_id BETWEEN (SELECT MIN(registration_id) FROM staging_mhr_document) AND 
                               (SELECT MAX(registration_id) FROM staging_mhr_document)
;
COMMIT;

DELETE
  FROM mhr_locations
 WHERE registration_id IN (SELECT r.id
                              FROM mhr_registrations r, staging_mhr_manuhome m
                             WHERE r.mhr_number = m.mhregnum
                               AND r.id >= 550000)
;
COMMIT;
DELETE 
  FROM mhr_locations
 WHERE registration_id BETWEEN (SELECT MIN(registration_id) FROM staging_mhr_document) AND 
                               (SELECT MAX(registration_id) FROM staging_mhr_document)
;
COMMIT;

DELETE
  FROM mhr_notes
 WHERE registration_id IN (SELECT r.id
                              FROM mhr_registrations r, staging_mhr_manuhome m
                             WHERE r.mhr_number = m.mhregnum
                               AND r.id >= 550000)
;
COMMIT;
DELETE 
  FROM mhr_notes
 WHERE registration_id BETWEEN (SELECT MIN(registration_id) FROM staging_mhr_document) AND 
                               (SELECT MAX(registration_id) FROM staging_mhr_document)
;
COMMIT;

DELETE
  FROM mhr_parties
 WHERE registration_id IN (SELECT r.id
                              FROM mhr_registrations r, staging_mhr_manuhome m
                             WHERE r.mhr_number = m.mhregnum
                               AND r.id >= 550000)
;
COMMIT;
DELETE 
  FROM mhr_parties
 WHERE registration_id BETWEEN (SELECT MIN(registration_id) FROM staging_mhr_document) AND 
                               (SELECT MAX(registration_id) FROM staging_mhr_document)
;
COMMIT;

DELETE
  FROM mhr_owner_groups
 WHERE registration_id IN (SELECT r.id
                              FROM mhr_registrations r, staging_mhr_manuhome m
                             WHERE r.mhr_number = m.mhregnum
                               AND r.id >= 550000)
;
COMMIT;
DELETE 
  FROM mhr_owner_groups
 WHERE registration_id BETWEEN (SELECT MIN(registration_id) FROM staging_mhr_document) AND 
                               (SELECT MAX(registration_id) FROM staging_mhr_document)
;
COMMIT;

DELETE
  FROM mhr_documents
 WHERE registration_id IN (SELECT r.id
                              FROM mhr_registrations r, staging_mhr_manuhome m
                             WHERE r.mhr_number = m.mhregnum
                               AND r.id >= 550000)
;
COMMIT;
DELETE 
  FROM mhr_documents
 WHERE registration_id BETWEEN (SELECT MIN(registration_id) FROM staging_mhr_document) AND 
                               (SELECT MAX(registration_id) FROM staging_mhr_document)
;
COMMIT;
DELETE
  FROM mhr_registrations
 WHERE id IN (SELECT r.id
                FROM mhr_registrations r, staging_mhr_manuhome m
               WHERE r.mhr_number = m.mhregnum
                 AND r.id >= 550000)
;
COMMIT;
DELETE 
  FROM mhr_registrations
 WHERE id BETWEEN (SELECT MIN(registration_id) FROM staging_mhr_document) AND 
                  (SELECT MAX(registration_id) FROM staging_mhr_document)
;
COMMIT;

-- 2 Always run addresses table cleanup, and run it last.
DELETE 
  FROM addresses
 WHERE id IN (SELECT address_id
                FROM staging_mhr_document)
;
COMMIT;
DELETE 
  FROM addresses
 WHERE id IN (SELECT address_id
                FROM staging_mhr_note)
;
COMMIT;
DELETE 
  FROM addresses
 WHERE id IN (SELECT submitting_address_id
                FROM staging_mhr_manufacturer)
;
DELETE 
  FROM addresses
 WHERE id IN (SELECT owner_address_id
                FROM staging_mhr_manufacturer)
;
DELETE 
  FROM addresses
 WHERE id IN (SELECT dealer_address_id
                FROM staging_mhr_manufacturer)
;
COMMIT;
DELETE 
  FROM addresses
 WHERE id IN (SELECT address_id
                FROM staging_mhr_location)
;
COMMIT;
DELETE 
  FROM addresses
 WHERE id IN (SELECT address_id
                FROM staging_mhr_owner)
;
COMMIT;
