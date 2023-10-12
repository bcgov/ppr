# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Model for generating historical search JSON.

Search for exact matches as of a past date and time.
"""
# flake8: noqa Q000,E122,E131
# Disable Q000: Allow query strings to be in double quotation marks that contain single quotation marks.
# Disable E122: allow query strings to be more human readable.
# Disable E131: allow query strings to be more human readable.
from flask import current_app
from sqlalchemy.sql import text

from ppr_api.exceptions import DatabaseException
from ppr_api.models import db, FinancingStatement, utils as model_utils, SearchRequest, SearchResult, Party
from ppr_api.models import GeneralCollateralLegacy, search_utils


SEARCH_HISTORICAL_ID_QUERY = """
select MAX(id)
  from registrations
 where registration_ts <= (TO_TIMESTAMP('?', 'YYYY-MM-DD HH24:MI:SSTZHH') at time zone 'utc')
   and id < 200000000
"""
# Serial number search base where clause
SERIAL_SEARCH_BASE = """
SELECT r.registration_type,r.registration_ts AS base_registration_ts,
        sc.serial_type,sc.serial_number,sc.year,sc.make,sc.model,
        r.registration_number AS base_registration_num,
        CASE WHEN serial_number = :query_value3 THEN 'EXACT' ELSE 'SIMILAR' END match_type,
        fs.expire_date,fs.state_type,sc.id AS vehicle_id, sc.mhr_number
  FROM registrations r, financing_statements fs, serial_collateral sc 
 WHERE r.financing_id = fs.id
   AND r.id <= :query_value1
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN')
   AND r.base_reg_number IS NULL
   AND (fs.expire_date IS NULL OR 
        fs.expire_date > ((TO_TIMESTAMP(:query_value2, 
                                        'YYYY-MM-DD HH24:MI:SSTZHH') at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id 
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((TO_TIMESTAMP(:query_value2,
                                                              'YYYY-MM-DD HH24:MI:SSTZHH') at time zone 'utc') - 
                                                interval '30 days'))
   AND sc.financing_id = fs.id
   AND sc.registration_id_end IS NULL
"""

# Equivalent logic as DB view search_by_reg_num_vw, but API determines the where clause.
REG_NUM_QUERY = """
SELECT r2.registration_type, r2.registration_ts AS base_registration_ts, 
       r2.registration_number AS base_registration_num,
       'EXACT' AS match_type, fs.state_type, fs.expire_date
  FROM registrations r, financing_statements fs, registrations r2
 WHERE r.financing_id = fs.id
   AND r.id <= :query_value1
   AND r2.financing_id = fs.id
   AND r2.registration_type_cl IN ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN')
   AND r.registration_number = :query_value3
   AND (fs.expire_date IS NULL OR 
        fs.expire_date > ((TO_TIMESTAMP(:query_value2, 
                                        'YYYY-MM-DD HH24:MI:SSTZHH') at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id 
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((TO_TIMESTAMP(:query_value2,
                                                              'YYYY-MM-DD HH24:MI:SSTZHH') at time zone 'utc') - 
                                                interval '30 days'))
"""

MHR_NUM_QUERY = SERIAL_SEARCH_BASE + """
   AND sc.serial_type = 'MH' 
   AND sc.mhr_number = (SELECT searchkey_mhr(:query_value3)) 
ORDER BY match_type, sc.serial_number ASC, sc.year ASC, r.registration_ts ASC
"""
SERIAL_NUM_QUERY = 'SELECT * FROM ( ' + SERIAL_SEARCH_BASE + """
   AND sc.serial_type NOT IN ('AC', 'AF', 'AP')
   AND sc.srch_vin = (SELECT searchkey_vehicle(:query_value3)) 
ORDER BY match_type, sc.serial_number ASC, sc.year ASC, r.registration_ts ASC
) AS q 
 WHERE q.match_type = 'EXACT'
 ORDER BY q.serial_number ASC, q.year ASC, q.base_registration_ts ASC
"""
AIRCRAFT_DOT_QUERY = 'SELECT * FROM ( ' + SERIAL_SEARCH_BASE + """
   AND sc.serial_type IN ('AC', 'AF', 'AP')
   AND sc.srch_vin = (SELECT searchkey_aircraft(:query_value3)) 
ORDER BY match_type, sc.serial_number ASC, sc.year ASC, r.registration_ts ASC
) AS q 
 WHERE q.match_type = 'EXACT'
 ORDER BY q.serial_number ASC, q.year ASC, q.base_registration_ts ASC
"""
BUSINESS_NAME_QUERY = """
WITH q AS (
   SELECT(SELECT searchkey_business_name(:query_bus_name)) AS search_key,
   SUBSTR((SELECT searchkey_business_name(:query_bus_name)),1,1) AS search_key_char1,
   (SELECT business_name_strip_designation(:query_bus_name)) AS search_name_base,
   (SELECT array_length(string_to_array(trim(regexp_replace(:query_bus_name,'^THE','','gi')),' '),1)) AS word_length)
 SELECT r.registration_type,r.registration_ts AS base_registration_ts,
       p.business_name,
       r.registration_number AS base_registration_num,
       CASE WHEN p.bus_name_base = search_name_base THEN 'EXACT'
            ELSE 'SIMILAR' END match_type,
       fs.expire_date,fs.state_type,p.id
  FROM registrations r, financing_statements fs, parties p, q
 WHERE r.financing_id = fs.id
   AND r.id <= :query_value1
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN')
   AND r.base_reg_number IS NULL
   AND (fs.expire_date IS NULL OR 
        fs.expire_date > ((TO_TIMESTAMP(:query_value2, 
                                        'YYYY-MM-DD HH24:MI:SSTZHH') at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((TO_TIMESTAMP(:query_value2,
                                                              'YYYY-MM-DD HH24:MI:SSTZHH') at time zone 'utc') - 
                                                interval '30 days'))
   AND p.financing_id = fs.id
   AND p.registration_id_end IS NULL
   AND p.party_type = 'DB'
   AND p.bus_name_base = search_name_base
   AND p.bus_name_key_char1 = search_key_char1
   AND ((search_key <% p.business_srch_key AND
          SIMILARITY(search_key, p.business_srch_key) >= :query_bus_quotient)
          OR p.business_srch_key = search_key
          OR word_length=1 and search_key = split_part(business_name,' ',1)
          OR (LENGTH(search_key) >= 3 AND LEVENSHTEIN(search_key, p.business_srch_key) <= 1) AND 
              p.bus_name_key_char1 = search_key_char1
    )
ORDER BY p.business_name ASC, r.registration_ts ASC
"""
INDIVIDUAL_NAME_QUERY = """
SELECT * FROM (WITH q AS (SELECT(searchkey_last_name(:query_last)) AS search_last_key)
 SELECT r.registration_type,r.registration_ts AS base_registration_ts,
       p.last_name,p.first_name,p.middle_initial,p.id,
       r.registration_number AS base_registration_num,
       CASE WHEN search_last_key = p.last_name_key AND p.first_name = :query_first THEN 'EXACT'
            WHEN search_last_key = p.last_name_key AND LENGTH(:query_first) = 1 AND
                 :query_first = p.first_name_char1 THEN 'EXACT'
            WHEN search_last_key = p.last_name_key AND LENGTH(p.first_name) = 1 AND
                 p.first_name = LEFT(:query_first, 1) THEN 'EXACT'
            WHEN search_last_key = p.last_name_key AND p.first_name_char2 IS NOT NULL AND p.first_name_char2 = '-' AND
                 p.first_name_char1 = LEFT(:query_first, 1) THEN 'EXACT'
            WHEN search_last_key = p.last_name_key AND LENGTH(:query_first) > 1 AND SUBSTR(:query_first, 2, 1) = '-'
                 AND p.first_name_char1 = LEFT(:query_first, 1) THEN 'EXACT'
            ELSE 'SIMILAR' END match_type,
       fs.expire_date,fs.state_type, p.birth_date
  FROM registrations r, financing_statements fs, parties p, q
 WHERE r.financing_id = fs.id
   AND r.id <= :query_value1
   AND r.registration_type_cl IN ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN')
   AND r.base_reg_number IS NULL
   AND (fs.expire_date IS NULL OR 
        fs.expire_date > ((TO_TIMESTAMP(:query_value2, 
                                        'YYYY-MM-DD HH24:MI:SSTZHH') at time zone 'utc') - interval '30 days'))
   AND NOT EXISTS (SELECT r3.id
                     FROM registrations r3
                    WHERE r3.financing_id = fs.id
                      AND r3.registration_type_cl = 'DISCHARGE'
                      AND r3.registration_ts < ((TO_TIMESTAMP(:query_value2,
                                                              'YYYY-MM-DD HH24:MI:SSTZHH') at time zone 'utc') - 
                                                interval '30 days'))
   AND p.financing_id = fs.id
   AND p.registration_id_end IS NULL
   AND p.party_type = 'DI'
   AND p.id IN (SELECT * FROM unnest(match_individual_name(:query_last, :query_first, :query_last_quotient,
                                                           :query_first_quotient, :query_default_quotient))) 
 ORDER BY match_type, p.last_name ASC, p.first_name ASC, p.middle_initial ASC, p.birth_date ASC,  r.registration_ts ASC
) AS q2 
 WHERE q2.match_type = 'EXACT'
"""
HISTORICAL_ACCOUNT_ID: str = 'HISTORICAL_SEARCH'
HISTORICAL_REF_ID: str = 'HISTORICAL SEARCH'


def get_search_historical_id(search_timestamp: str) -> int:
    """Execute a search to get the total match count for the search criteria. Only call if limit reached."""
    query_text = SEARCH_HISTORICAL_ID_QUERY.replace('?', search_timestamp.replace('T', ' '))
    query = text(query_text)
    result = db.session.execute(query)
    historical_reg_id: int = 0
    if result:
        row = result.first()
        historical_reg_id = int(row[0])
    current_app.logger.debug(f'historical search registration id={historical_reg_id}')
    return historical_reg_id


def search_by_serial_type(search_query: SearchRequest,  # pylint: disable=too-many-locals
                          search_reg_id: int,
                          search_ts: str) -> SearchRequest:
    """Execute a historical search query for a serial number, aircraft, or mhr number search type."""
    search_val: str = search_query.search_criteria['criteria']['value']
    current_app.logger.info(f'search criteria value={search_val}')
    query_text: str = SERIAL_NUM_QUERY
    if search_query.search_type == SearchRequest.SearchTypes.AIRCRAFT_AIRFRAME_DOT.value:
        query_text = AIRCRAFT_DOT_QUERY
    elif search_query.search_type == SearchRequest.SearchTypes.MANUFACTURED_HOME_NUM.value:
        query_text = MHR_NUM_QUERY
        query_text = query_text.replace('CASE WHEN serial_number', 'CASE WHEN mhr_number')
    query = text(query_text)
    rows = None
    try:
        result = db.session.execute(query, {'query_value1': search_reg_id,
                                            'query_value2': search_ts.replace('T', ' '),
                                            'query_value3': search_val})
        rows = result.fetchall()
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('DB search_by_serial_type exception: ' + str(db_exception))
        raise DatabaseException(db_exception)
    results_json = []
    if rows is not None:
        for row in rows:
            registration_type = str(row[0])
            timestamp = row[1]
            collateral = {
                'type': str(row[2]),
                'serialNumber': str(row[3])
            }
            value = row[4]
            if value is not None:
                collateral['year'] = int(value)
            value = row[5]
            if value is not None:
                collateral['make'] = str(value)
            value = row[6]
            if value is not None:
                collateral['model'] = str(value)
            match_type = str(row[8])
            if search_query.search_type == SearchRequest.SearchTypes.MANUFACTURED_HOME_NUM.value:
                collateral['manufacturedHomeRegistrationNumber'] = str(row[12])
            result_json = {
                'baseRegistrationNumber': str(row[7]),
                'matchType': match_type,
                'createDateTime': model_utils.format_ts(timestamp),
                'registrationType': registration_type,
                'vehicleCollateral': collateral
            }
            results_json.append(result_json)
        search_query.returned_results_size = len(results_json)
        search_query.total_results_size = search_query.returned_results_size
    else:
        search_query.returned_results_size = 0
        search_query.total_results_size = 0
    search_query.search_response = results_json
    current_app.logger.info(f'results size={search_query.returned_results_size}')
    return search_query


def search_by_business_name(search_query: SearchRequest,
                            search_reg_id: int,
                            search_ts: str) -> SearchRequest:
    """Execute a debtor business name search query."""
    search_val = search_query.search_criteria['criteria']['debtorName']['business']
    current_app.logger.info(f'search criteria value={search_val}')
    rows = None
    query = text(BUSINESS_NAME_QUERY)
    try:
        result = db.session.execute(query, {'query_value1': search_reg_id,
                                            'query_value2': search_ts.replace('T', ' '),
                                            'query_bus_name': search_val.strip().upper(),
                                            'query_bus_quotient':
                                            current_app.config.get('SIMILARITY_QUOTIENT_BUSINESS_NAME')})
        rows = result.fetchall()
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('DB search_by_business_name exception: ' + str(db_exception))
        raise DatabaseException(db_exception)
    results_json = []
    if rows is not None:
        for row in rows:
            registration_type = str(row[0])
            timestamp = row[1]
            debtor = {
                'businessName': str(row[2]),
                'partyId': int(row[7])
            }
            result_json = {
                'baseRegistrationNumber': str(row[3]),
                'matchType': str(row[4]),
                'createDateTime': model_utils.format_ts(timestamp),
                'registrationType': registration_type,
                'debtor': debtor
            }
            results_json.append(result_json)
        search_query.returned_results_size = len(results_json)
        search_query.total_results_size = search_query.returned_results_size
    else:
        search_query.returned_results_size = 0
        search_query.total_results_size = 0
    search_query.search_response = results_json
    current_app.logger.info(f'results size={search_query.returned_results_size}')
    return search_query


def search_by_individual_name(search_query: SearchRequest,  # pylint: disable=too-many-locals; easier to follow
                              search_reg_id: int,
                              search_ts: str) -> SearchRequest:
    """Execute a debtor individual name search query."""
    last_name = search_query.search_criteria['criteria']['debtorName']['last']
    first_name = search_query.search_criteria['criteria']['debtorName']['first']
    quotient_first = current_app.config.get('SIMILARITY_QUOTIENT_FIRST_NAME')
    quotient_last = current_app.config.get('SIMILARITY_QUOTIENT_LAST_NAME')
    quotient_default = current_app.config.get('SIMILARITY_QUOTIENT_DEFAULT')
    current_app.logger.info(f'search criteria first={first_name} last={last_name}')
    rows = None
    query = text(INDIVIDUAL_NAME_QUERY)
    try:
        result = db.session.execute(query, {'query_value1': search_reg_id,
                                            'query_value2': search_ts.replace('T', ' '),
                                            'query_last': last_name.strip().upper(),
                                            'query_first': first_name.strip().upper(),
                                            'query_last_quotient': quotient_last,
                                            'query_first_quotient': quotient_first,
                                            'query_default_quotient': quotient_default})
        rows = result.fetchall()
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('DB search_by_individual_name exception: ' + str(db_exception))
        raise DatabaseException(db_exception)
    results_json = []
    if rows is not None:
        for row in rows:
            person = {
                'last': str(row[2]),
                'first': str(row[3])
            }
            middle = str(row[4]) if row[4] else ''
            if middle:
                person['middle'] = middle
            debtor = {
                'personName': person,
                'partyId': int(row[5])
            }
            if row[10]:
                debtor['birthDate'] = model_utils.format_ts(row[10])
            result_json = {
                'baseRegistrationNumber': str(row[6]),
                'matchType': str(row[7]),
                'createDateTime': model_utils.format_ts(row[1]),
                'registrationType': str(row[0]),
                'debtor': debtor
            }
            results_json.append(result_json)
        search_query.returned_results_size = len(results_json)
        search_query.total_results_size = search_query.returned_results_size
    else:
        search_query.returned_results_size = 0
        search_query.total_results_size = 0
    search_query.search_response = results_json
    current_app.logger.info(f'results size={search_query.returned_results_size}')
    return search_query


def search_by_registration_number(search_query: SearchRequest,
                                  search_reg_id: int,
                                  search_ts: str) -> SearchRequest:
    """Execute a historical search query for a registration number search type."""
    reg_num: str = search_query.search_criteria['criteria']['value']
    current_app.logger.info(f'search registration number={reg_num}')
    query = text(REG_NUM_QUERY)
    rows = None
    try:
        result = db.session.execute(query, {'query_value1': search_reg_id,
                                            'query_value2': search_ts.replace('T', ' '),
                                            'query_value3': reg_num})
        rows = result.fetchall()
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('DB search_by_registration_number exception: ' + str(db_exception))
        raise DatabaseException(db_exception)
    results_json = []
    if rows is not None:
        for row in rows:
            registration_type = str(row[0])
            timestamp = row[1]
            results_json = [{
                'baseRegistrationNumber': str(row[2]),
                'matchType': str(row[3]),
                'createDateTime': model_utils.format_ts(timestamp),
                'registrationType': registration_type
            }]
            if reg_num != str(row[2]):
                results_json[0]['registrationNumber'] = reg_num

        search_query.returned_results_size = 1
        search_query.total_results_size = 1
    else:
        search_query.returned_results_size = 0
        search_query.total_results_size = 0
    search_query.search_response = results_json
    current_app.logger.info(f'results size={search_query.returned_results_size}')
    return search_query


def search(criteria: dict, search_reg_id: int) -> SearchRequest:
    """Execute a search with the previously set search type and criteria."""
    search_ts: str = criteria.get('searchDateTime')
    search_query: SearchRequest = SearchRequest(search_criteria=criteria,
                                                search_ts=model_utils.ts_from_iso_format(search_ts),
                                                account_id=HISTORICAL_ACCOUNT_ID,
                                                client_reference_id=HISTORICAL_REF_ID)
    search_type = criteria.get('type')
    search_query.search_type = model_utils.TO_DB_SEARCH_TYPE[search_type]
    current_app.logger.info(f'search ts={search_ts} reg_id={search_reg_id} type={search_query.search_type}')
    if search_query.search_type == SearchRequest.SearchTypes.REGISTRATION_NUM.value:
        search_query = search_by_registration_number(search_query, search_reg_id, search_ts)
    elif search_query.search_type == SearchRequest.SearchTypes.MANUFACTURED_HOME_NUM.value:
        # Format before searching
        search_utils.format_mhr_number(criteria)
        search_query = search_by_serial_type(search_query, search_reg_id, search_ts)
    elif search_query.search_type in (SearchRequest.SearchTypes.SERIAL_NUM.value,
                                      SearchRequest.SearchTypes.AIRCRAFT_AIRFRAME_DOT.value):
        search_query = search_by_serial_type(search_query, search_reg_id, search_ts)
    elif search_query.search_type == SearchRequest.SearchTypes.BUSINESS_DEBTOR.value:
        search_query = search_by_business_name(search_query, search_reg_id, search_ts)
    else:
        search_query = search_by_individual_name(search_query, search_reg_id, search_ts)
    search_query.save()
    return search_query


def build_search_results(search_reg_id: int, query: SearchRequest) -> SearchResult:
    """Built the historical search results from the search query results."""
    search_result: SearchResult = create_from_search_query(query, search_reg_id)
    if query.total_results_size > 0:
        detail_response = {
            'searchDateTime': model_utils.format_ts(query.search_ts),
            'exactResultsSize': query.total_results_size,
            'similarResultsSize': 0,
            'totalResultsSize': query.total_results_size,
            'searchQuery': query.search_criteria,
            'details': []
        }
        search_result.search_select = search_result.set_search_selection(query.search_response)
        new_results = update_details(search_result)
        detail_response['similarResultsSize'] = search_result.similar_match_count
        detail_response['totalResultsSize'] = (search_result.exact_match_count + search_result.similar_match_count)
        detail_response['details'] = new_results
        search_result.search_response = detail_response
    return search_result


def create_from_search_query(search_query: SearchRequest, search_reg_id: int) -> SearchResult:
    """Create a search detail object from the initial search query with no search selection criteria."""
    if search_query.total_results_size == 0:  # A search query with no results: build minimal details.
        current_app.logger.debug('Building nil results')
        search_result: SearchResult = SearchResult.create_from_search_query_no_results(search_query)
        search_result.search = search_query
        return search_result

    search_result = SearchResult(search_id=search_query.id, exact_match_count=0, similar_match_count=0)
    search_result.search = search_query
    query_results = search_query.search_response
    detail_results = []
    # search_result.search_response = detail_results
    for result in query_results:
        reg_num = result['baseRegistrationNumber']
        match_type = result['matchType']
        found = False
        if detail_results:  # Check for duplicates.
            for statement in detail_results:
                if statement['financingStatement']['baseRegistrationNumber'] == reg_num:
                    found = True
        if not found:  # No duplicates.
            # Set to staff for small performance gain: skip account id/historical checks.
            current_app.logger.debug(f'fetching registration for {reg_num}')
            financing = FinancingStatement.find_by_registration_number(reg_num, None, True, False)
            financing.mark_update_json = True  # Added for PDF, indicate if party or collateral was added.
            # Set to true to include change history.
            financing.include_changes_json = True
            financing_json = {
                'matchType': match_type,
                'financingStatement': get_historical_json(financing, search_reg_id, search_query.search_ts)
            }
            detail_results.append(financing_json)
            if match_type == model_utils.SEARCH_MATCH_EXACT:
                search_result.exact_match_count += 1
            else:
                search_result.similar_match_count += 1

    search_result.search_response = detail_results
    return search_result


def get_historical_json(fin: FinancingStatement, search_reg_id: int, search_ts) -> dict:
    """Get the reistration JSON with change history at a point in time."""
    statement = {
        'statusType': fin.state_type
    }
    if fin.state_type == model_utils.STATE_DISCHARGED:
        index = len(fin.registration) - 1
        if fin.registration[index].id > search_reg_id:
            statement['statusType'] = model_utils.STATE_ACTIVE
        else:
            statement['dischargedDateTime'] = model_utils.format_ts(fin.registration[index].registration_ts)
    elif fin.state_type == model_utils.STATE_ACTIVE and fin.expire_date and \
            fin.expire_date.timestamp() < search_ts.timestamp():
        statement['statusType'] = model_utils.STATE_EXPIRED
    set_reg_json(fin, statement)
    registration_id = fin.registration[0].id
    statement['registeringParty'] = party_json(fin, Party.PartyTypes.REGISTERING_PARTY.value, registration_id,
                                               search_reg_id)
    statement['securedParties'] = party_json(fin, Party.PartyTypes.SECURED_PARTY.value, registration_id, search_reg_id)
    statement['debtors'] = party_json(fin, Party.PartyTypes.DEBTOR_COMPANY.value, registration_id, search_reg_id)

    general_collateral = general_collateral_json(fin, registration_id, search_reg_id)
    if general_collateral:
        statement['generalCollateral'] = general_collateral

    vehicle_collateral = vehicle_collateral_json(fin, registration_id, search_reg_id)
    if vehicle_collateral:
        statement['vehicleCollateral'] = vehicle_collateral
    if fin.trust_indenture:
        for trust in fin.trust_indenture:
            if not trust.registration_id_end:
                if trust.trust_indenture == 'Y':
                    statement['trustIndenture'] = True
                else:
                    statement['trustIndenture'] = False
    else:
        statement['trustIndenture'] = False
    set_court_order_json(fin, statement, search_reg_id)
    set_transition_json(fin, statement)
    return set_changes_json(fin, statement, search_reg_id)


def set_reg_json(fin: FinancingStatement, statement):
    """Set the JSON base registration information."""
    reg = fin.registration[0]
    statement['type'] = reg.registration_type
    statement['baseRegistrationNumber'] = reg.registration_num
    if reg.registration_type:
        statement['registrationDescription'] = reg.reg_type.registration_desc
        statement['registrationAct'] = reg.reg_type.registration_act
        if reg.registration_type == model_utils.REG_TYPE_OTHER and fin.crown_charge_other:
            statement['otherTypeDescription'] = fin.crown_charge_other
            statement['registrationDescription'] = \
                f'CROWN CHARGE - OTHER - FILED PURSUANT TO {fin.crown_charge_other.upper()}'
    statement['createDateTime'] = model_utils.format_ts(reg.registration_ts)
    if reg.client_reference_id:
        statement['clientReferenceId'] = reg.client_reference_id
    if reg.registration_type == model_utils.REG_TYPE_REPAIRER_LIEN:
        if reg.lien_value:
            statement['lienAmount'] = reg.lien_value
        if reg.surrender_date:
            statement['surrenderDate'] = model_utils.format_ts(reg.surrender_date)
    if fin.life and fin.life == model_utils.LIFE_INFINITE:
        statement['lifeInfinite'] = True
    elif fin.life:
        statement['lifeYears'] = fin.life
    if fin.expire_date:
        statement['expiryDate'] = model_utils.format_ts(fin.expire_date)


def set_court_order_json(fin: FinancingStatement, statement, search_reg_id: int):
    """Add court order info to the statement json if generating the current view and court order info exists."""
    for registration in fin.registration:
        if registration.court_order and registration.id <= search_reg_id:
            statement['courtOrderInformation'] = registration.court_order.json


def set_changes_json(fin: FinancingStatement, statement, search_reg_id: int):
    """Add history of changes in reverse chronological order to financing statement json."""
    if len(fin.registration) > 1:
        changes = []
        for reg in reversed(fin.registration):
            if reg.registration_type_cl not in ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN') and reg.id <= search_reg_id:
                statement_json = reg.json
                statement_json['statementType'] = \
                    model_utils.REG_CLASS_TO_STATEMENT_TYPE[reg.registration_type_cl]
                changes.append(statement_json)
        if changes:
            statement['changes'] = changes
    return statement


def set_transition_json(fin: FinancingStatement, statement):
    """Add financing statement transition json if a previous financing statement exists."""
    if fin.previous_statement and fin.previous_statement[0].registration_type:
        previous_json = fin.previous_statement[0].json
        statement['transitionDescription'] = previous_json.get('transitionDescription')
        if previous_json.get('transitionDate'):
            statement['transitionDate'] = previous_json.get('transitionDate')
        if previous_json.get('transitionNumber'):
            statement['transitionNumber'] = previous_json.get('transitionNumber')
    return statement


def vehicle_collateral_json(fin: FinancingStatement, registration_id: int, search_reg_id: int) -> dict:
    """Build vehicle collateral JSON: current_view_json determines if current or original data is included."""
    if not fin.vehicle_collateral:
        return None
    collateral_list = []
    for collateral in fin.vehicle_collateral:
        collateral_json = None
        if collateral.registration_id == registration_id and \
                (not collateral.registration_id_end or collateral.registration_id_end <= search_reg_id):
            collateral_json = collateral.json
        elif collateral.registration_id_end and collateral.registation_id_end <= search_reg_id:
            collateral_json = collateral.json
            collateral_json['added'] = True
        elif not collateral.registration_id_end and collateral.registration_id <= search_reg_id:
            collateral_json = collateral.json
            collateral_json['added'] = True
        if collateral_json:
            collateral_list.append(collateral_json)
    return collateral_list


def party_json(fin: FinancingStatement, party_type: str, registration_id: int, search_reg_id: int) -> dict:
    """Build party JSON: current_view_json determines if current or original data is included."""
    if party_type == Party.PartyTypes.REGISTERING_PARTY.value:
        for party in fin.parties:
            if party.party_type == party_type and registration_id == party.registration_id:
                return party.json
        # No registering party record: legacy data.
        return {}

    parties = []
    for party in fin.parties:
        p_json = None
        if party.party_type == party_type or \
                (party_type == Party.PartyTypes.DEBTOR_COMPANY.value and
                 party.party_type == Party.PartyTypes.DEBTOR_INDIVIDUAL.value):
            if party.registration_id_end and party.registration_id_end <= search_reg_id:
                p_json = party.json
                if party.registration_id != registration_id:
                    p_json['added'] = True
            elif not party.registration_id_end and party.registration_id <= search_reg_id:
                p_json = party.json
                if party.registration_id != registration_id:
                    p_json['added'] = True
        if p_json:
            parties.append(p_json)
    return parties


def general_collateral_json(fin: FinancingStatement, registration_id: int, search_reg_id: int) -> dict:
    """Build general collateral JSON: current_view_json determines if current or original data is included."""
    if not fin.general_collateral and not fin.general_collateral_legacy:
        return None
    collateral_json = []
    collateral_json = __build_general_collateral_json(fin, registration_id, collateral_json, False, search_reg_id)
    collateral_json = __build_general_collateral_json(fin, registration_id, collateral_json, True, search_reg_id)
    return collateral_json


def __build_general_collateral_json(fin: FinancingStatement,
                                    registration_id: int,
                                    collateral_json: dict,
                                    legacy: bool,
                                    search_reg_id: int) -> dict:
    """Build general collateral JSON for a financing statement from either the API or legacy table."""
    collateral_list = None
    if (not legacy and not fin.general_collateral) or (legacy and not fin.general_collateral_legacy):
        return collateral_json
    if not legacy:
        collateral_list = reversed(fin.general_collateral)
    else:
        collateral_list = reversed(fin.general_collateral_legacy)

    for collateral in collateral_list:  # pylint: disable=too-many-nested-blocks
        if collateral.registration_id == registration_id or not collateral.status:
            gc_json = collateral.json
            collateral_json.append(gc_json)
        # Add only solution for legacy records: current view shows all records including deleted.
        elif collateral.registration_id <= search_reg_id:
            gc_json = collateral.current_json
            exists = False
            # If amendment/change registration is 1 add, 1 remove then combine them.
            if __is_edit_general_collateral(fin, collateral.registration_id, legacy):
                for exists_collateral in collateral_json:
                    if exists_collateral['addedDateTime'] == gc_json['addedDateTime']:
                        if 'descriptionAdd' in exists_collateral and \
                                'descriptionDelete' not in exists_collateral and \
                                    'descriptionDelete' in gc_json:
                            exists = True
                            exists_collateral['descriptionDelete'] = gc_json['descriptionDelete']
                        elif 'descriptionDelete' in exists_collateral and \
                                'descriptionAdd' not in exists_collateral and \
                                    'descriptionAdd' in gc_json:
                            exists = True
                            exists_collateral['descriptionAdd'] = gc_json['descriptionAdd']
            if not exists:
                collateral_json.append(gc_json)
    return collateral_json


def __is_edit_general_collateral(fin: FinancingStatement, registration_id: int, legacy: bool):
    """True if an amendment adds 1 gc and removes 1 gc."""
    add_count = 0
    delete_count = 0
    collateral_list = fin.general_collateral if not legacy else fin.general_collateral_legacy
    for collateral in collateral_list:
        if collateral.registration_id == registration_id and collateral.status:
            if collateral.status == GeneralCollateralLegacy.StatusTypes.ADDED:
                add_count += 1
            elif collateral.status == GeneralCollateralLegacy.StatusTypes.DELETED:
                delete_count += 1
    return add_count == 1 and delete_count == 1


def update_details(search_result: SearchResult) -> dict:
    """Generate the search selection details from the search selection order without duplicates."""
    results = search_result.search_response
    new_results = []
    similar_count = 0
    # Use the same order as the search selection match list in the registration list.
    for select in search_result.search_select:
        if select['matchType'] == model_utils.SEARCH_MATCH_EXACT or \
                ('selected' not in select or select['selected']):
            if select['matchType'] != model_utils.SEARCH_MATCH_EXACT:
                similar_count += 1
            reg_num = select['baseRegistrationNumber']
            found = False
            if new_results:  # Check for duplicates.
                for match in new_results:
                    if match['financingStatement']['baseRegistrationNumber'] == reg_num:
                        found = True
            if not found:  # No duplicates.
                for result in results:
                    if reg_num == result['financingStatement']['baseRegistrationNumber']:
                        new_results.append(result)
                        break
    search_result.similar_match_count = similar_count
    return new_results
