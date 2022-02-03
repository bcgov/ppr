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
        BEGIN
        v_search_key := LPAD(SUBSTR(serial_number, LENGTH(serial_number) - 5, 6),6,'0');
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
                                  REGEXP_REPLACE(v_search_key,'I','1','gi'),
                                                'L','1','gi'),
                                                'Z','2','gi'),
                                                'H','4','gi'),
                                                'Y','4','gi'),
                                                 'S','5','gi'),
                                                 'C','6','gi'),
                                                 'G','6','gi'),
                                                 'B','8','gi'),
                                                 'O','0','gi'),
                                                 '[^\w]+|[A-Za-z]+','0','gi');
               v_search_key := LPAD(v_search_key,6,'0');											 
        RETURN v_search_key;
    END
    ; 
    $$;
    """
)
