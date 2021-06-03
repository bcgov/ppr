"""Maintain db function get_registration_num here."""
from alembic_utils.pg_function import PGFunction


get_registration_num = PGFunction(
    schema="public",
    signature="get_registration_num()",
    definition="""
    RETURNS VARCHAR
    LANGUAGE plpgsql
    AS
    $$
    BEGIN
        RETURN trim(to_char(nextval('registration_num_seq'), '000000')) || 'B';
    END
    ; 
    $$;
    """
)
