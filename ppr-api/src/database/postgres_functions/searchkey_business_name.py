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
        regexp_replace(
        regexp_replace(
        regexp_replace(
            regexp_replace(
            regexp_replace(
            regexp_replace(
            regexp_replace(
                regexp_replace(
                regexp_replace(
                regexp_replace(
                regexp_replace(
                    regexp_replace(
                    regexp_replace(
                    regexp_replace(
                    regexp_replace(
                        regexp_replace(actual_name, '[[:<:]](BC|B C |B.C)[[:>:]]', ' ', 'gi'
                                    ),
                                    '[[:<:]](BRITISH COLUMBIA|BRITISHCOLUMBIA)[[:>:]]', ' ', 'gi'
                                    ),
                                    '[[:<:]](INCORPORATED|INCORPOREE)[[:>:]]', ' ', 'gi'
                                    ),
                                    '[[:<:]](CORPORATION)[[:>:]]', ' ', 'gi'
                                ),
                                '[[:<:]](ULC|HOLDINGS|HOLDING|ASSOCIATION|ASSOCIATES| ASSOC| ASSN|NON PERSONAL LIABILITY|UNLIMITED LIABILITY COMPANY|N P L|NPL|PARTNERSHIP|SOCIETY)[[:>:]]', ' ', 'gi'
                                ),
                                '[[:<:]](^THE|AND)[[:>:]]', ' ', 'gi'
                                ),
                                '[[:<:]](^DR)[[:>:]]', ' ', 'gi'
                                ),
                                '[[:<:]](CONSTRUCTION|CONTRACTING|CONTRACTOR)[[:>:]]', ' ', 'gi'
                            ),
                            '[[:<:]](CONSULTANTS|CONSULTANT|CONSULTING)[[:>:]]', ' ', 'gi'
                            ),
                            '[[:<:]](SERVICES|SERVICE)[[:>:]]', ' ', 'gi'
                            ),
                            '[[:<:]](TRUST)[[:>:]]', ' ', 'gi'
                            ),
                            '[[:<:]](CORP|COMPANY|CO\|LTD|LIMITED|LIMITEE|LTEE)[[:>:]]', ' ', 'gi'
                        ),
                        '[[:<:]](LTD|LIMITED|LIMITEE|LTEE)[[:>:]]', ' ', 'gi'
                        ),
                        '[[:<:]](CO|INC)[[:>:]]', ' ', 'gi'
                        ),
                        '[^a-zA-Z0-9]+', '', 'gi'
                        ),
                        '( ){2,}', '');    
    RETURN TRIM(v_search_key);
    END
    ; 
    $$;
    """
)
