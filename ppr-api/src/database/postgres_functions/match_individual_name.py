"""Maintain db function match_individual_name here."""
from alembic_utils.pg_function import PGFunction


match_individual_name = PGFunction(
    schema="public",
    signature="match_individual_name(lastname IN VARCHAR, firstname IN VARCHAR)",
    definition="""
    RETURNS int[]
    LANGUAGE plpgsql
    AS
    $$
    DECLARE
        v_ids  integer ARRAY;
    BEGIN
        SET pg_trgm.word_similarity_threshold = 0.4;
        
        SELECT array_agg(p.id)
        INTO v_ids
        FROM parties p
        WHERE p.registration_id_end IS NULL
        AND p.party_type = 'DI'
        AND lastname <% p.last_name_key
        AND ((firstname <% p.first_name_key AND word_similarity(firstname, p.first_name_key) >= .50) OR
                (firstname <% p.middle_initial AND word_similarity(firstname, p.middle_initial) >= .50) OR
                p.first_name_key IN (SELECT n.name 
                                    FROM nicknames n 
                                    WHERE n.name_id IN (SELECT n2.name_id
                                                            FROM nicknames n2
                                                        WHERE n2.name = firstname)));                                              
        RETURN v_ids;
    END
    ; 
    $$;
    """
)
