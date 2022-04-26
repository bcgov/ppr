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
from http import HTTPStatus

# import requests
from flask import Blueprint, current_app, jsonify, request
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils

from mhr_api.exceptions import BusinessException, DatabaseException
# from mhr_api.services.queue_service import GoogleQueueService
from mhr_api.models import SearchRequest, SearchResult  # , utils as model_utils,EventTracking
from mhr_api.resources import utils as resource_utils
from mhr_api.services.authz import authorized
from mhr_api.utils.auth import jwt


# from mhr_api.reports import ReportTypes, get_pdf
# from mhr_api.callback.reports.report_service import get_search_report
# from mhr_api.callback.utils.exceptions import ReportException, ReportDataException, StorageException
# from mhr_api.callback.document_storage.storage_service import GoogleStorageService


bp = Blueprint('SEARCH_RESULTS1', __name__, url_prefix='/api/v1/search-results')  # pylint: disable=invalid-name

VAL_ERROR = 'Search details request data validation errors.'  # Validation error prefix
GET_DETAILS_ERROR = 'Submit a search step 2 select results request before getting search result details.'
SEARCH_RESULTS_DOC_NAME = 'search-results-report-{search_id}.pdf'
CALLBACK_MESSAGES = {
    resource_utils.CallbackExceptionCodes.UNKNOWN_ID: '01: no search result data found for id={search_id}.',
    resource_utils.CallbackExceptionCodes.MAX_RETRIES: '02: maximum retries reached for id={search_id}.',
    resource_utils.CallbackExceptionCodes.INVALID_ID: '03: search result report setup not async for id={search_id}.',
    resource_utils.CallbackExceptionCodes.DEFAULT: '04: default error for id={search_id}.',
    resource_utils.CallbackExceptionCodes.REPORT_DATA_ERR: '05: report data error for id={search_id}.',
    resource_utils.CallbackExceptionCodes.REPORT_ERR: '06: generate report failed for id={search_id}.',
    resource_utils.CallbackExceptionCodes.STORAGE_ERR: '07: document storage save failed for id={search_id}.',
    resource_utils.CallbackExceptionCodes.NOTIFICATION_ERR: '08: notification failed for id={search_id}.',
}
CALLBACK_PARAM = 'callbackURL'
REPORT_URL = '/ppr/api/v1/search-results/{search_id}'
USE_CURRENT_PARAM = 'useCurrent'


@bp.route('/<string:search_id>', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def post_search_results(search_id: str):  # pylint: disable=too-many-branches, too-many-locals
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

        request_json = None
        use_current_selection = request.args.get(USE_CURRENT_PARAM)
        if use_current_selection:
            search_request = SearchRequest.find_by_id(search_id)
            request_json = search_request.updated_selection or []
        else:
            request_json = request.get_json(silent=True)
            # Validate schema.
            valid_format, errors = schema_utils.validate(request_json, 'searchSummary', 'mhr')
            if not valid_format:
                return resource_utils.validation_error_response(errors, VAL_ERROR)

        # Perform any extra data validation such as start and end dates here
        search_detail = SearchResult.validate_search_select(request_json, search_id)

        # Large report threshold check, require/save callbackURL parameter.
        # UI may not request a report in step 2.
        callback_url = request.args.get(CALLBACK_PARAM)
        is_ui_pdf = (callback_url is not None and callback_url == current_app.config.get('UI_SEARCH_CALLBACK_URL'))
        if is_async(search_detail, request_json) and (resource_utils.is_pdf(request) or is_ui_pdf):
            if callback_url is None:
                error = f'Large search report required callbackURL parameter missing for {search_id}.'
                current_app.logger.warn(error)
                return resource_utils.error_response(HTTPStatus.BAD_REQUEST, error)
        else:
            callback_url = None
            is_ui_pdf = False
        # Save the search query selection and details that match the selection.
        account_name = resource_utils.get_account_name(jwt.get_token_auth_header(), account_id)
        search_detail.update_selection(request_json, account_name, callback_url)
        if not search_detail.search_response:
            return resource_utils.unprocessable_error_response('search result details')

        response_data = search_detail.json
        # Results data that is too large for real time report generation (small number of results) is also
        # asynchronous.
        if callback_url is None and search_detail.callback_url is not None:
            callback_url = search_detail.callback_url
            is_ui_pdf = True
        # if resource_utils.is_pdf(request) or is_ui_pdf:
            # If results over threshold return JSON with callbackURL, getReportURL
            # if callback_url is not None:
            #    # Add enqueue report generation event here.
            #    enqueue_search_report(search_id)
            #    response_data['callbackURL'] = requests.utils.unquote(callback_url)
            #    response_data['getReportURL'] = REPORT_URL.format(search_id=search_id)
            #    return jsonify(response_data), HTTPStatus.OK

            # Return report if request header Accept MIME type is application/pdf.
            # return get_pdf(response_data, account_id, ReportTypes.SEARCH_DETAIL_REPORT.value,
            #                jwt.get_token_auth_header())

        return jsonify(response_data), HTTPStatus.OK

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, 'POST search select id=' + search_id)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('/<string:search_id>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_search_results(search_id: str):
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

        # If no search selection (step 2) return an error. Could be results
        # with no exact matches and no results selected - nil, which is valid.
        if search_detail.search_select is None and search_detail.search.total_results_size > 0:
            return resource_utils.bad_request_response(GET_DETAILS_ERROR)

        # If the request is for an async large report, fetch binary data from doc storage.
        # if resource_utils.is_pdf(request) and search_detail.callback_url is not None:
        #    if search_detail.doc_storage_url is None:
        #        error_msg = f'Search report not yet available for {search_id}.'
        #        current_app.logger.info(error_msg)
        #        return resource_utils.bad_request_response(error_msg)
        #    doc_name = search_detail.doc_storage_url if not search_detail.doc_storage_url.startswith('http') \
        #        else SEARCH_RESULTS_DOC_NAME.format(search_id=search_id)
        #    current_app.logger.info(f'Fetching large search report {doc_name} from doc storage.')
        #    raw_data = GoogleStorageService.get_document(doc_name)
        #    return raw_data, HTTPStatus.OK, {'Content-Type': 'application/pdf'}

        response_data = search_detail.json
        # if resource_utils.is_pdf(request):
        #   # Return report if request header Accept MIME type is application/pdf.
        #    return get_pdf(response_data, account_id, ReportTypes.SEARCH_DETAIL_REPORT.value,
        #                    jwt.get_token_auth_header())

        return jsonify(response_data), HTTPStatus.OK

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, 'GET search details id=' + search_id)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


def is_async(search_detail: SearchResult, search_select) -> bool:
    """Check if the request number of registrations exceeds the real time threshold."""
    threshold: int = current_app.config.get('SEARCH_PDF_ASYNC_THRESHOLD', 75)
    if search_detail.search.total_results_size < threshold:
        return False
    if len(search_select) > threshold:
        return True
    return False
