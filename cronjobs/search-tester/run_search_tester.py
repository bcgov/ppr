# Copyright © 2020 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This module holds all of the basic data about the auto analyzer uat testing."""
import csv
import os
from datetime import datetime
from typing import List

from flask import Flask

from ppr_api.models import db, SearchRequest, TestSearch, TestSearchBatch, TestSearchResult

from search_tester import create_app
from search_tester.utils.helpers import TO_API_SEARCH_TYPE
from search_tester.utils.logging import setup_logging


setup_logging(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'logging.conf'))


def add_legacy_results(search: TestSearch, result_list: List[dict], match_type: TestSearchResult.MatchType):
    """Add the given legacy results for the match type to the TestSearch obj."""
    for legacy_result, index in zip(result_list, range(len(result_list))):
        result = TestSearchResult()
        result.doc_id = legacy_result['doc_id']
        result.details = legacy_result['result']
        result.match_type = match_type.value
        result.source = TestSearchResult.Source.LEGACY.value
        result.index = index
        search.results.append(result)

def add_api_results(search: TestSearch, results: List[dict]):
    """Add the given api results to the TestSearch obj."""
    exact_index = 0
    similar_index = 0
    for api_result in results:
        result = TestSearchResult()
        result.doc_id = api_result['baseRegistrationNumber']
        result.source = TestSearchResult.Source.API.value
        if TestSearchResult.MatchType[api_result['matchType']] == TestSearchResult.MatchType.EXACT:
            result.match_type = TestSearchResult.MatchType.EXACT.value
            result.index = exact_index
            exact_index += 1
        else:
            result.match_type = TestSearchResult.MatchType.SIMILAR.value
            result.index = similar_index
            similar_index += 1
        if search_type in [SearchRequest.SearchTypes.BUSINESS_DEBTOR.value, SearchRequest.SearchTypes.INDIVIDUAL_DEBTOR.value]:
            result.details = api_result['debtor']
        elif search_type == SearchRequest.SearchTypes.REGISTRATION_NUM.value:
            result.details = api_result['baseRegistrationNumber']
        else:
            result.details = api_result['vehicleCollateral']
        search.results.append(result)

if __name__ == '__main__':
    try:
        app = create_app()
        app.logger.debug('Running search tester...')

        completed = 0
        skipped = 0

        filename = 'SEARCH_RESULTS.csv'
        batch_searches = {
            SearchRequest.SearchTypes.AIRCRAFT_AIRFRAME_DOT.value: {},
            SearchRequest.SearchTypes.BUSINESS_DEBTOR.value: {},
            SearchRequest.SearchTypes.INDIVIDUAL_DEBTOR.value: {},
            SearchRequest.SearchTypes.MANUFACTURED_HOME_NUM.value: {},
            SearchRequest.SearchTypes.REGISTRATION_NUM.value: {},
            SearchRequest.SearchTypes.SERIAL_NUM.value: {}
        }

        # read csv + prep for search tests
        with open(f'csvs/{filename}', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            # organize searches by time/criteria + split into exact/similar results
            for row in reader:
                search_type = row['SEARCH_TYPE']
                time = row['TIME']

                if time not in batch_searches[search_type]:
                    batch_searches[search_type][time] = {
                        'criteria': row['CRITERIA'],
                        'exact_matches': [],
                        'similar_matches': []
                    }

                if row['MATCH_TYPE'] == TestSearchResult.MatchType.EXACT.value:
                    batch_searches[search_type][time]['exact_matches'].append({
                        'result': row['RESULT'],
                        'doc_id': row['DOCUMENT_ID']
                    })
                else:
                    batch_searches[search_type][time]['similar_matches'].append({
                        'result': row['RESULT'],
                        'doc_id': row['DOCUMENT_ID']
                    })
        for search_type in batch_searches:
            try:
                if not batch_searches[search_type]:
                    # only do search batches for search types we got legacy data for
                    continue
                # init new batch
                batch = TestSearchBatch()
                batch.search_type = search_type
                batch.test_date = datetime.utcnow()
                batch.sim_val_business = app.config['SIM_VAL_BUSINESS']
                batch.sim_val_first_name = app.config['SIM_VAL_FIRST']
                batch.sim_val_last_name = app.config['SIM_VAL_LAST']
                batch.searches = []
                # populate searches
                for time in batch_searches[search_type]:
                    legacy_search = batch_searches[search_type][time]
                    search = TestSearch()
                    search.search_criteria = legacy_search['criteria']
                    search.results = []
                    # add legacy results exact
                    add_legacy_results(search, legacy_search['exact_matches'], TestSearchResult.MatchType.EXACT)
                    # add legacy results similar
                    add_legacy_results(search, legacy_search['similar_matches'], TestSearchResult.MatchType.SIMILAR)
                
                    ### get ppr-api search results
                    # prep search
                    criteria = { 'value': legacy_search['criteria'] }
                    if search_type == SearchRequest.SearchTypes.INDIVIDUAL_DEBTOR.value:
                        name = legacy_search['criteria'].split(' ')
                        criteria = { 'debtorName': { 'first': name[1], 'last': name[0] }}
                        if len(name) > 2:
                            criteria['debtorName']['second'] = name[2]
                    elif search_type == SearchRequest.SearchTypes.BUSINESS_DEBTOR.value:
                        criteria = { 'debtorName': { 'business': legacy_search['criteria'] }}

                    request_json = { 'criteria': criteria, 'type': TO_API_SEARCH_TYPE[search_type] }
                    query = SearchRequest.create_from_json(request_json, '0', 'search-tester')
                    # run search on api fn
                    start = datetime.utcnow()
                    query.search()
                    end  = datetime.utcnow()
                    interval = end - start
                    search.run_time = interval.total_seconds()
                    # save results
                    results = query.search_response or []
                    add_api_results(search, results)
                    # add search to batch
                    batch.searches.append(search)
                # save batch to db
                batch.save()
                completed += 1
                
            except Exception as err:
                app.logger.error(err.with_traceback(None))
                app.logger.debug('Error occurred, rolling back db...')
                db.session.rollback()
                app.logger.debug(f'Rollback successful. Skipping batch for {search_type}')
                skipped += 1

        app.logger.debug(f'Job completed.')
        app.logger.debug(f'Completed {completed} batches.')
        app.logger.debug(f'Skipped {skipped} batches.')

    except Exception as err:
        app.logger.error(err.with_traceback(None))
