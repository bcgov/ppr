-- Post staging tables load step 6:
-- Update legacy names: parse individual names into first, middle, last.
-- 1. Add and populate staging_mhr_owner business_name, last_name, first_name, middle_name.
-- 2. Add and populate staging_mhr_document submitting party business_name, last_name, first_name, middle_name, suffix.
-- 3. Add and populate staging_mhr_note contact party business_name, last_name, first_name, middle_name, suffix.

-- ~147000 records
UPDATE staging_mhr_owner
   SET last_name = TRIM(SUBSTR(ownrname, 1, 25)),
       first_name = TRIM(SUBSTR(ownrname, 26, 15)),
       middle_name = SUBSTR(ownrname, 41) 
 WHERE ownrtype = 'I'
   AND manhomid < 30000
;

-- ~114000 records
UPDATE staging_mhr_owner
   SET last_name = TRIM(SUBSTR(ownrname, 1, 25)),
       first_name = TRIM(SUBSTR(ownrname, 26, 15)),
       middle_name = SUBSTR(ownrname, 41) 
 WHERE ownrtype = 'I'
   AND manhomid BETWEEN 30001 AND 60000
;

-- ~118000 records
UPDATE staging_mhr_owner
   SET last_name = TRIM(SUBSTR(ownrname, 1, 25)),
       first_name = TRIM(SUBSTR(ownrname, 26, 15)),
       middle_name = SUBSTR(ownrname, 41) 
 WHERE ownrtype = 'I'
   AND manhomid BETWEEN 60001 AND 90000
;

-- ~42000 records
UPDATE staging_mhr_owner
   SET last_name = TRIM(SUBSTR(ownrname, 1, 25)),
       first_name = TRIM(SUBSTR(ownrname, 26, 15)),
       middle_name = SUBSTR(ownrname, 41) 
 WHERE ownrtype = 'I'
   AND manhomid > 90000
;


-- ~72000 records
UPDATE staging_mhr_owner
   SET business_name = ownrname
 WHERE ownrtype = 'B'
;


-- ~215 records Remove extra space characters.
UPDATE staging_mhr_document
   SET name = regexp_replace(name, '\s+', ' ', 'g')
 WHERE POSITION('  ' in name) > 0
;

-- staging_mhr_document submitting party target mhr_parties.business_name, first_name, middle_name, last_name, suffix
-- ~78000 records
UPDATE staging_mhr_document
   SET business_name = name
 WHERE documtid LIKE 'REG%'
   AND NOT public.mhr_conversion_is_individual(name)
;

-- ~123000 records
UPDATE staging_mhr_document
   SET business_name = name
 WHERE documtid LIKE '1%'
   AND NOT public.mhr_conversion_is_individual(name)
;

-- ~52000 records
UPDATE staging_mhr_document
   SET business_name = name
 WHERE documtid LIKE '8%' OR documtid LIKE '9%'
   AND NOT public.mhr_conversion_is_individual(name)
;

-- ~147000 records
UPDATE staging_mhr_document
   SET business_name = name
 WHERE documtid NOT LIKE 'REG%'
   AND documtid NOT LIKE '1%'
   AND documtid NOT LIKE '8%'
   AND documtid NOT LIKE '9%'
   AND NOT public.mhr_conversion_is_individual(name)
;

-- ~6 records
UPDATE staging_mhr_document
   SET first_name = public.mhr_conversion_individual_first(name),
       last_name = public.mhr_conversion_individual_last(name),
       middle_name = public.mhr_conversion_individual_middle(name),
       suffix = public.mhr_conversion_individual_suffix(name)
 WHERE documtid LIKE 'REG%'
   AND business_name IS NULL
   AND public.mhr_conversion_is_individual(name)
;

-- ~13000 records
UPDATE staging_mhr_document
   SET first_name = public.mhr_conversion_individual_first(name),
       last_name = public.mhr_conversion_individual_last(name),
       middle_name = public.mhr_conversion_individual_middle(name),
       suffix = public.mhr_conversion_individual_suffix(name)
 WHERE documtid LIKE '1%'
   AND business_name IS NULL
   AND public.mhr_conversion_is_individual(name)
;

-- ~64000 records
UPDATE staging_mhr_document
   SET first_name = public.mhr_conversion_individual_first(name),
       last_name = public.mhr_conversion_individual_last(name),
       middle_name = public.mhr_conversion_individual_middle(name),
       suffix = public.mhr_conversion_individual_suffix(name)
 WHERE documtid LIKE '8%' OR documtid LIKE '9%'
   AND business_name IS NULL
   AND public.mhr_conversion_is_individual(name)
;

-- ~51000 records
UPDATE staging_mhr_document
   SET first_name = public.mhr_conversion_individual_first(name),
       last_name = public.mhr_conversion_individual_last(name),
       middle_name = public.mhr_conversion_individual_middle(name),
       suffix = public.mhr_conversion_individual_suffix(name)
 WHERE documtid NOT LIKE 'REG%'
   AND documtid NOT LIKE '1%'
   AND documtid NOT LIKE '8%'
   AND documtid NOT LIKE '9%'
   AND business_name IS NULL
   AND public.mhr_conversion_is_individual(name)
;


-- Manual updates here
UPDATE staging_mhr_document
   SET last_name = TRIM(SPLIT_PART(name, ',', 1)),
       first_name = TRIM(SPLIT_PART(name, ',', 2)),
       middle_name = null, suffix = null
 WHERE position(',' in name) > 0
   AND last_name is not null
   AND name in ('VAN HOEK, SHIRLEY', 'VANDER KOOY, JAN', 'VAN DE VEN, L', 'DE ROSA, BIAGIO', 'DE BRUIN, WARREN',
                  'VAN DER NET, WIJNAND', 'VAN DER WYK, GERRITT')
;
UPDATE staging_mhr_document
   SET last_name = TRIM(SPLIT_PART(name, ',', 1)),
       first_name = TRIM(SPLIT_PART(name, ' ', 3)),
       middle_name = TRIM(SPLIT_PART(name, ' ', 4)),
       suffix = null
 WHERE position(',' in name) > 0
   AND last_name is not null
   AND name in ('VAN HEEK, DERRICK WILLIAM', 'DE STRAKE, BRYAN KELLY', 'VAN BEVEREN, MARTIN JOHN')
;
UPDATE staging_mhr_document
   SET last_name = TRIM(SPLIT_PART(name, ',', 1)),
       first_name = TRIM(SPLIT_PART(name, ' ', 4)),
       middle_name = TRIM(SPLIT_PART(name, ' ', 5)),
       suffix = null
 WHERE position(',' in name) > 0
   AND last_name is not null
   and name in ('VAN DER HOEVEN, NEIL DAVID')
;

UPDATE staging_mhr_document
   SET first_name = TRIM(SPLIT_PART(name, ' ', 1)),
       last_name = TRIM(SPLIT_PART(name, ' ', 2)) || ' ' || TRIM(SPLIT_PART(name, ' ', 3)),
       middle_name = null,
       suffix = null
 WHERE position(',' in name) < 1
   AND position('(' in name) < 1
   AND last_name is not null
   AND (name like '% VAN %' or name like '% DE %')
   AND SPLIT_PART(name, ' ', 4) = ''
   AND (TRIM(SPLIT_PART(name, ' ', 2)) IN ('VAN', 'DE'))
;
UPDATE staging_mhr_document
   SET first_name = TRIM(SPLIT_PART(name, ' ', 1)),
       last_name = TRIM(SPLIT_PART(name, ' ', 2)) || ' ' || TRIM(SPLIT_PART(name, ' ', 3)) || ' ' || TRIM(SPLIT_PART(name, ' ', 4)),
       middle_name = null,
       suffix = null
 WHERE position(',' in name) < 1
   AND position('(' in name) < 1
   AND last_name is not null
   AND (name like '% VAN %' or name like '% DE %')
   and SPLIT_PART(name, ' ', 4) != ''
   and SPLIT_PART(name, ' ', 5) = ''
   AND (TRIM(SPLIT_PART(name, ' ', 2)) IN ('VAN', 'DE'))
;
UPDATE staging_mhr_document
   SET first_name = TRIM(SPLIT_PART(name, ' ', 1)),
       middle_name = TRIM(SPLIT_PART(name, ' ', 2)),
       last_name = TRIM(SPLIT_PART(name, ' ', 3)) || ' ' || TRIM(SPLIT_PART(name, ' ', 4)),
       suffix = null
 WHERE position(',' in name) < 1
   AND position('(' in name) < 1
   AND last_name is not null
   AND (name like '% VAN %' or name like '% DE %')
   AND SPLIT_PART(name, ' ', 4) != ''
   AND SPLIT_PART(name, ' ', 5) = ''
   AND (TRIM(SPLIT_PART(name, ' ', 3)) IN ('VAN', 'DE'))
;
UPDATE staging_mhr_document
   SET first_name = TRIM(SPLIT_PART(name, ' ', 1)),
       middle_name = TRIM(SPLIT_PART(name, ' ', 2)),
       last_name = TRIM(SPLIT_PART(name, ' ', 3)) || ' ' || TRIM(SPLIT_PART(name, ' ', 4)) || ' ' || TRIM(SPLIT_PART(name, ' ', 5)),
       suffix = null
 WHERE position(',' in name) < 1
   AND position('(' in name) < 1
   AND last_name is not null
   AND (name like '% VAN %' or name like '% DE %')
   AND SPLIT_PART(name, ' ', 5) != ''
   AND (TRIM(SPLIT_PART(name, ' ', 3)) IN ('VAN', 'DE'))
;
UPDATE staging_mhr_document
   SET first_name = TRIM(SPLIT_PART(name, ' ', 1)),
       middle_name = TRIM(SPLIT_PART(name, ' ', 2)) || ' ' || TRIM(SPLIT_PART(name, ' ', 3)),
       last_name = TRIM(SPLIT_PART(name, ' ', 4)) || ' ' || TRIM(SPLIT_PART(name, ' ', 5)) || ' ' || TRIM(SPLIT_PART(name, ' ', 6)),
       suffix = null
 WHERE position(',' in name) < 1
   AND position('(' in name) < 1
   AND last_name is not null
   AND (name like '% VAN %' or name like '% DE %')
   AND SPLIT_PART(name, ' ', 6) != ''
   AND (TRIM(SPLIT_PART(name, ' ', 4)) IN ('VAN', 'DE'))
;
UPDATE staging_mhr_document
   SET first_name = TRIM(SPLIT_PART(name, ' ', 1)),
       middle_name = null,
       last_name = TRIM(SPLIT_PART(name, ' ', 2)) || ' ' || TRIM(SPLIT_PART(name, ' ', 3)) || ' ' || 
                   TRIM(SPLIT_PART(name, ' ', 4)) || ' ' || TRIM(SPLIT_PART(name, ' ', 5)) || ' ' || TRIM(SPLIT_PART(name, ' ', 6)),
       suffix = null
 WHERE position(',' in name) < 1
   AND position('(' in name) < 1
   AND last_name is not null
   AND (name like '% VAN %' or name like '% DE %')
   AND SPLIT_PART(name, ' ', 6) != ''
   AND (TRIM(SPLIT_PART(name, ' ', 2)) IN ('VAN', 'DE'))
;
UPDATE staging_mhr_document
   SET first_name = TRIM(SPLIT_PART(name, ' ', 1)),
       middle_name = TRIM(SPLIT_PART(name, ' ', 2)) || ' ' || TRIM(SPLIT_PART(name, ' ', 3)),
       last_name = TRIM(SPLIT_PART(name, ' ', 4)) || ' ' || TRIM(SPLIT_PART(name, ' ', 5)),
       suffix = null
 WHERE position(',' in name) < 1
   AND position('(' in name) < 1
   AND last_name is not null
   AND (name like '% VAN %' or name like '% DE %')
   and SPLIT_PART(name, ' ', 5) != ''
   and SPLIT_PART(name, ' ', 6) = ''
   AND (TRIM(SPLIT_PART(name, ' ', 4)) IN ('VAN', 'DE'))
   AND (TRIM(SPLIT_PART(name, ' ', 3)) NOT IN ('VAN', 'DE'))
;



-- staging_mhr_note contact party target mhr_parties.business_name, first_name, middle_name, last_name, suffix
-- ~102 records Remove extra space characters.
UPDATE staging_mhr_note
   SET name = regexp_replace(name, '\s+', ' ', 'g')
 WHERE POSITION('  ' in name) > 0
;

-- ~55,500 records
UPDATE staging_mhr_note
   SET business_name = name
 WHERE NOT public.mhr_conversion_is_individual(name)
;

-- ~26,500 records
UPDATE staging_mhr_note
   SET first_name = public.mhr_conversion_individual_first(name),
       last_name = public.mhr_conversion_individual_last(name),
       middle_name = public.mhr_conversion_individual_middle(name),
       suffix = public.mhr_conversion_individual_suffix(name)
 WHERE business_name IS NULL
   AND public.mhr_conversion_is_individual(name)
;

-- Manual updates here.
UPDATE staging_mhr_note
   SET last_name = TRIM(SPLIT_PART(name, ',', 1)),
       first_name = TRIM(SPLIT_PART(name, ',', 2)),
       middle_name = null, suffix = null
 WHERE position(',' in name) > 0
   AND last_name is not null
   AND name in ('VAN HOEK, SHIRLEY', 'VAN DE VEN, L', 'DE ROSA, BIAGIO', 'DE BRUIN, WARREN',
                  'VAN DER NET, WIJNAND', 'VAN DER WYK, GERRITT')
;
UPDATE staging_mhr_note
   SET last_name = TRIM(SPLIT_PART(name, ',', 1)),
       first_name = TRIM(SPLIT_PART(name, ' ', 3)),
       middle_name = TRIM(SPLIT_PART(name, ' ', 4)),
       suffix = null
 WHERE position(',' in name) > 0
   AND last_name is not null
   AND name in ('VAN HEEK, DERRICK WILLIAM', 'DE STRAKE, BRYAN KELLY')
;
UPDATE staging_mhr_note
   SET last_name = TRIM(SPLIT_PART(name, ',', 1)),
       first_name = TRIM(SPLIT_PART(name, ' ', 4)),
       middle_name = TRIM(SPLIT_PART(name, ' ', 5)),
       suffix = null
 WHERE position(',' in name) > 0
   AND last_name is not null
   and name in ('VAN DER HOEVEN, NEIL DAVID')
;
UPDATE staging_mhr_note
   SET first_name = TRIM(SPLIT_PART(name, ' ', 1)),
       last_name = TRIM(SPLIT_PART(name, ' ', 2)) || ' ' || TRIM(SPLIT_PART(name, ' ', 3)),
       middle_name = null,
       suffix = null
 WHERE position(',' in name) < 1
   AND position('(' in name) < 1
   AND last_name is not null
   AND (name like '% VAN %' or name like '% DE %')
   AND SPLIT_PART(name, ' ', 4) = ''
   AND (TRIM(SPLIT_PART(name, ' ', 2)) IN ('VAN', 'DE'))
;
UPDATE staging_mhr_note
   SET first_name = TRIM(SPLIT_PART(name, ' ', 1)),
       last_name = TRIM(SPLIT_PART(name, ' ', 2)) || ' ' || TRIM(SPLIT_PART(name, ' ', 3)) || ' ' || TRIM(SPLIT_PART(name, ' ', 4)),
       middle_name = null,
       suffix = null
 WHERE position(',' in name) < 1
   AND position('(' in name) < 1
   AND last_name is not null
   AND (name like '% VAN %' or name like '% DE %')
   and SPLIT_PART(name, ' ', 4) != ''
   and SPLIT_PART(name, ' ', 5) = ''
   AND (TRIM(SPLIT_PART(name, ' ', 2)) IN ('VAN', 'DE'))
;
UPDATE staging_mhr_note
   SET first_name = TRIM(SPLIT_PART(name, ' ', 1)),
       middle_name = TRIM(SPLIT_PART(name, ' ', 2)),
       last_name = TRIM(SPLIT_PART(name, ' ', 3)) || ' ' || TRIM(SPLIT_PART(name, ' ', 4)),
       suffix = null
 WHERE position(',' in name) < 1
   AND position('(' in name) < 1
   AND last_name is not null
   AND (name like '% VAN %' or name like '% DE %')
   AND SPLIT_PART(name, ' ', 4) != ''
   AND SPLIT_PART(name, ' ', 5) = ''
   AND (TRIM(SPLIT_PART(name, ' ', 3)) IN ('VAN', 'DE'))
;
UPDATE staging_mhr_note
   SET first_name = TRIM(SPLIT_PART(name, ' ', 1)),
       middle_name = TRIM(SPLIT_PART(name, ' ', 2)),
       last_name = TRIM(SPLIT_PART(name, ' ', 3)) || ' ' || TRIM(SPLIT_PART(name, ' ', 4)) || ' ' || TRIM(SPLIT_PART(name, ' ', 5)),
       suffix = null
 WHERE position(',' in name) < 1
   AND position('(' in name) < 1
   AND last_name is not null
   AND (name like '% VAN %' or name like '% DE %')
   AND SPLIT_PART(name, ' ', 5) != ''
   AND (TRIM(SPLIT_PART(name, ' ', 3)) IN ('VAN', 'DE'))
;


