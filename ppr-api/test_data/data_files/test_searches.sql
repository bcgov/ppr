-- Existing completed registration number search on TEST0001 (search step 1 and 2)
INSERT INTO search_client(search_id, search_ts, search_type_cd, api_criteria, search_response,
                         account_id, pay_invoice_id, pay_path, client_reference_id, total_results_size, returned_results_size)
  VALUES(200000000, sysdate, 'RG',
         '{"type": "REGISTRATION_NUMBER", "criteria": {"value": "TEST0001"}, "clientReferenceId": "T-S-RG-001"}',
         '[{"matchType": "EXACT", "registrationNumber": "TEST0001", "baseRegistrationNumber": "TEST0001", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
         'PS12345', null, null, 'UT-SQ-RG-001', 1, 1)
;
INSERT INTO search_result(search_id, api_result, registrations)
   VALUES(200000000,
'[{"baseRegistrationNumber": "TEST0001", "matchType": "EXACT", "registrationType": "SA"}]',
'UNIT TEST RESPONSE CONTENT NOT EXAMINED')
;

-- Existing incomplete registration number search on TEST0001 (search step only)
INSERT INTO search_client(search_id, search_ts, search_type_cd, api_criteria, search_response,
                         account_id, pay_invoice_id, pay_path, client_reference_id, total_results_size, returned_results_size)
  VALUES(200000001, sysdate, 'RG',
         '{"type": "REGISTRATION_NUMBER", "criteria": {"value": "TEST0001"}, "clientReferenceId": "T-S-RG-002"}',
         '[{"matchType": "EXACT", "registrationNumber": "TEST0001", "baseRegistrationNumber": "TEST0001", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
         'PS12345', null, null, 'UT-SQ-RG-002', 1, 1)
;

-- Existing registration number search on TEST0012 (search step only). A financing statement with no other registrations
INSERT INTO search_client(search_id, search_ts, search_type_cd, api_criteria, search_response,
                         account_id, pay_invoice_id, pay_path, client_reference_id, total_results_size, returned_results_size)
  VALUES(200000002, sysdate, 'RG',
         '{"type": "REGISTRATION_NUMBER", "criteria": {"value": "TEST0012"}, "clientReferenceId": "T-S-RG-003"}',
         '[{"matchType": "EXACT", "registrationNumber": "TEST0012", "baseRegistrationNumber": "TEST0012", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
         'PS12345', null, null, 'UT-SQ-RG-003', 1, 1)
;

-- Existing registration number search on TEST0002 (search step only). A financing statement with a renewal.
INSERT INTO search_client(search_id, search_ts, search_type_cd, api_criteria, search_response,
                         account_id, pay_invoice_id, pay_path, client_reference_id, total_results_size, returned_results_size)
  VALUES(200000003, sysdate, 'RG',
         '{"type": "REGISTRATION_NUMBER", "criteria": {"value": "TEST0002"}, "clientReferenceId": "T-S-RG-004"}',
         '[{"matchType": "EXACT", "registrationNumber": "TEST0002", "baseRegistrationNumber": "TEST0002", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
         'PS12345', null, null, 'UT-SQ-RG-004', 1, 1)
;
