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

import requests
from flask import request, current_app, jsonify
from flask_restx import Namespace, Resource, cors
from registry_schemas import utils as schema_utils

from ppr_api.utils.auth import jwt
from ppr_api.utils.util import cors_preflight
from ppr_api.exceptions import BusinessException, DatabaseException
from ppr_api.services.authz import authorized
from ppr_api.services.queue_service import GoogleQueueService
from ppr_api.models import EventTracking, SearchResult, SearchRequest, utils as model_utils
from ppr_api.resources import utils as resource_utils
from ppr_api.reports import ReportTypes, get_pdf
from ppr_api.callback.reports.report_service import get_search_report
from ppr_api.callback.utils.exceptions import ReportException, ReportDataException, StorageException
from ppr_api.callback.document_storage.storage_service import GoogleStorageService


API = Namespace('search-results', description='Endpoints for PPR search details (Search step 2).')
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


@cors_preflight('GET,POST,OPTIONS')
@API.route('/<path:search_id>', methods=['GET', 'POST', 'OPTIONS'])
class SearchResultsResource(Resource):
    """Resource for submitting PPR search detail (second step) requests."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def post(search_id):  # pylint: disable=too-many-branches, too-many-locals
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
                valid_format, errors = schema_utils.validate(request_json, 'searchSummary', 'ppr')
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
            if resource_utils.is_pdf(request) or is_ui_pdf:
                # If results over threshold return JSON with callbackURL, getReportURL
                if callback_url is not None:
                    # Add enqueue report generation event here.
                    enqueue_search_report(search_id)
                    response_data['callbackURL'] = requests.utils.unquote(callback_url)
                    response_data['getReportURL'] = REPORT_URL.format(search_id=search_id)
                    return jsonify(response_data), HTTPStatus.OK

                # Return report if request header Accept MIME type is application/pdf.
                return get_pdf(response_data, account_id, ReportTypes.SEARCH_DETAIL_REPORT.value,
                               jwt.get_token_auth_header())

            return jsonify(response_data), HTTPStatus.OK

        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, account_id, 'POST search select id=' + search_id)
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

            # If no search selection (step 2) return an error. Could be results
            # with no exact matches and no results selected - nil, which is valid.
            if search_detail.search_select is None and search_detail.search.total_results_size > 0:
                return resource_utils.bad_request_response(GET_DETAILS_ERROR)

            # If the request is for an async large report, fetch binary data from doc storage.
            if resource_utils.is_pdf(request) and search_detail.callback_url is not None:
                if search_detail.doc_storage_url is None:
                    error_msg = f'Search report not yet available for {search_id}.'
                    current_app.logger.info(error_msg)
                    return resource_utils.bad_request_response(error_msg)
                doc_name = search_detail.doc_storage_url if not search_detail.doc_storage_url.startswith('http') \
                    else SEARCH_RESULTS_DOC_NAME.format(search_id=search_id)
                current_app.logger.info(f'Fetching large search report {doc_name} from doc storage.')
                raw_data = GoogleStorageService.get_document(doc_name)
                return raw_data, HTTPStatus.OK, {'Content-Type': 'application/pdf'}

            response_data = search_detail.json
            if resource_utils.is_pdf(request):
                # Return report if request header Accept MIME type is application/pdf.
                return get_pdf(response_data, account_id, ReportTypes.SEARCH_DETAIL_REPORT.value,
                               jwt.get_token_auth_header())

            return jsonify(response_data), HTTPStatus.OK

        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, account_id, 'GET search details id=' + search_id)
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('POST,OPTIONS')
@API.route('/callback/<path:search_id>', methods=['POST', 'OPTIONS'])
class PatchSearchResultsResource(Resource):
    """Resource to generate a large search result report for a queue callback."""

    @staticmethod
    @cors.crossdomain(origin='*')
    def post(search_id):  # pylint: disable=too-many-branches, too-many-locals
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
                                      HTTPStatus.INTERNAL_SERVER_ERROR,
                                      'Max retries reached.')

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
                message = f'Status code={status_code}. Response: ' + raw_data.get_data(as_text=True)
                return callback_error(resource_utils.CallbackExceptionCodes.REPORT_ERR,
                                      search_id,
                                      HTTPStatus.INTERNAL_SERVER_ERROR,
                                      message)

            doc_name = model_utils.get_search_doc_storage_name(search_detail.search)
            current_app.logger.info(f'Saving report output to doc storage: name={doc_name}.')
            response = GoogleStorageService.save_document(doc_name, raw_data)
            current_app.logger.info('Save document storage response: ' + json.dumps(response))
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
                enqueue_notification(search_id)

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
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, None, 'POST large report event')
        except Exception as default_err:  # noqa: B902; return nicer default error
            return callback_error(resource_utils.CallbackExceptionCodes.DEFAULT,
                                  search_id,
                                  HTTPStatus.INTERNAL_SERVER_ERROR,
                                  repr(default_err))


@cors_preflight('POST,OPTIONS')
@API.route('/notifications/<path:search_id>', methods=['POST', 'OPTIONS'])
class PostResultsNotificationResource(Resource):
    """Resource to notify an API consumer that a large search result report is available."""

    @staticmethod
    @cors.crossdomain(origin='*')
    def post(search_id):
        """Notify originator of async report request that the document is available."""
        try:
            if search_id is None:
                return resource_utils.path_param_error_response('search ID')

            # If exceeded max retries we're done.
            event_count: int = 0
            events = EventTracking.find_by_key_id_type(search_id, EventTracking.EventTrackingTypes.API_NOTIFICATION)
            if events:
                event_count = len(events)
            if event_count > current_app.config.get('EVENT_MAX_RETRIES'):
                return notification_error(resource_utils.CallbackExceptionCodes.MAX_RETRIES, search_id,
                                          HTTPStatus.INTERNAL_SERVER_ERROR,
                                          'Max retries reached.')

            search_detail = SearchResult.find_by_search_id(search_id, False)
            if not search_detail:
                return notification_error(resource_utils.CallbackExceptionCodes.UNKNOWN_ID, search_id,
                                          HTTPStatus.NOT_FOUND)

            # Check if search result is async: always have callback_url.
            callback_url = search_detail.callback_url
            if callback_url is None:
                return notification_error(resource_utils.CallbackExceptionCodes.INVALID_ID,
                                          search_id,
                                          HTTPStatus.BAD_REQUEST,
                                          'Required callbackURL is missing.')

            # Send the notification.
            response = send_notification(callback_url, search_id)
            status_code = response.status_code
            if status_code not in (HTTPStatus.OK, HTTPStatus.ACCEPTED, HTTPStatus.NO_CONTENT):
                message = f'Status code={status_code}. Response: ' + str(response.content)
                return notification_error(resource_utils.CallbackExceptionCodes.NOTIFICATION_ERR,
                                          search_id,
                                          HTTPStatus.INTERNAL_SERVER_ERROR,
                                          message)

            # Track success event.
            EventTracking.create(search_id, EventTracking.EventTrackingTypes.API_NOTIFICATION, int(status_code))

            return response.content, response.status_code

        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, None, 'POST notificaton event')
        except Exception as default_err:  # noqa: B902; return nicer default error
            return notification_error(resource_utils.CallbackExceptionCodes.DEFAULT,
                                      search_id,
                                      HTTPStatus.INTERNAL_SERVER_ERROR,
                                      repr(default_err))


def callback_error(code: str, search_id: str, status_code, message: str = None):
    """Return to the event listener callback error response based on the code."""
    error = CALLBACK_MESSAGES[code].format(search_id=search_id)
    if message:
        error += ' ' + message
    current_app.logger.error(error)
    # Track event here.
    EventTracking.create(search_id, EventTracking.EventTrackingTypes.SEARCH_REPORT, status_code, message)
    if status_code != HTTPStatus.BAD_REQUEST and code not in (resource_utils.CallbackExceptionCodes.MAX_RETRIES,
                                                              resource_utils.CallbackExceptionCodes.UNKNOWN_ID):
        # set up retry
        enqueue_search_report(search_id)
    return resource_utils.error_response(status_code, error)


def notification_error(code: str, search_id: str, status_code, message: str = None):
    """Return to the event listener a notification error response based on the status code."""
    error = CALLBACK_MESSAGES[code].format(search_id=search_id)
    if message:
        error += ' ' + message
    current_app.logger.error(error)
    # Track event here.
    EventTracking.create(search_id, EventTracking.EventTrackingTypes.API_NOTIFICATION, status_code, message)
    if status_code != HTTPStatus.BAD_REQUEST and code not in (resource_utils.CallbackExceptionCodes.MAX_RETRIES,
                                                              resource_utils.CallbackExceptionCodes.UNKNOWN_ID):
        # set up retry
        enqueue_notification(search_id)
    return resource_utils.error_response(status_code, error)


def send_notification(callback_url: str, search_id):
    """Send a notification message that the search results report is available."""
    gateway_url = current_app.config.get('GATEWAY_URL')
    search_report_url = gateway_url + REPORT_URL.format(search_id=search_id)
    data = {
        'id': search_id,
        'getReportURL': search_report_url
    }
    data_json = json.dumps(data)
    headers = {
        'Content-Type': 'application/json'
    }
    current_app.logger.info('Sending ' + data_json + ' to ' + callback_url)
    response = requests.post(url=callback_url, headers=headers, data=data_json)
    return response


def is_async(search_detail: SearchResult, search_select) -> bool:
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


def enqueue_search_report(search_id: str):
    """Add the search report request to the queue."""
    try:
        payload = {
            'searchId': search_id
        }
        apikey = current_app.config.get('SUBSCRIPTION_API_KEY')
        if apikey:
            payload['apikey'] = apikey
        GoogleQueueService().publish_search_report(payload)
        current_app.logger.info(f'Enqueue search report successful for id={search_id}.')
    except Exception as err:  # noqa: B902; do not alter app processing
        current_app.logger.error(f'Enqueue search report failed for id={search_id}: ' + repr(err))
        EventTracking.create(search_id,
                             EventTracking.EventTrackingTypes.SEARCH_REPORT,
                             int(HTTPStatus.INTERNAL_SERVER_ERROR),
                             'Enqueue search report event failed: ' + repr(err))


def enqueue_notification(search_id: str):
    """Add the notification request to the queue."""
    try:
        payload = {
            'searchId': search_id
        }
        apikey = current_app.config.get('SUBSCRIPTION_API_KEY')
        if apikey:
            payload['apikey'] = apikey
        GoogleQueueService().publish_notification(payload)
        current_app.logger.info(f'Enqueue notification successful for id={search_id}.')
    except Exception as err:  # noqa: B902; do not alter app processing
        current_app.logger.error(f'Enqueue notification failed for id={search_id}: ' + repr(err))
        EventTracking.create(search_id,
                             EventTracking.EventTrackingTypes.API_NOTIFICATION,
                             int(HTTPStatus.INTERNAL_SERVER_ERROR),
                             'Enqueue api notification event failed: ' + repr(err))
