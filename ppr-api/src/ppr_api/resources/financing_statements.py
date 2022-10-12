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
# pylint: disable=too-many-return-statements
from http import HTTPStatus

from flask import g, jsonify, request, current_app
from flask_restx import Namespace, Resource, cors
from registry_schemas import utils as schema_utils

from ppr_api.exceptions import BusinessException, DatabaseException
from ppr_api.models import AccountBcolId, EventTracking, FinancingStatement, Registration, User, UserExtraRegistration
from ppr_api.models import utils as model_utils
from ppr_api.models.registration_utils import AccountRegistrationParams
from ppr_api.reports import ReportTypes
from ppr_api.resources import utils as resource_utils, financing_utils as fs_utils
from ppr_api.services.authz import authorized, is_sbc_office_account, \
                                   is_staff_account, is_bcol_help, is_all_staff_account
from ppr_api.services.payment.exceptions import SBCPaymentException
from ppr_api.utils.auth import jwt
from ppr_api.utils.util import cors_preflight
from ppr_api.callback.utils.exceptions import ReportDataException


API = Namespace('financing-statements', description='Endpoints for maintaining financing statements and updates.')


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
                return resource_utils.validation_error_response(errors, fs_utils.VAL_ERROR, extra_validation_msg)
            # Set up the financing statement registration, pay, and save the data.
            statement = fs_utils.pay_and_save_financing(request, request_json, account_id)
            response_json = statement.json
            if resource_utils.is_pdf(request):
                # Return report if request header Accept MIME type is application/pdf.
                return fs_utils.get_registration_report(statement.registration[0], response_json,
                                                        ReportTypes.FINANCING_STATEMENT_REPORT.value,
                                                        jwt.get_token_auth_header(), HTTPStatus.CREATED)
            resource_utils.enqueue_registration_report(statement.registration[0], response_json,
                                                       ReportTypes.FINANCING_STATEMENT_REPORT.value)
            return response_json, HTTPStatus.CREATED
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
            current_param = request.args.get(fs_utils.CURRENT_PARAM)
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
                return fs_utils.get_registration_report(statement.registration[0], statement.json,
                                                        ReportTypes.FINANCING_STATEMENT_REPORT.value,
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
                return resource_utils.validation_error_response(errors, fs_utils.VAL_ERROR, extra_validation_msg)
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
            registration = fs_utils.pay_and_save(request,
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
                return fs_utils.get_registration_report(registration, response_json,
                                                        ReportTypes.FINANCING_STATEMENT_REPORT.value,
                                                        jwt.get_token_auth_header(), HTTPStatus.CREATED)
            resource_utils.enqueue_registration_report(registration, response_json,
                                                       ReportTypes.FINANCING_STATEMENT_REPORT.value)
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
                return fs_utils.get_registration_report(statement, response_json,
                                                        ReportTypes.FINANCING_STATEMENT_REPORT.value,
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
                return fs_utils.get_registration_report(statement, response_json,
                                                        ReportTypes.FINANCING_STATEMENT_REPORT.value,
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
                return resource_utils.validation_error_response(errors, fs_utils.VAL_ERROR)
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
                return resource_utils.validation_error_response(errors, fs_utils.VAL_ERROR, extra_validation_msg)
            # Verify base debtor (bypassed for staff)
            if not statement.validate_debtor_name(request_json['debtorName'], is_staff_account(account_id)):
                return resource_utils.base_debtor_invalid_response()
            # Set up the registration, pay, and save the data.
            registration = fs_utils.pay_and_save(request,
                                                 request_json,
                                                 model_utils.REG_CLASS_RENEWAL,
                                                 statement,
                                                 registration_num,
                                                 account_id)
            response_json = registration.verification_json('renewalRegistrationNumber')
            if resource_utils.is_pdf(request):
                # Return report if request header Accept MIME type is application/pdf.
                return fs_utils.get_registration_report(registration, response_json,
                                                        ReportTypes.FINANCING_STATEMENT_REPORT.value,
                                                        jwt.get_token_auth_header(), HTTPStatus.CREATED)
            resource_utils.enqueue_registration_report(registration, response_json,
                                                       ReportTypes.FINANCING_STATEMENT_REPORT.value)
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
                return fs_utils.get_registration_report(statement, response_json,
                                                        ReportTypes.FINANCING_STATEMENT_REPORT.value,
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
                return resource_utils.validation_error_response(errors, fs_utils.VAL_ERROR, extra_validation_msg)
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
            registration = fs_utils.pay_and_save(request,
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
                return fs_utils.get_registration_report(registration, response_json,
                                                        ReportTypes.FINANCING_STATEMENT_REPORT.value,
                                                        jwt.get_token_auth_header(), HTTPStatus.CREATED)
            resource_utils.enqueue_registration_report(registration, response_json,
                                                       ReportTypes.FINANCING_STATEMENT_REPORT.value)
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
                return fs_utils.get_registration_report(statement, response_json,
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
            # Set feature flag value
            username = 'anonymous'
            user = User.find_by_jwt_token(g.jwt_oidc_token_info, account_id)
            if user and user.username:
                username = user.username
            new_feature_enabled = current_app.extensions['featureflags'].variation(
                'enable-new-feature-api', {'key': username}, False)
            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)
            collapse_param = request.args.get(fs_utils.COLLAPSE_PARAM)
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
            params: AccountRegistrationParams = AccountRegistrationParams(account_id=account_id,
                                                                          collapse=collapse_param,
                                                                          account_name=account_name,
                                                                          sbc_staff=sbc_staff)
            params = resource_utils.get_account_registration_params(request, params)
            statement_list = Registration.find_all_by_account_id(params, new_feature_enabled)
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
                message = fs_utils.DUPLICATE_REGISTRATION_ERROR.format(registration_num)
                return resource_utils.duplicate_error_response(message)
            # Restricted access check for crown charge class of registration types.
            if not is_all_staff_account(account_id) and \
                    registration['registrationClass'] in (model_utils.REG_CLASS_CROWN, model_utils.REG_CLASS_MISC) and \
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
                    registration['registrationClass'] in (model_utils.REG_CLASS_CROWN, model_utils.REG_CLASS_MISC) and \
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
                return fs_utils.callback_error(resource_utils.CallbackExceptionCodes.SETUP_ERR, registration_id,
                                               HTTPStatus.BAD_REQUEST, party_id,
                                               'No required partyId in message payload.')
            # Authenticate with request api key
            if not resource_utils.valid_api_key(request):
                return resource_utils.unauthorized_error_response('Verification report callback')
            # If exceeded max retries we're done.
            event_count: int = 0
            events = EventTracking.find_by_key_id_type(registration_id,
                                                       EventTracking.EventTrackingTypes.SURFACE_MAIL,
                                                       str(party_id))
            if events:
                event_count = len(events)
            if event_count > current_app.config.get('EVENT_MAX_RETRIES'):
                return fs_utils.callback_error(resource_utils.CallbackExceptionCodes.MAX_RETRIES, registration_id,
                                               HTTPStatus.INTERNAL_SERVER_ERROR, party_id,
                                               f'Max retries reached for party={party_id}.')
            registration = Registration.find_by_id(registration_id)
            if not registration:
                return fs_utils.callback_error(resource_utils.CallbackExceptionCodes.UNKNOWN_ID, registration_id,
                                               HTTPStatus.NOT_FOUND, party_id)
            # Verify party ID.
            party = resource_utils.find_secured_party(registration, party_id)
            if not party:
                return fs_utils.callback_error(resource_utils.CallbackExceptionCodes.UNKNOWN_ID, registration_id,
                                               HTTPStatus.NOT_FOUND, party_id,
                                               f'No party found for id={party_id}')
            # Generate the verification json data with the cover letter info for the secured party.
            json_data = fs_utils.get_mail_verification_data(registration_id, registration, party)
            report_data = fs_utils.get_verification_report_data(registration_id, json_data, registration.account_id,
                                                                None)
            current_app.logger.info(f'Generated the mail report data for id={registration_id}, party={party_id}')
            return jsonify(report_data), HTTPStatus.CREATED

        except ReportDataException as report_data_err:
            return fs_utils.callback_error(resource_utils.CallbackExceptionCodes.REPORT_DATA_ERR,
                                           registration_id,
                                           HTTPStatus.INTERNAL_SERVER_ERROR, party_id,
                                           f'Party={party_id}. ' + str(report_data_err))
        except Exception as default_err:  # noqa: B902; return nicer default error
            return fs_utils.callback_error(resource_utils.CallbackExceptionCodes.DEFAULT,
                                           registration_id,
                                           HTTPStatus.INTERNAL_SERVER_ERROR, party_id,
                                           f'Party={party_id}. ' + str(default_err))


@cors_preflight('POST,OPTIONS')
@API.route('/registration-report-callback/<path:registration_id>', methods=['POST', 'OPTIONS'])
class RegistrationReportResource(Resource):
    """Resource to handle a registration report (verification) api request for a callback/aysnchronous event."""

    @staticmethod
    @cors.crossdomain(origin='*')
    def post(registration_id):
        """Generate, store report, record request status and possibly retry."""
        try:
            current_app.logger.info(f'Verification report callback starting id={registration_id}.')
            if registration_id is None:
                return resource_utils.path_param_error_response('registration ID')
            # Authenticate with request api key
            if not resource_utils.valid_api_key(request):
                return resource_utils.unauthorized_error_response('Verification report callback')
            # If exceeded max retries we're done.
            event_count: int = 0
            events = EventTracking.find_by_key_id_type(registration_id,
                                                       EventTracking.EventTrackingTypes.REGISTRATION_REPORT)
            if events:
                event_count = len(events)
            if event_count > current_app.config.get('EVENT_MAX_RETRIES'):
                return fs_utils.registration_callback_error(resource_utils.CallbackExceptionCodes.MAX_RETRIES,
                                                            registration_id,
                                                            HTTPStatus.INTERNAL_SERVER_ERROR,
                                                            'Max retries reached.')
            # Verify the registration ID and request.
            registration: Registration = Registration.find_by_id(registration_id)
            if not registration:
                return fs_utils.registration_callback_error(resource_utils.CallbackExceptionCodes.UNKNOWN_ID,
                                                            registration_id,
                                                            HTTPStatus.NOT_FOUND)
            if not registration.verification_report:
                return fs_utils.registration_callback_error(resource_utils.CallbackExceptionCodes.SETUP_ERR,
                                                            registration_id,
                                                            HTTPStatus.BAD_REQUEST,
                                                            'No verification report data found for the registration.')
            return fs_utils.get_registration_callback_report(registration)
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception, None, 'POST registration report event')
        except Exception as default_err:  # noqa: B902; return nicer default error
            return fs_utils.registration_callback_error(resource_utils.CallbackExceptionCodes.DEFAULT,
                                                        registration_id,
                                                        HTTPStatus.INTERNAL_SERVER_ERROR,
                                                        str(default_err))
