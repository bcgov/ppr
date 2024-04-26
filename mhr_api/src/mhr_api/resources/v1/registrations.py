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
"""API endpoints for requests to maintain MH registrations."""
import copy
from http import HTTPStatus

from flask import Blueprint
from flask import g, current_app, jsonify, request
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils
from mhr_api.utils.auth import jwt
from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.services.authz import authorized, authorized_role, is_bcol_help, is_staff, is_all_staff_account
from mhr_api.services.authz import is_reg_staff_account, get_group, MANUFACTURER_GROUP, STAFF_ROLE, REGISTER_MH
from mhr_api.models import (
    batch_utils, EventTracking, MhrRegistration, MhrManufacturer, registration_utils as model_reg_utils
)
from mhr_api.models.type_tables import MhrNoteStatusTypes, MhrRegistrationTypes
from mhr_api.models.registration_utils import AccountRegistrationParams
from mhr_api.reports import get_callback_pdf
from mhr_api.reports.v2.report import Report
from mhr_api.reports.v2.report_utils import ReportTypes
from mhr_api.resources import utils as resource_utils, registration_utils as reg_utils
from mhr_api.services.payment import TransactionTypes
from mhr_api.services.payment.exceptions import SBCPaymentException
from mhr_api.services.utils.exceptions import ReportDataException, ReportException, StorageException
from mhr_api.services.document_storage.storage_service import DocumentTypes, GoogleStorageService


bp = Blueprint('REGISTRATIONS1',  # pylint: disable=invalid-name
               __name__, url_prefix='/api/v1/registrations')
CURRENT_PARAM: str = 'current'
COLLAPSE_PARAM: str = 'collapse'
NOTIFY_PARAM: str = 'notify'
DOWNLOAD_LINK_PARAM: str = 'downloadLink'
ACCOUNT_MANUFACTURER_ERROR = 'No existing manufacturer information found for account={account_id}.'


@bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_account_registrations():
    """Get account registrations summary list."""
    account_id = ''
    try:
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        # current_app.logger.debug(f'get_account_registrations account={account_id}.')
        # Try to fetch account registrations.
        collapse_param = request.args.get(COLLAPSE_PARAM)
        if collapse_param is None or not isinstance(collapse_param, (bool, str)):
            collapse_param = False
        elif isinstance(collapse_param, str) and collapse_param.lower() in ['true', '1', 'y', 'yes']:
            collapse_param = True
        elif isinstance(collapse_param, str):
            collapse_param = False
        is_read_staff: bool = (is_staff(jwt) or is_bcol_help(account_id, jwt))
        params: AccountRegistrationParams = AccountRegistrationParams(account_id=account_id,
                                                                      collapse=collapse_param,
                                                                      sbc_staff=is_read_staff)
        params = resource_utils.get_account_registration_params(request, params)
        statement_list = MhrRegistration.find_all_by_account_id(params)
        return jsonify(statement_list), HTTPStatus.OK

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id,
                                                    'GET account registrations id=' + account_id)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def post_registrations():  # pylint: disable=too-many-return-statements,too-many-branches
    """Create a new MHR registration."""
    account_id = ''
    try:
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None or account_id.strip() == '':
            return resource_utils.account_required_response()
        # Verify request JWT role
        if not authorized_role(jwt, REGISTER_MH):
            current_app.logger.error('User not staff or missing required role: ' + REGISTER_MH)
            return resource_utils.unauthorized_error_response(account_id)
        if is_bcol_help(account_id, jwt):
            return resource_utils.helpdesk_unauthorized_error_response('new manufactured home')
        manufacturer: MhrManufacturer = None
        if get_group(jwt) == MANUFACTURER_GROUP:
            current_app.logger.debug(f'Manufacturer request looking up info for account={account_id}.')
            manufacturer = MhrManufacturer.find_by_account_id(account_id)
            if not manufacturer:
                current_app.logger.info(f'No manufacturer info found for account id={account_id}')
                return resource_utils.bad_request_response(ACCOUNT_MANUFACTURER_ERROR.format(account_id=account_id))

        request_json = request.get_json(silent=True)
        # Validate request against the schema.
        # Location may have no street - replace with blank to pass validation
        if request_json.get('location') and request_json['location'].get('address') and \
                not request_json['location']['address'].get('street'):
            request_json['location']['address']['street'] = ' '
        valid_format, errors = schema_utils.validate(request_json, 'registration', 'mhr')
        # Additional validation not covered by the schema.
        extra_validation_msg = resource_utils.validate_registration(request_json, is_staff(jwt))
        group: str = get_group(jwt)
        if manufacturer and group == MANUFACTURER_GROUP:
            extra_validation_msg += resource_utils.validate_registration_manufacturer(request_json, manufacturer)

        if not valid_format or extra_validation_msg != '':
            return resource_utils.validation_error_response(errors, reg_utils.VAL_ERROR, extra_validation_msg)
        # Set up the registration, pay, and save the data.
        registration = reg_utils.pay_and_save_registration(request,
                                                           request_json,
                                                           account_id,
                                                           group,
                                                           TransactionTypes.REGISTRATION)
        registration.report_view = True
        response_json = registration.new_registration_json

        # Return report if request header Accept MIME type is application/pdf.
        if resource_utils.is_pdf(request):
            current_app.logger.info('Report not yet available: returning JSON.')
        response_json['usergroup'] = group
        if is_reg_staff_account(account_id):
            token = g.jwt_oidc_token_info
            username: str = token.get('firstname', '') + ' ' + token.get('lastname', '')
            response_json['username'] = username
            reg_utils.enqueue_registration_report(registration, response_json, ReportTypes.MHR_REGISTRATION_STAFF)
            del response_json['username']
        else:
            reg_utils.enqueue_registration_report(registration, response_json, ReportTypes.MHR_REGISTRATION)
        del response_json['usergroup']
        return response_json, HTTPStatus.CREATED

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id,
                                                    'POST mhr registration id=' + account_id)
    except SBCPaymentException as pay_exception:
        return resource_utils.pay_exception_response(pay_exception, account_id)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('/<string:mhr_number>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_registrations(mhr_number: str):  # pylint: disable=too-many-return-statements, too-many-branches
    """Get registration information for a previous MH registration created by the account."""
    try:
        current_app.logger.info(f'get_registrations mhr_number={mhr_number}')
        if mhr_number is None:
            return resource_utils.path_param_error_response('MHR number')
        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        # Set to false as default to generate json with original MH registration data.
        current_param = request.args.get(CURRENT_PARAM)
        if current_param is None or not isinstance(current_param, (bool, str)):
            current_param = False
        elif isinstance(current_param, str) and current_param.lower() in ['true', '1', 'y', 'yes']:
            current_param = True
        elif isinstance(current_param, str):
            current_param = False
        registration: MhrRegistration = None
        # Try to fetch MH registration by MHR number
        # Not found or not in the account list throw exceptions.
        if current_param:
            registration = MhrRegistration.find_all_by_mhr_number(mhr_number,
                                                                  account_id,
                                                                  is_all_staff_account(account_id))
            registration.current_view = True
            registration.staff = is_staff(jwt)
        else:
            registration = MhrRegistration.find_original_by_mhr_number(mhr_number,
                                                                       account_id,
                                                                       is_all_staff_account(account_id))
        response_json = registration.new_registration_json
        # Return report if request header Accept MIME type is application/pdf.
        if resource_utils.is_pdf(request):
            report_type = ReportTypes.MHR_REGISTRATION
            if is_reg_staff_account(account_id):
                report_type = ReportTypes.MHR_REGISTRATION_STAFF
            current_app.logger.info(f'Fetching registration report for MHR# {mhr_number}.')
            return reg_utils.get_registration_report(registration,
                                                     response_json,
                                                     report_type,
                                                     jwt.get_token_auth_header(),
                                                     HTTPStatus.CREATED)

        if current_param and response_json.get('permitStatus', '') == MhrNoteStatusTypes.ACTIVE:
            if is_all_staff_account(account_id):
                response_json['changePermit'] = True
            else:
                response_json['changePermit'] = get_change_permit(registration, account_id)
        return response_json, HTTPStatus.OK
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id,
                                                    'GET MH registration id=' + mhr_number)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('/batch/manufacturer', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
def get_batch_manufacturer_registrations():  # pylint: disable=too-many-return-statements
    """Get the batch manufacturer registrations report for registries staff and optionally email."""
    try:
        current_app.logger.info('getting batch manufacturer registrations')
        # Authenticate with request api key
        if not resource_utils.valid_api_key(request):
            return resource_utils.unauthorized_error_response('batch manufacturer registrations report')
        start_ts: str = request.args.get(model_reg_utils.START_TS_PARAM, None)
        end_ts: str = request.args.get(model_reg_utils.END_TS_PARAM, None)
        notify: bool = get_optional_param(request, NOTIFY_PARAM, False)
        return_link: bool = get_optional_param(request, DOWNLOAD_LINK_PARAM, notify)
        if notify:
            return_link = True
        if start_ts and end_ts:
            start_ts = resource_utils.remove_quotes(start_ts)
            end_ts = resource_utils.remove_quotes(end_ts)
            current_app.logger.debug(f'Using request timestamp range {start_ts} to {end_ts}')
        registrations = model_reg_utils.get_batch_manufacturer_reg_report_data(start_ts, end_ts)
        if not registrations:
            return batch_manufacturer_report_empty(notify, start_ts, end_ts)
        if registrations[0].get('batchStorageUrl'):  # Report already generated so fetch it.
            return batch_manufacturer_report_exists(registrations[0].get('batchStorageUrl'), notify, return_link)
        raw_data, status_code, headers = get_batch_manufacturer_report(registrations)
        if status_code not in (HTTPStatus.OK, HTTPStatus.CREATED):
            current_app.logger.error('Batch manufacturer report merge call failed: ' + raw_data.get_data(as_text=True))
            return raw_data, status_code, headers
        report_url: str = save_batch_manufacturer_report(registrations, raw_data, return_link)
        return batch_manufacturer_report_response(raw_data, report_url, notify)
    except ReportException as report_err:
        return event_error_response(resource_utils.CallbackExceptionCodes.REPORT_ERR,
                                    HTTPStatus.INTERNAL_SERVER_ERROR,
                                    'Batch manufacturer report API error: ' + str(report_err))
    except ReportDataException as report_data_err:
        return event_error_response(resource_utils.CallbackExceptionCodes.REPORT_DATA_ERR,
                                    HTTPStatus.INTERNAL_SERVER_ERROR,
                                    'Batch manufacturer report API data error: ' + str(report_data_err))
    except StorageException as storage_err:
        return event_error_response(resource_utils.CallbackExceptionCodes.STORAGE_ERR,
                                    HTTPStatus.INTERNAL_SERVER_ERROR,
                                    'Batch manufacturer report storage API error: ' + str(storage_err))
    except DatabaseException as db_exception:
        return event_error_response(resource_utils.CallbackExceptionCodes.DEFAULT,
                                    HTTPStatus.INTERNAL_SERVER_ERROR,
                                    'Batch manufacturer report database error: ' + str(db_exception))
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return event_error_response(resource_utils.CallbackExceptionCodes.DEFAULT,
                                    HTTPStatus.INTERNAL_SERVER_ERROR,
                                    'Batch manufacturer report default error: ' + str(default_exception))


@bp.route('/batch', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_batch_registrations():
    """Get the batch registrations by timestamp range. Restricted by account id in the API gateway configuration."""
    try:
        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if not account_id:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        current_app.logger.info(f'getting batch registrations account id {account_id}.')
        start_ts: str = request.args.get(model_reg_utils.START_TS_PARAM, None)
        end_ts: str = request.args.get(model_reg_utils.END_TS_PARAM, None)
        if start_ts and end_ts:
            start_ts = resource_utils.remove_quotes(start_ts)
            end_ts = resource_utils.remove_quotes(end_ts)
            current_app.logger.debug(f'Batch registrations using request timestamp range {start_ts} to {end_ts}')
        registrations = batch_utils.get_batch_registration_data(start_ts, end_ts)
        if not registrations:
            return jsonify([]), HTTPStatus.NO_CONTENT, {'Content-Type': 'application/json'}
        return jsonify(registrations), HTTPStatus.OK, {'Content-Type': 'application/json'}
    except DatabaseException as db_exception:
        return event_error_response(resource_utils.CallbackExceptionCodes.DEFAULT,
                                    HTTPStatus.INTERNAL_SERVER_ERROR,
                                    'Batch registration database error: ' + str(db_exception),
                                    reg_utils.EVENT_KEY_BATCH_REG)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return event_error_response(resource_utils.CallbackExceptionCodes.DEFAULT,
                                    HTTPStatus.INTERNAL_SERVER_ERROR,
                                    'Batch registration default error: ' + str(default_exception),
                                    reg_utils.EVENT_KEY_BATCH_REG)


@bp.route('/batch/manufacturer', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*')
def post_batch_manufacturer_registrations():  # pylint: disable=too-many-return-statements
    """Generate the batch manufacturer registrations report for registries staff and optionally email."""
    return get_batch_manufacturer_registrations()


@bp.route('/batch/noclocation', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*')
def post_batch_noc_locations():  # pylint: disable=too-many-return-statements
    """Generate the batch notice of change in location report for registries staff and optionally email."""
    try:
        current_app.logger.info('getting batch noc location registrations')
        # Authenticate with request api key
        if not resource_utils.valid_api_key(request):
            return resource_utils.unauthorized_error_response('batch noc location registrations report')
        start_ts: str = request.args.get(model_reg_utils.START_TS_PARAM, None)
        end_ts: str = request.args.get(model_reg_utils.END_TS_PARAM, None)
        notify: bool = get_optional_param(request, NOTIFY_PARAM, False)
        return_link: bool = get_optional_param(request, DOWNLOAD_LINK_PARAM, notify)
        if notify:
            return_link = True
        if start_ts and end_ts:
            start_ts = resource_utils.remove_quotes(start_ts)
            end_ts = resource_utils.remove_quotes(end_ts)
            current_app.logger.debug(f'Using request timestamp range {start_ts} to {end_ts}')
        registrations = batch_utils.get_batch_location_report_data(start_ts, end_ts)
        if not registrations:
            return batch_utils.batch_location_report_empty(notify, start_ts, end_ts)
        if registrations[0].get('batchStorageUrl'):  # Report already generated so fetch it.
            return batch_utils.batch_location_report_exists(registrations[0].get('batchStorageUrl'),
                                                            notify,
                                                            return_link)
        raw_data, status_code, headers = get_batch_noc_location_report(registrations)
        if status_code not in (HTTPStatus.OK, HTTPStatus.CREATED):
            current_app.logger.error('Batch noc location report merge call failed: ' + raw_data.get_data(as_text=True))
            return raw_data, status_code, headers
        report_url: str = batch_utils.save_batch_location_report(registrations, raw_data, return_link)
        return batch_utils.batch_location_report_response(raw_data, report_url, notify)
    except ReportException as report_err:
        return event_error_response(resource_utils.CallbackExceptionCodes.REPORT_ERR,
                                    HTTPStatus.INTERNAL_SERVER_ERROR,
                                    'Batch noc location report API error: ' + str(report_err),
                                    reg_utils.EVENT_KEY_BATCH_LOCATION)
    except ReportDataException as report_data_err:
        return event_error_response(resource_utils.CallbackExceptionCodes.REPORT_DATA_ERR,
                                    HTTPStatus.INTERNAL_SERVER_ERROR,
                                    'Batch noc location report API data error: ' + str(report_data_err),
                                    reg_utils.EVENT_KEY_BATCH_LOCATION)
    except StorageException as storage_err:
        return event_error_response(resource_utils.CallbackExceptionCodes.STORAGE_ERR,
                                    HTTPStatus.INTERNAL_SERVER_ERROR,
                                    'Batch noc location report storage API error: ' + str(storage_err),
                                    reg_utils.EVENT_KEY_BATCH_LOCATION)
    except DatabaseException as db_exception:
        return event_error_response(resource_utils.CallbackExceptionCodes.DEFAULT,
                                    HTTPStatus.INTERNAL_SERVER_ERROR,
                                    'Batch noc location report database error: ' + str(db_exception),
                                    reg_utils.EVENT_KEY_BATCH_LOCATION)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return event_error_response(resource_utils.CallbackExceptionCodes.DEFAULT,
                                    HTTPStatus.INTERNAL_SERVER_ERROR,
                                    'Batch noc location report default error: ' + str(default_exception),
                                    reg_utils.EVENT_KEY_BATCH_LOCATION)


def get_batch_noc_location_report(registrations):
    """Build the batch notice of change in location registration report from the registrations."""
    reports = []
    # Generate individual registration reports with a cover letter for each secured party.
    for reg in registrations:
        reg_data = reg.get('reportData')
        if reg_data.get('ppr') and reg_data['ppr'].get('securedParties'):
            current_app.logger.info('Generating noc location report(s) for reg id=' +
                                    str(reg_data.get('registrationId')))
            for party in reg_data['ppr'].get('securedParties'):
                rep_data = copy.deepcopy(reg_data)
                rep_data['ppr']['securedParty'] = party
                raw_data, status_code, headers = get_callback_pdf(rep_data,
                                                                  STAFF_ROLE,
                                                                  ReportTypes.MHR_REGISTRATION_STAFF,
                                                                  None,
                                                                  None)
                if status_code in (HTTPStatus.OK, HTTPStatus.CREATED):
                    reports.append(raw_data)
                else:
                    current_app.logger.error(str(reg.get('registrationId')) +
                                             ' report api call failed: ' + raw_data.get_data(as_text=True))
                    return raw_data, status_code, headers
    return Report.batch_merge(reports)


def get_batch_manufacturer_report(registrations):
    """Build the batch manufacturer registration report from the registrations."""
    reports = []
    # Generate individual registration reports with a cover letter
    for reg in registrations:
        raw_data, status_code, headers = get_callback_pdf(reg.get('reportData'),
                                                          reg.get('accountId'),
                                                          ReportTypes.MHR_REGISTRATION_STAFF,
                                                          None,
                                                          None)
        if status_code in (HTTPStatus.OK, HTTPStatus.CREATED):
            reports.append(raw_data)
        else:
            current_app.logger.error(str(reg.get('registrationId')) +
                                     ' report api call failed: ' + raw_data.get_data(as_text=True))
            return raw_data, status_code, headers
    return Report.batch_merge(reports)


def save_batch_manufacturer_report(registrations, raw_data, return_link: bool) -> str:
    """Save the batch manufacturer registration report to document storage."""
    link: str = None
    batch_storage_url = model_reg_utils.get_batch_storage_name_manufacturer_mhreg()
    current_app.logger.info(f'Saving batch manufacturer registration report to: {batch_storage_url}.')
    if return_link:
        link = GoogleStorageService.save_document_link(batch_storage_url,
                                                       raw_data,
                                                       DocumentTypes.BATCH_REGISTRATION,
                                                       batch_utils.DEFAULT_DOWNLOAD_DAYS)
    else:
        GoogleStorageService.save_document(batch_storage_url, raw_data, DocumentTypes.BATCH_REGISTRATION)
    model_reg_utils.update_reg_report_batch_url(registrations, batch_storage_url)
    return link


def batch_manufacturer_report_exists(batch_storage_url: str, notify: bool, return_link: bool):
    """Create response when batch manufacturer registration report already exists."""
    report_url: str = None
    raw_data = None
    current_app.logger.info(f'Fetching batch manufacturer registration report for: {batch_storage_url}.')
    if return_link:
        report_url = GoogleStorageService.get_document_link(batch_storage_url,
                                                            DocumentTypes.BATCH_REGISTRATION,
                                                            batch_utils.DEFAULT_DOWNLOAD_DAYS)
    else:
        raw_data = GoogleStorageService.get_document(batch_storage_url, DocumentTypes.BATCH_REGISTRATION)
    return batch_manufacturer_report_response(raw_data, report_url, notify)


def batch_manufacturer_report_empty(notify: bool, start_ts: str, end_ts: str):
    """Create response when no manufacturer registrations exist."""
    message: str = 'No manufacturer registrations found for default timestamp range of last 24 hours.'
    if start_ts and end_ts:
        message = f'No manufacturer registrations found for timestamp range {start_ts} to {end_ts}'
    current_app.logger.info(message)
    if notify:
        current_app.logger.debug('Sending notify with no registration report.')
        reg_utils.email_batch_man_report_staff(None)
    EventTracking.create(reg_utils.EVENT_KEY_BATCH_MAN_REG,
                         EventTracking.EventTrackingTypes.MHR_REGISTRATION_REPORT,
                         HTTPStatus.NO_CONTENT,
                         message)
    return '', HTTPStatus.NO_CONTENT


def batch_manufacturer_report_response(raw_data, report_url: str, notify: bool):
    """Create response when manufacturer registrations exist and report generated."""
    message: str = report_url if report_url else 'Batch manufacturer report returned in response.'
    if notify:
        current_app.logger.debug(f'Sending notify message with download link to {report_url}')
        reg_utils.email_batch_man_report_staff(report_url)
    if not report_url:
        headers = {'Content-Type': 'application/pdf'}
        return raw_data, HTTPStatus.OK, headers
    headers = {'Content-Type': 'application/json'}
    response_json = {'reportDownloadUrl': report_url}
    EventTracking.create(reg_utils.EVENT_KEY_BATCH_MAN_REG,
                         EventTracking.EventTrackingTypes.MHR_REGISTRATION_REPORT,
                         HTTPStatus.OK,
                         message)
    return response_json, HTTPStatus.OK, headers


def event_error_response(code: str, status_code, message: str = None, event_key: int = None):
    """Return to the event listener callback error response based on the code."""
    error = reg_utils.CALLBACK_MESSAGES[code].format(key_id='batch_manufacturer_report')
    if message:
        error += ' ' + message
    current_app.logger.error(error)
    # Track event here.
    e_key: int = event_key if event_key else reg_utils.EVENT_KEY_BATCH_MAN_REG
    EventTracking.create(e_key,
                         EventTracking.EventTrackingTypes.MHR_REGISTRATION_REPORT,
                         status_code,
                         message[:8000])
    return resource_utils.error_response(status_code, error)


def get_optional_param(req, param_name: str, default: bool = False) -> bool:
    """Try and obtain an optional boolean parameter value from the request parameters."""
    value: bool = default
    param = req.args.get(param_name)
    if param is None or not isinstance(param, (bool, str)):
        return value
    if isinstance(param, str) and param.lower() in ['true', '1', 'y', 'yes']:
        value = True
    elif isinstance(param, bool):
        value = param
    return value


def get_change_permit(registration: MhrRegistration, account_id: str) -> bool:
    """Currnent MH information if active permit set non-staff access."""
    can_edit: bool = False
    if registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.registration_type in (MhrRegistrationTypes.PERMIT, MhrRegistrationTypes.AMENDMENT):
                if reg.notes and reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE and \
                        account_id == reg.account_id:
                    can_edit = True
    return can_edit
