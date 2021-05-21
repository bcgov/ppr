"""Maintain db function get_draft_document_number here."""
from alembic_utils.pg_function import PGFunction


get_draft_document_number = PGFunction(
  schema="public",
  signature="get_draft_document_number()",
  definition="""
  RETURNS VARCHAR
  LANGUAGE plpgsql
  AS
  $$
    BEGIN
      RETURN 'D' || trim(to_char(nextval('document_number_seq'), '0000000'));
    END
  ; 
  $$;
  """
)
