-- Run as the last step
-- Patch mhr_registrations.summay_snapshot 
UPDATE mhr_registrations r 
SET summary_snapshot = to_jsonb(v) 
FROM mhr_account_reg_vw v 
WHERE v.registration_id = r.id 
  AND r.summary_snapshot IS NULL;
