"""Maintain db function match_individual_name here."""
from alembic_utils.pg_function import PGFunction


# Incomplete
match_individual_name = PGFunction(
    schema="public",
    signature="match_individual_name(lastname IN VARCHAR, firstname IN VARCHAR)",
    definition="""
    RETURNS int[]
    LANGUAGE plpgsql
    AS
    $$
    -- Debtor individual name matching comparison is between party.last_name_key and a key generated from lastname, and
    -- between party.first_name_key and a key generated from the firstname parameter.
    -- For matching, a last name key may have 2 names separated by a space character.
    -- For matching, a first name key may have 3 names separated by a space character.
    -- In all cases, first name matching is a cartesian cross product on either exact name or nickname.
    -- Cases from Oracle PL/SQL:
    -- 1. Match last name by keys on algorithm and first name by either algorithm, name, or nickname.
    -- 2. Match last name by exact match on party.last_name_key second name and lastname first name; first name by either name or nickname.  
    -- 3. Match last name by exact match on party.last_name_key first name and lastname second name; first name by either name or nickname.  
    -- 4. Match last name by exact match on party.last_name_key second name and lastname second name; first name by either name or nickname.
    -- As any of 2, 3 and 4 is a hit they are collapsed to the same condition below.
    -- Performance should improve if split names are stored as separate columns in the party table and indexed or stored in a separate table.
    DECLARE
        v_ids  integer ARRAY;
        v_lastname_key VARCHAR(50);
        v_last1 VARCHAR(50);
        v_last2 VARCHAR(50);
        v_firstname_key VARCHAR(50);
        v_first1 VARCHAR(50);
        v_first2 VARCHAR(50);
        v_first3 VARCHAR(50);
    BEGIN
        v_lastname_key := searchkey_last_name(lastname);
        v_last1 = split_part(v_lastname_key, ' ', 1);
        v_last2 = split_part(v_lastname_key, ' ', 2);  -- May be null
        v_firstname_key := searchkey_first_name(firstname);
        v_first1 = split_part(v_firstname_key, ' ', 1);
        v_first2 = split_part(v_firstname_key, ' ', 2);  -- May be null
        v_first3 = split_part(v_firstname_key, ' ', 3);  -- May be null

        IF (LENGTH(v_last2) < 1) THEN
            v_last2 := null;
        END IF;
        IF (LENGTH(v_first2) < 1) THEN
            v_first2 := null;
        END IF;
        IF (LENGTH(v_first3) < 1) THEN
            v_first3 := null;
        END IF;
        
        -- Replace where clause: Oracle uses UTL_MATCH.JARO_WINKLER_SIMILARITY
        SELECT array_agg(id)
        INTO v_ids
        FROM parties p
        WHERE registration_id_end IS NULL AND
            party_type = 'DI' AND
            (
                (levenshtein(p.last_name_key, v_lastname_key) <= 2 AND 
                (levenshtein(p.first_name_key, v_firstname_key) <= 2 OR
                searchkey_name_match(p.first_name_key, v_first1, v_first2, v_first3) > 0 OR
                searchkey_nickname_match(p.first_name_key, v_first1, v_first2, v_first3) > 0)
                ) OR
                -- This looks like a full parties table scan: commenting out reduces the query by about 3 seconds.
                (searchkey_name_match(p.last_name_key, v_last1, v_last2, null) > 0 AND 
                (searchkey_name_match(p.first_name_key, v_first1, v_first2, v_first3) > 0 OR
                searchkey_nickname_match(p.first_name_key, v_first1, v_first2, v_first3) > 0)
                )
            );
        RETURN v_ids;
    END
    ; 
    $$;
    """
)
