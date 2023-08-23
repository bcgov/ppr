-- Post staging tables load step 7:
-- Transform legacy addresses: parse a single address column into an addresses table record.
-- 1. Using a temp sequence to generate the primary keys for the staging_mhr_adresses table while testing.
--    Use the actual addresses sequence when ready for the final load.
-- 2. Create staging_mhr_addresses records from staging_mhr_document.address. Populate staging_mhr_document.address_id.
-- 3. Create staging_mhr_addresses records from staging_mhr_owner.ownraddr, ownrpoco. Populate staging_mhr_owner.address_id.
-- 4. Create staging_mhr_addresses records from staging_mhr_note.address. Populate staging_mhr_note.address_id.
-- 5. Create staging_mhr_addresses records from staging_mhr_location.stnumber,stname,towncity,province. Populate staging_mhr_location.address_id.

-- Correct postal codes identified as mistakes. 
UPDATE staging_mhr_owner SET ownrpoco = REPLACE(ownrpoco, 'VOC 2CO', 'V0C 2C0')
 WHERE manhomid in ('3020')
   AND ownrpoco = 'VOC 2CO'
;
UPDATE staging_mhr_owner SET ownrpoco = REPLACE(ownrpoco, 'VOC 2C0', 'V0C 2C0')
 WHERE manhomid in ('54920')
   AND ownrpoco = 'VOC 2C0'
;
UPDATE staging_mhr_owner SET ownrpoco = REPLACE(ownrpoco, 'VOE 1TO', 'V0E 1T0')
 WHERE manhomid in ('51827')
   AND ownrpoco = 'VOE 1TO'
;


-- Document submitting party addresses ~398000 address records
-- Do this to find and remove region and country text.
UPDATE staging_mhr_document
   SET address = address || ' '
 WHERE address IS NOT NULL
   AND LENGTH(address) < 160;


UPDATE staging_mhr_document SET address = REPLACE(address, 'VOJ 3A0', 'V0J 3A0')
 WHERE documtid in ('50366290')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOM 2GO', 'V0M 2G0')
 WHERE documtid in ('42405085')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOK-1GO', 'V0K 1G0')
 WHERE documtid in ('41261400')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOK 2E0', 'V0K 2E0')
 WHERE documtid in ('90001652')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOG 2G0', 'V0G 2G0')
 WHERE documtid in ('90010361')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOE1E0', 'V0E 1E0')
 WHERE documtid in ('90011615')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'V0B  1M1', 'V0B 1M1')
 WHERE documtid in ('90012858')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOJ 2NO', 'V0J 2N0')
 WHERE documtid in ('REG01980')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VIE-3B3', 'V1E 3B3')
 WHERE documtid in ('10003812')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOK 2GO', 'V0K 2G0')
 WHERE documtid in ('40882544')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'V0K-1G0', 'V0K 1G0')
 WHERE documtid in ('41261400')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOC 1VO', 'V0C 1V0')
 WHERE documtid in ('41267752')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOX 1NO', 'V0X 1N0')
 WHERE documtid in ('41268797')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOJ 1EO', 'V0J 1E0')
 WHERE documtid in ('41400028')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOB 1LO', 'V0B 1L0')
 WHERE documtid in ('42418614')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOR 2EO', 'V0R 2E0')
 WHERE documtid in ('42427285')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOK 2J8', 'V0K 2J8')
 WHERE documtid in ('42463798')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOH 1HO', 'V0H 1H0')
 WHERE documtid in ('43306617')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOJ 1EO', 'V0J 1E0')
 WHERE documtid in ('43323331', '44250256')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'V1J 3JS', 'V1J 3J5')
 WHERE documtid in ('43347404')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOE 1EO', 'V0E 1E0')
 WHERE documtid in ('43402433')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VIE 4N2', 'V1E 4N2')
 WHERE documtid in ('43404609')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'T58 2T8', '5T8 2T8')
 WHERE documtid in ('50605344')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOH 1H0', 'V0H 1H0')
 WHERE documtid in ('62624088')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOG 1GO', 'V0G 1G0')
 WHERE documtid in ('90004584', '90004629', '90004630')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOG1HO', 'V0G 1H0')
 WHERE documtid in ('90007310')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'V7J 3PS', 'V7J 3P5')
 WHERE documtid in ('90013209')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOK 1S0', 'V0K 1S0')
 WHERE documtid in ('90010039')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VQT 2B6', 'V0T 2B6')
 WHERE documtid in ('63115572')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOG 1MO', 'V0G 1M0')
 WHERE documtid in ('43589009')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOK 2GO', 'V0K 2G0')
 WHERE documtid in ('43304664')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOJ 1EO', 'V0J 1E0')
 WHERE documtid in ('41400046')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOK 2EO', 'V0K 2E0')
 WHERE documtid in ('41233414')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VOH 1TO', 'V0H 1T0')
 WHERE documtid in ('40850953')
;
UPDATE staging_mhr_document SET address = REPLACE(address, 'VON 2KO', 'V0N 2K0')
 WHERE documtid in ('44250336')
;
UPDATE staging_mhr_document SET address = TRIM(REPLACE(address, 'MARK ELLIS', '')) || ' '
 WHERE documtid in ('10003812')
;


-- ~25 records
SELECT mhr_conversion_address_document('REG', true);  

-- ~123000 records
SELECT mhr_conversion_address_document('1', true);  

-- ~50000 records
SELECT mhr_conversion_address_document('8', true);  

-- ~1400 records
SELECT mhr_conversion_address_document('9', true);  

-- ~147000 records
SELECT mhr_conversion_address_document('', true);  

-- ~6 records
SELECT mhr_conversion_address_document('REG', false);  

-- ~13000 records
SELECT mhr_conversion_address_document('1', false);  

-- ~50000 records
SELECT mhr_conversion_address_document('8', false);  

-- ~13000 records
SELECT mhr_conversion_address_document('9', false);  

-- ~51000 records
SELECT mhr_conversion_address_document('', false);  

-- ~ 260 records
UPDATE staging_mhr_addresses
   SET region = 'BC', country = 'CA'
 WHERE country IS NULL
   AND city IS NOT NULL
   AND mhr_conversion_is_bc_city(city)
;

-- ~25 rows
UPDATE staging_mhr_addresses
   SET region = 'BC', country = 'CA'
 WHERE country IS NULL
   AND street_additional IS NOT NULL
   AND (street_additional LIKE '%SALMON ARM%' OR street_additional LIKE '%PEMBERTON%')
;

-- ~8 rows
UPDATE staging_mhr_addresses
   SET region = 'BC', country = 'CA'
 WHERE country IS NULL
   AND city IS NOT NULL
   AND city in ('VIC', 'VICT')
;

UPDATE staging_mhr_addresses
   SET country = 'CA'
 WHERE id IN (select d.address_id
                from staging_mhr_document d, staging_mhr_manuhome m, staging_mhr_addresses a
               where m.mhstatus = 'R'
                 and m.mhregnum = d.mhregnum
                 and d.address is not null
                 and d.address_id = a.id
                 and a.country is null)
;


-- Owner addresses ~493000 address records
-- Do this to find and remove region and country text.
UPDATE staging_mhr_owner
   SET ownraddr = ownraddr || ' '
 WHERE ownraddr IS NOT NULL
   AND LENGTH(ownraddr) < 160;


-- ~57000 records
SELECT mhr_conversion_address_owner(1, 10000);  

-- ~54000 records
SELECT mhr_conversion_address_owner(10001, 20000);  

-- ~46000 records
SELECT mhr_conversion_address_owner(20001, 30000);  

-- ~44000 records
SELECT mhr_conversion_address_owner(30001, 40000);  

-- ~40000 records
SELECT mhr_conversion_address_owner(40001, 50000);  

-- ~38000 records
SELECT mhr_conversion_address_owner(50001, 60000);  

-- ~43000 records
SELECT mhr_conversion_address_owner(60001, 70000);  

-- ~46000 records
SELECT mhr_conversion_address_owner(70001, 80000);  

-- ~49000 records
SELECT mhr_conversion_address_owner(80001, 90000);  

-- ~47000 records
SELECT mhr_conversion_address_owner(90001, 100000);  

-- ~32000 records
SELECT mhr_conversion_address_owner(100001, 115000);  

-- ~300 records
UPDATE staging_mhr_addresses
   SET region = 'BC', country = 'CA'
 WHERE country IS NULL
   AND city IS NOT NULL
   AND mhr_conversion_is_bc_city(city)
;

UPDATE staging_mhr_addresses
   SET country = 'CA'
 WHERE id IN (SELECT o.address_id
                FROM staging_mhr_owner o
               WHERE o.manhomid = 107596
                 AND o.ownraddr LIKE '% BC %')
;
UPDATE staging_mhr_addresses
   SET country = 'US', region = 'WA'
 WHERE id IN (SELECT o.address_id
                FROM staging_mhr_owner o
               WHERE o.manhomid = 92750
                 AND o.ownraddr LIKE '% REDMOND %')
;
UPDATE staging_mhr_addresses
   SET country = 'CA'
 WHERE id IN (select o.address_id
                from staging_mhr_owner o, staging_mhr_owngroup og, staging_mhr_manuhome m, staging_mhr_addresses a
               where m.mhstatus = 'R'
                 and m.manhomid = og.manhomid
                 and og.status = '3'
                 and og.manhomid = o.manhomid
                 and og.owngrpid = o.owngrpid
                 and o.address_id = a.id
                 and a.country is null)
;


-- unit note addresses
UPDATE staging_mhr_note
   SET address = address || ' '
 WHERE address IS NOT NULL
   AND LENGTH(address) < 160;


UPDATE staging_mhr_note SET address = REPLACE(address, 'V7J 3PS', 'V7J 3P5')
 WHERE regdocid in ('90013209')
;
UPDATE staging_mhr_note SET address = REPLACE(address, 'VOG 1GO', 'V0G 1G0')
 WHERE regdocid in ('90004630')
;
UPDATE staging_mhr_note SET address = REPLACE(address, 'V0B  1M1', 'V0B 1M1 ')
 WHERE regdocid in ('90012858')
;
UPDATE staging_mhr_note SET address = REPLACE(address, 'VON 2KO', 'V0N 2K0')
 WHERE regdocid in ('44250336')
;
UPDATE staging_mhr_note SET address = REPLACE(address, 'VOE1E0 ', 'V0E 1E0')
 WHERE regdocid in ('90011615')
;
UPDATE staging_mhr_note SET address = REPLACE(address, 'VOJ 1EO ', 'V0J 1E0')
 WHERE regdocid in ('41400028', '43323331', '44250256')
;

-- ~4500 records
SELECT mhr_conversion_address_note();  

-- ~ records
UPDATE staging_mhr_addresses
   SET region = 'BC', country = 'CA'
 WHERE country IS NULL
   AND city IS NOT NULL
   AND mhr_conversion_is_bc_city(city)
;

-- ~77,400 records
UPDATE staging_mhr_note
   SET address_id = staging_mhr_document.address_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_note.regdocid
   AND staging_mhr_note.name IS NOT NULL
   AND staging_mhr_note.address_id IS NULL
;


UPDATE staging_mhr_addresses
   SET region = 'BC', country = 'CA'
 WHERE id IN (SELECT n.address_id
                FROM staging_mhr_note n, staging_mhr_manuhome m, staging_mhr_addresses a
               WHERE m.mhstatus = 'R'
                 AND m.manhomid = n.manhomid
                 AND n.status = 'A'
                 AND n.address is not null
                 AND n.address like '% BC %'
                 AND n.address_id = a.id
                 AND a.country is null)
;
UPDATE staging_mhr_addresses
   SET region = 'BC', country = 'CA'
 WHERE id IN (SELECT n.address_id
                FROM staging_mhr_note n, staging_mhr_manuhome m, staging_mhr_addresses a
               WHERE m.mhstatus = 'R'
                 AND m.manhomid = n.manhomid
                 AND n.status = 'A'
                 AND n.address is not null
                 AND (n.address like '%BURNS LAKE%' or n.address like '%PORT MCNEILL%' or n.address like '%DAWSON CREEK%' or 
                      n.address like '%SUNSINE COAST%' or n.address like '%NORTH FRASER%')
                 AND n.address_id = a.id
                 AND a.country is null)
;
UPDATE staging_mhr_addresses
   SET country = 'CA'
 WHERE id IN (SELECT n.address_id
                FROM staging_mhr_note n, staging_mhr_manuhome m, staging_mhr_addresses a
               WHERE m.mhstatus = 'R'
                 AND m.manhomid = n.manhomid
                 AND n.status = 'A'
                 AND n.address is not null
                 AND n.address_id = a.id
                 AND a.country is null)
;


-- location addresses ~198000 address records
-- ~97000 records
SELECT mhr_conversion_address_location(1, 60000);

-- ~102000 records
SELECT mhr_conversion_address_location(60001, 115000);

-- ~ records
UPDATE staging_mhr_addresses
   SET region = 'BC', country = 'CA'
 WHERE country IS NULL
   AND city IS NOT NULL
   AND mhr_conversion_is_bc_city(city)
;


UPDATE staging_mhr_addresses
   SET country = 'CA'
 WHERE country IS NOT NULL AND TRIM(country) = ''
;


UPDATE staging_mhr_addresses
   SET city = NULL
 WHERE city IS NOT NULL AND TRIM(city) = ''
;


UPDATE staging_mhr_addresses
   SET street_additional = NULL
 WHERE street_additional IS NOT NULL AND TRIM(street_additional) = ''
;

