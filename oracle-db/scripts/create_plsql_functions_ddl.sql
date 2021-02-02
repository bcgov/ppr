DROP FUNCTION get_document_num;
CREATE FUNCTION get_document_num
  RETURN VARCHAR2
  IS
  BEGIN
    RETURN 'D' || to_char(document_num_seq.nextval);
  END
;

DROP FUNCTION get_registration_num;
CREATE FUNCTION get_registration_num
  RETURN VARCHAR2
  IS
  BEGIN
    RETURN to_char(registration_num_seq.nextval) || 'B';
  END
;
