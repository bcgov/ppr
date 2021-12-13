-- Existing completed registration number search on TEST0001 (search step 1 and 2)
INSERT INTO search_requests(id, search_ts, search_type, api_criteria, search_response,
                         account_id, pay_invoice_id, pay_path, client_reference_id, total_results_size, returned_results_size)
  VALUES(200000000, CURRENT_TIMESTAMP, 'RG',
         '{"type": "REGISTRATION_NUMBER", "criteria": {"value": "TEST0001"}, "clientReferenceId": "T-S-RG-001"}',
         '[{"matchType": "EXACT", "registrationNumber": "TEST0001", "baseRegistrationNumber": "TEST0001", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
         'PS12345', null, null, 'UT-SQ-RG-001', 1, 1)
;
INSERT INTO search_results(search_id, exact_match_count, similar_match_count, api_result, registrations)
   VALUES(200000000, 1, 0,
'[{"baseRegistrationNumber": "TEST0001", "matchType": "EXACT", "registrationType": "SA"}]',
'[]')
;

-- Existing incomplete registration number search on TEST0001 (search step only)
INSERT INTO search_requests(id, search_ts, search_type, api_criteria, search_response,
                         account_id, pay_invoice_id, pay_path, client_reference_id, total_results_size, returned_results_size)
  VALUES(200000001, CURRENT_TIMESTAMP, 'RG',
         '{"type": "REGISTRATION_NUMBER", "criteria": {"value": "TEST0001"}, "clientReferenceId": "T-S-RG-002"}',
         '[{"matchType": "EXACT", "registrationNumber": "TEST0001", "baseRegistrationNumber": "TEST0001", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
         'PS12345', null, null, 'UT-SQ-RG-002', 1, 1)
;
INSERT INTO search_results(search_id, exact_match_count, similar_match_count, api_result, registrations)
   VALUES(200000001, 1, 0, null,
'[{"matchType": "EXACT", "financingStatement": {"type": "SA", "baseRegistrationNumber": "TEST0001", "registrationDescription": "PPSA SECURITY AGREEMENT", "registrationAct": "PPSA SECURITY ACT", "createDateTime": "2021-03-12T01:48:53+00:00", "clientReferenceId": "TEST-SA-0001", "registeringParty": {"personName": {"first": "TEST", "last": "REGISTERING", "middle": "1"}, "address": {"street": "TEST-0001", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, "securedParties": [{"partyId": 200000004, "code": "200000000", "businessName": "TEST SECURED PARTY", "address": {"street": "TEST 200000000", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}, "emailAddress": "test-sp-client@gmail.com"}, {"partyId": 200000026, "businessName": "TEST 9 CHANGE TRANSFER SECURED PARTY", "address": {"street": "TEST-00C9", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}], "debtors": [{"partyId": 200000002, "businessName": "TEST BUS 2 DEBTOR", "address": {"street": "TEST-0001", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, {"partyId": 200000024, "businessName": "TEST 8 TRANSFER DEBTOR", "address": {"street": "TEST-00C8", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}], "generalCollateral": [{"collateralId": 200000003, "description": "TEST GENERAL COLLATERAL CHANGE ADD."}, {"collateralId": 200000000, "description": "TEST0001 GC 1"}], "vehicleCollateral": [{"vehicleId": 200000007, "type": "MV", "year": 2014, "make": "BMW", "model": "Z4", "serialNumber": "JU622994"}, {"vehicleId": 200000008, "type": "MH", "year": 2012, "make": "HOMCO IND. LTD DIPLOMAT", "serialNumber": "999999", "manufacturedHomeRegistrationNumber": "220000"}, {"vehicleId": 200000000, "type": "MV", "year": 2018, "make": "HYUNDAI", "model": "TUSCON", "serialNumber": "KM8J3CA46JU622994"}], "trustIndenture": true, "lifeYears": 2, "expiryDate": "2023-03-12T01:48:53+00:00", "changes": [{"baseRegistrationNumber": "TEST0001", "createDateTime": "2021-03-12T01:48:54+00:00", "changeRegistrationNumber": "TEST0010", "changeType": "SU", "clientReferenceId": "TEST-CH-0010", "registeringParty": {"personName": {"first": "TEST-CHANGE-SU", "last": "REGISTERING", "middle": "10"}, "address": {"street": "TEST-0010", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, "addGeneralCollateral": [{"collateralId": 200000003, "description": "TEST GENERAL COLLATERAL CHANGE ADD."}], "deleteGeneralCollateral": [{"collateralId": 200000002, "description": "TEST GENERAL COLLATERAL AMEND ADD."}], "addVehicleCollateral": [{"vehicleId": 200000007, "type": "MV", "year": 2014, "make": "BMW", "model": "Z4", "serialNumber": "JU622994"}, {"vehicleId": 200000008, "type": "MH", "year": 2012, "make": "HOMCO IND. LTD DIPLOMAT", "serialNumber": "999999", "manufacturedHomeRegistrationNumber": "220000"}], "deleteVehicleCollateral": [{"vehicleId": 200000006, "type": "MV", "year": 2018, "make": "FORD", "model": "FIESTA", "serialNumber": "T346JU622994"}], "statementType": "CHANGE_STATEMENT"}]}}]')
;

-- Existing registration number search on TEST0012 (search step only). A financing statement with no other registrations
INSERT INTO search_requests(id, search_ts, search_type, api_criteria, search_response,
                         account_id, pay_invoice_id, pay_path, client_reference_id, total_results_size, returned_results_size)
  VALUES(200000002, CURRENT_TIMESTAMP, 'RG',
         '{"type": "REGISTRATION_NUMBER", "criteria": {"value": "TEST0012"}, "clientReferenceId": "T-S-RG-003"}',
         '[{"matchType": "EXACT", "registrationNumber": "TEST0012", "baseRegistrationNumber": "TEST0012", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
         'PS12345', null, null, 'UT-SQ-RG-003', 1, 1)
;
INSERT INTO search_results(search_id, exact_match_count, similar_match_count, api_result, registrations)
   VALUES(200000002, 1, 0, null,
'[{"matchType": "EXACT", "financingStatement": {"type": "SA", "baseRegistrationNumber": "TEST0012", "registrationDescription": "PPSA SECURITY AGREEMENT", "registrationAct": "PPSA SECURITY ACT", "createDateTime": "2021-03-12T01:48:54+00:00", "clientReferenceId": "TEST-SA-0012", "registeringParty": {"personName": {"first": "TEST", "last": "REGISTERING", "middle": "12"}, "address": {"street": "TEST-0012", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, "securedParties": [{"partyId": 200000033, "businessName": "TEST 12 SECURED PARTY", "address": {"street": "TEST-0012", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}], "debtors": [{"partyId": 200000032, "personName": {"first": "TEST IND", "last": "DEBTOR", "middle": "12"}, "address": {"street": "TEST-0012", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}], "vehicleCollateral": [{"vehicleId": 200000011, "type": "MH", "year": 2012, "make": "HOMCO IND. LTD DIPLOMAT", "serialNumber": "9999", "manufacturedHomeRegistrationNumber": "22000"}, {"vehicleId": 200000012, "type": "AC", "year": 1998, "make": "CESSNA", "model": "172R SKYHAWK", "serialNumber": "CFYX"}, {"vehicleId": 200000013, "type": "AF", "year": 1998, "make": "AIRFRAME make", "model": "AIRFRAME model", "serialNumber": "AF16031"}], "trustIndenture": true, "lifeYears": 1, "expiryDate": "2022-03-12T01:48:54+00:00"}}]')
;

-- Existing registration number search on TEST0002 (search step only). A financing statement with a renewal.
INSERT INTO search_requests(id, search_ts, search_type, api_criteria, search_response,
                         account_id, pay_invoice_id, pay_path, client_reference_id, total_results_size, returned_results_size)
  VALUES(200000003, CURRENT_TIMESTAMP, 'RG',
         '{"type": "REGISTRATION_NUMBER", "criteria": {"value": "TEST0002"}, "clientReferenceId": "T-S-RG-004"}',
         '[{"matchType": "EXACT", "registrationNumber": "TEST0002", "baseRegistrationNumber": "TEST0002", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
         'PS12345', null, null, 'UT-SQ-RG-004', 1, 1)
;
INSERT INTO search_results(search_id, exact_match_count, similar_match_count, api_result, registrations)
   VALUES(200000003, 1, 0, null,
'[{"matchType": "EXACT", "financingStatement": {"type": "RL", "baseRegistrationNumber": "TEST0002", "registrationDescription": "REPAIRERS LIEN", "registrationAct": "REPAIRERS LIEN ACT", "createDateTime": "2021-03-12T01:48:53+00:00", "clientReferenceId": "TEST-RL-0001", "registeringParty": {"personName": {"first": "TEST", "last": "REGISTERING", "middle": "2"}, "address": {"street": "TEST-0002", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, "securedParties": [{"partyId": 200000007, "code": "200000000", "businessName": "TEST SECURED PARTY", "address": {"street": "TEST 200000000", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}, "emailAddress": "test-sp-client@gmail.com"}], "debtors": [{"partyId": 200000006, "businessName": "TEST BUS 2 DEBTOR", "address": {"street": "TEST-0002", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}], "vehicleCollateral": [{"vehicleId": 200000002, "type": "MV", "year": 2014, "make": "HYUNDAI", "model": "TUSCON", "serialNumber": "KX8J3CA46JU622994"}], "lienAmount": "2000.00", "surrenderDate": "2021-06-10T01:48:53+00:00", "trustIndenture": false, "expiryDate": "2021-06-10T01:48:54+00:00", "changes": [{"baseRegistrationNumber": "TEST0002", "createDateTime": "2021-03-12T01:53:54+00:00", "renewalRegistrationNumber": "TEST00R6", "clientReferenceId": "TEST-REN-0006", "registeringParty": {"personName": {"first": "TEST-RENEWAL-RL", "last": "REGISTERING", "middle": "6"}, "address": {"street": "TEST-00R6", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, "expiryDate": "2021-06-10T01:48:54+00:00", "courtOrderInformation": {"courtName": "Supreme Court of British Columbia", "courtRegistry": "Victoria", "fileNumber": "BC123495", "orderDate": "2021-09-28T01:48:54+00:00", "effectOfOrder": "Court Order to renew Repairers Lien."}, "statementType": "RENEWAL_STATEMENT"}]}}]')
;


-- Existing Business debtor search for autosave search selection update testing.
INSERT INTO search_requests(id, search_ts, search_type, api_criteria, search_response,
                         account_id, pay_invoice_id, pay_path, client_reference_id, total_results_size, returned_results_size)
  VALUES(200000004, CURRENT_TIMESTAMP, 'BS',
         '{"type": "BUSINESS_DEBTOR", "criteria": {"debtorName": {"business": "TEST BUS 2 DEBTOR"}}, "clientReferenceId": "T-S-DB-001"}',
         '[{"baseRegistrationNumber": "TEST0001", "matchType": "EXACT", "createDateTime": "2021-03-02T22:46:43+00:00", "registrationType": "SA", "debtor": {"businessName": "TEST BUS 2 DEBTOR", "partyId": 200000002}}, {"baseRegistrationNumber": "TEST0002", "matchType": "EXACT", "createDateTime": "2021-03-02T22:46:43+00:00", "registrationType": "RL", "debtor": {"businessName": "TEST BUS 2 DEBTOR", "partyId": 200000006}}, {"baseRegistrationNumber": "TEST0003", "matchType": "SIMILAR", "createDateTime": "2021-03-02T22:46:43+00:00", "registrationType": "RL", "debtor": {"businessName": "TEST BUS 3 DEBTOR", "partyId": 200000009}}]',
         'PS12345', null, null, 'UT-SQ-MH-005', 1, 1)
;


-- Completed registration number search on TEST0012 to test get details: search ts in the future.
INSERT INTO search_requests(id, search_ts, search_type, api_criteria, search_response,
                         account_id, pay_invoice_id, pay_path, client_reference_id, total_results_size, returned_results_size)
  VALUES(200000005, CURRENT_TIMESTAMP + interval '365 days', 'RG',
         '{"type": "REGISTRATION_NUMBER", "criteria": {"value": "TEST0012"}, "clientReferenceId": "T-S-RG-003"}',
         '[{"matchType": "EXACT", "registrationNumber": "TEST0012", "baseRegistrationNumber": "TEST0012", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
         'PS12345', null, null, 'T-S-RG-003', 1, 1)
;
INSERT INTO search_results(search_id, exact_match_count, similar_match_count, api_result, registrations)
   VALUES(200000005, 1, 0,
'[{"matchType": "EXACT", "registrationNumber": "TEST0012", "baseRegistrationNumber": "TEST0012", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
'{
    "searchDateTime": "2021-03-12T19:46:46+00:00",
    "exactResultsSize": 1,
    "similarResultsSize": 0,
    "totalResultsSize": 1,
    "searchQuery": {
        "type": "REGISTRATION_NUMBER",
        "criteria": {"value": "JU622994"},
        "clientReferenceId": "T-SR-SS-1001"
    },
    "details": [ {
  "baseRegistrationNumber": "TEST0001", 
  "clientReferenceId": "T-API-DL-001", 
  "createDateTime": "2021-03-09T22:59:10+00:00", 
  "debtors": [
    {
      "address": {
        "city": "VICTORIA", 
        "country": "CA", 
        "postalCode": "A1A 1A1", 
        "region": "BC", 
        "street": "721 DEBTOR AVE"
      }, 
      "businessName": "MY COMPANY INC", 
      "partyId": 1118
    }, 
    {
      "address": {
        "city": "VICTORIA", 
        "country": "CA", 
        "postalCode": "V8S 2V4", 
        "region": "BC", 
        "street": "520 JOHNSON ST"
      }, 
      "birthDate": "1986-12-02T03:20:20+00:00", 
      "partyId": 1119, 
      "personName": {
        "first": "MICHAEL", 
        "last": "SMITH", 
        "middle": "J"
      }
    }
  ], 
  "expiryDate": "2026-03-09T23:59:59+00:00", 
  "lifeYears": 5, 
  "registeringParty": {
    "address": {
      "city": "VICTORIA", 
      "country": "CA", 
      "postalCode": "V8W 2V8", 
      "region": "BC", 
      "street": "222 SUMMER STREET"
    }, 
    "businessName": "ABC SEARCHING COMPANY"
  }, 
  "securedParties": [
    {
      "address": {
        "city": "SIDNEY", 
        "country": "CA", 
        "postalCode": "V7R 1R7", 
        "region": "BC", 
        "street": "3721 BEACON AVENUE"
      }, 
      "businessName": "BANK OF BRITISH COLUMBIA", 
      "partyId": 1117
    }
  ], 
  "trustIndenture": false, 
  "type": "SA", 
  "vehicleCollateral": [
    {
      "make": "HYUNDAI", 
      "model": "TUCSON", 
      "serialNumber": "KM8J3CA46JU622994", 
      "type": "MV", 
      "vehicleId": 417, 
      "year": 2018
    }
  ]
} ] }
')
;


-- Completed registration number search on TEST0012 to test get details: search ts too far in the past.
INSERT INTO search_requests(id, search_ts, search_type, api_criteria, search_response,
                         account_id, pay_invoice_id, pay_path, client_reference_id, total_results_size, returned_results_size)
  VALUES(200000006, CURRENT_TIMESTAMP - interval '32 days', 'RG',
         '{"type": "REGISTRATION_NUMBER", "criteria": {"value": "TEST0012"}, "clientReferenceId": "T-S-RG-003"}',
         '[{"matchType": "EXACT", "registrationNumber": "TEST0012", "baseRegistrationNumber": "TEST0012", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
         'PS12345', null, null, 'T-S-RG-003', 1, 1)
;
INSERT INTO search_results(search_id, exact_match_count, similar_match_count, api_result, registrations)
   VALUES(200000006, 1, 1,
'[{"matchType": "EXACT", "registrationNumber": "TEST0012", "baseRegistrationNumber": "TEST0012", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
'{
  "baseRegistrationNumber": "TEST0001", 
  "clientReferenceId": "T-API-DL-001", 
  "createDateTime": "2021-03-09T22:59:10+00:00", 
  "debtors": [
    {
      "address": {
        "city": "VICTORIA", 
        "country": "CA", 
        "postalCode": "A1A 1A1", 
        "region": "BC", 
        "street": "721 DEBTOR AVE"
      }, 
      "businessName": "MY COMPANY INC", 
      "partyId": 1118
    }, 
    {
      "address": {
        "city": "VICTORIA", 
        "country": "CA", 
        "postalCode": "V8S 2V4", 
        "region": "BC", 
        "street": "520 JOHNSON ST"
      }, 
      "birthDate": "1986-12-02T03:20:20+00:00", 
      "partyId": 1119, 
      "personName": {
        "first": "MICHAEL", 
        "last": "SMITH", 
        "middle": "J"
      }
    }
  ], 
  "expiryDate": "2026-03-09T23:59:59+00:00", 
  "lifeYears": 5, 
  "registeringParty": {
    "address": {
      "city": "VICTORIA", 
      "country": "CA", 
      "postalCode": "V8W 2V8", 
      "region": "BC", 
      "street": "222 SUMMER STREET"
    }, 
    "businessName": "ABC SEARCHING COMPANY"
  }, 
  "securedParties": [
    {
      "address": {
        "city": "SIDNEY", 
        "country": "CA", 
        "postalCode": "V7R 1R7", 
        "region": "BC", 
        "street": "3721 BEACON AVENUE"
      }, 
      "businessName": "BANK OF BRITISH COLUMBIA", 
      "partyId": 1117
    }
  ], 
  "trustIndenture": false, 
  "type": "SA", 
  "vehicleCollateral": [
    {
      "make": "HYUNDAI", 
      "model": "TUCSON", 
      "serialNumber": "KM8J3CA46JU622994", 
      "type": "MV", 
      "vehicleId": 417, 
      "year": 2018
    }
  ]
}')
;


-- Existing pending large search result report no tracking
INSERT INTO search_requests(id, search_ts, search_type, api_criteria, search_response,
                         account_id, pay_invoice_id, pay_path, client_reference_id, total_results_size, returned_results_size)
  VALUES(200000007, CURRENT_TIMESTAMP  at time zone 'utc', 'RG',
         '{"type": "REGISTRATION_NUMBER", "criteria": {"value": "TEST0001"}, "clientReferenceId": "T-S-RG-002"}',
         '[{"matchType": "EXACT", "registrationNumber": "TEST0001", "baseRegistrationNumber": "TEST0001", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
         'PS12345', null, null, 'UT-SQ-RG-002', 76, 76)
;
INSERT INTO search_results(search_id, exact_match_count, similar_match_count, api_result, registrations, callback_url, doc_storage_url)
   VALUES(200000007, 76, 0, '[]',
'[{"matchType": "EXACT", "financingStatement": {"type": "SA", "baseRegistrationNumber": "TEST0001", "registrationDescription": "PPSA SECURITY AGREEMENT", "registrationAct": "PPSA SECURITY ACT", "createDateTime": "2021-03-12T01:48:53+00:00", "clientReferenceId": "TEST-SA-0001", "registeringParty": {"personName": {"first": "TEST", "last": "REGISTERING", "middle": "1"}, "address": {"street": "TEST-0001", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, "securedParties": [{"partyId": 200000004, "code": "200000000", "businessName": "TEST SECURED PARTY", "address": {"street": "TEST 200000000", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}, "emailAddress": "test-sp-client@gmail.com"}, {"partyId": 200000026, "businessName": "TEST 9 CHANGE TRANSFER SECURED PARTY", "address": {"street": "TEST-00C9", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}], "debtors": [{"partyId": 200000002, "businessName": "TEST BUS 2 DEBTOR", "address": {"street": "TEST-0001", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, {"partyId": 200000024, "businessName": "TEST 8 TRANSFER DEBTOR", "address": {"street": "TEST-00C8", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}], "generalCollateral": [{"collateralId": 200000003, "description": "TEST GENERAL COLLATERAL CHANGE ADD."}, {"collateralId": 200000000, "description": "TEST0001 GC 1"}], "vehicleCollateral": [{"vehicleId": 200000007, "type": "MV", "year": 2014, "make": "BMW", "model": "Z4", "serialNumber": "JU622994"}, {"vehicleId": 200000008, "type": "MH", "year": 2012, "make": "HOMCO IND. LTD DIPLOMAT", "serialNumber": "999999", "manufacturedHomeRegistrationNumber": "220000"}, {"vehicleId": 200000000, "type": "MV", "year": 2018, "make": "HYUNDAI", "model": "TUSCON", "serialNumber": "KM8J3CA46JU622994"}], "trustIndenture": true, "lifeYears": 2, "expiryDate": "2023-03-12T01:48:53+00:00", "changes": [{"baseRegistrationNumber": "TEST0001", "createDateTime": "2021-03-12T01:48:54+00:00", "changeRegistrationNumber": "TEST0010", "changeType": "SU", "clientReferenceId": "TEST-CH-0010", "registeringParty": {"personName": {"first": "TEST-CHANGE-SU", "last": "REGISTERING", "middle": "10"}, "address": {"street": "TEST-0010", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, "addGeneralCollateral": [{"collateralId": 200000003, "description": "TEST GENERAL COLLATERAL CHANGE ADD."}], "deleteGeneralCollateral": [{"collateralId": 200000002, "description": "TEST GENERAL COLLATERAL AMEND ADD."}], "addVehicleCollateral": [{"vehicleId": 200000007, "type": "MV", "year": 2014, "make": "BMW", "model": "Z4", "serialNumber": "JU622994"}, {"vehicleId": 200000008, "type": "MH", "year": 2012, "make": "HOMCO IND. LTD DIPLOMAT", "serialNumber": "999999", "manufacturedHomeRegistrationNumber": "220000"}], "deleteVehicleCollateral": [{"vehicleId": 200000006, "type": "MV", "year": 2018, "make": "FORD", "model": "FIESTA", "serialNumber": "T346JU622994"}], "statementType": "CHANGE_STATEMENT"}]}}]',
'TEST_CALLBACK_URL', null)
;

-- Existing completed large search result report
INSERT INTO search_requests(id, search_ts, search_type, api_criteria, search_response,
                         account_id, pay_invoice_id, pay_path, client_reference_id, total_results_size, returned_results_size)
  VALUES(200000008, CURRENT_TIMESTAMP  at time zone 'utc', 'RG',
         '{"type": "REGISTRATION_NUMBER", "criteria": {"value": "TEST0001"}, "clientReferenceId": "T-S-RG-002"}',
         '[{"matchType": "EXACT", "registrationNumber": "TEST0001", "baseRegistrationNumber": "TEST0001", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
         'PS12345', null, null, 'UT-SQ-RG-002', 76, 76)
;
INSERT INTO search_results(search_id, exact_match_count, similar_match_count, api_result, registrations, callback_url, doc_storage_url)
   VALUES(200000008, 76, 0, '[]',
'[{"matchType": "EXACT", "financingStatement": {"type": "SA", "baseRegistrationNumber": "TEST0001", "registrationDescription": "PPSA SECURITY AGREEMENT", "registrationAct": "PPSA SECURITY ACT", "createDateTime": "2021-03-12T01:48:53+00:00", "clientReferenceId": "TEST-SA-0001", "registeringParty": {"personName": {"first": "TEST", "last": "REGISTERING", "middle": "1"}, "address": {"street": "TEST-0001", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, "securedParties": [{"partyId": 200000004, "code": "200000000", "businessName": "TEST SECURED PARTY", "address": {"street": "TEST 200000000", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}, "emailAddress": "test-sp-client@gmail.com"}, {"partyId": 200000026, "businessName": "TEST 9 CHANGE TRANSFER SECURED PARTY", "address": {"street": "TEST-00C9", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}], "debtors": [{"partyId": 200000002, "businessName": "TEST BUS 2 DEBTOR", "address": {"street": "TEST-0001", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, {"partyId": 200000024, "businessName": "TEST 8 TRANSFER DEBTOR", "address": {"street": "TEST-00C8", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}], "generalCollateral": [{"collateralId": 200000003, "description": "TEST GENERAL COLLATERAL CHANGE ADD."}, {"collateralId": 200000000, "description": "TEST0001 GC 1"}], "vehicleCollateral": [{"vehicleId": 200000007, "type": "MV", "year": 2014, "make": "BMW", "model": "Z4", "serialNumber": "JU622994"}, {"vehicleId": 200000008, "type": "MH", "year": 2012, "make": "HOMCO IND. LTD DIPLOMAT", "serialNumber": "999999", "manufacturedHomeRegistrationNumber": "220000"}, {"vehicleId": 200000000, "type": "MV", "year": 2018, "make": "HYUNDAI", "model": "TUSCON", "serialNumber": "KM8J3CA46JU622994"}], "trustIndenture": true, "lifeYears": 2, "expiryDate": "2023-03-12T01:48:53+00:00", "changes": [{"baseRegistrationNumber": "TEST0001", "createDateTime": "2021-03-12T01:48:54+00:00", "changeRegistrationNumber": "TEST0010", "changeType": "SU", "clientReferenceId": "TEST-CH-0010", "registeringParty": {"personName": {"first": "TEST-CHANGE-SU", "last": "REGISTERING", "middle": "10"}, "address": {"street": "TEST-0010", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, "addGeneralCollateral": [{"collateralId": 200000003, "description": "TEST GENERAL COLLATERAL CHANGE ADD."}], "deleteGeneralCollateral": [{"collateralId": 200000002, "description": "TEST GENERAL COLLATERAL AMEND ADD."}], "addVehicleCollateral": [{"vehicleId": 200000007, "type": "MV", "year": 2014, "make": "BMW", "model": "Z4", "serialNumber": "JU622994"}, {"vehicleId": 200000008, "type": "MH", "year": 2012, "make": "HOMCO IND. LTD DIPLOMAT", "serialNumber": "999999", "manufacturedHomeRegistrationNumber": "220000"}], "deleteVehicleCollateral": [{"vehicleId": 200000006, "type": "MV", "year": 2018, "make": "FORD", "model": "FIESTA", "serialNumber": "T346JU622994"}], "statementType": "CHANGE_STATEMENT"}]}}]',
'/ppr/api/v1/search-results/200000008', 'search-results-report-200000008.pdf')
;

-- Existing pending large search result report tracking errors
INSERT INTO search_requests(id, search_ts, search_type, api_criteria, search_response,
                         account_id, pay_invoice_id, pay_path, client_reference_id, total_results_size, returned_results_size)
  VALUES(200000009, CURRENT_TIMESTAMP  at time zone 'utc', 'RG',
         '{"type": "REGISTRATION_NUMBER", "criteria": {"value": "TEST0001"}, "clientReferenceId": "T-S-RG-002"}',
         '[{"matchType": "EXACT", "registrationNumber": "TEST0001", "baseRegistrationNumber": "TEST0001", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
         'PS12345', null, null, 'UT-SQ-RG-002', 76, 76)
;
INSERT INTO search_results(search_id, exact_match_count, similar_match_count, api_result, registrations, callback_url, doc_storage_url)
   VALUES(200000009, 76, 0, '[]',
'[{"matchType": "EXACT", "financingStatement": {"type": "SA", "baseRegistrationNumber": "TEST0001", "registrationDescription": "PPSA SECURITY AGREEMENT", "registrationAct": "PPSA SECURITY ACT", "createDateTime": "2021-03-12T01:48:53+00:00", "clientReferenceId": "TEST-SA-0001", "registeringParty": {"personName": {"first": "TEST", "last": "REGISTERING", "middle": "1"}, "address": {"street": "TEST-0001", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, "securedParties": [{"partyId": 200000004, "code": "200000000", "businessName": "TEST SECURED PARTY", "address": {"street": "TEST 200000000", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}, "emailAddress": "test-sp-client@gmail.com"}, {"partyId": 200000026, "businessName": "TEST 9 CHANGE TRANSFER SECURED PARTY", "address": {"street": "TEST-00C9", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}], "debtors": [{"partyId": 200000002, "businessName": "TEST BUS 2 DEBTOR", "address": {"street": "TEST-0001", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, {"partyId": 200000024, "businessName": "TEST 8 TRANSFER DEBTOR", "address": {"street": "TEST-00C8", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}], "generalCollateral": [{"collateralId": 200000003, "description": "TEST GENERAL COLLATERAL CHANGE ADD."}, {"collateralId": 200000000, "description": "TEST0001 GC 1"}], "vehicleCollateral": [{"vehicleId": 200000007, "type": "MV", "year": 2014, "make": "BMW", "model": "Z4", "serialNumber": "JU622994"}, {"vehicleId": 200000008, "type": "MH", "year": 2012, "make": "HOMCO IND. LTD DIPLOMAT", "serialNumber": "999999", "manufacturedHomeRegistrationNumber": "220000"}, {"vehicleId": 200000000, "type": "MV", "year": 2018, "make": "HYUNDAI", "model": "TUSCON", "serialNumber": "KM8J3CA46JU622994"}], "trustIndenture": true, "lifeYears": 2, "expiryDate": "2023-03-12T01:48:53+00:00", "changes": [{"baseRegistrationNumber": "TEST0001", "createDateTime": "2021-03-12T01:48:54+00:00", "changeRegistrationNumber": "TEST0010", "changeType": "SU", "clientReferenceId": "TEST-CH-0010", "registeringParty": {"personName": {"first": "TEST-CHANGE-SU", "last": "REGISTERING", "middle": "10"}, "address": {"street": "TEST-0010", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, "addGeneralCollateral": [{"collateralId": 200000003, "description": "TEST GENERAL COLLATERAL CHANGE ADD."}], "deleteGeneralCollateral": [{"collateralId": 200000002, "description": "TEST GENERAL COLLATERAL AMEND ADD."}], "addVehicleCollateral": [{"vehicleId": 200000007, "type": "MV", "year": 2014, "make": "BMW", "model": "Z4", "serialNumber": "JU622994"}, {"vehicleId": 200000008, "type": "MH", "year": 2012, "make": "HOMCO IND. LTD DIPLOMAT", "serialNumber": "999999", "manufacturedHomeRegistrationNumber": "220000"}], "deleteVehicleCollateral": [{"vehicleId": 200000006, "type": "MV", "year": 2018, "make": "FORD", "model": "FIESTA", "serialNumber": "T346JU622994"}], "statementType": "CHANGE_STATEMENT"}]}}]',
'TEST_CALLBACK_URL', null)
;

-- Existing pending large search result report tracking max errors exceeded
INSERT INTO search_requests(id, search_ts, search_type, api_criteria, search_response,
                         account_id, pay_invoice_id, pay_path, client_reference_id, total_results_size, returned_results_size)
  VALUES(200000010, CURRENT_TIMESTAMP  at time zone 'utc', 'RG',
         '{"type": "REGISTRATION_NUMBER", "criteria": {"value": "TEST0001"}, "clientReferenceId": "T-S-RG-002"}',
         '[{"matchType": "EXACT", "registrationNumber": "TEST0001", "baseRegistrationNumber": "TEST0001", "createDateTime": "2021-01-06T11:35:57+00:00", "registrationType": "SA"}]',
         'PS12345', null, null, 'UT-SQ-RG-002', 76, 76)
;
INSERT INTO search_results(search_id, exact_match_count, similar_match_count, api_result, registrations, callback_url, doc_storage_url)
   VALUES(200000010, 76, 0, '[]',
'[{"matchType": "EXACT", "financingStatement": {"type": "SA", "baseRegistrationNumber": "TEST0001", "registrationDescription": "PPSA SECURITY AGREEMENT", "registrationAct": "PPSA SECURITY ACT", "createDateTime": "2021-03-12T01:48:53+00:00", "clientReferenceId": "TEST-SA-0001", "registeringParty": {"personName": {"first": "TEST", "last": "REGISTERING", "middle": "1"}, "address": {"street": "TEST-0001", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, "securedParties": [{"partyId": 200000004, "code": "200000000", "businessName": "TEST SECURED PARTY", "address": {"street": "TEST 200000000", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}, "emailAddress": "test-sp-client@gmail.com"}, {"partyId": 200000026, "businessName": "TEST 9 CHANGE TRANSFER SECURED PARTY", "address": {"street": "TEST-00C9", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}], "debtors": [{"partyId": 200000002, "businessName": "TEST BUS 2 DEBTOR", "address": {"street": "TEST-0001", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, {"partyId": 200000024, "businessName": "TEST 8 TRANSFER DEBTOR", "address": {"street": "TEST-00C8", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}], "generalCollateral": [{"collateralId": 200000003, "description": "TEST GENERAL COLLATERAL CHANGE ADD."}, {"collateralId": 200000000, "description": "TEST0001 GC 1"}], "vehicleCollateral": [{"vehicleId": 200000007, "type": "MV", "year": 2014, "make": "BMW", "model": "Z4", "serialNumber": "JU622994"}, {"vehicleId": 200000008, "type": "MH", "year": 2012, "make": "HOMCO IND. LTD DIPLOMAT", "serialNumber": "999999", "manufacturedHomeRegistrationNumber": "220000"}, {"vehicleId": 200000000, "type": "MV", "year": 2018, "make": "HYUNDAI", "model": "TUSCON", "serialNumber": "KM8J3CA46JU622994"}], "trustIndenture": true, "lifeYears": 2, "expiryDate": "2023-03-12T01:48:53+00:00", "changes": [{"baseRegistrationNumber": "TEST0001", "createDateTime": "2021-03-12T01:48:54+00:00", "changeRegistrationNumber": "TEST0010", "changeType": "SU", "clientReferenceId": "TEST-CH-0010", "registeringParty": {"personName": {"first": "TEST-CHANGE-SU", "last": "REGISTERING", "middle": "10"}, "address": {"street": "TEST-0010", "city": "city", "region": "BC", "country": "CA", "postalCode": "V8R3A5", "streetAdditional": "line 2"}}, "addGeneralCollateral": [{"collateralId": 200000003, "description": "TEST GENERAL COLLATERAL CHANGE ADD."}], "deleteGeneralCollateral": [{"collateralId": 200000002, "description": "TEST GENERAL COLLATERAL AMEND ADD."}], "addVehicleCollateral": [{"vehicleId": 200000007, "type": "MV", "year": 2014, "make": "BMW", "model": "Z4", "serialNumber": "JU622994"}, {"vehicleId": 200000008, "type": "MH", "year": 2012, "make": "HOMCO IND. LTD DIPLOMAT", "serialNumber": "999999", "manufacturedHomeRegistrationNumber": "220000"}], "deleteVehicleCollateral": [{"vehicleId": 200000006, "type": "MV", "year": 2018, "make": "FORD", "model": "FIESTA", "serialNumber": "T346JU622994"}], "statementType": "CHANGE_STATEMENT"}]}}]',
'TEST_CALLBACK_URL', null)
;

INSERT INTO event_tracking(id, key_id, event_ts, event_tracking_type, status, message, email_address)
  VALUES(200000000, 200000008, CURRENT_TIMESTAMP  at time zone 'utc', 'SEARCH_REPORT', 200, null, null);
INSERT INTO event_tracking(id, key_id, event_ts, event_tracking_type, status, message, email_address)
  VALUES(200000001, 200000009, CURRENT_TIMESTAMP  at time zone 'utc' + interval '2 minutes', 'SEARCH_REPORT', 500, 'some error 1', null);
INSERT INTO event_tracking(id, key_id, event_ts, event_tracking_type, status, message, email_address)
  VALUES(200000002, 200000010, CURRENT_TIMESTAMP  at time zone 'utc' + interval '2 minutes', 'SEARCH_REPORT', 500, 'some error 1', null);
INSERT INTO event_tracking(id, key_id, event_ts, event_tracking_type, status, message, email_address)
  VALUES(200000003, 200000010, CURRENT_TIMESTAMP  at time zone 'utc' + interval '4 minutes', 'SEARCH_REPORT', 500, 'some error 2', null);
INSERT INTO event_tracking(id, key_id, event_ts, event_tracking_type, status, message, email_address)
  VALUES(200000004, 200000010, CURRENT_TIMESTAMP  at time zone 'utc' + interval '6 minutes', 'SEARCH_REPORT', 500, 'some error 3', null);
INSERT INTO event_tracking(id, key_id, event_ts, event_tracking_type, status, message, email_address)
  VALUES(200000005, 200000011, CURRENT_TIMESTAMP  at time zone 'utc', 'API_NOTIFICATION', null, null, null);
INSERT INTO event_tracking(id, key_id, event_ts, event_tracking_type, status, message, email_address)
  VALUES(200000006, 200000012, CURRENT_TIMESTAMP  at time zone 'utc', 'EMAIL', null, null, null);
INSERT INTO event_tracking(id, key_id, event_ts, event_tracking_type, status, message, email_address)
  VALUES(200000007, 200000013, CURRENT_TIMESTAMP  at time zone 'utc', 'SURFACE_MAIL', null, null, null);
INSERT INTO event_tracking(id, key_id, event_ts, event_tracking_type, status, message, email_address)
  VALUES(200000008, 200000014, CURRENT_TIMESTAMP  at time zone 'utc', 'EMAIL_REPORT', null, null, null);
INSERT INTO event_tracking(id, key_id, event_ts, event_tracking_type, status, message, email_address)
  VALUES(200000009, 200000010, CURRENT_TIMESTAMP  at time zone 'utc' + interval '8 minutes', 'SEARCH_REPORT', 500, 'max retries 4', null);
