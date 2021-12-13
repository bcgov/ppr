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
"""API endpoints for executing PPR search detail requests (search step 2)."""

# pylint: disable=too-many-return-statements
import json
from http import HTTPStatus

from flask import request, current_app, jsonify
from flask_restx import Namespace, Resource, cors
from registry_schemas import utils as schema_utils

from ppr_api.utils.auth import jwt
from ppr_api.utils.util import cors_preflight
from ppr_api.exceptions import BusinessException
from ppr_api.services.authz import authorized
from ppr_api.models import EventTracking, SearchResult, utils as model_utils
from ppr_api.resources import utils as resource_utils
from ppr_api.reports import ReportTypes, get_pdf
from ppr_api.callback.reports.report_service import get_search_report
from ppr_api.callback.utils.exceptions import ReportException, ReportDataException, StorageException
from ppr_api.callback.document_storage.storage_service import GoogleStorageService


API = Namespace('search-results', description='Endpoints for PPR search details (Search step 2).')
VAL_ERROR = 'Search details request data validation errors.'  # Validation error prefix
SEARCH_RESULTS_DOC_NAME = 'search-results-report-{search_id}.pdf'
CALLBACK_MESSAGES = {
    resource_utils.CallbackExceptionCodes.UNKNOWN_ID: '01: no search result data found for id={search_id}.',
    resource_utils.CallbackExceptionCodes.MAX_RETRIES: '02: maximum retries reached for id={search_id}.',
    resource_utils.CallbackExceptionCodes.INVALID_ID: '03: search result report setup not async for id={search_id}.',
    resource_utils.CallbackExceptionCodes.DEFAULT: '04: default error for id={search_id}.',
    resource_utils.CallbackExceptionCodes.REPORT_DATA_ERR: '05: report data error for id={search_id}.',
    resource_utils.CallbackExceptionCodes.REPORT_ERR: '06: generate report failed for id={search_id}.',
    resource_utils.CallbackExceptionCodes.STORAGE_ERR: '07: document storage save failed for id={search_id}.'
}
CALLBACK_PARAM = 'callbackURL'
REPORT_URL = '/ppr/api/v1/search-results/{search_id}'


@cors_preflight('GET,POST,OPTIONS')
@API.route('/<path:search_id>', methods=['GET', 'POST', 'OPTIONS'])
class SearchResultsResource(Resource):
    """Resource for submitting PPR search detail (second step) requests."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def post(search_id):
        """Execute a search detail request using selection choices in the request body."""
        try:
            if search_id is None:
                return resource_utils.path_param_error_response('search ID')

            # Quick check: must provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate schema.
            valid_format, errors = schema_utils.validate(request_json, 'searchSummary', 'ppr')
            if not valid_format:
                return resource_utils.validation_error_response(errors, VAL_ERROR)

            # Perform any extra data validation such as start and end dates here
            search_detail = SearchResult.validate_search_select(request_json, search_id)

            # Large report threshold check, require/save callbackURL parameter.
            callback_url = None
            if resource_utils.is_pdf(request) and is_async(search_detail, request_json):
                callback_url = request.args.get(CALLBACK_PARAM)
                if callback_url is None:
                    error = f'Large search report required callbackURL parameter missing for {search_id}.'
                    current_app.logger.warn(error)
                    return resource_utils.error_response(HTTPStatus.BAD_REQUEST, error)

            # Save the search query selection and details that match the selection.
            account_name = resource_utils.get_account_name(jwt.get_token_auth_header(), account_id)
            search_detail.update_selection(request_json, account_name, callback_url)
            if not search_detail.search_response:
                return resource_utils.unprocessable_error_response('search result details')

            response_data = search_detail.json
            if resource_utils.is_pdf(request):
                # If results over threshold return JSON with callbackURL, getReportURL
                if callback_url is not None:
                    # Add enqueue report generation event here.
                    response_data['callbackURL'] = callback_url
                    response_data['getReportURL'] = REPORT_URL.format(search_id=search_id)
                    return jsonify(response_data), HTTPStatus.OK

                # Return report if request header Accept MIME type is application/pdf.
                return get_pdf(response_data, account_id, ReportTypes.SEARCH_DETAIL_REPORT.value,
                               jwt.get_token_auth_header())

            return jsonify(response_data), HTTPStatus.OK

        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def get(search_id):
        """Get search detail information for a previous search."""
        try:
            if search_id is None:
                return resource_utils.path_param_error_response('search ID')

            # Quick check: must have an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)

            # Try to fetch search detail by search id.
            current_app.logger.info(f'Fetching search detail for {search_id}.')
            search_detail = SearchResult.find_by_search_id(search_id, True)
            if not search_detail:
                return resource_utils.not_found_error_response('searchId', search_id)

            # If the request is for an async large report, fetch binary data from doc storage.
            if resource_utils.is_pdf(request) and search_detail.callback_url is not None:
                if search_detail.doc_storage_url is None:
                    error = f'Search report not yet available for {search_id}.'
                    current_app.logger.info(error)
                    return resource_utils.error_response(HTTPStatus.NOT_FOUND, error)
                doc_name = SEARCH_RESULTS_DOC_NAME.format(search_id=search_id)
                current_app.logger.info(f'Fetching large search report {doc_name} from doc storage.')
                raw_data = GoogleStorageService.get_document(doc_name)
                return raw_data, HTTPStatus.OK

            response_data = search_detail.json
            if resource_utils.is_pdf(request):
                # Return report if request header Accept MIME type is application/pdf.
                return get_pdf(response_data, account_id, ReportTypes.SEARCH_DETAIL_REPORT.value,
                               jwt.get_token_auth_header())

            return jsonify(response_data), HTTPStatus.OK

        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('PATCH,OPTIONS')
@API.route('/callback/<path:search_id>', methods=['PATCH', 'OPTIONS'])
class PatchSearchResultsResource(Resource):
    """Resource to generates a large search result report for a queue callback ."""

    @staticmethod
    @cors.crossdomain(origin='*')
    def patch(search_id):  # pylint: disable=too-many-branches
        """Generate and store a report, update search_result.doc_storage_url."""
        try:
            if search_id is None:
                return resource_utils.path_param_error_response('search ID')

            # If exceeded max retries we're done.
            event_count: int = 0
            events = EventTracking.find_by_key_id_type(search_id, EventTracking.EventTrackingTypes.SEARCH_REPORT)
            if events:
                event_count = len(events)
            if event_count > current_app.config.get('EVENT_MAX_RETRIES'):
                return callback_error(resource_utils.CallbackExceptionCodes.MAX_RETRIES, search_id,
                                      HTTPStatus.INTERNAL_SERVER_ERROR)

            search_detail = SearchResult.find_by_search_id(search_id, False)
            if not search_detail:
                return callback_error(resource_utils.CallbackExceptionCodes.UNKNOWN_ID, search_id, HTTPStatus.NOT_FOUND)

            # Check if report already generated.
            if search_detail.doc_storage_url is not None:
                doc_ref = search_detail.doc_storage_url
                current_app.logger.warn(f'Search detail report for {search_id} already exists: {doc_ref}.')
                return {}, HTTPStatus.OK

            # Check if search result is async: always have callback_url.
            if search_detail.callback_url is None:
                return callback_error(resource_utils.CallbackExceptionCodes.INVALID_ID,
                                      search_id,
                                      HTTPStatus.BAD_REQUEST)

            # Generate the report with an API call
            current_app.logger.info(f'Generating search detail report for {search_id}.')
            raw_data, status_code, headers = get_search_report(search_id)
            if not raw_data or not status_code:
                return callback_error(resource_utils.CallbackExceptionCodes.REPORT_DATA_ERR,
                                      search_id,
                                      HTTPStatus.INTERNAL_SERVER_ERROR,
                                      'No data or status code.')
            current_app.logger.debug('report api call status=' + str(status_code) + ' headers=' + json.dumps(headers))
            if status_code not in (HTTPStatus.OK, HTTPStatus.CREATED):
                message = f'Status code={status_code}. Response: ' + json.dumps(raw_data)
                return callback_error(resource_utils.CallbackExceptionCodes.REPORT_ERR,
                                      search_id,
                                      HTTPStatus.INTERNAL_SERVER_ERROR,
                                      message)

            doc_name = SEARCH_RESULTS_DOC_NAME.format(search_id=search_id)
            current_app.logger.info(f'Saving report output to doc storage: name={doc_name}.')
            response = GoogleStorageService.save_document(doc_name, raw_data)
            current_app.logger.info('Save document storage response: ' + json.dumps(response))
            if response and 'selfLink' in response:
                search_detail.doc_storage_url = response['selfLink']
            else:
                search_detail.doc_storage_url = doc_name
            search_detail.save()

            # Track success event.
            EventTracking.create(search_id, EventTracking.EventTrackingTypes.SEARCH_REPORT, int(HTTPStatus.OK))

            # Enqueue notication event if not from UI.
            if search_detail.is_ui_callback():
                current_app.logger.info(f'Skipping report available notification for UI id={search_id}.')
            else:  # Enqueue notification event.
                current_app.logger.info(f'Queueing report notification for id={search_id}, callback=' +
                                        search_detail.callback_url)

            return response, HTTPStatus.OK

        except ReportException as report_err:
            return callback_error(resource_utils.CallbackExceptionCodes.REPORT_ERR,
                                  search_id,
                                  HTTPStatus.INTERNAL_SERVER_ERROR,
                                  repr(report_err))
        except ReportDataException as report_data_err:
            return callback_error(resource_utils.CallbackExceptionCodes.REPORT_DATA_ERR,
                                  search_id,
                                  HTTPStatus.INTERNAL_SERVER_ERROR,
                                  repr(report_data_err))
        except StorageException as storage_err:
            return callback_error(resource_utils.CallbackExceptionCodes.STORAGE_ERR,
                                  search_id,
                                  HTTPStatus.INTERNAL_SERVER_ERROR,
                                  repr(storage_err))
        except Exception as default_err:  # noqa: B902; return nicer default error
            return callback_error(resource_utils.CallbackExceptionCodes.DEFAULT,
                                  search_id,
                                  HTTPStatus.INTERNAL_SERVER_ERROR,
                                  repr(default_err))


def callback_error(code: str, search_id: str, status_code, message: str = None):
    """Return a callback error response based on the code."""
    error = CALLBACK_MESSAGES[code].format(search_id=search_id)
    if message:
        error += ' ' + message
    current_app.logger.error(error)
    # Track event here.
    EventTracking.create(search_id, EventTracking.EventTrackingTypes.SEARCH_REPORT, status_code, message)
    return resource_utils.error_response(status_code, error)


def is_async(search_detail: SearchResult, search_select):
    """Check if the request number of financing statements exceeds the real time threshold."""
    threshold = current_app.config.get('SEARCH_PDF_ASYNC_THRESHOLD')
    if search_detail.search.total_results_size < threshold:
        return False
    if search_detail.exact_match_count > threshold:
        return True
    exact_count = 0
    similar_count = 0
    for result in search_detail.search_response:
        # Always include exact matches.
        if result['matchType'] == model_utils.SEARCH_MATCH_EXACT:
            exact_count += 1
        else:
            reg_num = result['financingStatement']['baseRegistrationNumber']
            for select in search_select:
                # Verified: have to explicitly select a similar result to include.
                if select['baseRegistrationNumber'] == reg_num and \
                        ('selected' not in select or select['selected']):
                    similar_count += 1
    if (similar_count + exact_count) > threshold:
        return True

    return False
