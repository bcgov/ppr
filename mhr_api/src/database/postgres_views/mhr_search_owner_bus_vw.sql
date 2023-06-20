-- Search by owner org/business name view.
CREATE OR REPLACE VIEW public.mhr_search_owner_bus_vw AS
SELECT r.mhr_number, r.status_type, r.registration_ts, a.city,
       (SELECT s.serial_number
          FROM mhr_registrations rs, mhr_sections s
         WHERE rs.mhr_number = r.mhr_number 
           AND rs.id = s.registration_id
           AND s.status_type = 'ACTIVE'
       FETCH FIRST 1 ROWS ONLY) AS serial_number,
       d.year_made,
       d.make, d.model, r.id,
       p.business_name,
       og.status_type AS owner_status_type,
       p.compressed_name
  FROM mhr_registrations r,
       mhr_registrations rl,
       mhr_registrations rd,
       mhr_registrations ro,
       mhr_owner_groups og,
       mhr_parties p,
       mhr_locations l, 
       addresses a, 
       mhr_descriptions d
 WHERE (r.registration_type = 'MHREG' or r.registration_type = 'MHREG_CONVERSION')
   AND ro.mhr_number = r.mhr_number 
   AND ro.id = og.registration_id
   AND og.registration_id = p.registration_id
   AND p.owner_group_id = og.id
   AND p.party_type = 'OWNER_BUS'
   AND r.mhr_number = rl.mhr_number
   AND r.mhr_number = rd.mhr_number
   AND rl.id = l.registration_id
   AND l.status_type = 'ACTIVE'
   AND l.address_id = a.id
   AND rd.id = d.registration_id
   AND d.status_type = 'ACTIVE'
;
