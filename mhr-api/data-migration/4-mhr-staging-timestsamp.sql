-- Post staging tables load step 5:
-- Update legacy date, date and time to timestamp at time zone UTC.
-- 1. Create Postgres note expiry date values from legacy data.
-- 2. Create Postgres description engineer date values from legacy data.
-- 3. Create Postgres location tax certificate date values from legacy data.
-- 4. Create Postgres registration timestamp values from legacy data.
-- 5. Correct 42 registrations where regidate is before the conversion regidate: use the draft date which is after the
--    conversion date.

-- ~146000 records
UPDATE staging_mhr_document
   SET transfer_date = TO_TIMESTAMP((dateofex || ' 00:00:01'), 'YYYY-MM-DD HH24:MI:SS') at time zone 'utc'
 WHERE dateofex is not null
;

-- ~60000 records
UPDATE staging_mhr_note
   SET expiry_date = TO_TIMESTAMP((expiryda || ' 23:59:59'), 'YYYY-MM-DD HH24:MI:SS') at time zone 'utc'
 WHERE expiryda is not null
;
-- ~300 records
UPDATE staging_mhr_description
   SET engineer_date = TO_TIMESTAMP((engidate || ' 00:00:01'), 'YYYY-MM-DD HH24:MI:SS') at time zone 'utc'
 WHERE engidate is not null
;
-- ~20000 records
UPDATE staging_mhr_location
   SET tax_certification_date = TO_TIMESTAMP((taxdate || ' 23:59:59'), 'YYYY-MM-DD HH24:MI:SS') at time zone 'utc'
 WHERE taxdate is not null
;
-- ~77000 records
UPDATE staging_mhr_document
   SET registration_ts = TO_TIMESTAMP(SUBSTR(regidate, 1, 19), 'YYYY-MM-DD-HH24.MI.SS') at time zone 'utc'
 WHERE regidate IS NOT NULL 
   AND documtid LIKE 'REG%'
;

-- ~136000 records
UPDATE staging_mhr_document
   SET registration_ts = TO_TIMESTAMP(SUBSTR(regidate, 1, 19), 'YYYY-MM-DD-HH24.MI.SS') at time zone 'utc'
 WHERE regidate IS NOT NULL 
   AND documtid LIKE '1%'
;

-- ~65000 records
UPDATE staging_mhr_document
   SET registration_ts = TO_TIMESTAMP(SUBSTR(regidate, 1, 19), 'YYYY-MM-DD-HH24.MI.SS') at time zone 'utc'
 WHERE regidate IS NOT NULL 
   AND (documtid LIKE '8%' OR documtid LIKE '9%')
;

-- ~198000 records
UPDATE staging_mhr_document
   SET registration_ts = TO_TIMESTAMP(SUBSTR(regidate, 1, 19), 'YYYY-MM-DD-HH24.MI.SS') at time zone 'utc'
 WHERE regidate IS NOT NULL 
  AND documtid NOT LIKE 'REG%'
  AND documtid NOT LIKE '1%'
  AND documtid NOT LIKE '8%'
  AND documtid NOT LIKE '9%'
;

/*
Business decision to leave timestamps as is even when they are out of sync. Ticket 17023
UPDATE staging_mhr_document
   SET registration_ts = TO_TIMESTAMP(SUBSTR(drafdate, 1, 19), 'YYYY-MM-DD-HH24.MI.SS') at time zone 'utc'
 WHERE registration_ts IS NOT NULL 
   AND registration_ts < TO_DATE('1995-11-14', 'YYYY-MM-DD')
;
UPDATE staging_mhr_document
   SET registration_ts = TO_TIMESTAMP('1995-11-14 00:01:00', 'YYYY-MM-DD HH24:MI:SS') at time zone 'utc'
WHERE documtid = '41444482'
;
UPDATE staging_mhr_document
   SET registration_ts = TO_TIMESTAMP('1995-11-15 14:39:01', 'YYYY-MM-DD HH24:MI:SS') at time zone 'utc'
WHERE documtid = '42400883'
;
*/
