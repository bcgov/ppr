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

from flask import jsonify, request #, g
from flask_restplus import Namespace, Resource, cors
#from flask_jwt_oidc import JwtManager

from registry_schemas import utils as schema_utils
from ppr_api.utils.auth import jwt
from ppr_api.utils.util import cors_preflight
from ppr_api.exceptions import BusinessException
from ppr_api.services.authz import is_staff, authorized
from ppr_api.models import Registration, FinancingStatement

from .utils import get_account_id, account_required_response, validation_error_response, \
                   business_exception_response, default_exception_response
from .utils import unauthorized_error_response, path_param_error_response
from .utils import path_data_mismatch_error_response, base_debtor_invalid_response


API = Namespace('financing-statements', description='Endpoints for maintaining financing statements and updates.')

VAL_ERROR = "Financing Statement request data validation errors."  # Default validation error prefix
VAL_ERROR_AMEND = "Amendment Statement request data validation errors."  # Amendment validation error prefix
VAL_ERROR_CHANGE = "Change Statement request data validation errors."  # Change validation error prefix
VAL_ERROR_RENEWAL = "Renewal Statement request data validation errors."  # Renewal validation error prefix
VAL_ERROR_DISCHARGE = "Discharge Statement request data validation errors."  # Discharge validation error prefix


@cors_preflight('GET,POST,OPTIONS')
@API.route('', methods=['GET', 'POST', 'OPTIONS'])
class FinancingResource(Resource):
    """Resource for executing PPR searches."""

    @staticmethod
    @cors.crossdomain(origin='*')
#    @jwt.requires_auth
    def get():
        """Get the list of financing statements created by the header account ID."""
#        token = g.jwt_oidc_token_info

        try:

            # Quick check: must provide an account ID.
            account_id = get_account_id(request)
            if account_id is None:
                return account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return unauthorized_error_response(account_id)

            # Try to fetch financing statement list for account ID
            statement_list = FinancingStatement.find_all_by_account_id(account_id, is_staff(jwt))
#            if not statement_list:
#                return not_found_error_response('financing statements', account_id)

            return jsonify(statement_list), HTTPStatus.OK

        except BusinessException as exception:
            return business_exception_response(exception)
        except Exception as default_exception:
            return default_exception_response(default_exception)


    @staticmethod
    @cors.crossdomain(origin='*')
#    @jwt.requires_auth
    def post():
        """Create a new financing statement."""
#        token = g.jwt_oidc_token_info

        try:

            # Quick check: must be staff or provide an account ID.
            account_id = get_account_id(request)
            if not is_staff(jwt) and account_id is None:
                return account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate request data against the schema.
            valid_format, errors = schema_utils.validate(request_json, 'financingStatement', 'ppr')
            if not valid_format:
                return validation_error_response(errors, VAL_ERROR)

            # TODO: charge a fee.

            # Try to save the financing statement: failure throws a business exception.
            statement = FinancingStatement.create_from_json(request_json, account_id)
            statement.save()

            return statement.json, HTTPStatus.CREATED

        except BusinessException as exception:
            return business_exception_response(exception)
        except Exception as default_exception:
            return default_exception_response(default_exception)



@cors_preflight('GET,OPTIONS')
@API.route('/<path:registration_num>', methods=['GET', 'OPTIONS'])
class GetFinancingResource(Resource):
    """Resource to get an individual financing statement by registration number."""

    @staticmethod
    @cors.crossdomain(origin='*')
#    @jwt.requires_auth
    def get(registration_num):
        """Get a financing statement by registration number."""
#        token = g.jwt_oidc_token_info

        try:
            if registration_num is None:
                return path_param_error_response('registration number')

            # Quick check: must be staff or provide an account ID.
            account_id = get_account_id(request)
            if not is_staff(jwt) and account_id is None:
                return account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return unauthorized_error_response(account_id)

            # Try to fetch financing statement by registration number
            # Not found or non-staff historical throws a business exception.
            statement = FinancingStatement.find_by_registration_number(registration_num,
                                                                       is_staff(jwt))
            return statement.json, HTTPStatus.OK

        except BusinessException as exception:
            return business_exception_response(exception)
        except Exception as default_exception:
            return default_exception_response(default_exception)



@cors_preflight('POST,OPTIONS')
@API.route('/<path:registration_num>/amendments', methods=['POST', 'OPTIONS'])
class AmendmentResource(Resource):
    """Resource to register an amendment statement by registration number."""

    @staticmethod
    @cors.crossdomain(origin='*')
#    @jwt.requires_auth
    def post(registration_num):
        """Amend a financing statement by registration number."""
#        token = g.jwt_oidc_token_info

        try:
            if registration_num is None:
                return path_param_error_response('registration number')

            # Quick check: must be staff or provide an account ID.
            account_id = get_account_id(request)
            if not is_staff(jwt) and account_id is None:
                return account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate request data against the schema.
            valid_format, errors = schema_utils.validate(request_json, 'amendmentStatement', 'ppr')
            if not valid_format:
                return validation_error_response(errors, VAL_ERROR_AMEND)

            # payload base registration number must match path registration number
            if registration_num != request_json['baseRegistrationNumber']:
                return path_data_mismatch_error_response(registration_num, \
                                                         'base registration number', \
                                                         request_json['baseRegistrationNumber'])

            # Fetch base registration information: business exception thrown if not
            # found or historical.
            statement = FinancingStatement.find_by_registration_number(registration_num, False)

            # Verify base debtor (bypassed for staff)
            if not statement.validate_base_debtor(request_json['baseDebtor'], is_staff(jwt)):
                return base_debtor_invalid_response()

            # TODO: charge a fee.

            # Try to save the amendment statement: failure throws a business exception.
            statement = Registration.create_from_json(request_json,
                                                      'AMENDMENT',
                                                      statement,
                                                      registration_num,
                                                      account_id)
            statement.save()

            return statement.json, HTTPStatus.OK

        except BusinessException as exception:
            return business_exception_response(exception)
        except Exception as default_exception:
            return default_exception_response(default_exception)



@cors_preflight('POST,OPTIONS')
@API.route('/<path:registration_num>/changes', methods=['POST', 'OPTIONS'])
class ChangeResource(Resource):
    """Resource to register an change statement by registration number."""

    @staticmethod
    @cors.crossdomain(origin='*')
#    @jwt.requires_auth
    def post(registration_num):
        """Change a financing statement by registration number."""
#        token = g.jwt_oidc_token_info

        try:
            if registration_num is None:
                return path_param_error_response('registration number')

            # Quick check: must be staff or provide an account ID.
            account_id = get_account_id(request)
            if not is_staff(jwt) and account_id is None:
                return account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate request data against the schema.
            valid_format, errors = schema_utils.validate(request_json, 'changeStatement', 'ppr')
            if not valid_format:
                return validation_error_response(errors, VAL_ERROR_CHANGE)

            # payload base registration number must match path registration number
            if registration_num != request_json['baseRegistrationNumber']:
                return path_data_mismatch_error_response(registration_num, \
                                                         'base registration number', \
                                                         request_json['baseRegistrationNumber'])


            # Fetch base registration information: business exception thrown if not
            # found or historical.
            statement = FinancingStatement.find_by_registration_number(registration_num, False)

            # Verify base debtor (bypassed for staff)
            if not statement.validate_base_debtor(request_json['baseDebtor'], is_staff(jwt)):
                return base_debtor_invalid_response()

            # TODO: charge a fee.

            # Try to save the change statement: failure throws a business exception.
            statement = Registration.create_from_json(request_json,
                                                      'CHANGE',
                                                      statement,
                                                      registration_num,
                                                      account_id)
            statement.save()

            return statement.json, HTTPStatus.OK

        except BusinessException as exception:
            return business_exception_response(exception)
        except Exception as default_exception:
            return default_exception_response(default_exception)



@cors_preflight('POST,OPTIONS')
@API.route('/<path:registration_num>/renewals', methods=['POST', 'OPTIONS'])
class RenewalResource(Resource):
    """Resource to register an renewal statement by registration number."""

    @staticmethod
    @cors.crossdomain(origin='*')
#    @jwt.requires_auth
    def post(registration_num):
        """Renew a financing statement by registration number."""
#        token = g.jwt_oidc_token_info

        try:
            if registration_num is None:
                return path_param_error_response('registration number')

            # Quick check: must be staff or provide an account ID.
            account_id = get_account_id(request)
            if not is_staff(jwt) and account_id is None:
                return account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate request data against the schema.
            valid_format, errors = schema_utils.validate(request_json, 'renewalStatement', 'ppr')
            if not valid_format:
                return validation_error_response(errors, VAL_ERROR_RENEWAL)

            # payload base registration number must match path registration number
            if registration_num != request_json['baseRegistrationNumber']:
                return path_data_mismatch_error_response(registration_num,
                                                         'base registration number',
                                                         request_json['baseRegistrationNumber'])

            # Fetch base registration information: business exception thrown if not
            # found or historical.
            statement = FinancingStatement.find_by_registration_number(registration_num, False)

            # Verify base debtor (bypassed for staff)
            if not statement.validate_base_debtor(request_json['baseDebtor'], is_staff(jwt)):
                return base_debtor_invalid_response()

            # TODO: charge a fee.

            # Try to save the renewal statement: failure throws a business exception.
            statement = Registration.create_from_json(request_json,
                                                      'RENEWAL',
                                                      statement,
                                                      registration_num,
                                                      account_id)
            statement.save()

            return statement.json, HTTPStatus.OK

        except BusinessException as exception:
            return business_exception_response(exception)
        except Exception as default_exception:
            return default_exception_response(default_exception)



@cors_preflight('POST,OPTIONS')
@API.route('/<path:registration_num>/discharges', methods=['POST', 'OPTIONS'])
class DischargeResource(Resource):
    """Resource to discharge an individual financing statement by registration number."""

    @staticmethod
    @cors.crossdomain(origin='*')
#    @jwt.requires_auth
    def post(registration_num):
        """Discharge a financing statement by registration number."""
#        token = g.jwt_oidc_token_info

        try:
            if registration_num is None:
                return path_param_error_response('registration number')

            # Quick check: must be staff or provide an account ID.
            account_id = get_account_id(request)
            if not is_staff(jwt) and account_id is None:
                return account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate request data against the schema.
            valid_format, errors = schema_utils.validate(request_json, 'dischargeStatement', 'ppr')
            if not valid_format:
                return validation_error_response(errors, VAL_ERROR_DISCHARGE)

            # payload base registration number must match path registration number
            if registration_num != request_json['baseRegistrationNumber']:
                return path_data_mismatch_error_response(registration_num,
                                                         'base registration number',
                                                         request_json['baseRegistrationNumber'])

            # Fetch base registration information: business exception thrown if not
            # found or historical.
            statement = FinancingStatement.find_by_registration_number(registration_num, False)

            # Verify base debtor (bypassed for staff)
            if not statement.validate_base_debtor(request_json['baseDebtor'], is_staff(jwt)):
                return base_debtor_invalid_response()

            # TODO: charge a fee.

            # Try to save the discharge statement: failure throws a business exception.
            statement = Registration.create_from_json(request_json,
                                                      'DISCHARGE',
                                                      statement,
                                                      registration_num,
                                                      account_id)
            statement.save()


            return statement.json, HTTPStatus.OK

        except BusinessException as exception:
            return business_exception_response(exception)
        except Exception as default_exception:
            return default_exception_response(default_exception)
