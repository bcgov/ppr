-- 19494 PPR 1.2.1 Improve query performance for account drafts and registrations
CREATE INDEX ix_drafts_registration_type ON public.drafts USING btree (registration_type);
CREATE INDEX ix_registrations_registration_type ON public.registrations USING btree (registration_type);
CREATE INDEX ix_registrations_registration_type_cl ON public.registrations USING btree (registration_type_cl);
CREATE INDEX ix_parties_party_type ON public.parties USING btree (party_type);
CREATE INDEX ix_serial_collateral_serial_type ON public.serial_collateral USING btree (serial_type);

CREATE OR REPLACE VIEW public.account_draft_vw AS
SELECT d.document_number,
       d.create_ts,
       d.registration_type,
       d.registration_type_cl,
       rt.registration_desc,
       CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') THEN ''
            ELSE d.registration_number END base_reg_num,
       d.draft ->> 'type' AS draft_type,
       CASE WHEN d.update_ts IS NOT NULL THEN d.update_ts ELSE d.create_ts END last_update_ts,
       CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') THEN
                 d.draft -> 'financingStatement' ->> 'clientReferenceId'
            WHEN d.registration_type_cl = 'AMENDMENT' THEN d.draft -> 'amendmentStatement' ->> 'clientReferenceId'
            WHEN d.registration_type_cl = 'CHANGE' THEN d.draft -> 'changeStatement' ->> 'clientReferenceId'
            ELSE '' END client_reference_id,
       CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') AND
                 d.draft -> 'financingStatement' -> 'registeringParty' IS NOT NULL THEN
                 CASE WHEN d.draft -> 'financingStatement' -> 'registeringParty' -> 'businessName' IS NOT NULL THEN
                           d.draft -> 'financingStatement' -> 'registeringParty' ->> 'businessName'
                      WHEN d.draft -> 'financingStatement' -> 'registeringParty' ->> 'personName' IS NOT NULL THEN
                      concat(d.draft -> 'financingStatement' -> 'registeringParty' -> 'personName' ->> 'first', ' ',
                             d.draft -> 'financingStatement' -> 'registeringParty' -> 'personName' ->> 'last')
                 END
            WHEN d.registration_type_cl = 'AMENDMENT' AND
                 (d.draft -> 'amendmentStatement' -> 'registeringParty') IS NOT NULL THEN
                 CASE WHEN d.draft -> 'amendmentStatement' -> 'registeringParty' -> 'businessName' IS NOT NULL THEN
                           d.draft -> 'amendmentStatement' -> 'registeringParty' ->> 'businessName'
                      WHEN d.draft -> 'amendmentStatement' -> 'registeringParty' -> 'personName' IS NOT NULL THEN
                        concat(d.draft -> 'amendmentStatement' -> 'registeringParty' -> 'personName' ->> 'first', ' ',
                               d.draft -> 'amendmentStatement' -> 'registeringParty' -> 'personName' ->> 'last')
                 END
            ELSE '' END registering_party,
      CASE WHEN d.registration_type_cl IN ('PPSALIEN', 'CROWNLIEN', 'MISCLIEN') AND
                 d.draft -> 'financingStatement' -> 'securedParties' IS NOT NULL THEN
                (SELECT string_agg((CASE WHEN (sp -> 'businessName') IS NOT NULL THEN
                                             (sp ->> 'businessName')
                                         WHEN sp -> 'personName' IS NOT NULL THEN
                                            concat((sp -> 'personName' ->> 'first'), ' ',
                                                   (sp -> 'personName' ->> 'last'))
                                         END),
                                   ',')
                   FROM json_array_elements(d.draft -> 'financingStatement' -> 'securedParties') sp)
          WHEN d.registration_type_cl = 'AMENDMENT' AND
                 d.draft -> 'amendmentStatement' -> 'securedParties' IS NOT NULL THEN
                (SELECT string_agg((CASE WHEN (sp2 -> 'businessName') IS NOT NULL THEN
                                             (sp2 ->> 'businessName')
                                         WHEN sp2 -> 'personName' IS NOT NULL THEN
                                            concat((sp2 -> 'personName' ->> 'first'), ' ',
                                                   (sp2 -> 'personName' ->> 'last'))
                                         END),
                                   ',')
                   FROM json_array_elements(d.draft -> 'amendmentStatement' -> 'securedParties') sp2)
            ELSE ' ' END secured_party,
       (SELECT CASE WHEN d.user_id IS NULL THEN ''
                    ELSE (SELECT u.firstname || ' ' || u.lastname
                            FROM users u
                           WHERE u.username = d.user_id FETCH FIRST 1 ROWS ONLY) END) AS registering_name,
       d.account_id,
       d.id,
       d.registration_number
  FROM drafts d, registration_types rt
 WHERE d.registration_type = rt.registration_type
;

CREATE OR REPLACE VIEW public.account_registration_count_vw AS
SELECT r.id, r.account_id, r.registration_type_cl
  FROM registrations r, registration_types rt, financing_statements fs
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
UNION (
SELECT r.id, uer.account_id, r.registration_type_cl
  FROM registrations r, registration_types rt, financing_statements fs, user_extra_registrations uer
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
)
;


