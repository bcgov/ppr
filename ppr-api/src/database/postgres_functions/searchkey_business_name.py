"""Maintain db function searchkey_business_name here."""
from alembic_utils.pg_function import PGFunction


searchkey_business_name = PGFunction(
    schema="public",
    signature="searchkey_business_name(actual_name IN VARCHAR)",
    definition="""
 RETURNS character varying
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_search_key VARCHAR(150);
    v_name_2  VARCHAR(150);
    v_name_3  VARCHAR(150);
    v_name_4  VARCHAR(150);
    v_name_5  VARCHAR(150);
    v_word_1  VARCHAR(150);
    v_word_2  VARCHAR(150);
    v_word_3  VARCHAR(150);
    v_word_4  VARCHAR(150);
	
BEGIN
    IF LENGTH(SPLIT_PART(REGEXP_REPLACE(actual_name,'[A-Z]+','','g'),' ',1))>=5 then
        v_search_key := REGEXP_REPLACE(actual_name,'^0000|^000|^00|^0','','g');
        v_search_key := REGEXP_REPLACE(SPLIT_PART(v_search_key,' ',1),'[A-Za-z]+','','g');
        v_search_key := REGEXP_REPLACE(v_search_key,'[^\w\s]+','','gi');
    END IF;

    IF  array_length(string_to_array(v_search_key,''),1) is not null then
        RETURN v_search_key;
    ELSE
        v_search_key := split_part(upper(actual_name), 'INC', 1);
        v_search_key := split_part(upper(v_search_key), 'LTD', 1);
        v_search_key := split_part(upper(v_search_key), 'LTEE', 1);
        v_search_key := split_part(upper(v_search_key), 'LIMITED', 1);
        v_search_key := split_part(upper(v_search_key), 'INCORPORATED', 1);
        v_search_key := split_part(upper(v_search_key), 'INCORPORATEE', 1);
        v_search_key := split_part(upper(v_search_key), 'INCORPORATION', 1);
		v_search_key := regexp_replace(v_search_key, '\([^()]*\)', '', 'gi');
        v_search_key := regexp_replace(v_search_key,'^THE','','gi');
        v_search_key := regexp_replace(v_search_key,'\y(AND|DBA)\y', '', 'g');
        v_search_key := REGEXP_REPLACE(v_search_key,'[^\w\s]+',' ','gi');
        v_search_key := TRIM(REGEXP_REPLACE(v_search_key, '\s+', ' ', 'gi'));
        v_search_key := REGEXP_REPLACE(v_search_key,'\y( S$)\y','','gi');
    END IF;

    IF SUBSTR(v_search_key,2,1)=' ' AND SUBSTR(v_search_key,4,1)=' ' AND SUBSTR(v_search_key,6,1)!=' ' THEN
        v_search_key := TRIM(REGEXP_REPLACE(SUBSTR(v_search_key,1,3),'\s+', '', 'gi'))||SUBSTR(v_search_key,4,146);
    ELSIF SUBSTR(v_search_key,2,1)=' ' AND SUBSTR(v_search_key,4,1)=' ' AND SUBSTR(v_search_key,6,1)=' ' THEN 
        v_search_key := TRIM(REGEXP_REPLACE(SUBSTR(v_search_key,1,3),'\s+', '', 'gi'))||SUBSTR(v_search_key,5,145);
    ELSE
        v_search_key := v_search_key;
    END IF;

    v_name_2 := SPLIT_PART(v_search_key,' ',2);
    v_name_3 := SPLIT_PART(v_search_key,' ',3);
    v_name_4 := SPLIT_PART(v_search_key,' ',4);
    v_name_5 := SPLIT_PART(v_search_key,' ',5);
    v_word_1 := (select word from common_word where word = v_name_2 );
    v_word_2 := (select word from common_word where word = v_name_3 );
    v_word_3 := (select word from common_word where word = v_name_4 );
    v_word_4 := (select word from common_word where word = v_name_5 );

   

    IF v_word_2 is not null THEN
        v_search_key := regexp_replace(v_search_key,v_word_2,'','ig');
    ELSE    
        v_search_key := v_search_key;
    END IF;

    IF v_word_3 is not null THEN
    v_search_key := regexp_replace(v_search_key,v_word_3,'','ig');
    ELSE
        v_search_key := v_search_key;
    END IF;

    IF v_word_4 is not null THEN
        v_search_key := regexp_replace(v_search_key,v_word_4,'','ig');
    ELSE
        v_search_key := v_search_key;
    END IF;
    
    IF  v_search_key is null or LENGTH(TRIM(v_search_key)) = 0 THEN
        v_search_key := actual_name;
    ELSE
        v_search_key := v_search_key;
    END IF;

    v_search_key := REGEXP_REPLACE(v_search_key,'\y(BRITISH COLUMBIA|BRITISHCOLUMBIA)\y','BC','gi');
    v_search_key := REGEXP_REPLACE(v_search_key,'\y(LIMITED|PARTNERSHIP|GP|LLP|LP)\y','','gi');
    v_search_key := REGEXP_REPLACE(v_search_key,'\y(SOCIETY|ASSOCIATION|TRUST|TRUSTEE|SOCIETE)\y','','gi');
    v_search_key := REGEXP_REPLACE(v_search_key,'\y(INCORPORATED|INCORPOREE|INCORPORATION|INCORP|INC)\y','','gi');
    v_search_key := REGEXP_REPLACE(v_search_key,'\y(COMPANY|CORPORATIONS|CORPORATION|CORPS|CORP|CO)\y','','gi');
    v_search_key := REGEXP_REPLACE(v_search_key,'\y(LIMITEE|LTEE|LTD|ULC)\y','','gi');
	v_search_key := regexp_replace(v_search_key,'\y(AND)\y','AN','gi');
	v_search_key := regexp_replace(v_search_key,'&','AN','gi');
	v_search_key := regexp_replace(v_search_key, '\([^()]*\)', '', 'gi');
    v_search_key := regexp_replace(v_search_key,'^THE','','gi');
    v_search_key := regexp_replace(v_search_key,'\y(DBA)\y', '', 'g');
	v_search_key := REGEXP_REPLACE(v_search_key,'[^\w\s]+','','gi');
    v_search_key := trim(regexp_replace(v_search_key, '\s+', '', 'gi'));
	
    RETURN v_search_key;

END
    ; 
$function$;
    """
)
