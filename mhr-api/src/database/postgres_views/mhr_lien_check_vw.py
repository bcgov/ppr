"""Maintain db view mhr_lien_check_vw here."""

from alembic_utils.pg_view import PGView

# 14527 view to check if there is an outstanding PPR lien on a manufactured home searching by MHR number.
# 17853 updated.

mhr_lien_check_vw = PGView(
    schema="public",
    signature="mhr_lien_check_vw",
    definition=r"""
  SELECT sc.mhr_number, r.registration_type, r.registration_ts AS base_registration_ts,
        r.registration_number AS base_registration_num
    FROM registrations r, financing_statements fs, serial_collateral sc
  WHERE r.financing_id = fs.id
    AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN')
    AND r.registration_type NOT IN ('SA', 'TA', 'TM')
    AND (fs.expire_date IS NULL OR fs.expire_date > (now() at time zone 'utc'))
    AND NOT EXISTS (SELECT r3.id 
                      FROM registrations r3
                      WHERE r3.financing_id = fs.id
                        AND r3.registration_type_cl = 'DISCHARGE'
                        AND r3.registration_ts < (now() at time zone 'utc'))
    AND sc.financing_id = fs.id
    AND sc.registration_id_end IS NULL
    AND sc.mhr_number IS NOT NULL
    AND sc.mhr_number != 'NR'
  UNION (
  SELECT sc.mhr_number, r.registration_type || '_TAX', r.registration_ts AS base_registration_ts,
        r.registration_number AS base_registration_num
    FROM registrations r, financing_statements fs, serial_collateral sc
  WHERE r.financing_id = fs.id
    AND r.registration_type_cl = 'PPSALIEN'
    AND r.registration_type IN ('SA', 'TA', 'TM')
    AND (fs.expire_date IS NULL OR fs.expire_date > (now() at time zone 'utc'))
    AND NOT EXISTS (SELECT r3.id 
                      FROM registrations r3
                      WHERE r3.financing_id = fs.id
                        AND r3.registration_type_cl = 'DISCHARGE'
                        AND r3.registration_ts < (now() at time zone 'utc'))
    AND sc.financing_id = fs.id
    AND sc.registration_id_end IS NULL
    AND sc.mhr_number IS NOT NULL
    AND sc.mhr_number != 'NR'
    AND EXISTS (SELECT p.id
                  FROM parties p, client_codes cc
                  WHERE p.financing_id = fs.id
                    AND p.party_type = 'SP'
                    AND p.registration_id_end IS NULL
                    AND p.branch_id IS NOT NULL
                    AND p.branch_id = cc.id
                    AND cc.name like '%TAX DEFERME%')
  )
  UNION (
  SELECT sc.mhr_number, r.registration_type || '_GOV', r.registration_ts AS base_registration_ts,
        r.registration_number AS base_registration_num
    FROM registrations r, financing_statements fs, serial_collateral sc
  WHERE r.financing_id = fs.id
    AND r.registration_type_cl = 'PPSALIEN'
    AND r.registration_type IN ('SA', 'TA', 'TM')
    AND r.registration_ts <= TO_DATE('2004-03-31', 'YYYY-MM-DD')
    AND (fs.expire_date IS NULL OR fs.expire_date > (now() at time zone 'utc'))
    AND NOT EXISTS (SELECT r3.id 
                      FROM registrations r3
                      WHERE r3.financing_id = fs.id
                        AND r3.registration_type_cl = 'DISCHARGE'
                        AND r3.registration_ts < (now() at time zone 'utc'))
    AND sc.financing_id = fs.id
    AND sc.registration_id_end IS NULL
    AND sc.mhr_number IS NOT NULL
    AND sc.mhr_number != 'NR'
    AND EXISTS (SELECT p.id
                  FROM parties p, client_codes cc
                  WHERE p.financing_id = fs.id
                    AND p.party_type = 'SP'
                    AND p.registration_id_end IS NULL
                    AND p.branch_id IS NOT NULL
                    AND p.branch_id = cc.id
                    AND cc.name like 'HER MAJESTY%')
  )
  UNION (
  SELECT sc.mhr_number, r.registration_type, r.registration_ts AS base_registration_ts,
        r.registration_number AS base_registration_num
    FROM registrations r, financing_statements fs, serial_collateral sc
  WHERE r.financing_id = fs.id
    AND r.registration_type_cl = 'PPSALIEN'
    AND r.registration_type IN ('SA', 'TA', 'TM')
    AND (fs.expire_date IS NULL OR fs.expire_date > (now() at time zone 'utc'))
    AND NOT EXISTS (SELECT r3.id 
                      FROM registrations r3
                      WHERE r3.financing_id = fs.id
                        AND r3.registration_type_cl = 'DISCHARGE'
                        AND r3.registration_ts < (now() at time zone 'utc'))
    AND sc.financing_id = fs.id
    AND sc.registration_id_end IS NULL
    AND sc.mhr_number IS NOT NULL
    AND sc.mhr_number != 'NR'
    AND NOT EXISTS (SELECT p.id
                      FROM parties p, client_codes cc
                      WHERE p.financing_id = fs.id
                        AND p.party_type = 'SP'
                        AND p.registration_id_end IS NULL
                        AND p.branch_id IS NOT NULL
                        AND p.branch_id = cc.id
                        AND (cc.name like 'HER MAJESTY%' OR cc.name like '%TAX DEFERME%'))
  )
"""
)
