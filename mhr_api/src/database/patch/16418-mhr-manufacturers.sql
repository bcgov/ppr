-- PostgreSQL ETL steps for importing DB2 manufact table data into the mhr_manufactures table 
--
-- 1. Create table staging_mhr_manufacturer with the same definition as the DB2 manufact table.
-- 2. Outside of this script load data into staging_mhr_manufacturer from CSV file.
-- 3. Trim all character columns and set to null if empty.
-- 4. Add address id columns.
-- 5. Create functions to transform and load the manufacturer information. Requires migration address ETL functions.
-- 6. Create staging_mhr_addresses records from staging_mhr_manufacturer.subpaddr, ownraddr and ownrpoco, and stname, stnumber, towncity, and province.
--    Populate staging_mhr_manufacturer.submitting_address_id, owner_address_id, and dealer_address_id.
-- 7. Apply manual updates.
-- 8. Insert into final PostgreSQL tables mhr_registration, mhr_parties, mhr_manufacturers

DROP TABLE staging_mhr_manufacturer;
CREATE TABLE public.staging_mhr_manufacturer (
MANUFAID INTEGER PRIMARY KEY,
BCOLACCT VARCHAR (6),
MHDEALER VARCHAR (60),
SUBPNAME VARCHAR (40),
SUBPFONE VARCHAR (10),
SUBPADDR VARCHAR (160),
OWNRNAME VARCHAR (70),
OWNRFONE VARCHAR (10),
OWNRADDR VARCHAR (160),
OWNRPOCO VARCHAR (10),
STNUMBER VARCHAR (6),
STNAME   VARCHAR (25),
TOWNCITY VARCHAR (20),
PROVINCE VARCHAR (2),
MANUNAME VARCHAR (65)
);
select *
 from staging_mhr_manufacturer
;

-- load data here

DELETE
  FROM staging_mhr_manufacturer
 WHERE mhdealer LIKE 'BOBS TEST%'
;

UPDATE staging_mhr_manufacturer
   SET mhdealer = (CASE WHEN TRIM(mhdealer) = '' THEN NULL ELSE TRIM(mhdealer) END),
       subpname = (CASE WHEN TRIM(SUBPNAME) = '' THEN NULL ELSE TRIM(SUBPNAME) END),
       SUBPFONE = (CASE WHEN TRIM(SUBPFONE) = '' THEN NULL ELSE TRIM(SUBPFONE) END),
       SUBPADDR = (CASE WHEN TRIM(SUBPADDR) = '' THEN NULL ELSE TRIM(SUBPADDR) END),
       OWNRNAME = (CASE WHEN TRIM(OWNRNAME) = '' THEN NULL ELSE TRIM(OWNRNAME) END),
       OWNRFONE = (CASE WHEN TRIM(OWNRFONE) = '' THEN NULL ELSE TRIM(OWNRFONE) END),
       OWNRADDR = (CASE WHEN TRIM(OWNRADDR) = '' THEN NULL ELSE TRIM(OWNRADDR) END),
       OWNRPOCO = (CASE WHEN TRIM(OWNRPOCO) = '' THEN NULL ELSE TRIM(OWNRPOCO) END),
       STNAME = (CASE WHEN TRIM(STNAME) = '' THEN NULL ELSE TRIM(STNAME) END),
       STNUMBER = (CASE WHEN TRIM(STNUMBER) = '' THEN NULL ELSE TRIM(STNUMBER) END),
       TOWNCITY = (CASE WHEN TRIM(TOWNCITY) = '' THEN NULL ELSE TRIM(TOWNCITY) END),
       PROVINCE = (CASE WHEN TRIM(PROVINCE) = '' THEN NULL ELSE TRIM(PROVINCE) END),
       MANUNAME = (CASE WHEN TRIM(MANUNAME) = '' THEN NULL ELSE TRIM(MANUNAME) END)
;

ALTER TABLE staging_mhr_manufacturer
  ADD COLUMN submitting_address_id INTEGER NULL,
  ADD COLUMN owner_address_id INTEGER NULL,
  ADD COLUMN dealer_address_id INTEGER NULL
;


create or replace function public.mhr_conversion_address_manufacturer() returns integer
  language plpgsql
as $$
declare
  cur_addresses cursor 
            for select subpaddr, ownraddr, ownrpoco, stname, stnumber, towncity, province 
                  from staging_mhr_manufacturer
                 where subpaddr is not null;
  rec_address record;
  counter integer := 0;
  submitting_addr_id integer := 0;
  owner_addr_id integer := 0;
  dealer_addr_id integer := 0;
  street varchar(50);
  street_add varchar(50);
  city varchar(40);
  pcode varchar(15);
  region varchar(2);
  country varchar(2);
begin
  open cur_addresses;
  loop
    fetch cur_addresses into rec_address;
    exit when not found;
    counter := counter + 1;
    select * 
      from mhr_conversion_address(rec_address.subpaddr, '')
      into submitting_addr_id, street, street_add, city, region, pcode, country;
    submitting_addr_id := nextval('address_id_seq');
    city := TRIM(REPLACE(city, ',', ''));
    insert into addresses values(submitting_addr_id, street, street_add, city, region, pcode, country);

    select * 
      from mhr_conversion_address(rec_address.ownraddr, rec_address.ownrpoco)
      into owner_addr_id, street, street_add, city, region, pcode, country;
    owner_addr_id := nextval('address_id_seq');
    city := TRIM(REPLACE(city, ',', ''));
    insert into addresses values(owner_addr_id, street, street_add, city, region, pcode, country);

    dealer_addr_id := nextval('address_id_seq');
    if rec_address.province in ('ID', 'OR', 'MN', 'WA') then
      country := 'US';
    else
      country := 'CA';
    end if;
    if rec_address.towncity = city and rec_address.stnumber is not null and 
       trim(rec_address.stnumber || ' ' || rec_address.stname) = trim(street) then
       street_add := rec_address.ownrpoco; -- do nothing
    elsif rec_address.towncity = city and rec_address.stnumber is null and position(rec_address.stname in street) > 0 then
       street_add := rec_address.ownrpoco; -- do nothing
    else
      pcode := null;
    end if;
    if rec_address.stnumber is not null then
      insert into addresses values(dealer_addr_id, rec_address.stnumber || ' ' || rec_address.stname, null, rec_address.towncity, rec_address.province, pcode, country);
    else
      insert into addresses values(dealer_addr_id, rec_address.stname, null, rec_address.towncity, rec_address.province, pcode, country);
    end if;
    update staging_mhr_manufacturer 
       set submitting_address_id = submitting_addr_id, owner_address_id = owner_addr_id, dealer_address_id = dealer_addr_id 
     where current of cur_addresses;
  end loop;
  close cur_addresses;
  return counter;
end;
$$;


create or replace function public.mhr_conversion_manufacturer() returns integer
  language plpgsql
as $$
declare
  cur_manufacturers cursor
             for select * 
                   from staging_mhr_manufacturer; 
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
           values(reg_id, 'MAN' || to_char(counter, 'fm000'), 'SYSTEM', 'MANUFACTURER', now() at time zone 'UTC', 'ACTIVE', 0, null, null, null);

    insert into mhr_parties(id, party_type, status_type, registration_id, change_registration_id, business_name, 
                            compressed_name, address_id, phone_number)
        values(submitting_pid, 'SUBMITTING', 'ACTIVE', reg_id, reg_id, rec_man.subpname, 'XXXXXXXXXXXXX', 
               rec_man.submitting_address_id, rec_man.subpfone);
    insert into mhr_parties(id, party_type, status_type, registration_id, change_registration_id, business_name, 
                            compressed_name, address_id, phone_number)
        values(owner_pid, 'OWNER_BUS', 'ACTIVE', reg_id, reg_id, rec_man.ownrname, 'XXXXXXXXXXXXX', 
               rec_man.owner_address_id, null);
    insert into mhr_parties(id, party_type, status_type, registration_id, change_registration_id, business_name, 
                            compressed_name, address_id, phone_number)
        values(dealer_pid, 'MANUFACTURER', 'ACTIVE', reg_id, reg_id, rec_man.mhdealer, 'XXXXXXXXXXXXX', 
               rec_man.dealer_address_id, null);
    insert into mhr_manufacturers(id, registration_id, submitting_party_id, owner_party_id, dealer_party_id,
                                  manufacturer_name, account_id, bcol_account)
         values (nextval('mhr_manufacturer_id_seq'), reg_id, submitting_pid, owner_pid, dealer_pid, rec_man.manuname, null, null);
  end loop;
  close cur_manufacturers;
  return counter;
end;
$$;


UPDATE staging_mhr_manufacturer
   SET subpaddr = subpaddr || ' '
 WHERE subpaddr IS NOT NULL
   AND LENGTH(subpaddr) < 160;
UPDATE staging_mhr_manufacturer
   SET ownraddr = ownraddr || ' '
 WHERE ownraddr IS NOT NULL
   AND LENGTH(ownraddr) < 160;

UPDATE staging_mhr_manufacturer
   SET subpaddr = 'SHERRING INDUSTRIAL PARK                3501 GIFFEN ROAD NORTH                  LETHBRIDGE, AB T1H 0E8 '
 WHERE manufaid = 7
;
UPDATE staging_mhr_manufacturer
   SET subpaddr = 'PO BOX 5579                             BEND OR USA     97708 ',
       ownraddr = '20495 MURRAY ROAD                       BEND OR USA     97708 '
 WHERE manufaid = 25
;
UPDATE staging_mhr_manufacturer
   SET ownraddr = '700 SHAWNIGAN LAKE ROAD                 SHAWNIGAN LAKE, BC V0R2W3 '
 WHERE manufaid = 26
;
UPDATE staging_mhr_manufacturer
   SET subpaddr = 'RR1, S2,C23                             OKANAGAN FALLS B.C. V0H 1R0 '
 WHERE manufaid = 23
;

SELECT mhr_conversion_address_manufacturer();

UPDATE addresses
   SET city = 'RATHDRUM', street_additional = null, postal_code = '83858-1075'
 WHERE id IN (SELECT submitting_address_id FROM staging_mhr_manufacturer WHERE manufaid = 21)
;
UPDATE addresses
   SET city = 'RATHDRUM', street_additional = null, postal_code = '83858-1075'
 WHERE id IN (SELECT owner_address_id FROM staging_mhr_manufacturer WHERE manufaid = 21)
;

select *
  from mhr_drafts
where id = 0
;
-- Insert if it does not exist.
INSERT INTO mhr_drafts(id, draft_number, account_id, registration_type, create_ts, draft, mhr_number, update_ts, user_id)
     VALUES (0, 'CONV-1', '0', 'MHREG', now() at time zone 'UTC', '{}',null, null, 'TESTUSER')
;

SELECT mhr_conversion_manufacturer();

SELECT *
  FROM mhr_manufacturers
;
/*
-- Example to set some test account id's in DEV and TEST.
update mhr_manufacturers
   set account_id = '2617'
 where id = 4
;
*/
