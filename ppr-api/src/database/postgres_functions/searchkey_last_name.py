"""Maintain db function searchkey_last_name here."""
from alembic_utils.pg_function import PGFunction


searchkey_last_name = PGFunction(
    schema="public",
    signature="searchkey_last_name(actual_name IN character varying)",
    definition="""
    RETURNS character varying
    LANGUAGE plpgsql
    COST 100
    VOLATILE PARALLEL UNSAFE
    AS
    $$
DECLARE
        v_last_name VARCHAR(60);
    BEGIN
        -- Remove special characters last name
        v_last_name := regexp_replace(actual_name,'[^\w]+',' ','gi');
        -- Remove prefixes suffixes last name
		v_last_name := regexp_replace(v_last_name,'\y(DR|MR|MRS|MS|CH|DE|DO|DA|LE|LA|MA|JR|SR|I|II|III)\y','','gi');
		-- Remove extra spaces
		v_last_name := trim(regexp_replace(v_last_name, '\s+', ' ', 'gi'));
		-- Remove repeating letters
		v_last_name := regexp_replace(v_last_name, '(.)\1{1,}', '\1', 'g');
		-- Remove special characters first name
     RETURN UPPER(v_last_name);
    END
    ; 
    $$;
    """
)
