"""Maintain db view mhr_search_mhr_number_vw here."""

from alembic_utils.pg_view import PGView


mhr_search_mhr_number_vw = PGView(
    schema="public",
    signature="mhr_search_mhr_number_vw",
    definition=r"""
     SELECT r.mhr_number, r.status_type, r.registration_ts, a.city,
          (SELECT s.serial_number
               FROM mhr_registrations rs, mhr_sections s
          WHERE rs.mhr_number = r.mhr_number 
               AND rs.id = s.registration_id
               AND s.status_type = 'ACTIVE'
          ORDER BY s.id
          FETCH FIRST 1 ROWS ONLY) AS serial_number,
          d.year_made,
          d.make, d.model, r.id,
          (SELECT CASE WHEN p.business_name IS NOT NULL THEN og.status_type || '|' || p.business_name
                         WHEN p.middle_name IS NOT NULL THEN og.status_type || '|' || p.first_name || '|' || p.middle_name || '|' || p.last_name
                         ELSE og.status_type || '|' || p.first_name || '|' || p.last_name
                    END
               FROM mhr_registrations ro, mhr_owner_groups og, mhr_parties p
          WHERE ro.mhr_number = r.mhr_number 
               AND ro.id = og.registration_id
               AND og.registration_id = p.registration_id
               AND og.status_type IN ('ACTIVE', 'EXEMPT')
               ORDER BY p.id DESC
               FETCH FIRST 1 ROWS ONLY) AS owner_info,
          d.manufacturer_name,
          case when a.street_additional is not null then a.street || '|' || a.street_additional || '|' || a.city || ' ' || a.region || '|' || initcap(ct.country_desc)
               else a.street || '|' || a.city || ' ' || a.region || '|' || initcap(ct.country_desc) end as civic_address
     FROM mhr_registrations r,
          mhr_registrations rl,
          mhr_registrations rd,
          mhr_locations l, 
          addresses a,
          country_types ct,
          mhr_descriptions d
     WHERE (r.registration_type = 'MHREG' or r.registration_type = 'MHREG_CONVERSION')
     AND r.mhr_number = rl.mhr_number
     AND r.mhr_number = rd.mhr_number
     AND rl.id = l.registration_id
     AND l.status_type = 'ACTIVE'
     AND l.address_id = a.id
     and a.country = ct.country_type
     AND rd.id = d.registration_id
     AND d.status_type = 'ACTIVE'
"""
)
