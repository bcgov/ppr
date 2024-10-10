-- Set up final load primary keys (registration id's):
-- 1. Set staging_mhr_document.registration id 
-- 2. Set staging_mhr_note registration_id and change_registration_id
-- 3. Set staging_mhr_description registration_id and change_registration_id
-- 4. Set staging_mhr_location registration_id and change_registration_id
-- 5. Set staging_mhr_owngroup registration_id and change_registration_id
-- 6. Set staging_mhr_owner registration_id and change_registration_id


/*
Issues spreadsheet row 23.
delete 
  from staging_mhr_document
 where documtid = '41444482'
;

Correct orphaned document record with wrong mhr number
update staging_mhr_document
   set mhregnum = '083555', status_type = 'ACTIVE'
where mhregnum = '078216'
;
*/


-- Generate registration id's.
SELECT setval('staging_mhr_reg_id_seq', 1);
-- ~476000 records 
SELECT mhr_conversion_reg_id();


-- Update staging_mhr_note set registration_id, change_registration_id
-- ~82000 records
UPDATE staging_mhr_note
   SET registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_note.regdocid
;

-- ~3700 records
UPDATE staging_mhr_note
   SET change_registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_note.candocid
;


-- Update staging_mhr_description set registration_id, change_registration_id
-- ~53000 records
UPDATE staging_mhr_description
   SET registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_description.regdocid
   AND staging_mhr_description.manhomid BETWEEN 1 and 50000
;

-- ~62000 records
UPDATE staging_mhr_description
   SET registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_description.regdocid
   AND staging_mhr_description.manhomid >= 50001
;


-- ~4300 records
UPDATE staging_mhr_description
   SET change_registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_description.candocid
   AND staging_mhr_description.candocid IS NOT NULL
   AND staging_mhr_description.manhomid BETWEEN 1 and 50000
;

-- ~4200 records
UPDATE staging_mhr_description
   SET change_registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_description.candocid
   AND staging_mhr_description.candocid IS NOT NULL
   AND staging_mhr_description.manhomid >= 50001
;


-- Update staging_mhr_location set registration_id, change_registration_id
-- ~81000 records
UPDATE staging_mhr_location
   SET registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_location.regdocid
   AND staging_mhr_location.manhomid BETWEEN 1 and 50000
;

-- ~117000 records
UPDATE staging_mhr_location
   SET registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_location.regdocid
   AND staging_mhr_location.manhomid >= 50001
;

-- ~33000 records
UPDATE staging_mhr_location
   SET change_registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_location.candocid
   AND staging_mhr_location.candocid IS NOT NULL
   AND staging_mhr_location.manhomid BETWEEN 1 and 50000
;

-- ~59000 records
UPDATE staging_mhr_location
   SET change_registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_location.candocid
   AND staging_mhr_location.candocid IS NOT NULL
   AND staging_mhr_location.manhomid >= 50001
;

-- Update staging_mhr_owngroup set registration_id, change_registration_id
-- ~75000 records
UPDATE staging_mhr_owngroup
   SET registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_owngroup.regdocid
   AND staging_mhr_owngroup.manhomid BETWEEN 1 and 20000
;

-- ~63000 records
UPDATE staging_mhr_owngroup
   SET registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_owngroup.regdocid
   AND staging_mhr_owngroup.manhomid BETWEEN 20001 and 40000
;

-- ~56000 records
UPDATE staging_mhr_owngroup
   SET registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_owngroup.regdocid
   AND staging_mhr_owngroup.manhomid BETWEEN 40001 and 60000
;

-- ~65000 records
UPDATE staging_mhr_owngroup
   SET registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_owngroup.regdocid
   AND staging_mhr_owngroup.manhomid BETWEEN 60001 and 80000
;

-- ~74000 records
UPDATE staging_mhr_owngroup
   SET registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_owngroup.regdocid
   AND staging_mhr_owngroup.manhomid BETWEEN 80001 and 100000
;

-- ~26000 records
UPDATE staging_mhr_owngroup
   SET registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_owngroup.regdocid
   AND staging_mhr_owngroup.manhomid >= 100001
;

-- ~68000 records
UPDATE staging_mhr_owngroup
   SET change_registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_owngroup.candocid
   AND staging_mhr_owngroup.candocid IS NOT NULL
   AND staging_mhr_owngroup.manhomid BETWEEN 1 and 25000
;

-- ~50000 records
UPDATE staging_mhr_owngroup
   SET change_registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_owngroup.candocid
   AND staging_mhr_owngroup.candocid IS NOT NULL
   AND staging_mhr_owngroup.manhomid BETWEEN 25001 and 50000
;

-- ~51000 records
UPDATE staging_mhr_owngroup
   SET change_registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_owngroup.candocid
   AND staging_mhr_owngroup.candocid IS NOT NULL
   AND staging_mhr_owngroup.manhomid BETWEEN 50001 and 75000
;

-- ~84000 records
UPDATE staging_mhr_owngroup
   SET change_registration_id = staging_mhr_document.registration_id 
  FROM staging_mhr_document
 WHERE staging_mhr_document.documtid = staging_mhr_owngroup.candocid
   AND staging_mhr_owngroup.candocid IS NOT NULL
   AND staging_mhr_owngroup.manhomid >= 75001
;


-- Update staging_mhr_owner set registration_id, change_registration_id
-- ~134000 records
UPDATE staging_mhr_owner
   SET registration_id = staging_mhr_owngroup.registration_id,
       change_registration_id = staging_mhr_owngroup.change_registration_id
  FROM staging_mhr_owngroup
 WHERE staging_mhr_owngroup.manhomid = staging_mhr_owner.manhomid
   AND staging_mhr_owngroup.owngrpid = staging_mhr_owner.owngrpid
   AND staging_mhr_owngroup.manhomid BETWEEN 1 and 25000
;

-- ~106000 records
UPDATE staging_mhr_owner
   SET registration_id = staging_mhr_owngroup.registration_id,
       change_registration_id = staging_mhr_owngroup.change_registration_id
  FROM staging_mhr_owngroup
 WHERE staging_mhr_owngroup.manhomid = staging_mhr_owner.manhomid
   AND staging_mhr_owngroup.owngrpid = staging_mhr_owner.owngrpid
   AND staging_mhr_owngroup.manhomid BETWEEN 25001 and 50000
;

-- ~103000 records
UPDATE staging_mhr_owner
   SET registration_id = staging_mhr_owngroup.registration_id,
       change_registration_id = staging_mhr_owngroup.change_registration_id
  FROM staging_mhr_owngroup
 WHERE staging_mhr_owngroup.manhomid = staging_mhr_owner.manhomid
   AND staging_mhr_owngroup.owngrpid = staging_mhr_owner.owngrpid
   AND staging_mhr_owngroup.manhomid BETWEEN 50001 and 75000
;

-- ~151000 records
UPDATE staging_mhr_owner
   SET registration_id = staging_mhr_owngroup.registration_id,
       change_registration_id = staging_mhr_owngroup.change_registration_id
  FROM staging_mhr_owngroup
 WHERE staging_mhr_owngroup.manhomid = staging_mhr_owner.manhomid
   AND staging_mhr_owngroup.owngrpid = staging_mhr_owner.owngrpid
   AND staging_mhr_owngroup.manhomid >= 75001
;

