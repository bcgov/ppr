"""Maintain db function searchkey_nickname_match here."""
from alembic_utils.pg_function import PGFunction


searchkey_nickname_match = PGFunction(
    schema="public",
    signature="searchkey_nickname_match(search_key IN VARCHAR, name1 IN VARCHAR, name2 IN VARCHAR, name3 IN varchar)",
    definition="""
    RETURNS int
    LANGUAGE plpgsql
    AS
    $$
    -- Cartesion cross-product on nickname: search key may have up to 3 names, a nickname match on any name is a hit.
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
        SELECT COUNT(name_id)
        INTO v_match_count
        FROM nicknames n1
        WHERE (name = v_name1 AND 
                n1.name_id IN (SELECT n2.name_id 
                                FROM nicknames n2
                                WHERE n2.name IN (name1, name2, name3))) OR
            (v_name2 IS NOT NULL AND
                name = v_name2 AND 
                n1.name_id IN (SELECT n2.name_id 
                                FROM nicknames n2
                                WHERE n2.name IN (name1, name2, name3))) OR
            (v_name3 IS NOT NULL AND
                name = v_name3 AND 
                n1.name_id IN (SELECT n2.name_id 
                                FROM nicknames n2
                                WHERE n2.name IN (name1, name2, name3)));

        RETURN v_match_count;
    END
    ; 
    $$;
    """
)
