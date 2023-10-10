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

gcloud sql import csv ppr-sandbox-pgdb gs://mhr-db2-sandbox/export-mhr-registrations-prod.csv \
--database=ppr --table=temp_mhr_registrations \
--user=user4ca \
--quote="22" \
--fields-terminated-by="2C"

gcloud sql import csv ppr-sandbox-pgdb gs://mhr-db2-sandbox/export-mhr-documents-prod.csv \
--database=ppr --table=temp_mhr_documents \
--user=user4ca \
--quote="22" \
--fields-terminated-by="2C"

gcloud sql import csv ppr-sandbox-pgdb gs://mhr-db2-sandbox/export-mhr-locations-prod.csv \
--database=ppr --table=temp_mhr_locations \
--user=user4ca \
--quote="22" \
--fields-terminated-by="2C"

gcloud sql import csv ppr-sandbox-pgdb gs://mhr-db2-sandbox/export-mhr-notes-prod.csv \
--database=ppr --table=temp_mhr_notes \
--user=user4ca \
--quote="22" \
--fields-terminated-by="2C"

gcloud sql import csv ppr-sandbox-pgdb gs://mhr-db2-sandbox/export-mhr-owner-groups-prod.csv \
--database=ppr --table=temp_mhr_owner_groups \
--user=user4ca \
--quote="22" \
--fields-terminated-by="2C"

gcloud sql import csv ppr-sandbox-pgdb gs://mhr-db2-sandbox/export-mhr-parties-prod.csv \
--database=ppr --table=temp_mhr_parties \
--user=user4ca \
--quote="22" \
--fields-terminated-by="2C"

gcloud sql import csv ppr-sandbox-pgdb gs://mhr-db2-sandbox/export-mhr-manufacturers-prod.csv \
--database=ppr --table=temp_mhr_manufacturers \
--user=user4ca \
--quote="22" \
--fields-terminated-by="2C"

gcloud sql import csv ppr-sandbox-pgdb gs://mhr-db2-sandbox/export-mhr-sections-prod.csv \
--database=ppr --table=temp_mhr_sections \
--user=user4ca \
--quote="22" \
--fields-terminated-by="2C"

gcloud sql import csv ppr-sandbox-pgdb gs://mhr-db2-sandbox/export-mhr-descriptions-prod.csv \
--database=ppr --table=temp_mhr_descriptions \
--user=user4ca \
--quote="22" \
--fields-terminated-by="2C"

gcloud sql import csv ppr-sandbox-pgdb gs://mhr-db2-sandbox/export-mhr-party-addresses-prod.csv \
--database=ppr --table=temp_addresses \
--user=user4ca \
--quote="22" \
--fields-terminated-by="2C"

gcloud sql import csv ppr-sandbox-pgdb gs://mhr-db2-sandbox/export-mhr-location-addresses-prod.csv \
--database=ppr --table=temp_addresses \
--user=user4ca \
--quote="22" \
--fields-terminated-by="2C"

-- insert temp_mhr_registration_reports replace & with chr(38)
*/