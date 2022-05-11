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
"""API callback endpoint to generate and store MHR search reports after completting search step 2."""

from http import HTTPStatus

# import requests
from flask import Blueprint, current_app  # , jsonify, request
from flask_cors import cross_origin

from mhr_api.exceptions import DatabaseException
from mhr_api.services.queue_service import GoogleQueueService
from mhr_api.models import EventTracking, SearchResult  # , utils as model_utils
from mhr_api.resources import utils as resource_utils


# from mhr_api.reports import ReportTypes, get_pdf
# from mhr_api.callback.reports.report_service import get_search_report
from mhr_api.services.utils.exceptions import ReportException, ReportDataException, StorageException
# from mhr_api.services.document_storage.storage_service import GoogleStorageService


bp = Blueprint('SEARCH_REPORT1', __name__, url_prefix='/api/v1/search-report-callback')  # pylint: disable=invalid-name

CALLBACK_MESSAGES = {
    resource_utils.CallbackExceptionCodes.UNKNOWN_ID: '01: no search result data found for id={search_id}.',
    resource_utils.CallbackExceptionCodes.MAX_RETRIES: '02: maximum retries reached for id={search_id}.',
    resource_utils.CallbackExceptionCodes.INVALID_ID: '03: search result report setup not async for id={search_id}.',
    resource_utils.CallbackExceptionCodes.DEFAULT: '04: default error for id={search_id}.',
    resource_utils.CallbackExceptionCodes.REPORT_DATA_ERR: '05: report data error for id={search_id}.',
    resource_utils.CallbackExceptionCodes.REPORT_ERR: '06: generate report failed for id={search_id}.',
    resource_utils.CallbackExceptionCodes.STORAGE_ERR: '07: document storage save failed for id={search_id}.',
    resource_utils.CallbackExceptionCodes.NOTIFICATION_ERR: '08: notification failed for id={search_id}.'
}


@bp.route('/<string:search_id>', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*')
def post_search_report_callback(  # pylint: disable=too-many-branches,too-many-locals,too-many-return-statements
        search_id: str
        ):
    """Resource to generate and store a search result report as callback request."""
    try:
        current_app.logger.info(f'Search report callback starting id={search_id}.')
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

        # Generate the report with an API call here
        current_app.logger.info(f'Generating search detail report for {search_id}.')
        # raw_data, status_code, headers = get_search_report(search_id)
        # if not raw_data or not status_code:
        #    return callback_error(resource_utils.CallbackExceptionCodes.REPORT_DATA_ERR,
        #                            search_id,
        #                            HTTPStatus.INTERNAL_SERVER_ERROR,
        #                            'No data or status code.')
        # current_app.logger.debug('report api call status=' + str(status_code) + ' headers=' + json.dumps(headers))
        # if status_code not in (HTTPStatus.OK, HTTPStatus.CREATED):
        #    message = f'Status code={status_code}. Response: ' + raw_data.get_data(as_text=True)
        #    return callback_error(resource_utils.CallbackExceptionCodes.REPORT_ERR,
        #                            search_id,
        #                            HTTPStatus.INTERNAL_SERVER_ERROR,
        #                            message)

        # doc_name = model_utils.get_search_doc_storage_name(search_detail.search)
        # current_app.logger.info(f'Saving report output to doc storage: name={doc_name}.')
        # response = GoogleStorageService.save_document(doc_name, raw_data)
        # current_app.logger.info('Save document storage response: ' + json.dumps(response))
        # search_detail.doc_storage_url = doc_name
        # search_detail.save()

        # Track success event.
        EventTracking.create(search_id, EventTracking.EventTrackingTypes.SEARCH_REPORT, int(HTTPStatus.OK))

        # return response, HTTPStatus.OK
        # Replace with above when report implemented.
        return None, HTTPStatus.OK
    except ReportException as report_err:
        return callback_error(resource_utils.CallbackExceptionCodes.REPORT_ERR,
                              search_id,
                              HTTPStatus.INTERNAL_SERVER_ERROR,
                              str(report_err))
    except ReportDataException as report_data_err:
        return callback_error(resource_utils.CallbackExceptionCodes.REPORT_DATA_ERR,
                              search_id,
                              HTTPStatus.INTERNAL_SERVER_ERROR,
                              str(report_data_err))
    except StorageException as storage_err:
        return callback_error(resource_utils.CallbackExceptionCodes.STORAGE_ERR,
                              search_id,
                              HTTPStatus.INTERNAL_SERVER_ERROR,
                              str(storage_err))
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, None, 'POST large report event')
    except Exception as default_err:  # noqa: B902; return nicer default error
        return callback_error(resource_utils.CallbackExceptionCodes.DEFAULT,
                              search_id,
                              HTTPStatus.INTERNAL_SERVER_ERROR,
                              str(default_err))


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
        current_app.logger.error(f'Enqueue search report failed for id={search_id}: ' + str(err))
        EventTracking.create(search_id,
                             EventTracking.EventTrackingTypes.SEARCH_REPORT,
                             int(HTTPStatus.INTERNAL_SERVER_ERROR),
                             'Enqueue search report event failed: ' + str(err))
