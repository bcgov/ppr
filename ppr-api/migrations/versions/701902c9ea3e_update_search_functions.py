"""update search functions.

Revision ID: 701902c9ea3e
Revises: c868a87ae202
Create Date: 2022-01-07 13:36:59.196783

"""
from alembic import op
import sqlalchemy as sa
from alembic_utils.pg_function import PGFunction
from sqlalchemy import text as sql_text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '701902c9ea3e'
down_revision = 'c868a87ae202'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    public_sim_number = PGFunction(
        schema="public",
        signature="sim_number(actual_name character varying)",
        definition="RETURNS numeric\n LANGUAGE plpgsql\nAS $function$\nDECLARE\n   v_name VARCHAR(60);\n   v_sim_number DECIMAL;\n  BEGIN\n     v_name := regexp_replace(actual_name, '(.)\x01{1,}', '\x01', 'g');\n\n     if length((SELECT public.searchkey_last_name(v_name))) <= 3 then\n\t v_sim_number := .65 ;\n\t else\n\t v_sim_number := .46 ;\n   end if;\n  return v_sim_number;\n  END\n    ; \n    $function$"
    )
    op.create_entity(public_sim_number)

    public_individual_split_1 = PGFunction(
        schema="public",
        signature="individual_split_1(actual_name character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $function$\n    DECLARE\n    v_last_name VARCHAR(150);\n    v_split_1 VARCHAR(50);\n    BEGIN\n            -- Remove special characters last name\n            v_last_name := regexp_replace(ACTUAL_NAME,'[^\\w]+',' ','gi');\n            -- Remove prefixes last name\n            v_last_name := regexp_replace(v_last_name,'DR |MR |MRS |MS |CH |DE |DO |DA |LE |LA |MA |^[A-Z] ','','i');\n            -- Remove suffixes last name\n            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$| I$| II$| III$','','gi');\n            v_last_name := regexp_replace(v_last_name,' I$| II$| III$','','gi');\n            v_last_name := regexp_replace(v_last_name,' I $| II $| III $','','gi');\n            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$','','gi');\n            -- Split first name\n            v_last_name := trim(v_last_name);\n            v_split_1 := split_part(v_last_name,' ',1);\n        RETURN UPPER(v_split_1);\n\n    END\n    ; \n    $function$"
    )
    op.create_entity(public_individual_split_1)

    public_individual_split_2 = PGFunction(
        schema="public",
        signature="individual_split_2(actual_name character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $function$\n    DECLARE\n    v_last_name VARCHAR(150);\n    v_split_2 VARCHAR(50);\n    BEGIN\n            -- Remove special characters last name\n            v_last_name := regexp_replace(ACTUAL_NAME,'[^\\w]+',' ','gi');\n            -- Remove prefixes last name\n            v_last_name := regexp_replace(v_last_name,'DR |MR |MRS |MS |CH |DE |DO |DA |LE |LA |MA |^[A-Z] ','','i');\n            --Remove words\n            v_last_name := regexp_replace(v_last_name,' CH | DO | DA | LA | MA ',' ','gi');\n            -- Remove suffixes last name\n            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$| I$| II$| III$',' ','gi');\n            v_last_name := regexp_replace(v_last_name,' I$| II$| III$',' ','gi');\n            v_last_name := regexp_replace(v_last_name,' I $| II $| III $',' ','gi');\n            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$',' ','gi');\n            v_last_name := trim(v_last_name);\n            -- Split first name\n            v_split_2 := split_part(v_last_name,' ',2);\n        RETURN UPPER(v_split_2);\n\n    END\n    ; \n    $function$"
    )
    op.create_entity(public_individual_split_2)

    public_individual_split_3 = PGFunction(
        schema="public",
        signature="individual_split_3(actual_name character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $function$\n    DECLARE\n    v_last_name VARCHAR(150);\n    v_split_3 VARCHAR(50);\n    BEGIN\n            -- Remove special characters last name\n            v_last_name := regexp_replace(ACTUAL_NAME,'[^\\w]+',' ','gi');\n            -- Remove prefixes last name\n            v_last_name := regexp_replace(v_last_name,'DR |MR |MRS |MS |CH |DE |DO |DA |LE |LA |MA |^[A-Z] ','','i');\n            -- Remove suffixes last name\n            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$| I$| II$| III$','','gi');\n            v_last_name := regexp_replace(v_last_name,' I$| II$| III$','','gi');\n            v_last_name := regexp_replace(v_last_name,' I $| II $| III $','','gi');\n            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$','','gi');\n            v_last_name := trim(v_last_name);\n            -- Split first name\n            v_split_3 := split_part(v_last_name,' ',3);\n        RETURN UPPER(v_split_3);\n\n    END\n    ; \n    $function$"
    )
    op.create_entity(public_individual_split_3)

    public_searchkey_individual = PGFunction(
        schema="public",
        signature="searchkey_individual(last_name character varying, first_name character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $function$\n    DECLARE\n            v_ind_key VARCHAR(50);\n            v_last_name VARCHAR(50);\n            v_first_name VARCHAR(50);\n        BEGIN\n            -- Remove special characters last name\n            v_last_name := regexp_replace(LAST_NAME,'[^\\w]+',' ','gi');\n            -- Remove prefixes last name\n            v_last_name := regexp_replace(v_last_name,'^DR |^MR |^MRS |^MS ','','gi');\n            -- Remove suffixes last name\n            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$| I$| II$| III$','','gi');\n            v_last_name := regexp_replace(v_last_name,' I$| II$| III$','','gi');\n            v_last_name := regexp_replace(v_last_name,' I $| II $| III $','','gi');\n            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$','','gi');\n            -- Remove repeating letters\n            v_last_name := regexp_replace(v_last_name, '(.)\x01{1,}', '\x01', 'g');\n            -- Remove extra spaces\n            v_last_name := trim(regexp_replace(v_last_name, '\\s+', '', 'gi'));\n            -- Remove special characters first name\n            v_first_name := regexp_replace(first_name,'[^\\w]+',' ','gi');\n            -- Remove prefixes first name\n            v_first_name := regexp_replace(v_first_name,'^DR |^MR |^MRS |^MS ','','gi');\n            -- Remove suffixes first name\n            v_first_name := regexp_replace(v_first_name,' DR$| JR$|JR$| SR$|SR$| I$| II$| III$','','gi');\n            v_first_name := regexp_replace(v_first_name,' I$| II$| III$','','gi');\n            v_first_name := regexp_replace(v_first_name,' I $| II $| III $','','gi');\n            v_first_name := regexp_replace(v_first_name,' DR$| JR$|JR$| SR$|SR$','','gi');\n            -- Remove repeating letters\n            v_first_name := regexp_replace(v_first_name, '(.)\x01{1,}', '\x01', 'g');\n            -- Remove extra spaces\n            v_first_name := trim(regexp_replace(v_first_name, '\\s+', '', 'gi'));\n            -- join last first name\n            v_ind_key := v_last_name||' '||v_first_name;\n\n\n\n        RETURN UPPER(v_ind_key);\n        END\n    ; \n    $function$"
    )
    op.create_entity(public_searchkey_individual)

    public_match_individual_name = PGFunction(
        schema="public",
        signature="match_individual_name(lastname character varying,firstname character varying,sim_last real,sim_first real,sim_def real)",
        definition="RETURNS integer[]\n LANGUAGE plpgsql\n    AS $function$\n    DECLARE\n        v_ids  INTEGER ARRAY;\n    BEGIN\n\n        SET pg_trgm.similarity_threshold = 0.29; -- assigning from variable does not work\n\n        WITH q AS (SELECT(SELECT public.searchkey_individual(lastname, firstname)) AS INDKEY,\n                        lastname AS LAST,\n                        firstname AS FIRST,\n                (SELECT public.sim_number(lastname)) as simnumber,\n                (SELECT public.individual_split_1(lastname)) AS SPLIT1,\n                (SELECT public.individual_split_2(lastname)) AS SPLIT2,\n                (SELECT public.individual_split_3(lastname)) AS SPLIT3,\n                (SELECT public.individual_split_1(firstname)) AS SPLIT4, \n                (SELECT public.individual_split_2(firstname)) AS SPLIT5\n                )\n        SELECT array_agg(p.id)\n        INTO v_ids\n        FROM PARTIES p,q\n        WHERE p.PARTY_TYPE = 'DI'\n        AND p.REGISTRATION_ID_END IS NULL\n        AND p.LAST_NAME = LAST\n        AND (p.FIRST_NAME = FIRST OR p.MIDDLE_INITIAL= FIRST OR \n                p.FIRST_NAME IN (SELECT NAME \n                                FROM public.NICKNAMES \n                                WHERE NAME_ID IN (SELECT NAME_ID \n                                                    FROM public.NICKNAMES WHERE(UPPER(FIRST)) = NAME))\n            )\n            OR (p.PARTY_TYPE = 'DI' AND \n                p.REGISTRATION_ID_END IS NULL AND \n                SIMILARITY(p.FIRST_NAME_KEY, indkey) >= SIMNUMBER AND \n                SUBSTR(p.FIRST_NAME_KEY,1,1)=SUBSTR(INDKEY,1,1) AND \n                SIMILARITY(p.FIRST_NAME,FIRST)>= sim_first AND \n                (LENGTH(LAST) BETWEEN LENGTH(p.LAST_NAME)-3 AND LENGTH(p.LAST_NAME)+3 OR LENGTH(LAST)>=10)\n            )\n            OR (p.PARTY_TYPE = 'DI' AND  \n                p.REGISTRATION_ID_END IS NULL AND  \n                SIMILARITY(p.FIRST_NAME,FIRST)>= sim_first AND \n                ((SELECT public.individual_split_1(p.LAST_NAME)) = SPLIT1 OR    \n                (SELECT public.individual_split_2(p.LAST_NAME)) = SPLIT1 and (SELECT public.individual_split_2(p.LAST_NAME)) != '' OR    \n                (SELECT public.individual_split_3(p.LAST_NAME)) = SPLIT1 and (SELECT public.individual_split_3(p.LAST_NAME)) != '' OR    \n                (SELECT public.individual_split_1(p.LAST_NAME)) = SPLIT2 OR    \n                (SELECT public.individual_split_2(p.LAST_NAME)) = SPLIT2 and (SELECT public.individual_split_2(p.LAST_NAME)) != '' OR    \n                (SELECT public.individual_split_3(p.LAST_NAME)) = SPLIT2 and (SELECT public.individual_split_3(p.LAST_NAME)) != '' OR    \n                (SELECT public.individual_split_1(p.LAST_NAME)) = SPLIT3 OR    \n                (SELECT public.individual_split_2(p.LAST_NAME)) = SPLIT3 and (SELECT public.individual_split_2(p.LAST_NAME)) != '' OR    \n                (SELECT public.individual_split_3(p.LAST_NAME)) = SPLIT3 and (SELECT public.individual_split_3(p.LAST_NAME)) != ''\n                )\n            )\n            OR (p.PARTY_TYPE = 'DI' AND  \n                p.REGISTRATION_ID_END IS NULL AND  \n                SIMILARITY(p.LAST_NAME,LAST)>= SIMNUMBER AND \n                ((SELECT public.individual_split_1(p.FIRST_NAME)) = SPLIT4 OR    \n                (SELECT public.individual_split_2(p.FIRST_NAME)) = SPLIT4 and (SELECT public.individual_split_2(p.FIRST_NAME)) != '' OR    \n                (SELECT public.individual_split_1(p.FIRST_NAME)) = SPLIT5 OR    \n                (SELECT public.individual_split_2(p.FIRST_NAME)) = SPLIT5 and (SELECT public.individual_split_2(p.FIRST_NAME)) != ''\n                )\n            )\n        ;\n        RETURN v_ids;\n    END\n    ; \n    $function$"
    )
    op.create_entity(public_match_individual_name)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    public_match_individual_name = PGFunction(
        schema="public",
        signature="match_individual_name(lastname character varying,firstname character varying,sim_last real,sim_first real,sim_def real)",
        definition="RETURNS integer[]\n LANGUAGE plpgsql\n    AS $function$\n    DECLARE\n        v_ids  INTEGER ARRAY;\n    BEGIN\n\n        SET pg_trgm.similarity_threshold = 0.29; -- assigning from variable does not work\n\n        WITH q AS (SELECT(SELECT public.searchkey_individual(lastname, firstname)) AS INDKEY,\n                        lastname AS LAST,\n                        firstname AS FIRST,\n                (SELECT public.sim_number(lastname)) as simnumber,\n                (SELECT public.individual_split_1(lastname)) AS SPLIT1,\n                (SELECT public.individual_split_2(lastname)) AS SPLIT2,\n                (SELECT public.individual_split_3(lastname)) AS SPLIT3,\n                (SELECT public.individual_split_1(firstname)) AS SPLIT4, \n                (SELECT public.individual_split_2(firstname)) AS SPLIT5\n                )\n        SELECT array_agg(p.id)\n        INTO v_ids\n        FROM PARTIES p,q\n        WHERE p.PARTY_TYPE = 'DI'\n        AND p.REGISTRATION_ID_END IS NULL\n        AND p.LAST_NAME = LAST\n        AND (p.FIRST_NAME = FIRST OR p.MIDDLE_INITIAL= FIRST OR \n                p.FIRST_NAME IN (SELECT NAME \n                                FROM public.NICKNAMES \n                                WHERE NAME_ID IN (SELECT NAME_ID \n                                                    FROM public.NICKNAMES WHERE(UPPER(FIRST)) = NAME))\n            )\n            OR (p.PARTY_TYPE = 'DI' AND \n                p.REGISTRATION_ID_END IS NULL AND \n                SIMILARITY(p.FIRST_NAME_KEY, indkey) >= SIMNUMBER AND \n                SUBSTR(p.FIRST_NAME_KEY,1,1)=SUBSTR(INDKEY,1,1) AND \n                SIMILARITY(p.FIRST_NAME,FIRST)>= sim_first AND \n                (LENGTH(LAST) BETWEEN LENGTH(p.LAST_NAME)-3 AND LENGTH(p.LAST_NAME)+3 OR LENGTH(LAST)>=10)\n            )\n            OR (p.PARTY_TYPE = 'DI' AND  \n                p.REGISTRATION_ID_END IS NULL AND  \n                SIMILARITY(p.FIRST_NAME,FIRST)>= sim_first AND \n                ((SELECT public.individual_split_1(p.LAST_NAME)) = SPLIT1 OR    \n                (SELECT public.individual_split_2(p.LAST_NAME)) = SPLIT1 and (SELECT public.individual_split_2(p.LAST_NAME)) != '' OR    \n                (SELECT public.individual_split_3(p.LAST_NAME)) = SPLIT1 and (SELECT public.individual_split_3(p.LAST_NAME)) != '' OR    \n                (SELECT public.individual_split_1(p.LAST_NAME)) = SPLIT2 OR    \n                (SELECT public.individual_split_2(p.LAST_NAME)) = SPLIT2 and (SELECT public.individual_split_2(p.LAST_NAME)) != '' OR    \n                (SELECT public.individual_split_3(p.LAST_NAME)) = SPLIT2 and (SELECT public.individual_split_3(p.LAST_NAME)) != '' OR    \n                (SELECT public.individual_split_1(p.LAST_NAME)) = SPLIT3 OR    \n                (SELECT public.individual_split_2(p.LAST_NAME)) = SPLIT3 and (SELECT public.individual_split_2(p.LAST_NAME)) != '' OR    \n                (SELECT public.individual_split_3(p.LAST_NAME)) = SPLIT3 and (SELECT public.individual_split_3(p.LAST_NAME)) != ''\n                )\n            )\n            OR (p.PARTY_TYPE = 'DI' AND  \n                p.REGISTRATION_ID_END IS NULL AND  \n                SIMILARITY(p.LAST_NAME,LAST)>= SIMNUMBER AND \n                ((SELECT public.individual_split_1(p.FIRST_NAME)) = SPLIT4 OR    \n                (SELECT public.individual_split_2(p.FIRST_NAME)) = SPLIT4 and (SELECT public.individual_split_2(p.FIRST_NAME)) != '' OR    \n                (SELECT public.individual_split_1(p.FIRST_NAME)) = SPLIT5 OR    \n                (SELECT public.individual_split_2(p.FIRST_NAME)) = SPLIT5 and (SELECT public.individual_split_2(p.FIRST_NAME)) != ''\n                )\n            )\n        ;\n        RETURN v_ids;\n    END\n    ; \n    $function$"
    )
    op.drop_entity(public_match_individual_name)

    public_searchkey_individual = PGFunction(
        schema="public",
        signature="searchkey_individual(last_name character varying, first_name character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $function$\n    DECLARE\n            v_ind_key VARCHAR(50);\n            v_last_name VARCHAR(50);\n            v_first_name VARCHAR(50);\n        BEGIN\n            -- Remove special characters last name\n            v_last_name := regexp_replace(LAST_NAME,'[^\\w]+',' ','gi');\n            -- Remove prefixes last name\n            v_last_name := regexp_replace(v_last_name,'^DR |^MR |^MRS |^MS ','','gi');\n            -- Remove suffixes last name\n            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$| I$| II$| III$','','gi');\n            v_last_name := regexp_replace(v_last_name,' I$| II$| III$','','gi');\n            v_last_name := regexp_replace(v_last_name,' I $| II $| III $','','gi');\n            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$','','gi');\n            -- Remove repeating letters\n            v_last_name := regexp_replace(v_last_name, '(.)\x01{1,}', '\x01', 'g');\n            -- Remove extra spaces\n            v_last_name := trim(regexp_replace(v_last_name, '\\s+', '', 'gi'));\n            -- Remove special characters first name\n            v_first_name := regexp_replace(first_name,'[^\\w]+',' ','gi');\n            -- Remove prefixes first name\n            v_first_name := regexp_replace(v_first_name,'^DR |^MR |^MRS |^MS ','','gi');\n            -- Remove suffixes first name\n            v_first_name := regexp_replace(v_first_name,' DR$| JR$|JR$| SR$|SR$| I$| II$| III$','','gi');\n            v_first_name := regexp_replace(v_first_name,' I$| II$| III$','','gi');\n            v_first_name := regexp_replace(v_first_name,' I $| II $| III $','','gi');\n            v_first_name := regexp_replace(v_first_name,' DR$| JR$|JR$| SR$|SR$','','gi');\n            -- Remove repeating letters\n            v_first_name := regexp_replace(v_first_name, '(.)\x01{1,}', '\x01', 'g');\n            -- Remove extra spaces\n            v_first_name := trim(regexp_replace(v_first_name, '\\s+', '', 'gi'));\n            -- join last first name\n            v_ind_key := v_last_name||' '||v_first_name;\n\n\n\n        RETURN UPPER(v_ind_key);\n        END\n    ; \n    $function$"
    )
    op.drop_entity(public_searchkey_individual)

    public_individual_split_3 = PGFunction(
        schema="public",
        signature="individual_split_3(actual_name character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $function$\n    DECLARE\n    v_last_name VARCHAR(150);\n    v_split_3 VARCHAR(50);\n    BEGIN\n            -- Remove special characters last name\n            v_last_name := regexp_replace(ACTUAL_NAME,'[^\\w]+',' ','gi');\n            -- Remove prefixes last name\n            v_last_name := regexp_replace(v_last_name,'DR |MR |MRS |MS |CH |DE |DO |DA |LE |LA |MA |^[A-Z] ','','i');\n            -- Remove suffixes last name\n            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$| I$| II$| III$','','gi');\n            v_last_name := regexp_replace(v_last_name,' I$| II$| III$','','gi');\n            v_last_name := regexp_replace(v_last_name,' I $| II $| III $','','gi');\n            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$','','gi');\n            v_last_name := trim(v_last_name);\n            -- Split first name\n            v_split_3 := split_part(v_last_name,' ',3);\n        RETURN UPPER(v_split_3);\n\n    END\n    ; \n    $function$"
    )
    op.drop_entity(public_individual_split_3)

    public_individual_split_2 = PGFunction(
        schema="public",
        signature="individual_split_2(actual_name character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $function$\n    DECLARE\n    v_last_name VARCHAR(150);\n    v_split_2 VARCHAR(50);\n    BEGIN\n            -- Remove special characters last name\n            v_last_name := regexp_replace(ACTUAL_NAME,'[^\\w]+',' ','gi');\n            -- Remove prefixes last name\n            v_last_name := regexp_replace(v_last_name,'DR |MR |MRS |MS |CH |DE |DO |DA |LE |LA |MA |^[A-Z] ','','i');\n            --Remove words\n            v_last_name := regexp_replace(v_last_name,' CH | DO | DA | LA | MA ',' ','gi');\n            -- Remove suffixes last name\n            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$| I$| II$| III$',' ','gi');\n            v_last_name := regexp_replace(v_last_name,' I$| II$| III$',' ','gi');\n            v_last_name := regexp_replace(v_last_name,' I $| II $| III $',' ','gi');\n            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$',' ','gi');\n            v_last_name := trim(v_last_name);\n            -- Split first name\n            v_split_2 := split_part(v_last_name,' ',2);\n        RETURN UPPER(v_split_2);\n\n    END\n    ; \n    $function$"
    )
    op.drop_entity(public_individual_split_2)

    public_individual_split_1 = PGFunction(
        schema="public",
        signature="individual_split_1(actual_name character varying)",
        definition="RETURNS character varying\n    LANGUAGE plpgsql\n    AS $function$\n    DECLARE\n    v_last_name VARCHAR(150);\n    v_split_1 VARCHAR(50);\n    BEGIN\n            -- Remove special characters last name\n            v_last_name := regexp_replace(ACTUAL_NAME,'[^\\w]+',' ','gi');\n            -- Remove prefixes last name\n            v_last_name := regexp_replace(v_last_name,'DR |MR |MRS |MS |CH |DE |DO |DA |LE |LA |MA |^[A-Z] ','','i');\n            -- Remove suffixes last name\n            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$| I$| II$| III$','','gi');\n            v_last_name := regexp_replace(v_last_name,' I$| II$| III$','','gi');\n            v_last_name := regexp_replace(v_last_name,' I $| II $| III $','','gi');\n            v_last_name := regexp_replace(v_last_name,' DR$| JR$|JR$| SR$|SR$','','gi');\n            -- Split first name\n            v_last_name := trim(v_last_name);\n            v_split_1 := split_part(v_last_name,' ',1);\n        RETURN UPPER(v_split_1);\n\n    END\n    ; \n    $function$"
    )
    op.drop_entity(public_individual_split_1)

    public_sim_number = PGFunction(
        schema="public",
        signature="sim_number(actual_name character varying)",
        definition="RETURNS numeric\n LANGUAGE plpgsql\nAS $function$\nDECLARE\n   v_name VARCHAR(60);\n   v_sim_number DECIMAL;\n  BEGIN\n     v_name := regexp_replace(actual_name, '(.)\x01{1,}', '\x01', 'g');\n\n     if length((SELECT public.searchkey_last_name(v_name))) <= 3 then\n\t v_sim_number := .65 ;\n\t else\n\t v_sim_number := .46 ;\n   end if;\n  return v_sim_number;\n  END\n    ; \n    $function$"
    )
    op.drop_entity(public_sim_number)

    # ### end Alembic commands ###
