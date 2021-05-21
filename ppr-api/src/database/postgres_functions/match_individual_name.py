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
    DECLARE
        v_ids  integer ARRAY;
        v_lastname_key VARCHAR(50);
        v_firstname_key VARCHAR(50);
    BEGIN
        v_lastname_key := searchkey_last_name(lastname);
        v_firstname_key := searchkey_first_name(firstname);
        -- Replace where clause: Oracle uses nickname table and UTL_MATCH.JARO_WINKLER_SIMILARITY
        SELECT array_agg(party_id)
        INTO v_ids
        FROM party
        WHERE registration_id_end IS NULL AND
            last_name_key = v_lastname_key AND
            first_name_key = v_firstname_key;
        RETURN v_ids;
    END
    ; 
    $$;
    """
)
