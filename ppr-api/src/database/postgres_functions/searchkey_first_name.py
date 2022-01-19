"""Maintain db function searchkey_first_name here."""
from alembic_utils.pg_function import PGFunction


searchkey_first_name = PGFunction(
    schema="public",
    signature="searchkey_first_name(actual_name IN character varying)",
    definition="""
    RETURNS character varying
    LANGUAGE plpgsql
    AS
    $$
DECLARE
        v_search_key VARCHAR(92);
    BEGIN
        -- Remove special characters first name
        v_search_key := regexp_replace(actual_name,'[^\w]+',' ','gi');
        -- Remove prefixes first name
		v_search_key := regexp_replace(v_first_name,'\y(DR|MR|MRS|MS|CH|DE|DO|DA|LE|LA|MA|JR|SR|I|II|III)\y','','gi');
		-- Remove extra spaces
		v_search_key := trim(regexp_replace(v_first_name, '\s+', ' ', 'gi'));
		-- Remove repeating letters
		v_search_key := regexp_replace(v_first_name, '(.)\1{1,}', '\1', 'g');
        RETURN UPPER(v_search_key);
    END
    ; 
    $$;
    """
)
