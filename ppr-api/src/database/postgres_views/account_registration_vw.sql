-- 10903 2022-02-04 Run this manually for now
--DROP VIEW public.account_registration_vw;
CREATE OR REPLACE VIEW public.account_registration_vw AS
WITH q AS (
  SELECT (TO_TIMESTAMP(TO_CHAR(current_date, 'YYYY-MM-DD') || ' 23:59:59', 'YYYY-MM-DD HH24:MI:SS') at time zone 'utc')
      AS current_expire_ts
)
SELECT r.registration_number, r.registration_ts, r.registration_type, r.registration_type_cl, r.account_id,
       rt.registration_desc, r.base_reg_number, r.id AS registration_id, fs.id AS financing_id,
       CASE WHEN fs.state_type = 'ACT' AND fs.expire_date IS NOT NULL AND
                 (fs.expire_date at time zone 'utc') < (now() at time zone 'utc') THEN 'HEX'
            ELSE fs.state_type END AS state,
       CASE WHEN fs.life = 99 THEN -99
            ELSE CAST(EXTRACT(day from ((fs.expire_date at time zone 'utc') - current_expire_ts)) AS INT) END expire_days,
       (SELECT MAX(r2.registration_ts)
          FROM registrations r2
         WHERE r2.financing_id = r.financing_id) AS last_update_ts,
       (SELECT CASE WHEN p.business_name IS NOT NULL THEN p.business_name
                    WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)
                    ELSE p.first_name || ' ' || p.last_name END
          FROM parties p
         WHERE p.registration_id = r.id
           AND p.party_type = 'RG') AS registering_party,
       (SELECT string_agg((CASE WHEN p.business_name IS NOT NULL THEN p.business_name
                                WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)
                                ELSE p.first_name || ' ' || p.last_name END), ', ')
          FROM parties p
         WHERE p.financing_id = fs.id
           AND p.registration_id_end IS NULL
           AND p.party_type = 'SP') AS secured_party,
       r.client_reference_id,
       (SELECT CASE WHEN r.user_id IS NULL THEN ''
                    ELSE (SELECT u.firstname || ' ' || u.lastname
                            FROM users u
                           WHERE u.username = r.user_id) END) AS registering_name,
       r.account_id AS orig_account_id,
       r2.account_id AS base_account_id
 FROM registrations r, registration_types rt, financing_statements fs, registrations r2, q
 WHERE r.registration_type = rt.registration_type
   AND fs.id = r.financing_id
   AND (fs.expire_date IS NULL OR (fs.expire_date at time zone 'utc') > ((now() at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
  AND NOT EXISTS (SELECT r2.financing_id
                    FROM user_extra_registrations uer, registrations r2
                   WHERE uer.registration_number = r2.registration_number
                     AND r2.financing_id = r.financing_id
                     AND uer.removed_ind = 'Y')
  AND r2.financing_id = fs.id
  AND r2.financing_id = r.financing_id
  AND r2.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')
UNION (
SELECT r.registration_number, r.registration_ts, r.registration_type, r.registration_type_cl, uer.account_id,
       rt.registration_desc, r.base_reg_number, r.id AS registration_id, fs.id AS financing_id,
       CASE WHEN fs.state_type = 'ACT' AND fs.expire_date IS NOT NULL AND
                 (fs.expire_date at time zone 'utc') < (now() at time zone 'utc') THEN 'HEX'
            ELSE fs.state_type END AS state,
       CASE WHEN fs.life = 99 THEN -99
            ELSE CAST(EXTRACT(day from ((fs.expire_date at time zone 'utc') - current_expire_ts)) AS INT) END expire_days,
       (SELECT MAX(r2.registration_ts)
          FROM registrations r2
         WHERE r2.financing_id = r.financing_id) AS last_update_ts,
       (SELECT CASE WHEN p.business_name IS NOT NULL THEN p.business_name
                    WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)
                    ELSE p.first_name || ' ' || p.last_name END
          FROM parties p
         WHERE p.registration_id = r.id
           AND p.party_type = 'RG') AS registering_party,
       (SELECT string_agg((CASE WHEN p.business_name IS NOT NULL THEN p.business_name
                                WHEN p.branch_id IS NOT NULL THEN (SELECT name FROM client_codes WHERE id = p.branch_id)
                                ELSE p.first_name || ' ' || p.last_name END), ', ')
          FROM parties p
         WHERE p.financing_id = fs.id
           AND p.registration_id_end IS NULL
           AND p.party_type = 'SP') AS secured_party,
       r.client_reference_id,
       (SELECT CASE WHEN r.user_id IS NULL THEN ''
                    ELSE (SELECT u.firstname || ' ' || u.lastname
                            FROM users u
                           WHERE u.username = r.user_id) END) AS registering_name,
       r.account_id AS orig_account_id,
       r2.account_id AS base_account_id
  FROM registrations r, registration_types rt, financing_statements fs, user_extra_registrations uer, registrations r2, q
 WHERE r.registration_type = rt.registration_type
   AND fs.id = r.financing_id
   AND (fs.expire_date IS NULL OR (fs.expire_date at time zone 'utc') > ((now() at time zone 'utc') - interval '30 days'))
   AND (r.registration_number = uer.registration_number OR r.base_reg_number = uer.registration_number)
   AND uer.removed_ind IS NULL
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days'))
  AND r2.financing_id = fs.id
  AND r2.financing_id = r.financing_id
  AND r2.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')
)
;
