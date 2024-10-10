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

-- Add some test mail_reports records for some of the test registrations.

-- Discharge
INSERT INTO mail_reports(id, create_ts, registration_id, party_id, report_data, doc_storage_url, retry_count, status, message)
  VALUES(200000000, current_timestamp at time zone 'utc' + interval '5 minutes', 200000004, 200000013,
         '{"test": "junk"}', '/testing/PPRVER.20230206.200000004.200000013.PDF', null, 200, null)
;
-- Amendment
INSERT INTO mail_reports(id, create_ts, registration_id, party_id, report_data, doc_storage_url, retry_count, status, message)
  VALUES(200000001, current_timestamp at time zone 'utc' + interval '5 minutes', 200000008, 200000022,
         '{"test": "junk"}', '/testing/PPRVER.20230206.200000008.200000022.PDF', null, 200, null)
;
INSERT INTO mail_reports(id, create_ts, registration_id, party_id, report_data, doc_storage_url, retry_count, status, message)
  VALUES(200000002, current_timestamp at time zone 'utc' + interval '5 minutes', 200000008, 200000023,
         '{"test": "junk"}', null, 2, null, null)
;
INSERT INTO mail_reports(id, create_ts, registration_id, party_id, report_data, doc_storage_url, retry_count, status, message)
  VALUES(200000003, current_timestamp at time zone 'utc' + interval '5 minutes', 200000008, 200000024,
         '{"test": "junk"}', null, 4, null, null)
;
