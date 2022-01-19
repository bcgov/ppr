"""Maintain db function match_individual_name here."""
from alembic_utils.pg_function import PGFunction

# Manually replace after script runs: actual signature is too long and truncated, causing an alembic error.
# Actual signature is:
# match_individual_name(lastname character varying, firstname character varying, sim_quotient_last real DEFAULT 0.29, sim_quotient_first real DEFAULT 0.4, sim_quotient_default real DEFAULT 0.50)
match_individual_name = PGFunction(
    schema="public",
    signature="match_individual_name(lastname character varying,firstname character varying,sim_last real,sim_first real,sim_def real)",
    definition="""
 RETURNS integer[]
 LANGUAGE plpgsql
    AS $function$
DECLARE
    v_ids  INTEGER ARRAY;
  BEGIN

    SET pg_trgm.similarity_threshold = 0.29; -- assigning from variable does not work

    WITH q AS (SELECT(SELECT public.searchkey_individual(lastname, firstname)) AS INDKEY,
                       lastname AS LAST,
                       firstname AS FIRST,
               (SELECT public.sim_number(lastname)) as simnumber,
               (SELECT public.individual_split_1(lastname)) AS SPLIT1,
               (SELECT public.individual_split_2(lastname)) AS SPLIT2,
               (SELECT public.individual_split_3(lastname)) AS SPLIT3,
               (SELECT public.individual_split_1(firstname)) AS SPLIT4, 
               (SELECT public.individual_split_2(firstname)) AS SPLIT5
              )
    SELECT array_agg(p.id)
      INTO v_ids
      FROM PARTIES p,q
     WHERE p.PARTY_TYPE = 'DI'
       AND p.REGISTRATION_ID_END IS NULL
       AND p.LAST_NAME = LAST
       AND (p.FIRST_NAME = FIRST OR p.MIDDLE_INITIAL= FIRST OR 
            p.FIRST_NAME IN (SELECT NAME 
                             FROM public.NICKNAMES 
                            WHERE NAME_ID IN (SELECT NAME_ID 
                                                FROM public.NICKNAMES WHERE(UPPER(FIRST)) = NAME))
           )
        OR (p.PARTY_TYPE = 'DI' AND 
            p.REGISTRATION_ID_END IS NULL AND 
            SIMILARITY(p.FIRST_NAME_KEY, indkey) >= SIMNUMBER AND 
            SUBSTR(p.FIRST_NAME_KEY,1,1)=SUBSTR(INDKEY,1,1) AND 
            SIMILARITY(p.FIRST_NAME,FIRST)>= sim_first AND 
            (LENGTH(LAST) BETWEEN LENGTH(p.LAST_NAME)-3 AND LENGTH(p.LAST_NAME)+3 OR LENGTH(LAST)>=10)
           )
        OR (p.PARTY_TYPE = 'DI' AND  
            p.REGISTRATION_ID_END IS NULL AND  
            SIMILARITY(p.FIRST_NAME,FIRST)>= sim_first AND 
            ((SELECT public.individual_split_1(p.LAST_NAME)) = SPLIT1 OR    
             (SELECT public.individual_split_2(p.LAST_NAME)) = SPLIT1 and (SELECT public.individual_split_2(p.LAST_NAME)) != '' OR    
             (SELECT public.individual_split_3(p.LAST_NAME)) = SPLIT1 and (SELECT public.individual_split_3(p.LAST_NAME)) != '' OR    
             (SELECT public.individual_split_1(p.LAST_NAME)) = SPLIT2 OR    
             (SELECT public.individual_split_2(p.LAST_NAME)) = SPLIT2 and (SELECT public.individual_split_2(p.LAST_NAME)) != '' OR    
             (SELECT public.individual_split_3(p.LAST_NAME)) = SPLIT2 and (SELECT public.individual_split_3(p.LAST_NAME)) != '' OR    
             (SELECT public.individual_split_1(p.LAST_NAME)) = SPLIT3 OR    
             (SELECT public.individual_split_2(p.LAST_NAME)) = SPLIT3 and (SELECT public.individual_split_2(p.LAST_NAME)) != '' OR    
             (SELECT public.individual_split_3(p.LAST_NAME)) = SPLIT3 and (SELECT public.individual_split_3(p.LAST_NAME)) != ''
            )
           )
        OR (p.PARTY_TYPE = 'DI' AND  
            p.REGISTRATION_ID_END IS NULL AND  
            SIMILARITY(p.LAST_NAME,LAST)>= SIMNUMBER AND 
            ((SELECT public.individual_split_1(p.FIRST_NAME)) = SPLIT4 OR    
             (SELECT public.individual_split_2(p.FIRST_NAME)) = SPLIT4 and (SELECT public.individual_split_2(p.FIRST_NAME)) != '' OR    
             (SELECT public.individual_split_1(p.FIRST_NAME)) = SPLIT5 OR    
             (SELECT public.individual_split_2(p.FIRST_NAME)) = SPLIT5 and (SELECT public.individual_split_2(p.FIRST_NAME)) != ''
            )
           )
    ;
    RETURN v_ids;
  END
    ; 
    $function$;
    """
)
