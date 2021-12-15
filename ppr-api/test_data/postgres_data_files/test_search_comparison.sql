-- TestSearchBatch business search
INSERT INTO test_search_batches(id, search_type, test_date, sim_val_business, sim_val_first_name, sim_val_last_name)
  VALUES(200000000, 'BS', CURRENT_TIMESTAMP, 0.6, 0.7, 0.8)
;
-- TestSearch pass, api == legacy
INSERT INTO test_searches(batch_id, id, search_criteria, run_time)
   VALUES(200000000, 300000000, 'BUSINESS SEARCH TEST 1', 0.1111)
;
-- TestSearchResult (party ids are not used)
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000000, 400000000, 'R7654321','BUSINESS SEARCH TEST 1', 0, 'E', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000000, 400000001, 'R7654322','BUSINESS SEARCH TEST 1', 1, 'E', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000000, 400000002, 'R7654323','BUSINESS SEARCH TEST 2', 0, 'S', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000000, 400000003, 'R7654324','BUSINESS SEARCH TEST 3', 1, 'S', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000000, 400000004, 'R7654321','{"businessName": "BUSINESS SEARCH TEST 1", "partyId": 200000002}', 0, 'E', 'api');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000000, 400000005, 'R7654322','{"businessName": "BUSINESS SEARCH TEST 1", "partyId": 200000003}', 1, 'E', 'api');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000000, 400000006, 'R7654323','{"businessName": "BUSINESS SEARCH TEST 2", "partyId": 200000004}', 0, 'S', 'api');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000000, 400000007, 'R7654324','{"businessName": "BUSINESS SEARCH TEST 3", "partyId": 200000005}', 1, 'S', 'api');

-- TestSearch pass, exact + similar fail
INSERT INTO test_searches(batch_id, id, search_criteria, run_time)
   VALUES(200000000, 300000001, 'BUSINESS SEARCH TEST 2', 0.2222)
;

-- TestSearchResult
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000001, 400000100, 'R0654321','BUSINESS SEARCH TEST 2', 0, 'E', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000001, 400000101, 'R0654322','BUSINESS SEARCH TEST 2', 1, 'E', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000001, 400000109, 'R0654327','BUSINESS SEARCH TEST 2', 2, 'E', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000001, 400000102, 'R0654323','BUSINESS SEARCH TEST 1', 0, 'S', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000001, 400000103, 'R0654324','BUSINESS SEARCH TEST 3', 1, 'S', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000001, 400000104, 'R0654326','BUSINESS SEARCH TEST 5', 2, 'S', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000001, 400000105, 'R0654327','{"businessName": "BUSINESS SEARCH TEST 2", "partyId": 200000006}', 0, 'E', 'api');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000001, 400000110, 'R0654321','{"businessName": "BUSINESS SEARCH TEST 2", "partyId": 200000007}', 1, 'E', 'api');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000001, 400000106, 'R0654323','{"businessName": "BUSINESS SEARCH TEST 1", "partyId": 200000008}', 0, 'S', 'api');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000001, 400000107, 'R0654325','{"businessName": "BUSINESS SEARCH TEST 4", "partyId": 200000009}', 1, 'S', 'api');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000001, 400000108, 'R0654324','{"businessName": "BUSINESS SEARCH TEST 3", "partyId": 200000010}', 2, 'S', 'api');

-- TestSearchBatch individual search
INSERT INTO test_search_batches(id, search_type, test_date, sim_val_business, sim_val_first_name, sim_val_last_name)
  VALUES(200000001, 'IS', CURRENT_TIMESTAMP, 0.6, 0.7, 0.8)
;
-- TestSearch pass, api == legacy. Name order = last, first, middle
INSERT INTO test_searches(batch_id, id, search_criteria, run_time)
   VALUES(200000001, 300000100, 'SEARCHTEST1 INDIVIDUAL', 0.1111)
;
-- TestSearchResult
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000100, 400000200, 'R7654321','SEARCHTEST1 INDIVIDUAL', 0, 'E', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000100, 400000201, 'R7654322','SEARCHTEST1 INDIVIDUAL', 1, 'E', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000100, 400000202, 'R7654323','SEARCHTEST2 INDIVIDUAL', 0, 'S', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000100, 400000203, 'R7654324','SEARCHTEST3 INDIVIDUAL', 1, 'S', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000100, 400000204, 'R7654321','{"personName": { "first": "INDIVIDUAL", "last": "SEARCHTEST1"}, "partyId": 200000002}', 0, 'E', 'api');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000100, 400000205, 'R7654322','{"personName": { "first": "INDIVIDUAL", "last": "SEARCHTEST1"}, "partyId": 200000003}', 1, 'E', 'api');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000100, 400000206, 'R7654323','{"personName": { "first": "INDIVIDUAL", "last": "SEARCHTEST2"}, "partyId": 200000004}', 0, 'S', 'api');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000100, 400000207, 'R7654324','{"personName": { "first": "INDIVIDUAL", "last": "SEARCHTEST3"}, "partyId": 200000005}', 1, 'S', 'api');

-- TestSearch pass, exact + similar fail
INSERT INTO test_searches(batch_id, id, search_criteria, run_time)
   VALUES(200000001, 300000101, 'SEARCHTEST2 INDIVIDUAL', 0.2222)
;

-- TestSearchResult
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000101, 400000300, 'R0654321','SEARCHTEST2 INDIVIDUAL', 0, 'E', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000101, 400000301, 'R0654322','SEARCHTEST2 INDIVIDUAL', 1, 'E', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000101, 400000309, 'R0654327','SEARCHTEST2 INDIVIDUAL', 2, 'E', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000101, 400000302, 'R0654323','SEARCHTEST1 INDIVIDUAL', 0, 'S', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000101, 400000303, 'R0654324','SEARCHTEST3 INDIVIDUAL', 1, 'S', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000101, 400000304, 'R0654326','SEARCHTEST5 INDIVIDUAL', 2, 'S', 'legacy');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000101, 400000305, 'R0654327','{"personName": { "first": "INDIVIDUAL", "last": "SEARCHTEST2"}', 0, 'E', 'api');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000101, 400000310, 'R0654321','{"personName": { "first": "INDIVIDUAL", "last": "SEARCHTEST2"}', 1, 'E', 'api');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000101, 400000306, 'R0654323','{"personName": { "first": "INDIVIDUAL", "last": "SEARCHTEST1"}', 0, 'S', 'api');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000101, 400000307, 'R0654325','{"personName": { "first": "INDIVIDUAL", "last": "SEARCHTEST4"}', 1, 'S', 'api');
INSERT INTO test_search_results(search_id, id, doc_id, details, index, match_type, source)
   VALUES(300000101, 400000308, 'R0654324','{"personName": { "first": "INDIVIDUAL", "last": "SEARCHTEST3"}', 2, 'S', 'api');
