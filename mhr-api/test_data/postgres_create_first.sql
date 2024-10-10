-- Place any general or common use statements here.
DELETE FROM mhr_drafts WHERE id = 0;

INSERT INTO mhr_drafts(id, draft_number, account_id, registration_type, create_ts, draft, mhr_number, update_ts, user_id)
     VALUES (0, 'CONV-1', '0', 'MHREG', now() at time zone 'UTC', '{}',null, null, 'TESTUSER')
;

INSERT INTO mhr_extra_registrations(id, account_id, mhr_number, removed_ind)
    VALUES (200000000, 'PS12345', 'TEST01', null)
;

INSERT INTO mhr_extra_registrations(id, account_id, mhr_number, removed_ind)
    VALUES (200000001, 'PS12345', '045349', null)
;

DELETE FROM mhr_service_agreements WHERE id = 1;

INSERT INTO mhr_service_agreements(id, agreement_type, version, create_ts, doc_storage_url, current_version)
     VALUES (1, 'DEFAULT', 'v1', now() at time zone 'UTC', 'default/v1/QS-Terms-of-Use.pdf', 'Y')
;

INSERT INTO users(id, creation_date, username, sub, account_id, firstname, lastname, email, iss, idp_userid, login_source)
  VALUES(190000000, current_timestamp, 'UT-test-man', 'subject-190000000', '2617', 'TEST', 'MANUFACTURER', null, 'issuer', '190000000', 'IDIR')
;
INSERT INTO users(id, creation_date, username, sub, account_id, firstname, lastname, email, iss, idp_userid, login_source)
  VALUES(190000001, current_timestamp, 'UT-test-qa', 'subject-190000001', '3026', 'TEST', 'SUPPLIER', null, 'issuer', '190000001', 'IDIR')
;

INSERT INTO user_profiles(id, payment_confirmation, search_selection_confirmation, default_drop_downs, default_table_filters,
                          registrations_table, misc_preferences, service_agreements)
  VALUES (190000000, 'Y', 'Y', 'Y', 'Y', null, null, null)
;

INSERT INTO user_profiles(id, payment_confirmation, search_selection_confirmation, default_drop_downs, default_table_filters,
                          registrations_table, misc_preferences, service_agreements)
  VALUES (190000001, 'Y', 'Y', 'Y', 'Y', null, null, '{"agreementType": "DEFAULT", "version": "v1", "latestVersion": true, "accepted": true, "acceptedDateTime": "2023-08-11T22:07:37+00:00", "acceptAgreementRequired": true}')
;
