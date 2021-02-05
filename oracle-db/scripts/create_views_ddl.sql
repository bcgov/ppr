CREATE OR REPLACE VIEW SEARCH_BY_REG_NUM_VW AS
SELECT r.registration_type_cd,
       fs.state_type_cd,
       'EXACT' AS match_type,
       r2.registration_number as registration_num,
       r.registration_number AS base_registration_num,
       r.registration_ts AS base_registration_ts
  FROM registration r, financing_statement fs, registration r2
 WHERE r2.financing_id = r.financing_id
   AND r.financing_id = fs.financing_id
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN')
   AND r.base_reg_number IS NULL
   AND (fs.expire_date IS NULL OR fs.expire_date > (sysdate - 30))
   AND NOT EXISTS (SELECT r3.registration_id
                     FROM registration r3
                    WHERE r3.financing_id = fs.financing_id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < (sysdate - 30))
WITH READ ONLY
;

CREATE OR REPLACE VIEW SEARCH_BY_MHR_NUM_VW AS
SELECT r.registration_type_cd,
       fs.state_type_cd,
       'EXACT' AS match_type,
       r.registration_number AS base_registration_num,
       r.registration_ts AS base_registration_ts,
       sc.serial_type_cd,
       sc.serial_number,
       sc.year,
       sc.make,
       sc.model,
       sc.mhr_number
  FROM registration r, financing_statement fs, serial_collateral sc
 WHERE r.financing_id = fs.financing_id
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN')
   AND r.base_reg_number IS NULL
   AND (fs.expire_date IS NULL OR fs.expire_date > (sysdate - 30))
   AND NOT EXISTS (SELECT r3.registration_id
                     FROM registration r3
                    WHERE r3.financing_id = fs.financing_id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < (sysdate - 30))
   AND sc.financing_id = fs.financing_id
   AND sc.serial_type_cd = 'MH'
   AND sc.registration_id_end IS NULL
WITH READ ONLY
;


CREATE OR REPLACE VIEW SEARCH_BY_SERIAL_NUM_VW AS
SELECT r.registration_type_cd,
       fs.state_type_cd,
       r.registration_number AS base_registration_num,
       r.registration_ts AS base_registration_ts,
       sc.serial_type_cd,
       sc.serial_number,
       sc.year,
       sc.make,
       sc.model,
       sc.srch_vin
  FROM registration r, financing_statement fs, serial_collateral sc
 WHERE r.financing_id = fs.financing_id
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN')
   AND r.base_reg_number IS NULL
   AND (fs.expire_date IS NULL OR fs.expire_date > (sysdate - 30))
   AND NOT EXISTS (SELECT r3.registration_id
                     FROM registration r3
                    WHERE r3.financing_id = fs.financing_id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < (sysdate - 30))
   AND sc.financing_id = fs.financing_id
   AND sc.serial_type_cd NOT IN ('AC', 'AF')
   AND sc.registration_id_end IS NULL
WITH READ ONLY
;

CREATE OR REPLACE VIEW SEARCH_BY_AIRCRAFT_DOT_VW AS
SELECT r.registration_type_cd,
       fs.state_type_cd,
       r.registration_number AS base_registration_num,
       r.registration_ts AS base_registration_ts,
       sc.serial_type_cd,
       sc.serial_number,
       sc.year,
       sc.make,
       sc.model
  FROM registration r, financing_statement fs, serial_collateral sc
 WHERE r.financing_id = fs.financing_id
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN')
   AND r.base_reg_number IS NULL
   AND (fs.expire_date IS NULL OR fs.expire_date > (sysdate - 30))
   AND NOT EXISTS (SELECT r3.registration_id
                     FROM registration r3
                    WHERE r3.financing_id = fs.financing_id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < (sysdate - 30))
   AND sc.financing_id = fs.financing_id
   AND sc.serial_type_cd IN ('AC', 'AF')
   AND sc.registration_id_end IS NULL
WITH READ ONLY
;
