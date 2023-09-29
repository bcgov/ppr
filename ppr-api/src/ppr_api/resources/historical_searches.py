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
"""API endpoints for executing PPR  historical searches."""
# pylint: disable=too-many-return-statements
import json
from http import HTTPStatus

from flask import current_app, jsonify, request
from flask_restx import Namespace, Resource, cors
from registry_schemas import utils as schema_utils

from ppr_api.exceptions import BusinessException, DatabaseException
from ppr_api.models import SearchRequest, SearchResult, search_historical, utils as model_utils
from ppr_api.resources import utils as resource_utils
from ppr_api.services.authz import is_staff
from ppr_api.reports import ReportTypes, get_callback_pdf
from ppr_api.callback.document_storage.storage_service import GoogleStorageService, DocumentTypes
from ppr_api.callback.utils.exceptions import StorageException
from ppr_api.utils.auth import jwt
from ppr_api.utils.util import cors_preflight


API = Namespace('historical-searches', description='Endpoint for PPR historical searches.')
VAL_ERROR = 'Search request data validation errors.'  # Validation error prefix
VAL_ERROR_SEARCH_TS = 'Search request data validation errors: searchDateTime required.'
STORAGE_LINK_LIFE: int = 7


@cors_preflight('POST,OPTIONS')
@API.route('', methods=['POST', 'OPTIONS'])
class HistoricalSearchResource(Resource):
    """Resource for executing PPR searches."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def post():  # pylint: disable=too-many-branches,too-many-locals
        """Execute a new historical search request using criteria in the request body."""
        try:
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()
            # Verify request JWT staff only
            if not is_staff(jwt):
                return resource_utils.unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate request against the schema.
            valid_format, errors = schema_utils.validate(request_json, 'searchQuery', 'ppr')
            if not valid_format:
                return resource_utils.validation_error_response(errors, VAL_ERROR)
            if not request_json.get('searchDateTime'):
                current_app.logger.error('searchDateTime required for historical searches')
                return resource_utils.bad_request_response(VAL_ERROR_SEARCH_TS)
            # Perform any extra data validation such as start and end dates here
            SearchRequest.validate_query(request_json)
            search_ts: str = request_json.get('searchDateTime')
            current_app.logger.debug(f'Historical search ts={search_ts}')
            max_reg_id: int = search_historical.get_search_historical_id(search_ts)
            current_app.logger.debug(f'Historical search max registration id={max_reg_id}')
            # Execute the search query: treat no results as a success.
            query: SearchRequest = search_historical.search(request_json, max_reg_id)
            current_app.logger.debug('Executed search query, building detail results')
            result: SearchResult = search_historical.build_search_results(max_reg_id, query)
            if request_json.get('accountName'):
                result.account_name = request_json.get('accountName')
            results_data = result.json
            current_app.logger.debug('Generating report with detail results')
            rep_data, status_code, headers = get_callback_pdf(results_data,
                                                              'HIST_SEARCH',
                                                              ReportTypes.SEARCH_DETAIL_REPORT.value,
                                                              jwt.get_token_auth_header(),
                                                              result.account_name)
            current_app.logger.debug(f'report api call status={status_code}, headers=' + json.dumps(headers))
            current_app.logger.debug('Saving report to doc storage and generating a link.')
            doc_name = model_utils.get_search_doc_storage_name(result.search)
            doc_name = doc_name.replace('search', 'historical-search')
            rep_url = GoogleStorageService.save_document_link(doc_name,
                                                              rep_data,
                                                              DocumentTypes.SEARCH_RESULTS,
                                                              STORAGE_LINK_LIFE)
            current_app.logger.info(f'Saved {doc_name} document storage link: {rep_url}')
            result.doc_storage_url = doc_name
            result.save()
            update_response_data(results_data, rep_url)
            return jsonify(results_data), HTTPStatus.CREATED, {'Content-Type': 'application/json'}
        except StorageException as storage_err:
            return resource_utils.error_response(HTTPStatus.INTERNAL_SERVER_ERROR,
                                                 'Unable to save report to doc storage: ' + str(storage_err))
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, 'HIST_SEARCH', 'POST historical search')
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


def update_response_data(results_data: dict, rep_url: str) -> dict:
    """Remove temporarily added report generation properties and set the report url."""
    results_data['reportUrl'] = rep_url
    if results_data.get('environment'):
        del results_data['environment']
    if results_data.get('footer_content'):
        del results_data['footer_content']
    if results_data.get('meta_account_id'):
        del results_data['meta_account_id']
    if results_data.get('meta_account_name'):
        del results_data['meta_account_name']
    if results_data.get('meta_subject'):
        del results_data['meta_subject']
    if results_data.get('meta_subtitle'):
        del results_data['meta_subtitle']
    if results_data.get('meta_title'):
        del results_data['meta_title']
    if results_data.get('search_large'):
        del results_data['search_large']
