-- Assets 19027 begin DEV 2023-12-14, TEST 2023-12-, SANDBOX 2023-12-, PROD 2023-12-22
-- Update database function to generate registration numbers: roll over 99****P to 100000Q

select pg_get_functiondef(p.oid) FROM pg_proc p WHERE p.proname = 'get_registration_num';

CREATE SEQUENCE registration_num_q_seq INCREMENT 1 START 100000;

CREATE OR REPLACE FUNCTION public.get_registration_num()
 RETURNS character varying
 LANGUAGE plpgsql
AS $function$
    DECLARE
      v_value integer;
    BEGIN
        RETURN trim(to_char(nextval('registration_num_q_seq'), '000000')) || 'Q';
    END
    ; 
$function$

-- Test
SELECT get_registration_num();
-- Assets 19027 end
