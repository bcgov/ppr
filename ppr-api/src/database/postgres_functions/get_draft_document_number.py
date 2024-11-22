"""Maintain db function get_draft_document_number here."""
from alembic_utils.pg_function import PGFunction


get_draft_document_number = PGFunction(
  schema="public",
  signature="get_draft_document_number()",
  definition=r"""
  RETURNS VARCHAR
  LANGUAGE plpgsql
  AS
  $$
    DECLARE
      v_id INTEGER;
      v_doc_num VARCHAR(10);
    BEGIN
      v_id := nextval('document_number_seq');
      IF v_id >= 10000000 THEN
        v_doc_num := 'D' || trim(to_char(nextval('document_number_seq'), '00000000'));
      ELSE
        v_doc_num := 'D' || trim(to_char(nextval('document_number_seq'), '0000000'));
      END IF;
      RETURN v_doc_num;
    END
  ; 
  $$;
  """
)
