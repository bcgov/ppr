"""Maintain db function searchkey_first_name here."""
from alembic_utils.pg_function import PGFunction


business_name_strip_designation = PGFunction(
    schema="public",
    signature="business_name_strip_designation(actual_name character varying)",
    definition="""
    RETURNS character varying
    LANGUAGE plpgsql
    AS $function$
  DECLARE
    v_base VARCHAR(150);
  BEGIN
    -- Remove suffixes
    v_base := regexp_replace(
                 regexp_replace(
                   regexp_replace(actual_name,'[^\w\s]+','','gi'),
                   '\y(CORPORATION|INCORPORATED|INCORPOREE|LIMITED|LIMITEE|NON PERSONAL LIABILITY|CORP|INC|LTD|LTEE|NPL|ULC)\y','','gi'),
                 '\s+', '', 'gi');
    RETURN TRIM(v_base);
  END
    ; 
    $function$;
    """
)
