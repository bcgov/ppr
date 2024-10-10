-- Optionally run this script if either regenerating the staging tables and staging related objects 
-- or cleaning up post data migration.
-- Drop tables, sequences, and functions
-- If reusing address range, capture the current address range before droping the staging tables.
select min(id), max(id)
  from staging_mhr_addresses
;

DROP FUNCTION mhr_conversion_reg_id;
DROP FUNCTION mhr_conversion_registration_all;
DROP FUNCTION mhr_conversion_registration;
DROP FUNCTION mhr_conversion_location;
DROP FUNCTION mhr_conversion_description;
DROP FUNCTION mhr_conversion_owngroup;
DROP FUNCTION mhr_conversion_owner;
DROP FUNCTION mhr_conversion_note;
DROP FUNCTION mhr_conversion_address_location;
DROP FUNCTION mhr_conversion_address_note;
DROP FUNCTION mhr_conversion_address_owner;
DROP FUNCTION mhr_conversion_address_document;
DROP FUNCTION mhr_conversion_address;
DROP FUNCTION mhr_conversion_address_pcode;
DROP FUNCTION mhr_conversion_address_remove;
DROP FUNCTION mhr_conversion_address_country_pcode;
DROP FUNCTION mhr_conversion_address_country;
DROP FUNCTION mhr_conversion_is_bc_city;
DROP FUNCTION mhr_conversion_address_region;
DROP FUNCTION mhr_conversion_individual_suffix;
DROP FUNCTION mhr_conversion_individual_middle;
DROP FUNCTION mhr_conversion_individual_first;
DROP FUNCTION mhr_conversion_individual_last;
DROP FUNCTION mhr_conversion_is_individual;
DROP FUNCTION mhr_conversion_interest_fraction;
DROP FUNCTION mhr_conversion_make_model;
DROP FUNCTION mhr_restore_manufacturer;

DROP TABLE public.staging_mhr_location;
DROP TABLE public.staging_mhr_note;
DROP TABLE public.staging_mhr_owngroup;
DROP TABLE public.staging_mhr_owner;
DROP TABLE public.staging_mhr_description;
DROP TABLE public.staging_mhr_document;
DROP TABLE public.staging_mhr_manuhome;
--DROP TABLE public.staging_mhr_doc_types;

DROP SEQUENCE staging_mhr_address_id_seq;
DROP TABLE staging_mhr_addresses;
DROP SEQUENCE staging_mhr_reg_id_seq;
