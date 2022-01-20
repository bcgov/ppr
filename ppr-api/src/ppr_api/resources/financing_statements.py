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
"""API endpoints for maintaining financing statements and updates to financing statements."""

# pylint: disable=too-many-return-statements, too-many-lines
from http import HTTPStatus

from flask import jsonify, request, current_app, g
from flask_restx import Namespace, Resource, cors
from registry_schemas import utils as schema_utils

from ppr_api.exceptions import BusinessException, DatabaseException
from ppr_api.models import AccountBcolId, EventTracking, FinancingStatement, Party, Registration, UserExtraRegistration
from ppr_api.models import utils as model_utils
from ppr_api.reports import ReportTypes, get_pdf, get_report_api_payload
from ppr_api.resources import utils as resource_utils
from ppr_api.services.authz import authorized, is_reg_staff_account, is_sbc_office_account, \
                                   is_staff_account, is_bcol_help, is_all_staff_account
from ppr_api.services.payment import TransactionTypes
from ppr_api.services.payment.exceptions import SBCPaymentException
from ppr_api.services.payment.payment import Payment
from ppr_api.utils.auth import jwt
from ppr_api.utils.util import cors_preflight
from ppr_api.callback.utils.exceptions import ReportDataException


API = Namespace('financing-statements', description='Endpoints for maintaining financing statements and updates.')

VAL_ERROR = 'Financing Statement request data validation errors.'  # Default validation error prefix
VAL_ERROR_AMEND = 'Amendment Statement request data validation errors.'  # Amendment validation error prefix
VAL_ERROR_CHANGE = 'Change Statement request data validation errors.'  # Change validation error prefix
VAL_ERROR_RENEWAL = 'Renewal Statement request data validation errors.'  # Renewal validation error prefix
VAL_ERROR_DISCHARGE = 'Discharge Statement request data validation errors.'  # Discharge validation error prefix
SAVE_ERROR_MESSAGE = 'Account {0} create {1} statement db save failed: {2}'
PAY_REFUND_MESSAGE = 'Account {0} create {1} statement refunding payment for invoice {2}.'
PAY_REFUND_ERROR = 'Account {0} create {1} statement payment refund failed for invoice {2}: {3}.'
DUPLICATE_REGISTRATION_ERROR = 'Registration {0} is already available to the account.'
# Payment detail/transaction description by registration.
REG_CLASS_TO_STATEMENT_TYPE = {
    'AMENDMENT': 'Register an Amendment Statement',
    'COURTORDER': 'Register an Amendment Statement',
    'CHANGE': 'Register a Change Statement',
    'RENEWAL': 'Register a Renewal Statement',
    'DISCHARGE': 'Register a Discharge Statement'
}
COLLAPSE_PARAM = 'collapse'
CURRENT_PARAM = 'current'
CALLBACK_MESSAGES = {
    resource_utils.CallbackExceptionCodes.UNKNOWN_ID: '01: no registration data found for id={key_id}.',
    resource_utils.CallbackExceptionCodes.MAX_RETRIES: '02: maximum retries reached for id={key_id}.',
    resource_utils.CallbackExceptionCodes.INVALID_ID: '03: no registration found for id={key_id}.',
    resource_utils.CallbackExceptionCodes.DEFAULT: '04: default error for id={key_id}.',
    resource_utils.CallbackExceptionCodes.REPORT_DATA_ERR: '05: report data error for id={key_id}.',
    resource_utils.CallbackExceptionCodes.REPORT_ERR: '06: generate report failed for id={key_id}.',
    resource_utils.CallbackExceptionCodes.FILE_TRANSFER_ERR: '09: SFTP failed for id={key_id}.',
    resource_utils.CallbackExceptionCodes.SETUP_ERR: '10: setup failed for id={key_id}.'
}


@cors_preflight('GET,POST,OPTIONS')
@API.route('', methods=['GET', 'POST', 'OPTIONS'])
class FinancingResource(Resource):
    """Resource for maintaining Financing Statements."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def get():
        """Get the list of financing statements created by the header account ID."""
        try:
            # Quick check: must provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()
            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)
            # Try to fetch financing statement list for account ID
            try:
                statement_list = FinancingStatement.find_all_by_account_id(account_id)
                return jsonify(statement_list), HTTPStatus.OK
            except Exception as db_exception:   # noqa: B902; return nicer default error
                return resource_utils.db_exception_response(db_exception, account_id, 'GET financing statements')
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def post():
        """Create a new financing statement."""
        try:
            # Quick check: must be staff or provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()
            # Verify request JWT and account ID. BCOL helpdesk is not allowed to submit this request.
            if not authorized(account_id, jwt) or is_bcol_help(account_id):
                return resource_utils.unauthorized_error_response(account_id)
            request_json = request.get_json(silent=True)
            # Validate request data against the schema.
            valid_format, errors = schema_utils.validate(request_json, 'financingStatement', 'ppr')
            extra_validation_msg = resource_utils.validate_financing(request_json)
            if not valid_format or extra_validation_msg != '':
                return resource_utils.validation_error_response(errors, VAL_ERROR, extra_validation_msg)
            # Set up the financing statement registration, pay, and save the data.
            statement = pay_and_save_financing(request, request_json, account_id)
            if resource_utils.is_pdf(request):
                # Return report if request header Accept MIME type is application/pdf.
                return get_pdf(statement.json, account_id, ReportTypes.FINANCING_STATEMENT_REPORT.value,
                               jwt.get_token_auth_header())
            return statement.json, HTTPStatus.CREATED
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, account_id, 'POST financing statement')
        except SBCPaymentException as pay_exception:
            return resource_utils.pay_exception_response(pay_exception, account_id)
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('GET,OPTIONS')
@API.route('/<path:registration_num>', methods=['GET', 'OPTIONS'])
class GetFinancingResource(Resource):
    """Resource to get an individual financing statement by registration number."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def get(registration_num):
        """Get a financing statement by registration number."""
        try:
            if registration_num is None:
                return resource_utils.path_param_error_response('registration number')
            # Quick check: must be staff or provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()
            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)
            # Try to fetch financing statement by registration number
            # Not found throws a business exception.
            statement = FinancingStatement.find_by_registration_number(registration_num,
                                                                       account_id,
                                                                       is_all_staff_account(account_id))
            # Extra check account name matches either registering party or a secured party name.
            if resource_utils.is_pdf(request):
                resource_utils.check_access_financing(jwt.get_token_auth_header(),
                                                      is_all_staff_account(account_id), account_id, statement)
            # Set to false to exclude change history.
            statement.include_changes_json = False
            # Set to false as default to generate json with original financing statement data.
            current_param = request.args.get(CURRENT_PARAM)
            if current_param is None or not isinstance(current_param, (bool, str)):
                statement.current_view_json = False
            elif isinstance(current_param, str) and current_param.lower() in ['true', '1', 'y', 'yes']:
                statement.current_view_json = True
            elif isinstance(current_param, str):
                statement.current_view_json = False
            else:
                statement.current_view_json = current_param
            if resource_utils.is_pdf(request):
                # Return report if request header Accept MIME type is application/pdf.
                return get_pdf(statement.json, account_id, ReportTypes.FINANCING_STATEMENT_REPORT.value,
                               jwt.get_token_auth_header())
            return statement.json, HTTPStatus.OK
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, account_id,
                                                        'GET financing statement id=' + registration_num)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('POST,OPTIONS')
@API.route('/<path:registration_num>/amendments', methods=['POST', 'OPTIONS'])
class AmendmentResource(Resource):
    """Resource to register an amendment statement by registration number."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def post(registration_num):
        """Amend a financing statement by registration number."""
        try:
            if registration_num is None:
                return resource_utils.path_param_error_response('registration number')
            # Quick check: must be staff or provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()
            # Verify request JWT and account ID. BCOL helpdesk is not allowed to submit this request.
            if not authorized(account_id, jwt) or is_bcol_help(account_id):
                return resource_utils.unauthorized_error_response(account_id)
            request_json = request.get_json(silent=True)
            # Validate request data against the schema.
            valid_format, errors = schema_utils.validate(request_json, 'amendmentStatement', 'ppr')
            extra_validation_msg = resource_utils.validate_registration(request_json)
            if not valid_format or extra_validation_msg != '':
                return resource_utils.validation_error_response(errors, VAL_ERROR, extra_validation_msg)
            # payload base registration number must match path registration number
            if registration_num != request_json['baseRegistrationNumber']:
                return resource_utils.path_data_mismatch_error_response(registration_num,
                                                                        'base registration number',
                                                                        request_json['baseRegistrationNumber'])
            # Fetch base registration information: business exception thrown if not
            # found or historical.
            statement = FinancingStatement.find_by_registration_number(registration_num, account_id,
                                                                       is_staff_account(account_id), True)
            # Verify base debtor (bypassed for staff)
            if not statement.validate_debtor_name(request_json['debtorName'], is_staff_account(account_id)):
                return resource_utils.base_debtor_invalid_response()
            # Verify delete party and collateral ID's
            resource_utils.validate_delete_ids(request_json, statement)
            # Set up the registration, pay, and save the data.
            registration = pay_and_save(request,
                                        request_json,
                                        model_utils.REG_CLASS_AMEND,
                                        statement,
                                        registration_num,
                                        account_id)
            response_json = registration.verification_json('amendmentRegistrationNumber')
            # If get to here request was successful, enqueue verification statements for secured parties.
            resource_utils.queue_secured_party_verification(registration)
            if resource_utils.is_pdf(request):
                # Return report if request header Accept MIME type is application/pdf.
                return get_pdf(response_json,
                               account_id,
                               ReportTypes.FINANCING_STATEMENT_REPORT.value,
                               jwt.get_token_auth_header())
            return response_json, HTTPStatus.CREATED
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, account_id,
                                                        'POST Amendment id=' + registration_num)
        except SBCPaymentException as pay_exception:
            return resource_utils.pay_exception_response(pay_exception, account_id)
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('GET,OPTIONS')
@API.route('/<path:registration_num>/amendments/<path:amendment_registration_num>', methods=['GET', 'OPTIONS'])
class GetAmendmentResource(Resource):
    """Resource to get an individual amendment registration statement by registration number."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def get(registration_num, amendment_registration_num):
        """Get an amendment registration statement by registration number."""
        try:
            if amendment_registration_num is None:
                return resource_utils.path_param_error_response('amendment registration number')
            # Quick check: must be staff or provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()
            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)
            # Try to fetch registration statement by registration number
            statement = Registration.find_by_registration_number(amendment_registration_num,
                                                                 account_id,
                                                                 is_all_staff_account(account_id),
                                                                 registration_num)
            # If requesting a verification statement report, check the account name matches either
            # the registering party or a secured party name.
            if resource_utils.is_pdf(request):
                resource_utils.check_access_registration(jwt.get_token_auth_header(),
                                                         is_all_staff_account(account_id), account_id,
                                                         statement)
            response_json = statement.verification_json('amendmentRegistrationNumber')
            if resource_utils.is_pdf(request):
                # Return report if request header Accept MIME type is application/pdf.
                return get_pdf(response_json, account_id, ReportTypes.FINANCING_STATEMENT_REPORT.value,
                               jwt.get_token_auth_header())
            return response_json, HTTPStatus.OK
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, account_id,
                                                        'GET Amendment id=' + amendment_registration_num)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('GET,OPTIONS')
@API.route('/<path:registration_num>/changes/<path:change_registration_num>', methods=['GET', 'OPTIONS'])
class GetChangeResource(Resource):
    """Resource to get an individual change registration statement by registration number."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def get(registration_num, change_registration_num):
        """Get a change registration statement by registration number."""
        try:
            if change_registration_num is None:
                return resource_utils.path_param_error_response('change registration number')
            # Quick check: must be staff or provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()
            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)
            # Try to fetch registration statement by registration number
            statement = Registration.find_by_registration_number(change_registration_num,
                                                                 account_id,
                                                                 is_all_staff_account(account_id),
                                                                 registration_num)
            # If requesting a verification statement report, check the account name matches either
            # the registering party or a secured party name.
            if resource_utils.is_pdf(request):
                resource_utils.check_access_registration(jwt.get_token_auth_header(),
                                                         is_all_staff_account(account_id), account_id,
                                                         statement)
            response_json = statement.verification_json('changeRegistrationNumber')
            if resource_utils.is_pdf(request):
                # Return report if request header Accept MIME type is application/pdf.
                return get_pdf(response_json, account_id, ReportTypes.FINANCING_STATEMENT_REPORT.value,
                               jwt.get_token_auth_header())
            return response_json, HTTPStatus.OK
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, account_id,
                                                        'GET Change id=' + change_registration_num)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('POST,OPTIONS')
@API.route('/<path:registration_num>/renewals', methods=['POST', 'OPTIONS'])
class RenewalResource(Resource):
    """Resource to register an renewal statement by registration number."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def post(registration_num):
        """Renew a financing statement by registration number."""
        try:
            if registration_num is None:
                return resource_utils.path_param_error_response('registration number')
            # Quick check: must be staff or provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()
            # Verify request JWT and account ID. BCOL helpdesk is not allowed to submit this request.
            if not authorized(account_id, jwt) or is_bcol_help(account_id):
                return resource_utils.unauthorized_error_response(account_id)
            request_json = request.get_json(silent=True)
            # Validate request data against the schema.
            valid_format, errors = schema_utils.validate(request_json, 'renewalStatement', 'ppr')
            if not valid_format:
                return resource_utils.validation_error_response(errors, VAL_ERROR)
            # payload base registration number must match path registration number
            if registration_num != request_json['baseRegistrationNumber']:
                return resource_utils.path_data_mismatch_error_response(registration_num,
                                                                        'base registration number',
                                                                        request_json['baseRegistrationNumber'])
            # Fetch base registration information: business exception thrown if not
            # found or historical.
            statement = FinancingStatement.find_by_registration_number(registration_num, account_id,
                                                                       is_staff_account(account_id), True)
            extra_validation_msg = resource_utils.validate_renewal(request_json, statement)
            if extra_validation_msg != '':
                return resource_utils.validation_error_response(errors, VAL_ERROR, extra_validation_msg)
            # Verify base debtor (bypassed for staff)
            if not statement.validate_debtor_name(request_json['debtorName'], is_staff_account(account_id)):
                return resource_utils.base_debtor_invalid_response()
            # Set up the registration, pay, and save the data.
            registration = pay_and_save(request,
                                        request_json,
                                        model_utils.REG_CLASS_RENEWAL,
                                        statement,
                                        registration_num,
                                        account_id)
            response_json = registration.verification_json('renewalRegistrationNumber')
            if resource_utils.is_pdf(request):
                # Return report if request header Accept MIME type is application/pdf.
                return get_pdf(response_json, account_id, ReportTypes.FINANCING_STATEMENT_REPORT.value,
                               jwt.get_token_auth_header())
            return response_json, HTTPStatus.CREATED
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, account_id,
                                                        'POST Renewal id=' + registration_num)
        except SBCPaymentException as pay_exception:
            return resource_utils.pay_exception_response(pay_exception, account_id)
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('GET,OPTIONS')
@API.route('/<path:registration_num>/renewals/<path:renewal_registration_num>', methods=['GET', 'OPTIONS'])
class GetRenewalResource(Resource):
    """Resource to get an individual renewal registration statement by registration number."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def get(registration_num, renewal_registration_num):
        """Get a renewal registration statement by registration number."""
        try:
            if renewal_registration_num is None:
                return resource_utils.path_param_error_response('renewal registration number')
            # Quick check: must be staff or provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()
            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)
            # Try to fetch registration statement by registration number
            statement = Registration.find_by_registration_number(renewal_registration_num,
                                                                 account_id,
                                                                 is_all_staff_account(account_id),
                                                                 registration_num)
            # If requesting a verification statement report, check the account name matches either
            # the registering party or a secured party name.
            if resource_utils.is_pdf(request):
                resource_utils.check_access_registration(jwt.get_token_auth_header(),
                                                         is_all_staff_account(account_id), account_id,
                                                         statement)
            response_json = statement.verification_json('renewalRegistrationNumber')
            if resource_utils.is_pdf(request):
                # Return report if request header Accept MIME type is application/pdf.
                return get_pdf(response_json, account_id, ReportTypes.FINANCING_STATEMENT_REPORT.value,
                               jwt.get_token_auth_header())
            return response_json, HTTPStatus.OK
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, account_id,
                                                        'GET Renewal id=' + renewal_registration_num)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('POST,OPTIONS')
@API.route('/<path:registration_num>/discharges', methods=['POST', 'OPTIONS'])
class DischargeResource(Resource):
    """Resource to discharge an individual financing statement by registration number."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def post(registration_num):
        """Discharge a financing statement by registration number."""
        try:
            if registration_num is None:
                return resource_utils.path_param_error_response('registration number')
            # Quick check: must be staff or provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()
            # Verify request JWT and account ID. BCOL helpdesk is not allowed to submit this request.
            if not authorized(account_id, jwt) or is_bcol_help(account_id):
                return resource_utils.unauthorized_error_response(account_id)
            request_json = request.get_json(silent=True)
            # Validate request data against the schema.
            valid_format, errors = schema_utils.validate(request_json, 'dischargeStatement', 'ppr')
            extra_validation_msg = resource_utils.validate_registration(request_json)
            if not valid_format or extra_validation_msg != '':
                return resource_utils.validation_error_response(errors, VAL_ERROR, extra_validation_msg)
            # payload base registration number must match path registration number
            if registration_num != request_json['baseRegistrationNumber']:
                return resource_utils.path_data_mismatch_error_response(registration_num,
                                                                        'base registration number',
                                                                        request_json['baseRegistrationNumber'])
            # Fetch base registration information: business exception thrown if not
            # found or historical.
            statement = FinancingStatement.find_by_registration_number(registration_num, account_id,
                                                                       is_staff_account(account_id), True)
            # Verify base debtor (bypassed for staff)
            if not statement.validate_debtor_name(request_json['debtorName'], is_staff_account(account_id)):
                return resource_utils.base_debtor_invalid_response()
            # No fee for a discharge but create a payment transaction record.
            # Set up the registration, pay, and save the data.
            registration = pay_and_save(request,
                                        request_json,
                                        model_utils.REG_CLASS_DISCHARGE,
                                        statement,
                                        registration_num,
                                        account_id)
            response_json = registration.verification_json('dischargeRegistrationNumber')
            # If get to here request was successful, enqueue verification statements for secured parties.
            resource_utils.queue_secured_party_verification(registration)
            if resource_utils.is_pdf(request):
                # Return report if request header Accept MIME type is application/pdf.
                return get_pdf(response_json,
                               account_id,
                               ReportTypes.FINANCING_STATEMENT_REPORT.value,
                               jwt.get_token_auth_header())
            return response_json, HTTPStatus.CREATED
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, account_id,
                                                        'POST Discharge id=' + registration_num)
        except SBCPaymentException as pay_exception:
            return resource_utils.pay_exception_response(pay_exception, account_id)
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('GET,OPTIONS')
@API.route('/<path:registration_num>/discharges/<path:discharge_registration_num>', methods=['GET', 'OPTIONS'])
class GetDischargeResource(Resource):
    """Resource to get an individual discharge registration statement by registration number."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def get(registration_num, discharge_registration_num):
        """Get a discharge registration statement by registration number."""
        try:
            if discharge_registration_num is None:
                return resource_utils.path_param_error_response('discharge registration number')
            # Quick check: must be staff or provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()
            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)
            # Try to fetch registration statement by registration number
            statement = Registration.find_by_registration_number(discharge_registration_num,
                                                                 account_id,
                                                                 is_all_staff_account(account_id),
                                                                 registration_num)
            # If requesting a verification statement report, check the account name matches either
            # the registering party or a secured party name.
            if resource_utils.is_pdf(request):
                resource_utils.check_access_registration(jwt.get_token_auth_header(),
                                                         is_all_staff_account(account_id), account_id,
                                                         statement)
            response_json = statement.verification_json('dischargeRegistrationNumber')
            if resource_utils.is_pdf(request):
                # Return report if request header Accept MIME type is application/pdf.
                return get_pdf(response_json,
                               account_id,
                               ReportTypes.FINANCING_STATEMENT_REPORT.value,
                               jwt.get_token_auth_header())
            return response_json, HTTPStatus.OK
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, account_id,
                                                        'GET Discharge id=' + discharge_registration_num)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('GET,OPTIONS')
@API.route('/<path:registration_num>/debtorNames', methods=['GET', 'OPTIONS'])
class GetDebtorNamesResource(Resource):
    """Resource to get debtor names for a financing statement identified by the registration number."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def get(registration_num,):
        """Get financing statement debtor names by registration number."""
        try:
            if registration_num is None:
                return resource_utils.path_param_error_response('base registration number')
            # Quick check: must be staff or provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()
            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)
            # Try to fetch financing statement list for account ID
            names_list = FinancingStatement.find_debtor_names_by_registration_number(registration_num)
            return jsonify(names_list), HTTPStatus.OK
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, account_id,
                                                        'GET Debtor Names id=' + registration_num)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('GET,OPTIONS')
@API.route('/registrations', methods=['GET', 'OPTIONS'])
class GetRegistrationResource(Resource):
    """Resource to get a summary list of recent registrations by account ID."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def get():
        """Get the list of recent registrations created by the header account ID."""
        try:
            # Quick check: must provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()
            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)
            collapse_param = request.args.get(COLLAPSE_PARAM)
            if collapse_param is None or not isinstance(collapse_param, (bool, str)):
                collapse_param = False
            elif isinstance(collapse_param, str) and collapse_param.lower() in ['true', '1', 'y', 'yes']:
                collapse_param = True
            elif isinstance(collapse_param, str):
                collapse_param = False
            # Try to fetch financing statement list for account ID
            # To access a registration report, use the account name to match on registering/secured parties.
            account_name = resource_utils.get_account_name(jwt.get_token_auth_header(), account_id)
            sbc_staff: bool = is_sbc_office_account(jwt.get_token_auth_header(), account_id)
            statement_list = Registration.find_all_by_account_id(account_id,
                                                                 collapse_param,
                                                                 account_name,
                                                                 sbc_staff)
            return jsonify(statement_list), HTTPStatus.OK
        except DatabaseException as db_exception:   # noqa: B902; return nicer error
            return resource_utils.db_exception_response(db_exception, account_id,
                                                        'GET Account Registration Summary id=' + account_id)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('DELETE,GET,POST,OPTIONS')
@API.route('/registrations/<path:registration_num>', methods=['DELETE', 'GET', 'POST', 'OPTIONS'])
class AccountRegistrationResource(Resource):
    """Resource to maintain user account additional Financing Statements by registration number."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def post(registration_num):
        """Add a financing statement by registration number to the user registrations list."""
        try:
            if registration_num is None:
                return resource_utils.path_param_error_response('registration number')
            # Quick check: must provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()
            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)
            # Try to fetch summary registration by registration number
            account_name = resource_utils.get_account_name(jwt.get_token_auth_header(), account_id)
            sbc_staff: bool = is_sbc_office_account(jwt.get_token_auth_header(), account_id)
            registration = Registration.find_summary_by_reg_num(account_id, registration_num, account_name, sbc_staff)
            if registration is None:
                return resource_utils.not_found_error_response('Financing Statement registration', registration_num)
            # Save the base registration: request may be a change registration number.
            base_reg_num = registration['baseRegistrationNumber']
            # Check if registration was created by the account and deleted. If so, restore it.
            if registration['accountId'] == account_id and registration['existsCount'] > 0:
                UserExtraRegistration.delete(base_reg_num, account_id)
            # Check if duplicate.
            elif registration['accountId'] == account_id or registration['existsCount'] > 0:
                return resource_utils.duplicate_error_response(DUPLICATE_REGISTRATION_ERROR.format(registration_num))
            # Restricted access check for crown charge class of registration types.
            if not is_all_staff_account(account_id) and \
                    registration['registrationClass'] == model_utils.REG_CLASS_CROWN and \
                    not AccountBcolId.crown_charge_account(account_id):
                return resource_utils.cc_forbidden_error_response(account_id)
            if registration['accountId'] != account_id:
                extra_registration = UserExtraRegistration(account_id=account_id, registration_number=base_reg_num)
                extra_registration.save()
            del registration['accountId']
            del registration['existsCount']
            if 'inUserList' in registration:
                del registration['inUserList']
            return registration, HTTPStatus.CREATED
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, account_id,
                                                        'POST Extra Registration id=' + registration_num)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def get(registration_num):
        """Get summary registration information by registration number before adding to the user registrations list."""
        try:
            if registration_num is None:
                return resource_utils.path_param_error_response('registration number')
            # Quick check: must provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()
            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)
            # Try to fetch summary registration by registration number
            account_name = resource_utils.get_account_name(jwt.get_token_auth_header(), account_id)
            sbc_staff: bool = is_sbc_office_account(jwt.get_token_auth_header(), account_id)
            registration = Registration.find_summary_by_reg_num(account_id, registration_num, account_name, sbc_staff)
            if registration is None:
                return resource_utils.not_found_error_response('Financing Statement registration', registration_num)
            # Restricted access check for crown charge class of registration types.
            if not is_all_staff_account(account_id) and \
                    registration['registrationClass'] == model_utils.REG_CLASS_CROWN and \
                    not AccountBcolId.crown_charge_account(account_id):
                return resource_utils.cc_forbidden_error_response(account_id)
            del registration['accountId']
            del registration['existsCount']
            return registration, HTTPStatus.OK
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, account_id,
                                                        'GET Registration Summary id=' + registration_num)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def delete(registration_num):
        """Delete a financing statement by registration number from the user registrations list."""
        try:
            if registration_num is None:
                return resource_utils.path_param_error_response('registration number')
            # Quick check: must provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()
            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)
            # Try and get existing record
            account_name = resource_utils.get_account_name(jwt.get_token_auth_header(), account_id)
            registration = Registration.find_summary_by_reg_num(account_id, registration_num, account_name)
            extra_registration = UserExtraRegistration.find_by_registration_number(registration_num, account_id)
            if extra_registration is None and registration is None:
                return resource_utils.not_found_error_response('user account registration', registration_num)
            # Remove another account's financing statement registration.
            if extra_registration and not extra_registration.removed_ind:
                UserExtraRegistration.delete(registration_num, account_id)
            # Mark the user account's financing statement registration as removed
            elif not extra_registration and registration['accountId'] == account_id:
                extra_registration = UserExtraRegistration(account_id=account_id, registration_number=registration_num)
                extra_registration.removed_ind = UserExtraRegistration.REMOVE_IND
                extra_registration.save()
            return '', HTTPStatus.NO_CONTENT
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, account_id,
                                                        'DELETE Extra Registration id=' + registration_num)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('POST,OPTIONS')
@API.route('/verification-callback', methods=['POST', 'OPTIONS'])
class VerificationResource(Resource):
    """Resource to handle a verification report mail request for a callback event."""

    @staticmethod
    @cors.crossdomain(origin='*')
    def post():
        """Get report data including cover letter for mailing a verification report."""
        request_json = request.get_json(silent=True)
        registration_id: int = request_json.get('registrationId', -1)
        party_id: int = request_json.get('partyId', -1)
        try:
            if registration_id < 0:
                return resource_utils.error_response(HTTPStatus.BAD_REQUEST,
                                                     'Mail verification statement no registration ID.')
            if party_id < 0:
                return callback_error(resource_utils.CallbackExceptionCodes.SETUP_ERR, registration_id,
                                      HTTPStatus.BAD_REQUEST, party_id,
                                      'No required partyId in message payload.')
            # If exceeded max retries we're done.
            event_count: int = 0
            events = EventTracking.find_by_key_id_type(registration_id,
                                                       EventTracking.EventTrackingTypes.SURFACE_MAIL,
                                                       str(party_id))
            if events:
                event_count = len(events)
            if event_count > current_app.config.get('EVENT_MAX_RETRIES'):
                return callback_error(resource_utils.CallbackExceptionCodes.MAX_RETRIES, registration_id,
                                      HTTPStatus.INTERNAL_SERVER_ERROR, party_id,
                                      f'Max retries reached for party={party_id}.')
            registration = Registration.find_by_id(registration_id)
            if not registration:
                return callback_error(resource_utils.CallbackExceptionCodes.UNKNOWN_ID, registration_id,
                                      HTTPStatus.NOT_FOUND, party_id)
            # Verify party ID.
            party = resource_utils.find_secured_party(registration, party_id)
            if not party:
                return callback_error(resource_utils.CallbackExceptionCodes.UNKNOWN_ID, registration_id,
                                      HTTPStatus.NOT_FOUND, party_id,
                                      f'No party found for id={party_id}')
            # Generate the verification json data with the cover letter info for the secured party.
            json_data = get_mail_verification_data(registration_id, registration, party)
            report_data = get_verification_report_data(registration_id, json_data, registration.account_id, None)
            current_app.logger.info(f'Generated the mail report data for id={registration_id}, party={party_id}')
            return jsonify(report_data), HTTPStatus.CREATED

        except ReportDataException as report_data_err:
            return callback_error(resource_utils.CallbackExceptionCodes.REPORT_DATA_ERR,
                                  registration_id,
                                  HTTPStatus.INTERNAL_SERVER_ERROR, party_id,
                                  f'Party={party_id}. ' + repr(report_data_err))
        except Exception as default_err:  # noqa: B902; return nicer default error
            return callback_error(resource_utils.CallbackExceptionCodes.DEFAULT,
                                  registration_id,
                                  HTTPStatus.INTERNAL_SERVER_ERROR, party_id,
                                  f'Party={party_id}. ' + repr(default_err))


def pay_and_save(req: request,  # pylint: disable=too-many-arguments,too-many-locals,too-many-branches
                 request_json, registration_class, financing_statement, registration_num, account_id):
    """Set up the registration, pay if there is an account id, and save the data."""
    token: dict = g.jwt_oidc_token_info
    registration = Registration.create_from_json(request_json,
                                                 registration_class,
                                                 financing_statement,
                                                 registration_num,
                                                 account_id)
    registration.user_id = token.get('username', None)
    pay_trans_type = TransactionTypes.CHANGE.value
    fee_quantity = 1
    pay_ref = None
    if registration_class == model_utils.REG_CLASS_AMEND:
        pay_trans_type = TransactionTypes.AMENDMENT.value
        if resource_utils.no_fee_amendment(financing_statement.registration[0].registration_type):
            pay_trans_type = TransactionTypes.AMENDMENT_NO_FEE.value
    elif registration_class == model_utils.REG_CLASS_RENEWAL and registration.life == model_utils.LIFE_INFINITE:
        pay_trans_type = TransactionTypes.RENEWAL_INFINITE.value
    elif registration_class == model_utils.REG_CLASS_RENEWAL:
        fee_quantity = registration.life
        pay_trans_type = TransactionTypes.RENEWAL_LIFE_YEAR.value
    elif registration_class == model_utils.REG_CLASS_DISCHARGE:
        pay_trans_type = TransactionTypes.DISCHARGE.value
    processing_fee = None
    is_dicharge = pay_trans_type == TransactionTypes.DISCHARGE.value
    if not is_reg_staff_account(account_id):
        # if sbc staff and not 'no fee' then add processing fee
        if not is_dicharge and is_sbc_office_account(jwt.get_token_auth_header(), account_id):
            processing_fee = TransactionTypes.CHANGE_STAFF_PROCESS_FEE.value
        pay_account_id: str = account_id
        payment = Payment(jwt=jwt.get_token_auth_header(),
                          account_id=pay_account_id,
                          details=resource_utils.get_payment_details(registration))
        pay_ref = payment.create_payment(
            pay_trans_type, fee_quantity, None, registration.client_reference_id, processing_fee)
    else:
        # if not discharge add process fee
        if not is_dicharge:
            processing_fee = TransactionTypes.CHANGE_STAFF_PROCESS_FEE.value
        payment_info = resource_utils.build_staff_registration_payment(req, pay_trans_type, fee_quantity)
        payment = Payment(jwt=jwt.get_token_auth_header(),
                          account_id=None,
                          details=resource_utils.get_payment_details(registration))
        pay_ref = payment.create_payment_staff_registration(
            payment_info, registration.client_reference_id, processing_fee)
    invoice_id = pay_ref['invoiceId']
    registration.pay_invoice_id = int(invoice_id)
    registration.pay_path = pay_ref['receipt']
    # Try to save the registration: failure will rollback the payment if one was made.
    try:
        registration.save()
    except BusinessException as bus_exception:
        # just pass it along
        raise bus_exception
    except Exception as db_exception:   # noqa: B902; handle all db related errors.
        current_app.logger.error(SAVE_ERROR_MESSAGE.format(account_id, registration_class, repr(db_exception)))
        if account_id and invoice_id is not None:
            current_app.logger.info(PAY_REFUND_MESSAGE.format(account_id, registration_class, invoice_id))
            try:
                payment = Payment(jwt=jwt.get_token_auth_header(), account_id=account_id)
                payment.cancel_payment(invoice_id)
            except SBCPaymentException as cancel_exception:
                current_app.logger.error(PAY_REFUND_ERROR.format(account_id, registration_class, invoice_id,
                                                                 repr(cancel_exception)))
        raise DatabaseException(db_exception)
    return registration


def pay_and_save_financing(req: request, request_json, account_id):  # pylint: disable=too-many-locals
    """Set up the financing statement, pay if there is an account id, and save the data."""
    # Charge a fee.
    token: dict = g.jwt_oidc_token_info
    statement = FinancingStatement.create_from_json(request_json, account_id, token.get('username', None))
    invoice_id = None
    registration = statement.registration[0]
    pay_trans_type, fee_quantity = resource_utils.get_payment_type_financing(registration)
    pay_ref = None
    processing_fee = None
    is_no_fee = pay_trans_type == TransactionTypes.FINANCING_NO_FEE.value
    if not is_reg_staff_account(account_id):
        # if sbc staff and not 'no fee' then add processing fee
        if not is_no_fee and is_sbc_office_account(jwt.get_token_auth_header(), account_id):
            processing_fee = TransactionTypes.FINANCING_STAFF_PROCESS_FEE.value
        pay_account_id: str = account_id
        payment = Payment(jwt=jwt.get_token_auth_header(),
                          account_id=pay_account_id,
                          details=resource_utils.get_payment_details_financing(registration))
        pay_ref = payment.create_payment(
            pay_trans_type, fee_quantity, None, registration.client_reference_id, processing_fee)
    else:
        # if not 'no fee' then add processing fee
        if not is_no_fee:
            processing_fee = TransactionTypes.FINANCING_STAFF_PROCESS_FEE.value
        payment_info = resource_utils.build_staff_registration_payment(req, pay_trans_type, fee_quantity)
        payment = Payment(jwt=jwt.get_token_auth_header(),
                          account_id=None,
                          details=resource_utils.get_payment_details_financing(registration))
        pay_ref = payment.create_payment_staff_registration(
            payment_info, registration.client_reference_id, processing_fee)
    invoice_id = pay_ref['invoiceId']
    registration.pay_invoice_id = int(invoice_id)
    registration.pay_path = pay_ref['receipt']
    # Try to save the financing statement: failure throws an exception.
    try:
        statement.save()
    except Exception as db_exception:   # noqa: B902; handle all db related errors.
        current_app.logger.error(SAVE_ERROR_MESSAGE.format(account_id, 'financing', repr(db_exception)))
        if account_id and invoice_id is not None:
            current_app.logger.info(PAY_REFUND_MESSAGE.format(account_id, 'financing', invoice_id))
            try:
                payment.cancel_payment(invoice_id)
            except SBCPaymentException as cancel_exception:
                current_app.logger.error(PAY_REFUND_ERROR.format(account_id, 'financing', invoice_id,
                                                                 repr(cancel_exception)))
        raise DatabaseException(db_exception)
    return statement


def callback_error(code: str, registration_id: int, status_code, party_id: int, message: str = None):
    """Return the event listener callback error response based on the code."""
    error: str = CALLBACK_MESSAGES[code].format(key_id=registration_id)
    if message:
        error += ' ' + message
    # Track event here.
    EventTracking.create(registration_id, EventTracking.EventTrackingTypes.SURFACE_MAIL, status_code, message)
    if status_code != HTTPStatus.BAD_REQUEST and code not in (resource_utils.CallbackExceptionCodes.MAX_RETRIES,
                                                              resource_utils.CallbackExceptionCodes.UNKNOWN_ID,
                                                              resource_utils.CallbackExceptionCodes.SETUP_ERR):
        # set up retry
        resource_utils.enqueue_verification_report(registration_id, party_id)
    return resource_utils.error_response(status_code, error)


def get_mail_verification_data(registration_id: int, registration: Registration, party: Party):
    """Generate json for a surface mail verification statement report."""
    try:
        statement_type = model_utils.REG_CLASS_TO_STATEMENT_TYPE[registration.registration_type_cl]
        reg_num_key = 'dischargeRegistrationNumber'
        if statement_type == model_utils.DRAFT_TYPE_AMENDMENT:
            reg_num_key = 'amendmentRegistrationNumber'
        report_data = registration.verification_json(reg_num_key)
        cover_data = party.json
        cover_data['statementType'] = statement_type
        cover_data['partyType'] = party.party_type
        cover_data['createDateTime'] = report_data['createDateTime']
        cover_data['registrationNumber'] = registration.registration_num
        report_data['cover'] = cover_data
        return report_data
    except Exception as err:  # pylint: disable=broad-except # noqa F841;
        msg = f'Mail verification json data generation failed for id={registration_id}: ' + repr(err)
        # current_app.logger.error(msg)
        raise ReportDataException(msg)


def get_verification_report_data(registration_id: int, json_data, account_id: str, account_name: str = None):
    """Generate report data json for a surface mail verification statement report."""
    try:
        cover_data = get_report_api_payload(json_data, account_id, ReportTypes.COVER_PAGE_REPORT.value, account_name)
        verification_data = get_report_api_payload(json_data,
                                                   account_id,
                                                   ReportTypes.FINANCING_STATEMENT_REPORT.value,
                                                   account_name)
        report_data = {
            'coverLetterData': cover_data,
            'verificationData': verification_data
        }
        return report_data
    except Exception as err:  # pylint: disable=broad-except # noqa F841;
        msg = f'Mail verification report data generation failed for id={registration_id}: ' + repr(err)
        # current_app.logger.error(msg)
        raise ReportDataException(msg)
