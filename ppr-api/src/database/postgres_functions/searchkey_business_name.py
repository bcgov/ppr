"""Maintain db function searchkey_business_name here."""
from alembic_utils.pg_function import PGFunction


searchkey_business_name = PGFunction(
    schema="public",
    signature="searchkey_business_name(actual_name IN VARCHAR)",
    definition="""
    RETURNS VARCHAR
    LANGUAGE plpgsql
    AS
    $$
    DECLARE
    v_search_key VARCHAR(150);
    BEGIN
        v_search_key :=
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
                            REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                    REGEXP_REPLACE(actual_name,'^0000|^000|^00|^0|^THE | THE |\([^()]*\)',''),
                                    'CORPORATION|CORP|COMPANY|CO\.|LTD|INCORPORATED|INC$|INC.|INCORPOREE|LIMITED|LIMITEE|LTEE|LTD|ASSOCIATION$|ASSOC$|ASSN$|NON PERSONAL LIABILITY$|UNLIMITED LIABILITY COMPANY|N P L$|NPL$|PARTNERSHIP|SOCIETY$|SOC$',''),
                                'BRITISH COLUMBIA|BRITISHCOLUMBIA','BC'),
                                '&','AND'),
                                '#','NUMBER'),
                                '1','ONE'),
                            '2','TWO'),
                            '3','THREE'),
                            '4','FOUR'),
                            '5','FIVE'),
                        '6','SIX'),
                        '7','SEVEN'),
                        '8','EIGHT'),
                        '9','NINE'),
                    '0','ZERO'),
                    'TEN','ONEZERO'),
                    'TWENTY','TWOZERO'),
                    'THIRTY','THREEERO'),
                'FORTY','FOURZERO'),
                'FOURTY','FOURZERO'),
                'FIFTY','FIVEZERO'),
                'SIXTY','SIXZERO'),
            'SEVENTY','SEVENZERO'),
            'EIGHTY','EIGHTZERO'),
            'NINETY','NINEZERO'),
            '[^0-9A-Za-z]','','gi');
        RETURN UPPER(v_search_key);
    END
    ; 
    $$;
    """
)
