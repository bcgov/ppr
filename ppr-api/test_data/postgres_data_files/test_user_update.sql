-- Set the user id for all test registrations
UPDATE registrations
   SET user_id = 'TESTUSER'
 WHERE id >= 200000000
   AND user_id IS NULL
;
UPDATE drafts
   SET user_id = 'TESTUSER'
 WHERE id >= 200000000
   AND user_id IS NULL
;

-- staff roles other account registrations
INSERT INTO user_extra_registrations(id, account_id, registration_number, removed_ind)
  VALUES(200000004, 'ppr_staff', 'TEST0001', null)
;
INSERT INTO user_extra_registrations(id, account_id, registration_number, removed_ind)
  VALUES(200000005, 'helpdesk', 'TEST0001', null)
;
INSERT INTO user_extra_registrations(id, account_id, registration_number, removed_ind)
  VALUES(200000006, 'gov_account_user', 'TEST0001', null)
;
