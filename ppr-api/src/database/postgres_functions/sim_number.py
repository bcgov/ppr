"""Maintain db function searchkey_first_name here."""
from alembic_utils.pg_function import PGFunction


sim_number = PGFunction(
    schema="public",
    signature="sim_number(actual_name character varying)",
    definition="""
 RETURNS numeric
 LANGUAGE plpgsql
AS $function$
DECLARE
   v_name VARCHAR(60);
   v_sim_number DECIMAL;
  BEGIN
     v_name := regexp_replace(actual_name, '(.)\1{1,}', '\1', 'g');

     if length((SELECT public.searchkey_last_name(v_name))) <= 3 then
	 v_sim_number := .65 ;
	 else
	 v_sim_number := .46 ;
   end if;
  return v_sim_number;
  END
    ; 
    $function$;
    """
)
