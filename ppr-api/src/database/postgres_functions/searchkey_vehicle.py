"""Maintain db function searchkey_vehicle here."""
from alembic_utils.pg_function import PGFunction


searchkey_vehicle = PGFunction(
    schema="public",
    signature="searchkey_vehicle(serial_number IN VARCHAR)",
    definition="""
    RETURNS VARCHAR
    LANGUAGE plpgsql
    AS
    $$
    DECLARE
        v_search_key VARCHAR(25);
        v_vin VARCHAR(25);
        v_digits VARCHAR(25);
        v_length_digits integer;
        v_last_digit_index integer;
    BEGIN
        v_search_key := UPPER(REGEXP_REPLACE(serial_number,'[^0-9A-Za-z]','','gi'));
        v_digits := regexp_replace(v_search_key, '[^0-9]', '', 'g');
        v_length_digits := length(v_digits);
        v_vin := '';
        IF (v_length_digits > 0) THEN
        v_last_digit_index := length(v_search_key) - length(regexp_replace(v_search_key, '.*' || RIGHT(v_digits, 1),'', 'g'));
        ELSE
        v_last_digit_index := 0;
        END IF;
        
        SELECT 
        CASE 
            WHEN v_length_digits = 0 THEN '000000'
            WHEN v_length_digits = 1 THEN LPAD(v_digits, 6, '0')
            WHEN RIGHT(v_search_key, 1) BETWEEN '0' AND '9' THEN LPAD(RIGHT(v_search_key, LEAST(LENGTH(v_search_key), 6)), 6, '0')
            WHEN RIGHT(v_search_key, 1) IN ('B','C','G','H','I','L','S','O','Y','Z') AND 
                LEFT(RIGHT(v_search_key, 2), 1)  NOT BETWEEN 'A' AND 'Z' THEN LPAD(RIGHT(v_search_key, 6), 6, '0')
            WHEN RIGHT(v_search_key, 1) NOT IN ('B','C','G','H','I','L','S','O','Y','Z') AND 
                LEFT(RIGHT(v_search_key, 2), 1)  BETWEEN '0' AND '9' AND
                LENGTH(v_search_key) > 6 THEN LEFT(RIGHT(v_search_key, 7), 6)
            WHEN RIGHT(v_search_key, 1) BETWEEN 'A' AND 'Z' AND 
                LEFT(RIGHT(v_search_key, 2), 1) BETWEEN 'A' AND 'Z' AND
                LENGTH(v_search_key) < 6 THEN LPAD(REGEXP_REPLACE(v_search_key,'[$A-Za-z]','', 'g'), 6, '0')
            WHEN RIGHT(v_search_key, 1) BETWEEN 'A' AND 'Z' AND 
                LEFT(RIGHT(v_search_key, 2), 1) NOT BETWEEN 'A' AND 'Z' AND
                v_last_digit_index BETWEEN 1 AND 5
                THEN LPAD(REGEXP_REPLACE(v_search_key,'[$A-Za-z]','', 'g'), 6, '0')
            WHEN RIGHT(v_search_key, 1) BETWEEN 'A' AND 'Z' AND 
                LEFT(RIGHT(v_search_key, 2), 1) BETWEEN 'A' AND 'Z' AND
                LENGTH(v_search_key) > 6
                -- This does not appear to always work correctly.
                THEN LPAD(SUBSTR(v_search_key, (v_last_digit_index - 5), 5), 6, '0')
            WHEN RIGHT(v_search_key, 1) BETWEEN 'A' AND 'Z' AND 
                LEFT(RIGHT(v_search_key, 2), 1) BETWEEN 'A' AND 'Z' AND
                LENGTH(v_search_key) > 6
                -- This does not appear to always work correctly.
                THEN SUBSTR(v_search_key, (v_last_digit_index - 5), 6)
        END
        INTO v_vin;

        IF (LENGTH(v_vin) > 0) THEN
        v_search_key := v_vin;
        END IF;
        IF (LENGTH(v_search_key) > 6) THEN
        v_search_key := RIGHT(v_search_key, 6);
        END IF;

        v_search_key := REGEXP_REPLACE(
                        REPLACE(
                        REPLACE(
                        REPLACE(
                            REPLACE(
                            REPLACE(
                            REPLACE(
                            REPLACE(
                                REPLACE(
                                REPLACE(
                                REPLACE(v_search_key,'I','1'),
                                'L','1'),
                            'Z','2'),
                            'H','4'),
                            'Y','4'),
                            'S','5'),
                        'C','6'),
                        'G','6'),
                        'B','8'),
                        'O','0'),
                    '[A-Za-z]','0');     

        RETURN v_search_key;
    END
    ; 
    $$;
    """
)
