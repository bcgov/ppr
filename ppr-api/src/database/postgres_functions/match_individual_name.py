"""Maintain db function match_individual_name here."""
from alembic_utils.pg_function import PGFunction


match_individual_name = PGFunction(
    schema="public",
    signature="match_individual_name(lastname IN VARCHAR, firstname IN VARCHAR, sim_quotient_last IN REAL DEFAULT 0.29, sim_quotient_first IN REAL DEFAULT 0.23, sim_quotient_default IN REAL DEFAULT 0.50)",
    definition="""
    RETURNS int[]
    LANGUAGE plpgsql
    AS
    $$
    DECLARE
        v_ids  INTEGER ARRAY;
        v_last_count INTEGER;
        v_first_count INTEGER;
        v_sim_quotient_last REAL := sim_quotient_default;
        v_sim_quotient_first REAL := sim_quotient_default;
    BEGIN

        SELECT COUNT(id)
        INTO v_last_count
        FROM parties
        WHERE last_name_key = lastname
        AND registration_id_end IS NULL
        ;
        SELECT COUNT(id)
        INTO v_first_count
        FROM parties
        WHERE first_name_key = lastname
        AND registration_id_end IS NULL
        ;
        IF (v_last_count <= 600) THEN
        v_sim_quotient_last := sim_quotient_last;
        END IF;
        IF (v_first_count <= 1000) THEN
        v_sim_quotient_first := sim_quotient_first;
        END IF;
        SET pg_trgm.similarity_threshold = 0.23; -- assigning from variable does not work
        
        SELECT array_agg(p.id)
        INTO v_ids
        FROM parties p
        WHERE p.registration_id_end IS NULL
        AND p.party_type = 'DI'
        AND (lastname % p.last_name_key AND similarity(lastname, p.last_name_key) >= v_sim_quotient_last)
        AND ((firstname % p.first_name_key AND similarity(firstname, p.first_name_key) >= v_sim_quotient_first) OR
                (firstname % p.middle_initial AND similarity(firstname, p.middle_initial) >= v_sim_quotient_first) OR
                p.first_name_key IN (SELECT n.name 
                                    FROM nicknames n 
                                    WHERE n.name_id IN (SELECT n2.name_id
                                                            FROM nicknames n2
                                                        WHERE n2.name = firstname)) OR
                SUBSTR(firstname,1,1) = p.FIRST_NAME);                                             
        RETURN v_ids;
    END
    ; 
    $$;
    """
)
