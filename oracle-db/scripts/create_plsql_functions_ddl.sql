DROP FUNCTION get_draft_document_number;
CREATE FUNCTION get_draft_document_number
  RETURN VARCHAR2
  IS
  BEGIN
    RETURN 'D'||to_char(DOCUMENT_NUMBER_SEQ.nextval);
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
