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
import json
import copy

import requests
from flask import Blueprint, current_app, jsonify, request
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils

from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.models import EventTracking, SearchRequest, SearchResult, utils as model_utils
from mhr_api.models.search_request import REPORT_STATUS_PENDING
from mhr_api.resources import utils as resource_utils
from mhr_api.resources.v1.search_report_callback import get_search_report
from mhr_api.services.authz import authorized, is_bcol_help, is_sbc_office_account, is_staff_account
from mhr_api.services.document_storage.storage_service import GoogleStorageService
from mhr_api.services.payment.exceptions import SBCPaymentException
from mhr_api.services.payment.payment import Payment
from mhr_api.services.queue_service import GoogleQueueService
from mhr_api.services.utils.exceptions import ReportException, ReportDataException, StorageException
from mhr_api.utils.auth import jwt


bp = Blueprint('SEARCH_RESULTS1', __name__, url_prefix='/api/v1/search-results')  # pylint: disable=invalid-name

VAL_ERROR = 'Search details request data validation errors.'  # Validation error prefix
SAVE_ERROR_MESSAGE = 'Account {0} search db save failed: {1}'
PAY_REFUND_MESSAGE = 'Account {0} search refunding payment for invoice {1}.'
PAY_REFUND_ERROR = 'Account {0} search payment refund failed for invoice {1}: {2}.'
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
# Map search type to payment transaction details description
TO_SEARCH_TYPE_DESCRIPTION = {
    SearchRequest.SearchTypes.ORGANIZATION_NAME.value: 'Organization/Business Name:',
    SearchRequest.SearchTypes.OWNER_NAME.value: 'Owner Individual Name:',
    SearchRequest.SearchTypes.MANUFACTURED_HOME_NUM.value: 'Manufactured Home Registration Number:',
    SearchRequest.SearchTypes.SERIAL_NUM.value: 'Serial Number:'
}
CERTIFIED_PARAM = 'certified'
ROUTING_SLIP_PARAM = 'routingSlipNumber'
DAT_NUMBER_PARAM = 'datNumber'
BCOL_NUMBER_PARAM = 'bcolAccountNumber'
PRIORITY_PARAM = 'priority'
CLIENT_REF_PARAM = 'clientReferenceId'


@bp.route('/<string:search_id>', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def post_search_results(search_id: str):  # pylint: disable=too-many-branches, too-many-locals, too-many-statements
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
        search_detail: SearchResult = SearchResult.validate_search_select(request_json, search_id)

        # Large report threshold check, require/save callbackURL parameter.
        # UI may not request a report in step 2.
        callback_url = request.args.get(CALLBACK_PARAM)
        if is_async(search_detail, request_json):
            if callback_url is None:
                error = f'Large search report required callbackURL parameter missing for {search_id}.'
                current_app.logger.warn(error)
                return resource_utils.error_response(HTTPStatus.BAD_REQUEST, error)
        else:
            callback_url = None

        # Charge a search fee.
        payment = Payment(jwt=jwt.get_token_auth_header(),
                          account_id=account_id,
                          details=get_payment_details(search_detail, request_json))
        query: SearchRequest = search_detail.search
        pay_ref: None
        invoice_id = None
        certified: bool = False
        # Conditionally update client reference id from request parameter.
        # Do here to pass to an updated value to the pay api.
        if request.args.get(CLIENT_REF_PARAM):
            client_ref: str = request.args.get(CLIENT_REF_PARAM)
            client_ref = client_ref.strip()
            if client_ref is not None and len(client_ref) < 51:  # Allow empty strings as clearing the value.
                query.client_reference_id = client_ref
                # Also update the original search criteria json as this is used in the account search history.
                criteria = copy.deepcopy(query.search_criteria)
                criteria['clientReferenceId'] = client_ref
                query.search_criteria = criteria
                current_app.logger.info(f'POST search results updating client ref to {client_ref}.')

        # Staff has special payment rules and setup.
        if is_staff_account(account_id, jwt) or is_bcol_help(account_id, jwt):
            current_app.logger.info(f'Setting up reg staff search for {account_id}.')
            payment_info = build_staff_payment(request, account_id)
            # bcol help is no fee; reg staff can be no fee.
            # FAS is routing slip only.
            # BCOL is dat number (optional) and BCOL account number (mandatory).
            # All staff roles including SBC can submit no fee searches.
            if ROUTING_SLIP_PARAM in payment_info and BCOL_NUMBER_PARAM in payment_info:
                return resource_utils.staff_payment_bcol_fas()
            pay_ref = payment.create_payment_staff_search(request_json,
                                                          payment_info,
                                                          str(query.id),
                                                          query.client_reference_id)
            if is_staff_account(account_id, jwt):
                certified = payment_info.get(CERTIFIED_PARAM)
        else:
            pay_ref = payment.create_payment_search(request_json,
                                                    str(query.id),
                                                    query.client_reference_id,
                                                    is_sbc_office_account(jwt.get_token_auth_header(), account_id))
        invoice_id = pay_ref['invoiceId']
        query.pay_invoice_id = int(invoice_id)
        query.pay_path = pay_ref['receipt']
        try:
            # Save the search query selection and details that match the selection.
            account_name = resource_utils.get_account_name(jwt.get_token_auth_header(), account_id)
            current_app.logger.debug('SearchResult.update_selection start')
            # Add user access group for conditional report content.
            search_detail.update_selection(request_json,
                                           account_name,
                                           callback_url,
                                           certified,
                                           is_staff_account(account_id, jwt))
            query.save()
            current_app.logger.debug('SearchResult.update_selection end')
        except Exception as db_exception:   # noqa: B902; handle all db related errors.
            current_app.logger.error(SAVE_ERROR_MESSAGE.format(account_id, str(db_exception)))
            if invoice_id is not None:
                current_app.logger.info(PAY_REFUND_MESSAGE.format(account_id, invoice_id))
                try:
                    payment.cancel_payment(invoice_id)
                except Exception as cancel_exception:   # noqa: B902; log exception
                    current_app.logger.error(PAY_REFUND_ERROR.format(account_id, invoice_id,
                                                                     str(cancel_exception)))
            raise db_exception

        response_data = search_detail.json
        # queue report generation.
        enqueue_search_report(search_id)
        response_data['getReportURL'] = REPORT_URL.format(search_id=search_id)
        if callback_url is None and search_detail.callback_url is not None:
            callback_url = search_detail.callback_url
            response_data['callbackURL'] = requests.utils.unquote(callback_url)

        return jsonify(response_data), HTTPStatus.OK

    except SBCPaymentException as pay_exception:
        return resource_utils.pay_exception_response(pay_exception, account_id)
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, 'POST search select id=' + search_id)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('/<string:search_id>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_search_results(search_id: str):  # pylint: disable=too-many-branches
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

        # Try to fetch search detail by search id. Remove _PENDING if it is in the id.
        if search_id.find(('_' + REPORT_STATUS_PENDING)) != -1:
            search_id = search_id.replace(('_' + REPORT_STATUS_PENDING), '')
        current_app.logger.info(f'Fetching search detail for {search_id}.')
        search_detail = SearchResult.find_by_search_id(search_id, True)
        if not search_detail:
            return resource_utils.not_found_error_response('searchId', search_id)

        # If no search selection (step 2) return an error. Could be results
        # with no exact matches and no results selected - nil, which is valid.
        if search_detail.search_select is None and search_detail.search.total_results_size > 0:
            return resource_utils.bad_request_response(GET_DETAILS_ERROR)

        if resource_utils.is_pdf(request):
            if search_detail.doc_storage_url is None:
                # Retry if more than 15 minutes has elapsed since the request was queued and no report.
                if not model_utils.report_retry_elapsed(search_detail.search.search_ts):
                    error_msg = f'Search report not yet available for {search_id}.'
                    current_app.logger.info(error_msg)
                    return resource_utils.bad_request_response(error_msg)
                return generate_search_report(search_detail, search_id)

            # If the request is for a report, fetch binary data from doc storage.
            doc_name = search_detail.doc_storage_url
            current_app.logger.info(f'Fetching search report {doc_name} from doc storage.')
            raw_data = GoogleStorageService.get_document(doc_name)
            return raw_data, HTTPStatus.OK, {'Content-Type': 'application/pdf'}

        response_data = search_detail.json
        response_data['reportAvailable'] = search_detail.doc_storage_url is not None
        return jsonify(response_data), HTTPStatus.OK

    except ReportException as report_err:
        return report_error(resource_utils.CallbackExceptionCodes.REPORT_ERR,
                            search_id,
                            HTTPStatus.INTERNAL_SERVER_ERROR,
                            str(report_err))
    except ReportDataException as report_data_err:
        return report_error(resource_utils.CallbackExceptionCodes.REPORT_DATA_ERR,
                            search_id,
                            HTTPStatus.INTERNAL_SERVER_ERROR,
                            str(report_data_err))
    except StorageException as storage_err:
        return report_error(resource_utils.CallbackExceptionCodes.STORAGE_ERR,
                            search_id,
                            HTTPStatus.INTERNAL_SERVER_ERROR,
                            str(storage_err))
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


def get_payment_details(search_detail: SearchResult, request_json):
    """Extract the payment details value from the search request criteria."""
    label = 'MHR Search'
    for selected in request_json:
        if selected.get('includeLienInfo', False):
            label = 'Combined Search'
            break

    details = {
        'label': label
    }
    search_criteria = search_detail.search.search_criteria
    if search_detail.search.search_type == SearchRequest.SearchTypes.OWNER_NAME.value:
        details['value'] = search_criteria['criteria']['ownerName']['last'] + ', ' +\
                           search_criteria['criteria']['ownerName']['first']
    else:
        details['value'] = search_criteria['criteria']['value']
    return details


def build_staff_payment(req: request, account_id: str):
    """Extract staff payment information from request parameters."""
    payment_info = {
        'waiveFees': True,
        'accountId': resource_utils.get_staff_account_id(req)
    }
    if is_bcol_help(account_id):
        return payment_info

    certified = req.args.get(CERTIFIED_PARAM)
    routing_slip = req.args.get(ROUTING_SLIP_PARAM)
    bcol_number = req.args.get(BCOL_NUMBER_PARAM)
    dat_number = req.args.get(DAT_NUMBER_PARAM)
    priority = req.args.get(PRIORITY_PARAM)
    if certified is not None and isinstance(certified, bool) and certified:
        payment_info[CERTIFIED_PARAM] = True
    elif certified is not None and isinstance(certified, str) and \
            certified.lower() in ['true', '1', 'y', 'yes']:
        payment_info[CERTIFIED_PARAM] = True
    if routing_slip is not None:
        payment_info[ROUTING_SLIP_PARAM] = str(routing_slip)
    if bcol_number is not None:
        payment_info[BCOL_NUMBER_PARAM] = str(bcol_number)
    if dat_number is not None:
        payment_info[DAT_NUMBER_PARAM] = str(dat_number)
    if priority is not None and isinstance(priority, bool) and priority:
        payment_info[PRIORITY_PARAM] = True
    elif priority is not None and isinstance(priority, str) and \
            priority.lower() in ['true', '1', 'y', 'yes']:
        payment_info[PRIORITY_PARAM] = True

    if ROUTING_SLIP_PARAM in payment_info or BCOL_NUMBER_PARAM in payment_info:
        payment_info['waiveFees'] = False
    current_app.logger.debug(payment_info)
    return payment_info


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


def generate_search_report(search_detail: SearchResult, search_id: str):
    """Attempt to regenerat search report request to the queue."""
    # Generate the report with an API call here
    current_app.logger.info(f'Generating search detail report for {search_id}.')
    raw_data, status_code, headers = get_search_report(search_id)
    if not raw_data or not status_code:
        return report_error(resource_utils.CallbackExceptionCodes.REPORT_DATA_ERR,
                            search_id,
                            HTTPStatus.INTERNAL_SERVER_ERROR,
                            'No data or status code.')
    current_app.logger.debug('report api call status=' + str(status_code) + ' headers=' + json.dumps(headers))
    if status_code not in (HTTPStatus.OK, HTTPStatus.CREATED):
        message = f'Status code={status_code}. Response: ' + raw_data.get_data(as_text=True)
        return report_error(resource_utils.CallbackExceptionCodes.REPORT_ERR,
                            search_id,
                            HTTPStatus.INTERNAL_SERVER_ERROR,
                            message)

    doc_name = model_utils.get_search_doc_storage_name(search_detail.search)
    current_app.logger.info(f'Saving report output to doc storage: name={doc_name}.')
    response = GoogleStorageService.save_document(doc_name, raw_data)
    current_app.logger.info('Save document storage response: ' + str(response))
    search_detail.doc_storage_url = doc_name
    search_detail.save()

    # Track success event.
    EventTracking.create(search_id, EventTracking.EventTrackingTypes.SEARCH_REPORT, int(HTTPStatus.OK))
    return raw_data, status_code, {'Content-Type': 'application/pdf'}


def report_error(code: str, search_id: str, status_code, message: str = None):
    """Return to the event listener callback error response based on the code."""
    error = CALLBACK_MESSAGES[code].format(search_id=search_id)
    if message:
        error += ' ' + message
    current_app.logger.error(error)
    # Track event here.
    EventTracking.create(search_id, EventTracking.EventTrackingTypes.SEARCH_REPORT, status_code, message)
    return resource_utils.error_response(status_code, error)
