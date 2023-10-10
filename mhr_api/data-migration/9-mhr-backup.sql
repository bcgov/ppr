-- Backup all mhr* tables as temp_mhr* tables:
-- Requires that the API gateway MHR api proxy is set to unavailable.

/*
DROP TABLE temp_mhr_registrations;
DROP TABLE temp_mhr_documents;
DROP TABLE temp_mhr_descriptions;
DROP TABLE temp_mhr_locations;
DROP TABLE temp_mhr_notes;
DROP TABLE temp_mhr_owner_groups;
DROP TABLE temp_mhr_parties;
DROP TABLE temp_mhr_manufacturers;
DROP TABLE temp_mhr_registration_reports;
DROP TABLE temp_mhr_sections;
*/
SELECT *
  INTO TABLE temp_mhr_registrations
  FROM mhr_registrations;
SELECT *
  INTO TABLE temp_mhr_documents
  FROM mhr_documents;
SELECT *
  INTO TABLE temp_mhr_descriptions
  FROM mhr_descriptions;
SELECT *
  INTO TABLE temp_mhr_locations
  FROM mhr_locations;
SELECT *
  INTO TABLE temp_mhr_notes
  FROM mhr_notes;
SELECT *
  INTO TABLE temp_mhr_owner_groups
  FROM mhr_owner_groups;
SELECT *
  INTO TABLE temp_mhr_parties
  FROM mhr_parties;
SELECT *
  INTO TABLE temp_mhr_manufacturers
  FROM mhr_manufacturers;
SELECT *
  INTO TABLE temp_mhr_registration_reports
  FROM mhr_registration_reports;
SELECT *
  INTO TABLE temp_mhr_sections
  FROM mhr_sections;

/*
Non-PROD env loading prod data.
TRUNCATE TABLE temp_mhr_registrations;
TRUNCATE TABLE temp_mhr_documents;
TRUNCATE TABLE temp_mhr_descriptions;
TRUNCATE TABLE temp_mhr_locations;
TRUNCATE TABLE temp_mhr_notes;
TRUNCATE TABLE temp_mhr_owner_groups;
TRUNCATE TABLE temp_mhr_parties;
TRUNCATE TABLE temp_mhr_manufacturers;
TRUNCATE TABLE temp_mhr_registration_reports;
TRUNCATE TABLE temp_mhr_sections;
TRUNCATE TABLE temp_addresses;

select *
  from addresses
where id in (select address_id from mhr_parties)
;
select *
  from addresses
where id in (select address_id from mhr_locations)
;
*/