"""Maintain db function searchkey_business_name here."""
from alembic_utils.pg_function import PGFunction


searchkey_business_name = PGFunction(
    schema="public",
    signature="searchkey_business_name(actual_name IN VARCHAR)",
    definition="""
    RETURNS VARCHAR
    COST 100
    VOLATILE PARALLEL UNSAFE
    LANGUAGE plpgsql
    AS
    $$
    DECLARE
    v_search_key VARCHAR(40);
    BEGIN
        if LENGTH(SPLIT_PART(REGEXP_REPLACE(actual_name,'[A-Z]+','','g'),' ',1))>=5 then
        v_search_key := REGEXP_REPLACE(actual_name,'^0000|^000|^00|^0','','g');
        v_search_key := REGEXP_REPLACE(SPLIT_PART(v_search_key,' ',1),'[A-Za-z]+','','g');
        v_search_key := REGEXP_REPLACE(v_search_key,'[^\w]+|[A-Za-z]+','','g');
        else
        v_search_key := REGEXP_REPLACE(
                        REGEXP_REPLACE(
                        REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(
                            REGEXP_REPLACE(
                            REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                    REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                    REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                    REGEXP_REPLACE(
                                        REGEXP_REPLACE(
        REGEXP_REPLACE(actual_name,'INVESTMENTS|INVESTMENT','','gi'
                            ),
        'AUTO | AERO|DEVELOPMENTS|DEVELOPMENT|ENTERPRISES|ENTERPRISE|EQUIPMENT|GROUP|HOLDINGS|HOLDING|HOMES|INDUSTRIES|MANAGEMENT|MOTORS|PRODUCTIONS|PRODUCTS|PROPERTIES|PROPERTY|RENTALS|SALES|SERVICES|SERVICE|SOLUTIONS|SYSTEMS|TRANSPORT|TRUCKING|VENTURES'
        ,'','gi')
        ,'CONSULTING','','gi')
        ,'LOGISTICS','','gi')
        ,'MECHANICAL','','gi')
        ,'AUTOMOBILE|AUTOBODY','','gi')
        ,'AVENUE|STREET','','gi')
        ,' EAST | WEST | SOUTH | NORTH ','','gi')
        ,'CONSTRUCTION|CONTRACTING|CONTRACTORS','','gi')
        ,'LIMITED PARTNERSHIP| LIMITED| PARTNERSHIP','','gi')
        ,'SOCIETY|ASSOCIATION|TRUST|SOCIETE','','gi')
        ,'BRITISH COLUMBIA|BRITISHCOLUMBIA','BC','gi')
        ,'INCORPORATED|INCORPOREE|INCORPORATION|INCORP|INC.$|INC$','','gi')
        ,'COMPANY| CORPORATION|CORPORATION$| CORPS| CORP| CO.$| CO.,$| CO$| CO.$','','gi')
        ,'LIMITEE$|LTEE$| LTD| LTD.|LTD.$|LTD$|LTD,.$','','gi')
        ,' B.C.| B.C| BC.',' BC ','g')					 
        ,' DEV | DEV. ','','gi')
        ,' ULC$','','gi')
        ,'^THE ','','gi')
        ,'\([^()]*\)','','gi')
        ,'&', 'AND','gi')
        ,'[^\w]+',' ','gi')
        ;
        end if;
        if v_search_key = ' ' then 
        v_search_key := regexp_replace(actual_name,'[^\w]+','','gi');
        end if;
        v_search_key := trim(regexp_replace(v_search_key,'\s+',' ','gi')); 
    RETURN v_search_key;
    END
    ; 
    $$;
    """
)
