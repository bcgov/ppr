"""Maintain db view account_registration_count_vw here."""

from alembic_utils.pg_view import PGView


account_registration_count_vw = PGView(
    schema="public",
    signature="account_registration_count_vw",
    definition=r"""
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
                            AND r3.registration_ts < ((now() at time zone 'utc') - interval '30 days')))
    """
)
