"""Maintain db view account_draft_vw here."""

from alembic_utils.pg_view import PGView


account_draft_vw = PGView(
    schema="public",
    signature="account_draft_vw",
    definition=r"""
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
       (SELECT CASE
          WHEN d.user_id IS NULL OR d.user_id = '' THEN ''
          ELSE COALESCE((
               SELECT CONCAT_WS(' ', NULLIF(TRIM(u.firstname), ''), NULLIF(TRIM(u.lastname), ''))
               FROM users u
               WHERE u.username = d.user_id FETCH FIRST 1 ROWS ONLY
          ), '') END) AS registering_name,
       d.account_id,
       d.id,
       d.registration_number
  FROM drafts d, registration_types rt
 WHERE d.registration_type = rt.registration_type
"""
)