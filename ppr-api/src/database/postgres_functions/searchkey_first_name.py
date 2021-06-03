"""Maintain db function searchkey_first_name here."""
from alembic_utils.pg_function import PGFunction


searchkey_first_name = PGFunction(
    schema="public",
    signature="searchkey_first_name(actual_name IN VARCHAR)",
    definition="""
    RETURNS VARCHAR
    LANGUAGE plpgsql
    AS
    $$
    DECLARE
        v_search_key VARCHAR(92);
    BEGIN
        -- Remove prefixes
        v_search_key := REGEXP_REPLACE(actual_name,'^DR |^DR.|^DR. |^MR |^MR.|^MR. |^MRS |^MRS.|^MRS. |^MS |^MS.|^MS. ','','gi');
        -- Remove suffixes
        v_search_key := REGEXP_REPLACE(v_search_key,' JR$| JR.$| JR. $| SR$| SR $| SR.$| SR. $','','gi');
        v_search_key := REGEXP_REPLACE(v_search_key,'[^0-9A-Za-z]',' ','gi');
        -- Remove internal extra space characters
        v_search_key := TRIM(REGEXP_REPLACE(v_search_key,'( ){2,}',' ','g'));
        RETURN UPPER(v_search_key);
    END
    ; 
    $$;
    """
)
