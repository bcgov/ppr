"""Maintain db function searchkey_mhr here."""
from alembic_utils.pg_function import PGFunction


searchkey_mhr = PGFunction(
    schema="public",
    signature="searchkey_mhr(mhr_number IN VARCHAR)",
    definition="""
    RETURNS VARCHAR
    LANGUAGE plpgsql
    AS
    $$
    DECLARE
        v_search_key VARCHAR(6);
    BEGIN
        v_search_key := TRIM(REGEXP_REPLACE(mhr_number,'[^0-9A-Za-z]','','gi'));
        v_search_key := LPAD(REGEXP_REPLACE(v_search_key,'[$A-Za-z]','0'),6,'0');
        RETURN v_search_key;
    END
    ; 
    $$;
    """
)
