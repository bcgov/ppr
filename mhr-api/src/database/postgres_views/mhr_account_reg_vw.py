"""Maintain db view mhr_account_reg_vw here."""

from alembic_utils.pg_view import PGView


mhr_account_reg_vw = PGView(
    schema="public",
    signature="mhr_account_reg_vw",
    definition=r"""
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
            FROM mhr_registrations r1, mhr_owner_groups og, mhr_parties p
          WHERE r1.mhr_number = r.mhr_number 
            AND r1.id = og.registration_id
            AND og.registration_id = p.registration_id
            AND og.id = p.owner_group_id
            AND r1.registration_ts = (SELECT MAX(r2.registration_ts)
                                        FROM mhr_registrations r2, mhr_owner_groups og2
                                        WHERE r2.mhr_number = r.mhr_number
                                          AND og2.registration_id = r2.id
                                          AND r2.id <= r.id)) AS owner_names,       
        (SELECT CASE WHEN r.user_id IS NULL THEN ''
                      ELSE (SELECT CASE WHEN u.lastname = '' or u.lastname IS NULL THEN u.firstname
                                   ELSE u.firstname || ' ' || u.lastname END
                              FROM users u
                            WHERE u.username = r.user_id FETCH FIRST 1 ROWS ONLY) END) AS registering_name,
        d.document_id,
        d.document_registration_number,
        (SELECT d2.document_type
            FROM mhr_documents d2
          WHERE d2.id = (SELECT d3.id
                           FROM mhr_documents d3, mhr_registrations r2
                          WHERE r2.id = d3.registration_id
                            AND r2.mhr_number = r.mhr_number
                          ORDER BY r2.registration_ts DESC
                        FETCH FIRST 1 ROWS ONLY)) AS last_doc_type,
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
            AND n.document_type IN ('TAXN', 'NCON', 'REST')
          FETCH FIRST 1 ROWS ONLY) AS frozen_doc_type,
        r.account_id,
        dt.document_type_desc,
        (SELECT CASE WHEN r.registration_type NOT IN ('MHREG', 'MHREG_CONVERSION') THEN ''
              ELSE (SELECT lcv.registration_type
                      FROM mhr_lien_check_vw lcv
                    WHERE lcv.mhr_number = r.mhr_number
                  ORDER BY lcv.base_registration_ts
                  FETCH FIRST 1 ROWS ONLY) END) AS ppr_lien_type,
        d.document_type,
        r.id AS registration_id,
        (SELECT mrr.doc_storage_url
            FROM mhr_registration_reports mrr
          WHERE mrr.registration_id = r.id) AS doc_storage_url,
        (SELECT l.location_type
            FROM mhr_locations l, mhr_registrations r2
          WHERE r2.mhr_number = r.mhr_number
            AND r2.id = l.registration_id
            AND l.status_type = 'ACTIVE') AS location_type,
        d.affirm_by,
        (SELECT COUNT(mrr.id)
            FROM mhr_registration_reports mrr
          WHERE mrr.registration_id = r.id) AS report_count
    FROM mhr_registrations r, mhr_documents d, mhr_document_types dt
  WHERE r.id = d.registration_id
    AND d.document_type = dt.document_type
"""
)
