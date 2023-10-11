-- Post staging tables load step 2:
-- Alter staging table definitions to add columns that will hold the target PostgreSQL table transformed data values.
-- After all transforms have occurred, the target table load will be an insert from the corresponding staging table.

-- staging_mhr_note.status_type target mhr_notes.status_type
-- staging_mhr_note.expiry_date target mhr_notes.expiry_date
-- staging_mhr_note contact party target mhr_parties.business_name, first_name, middle_name, last_name, suffix
-- staging_mhr_note.address_id target mhr_notes.address_id, addresses.id
-- staging_mhr_note.registration_id target mhr_notes.registration_id
-- staging_mhr_note.change_registration_id target mhr_notes.change_registration_id
ALTER TABLE staging_mhr_note
  ADD COLUMN status_type VARCHAR(20) NULL,
  ADD COLUMN expiry_date TIMESTAMP NULL,
  ADD COLUMN business_name VARCHAR(40) NULL,
  ADD COLUMN first_name VARCHAR(40) NULL,
  ADD COLUMN middle_name VARCHAR(40) NULL,
  ADD COLUMN last_name VARCHAR(40) NULL,
  ADD COLUMN suffix VARCHAR(40) NULL,
  ADD COLUMN address_id INTEGER NULL,
  ADD COLUMN registration_id INTEGER NULL,
  ADD COLUMN change_registration_id INTEGER NULL
;

-- staging_mhr_document.registration_ts target mhr_registrations.registration_ts
-- staging_mhr_document.status_type target mhr_registrations.status_type
-- staging_mhr_document submitting party target mhr_parties.business_name, first_name, middle_name, last_name, suffix
-- staging_mhr_document.address_id target addresses.id
-- staging_mhr_document.registration_type target mhr_registrations.registration_type
-- staging_mhr_document.registration_id target mhr_registrations.id,mhr_documents.registration_id,mhr_documents.change_registration_id
ALTER TABLE staging_mhr_document
  ADD COLUMN registration_ts TIMESTAMP NULL,
  ADD COLUMN status_type VARCHAR(20) NULL,
  ADD COLUMN transfer_date TIMESTAMP NULL,
  ADD COLUMN business_name VARCHAR(40) NULL,
  ADD COLUMN first_name VARCHAR(40) NULL,
  ADD COLUMN middle_name VARCHAR(40) NULL,
  ADD COLUMN last_name VARCHAR(40) NULL,
  ADD COLUMN suffix VARCHAR(40) NULL,
  ADD COLUMN address_id INTEGER NULL,
  ADD COLUMN registration_type VARCHAR(20) NULL,
  ADD COLUMN registration_id INTEGER NULL
;

-- staging_mhr_description.status_type target mhr_descriptions.status_type
-- staging_mhr_description.engineer_date target mhr_descriptions.engineer_date
-- staging_mhr_description.make target mhr_descriptions.make
-- staging_mhr_description.model target mhr_descriptions.model
-- staging_mhr_description.registration_id target mhr_descriptions.registration_id
-- staging_mhr_description.change_registration_id target mhr_descriptions.change_registration_id
ALTER TABLE staging_mhr_description
  ADD COLUMN status_type VARCHAR(20) NULL,
  ADD COLUMN engineer_date TIMESTAMP NULL,
  ADD COLUMN make VARCHAR(60) NULL,
  ADD COLUMN model VARCHAR(60) NULL,
  ADD COLUMN registration_id INTEGER NULL,
  ADD COLUMN change_registration_id INTEGER NULL
;

-- staging_mhr_location.status_type target mhr_locations.status_type
-- staging_mhr_location.locationType target mhr_locations.location_type
-- staging_mhr_location.tax_certification_date target mhr_locations.tax_certification_date
-- staging_mhr_location.address_id target addresses.id
-- staging_mhr_location.registration_id target mhr_locations.registration_id
-- staging_mhr_location.change_registration_id target mhr_locations.change_registration_id
ALTER TABLE staging_mhr_location
  ADD COLUMN status_type VARCHAR(20) NULL,
  ADD COLUMN location_type VARCHAR(20) NULL,
  ADD COLUMN tax_certification_date TIMESTAMP NULL,
  ADD COLUMN address_id INTEGER NULL,
  ADD COLUMN registration_id INTEGER NULL,
  ADD COLUMN change_registration_id INTEGER NULL
;

-- staging_mhr_owngroup.status_type target mhr_owner_groups.status_type
-- staging_mhr_owngroup.tenancy_type target mhr_owner_groups.tenancy_type
-- staging_mhr_owngroup.interest_numerator target mhr_owner_groups.interest_numerator
-- staging_mhr_owngroup.interest_denominator target mhr_owner_groups.interest_denominator
-- staging_mhr_owngroup.registration_id target mhr_owner_groups.registration_id
-- staging_mhr_owngroup.change_registration_id target mhr_owner_groups.change_registration_id
ALTER TABLE staging_mhr_owngroup
  ADD COLUMN status_type VARCHAR(20) NULL,
  ADD COLUMN tenancy_type VARCHAR(20) NULL,
  ADD COLUMN interest_numerator INTEGER NULL,
  ADD COLUMN interest_denominator INTEGER NULL,
  ADD COLUMN registration_id INTEGER NULL,
  ADD COLUMN change_registration_id INTEGER NULL
;

-- staging_mhr_owner.party_type target mhr_parties.party_type
-- staging_mhr_owner target mhr_parties.business_name, first_name, middle_name, last_name
-- staging_mhr_owner.address_id target addresses.id
-- staging_mhr_owner.registration_id target mhr_parties.registration_id
-- staging_mhr_owner.change_registration_id target mhr_parties.change_registration_id
ALTER TABLE staging_mhr_owner
  ADD COLUMN party_type VARCHAR(20) NULL,
  ADD COLUMN business_name VARCHAR(70) NULL,
  ADD COLUMN first_name VARCHAR(15) NULL,
  ADD COLUMN middle_name VARCHAR(30) NULL,
  ADD COLUMN last_name VARCHAR(25) NULL,
  ADD COLUMN description VARCHAR(70) NULL,
  ADD COLUMN address_id INTEGER NULL,
  ADD COLUMN registration_id INTEGER NULL,
  ADD COLUMN change_registration_id INTEGER NULL
;
