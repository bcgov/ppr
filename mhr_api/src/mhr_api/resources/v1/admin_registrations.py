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
"""API endpoints for requests to maintain MH unit note registrations."""

from http import HTTPStatus

from flask import Blueprint
from flask import g, current_app, request, jsonify
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils

from mhr_api.utils.auth import jwt
from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.services.authz import is_staff, get_group
from mhr_api.models import MhrRegistration
from mhr_api.models.type_tables import MhrDocumentTypes
from mhr_api.reports.v2.report_utils import ReportTypes
from mhr_api.resources import utils as resource_utils, registration_utils as reg_utils
from mhr_api.services.payment import TransactionTypes
from mhr_api.services.payment.exceptions import SBCPaymentException


bp = Blueprint('ADMIN_REGISTRATIONS1',  # pylint: disable=invalid-name
               __name__, url_prefix='/api/v1/admin-registrations')


@bp.route('/<string:mhr_number>', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def post_admin_registration(mhr_number: str):  # pylint: disable=too-many-return-statements
    """Create a new admin registration."""
    account_id = ''
    try:
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        current_app.logger.info(f'Starting new admin reg mhr={mhr_number}, account={account_id}')
        if account_id is None or account_id.strip() == '':
            return resource_utils.account_required_response()
        # Verify request JWT role
        request_json = request.get_json(silent=True)
        if not is_staff(jwt):
            current_app.logger.error('User not staff: admin registrations are registries staff only.')
            return resource_utils.unauthorized_error_response(account_id)
        # Not found or not allowed to access throw exceptions.
        current_reg: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_number, account_id, True)
        # Validate request against the schema.
        valid_format, errors = schema_utils.validate(request_json, 'adminRegistration', 'mhr')
        # Additional validation not covered by the schema.
        extra_validation_msg = resource_utils.validate_admin_registration(current_reg, request_json)
        if not valid_format or extra_validation_msg != '':
            return resource_utils.validation_error_response(errors, reg_utils.VAL_ERROR, extra_validation_msg)

        return save_registration(request, request_json, current_reg, account_id, mhr_number)
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id,
                                                    'POST mhr note id=' + account_id)
    except SBCPaymentException as pay_exception:
        return resource_utils.pay_exception_response(pay_exception, account_id)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


def save_registration(req: request, request_json: dict, current_reg: MhrRegistration, account_id: str, mhr_number: str):
    """Perform the remaining set up the registration, pay, save the data, set up the report request."""
    group: str = get_group(jwt)
    # Get current location and owners before updating for batch JSON (amendment, correction, location change).
    current_reg.current_view = True
    current_location: dict = None
    current_owners = None
    if request_json.get('location'):
        current_location = reg_utils.get_active_location(current_reg)
    if request_json.get('addOwnerGroups'):
        current_owners = reg_utils.get_active_owners(current_reg)
    registration = reg_utils.pay_and_save_admin(req,
                                                current_reg,
                                                request_json,
                                                account_id,
                                                group,
                                                get_transaction_type(request_json))
    current_app.logger.debug(f'building admin reg response json for {mhr_number}')
    registration.change_registrations = current_reg.change_registrations
    response_json = registration.json
    if resource_utils.is_pdf(request):
        current_app.logger.info('Report not yet available: returning JSON.')
    current_json = current_reg.new_registration_json
    if current_location:
        current_json['location'] = current_location
    if current_owners:
        current_json['ownerGroups'] = current_owners
    setup_report(registration, response_json, current_json, group)
    return jsonify(response_json), HTTPStatus.CREATED


def setup_report(registration: MhrRegistration,
                 response_json: dict,
                 current_json: dict,
                 group: str):
    """Update the registration data for reporting and publish the registration event."""
    response_json['usergroup'] = group
    response_json['username'] = reg_utils.get_affirmby(g.jwt_oidc_token_info)
    response_json['status'] = current_json.get('status')
    if response_json.get('location') and not response_json.get('ownerGroups'):
        response_json['ownerGroups'] = current_json.get('ownerGroups')
    reg_utils.enqueue_registration_report(registration, response_json, ReportTypes.MHR_REGISTRATION_STAFF, current_json)
    del response_json['username']
    del response_json['usergroup']


def get_transaction_type(request_json) -> str:
    """Try and obtain an optional boolean parameter value from the request parameters."""
    if request_json.get('documentType', '') == MhrDocumentTypes.NRED:
        return TransactionTypes.UNIT_NOTE
    if request_json.get('documentType', '') == MhrDocumentTypes.STAT:
        return TransactionTypes.ADMIN_RLCHG
    if request_json.get('documentType') == MhrDocumentTypes.REGC:
        return TransactionTypes.ADMIN_CORLC
    if request_json.get('documentType') == MhrDocumentTypes.PUBA:
        return TransactionTypes.UNIT_NOTE_OTHER
    return TransactionTypes.UNIT_NOTE
