"""Maintain db function searchkey_first_name here."""
from alembic_utils.pg_function import PGFunction


searchkey_individual = PGFunction(
    schema="public",
    signature="searchkey_individual(last_name character varying, first_name character varying)",
    definition="""
    RETURNS character varying
    LANGUAGE plpgsql
    AS $function$
    DECLARE
            v_ind_key VARCHAR(50);
            v_last_name VARCHAR(50);
            v_first_name VARCHAR(50);
        BEGIN
            -- Remove special characters last name
            v_last_name := regexp_replace(LAST_NAME,'[^\w]+',' ','gi');
            -- Remove prefixes last name
            v_last_name := regexp_replace(v_last_name,'^DR |^MR |^MRS |^MS ','','gi');
            -- Remove suffixes last name
            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$| I$| II$| III$','','gi');
            v_last_name := regexp_replace(v_last_name,' I$| II$| III$','','gi');
            v_last_name := regexp_replace(v_last_name,' I $| II $| III $','','gi');
            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$','','gi');
            -- Remove repeating letters
            v_last_name := regexp_replace(v_last_name, '(.)\1{1,}', '\1', 'g');
            -- Remove extra spaces
            v_last_name := trim(regexp_replace(v_last_name, '\s+', '', 'gi'));
            -- Remove special characters first name
            v_first_name := regexp_replace(first_name,'[^\w]+',' ','gi');
            -- Remove prefixes first name
            v_first_name := regexp_replace(v_first_name,'^DR |^MR |^MRS |^MS ','','gi');
            -- Remove suffixes first name
            v_first_name := regexp_replace(v_first_name,' DR$| JR$|JR$| SR$|SR$| I$| II$| III$','','gi');
            v_first_name := regexp_replace(v_first_name,' I$| II$| III$','','gi');
            v_first_name := regexp_replace(v_first_name,' I $| II $| III $','','gi');
            v_first_name := regexp_replace(v_first_name,' DR$| JR$|JR$| SR$|SR$','','gi');
            -- Remove repeating letters
            v_first_name := regexp_replace(v_first_name, '(.)\1{1,}', '\1', 'g');
            -- Remove extra spaces
            v_first_name := trim(regexp_replace(v_first_name, '\s+', '', 'gi'));
            -- join last first name
            v_ind_key := v_last_name||' '||v_first_name;



        RETURN UPPER(v_ind_key);
        END
    ; 
    $function$;
    """
)
