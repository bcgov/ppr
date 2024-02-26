-- 19902 archive to new tables all registration data for registrations expired/discharged more than 180 days.
-- Archve table naming: archive_{original_table_name}
-- Archive tables and delete order:
-- Table Name                            Source                     Record Count Before   Record Count After
-- archive_verification_reports          verification_reports
-- archive_mail_reports                  mail_reports
-- archive_serial_collateral             serial_collateral
-- archive_general_collateral            general_collateral
-- archive_parties                       parties
-- archive_trust_indentures              trust_indentures
-- archive_court_orders                  court_orders
-- archive_registrations                 registrations
-- archive_financing_statements          financing_statements
-- archive_drafts                        drafts
-- archive_addresses                     addresses
-- archive_user_extra_registrations      user_extra_registrations
--
-- Script run date
-- DEV:     2024-02-26
-- TEST:    2024-02-27
-- SANDBOX: 2024-02-27
-- PROD:    

-- Count registrations to be archived by expired, then discharged
-- Expired more than 6 months ago. 
SELECT count(r.id) 
  FROM registrations r, financing_statements fs
 WHERE fs.id = r.financing_id
   AND fs.id IN (SELECT fs2.id
                   FROM financing_statements fs2, registrations r2
                  WHERE fs2.id = r2.financing_id
                    AND r2.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN'))
   AND fs.expire_date IS NOT NULL 
   AND fs.expire_date < ((now() at time zone 'utc') - interval '180 days')
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))                      
;
-- Discharged more than 6 months ago. 
SELECT count(r.id) 
  FROM registrations r, financing_statements fs
 WHERE fs.id = r.financing_id
   AND fs.id IN (SELECT fs2.id
                   FROM financing_statements fs2, registrations r2
                  WHERE fs2.id = r2.financing_id
                    AND r2.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN'))
   AND (fs.expire_date IS NULL OR fs.expire_date > ((now() at time zone 'utc') - interval '30 days'))
   AND EXISTS (SELECT r3.id
                 FROM registrations r3
                WHERE r3.financing_id = fs.id
                  AND r3.registration_type_cl = 'DISCHARGE'
                  AND r3.registration_ts < ((now() at time zone 'utc') - interval '180 days'))                      
;

-- Financing statements and registrations first, then key off those table ID's for the remaining table copies.
SELECT *
  INTO TABLE archive_financing_statements
  FROM financing_statements
 WHERE id in 
(
SELECT fs.id
  FROM registrations r, financing_statements fs
 WHERE fs.id = r.financing_id
   AND fs.id IN (SELECT fs2.id
                   FROM financing_statements fs2, registrations r2
                  WHERE fs2.id = r2.financing_id
                    AND r2.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN'))
   AND fs.expire_date IS NOT NULL 
   AND fs.expire_date < ((now() at time zone 'utc') - interval '180 days')
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))                      
);
SELECT COUNT(id)
  FROM archive_financing_statements
;
INSERT INTO archive_financing_statements
SELECT fs.*
  FROM registrations r, financing_statements fs
 WHERE fs.id = r.financing_id
   AND fs.id IN (SELECT fs2.id
                   FROM financing_statements fs2, registrations r2
                  WHERE fs2.id = r2.financing_id
                    AND r2.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN'))
   AND (fs.expire_date IS NULL OR fs.expire_date > ((now() at time zone 'utc') - interval '30 days'))
   AND EXISTS (SELECT r3.id
                 FROM registrations r3
                WHERE r3.financing_id = fs.id
                  AND r3.registration_type_cl = 'DISCHARGE'
                  AND r3.registration_ts < ((now() at time zone 'utc') - interval '180 days'))                      
;
SELECT COUNT(id) FROM archive_financing_statements; -- 

SELECT *
  INTO TABLE archive_registrations
  FROM registrations
 WHERE id in 
(
SELECT r.id
  FROM registrations r, financing_statements fs
 WHERE fs.id = r.financing_id
   AND fs.id IN (SELECT fs2.id
                   FROM financing_statements fs2, registrations r2
                  WHERE fs2.id = r2.financing_id
                    AND r2.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN'))
   AND fs.expire_date IS NOT NULL 
   AND fs.expire_date < ((now() at time zone 'utc') - interval '180 days')
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))                      
);
SELECT COUNT(id)
  FROM archive_registrations
;
INSERT INTO archive_registrations
SELECT r.*
  FROM registrations r, financing_statements fs
 WHERE fs.id = r.financing_id
   AND fs.id IN (SELECT fs2.id
                   FROM financing_statements fs2, registrations r2
                  WHERE fs2.id = r2.financing_id
                    AND r2.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN'))
   AND (fs.expire_date IS NULL OR fs.expire_date > ((now() at time zone 'utc') - interval '30 days'))
   AND EXISTS (SELECT r3.id
                 FROM registrations r3
                WHERE r3.financing_id = fs.id
                  AND r3.registration_type_cl = 'DISCHARGE'
                  AND r3.registration_ts < ((now() at time zone 'utc') - interval '180 days'))                      
;
SELECT COUNT(id) FROM archive_registrations --
;

SELECT *
  INTO TABLE archive_drafts
  FROM drafts
 WHERE id IN (SELECT draft_id FROM archive_registrations);
SELECT COUNT(id) FROM archive_drafts; -- 

SELECT *
  INTO TABLE archive_user_extra_registrations
  FROM user_extra_registrations
 WHERE registration_number IN (SELECT registration_number FROM archive_registrations);
SELECT COUNT(id) FROM archive_user_extra_registrations; -- 

SELECT *
  INTO TABLE archive_court_orders
  FROM court_orders
 WHERE registration_id IN (SELECT id FROM archive_registrations);
SELECT COUNT(id) FROM archive_court_orders; -- 

SELECT *
  INTO TABLE archive_trust_indentures
  FROM trust_indentures
 WHERE registration_id IN (SELECT id FROM archive_registrations);
SELECT COUNT(id) FROM archive_trust_indentures; -- 

SELECT *
  INTO TABLE archive_parties
  FROM parties
 WHERE financing_id IN (SELECT id FROM archive_financing_statements);
SELECT COUNT(id) FROM archive_parties; -- 

SELECT *
  INTO TABLE archive_addresses
  FROM addresses
 WHERE id IN (SELECT address_id FROM archive_parties);
SELECT COUNT(id) FROM archive_addresses; -- 

SELECT *
  INTO TABLE archive_general_collateral
  FROM general_collateral
 WHERE financing_id IN (SELECT id FROM archive_financing_statements);
SELECT COUNT(id) FROM archive_general_collateral; -- 

SELECT *
  INTO TABLE archive_serial_collateral
  FROM serial_collateral
 WHERE financing_id IN (SELECT id FROM archive_financing_statements);
SELECT COUNT(id) FROM archive_serial_collateral; -- 

SELECT *
  INTO TABLE archive_mail_reports
  FROM mail_reports
 WHERE registration_id IN (SELECT id FROM archive_registrations);
SELECT COUNT(id) FROM archive_mail_reports; -- 

SELECT *
  INTO TABLE archive_verification_reports
  FROM verification_reports
 WHERE registration_id IN (SELECT id FROM archive_registrations);
SELECT COUNT(id) FROM archive_verification_reports; -- 


-- totals before archiving
SELECT COUNT(id) FROM registrations; --
SELECT COUNT(id) FROM financing_statements; --
SELECT COUNT(id) FROM drafts; --
SELECT COUNT(id) FROM addresses; --
SELECT COUNT(id) FROM user_extra_registrations; --
SELECT COUNT(id) FROM court_orders; --
SELECT COUNT(id) FROM trust_indentures; --
SELECT COUNT(id) FROM parties; --
SELECT COUNT(id) FROM general_collateral; --
SELECT COUNT(id) FROM serial_collateral; --
SELECT COUNT(id) FROM mail_reports; --
SELECT COUNT(id) FROM verification_reports; --
SELECT COUNT(id) FROM previous_financing_statements; --

DELETE FROM verification_reports WHERE id IN (SELECT id FROM archive_verification_reports);
DELETE FROM mail_reports WHERE id IN (SELECT id FROM archive_mail_reports);
DELETE FROM serial_collateral WHERE id IN (SELECT id FROM archive_serial_collateral);
DELETE FROM general_collateral WHERE id IN (SELECT id FROM archive_general_collateral);
DELETE FROM parties WHERE id IN (SELECT id FROM archive_parties);
DELETE FROM trust_indentures WHERE id IN (SELECT id FROM archive_trust_indentures);
DELETE FROM court_orders WHERE id IN (SELECT id FROM archive_court_orders);
DELETE FROM registrations WHERE id IN (SELECT id FROM archive_registrations);
DELETE FROM previous_financing_statements WHERE financing_id IN (SELECT id FROM archive_financing_statements);
DELETE FROM financing_statements WHERE id IN (SELECT id FROM archive_financing_statements);
DELETE FROM drafts WHERE id IN (SELECT id FROM archive_drafts);
DELETE FROM addresses WHERE id IN (SELECT id FROM archive_addresses);
DELETE FROM user_extra_registrations WHERE id IN (SELECT id FROM archive_user_extra_registrations);

-- Optionally rebuild indexes (PROD in a change window)
REINDEX TABLE registrations;
REINDEX TABLE financing_statements;
REINDEX TABLE drafts;
REINDEX TABLE addresses;
REINDEX TABLE user_extra_registrations;
REINDEX TABLE court_orders;
REINDEX TABLE trust_indentures;
REINDEX TABLE parties;
REINDEX TABLE general_collateral;
REINDEX TABLE serial_collateral;
REINDEX TABLE mail_reports;
REINDEX TABLE verification_reports;

-- totals after archiving
SELECT COUNT(id) FROM registrations; --
SELECT COUNT(id) FROM financing_statements; --
SELECT COUNT(id) FROM drafts; --
SELECT COUNT(id) FROM addresses; --
SELECT COUNT(id) FROM user_extra_registrations; --
SELECT COUNT(id) FROM court_orders; --
SELECT COUNT(id) FROM trust_indentures; --
SELECT COUNT(id) FROM parties; --
SELECT COUNT(id) FROM general_collateral; --
SELECT COUNT(id) FROM serial_collateral; --
SELECT COUNT(id) FROM mail_reports; --
SELECT COUNT(id) FROM verification_reports; --
SELECT COUNT(id) FROM previous_financing_statements; --
