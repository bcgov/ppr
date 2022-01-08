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
            -- Remove prefixes last name
            v_last_name := regexp_replace(v_last_name,'DR |MR |MRS |MS |CH |DE |DO |DA |LE |LA |MA |^[A-Z] ','','i');
            -- Remove suffixes last name
            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$| I$| II$| III$','','gi');
            v_last_name := regexp_replace(v_last_name,' I$| II$| III$','','gi');
            v_last_name := regexp_replace(v_last_name,' I $| II $| III $','','gi');
            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$','','gi');
            -- Split first name
            v_last_name := trim(v_last_name);
            v_split_1 := split_part(v_last_name,' ',1);
        RETURN UPPER(v_split_1);

    END
    ; 
    $function$;
    """
)
