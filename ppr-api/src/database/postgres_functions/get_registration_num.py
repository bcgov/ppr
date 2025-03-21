"""Maintain db function get_registration_num here."""
from alembic_utils.pg_function import PGFunction

# Assets 19027
# Update database function to generate registration numbers: roll over 99****Q to 100000R
# CREATE SEQUENCE registration_num_r_seq INCREMENT 1 START 100000;
get_registration_num = PGFunction(
    schema="public",
    signature="get_registration_num()",
    definition=r"""
    RETURNS VARCHAR
    LANGUAGE plpgsql
    AS
    $$
    BEGIN
        RETURN trim(to_char(nextval('registration_num_r_seq'), '000000')) || 'R';
    END
    ; 
    $$;
    """
)
