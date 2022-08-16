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
from flask import current_app, jsonify, request
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils

from mhr_api.utils.auth import jwt
from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.services.authz import is_staff, authorized, authorized_role, REGISTER_MH
from mhr_api.models import MhrRegistration
from mhr_api.resources import utils as resource_utils, registration_utils as reg_utils
from mhr_api.services.payment import TransactionTypes
from mhr_api.services.payment.exceptions import SBCPaymentException


bp = Blueprint('REGISTRATIONS1',  # pylint: disable=invalid-name
               __name__, url_prefix='/api/v1/registrations')


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
        statement_list = MhrRegistration.find_all_by_account_id(account_id)
        return jsonify(statement_list), HTTPStatus.OK

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id,
                                                    'GET account registrations id=' + account_id)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def post_registrations():  # pylint: disable=too-many-return-statements
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
        request_json = request.get_json(silent=True)
        # Validate request against the schema.
        valid_format, errors = schema_utils.validate(request_json, 'registration', 'mhr')
        # Additional validation not covered by the schema.
        extra_validation_msg = resource_utils.validate_registration(request_json, is_staff(jwt))
        if not valid_format or extra_validation_msg != '':
            return resource_utils.validation_error_response(errors, reg_utils.VAL_ERROR, extra_validation_msg)
        # Set up the registration, pay, and save the data.
        registration = reg_utils.pay_and_save_registration(request,
                                                           request_json,
                                                           account_id,
                                                           TransactionTypes.REGISTRATION)
        response_json = {}
        if registration.manuhome:
            response_json = registration.manuhome.new_registration_json
        else:
            response_json = registration.json

        # Return report if request header Accept MIME type is application/pdf.
        if resource_utils.is_pdf(request):
            current_app.logger.info('Report not yet available: returning JSON.')
            # return reg_utils.get_registration_report(statement.registration[0], response_json,
            #                                        ReportTypes.FINANCING_STATEMENT_REPORT.value,
            #                                        jwt.get_token_auth_header(), HTTPStatus.CREATED)
        # resource_utils.enqueue_registration_report(statement.registration[0], response_json,
        #                                            ReportTypes.FINANCING_STATEMENT_REPORT.value)
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
