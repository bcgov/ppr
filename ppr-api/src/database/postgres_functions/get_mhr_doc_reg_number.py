"""Maintain db function get_mhr_doc_reg_number here."""
from alembic_utils.pg_function import PGFunction


get_mhr_doc_reg_number = PGFunction(
  schema="public",
  signature="get_mhr_doc_reg_number()",
  definition=r"""
  RETURNS VARCHAR
  LANGUAGE plpgsql
  AS
  $$
    BEGIN
        RETURN trim(to_char(nextval('mhr_doc_reg_seq'), '00000000'));
    END
  ; 
  $$;
  """
)
