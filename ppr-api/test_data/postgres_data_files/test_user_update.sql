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
