-- 1. Merge migration records with existing PostgreSQL MHR table records in the temp_mhr* tables.
--    i.  Matching on registrations by mhr_documents.document_id, update all temp_mhr* table primary and foreign keys.  
--    ii. Update all mhr* table non-key column values with those in the corresponding temp_mhr* table, matching on registration
--        id and type.
-- 2. Update location ltsa_description from table ltsa_descriptions.
-- 3. Optional: enable constraints
-- 4. Reload mhr_manufacturers table records: see script: ./mhr-manufacturers.sql

-- First, update existing registration record temp_mhr* table keys.
UPDATE temp_mhr_registrations
   SET id = mhr_documents.registration_id
  FROM mhr_documents, temp_mhr_documents
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
   AND temp_mhr_registrations.id = temp_mhr_documents.registration_id
   AND temp_mhr_registrations.registration_type != 'MANUFACTURER'
;
UPDATE temp_mhr_locations
   SET id = mhr_locations.id, registration_id = mhr_locations.registration_id, change_registration_id = mhr_locations.change_registration_id
  FROM mhr_documents, temp_mhr_documents, mhr_locations
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
   AND mhr_locations.registration_id = mhr_documents.registration_id
   AND temp_mhr_locations.registration_id = temp_mhr_documents.registration_id
;
UPDATE temp_mhr_descriptions
   SET id = mhr_descriptions.id, registration_id = mhr_descriptions.registration_id, change_registration_id = mhr_descriptions.change_registration_id
  FROM mhr_documents, temp_mhr_documents, mhr_descriptions
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
   AND mhr_descriptions.registration_id = mhr_documents.registration_id
   AND temp_mhr_descriptions.registration_id = temp_mhr_documents.registration_id
;
UPDATE temp_mhr_notes
   SET id = mhr_notes.id, registration_id = mhr_notes.registration_id, change_registration_id = mhr_notes.change_registration_id
  FROM mhr_documents, temp_mhr_documents, mhr_notes
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
   AND mhr_notes.registration_id = mhr_documents.registration_id
   AND temp_mhr_notes.registration_id = temp_mhr_documents.registration_id
;

-- This table has no migrated data.
UPDATE temp_mhr_registration_reports
   SET registration_id = mhr_documents.registration_id
  FROM mhr_documents, temp_mhr_documents
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
   AND temp_mhr_documents.registration_id = temp_mhr_registration_reports.registration_id
;
UPDATE temp_mhr_owner_groups
   SET id = mhr_owner_groups.id, registration_id = mhr_owner_groups.registration_id, change_registration_id = mhr_owner_groups.change_registration_id
  FROM mhr_documents, temp_mhr_documents, mhr_owner_groups
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
   AND mhr_owner_groups.registration_id = mhr_documents.registration_id
   AND temp_mhr_owner_groups.registration_id = temp_mhr_documents.registration_id
   AND mhr_owner_groups.sequence_number = temp_mhr_owner_groups.sequence_number
;
UPDATE temp_mhr_sections
   SET id = mhr_sections.id, registration_id = mhr_sections.registration_id, change_registration_id = mhr_sections.change_registration_id
  FROM mhr_documents, temp_mhr_documents, mhr_sections
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
   AND mhr_sections.registration_id = mhr_documents.registration_id
   AND temp_mhr_sections.registration_id = temp_mhr_documents.registration_id
   AND mhr_sections.serial_number = temp_mhr_sections.serial_number
   AND mhr_sections.length_feet = temp_mhr_sections.length_feet
   AND mhr_sections.width_feet = temp_mhr_sections.width_feet
;
UPDATE temp_mhr_parties
   SET id = mhr_parties.id, registration_id = mhr_parties.registration_id, change_registration_id = mhr_parties.change_registration_id,
       owner_group_id = mhr_parties.owner_group_id
  FROM mhr_documents, temp_mhr_documents, mhr_parties
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
   AND mhr_parties.registration_id = mhr_documents.registration_id
   AND temp_mhr_parties.registration_id = temp_mhr_documents.registration_id
   AND mhr_parties.party_type = temp_mhr_parties.party_type
   AND temp_mhr_parties.party_type = 'SUBMITTING'
;
UPDATE temp_mhr_parties
   SET id = mhr_parties.id, registration_id = mhr_parties.registration_id, change_registration_id = mhr_parties.change_registration_id,
       owner_group_id = mhr_parties.owner_group_id
  FROM mhr_documents, temp_mhr_documents, mhr_parties
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
   AND mhr_parties.registration_id = mhr_documents.registration_id
   AND temp_mhr_parties.registration_id = temp_mhr_documents.registration_id
   AND mhr_parties.party_type = temp_mhr_parties.party_type
   AND temp_mhr_parties.party_type != 'SUBMITTING'
   AND (mhr_parties.business_name = temp_mhr_parties.business_name OR
        (mhr_parties.last_name = temp_mhr_parties.last_name AND mhr_parties.first_name = temp_mhr_parties.first_name))
;
-- Must be the last update.
UPDATE temp_mhr_documents
   SET id = mhr_documents.id, registration_id = mhr_documents.registration_id, change_registration_id = mhr_documents.change_registration_id
  FROM mhr_documents
 WHERE mhr_documents.document_id = temp_mhr_documents.document_id
;

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
UPDATE mhr_locations
   SET address_id = temp_mhr_locations.address_id,
       location_type = temp_mhr_locations.location_type,
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

INSERT INTO mhr_registration_reports (id, create_ts, report_data, registration_id, report_type, doc_storage_url, batch_storage_url)
(SELECT id, create_ts, report_data, registration_id, report_type, doc_storage_url, batch_storage_url
   FROM temp_mhr_registration_reports)  
;
SELECT setval('mhr_registration_report_id_seq', (SELECT MAX(id) + 1 from mhr_registration_reports WHERE id < 100000000));


-- Update location.ltsa_description from table ltsa_descriptions.
UPDATE mhr_locations
   SET ltsa_description = ltsa_descriptions.ltsa_description
  FROM ltsa_descriptions
 WHERE mhr_locations.ltsa_description IS NULL
   AND mhr_locations.pid_number IS NOT NULL
   AND mhr_locations.pid_number = ltsa_descriptions.pid_number
;

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

-- Reload mhr_manufacturers records see script ./mhr-manufacturers.sql.
ALTER SEQUENCE mhr_manufacturer_id_seq INCREMENT 1 START 1;
SELECT mhr_restore_manufacturer();

-- Container update env property USE_LEGACY_DB set to "false" .
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
