"""Maintain db function searchkey_first_name here."""
from alembic_utils.pg_function import PGFunction


individual_split_1 = PGFunction(
    schema="public",
    signature="individual_split_1(actual_name character varying)",
    definition="""
    RETURNS character varying
    LANGUAGE plpgsql
    AS $function$
DECLARE
  v_last_name VARCHAR(150);
  v_split_1 VARCHAR(50);
  BEGIN
        -- Remove special characters last name
    v_last_name := regexp_replace(ACTUAL_NAME,'[^\w]+',' ','gi');
        -- Remove prefixes suffix
	v_last_name := regexp_replace(v_last_name,'\y(DR|MR|MRS|MS|CH|DE|DO|DA|LE|LA|MA|JR|SR|I|II|III)\y','','gi');
       	-- Split first name
	v_last_name := trim(v_last_name);
    v_split_1 := split_part(v_last_name,' ',1);
	  RETURN UPPER(v_split_1);

  END
    ; 
    $function$;
    """
)
