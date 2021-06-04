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

from flask import jsonify, request, current_app
from flask_restx import Namespace, Resource, cors
from registry_schemas import utils as schema_utils

from ppr_api.exceptions import BusinessException
from ppr_api.models import FinancingStatement, Registration
from ppr_api.models import utils as model_utils
from ppr_api.resources import utils as resource_utils
from ppr_api.services.authz import authorized, is_staff
from ppr_api.services.payment.exceptions import SBCPaymentException
from ppr_api.services.payment.payment import Payment, TransactionTypes
from ppr_api.utils.auth import jwt
from ppr_api.utils.util import cors_preflight


API = Namespace('financing-statements', description='Endpoints for maintaining financing statements and updates.')

VAL_ERROR = 'Financing Statement request data validation errors.'  # Default validation error prefix
VAL_ERROR_AMEND = 'Amendment Statement request data validation errors.'  # Amendment validation error prefix
VAL_ERROR_CHANGE = 'Change Statement request data validation errors.'  # Change validation error prefix
VAL_ERROR_RENEWAL = 'Renewal Statement request data validation errors.'  # Renewal validation error prefix
VAL_ERROR_DISCHARGE = 'Discharge Statement request data validation errors.'  # Discharge validation error prefix
SAVE_ERROR_MESSAGE = 'Account {0} create {1} statement db save failed: {2}'
PAY_REFUND_MESSAGE = 'Account {0} create {1} statement refunding payment for invoice {2}.'
PAY_REFUND_ERROR = 'Account {0} create {1} statement payment refund failed for invoice {2}: {3}.'


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
            statement_list = FinancingStatement.find_all_by_account_id(account_id, is_staff(jwt))

            return jsonify(statement_list), HTTPStatus.OK

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
            if not is_staff(jwt) and account_id is None:
                return resource_utils.account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate request data against the schema.
            valid_format, errors = schema_utils.validate(request_json, 'financingStatement', 'ppr')
            if not valid_format:
                return resource_utils.validation_error_response(errors, VAL_ERROR)

            # Charge a fee.
            statement = FinancingStatement.create_from_json(request_json, account_id)
            invoice_id = None
            if account_id:
                fee_code = TransactionTypes.FINANCING_LIFE_YEAR.value
                fee_quantity = statement.life
                if statement.life == model_utils.LIFE_INFINITE:
                    fee_quantity = 1
                    fee_code = TransactionTypes.FINANCING_INFINITE.value
                payment = Payment(jwt=jwt.get_token_auth_header(), account_id=account_id)
                pay_ref = payment.create_payment(fee_code, fee_quantity, None,
                                                 statement.registration[0].client_reference_id)
                invoice_id = pay_ref['invoiceId']
                statement.registration[0].pay_invoice_id = int(invoice_id)
                statement.registration[0].pay_path = pay_ref['receipt']

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
                raise db_exception

            return statement.json, HTTPStatus.CREATED

        except SBCPaymentException as pay_exception:
            return resource_utils.pay_exception_response(pay_exception)
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
            if not is_staff(jwt) and account_id is None:
                return resource_utils.account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)

            # Try to fetch financing statement by registration number
            # Not found throws a business exception.
            statement = FinancingStatement.find_by_registration_number(registration_num,
                                                                       is_staff(jwt),
                                                                       True)
            return statement.json, HTTPStatus.OK

        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
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
            if not is_staff(jwt) and account_id is None:
                return resource_utils.account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate request data against the schema.
            valid_format, errors = schema_utils.validate(request_json, 'amendmentStatement', 'ppr')
            if not valid_format:
                return resource_utils.validation_error_response(errors, VAL_ERROR_AMEND)

            # payload base registration number must match path registration number
            if registration_num != request_json['baseRegistrationNumber']:
                return resource_utils.path_data_mismatch_error_response(registration_num,
                                                                        'base registration number',
                                                                        request_json['baseRegistrationNumber'])

            # Fetch base registration information: business exception thrown if not
            # found or historical.
            statement = FinancingStatement.find_by_registration_number(registration_num, False)

            # Verify base debtor (bypassed for staff)
            if not statement.validate_base_debtor(request_json['baseDebtor'], is_staff(jwt)):
                return resource_utils.base_debtor_invalid_response()

            # Set up registration and pay.
            registration = setup_registration_pay(request_json,
                                                  model_utils.REG_CLASS_AMEND,
                                                  statement,
                                                  registration_num,
                                                  account_id)
            invoice_id = str(registration.pay_invoice_id)

            # Try to save the amendment statement: failure throws an exception.
            try:
                registration.save()
            except Exception as db_exception:   # noqa: B902; handle all db related errors.
                current_app.logger.error(SAVE_ERROR_MESSAGE.format(account_id, 'amendment', repr(db_exception)))
                if account_id and invoice_id is not None:
                    current_app.logger.info(PAY_REFUND_MESSAGE.format(account_id, 'amendment', invoice_id))
                    try:
                        payment = Payment(jwt=jwt.get_token_auth_header(), account_id=account_id)
                        payment.cancel_payment(invoice_id)
                    except SBCPaymentException as cancel_exception:
                        current_app.logger.error(PAY_REFUND_ERROR.format(account_id, 'amendment', invoice_id,
                                                                         repr(cancel_exception)))
                raise db_exception

            return registration.json, HTTPStatus.CREATED

        except SBCPaymentException as pay_exception:
            return resource_utils.pay_exception_response(pay_exception)
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('POST,OPTIONS')
@API.route('/<path:registration_num>/changes', methods=['POST', 'OPTIONS'])
class ChangeResource(Resource):
    """Resource to register an change statement by registration number."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def post(registration_num):
        """Change a financing statement by registration number."""
        try:
            if registration_num is None:
                return resource_utils.path_param_error_response('registration number')

            # Quick check: must be staff or provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if not is_staff(jwt) and account_id is None:
                return resource_utils.account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate request data against the schema.
            valid_format, errors = schema_utils.validate(request_json, 'changeStatement', 'ppr')
            if not valid_format:
                return resource_utils.validation_error_response(errors, VAL_ERROR_CHANGE)

            # payload base registration number must match path registration number
            if registration_num != request_json['baseRegistrationNumber']:
                return resource_utils.path_data_mismatch_error_response(registration_num,
                                                                        'base registration number',
                                                                        request_json['baseRegistrationNumber'])

            # Fetch base registration information: business exception thrown if not
            # found or historical.
            statement = FinancingStatement.find_by_registration_number(registration_num, False)

            # Verify base debtor (bypassed for staff)
            if not statement.validate_base_debtor(request_json['baseDebtor'], is_staff(jwt)):
                return resource_utils.base_debtor_invalid_response()

            # Set up registration and pay.
            registration = setup_registration_pay(request_json,
                                                  model_utils.REG_CLASS_CHANGE,
                                                  statement,
                                                  registration_num,
                                                  account_id)
            invoice_id = str(registration.pay_invoice_id)

            # Try to save the change statement: failure throws an exception.
            try:
                registration.save()
            except Exception as db_exception:   # noqa: B902; handle all db related errors.
                current_app.logger.error(SAVE_ERROR_MESSAGE.format(account_id, 'change', repr(db_exception)))
                if account_id and invoice_id is not None:
                    current_app.logger.info(PAY_REFUND_MESSAGE.format(account_id, 'change', invoice_id))
                    try:
                        payment = Payment(jwt=jwt.get_token_auth_header(), account_id=account_id)
                        payment.cancel_payment(invoice_id)
                    except SBCPaymentException as cancel_exception:
                        current_app.logger.error(PAY_REFUND_ERROR.format(account_id, 'change', invoice_id,
                                                                         repr(cancel_exception)))
                raise db_exception

            return registration.json, HTTPStatus.CREATED

        except SBCPaymentException as pay_exception:
            return resource_utils.pay_exception_response(pay_exception)
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
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
            if not is_staff(jwt) and account_id is None:
                return resource_utils.account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate request data against the schema.
            valid_format, errors = schema_utils.validate(request_json, 'renewalStatement', 'ppr')
            if not valid_format:
                return resource_utils.validation_error_response(errors, VAL_ERROR_RENEWAL)

            # payload base registration number must match path registration number
            if registration_num != request_json['baseRegistrationNumber']:
                return resource_utils.path_data_mismatch_error_response(registration_num,
                                                                        'base registration number',
                                                                        request_json['baseRegistrationNumber'])

            # Fetch base registration information: business exception thrown if not
            # found or historical.
            statement = FinancingStatement.find_by_registration_number(registration_num, False)

            # Verify base debtor (bypassed for staff)
            if not statement.validate_base_debtor(request_json['baseDebtor'], is_staff(jwt)):
                return resource_utils.base_debtor_invalid_response()

            # Set up registration and pay.
            registration = setup_registration_pay(request_json,
                                                  model_utils.REG_CLASS_RENEWAL,
                                                  statement,
                                                  registration_num,
                                                  account_id)
            invoice_id = str(registration.pay_invoice_id)

            # Try to save the renewal statement: failure throws an exception.
            try:
                registration.save()
            except Exception as db_exception:   # noqa: B902; handle all db related errors.
                current_app.logger.error(SAVE_ERROR_MESSAGE.format(account_id, 'renewal', repr(db_exception)))
                if account_id and invoice_id is not None:
                    current_app.logger.info(PAY_REFUND_MESSAGE.format(account_id, 'renewal', invoice_id))
                    try:
                        payment = Payment(jwt=jwt.get_token_auth_header(), account_id=account_id)
                        payment.cancel_payment(invoice_id)
                    except SBCPaymentException as cancel_exception:
                        current_app.logger.error(PAY_REFUND_ERROR.format(account_id, 'renewal', invoice_id,
                                                                         repr(cancel_exception)))
                raise db_exception

            return registration.json, HTTPStatus.CREATED

        except SBCPaymentException as pay_exception:
            return resource_utils.pay_exception_response(pay_exception)
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
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
            if not is_staff(jwt) and account_id is None:
                return resource_utils.account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate request data against the schema.
            valid_format, errors = schema_utils.validate(request_json, 'dischargeStatement', 'ppr')
            if not valid_format:
                return resource_utils.validation_error_response(errors, VAL_ERROR_DISCHARGE)

            # payload base registration number must match path registration number
            if registration_num != request_json['baseRegistrationNumber']:
                return resource_utils.path_data_mismatch_error_response(registration_num,
                                                                        'base registration number',
                                                                        request_json['baseRegistrationNumber'])

            # Fetch base registration information: business exception thrown if not
            # found or historical.
            statement = FinancingStatement.find_by_registration_number(registration_num, False)

            # Verify base debtor (bypassed for staff)
            if not statement.validate_base_debtor(request_json['baseDebtor'], is_staff(jwt)):
                return resource_utils.base_debtor_invalid_response()

            # No fee for a discharge.
            # Try to save the discharge statement: failure throws a business exception.
            statement = Registration.create_from_json(request_json,
                                                      model_utils.REG_CLASS_DISCHARGE,
                                                      statement,
                                                      registration_num,
                                                      account_id)
            statement.save()
            return statement.json, HTTPStatus.CREATED

        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


def setup_registration_pay(request_json, registration_class, financing_statement, registration_num, account_id):
    """Set up the registration and optionally pay."""
    registration = Registration.create_from_json(request_json,
                                                 registration_class,
                                                 financing_statement,
                                                 registration_num,
                                                 account_id)
    if account_id:
        fee_code = TransactionTypes.CHANGE.value
        fee_quantity = registration.life
        if registration_class == model_utils.REG_CLASS_AMEND:
            fee_code = TransactionTypes.AMENDMENT.value
        elif registration_class == model_utils.REG_CLASS_RENEWAL and registration.life == model_utils.LIFE_INFINITE:
            fee_quantity = 1
            fee_code = TransactionTypes.RENEWAL_INFINITE.value
        elif registration_class == model_utils.REG_CLASS_RENEWAL:
            fee_code = TransactionTypes.RENEWAL_LIFE_YEAR.value

        payment = Payment(jwt=jwt.get_token_auth_header(), account_id=account_id)
        pay_ref = payment.create_payment(fee_code, fee_quantity, None, registration.client_reference_id)
        registration.pay_invoice_id = int(pay_ref['invoiceId'])
        registration.pay_path = pay_ref['receipt']

    return registration
