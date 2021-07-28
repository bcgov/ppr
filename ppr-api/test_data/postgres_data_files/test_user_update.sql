-- Set the user id for all test registrations
UPDATE registrations
   SET user_id = 'TESTUSER'
 WHERE id >= 200000000
;
UPDATE drafts
   SET user_id = 'TESTUSER'
 WHERE id >= 200000000
;
