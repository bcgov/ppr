-- PostgreSQL restore mhr_manufacturers table records from backup temp_mhr_manufacturers. 
-- Address records already exist.
-- Use a new stored procedure mhr_restore_manufacturer to:
-- 1. Insert party records from temp_mhr_parties
-- 2. Update party id's in temp_mhr_manufacturers 
-- 3. Insert into mhr_manufacturers from temp_mhr_parties.

/*
-- No longer use these.
DROP TABLE staging_mhr_manufacturer;
DROP FUNCTION mhr_conversion_address_manufacturer;
DROP FUNCTION mhr_conversion_manufacturer;
*/

ALTER SEQUENCE mhr_manufacturer_id_seq INCREMENT 1 START 1;

create or replace function public.mhr_restore_manufacturer() returns integer
  language plpgsql
as $$
declare
  cur_manufacturers cursor
             for select * 
                   from temp_mhr_manufacturers; 
  rec_man record;
  reg_id integer := 0;
  submitting_pid integer := 0;
  owner_pid integer := 0;
  dealer_pid integer := 0;
  counter integer := 0;
begin
  open cur_manufacturers;
  loop
    fetch cur_manufacturers into rec_man;
    exit when not found;
    
    counter := counter + 1;
    
    reg_id := nextval('mhr_registration_id_seq');
    submitting_pid := nextval('mhr_party_id_seq');
    owner_pid := nextval('mhr_party_id_seq');
    dealer_pid := nextval('mhr_party_id_seq');
    insert into mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id,
                                   pay_invoice_id, pay_path, user_id)
    (select reg_id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id, pay_invoice_id, pay_path, user_id
       from temp_mhr_registrations 
      where id = rec_man.registration_id);

    insert into mhr_parties(id, party_type, status_type, registration_id, change_registration_id, business_name, 
                            compressed_name, address_id, phone_number)
     (select submitting_pid, party_type, status_type, reg_id, reg_id, business_name,
             compressed_name, address_id, phone_number
        from temp_mhr_parties
      where id = rec_man.submitting_party_id);

    insert into mhr_parties(id, party_type, status_type, registration_id, change_registration_id, business_name, 
                            compressed_name, address_id, phone_number)
     (select owner_pid, party_type, status_type, reg_id, reg_id, business_name,
             compressed_name, address_id, phone_number
        from temp_mhr_parties
      where id = rec_man.owner_party_id);

    insert into mhr_parties(id, party_type, status_type, registration_id, change_registration_id, business_name, 
                            compressed_name, address_id, phone_number)
     (select dealer_pid, party_type, status_type, reg_id, reg_id, business_name,
             compressed_name, address_id, phone_number
        from temp_mhr_parties
      where id = rec_man.dealer_party_id);

    insert into mhr_manufacturers(id, registration_id, submitting_party_id, owner_party_id, dealer_party_id,
                                  manufacturer_name, account_id, bcol_account, dba_name, terms_accepted, authorization_name)
         values (nextval('mhr_manufacturer_id_seq'), reg_id, submitting_pid, owner_pid, dealer_pid, rec_man.manufacturer_name,
                 rec_man.account_id, rec_man.bcol_account, rec_man.dba_name, rec_man.terms_accepted, rec_man.authorization_name);
  end loop;
  close cur_manufacturers;
  return counter;
end;
$$;
