"""Maintain db function mhr_name_compressed_key here."""
from alembic_utils.pg_function import PGFunction


mhr_name_compressed_key = PGFunction(
  schema="public",
  signature="mhr_name_compressed_key(v_name character varying)",
  definition=r"""
  RETURNS character varying
  IMMUTABLE
  LANGUAGE plpgsql
  AS
  $$
    declare
    v_key VARCHAR(250);
    begin
    v_key := upper(v_name);
    if position(left(v_key, 1) in '&#ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890') < 1 then
        v_key := substring(v_key, 2);
    end if;
    if left(v_key, 4) = 'THE ' then
        v_key := substring(v_key, 5);
    end if;
    v_key := regexp_replace(v_key, '[^0-9A-Z&#]+', '', 'gi');
    if left(v_key, 15) = 'BRITISHCOLUMBIA' then
        v_key := 'BC' || substring(v_key, 16);
    end if;
    v_key := replace(v_key, '#', 'NUMBER');
    v_key := replace(v_key, '&', 'AND');
    v_key := replace(v_key, '0', 'ZERO');
    v_key := replace(v_key, '1', 'ONE');
    v_key := replace(v_key, '2', 'TWO');
    v_key := replace(v_key, '3', 'THREE');
    v_key := replace(v_key, '4', 'FOUR');
    v_key := replace(v_key, '5', 'FIVE');
    v_key := replace(v_key, '6', 'SIX');
    v_key := replace(v_key, '7', 'SEVEN');
    v_key := replace(v_key, '8', 'EIGHT');
    v_key := replace(v_key, '9', 'NINE');
    if length(v_key) > 30 then
        v_key := substring(v_key, 1, 30);
    end if;
    return v_key;
    end;
  $$;
  """
)
