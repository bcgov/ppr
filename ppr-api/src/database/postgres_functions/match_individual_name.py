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
               (SELECT public.searchkey_last_name(lastname)) AS search_last_key,              
              lastname AS LAST,
              firstname AS FIRST,
              LENGTH(lastname) AS LAST_LENGTH,
              LENGTH(firstname) AS FIRST_LENGTH,
              SUBSTR(firstname,1,1) AS FIRST_CHAR1,
              SUBSTR(firstname,2,1) AS FIRST_CHAR2,
              SUBSTR((SELECT(SELECT public.searchkey_individual(lastname, firstname))),1,1) AS INDKEY_CHAR1,
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
 WHERE (p.LAST_NAME_key = search_last_key OR 
        (first_name_key_char1 = INDKEY_CHAR1 AND
         indkey <% p.FIRST_NAME_KEY AND 
         LEVENSHTEIN(p.FIRST_NAME_KEY,indkey) <= 2)) 
   AND p.PARTY_TYPE = 'DI'
   AND p.REGISTRATION_ID_END IS NULL
   AND (
        (p.FIRST_NAME = FIRST OR p.MIDDLE_INITIAL= FIRST)
    OR  (p.FIRST_NAME IN (SELECT NAME 
                            FROM public.NICKNAMES 
                           WHERE NAME_ID IN (SELECT NAME_ID 
                                               FROM public.NICKNAMES WHERE(FIRST) = NAME))
        )
    OR  (FIRST_LENGTH = 1 AND FIRST_CHAR1 = p.first_name_char1)
    OR  (FIRST_LENGTH > 1 AND FIRST_CHAR1 = p.first_name_char1 AND p.first_name_char2 IS NOT NULL AND p.first_name_char2 = '-')
    OR  (FIRST_LENGTH > 1 AND FIRST_CHAR2 IS NOT NULL AND FIRST_CHAR2 = '-' AND FIRST_CHAR1 = p.first_name_char1)
    OR (p.first_name_char1 = FIRST_CHAR1 AND LENGTH(p.first_name) = 1)
    OR (indkey <% p.FIRST_NAME_KEY AND
        SIMILARITY(p.FIRST_NAME_KEY, indkey) >= SIMNUMBER AND 
        p.first_name_key_char1 = INDKEY_CHAR1 AND 
        ((FIRST <% p.first_name AND 
          SIMILARITY(p.FIRST_NAME,FIRST)>= sim_quotient_first AND 
          (LAST_LENGTH BETWEEN LENGTH(p.LAST_NAME)-3 AND LENGTH(p.LAST_NAME)+3 OR LAST_LENGTH >= 10)) OR
          (p.first_name_char1 = FIRST_CHAR1 OR P.FIRST_NAME = FIRST_CHAR1))          
       )
    OR (FIRST <% p.first_name AND
        SIMILARITY(p.FIRST_NAME,FIRST)>= sim_quotient_first AND 
        (p.last_name_split1 = SPLIT1 OR 
         p.last_name_split2 = SPLIT1 and p.last_name_split2 != '' OR
         p.last_name_split3 = SPLIT1 and p.last_name_split3 != '' OR
         p.last_name_split1 = SPLIT2 OR 
         p.last_name_split2 = SPLIT2 and p.last_name_split2 != '' OR
         p.last_name_split3 = SPLIT2 and p.last_name_split3 != '' OR
         p.last_name_split1 = SPLIT3 OR 
         p.last_name_split2 = SPLIT3 and p.last_name_split2 != '' OR
         p.last_name_split3 = SPLIT3 and p.last_name_split3 != ''
        )
       )       
    OR (LAST <% p.LAST_NAME AND
        SIMILARITY(p.LAST_NAME,LAST)>= SIMNUMBER AND 
        (p.first_name_split1 = SPLIT4 OR
         p.first_name_split2 = SPLIT4 and p.first_name_split2 != '' OR
         p.first_name_split1 = SPLIT5 OR
         p.first_name_split2 = SPLIT5 and p.first_name_split2 != ''
        )
       )
    )
    ;
    RETURN v_ids;
  END
    ; 
    $function$;
    """
)
