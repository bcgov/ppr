-- registration summary view.
CREATE OR REPLACE VIEW public.mhr_account_reg_vw AS
SELECT r.mhr_number, r.status_type, r.registration_ts,
       (SELECT CASE WHEN p.business_name IS NOT NULL THEN p.business_name
                    WHEN p.middle_name IS NOT NULL THEN p.first_name || ' ' || p.middle_name || ' ' || p.last_name
                    ELSE p.first_name || ' ' || p.last_name
               END
          FROM mhr_parties p
         WHERE p.registration_id = r.id 
           AND p.party_type = 'SUBMITTING') AS submitting_name,
       r.client_reference_id,
       r.registration_type,       
       (SELECT string_agg((CASE WHEN p.business_name IS NOT NULL THEN p.business_name
                                WHEN p.middle_name IS NOT NULL THEN p.first_name || ' ' || p.middle_name || ' ' || p.last_name
                                ELSE p.first_name || ' ' || p.last_name END), '\n')
          FROM mhr_registrations ro, mhr_owner_groups og, mhr_parties p
         WHERE ro.mhr_number = r.mhr_number 
           AND ro.id = og.registration_id
           AND og.status_type = 'ACTIVE'
           AND og.registration_id = p.registration_id
           AND og.id = p.owner_group_id) AS owner_names,       
       (SELECT CASE WHEN r.user_id IS NULL THEN ''
                    ELSE (SELECT u.firstname || ' ' || u.lastname
                            FROM users u
                           WHERE u.username = r.user_id FETCH FIRST 1 ROWS ONLY) END) AS registering_name,
       d.document_id,
       d.document_registration_number,
       (SELECT d2.document_type
          FROM mhr_documents d2
         WHERE d2.id = (SELECT MAX(d3.id)
                          FROM mhr_documents d3, mhr_registrations r2
                         WHERE r2.id = d3.registration_id
                          AND r2.mhr_number = r.mhr_number)) AS last_doc_type,
       (SELECT n.status_type
          FROM mhr_notes n
         WHERE n.registration_id = r.id) AS note_status,
       (SELECT n.expiry_date
          FROM mhr_notes n
         WHERE n.registration_id = r.id) AS note_expiry,
       (CASE
          WHEN d.document_type in ('NCAN', 'NRED') THEN
            (SELECT n.document_type
               FROM mhr_notes n
              WHERE n.status_type != 'ACTIVE'
                AND n.change_registration_id = r.id
                AND n.document_type != 'CAUC'
                AND n.document_type != 'CAUE'
             FETCH FIRST 1 ROWS ONLY)
          ELSE NULL
        END) AS cancel_doc_type,
       (SELECT n.document_type
          FROM mhr_notes n, mhr_registrations r2
         WHERE r2.mhr_number = r.mhr_number
           AND r2.id = n.registration_id
           AND n.status_type = 'ACTIVE'
           AND (n.document_type IN ('TAXN', 'NCON', 'REST') OR 
                (n.document_type IN ('REG_103', 'REG_103E') AND 
                 n.expiry_date IS NOT NULL AND n.expiry_date > (now() at time zone 'UTC')))
         FETCH FIRST 1 ROWS ONLY) AS frozen_doc_type,
       r.account_id,
       dt.document_type_desc,
      (SELECT CASE WHEN r.registration_type != 'MHREG' THEN ''
            ELSE (SELECT lcv.registration_type
                    FROM mhr_lien_check_vw lcv
                   WHERE lcv.mhr_number = r.mhr_number) END) AS ppr_lien_type,
       d.document_type,
       r.id AS registration_id,
       (SELECT mrr.doc_storage_url
          FROM mhr_registration_reports mrr
         WHERE mrr.registration_id = r.id) AS doc_storage_url
  FROM mhr_registrations r, mhr_documents d, mhr_document_types dt
 WHERE r.id = d.registration_id
   AND d.document_type = dt.document_type
;
 