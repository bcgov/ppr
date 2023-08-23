-- Post staging tables load step 4:
-- 1. Update document.docutype to Postgres values.
-- 2. Create Postgres status_type values from legacy status codes.
-- 3. Create Postgres owner group tenancy type values from legacy codes. 
-- 4. Create Postgres owner party type values from legacy data.
-- 5. Create Postres location location type values from legacy data.
-- 6. For active fractional owner group interest, parse interest text into integer numerator and denominator.
-- 7. For active description records parse makemodl into make and model.

-- staging_mhr_document.docutype map to target mhr_documents.document_type
UPDATE staging_mhr_document
   SET DOCUTYPE = 'REG_101', registration_type = 'MHREG'
 WHERE DOCUTYPE = '101'
;


UPDATE staging_mhr_document
   SET DOCUTYPE = 'REG_102', registration_type = 'DECAL_REPLACE'
 WHERE DOCUTYPE = '102'
;


UPDATE staging_mhr_document
   SET DOCUTYPE = 'REG_103', registration_type = 'PERMIT'
 WHERE DOCUTYPE = '103'
;


UPDATE staging_mhr_document
   SET DOCUTYPE = 'REG_103E', registration_type = 'PERMIT_EXTENSION'
 WHERE DOCUTYPE = '103E'
;


UPDATE staging_mhr_document
   SET registration_type = 'MHREG_CONVERSION'
 WHERE DOCUTYPE = 'CONV'
;


UPDATE staging_mhr_document
   SET registration_type = 'TRANS'
 WHERE DOCUTYPE = 'TRAN'
;


UPDATE staging_mhr_document
   SET registration_type = 'TRANS_AFFIDAVIT'
 WHERE DOCUTYPE = 'AFFE'
;


UPDATE staging_mhr_document
   SET registration_type = 'TRAND'
 WHERE DOCUTYPE = 'DEAT'
;


UPDATE staging_mhr_document
   SET registration_type = 'EXEMPTION_RES'
 WHERE DOCUTYPE = 'EXRS'
;


UPDATE staging_mhr_document
   SET registration_type = 'EXEMPTION_NON_RES'
 WHERE DOCUTYPE = 'EXNR'
;


UPDATE staging_mhr_document
   SET registration_type = 'TRANS_ADMIN'
 WHERE DOCUTYPE = 'LETA'
;


UPDATE staging_mhr_document
   SET registration_type = 'TRANS_WILL'
 WHERE DOCUTYPE = 'WILL'
;


-- The rest are reg staff only
UPDATE staging_mhr_document
   SET registration_type = 'REG_STAFF_ADMIN'
 WHERE registration_type IS NULL
;


-- Set registration status type
-- ~345000 records
UPDATE staging_mhr_document
   SET status_type = 'ACTIVE'
  FROM staging_mhr_manuhome 
 WHERE staging_mhr_manuhome.mhregnum = staging_mhr_document.mhregnum
   AND staging_mhr_manuhome.mhstatus = 'R'
;

-- ~129000 records
UPDATE staging_mhr_document
   SET status_type = 'EXEMPT'
  FROM staging_mhr_manuhome 
 WHERE staging_mhr_manuhome.mhregnum = staging_mhr_document.mhregnum
   AND staging_mhr_manuhome.mhstatus = 'E'
;

-- ~800 records
UPDATE staging_mhr_document
   SET status_type = 'CANCELLED'
  FROM staging_mhr_manuhome 
 WHERE staging_mhr_manuhome.mhregnum = staging_mhr_document.mhregnum
   AND staging_mhr_manuhome.mhstatus = 'C'
;



UPDATE staging_mhr_note
   SET DOCUTYPE = 'REG_101'
 WHERE DOCUTYPE = '101'
;


UPDATE staging_mhr_note
   SET DOCUTYPE = 'REG_102'
 WHERE DOCUTYPE = '102'
;


UPDATE staging_mhr_note
   SET DOCUTYPE = 'REG_103'
 WHERE DOCUTYPE = '103'
;


UPDATE staging_mhr_note
   SET DOCUTYPE = 'REG_103E'
 WHERE DOCUTYPE = '103E'
;


-- ~77000 records
UPDATE staging_mhr_note
   SET status_type = 'ACTIVE'
 WHERE status = 'A'
;

-- ~3700 records
UPDATE staging_mhr_note
   SET status_type = 'CANCELLED'
 WHERE status = 'C'
;

-- ~350 records
UPDATE staging_mhr_note
   SET status_type = 'EXPIRED'
 WHERE status = 'E'
;


-- ~107000 records
UPDATE staging_mhr_description
   SET status_type = 'ACTIVE'
 WHERE status = 'A'
;

-- ~9000 records
UPDATE staging_mhr_description
   SET status_type = 'HISTORICAL'
 WHERE status = 'H'
;


-- ~107000 records
UPDATE staging_mhr_location
   SET status_type = 'ACTIVE'
 WHERE status = 'A'
;

-- ~92000 records
UPDATE staging_mhr_location
   SET status_type = 'HISTORICAL'
 WHERE status = 'H'
;


-- ~76000 records
UPDATE staging_mhr_owngroup
   SET status_type = 'ACTIVE'
 WHERE status = '3'
;

-- ~33000 records
UPDATE staging_mhr_owngroup
   SET status_type = 'EXEMPT'
 WHERE status = '4'
;

-- ~251000 records
UPDATE staging_mhr_owngroup
   SET status_type = 'PREVIOUS'
 WHERE status in ('5', '6', '7')
;

-- ~223000 records
UPDATE staging_mhr_owngroup
   SET tenancy_type = 'SOLE'
 WHERE tenytype = 'SO'
;

-- ~127000 records
UPDATE staging_mhr_owngroup
   SET tenancy_type = 'JOINT'
 WHERE tenytype = 'JT'
;

-- ~8700 records
UPDATE staging_mhr_owngroup
   SET tenancy_type = 'COMMON'
 WHERE tenytype = 'TC'
;


-- ~225 records
UPDATE staging_mhr_owner
   SET party_type = 'TRUSTEE',
       description = ownrsuff,
       ownrsuff = null
 WHERE ownrsuff IS NOT NULL
   AND ownrsuff like '%BANKRUPT%'
;

-- ~75 records
/* Skip for now
UPDATE staging_mhr_owner
   SET party_type = 'TRUST',
       description = ownrsuff,
       ownrsuff = null
 WHERE ownrsuff IS NOT NULL
   AND ownrsuff like '%TRUST%'
   AND party_type IS NULL
;

*/
-- ~11000 records
UPDATE staging_mhr_owner
   SET party_type = 'EXECUTOR',
       description = ownrsuff,
       ownrsuff = null
 WHERE ownrsuff IS NOT NULL
   AND ownrsuff like '%EXEC%'
   AND party_type IS NULL
;

-- ~2300 records
UPDATE staging_mhr_owner
   SET party_type = 'ADMINISTRATOR',
       description = ownrsuff,
       ownrsuff = null
 WHERE ownrsuff IS NOT NULL
   AND ownrsuff like '%ADMIN%'
   AND party_type IS NULL
;

-- ~408000 records
UPDATE staging_mhr_owner
   SET party_type = 'OWNER_IND'
 WHERE ownrtype = 'I'
   AND party_type IS NULL
;

-- ~72000 records
UPDATE staging_mhr_owner
   SET party_type = 'OWNER_BUS'
 WHERE ownrtype = 'B'
   AND party_type IS NULL
;


-- ~35000 records
UPDATE staging_mhr_location
   SET location_type = 'MANUFACTURER'
 WHERE  mhdealer IS NOT NULL
;

-- ~74000 records
UPDATE staging_mhr_location
   SET location_type = 'MH_PARK'
 WHERE mahpname IS NOT NULL
   AND location_type IS NULL
;

-- ~3200 records
UPDATE staging_mhr_location
   SET location_type = 'RESERVE'
 WHERE adddesc IS NOT NULL
   AND location_type IS NULL
   AND (adddesc LIKE '%BAND%' OR adddesc LIKE '%INDIAN%' OR adddesc LIKE '%RESERVE%')
;

-- ~86000 records
UPDATE staging_mhr_location
   SET location_type = 'OTHER'
 WHERE location_type IS NULL
;


-- ~2300 records
UPDATE staging_mhr_owngroup
   SET interest_numerator = mhr_conversion_interest_fraction(interest, true),
       interest_denominator = mhr_conversion_interest_fraction(interest, false)
 WHERE status = '3'
   AND TRIM(interest) != ''
;
-- Conditionally update interest text: leave exceptions alone.
UPDATE staging_mhr_owngroup
   SET interest = 'UNDIVIDED'
 WHERE status = '3'
   AND interest IS NOT NULL
   AND interest LIKE 'UNDIVIDED %' 
   AND interest_numerator > 0
   AND interest_denominator > 0
   AND interest = 'UNDIVIDED ' || cast(interest_numerator as varchar) || '/' || cast(interest_denominator as varchar) 
;

UPDATE staging_mhr_owngroup
   SET interest = 'UNDIVIDED'
 WHERE status = '3'
   AND interest IS NOT NULL
   AND interest_numerator > 0
   AND interest_denominator > 0
   AND interest = cast(interest_numerator as varchar) || '/' || cast(interest_denominator as varchar) 
;

UPDATE staging_mhr_owngroup
   SET interest_numerator = mhr_conversion_interest_fraction(interest, true),
       interest_denominator = mhr_conversion_interest_fraction(interest, false)
 WHERE status != '3'
   AND interest is not null
   AND TRIM(interest) != ''
;
UPDATE staging_mhr_owngroup
   SET interest = 'UNDIVIDED'
 WHERE status != '3'
   AND interest IS NOT NULL
   AND interest LIKE 'UNDIVIDED %' 
   AND interest_numerator > 0
   AND interest_denominator > 0
   AND interest = 'UNDIVIDED ' || cast(interest_numerator as varchar) || '/' || cast(interest_denominator as varchar)
;

UPDATE staging_mhr_owngroup
   SET interest = 'UNDIVIDED'
 WHERE status != '3'
   AND interest IS NOT NULL
   AND interest_numerator > 0
   AND interest_denominator > 0
   AND interest = cast(interest_numerator as varchar) || '/' || cast(interest_denominator as varchar) 
;
UPDATE staging_mhr_owngroup
   SET interest = 'UNDIVIDED'
 WHERE interest IS NOT NULL
   AND interest_numerator > 0
   AND interest_denominator > 0
   AND interest IN ('A 45/100 INTEREST', 'A 55/100 INTEREST', 'AN UNDIVIDED 1/4', 'UNDIVIDED 1/2 INT.', 'UNDIVIDED 49.5/100',
                    'UNDIVIDED 50/100THS', '1/2 UNDIVIDED', '1/6 UNDIVIDED', '16/37TH INTEREST', '21/37TH INTEREST',
                    '4/6 UNDIVIDED')
;

-- ~107000 records
UPDATE staging_mhr_description 
   SET make = mhr_conversion_make_model(makemodl, true), model = mhr_conversion_make_model(makemodl, false)
 WHERE status = 'A'
;
UPDATE staging_mhr_description 
   SET make = makemodl
 WHERE status != 'A'
;
UPDATE staging_mhr_description 
   SET model = NULL
 WHERE status = 'A'
   AND model IS NOT NULL
   AND TRIM(model) = ''
;
UPDATE staging_mhr_description 
   SET make = NULL
 WHERE status = 'A'
   AND make IS NOT NULL
   AND TRIM(make) = ''
;

