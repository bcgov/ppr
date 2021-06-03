"""Maintain db function searchkey_aircraft here."""
from alembic_utils.pg_function import PGFunction


searchkey_aircraft = PGFunction(
    schema="public",
    signature="searchkey_aircraft(aircraft_number IN VARCHAR)",
    definition="""
    RETURNS VARCHAR
    LANGUAGE plpgsql
    AS
    $$
    DECLARE
        v_search_key VARCHAR(25);
    BEGIN
        v_search_key := TRIM(REGEXP_REPLACE(aircraft_number,'\s|-','','gi'));
        IF (LENGTH(v_search_key) > 6) THEN
        v_search_key := RIGHT(v_search_key, 6);
        END IF;
        RETURN v_search_key;
    END
    ; 
    $$;
    """
)
