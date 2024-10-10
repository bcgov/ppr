-- Delete all test data created with the scripts in this directory.
DELETE FROM mhr_registration_reports WHERE id >= 200000000;
DELETE FROM mhr_registration_reports WHERE registration_id >= 200000000;
DELETE FROM mhr_manufacturers WHERE id >= 200000000;
DELETE FROM mhr_qualified_suppliers WHERE id >= 200000000;
DELETE FROM mhr_sections WHERE id >= 200000000;
DELETE FROM mhr_descriptions WHERE id >= 200000000;
DELETE FROM mhr_notes WHERE id >= 200000000;
DELETE FROM mhr_locations WHERE id >= 200000000;
DELETE FROM mhr_documents WHERE id >= 200000000;
DELETE FROM mhr_parties WHERE id >= 200000000;
DELETE FROM mhr_owner_groups WHERE id >= 200000000;
DELETE FROM mhr_registrations WHERE id >= 200000000;
DELETE FROM mhr_drafts WHERE id >= 200000000;
DELETE FROM mhr_extra_registrations WHERE id >= 200000000;
DELETE FROM addresses WHERE id BETWEEN 190000000 AND 191000000;
DELETE FROM user_profiles WHERE id BETWEEN 190000000 AND 191000000; 
DELETE FROM users WHERE id BETWEEN 190000000 AND 191000000; 

-- Delete test data end
