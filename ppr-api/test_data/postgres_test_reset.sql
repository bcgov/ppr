-- Delete all test data created with the scripts in this directory.
DELETE FROM search_results
  WHERE search_id >= 200000000;
DELETE FROM search_requests
  WHERE id >= 200000000;
DELETE FROM serial_collateral
  WHERE financing_id >= 200000000;
DELETE FROM general_collateral
  WHERE financing_id >= 200000000;
DELETE FROM general_collateral_legacy
  WHERE financing_id >= 200000000;
DELETE FROM parties
  WHERE financing_id >= 200000000;
DELETE FROM trust_indentures
  WHERE financing_id >= 200000000;
DELETE FROM court_orders
  WHERE registration_id >= 200000000;
DELETE FROM registrations
  WHERE financing_id >= 200000000;
DELETE FROM previous_financing_statements
  WHERE financing_id >= 200000000;
DELETE FROM financing_statements
  WHERE id >= 200000000;
DELETE FROM drafts
  WHERE id >= 200000000;
DELETE FROM client_codes_historical
  WHERE id >= 200000000;
DELETE FROM client_codes
  WHERE id >= 200000000;
DELETE FROM addresses
  WHERE id >= 200000000;
DELETE FROM client_codes
  WHERE id BETWEEN 99990001 AND 99990004;
DELETE FROM addresses
  WHERE id BETWEEN 99990001 AND 99990004;
DELETE FROM users
  WHERE id >= 200000000;
DELETE FROM user_extra_registrations
  WHERE id >= 200000000;
DELETE FROM account_bcol_ids
  WHERE id >= 200000000;
DELETE FROM event_tracking
  WHERE id >= 200000000;
-- Delete test data end
