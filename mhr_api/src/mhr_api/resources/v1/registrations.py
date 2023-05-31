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

from http import HTTPStatus

from flask import Blueprint
from flask import g, current_app, jsonify, request
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils

from mhr_api.utils.auth import jwt
from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.services.authz import authorized, authorized_role, is_staff, is_all_staff_account, REGISTER_MH
from mhr_api.services.authz import is_reg_staff_account, get_group, MANUFACTURER_GROUP
from mhr_api.models import MhrRegistration, MhrManufacturer, registration_utils as model_reg_utils
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

        params: AccountRegistrationParams = AccountRegistrationParams(account_id=account_id,
                                                                      collapse=collapse_param,
                                                                      sbc_staff=is_staff(jwt))
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
            registration = MhrRegistration.find_by_mhr_number(mhr_number,
                                                              account_id,
                                                              is_all_staff_account(account_id))
            registration.current_view = True
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
def get_batch_manufacturer_registrations():  # pylint: disable=too-many-return-statements, too-many-branches
    """Get batch manufacturer registrations report for ."""
    try:
        current_app.logger.info('getting batch manufacturer registrations')
        # Authenticate with request api key
        if not resource_utils.valid_api_key(request):
            return resource_utils.unauthorized_error_response('batch manufacturer registrations report')
        start_ts: str = request.args.get(model_reg_utils.START_TS_PARAM, None)
        end_ts: str = request.args.get(model_reg_utils.END_TS_PARAM, None)
        if start_ts and end_ts:
            start_ts = resource_utils.remove_quotes(start_ts)
            end_ts = resource_utils.remove_quotes(end_ts)
            current_app.logger.debug(f'Using request timestamp range {start_ts} to {end_ts}')
        registrations = model_reg_utils.get_batch_manufacturer_reg_report_data(start_ts, end_ts)
        if not registrations:
            current_app.logger.debug(f'No manufacturer registrations found for timestamp range {start_ts} to {end_ts}')
            return '', HTTPStatus.NO_CONTENT
        # Generate individual registration reports with a cover letter
        reports = []
        for reg in registrations:
            raw_data, status_code, headers = get_callback_pdf(reg.get('reportData'),
                                                              reg.get('accountId'),
                                                              ReportTypes.MHR_REGISTRATION_STAFF,
                                                              None,
                                                              None)
            if status_code in (HTTPStatus.OK, HTTPStatus.CREATED):
                reports.append(raw_data)
            else:
                current_app.logger.error(str(reg.get('registrationId')) + ' report api call failed: ' +
                                         raw_data.get_data(as_text=True))
        if reports and len(reports) > 1:
            raw_data, status_code, headers = Report.batch_merge(reports)
        if status_code not in (HTTPStatus.OK, HTTPStatus.CREATED):
            current_app.logger.error('Batch manufacturer report merge call failed: ' + raw_data.get_data(as_text=True))
            return raw_data, status_code, headers
        batch_storage_url = model_reg_utils.get_batch_storage_name_manufacturer_mhreg()
        current_app.logger.info(f'Saving batch manufacturer registration report to: {batch_storage_url}.')
        GoogleStorageService.save_document(batch_storage_url, raw_data, DocumentTypes.BATCH_REGISTRATION)
        model_reg_utils.update_reg_report_batch_url(registrations, batch_storage_url)
        return raw_data, HTTPStatus.OK, headers
    except ReportException as report_err:
        return resource_utils.service_exception_response('Batch manufacturer report API error: ' + str(report_err))
    except ReportDataException as report_data_err:
        return resource_utils.service_exception_response('Batch manufacturerreport API data error: ' +
                                                         str(report_data_err))
    except StorageException as storage_err:
        return resource_utils.service_exception_response('Batch manufacturer report storage API error: ' +
                                                         str(storage_err))
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, None, 'Batch manufacturer report error')
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)
