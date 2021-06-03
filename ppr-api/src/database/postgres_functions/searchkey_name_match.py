"""Maintain db function searchkey_name_match here."""
from alembic_utils.pg_function import PGFunction


searchkey_name_match = PGFunction(
    schema="public",
    signature="searchkey_name_match(search_key IN VARCHAR, name1 IN VARCHAR, name2 IN VARCHAR, name3 IN varchar)",
    definition="""
    RETURNS int
    LANGUAGE plpgsql
    AS
    $$
    -- Cartesion cross-product on name: search key may have up to 3 names, an exact match on any name is a hit.
    -- search_key is party.first_name_key to match on: may be 3 names separated by a space character.
    -- name1, name2, name3 are names already parsed from the search criteria: name2 and name3 may be null. 
    DECLARE
        v_name1 VARCHAR(50);
        v_name2 VARCHAR(50);
        v_name3 VARCHAR(50);
        v_match_count integer;
    BEGIN
        v_match_count := 0;
        v_name1 = split_part(search_key, ' ', 1);
        v_name2 = split_part(search_key, ' ', 2);  -- May be null
        v_name3 = split_part(search_key, ' ', 3);  -- May be null
        IF (v_name1 = name1 OR (name2 IS NOT NULL AND v_name1 = name2) OR (name3 IS NOT NULL AND v_name1 = name3)) THEN
        v_match_count := 1;
        ELSIF (v_name2 IS NOT NULL AND v_name2 = name1 OR (name2 IS NOT NULL AND v_name2 = name2) OR (name3 IS NOT NULL AND v_name2 = name3)) THEN
        v_match_count := 1;
        ELSIF (v_name3 IS NOT NULL AND v_name3 = name1 OR (name2 IS NOT NULL AND v_name3 = name2) OR (name3 IS NOT NULL AND v_name3 = name3)) THEN
        v_match_count := 1;
        END IF;

        RETURN v_match_count;
    END
    ; 
    $$;
    """
)
