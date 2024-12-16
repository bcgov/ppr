"""Maintain db function mhr_serial_compressed_key here."""
from alembic_utils.pg_function import PGFunction


mhr_serial_compressed_key = PGFunction(
  schema="public",
  signature="mhr_serial_compressed_key(v_serial character varying)",
  definition=r"""
  RETURNS character varying
  IMMUTABLE
  LANGUAGE plpgsql
  AS
  $$
    declare
    v_key VARCHAR(40);
    last_pos integer := 6;
    i integer := 1;
    begin
    v_key := upper(v_serial);
    v_key := REGEXP_REPLACE(v_key, '[^0-9A-Za-z]','','gi');
    v_key := '000000' || v_key;
    for i in 1 .. LENGTH(v_key)
    loop
        if POSITION(substring(v_key, i, 1) in '0123456789') > 0 then
        last_pos := i;
        end if;
    end loop;
    v_key := replace(v_key, 'B', '8');
    v_key := replace(v_key, 'C', '6');
    v_key := replace(v_key, 'G', '6');
    v_key := replace(v_key, 'H', '4');
    v_key := replace(v_key, 'I', '1');
    v_key := replace(v_key, 'L', '1');
    v_key := replace(v_key, 'S', '5');
    v_key := replace(v_key, 'Y', '4');
    v_key := replace(v_key, 'Z', '2');
    v_key := REGEXP_REPLACE(v_key, '[^0-9]','0','gi');
    v_key := substring(v_key, last_pos - 5, 6);
    return v_key;
    end;
  $$;
  """
)
