-- 14527 view to check if there is an outstanding PPR lien on a manufactured home searching by MHR number.
CREATE OR REPLACE VIEW public.mhr_lien_check_vw AS
SELECT sc.mhr_number, r.registration_type, r.registration_ts AS base_registration_ts,
       r.registration_number AS base_registration_num,
       cc.id AS client_code_id, cc.name AS secured_party_name
  FROM registrations r, financing_statements fs, serial_collateral sc, parties p, client_codes cc
 WHERE r.financing_id = fs.id
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN')
   AND r.registration_type IN ('SG', 'SA', 'LT', 'FR', 'MH')
   AND (fs.expire_date IS NULL OR fs.expire_date > ((now() at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id 
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
   AND sc.financing_id = fs.id
   AND sc.registration_id_end IS NULL
   AND sc.mhr_number IS NOT NULL
   AND sc.mhr_number != 'NR'
   AND p.financing_id = fs.id
   AND p.party_type = 'SP'
   AND p.registration_id_end IS NULL
   AND p.branch_id IS NOT NULL
   AND p.branch_id = cc.id
   AND (cc.name like 'HER MAJESTY%' OR cc.name like '%TAX DEFERME%')
;
