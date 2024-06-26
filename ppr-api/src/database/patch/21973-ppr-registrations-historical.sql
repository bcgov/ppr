-- 21973 begin PPR API build 1.2.5 
-- 1. Append _HIS to the account id of all existing registrations expired/discharged more than 30 days.
-- 2. Set the status for all existing registrations expired more than 30 days that have not been discharged
--    to HEX Historical Expired.
-- 3. Cleanup: delete from user_extra_registrations all registration numbers for base registrations that 
--    have been discharged or expired more than 30 days.

INSERT INTO event_tracking_types(event_tracking_type, event_tracking_desc)
     VALUES('REG_HIST_JOB', 'Job to updated account IDs when registrations become historical.');


-- 3638712 PROD 2024-06-24
select max(id)
  from registrations
;

-- 1886177
select max(id)
  from registrations
 where account_id = '0'
;

-- PROD 2024-06-24 827,202
SELECT COUNT(fs.id)
 FROM registrations r, financing_statements fs
 WHERE fs.id = r.financing_id
   AND r.account_id != '0'
   AND r.account_id NOT LIKE '%_HIS'
   AND EXISTS (SELECT r3.id
                 FROM registrations r3
                WHERE r3.financing_id = fs.id
                  AND r3.registration_type_cl = 'DISCHARGE'
                  AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
   AND r.id between 1886178 and 2300000 -- 231025
--   AND r.id between 2300001 and 2800000 -- 259057
--   AND r.id between 2800001 and 3300000 -- 228484
--   AND r.id > 3300000 -- 108635
;

-- PROD 2024-06-24 46,687
SELECT COUNT(fs.id)
 FROM registrations r, financing_statements fs
 WHERE fs.id = r.financing_id
   AND r.account_id != '0'
   AND r.account_id NOT LIKE '%_HIS'   
   AND (fs.expire_date IS NOT NULL AND 
       (fs.expire_date at time zone 'utc') < ((now() at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
;

UPDATE registrations
   SET account_id = account_id || '_HIS'
 WHERE financing_id IN (SELECT fs.id
                          FROM registrations r, financing_statements fs
                          WHERE fs.id = r.financing_id
                            AND r.account_id != '0'
                            AND r.account_id NOT LIKE '%_HIS'
                            AND EXISTS (SELECT r3.id
                                          FROM registrations r3
                                         WHERE r3.financing_id = fs.id
                                           AND r3.registration_type_cl = 'DISCHARGE'
                                           AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
                            AND r.id between 1886178 and 2300000)
;
UPDATE registrations
   SET account_id = account_id || '_HIS'
 WHERE financing_id IN (SELECT fs.id
                          FROM registrations r, financing_statements fs
                          WHERE fs.id = r.financing_id
                            AND r.account_id != '0'
                            AND r.account_id NOT LIKE '%_HIS'
                            AND EXISTS (SELECT r3.id
                                          FROM registrations r3
                                         WHERE r3.financing_id = fs.id
                                           AND r3.registration_type_cl = 'DISCHARGE'
                                           AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
                            AND r.id between 2300001 and 2800000)
;
UPDATE registrations
   SET account_id = account_id || '_HIS'
 WHERE financing_id IN (SELECT fs.id
                          FROM registrations r, financing_statements fs
                          WHERE fs.id = r.financing_id
                            AND r.account_id != '0'
                            AND r.account_id NOT LIKE '%_HIS'
                            AND EXISTS (SELECT r3.id
                                          FROM registrations r3
                                         WHERE r3.financing_id = fs.id
                                           AND r3.registration_type_cl = 'DISCHARGE'
                                           AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
                            AND r.id between 2800001 and 3300000)
;
UPDATE registrations
   SET account_id = account_id || '_HIS'
 WHERE financing_id IN (SELECT fs.id
                          FROM registrations r, financing_statements fs
                          WHERE fs.id = r.financing_id
                            AND r.account_id != '0'
                            AND r.account_id NOT LIKE '%_HIS'
                            AND EXISTS (SELECT r3.id
                                          FROM registrations r3
                                         WHERE r3.financing_id = fs.id
                                           AND r3.registration_type_cl = 'DISCHARGE'
                                           AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
                            AND r.id > 3300000)
;

UPDATE financing_statements
   SET state_type = 'HEX'
 WHERE id IN (SELECT DISTINCT fs.id
                FROM registrations r, financing_statements fs
               WHERE fs.id = r.financing_id
                 AND r.account_id != '0'
                 AND r.account_id NOT LIKE '%_HIS'   
                 AND (fs.expire_date IS NOT NULL AND 
                     (fs.expire_date at time zone 'utc') < ((now() at time zone 'utc') - interval '30 days'))
                 AND NOT EXISTS (SELECT r3.id
                                   FROM registrations r3
                                  WHERE r3.financing_id = fs.id
                                    AND r3.registration_type_cl = 'DISCHARGE'
                                    AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days')))
   AND state_type = 'ACT'
;
UPDATE registrations
   SET account_id = account_id || '_HIS'
 WHERE financing_id IN (SELECT fs.id
                          FROM registrations r, financing_statements fs
                         WHERE fs.id = r.financing_id
                           AND r.account_id != '0'
                           AND r.account_id NOT LIKE '%_HIS'   
                           AND (fs.expire_date IS NOT NULL AND 
                               (fs.expire_date at time zone 'utc') < ((now() at time zone 'utc') - interval '30 days'))
                           AND NOT EXISTS (SELECT r3.id
                                             FROM registrations r3
                                            WHERE r3.financing_id = fs.id
                                              AND r3.registration_type_cl = 'DISCHARGE'
                                              AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days')))
;

SELECT COUNT(uer.id)
  FROM registrations r, user_extra_registrations uer
 WHERE r.registration_number = uer.registration_number
   AND r.account_id LIKE '%_HIS'
;
DELETE 
  FROM user_extra_registrations uer2
 WHERE uer2.id IN (SELECT uer.id
                     FROM registrations r, user_extra_registrations uer
                    WHERE r.registration_number = uer.registration_number
                      AND r.account_id LIKE '%_HIS')
;
-- PROD 462,576 before historical delete
SELECT count(r.id)
  FROM registrations r, user_extra_registrations uer
 WHERE r.registration_number = uer.registration_number
   AND r.account_id = uer.account_id
   AND uer.removed_ind IS NOT NULL
   AND uer.removed_ind = 'Y'
   AND r.id <= 2800000 -- 257132
--   AND r.id > 2800000 -- 205442
;
UPDATE registrations
   SET account_id = registrations.account_id || '_R'
  FROM user_extra_registrations
 WHERE registrations.account_id = user_extra_registrations.account_id
   AND user_extra_registrations.removed_ind IS NOT NULL
   AND user_extra_registrations.removed_ind = 'Y'
   AND registrations.financing_id = (SELECT DISTINCT fs.id
                                       FROM financing_statements fs, registrations r
                                      WHERE r.financing_id = fs.id
                                        AND r.account_id = user_extra_registrations.account_id
                                        AND r.registration_number = user_extra_registrations.registration_number)
;


-- 5797 teranet +1000000 8.9s
-- 5838 ESC 243696 3.09s
-- Testing PROD before/after update.
SELECT * FROM 
(
SELECT document_number, create_ts, registration_type, registration_type_cl, registration_desc, base_reg_num, draft_type,
       last_update_ts, client_reference_id, registering_party, secured_party, registering_name, account_id
  FROM account_draft_vw adv
 WHERE account_id = '5797'
   AND NOT EXISTS (SELECT r.draft_id FROM registrations r WHERE r.account_id = adv.account_id AND r.draft_id = adv.id)
   AND NOT EXISTS (SELECT uer.id
                     FROM user_extra_registrations uer
                    WHERE uer.registration_number = adv.registration_number
                      AND uer.account_id = adv.account_id
                      AND uer.removed_ind = 'Y')
) AS q WHERE account_id = '5797'
 ORDER BY create_ts DESC
 FETCH FIRST 1000 ROWS ONLY
;
-- 5797 teranet +1000000 19.9s
-- 5838 ESC 243696 3.6s
SELECT * FROM 
(
    SELECT registration_number, registration_ts, registration_type, registration_type_cl, account_id,
           registration_desc, base_reg_number, state, expire_days, last_update_ts, registering_party,
           secured_party, client_reference_id, registering_name, orig_account_id, pending_count, vehicle_count
      FROM account_registration_vw arv
     WHERE arv.account_id = '5797'
       AND arv.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')
) AS q 
 ORDER BY registration_ts DESC
 LIMIT 100 OFFSET 1
; 

-- 21973 end PPR API build 1.2.5 
