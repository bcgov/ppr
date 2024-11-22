"""Maintain db function get_mhr_draft_number here."""
from alembic_utils.pg_function import PGFunction


get_mhr_draft_number = PGFunction(
  schema="public",
  signature="get_mhr_draft_number()",
  definition=r"""
  RETURNS VARCHAR
  LANGUAGE plpgsql
  AS
  $$
    BEGIN
        RETURN trim(to_char(nextval('mhr_draft_number_seq'), '000000'));
    END
  ; 
  $$;
  """
)
