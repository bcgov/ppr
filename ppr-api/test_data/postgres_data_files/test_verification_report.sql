-- Add some test verification_reports records for some of the test registrations.

-- Financing statement
INSERT INTO verification_reports(id, create_ts, registration_id, report_data, report_type, doc_storage_url)
  VALUES(200000000, current_timestamp at time zone 'utc', 200000000,
        '{"test": "junk"}', 'financingStatement', null)
;
-- Renewal
INSERT INTO verification_reports(id, create_ts, registration_id, report_data, report_type, doc_storage_url)
  VALUES(200000001, current_timestamp at time zone 'utc' + interval '5 minutes', 200000006,
         '{"test": "junk"}', 'financingStatement', null)
;

-- Amendment 
INSERT INTO verification_reports(id, create_ts, registration_id, report_data, report_type, doc_storage_url)
  VALUES(200000002, current_timestamp at time zone 'utc' + interval '5 minutes', 200000008,
         '{"test": "junk"}', 'financingStatement', null)
;

-- Discharge
INSERT INTO verification_reports(id, create_ts, registration_id, report_data, report_type, doc_storage_url)
  VALUES(200000003, current_timestamp at time zone 'utc' + interval '5 minutes', 200000004,
         '{"test": "junk"}', 'financingStatement', null)
;
-- Existing
INSERT INTO verification_reports(id, create_ts, registration_id, report_data, report_type, doc_storage_url)
  VALUES(200000004, current_timestamp at time zone 'utc' + interval '5 minutes', 200000011,
         '{"test": "junk"}', 'financingStatement', 'test-change-200000011.pdf')
;
