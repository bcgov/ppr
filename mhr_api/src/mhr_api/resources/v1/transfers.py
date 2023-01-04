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
"""API endpoints for requests to maintain MH transfer of sale/ownership requests."""

from http import HTTPStatus

from flask import Blueprint
from flask import current_app, request, jsonify
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils

from mhr_api.utils.auth import jwt
from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.services.authz import authorized_role, is_staff, is_all_staff_account, get_group
from mhr_api.services.authz import TRANSFER_SALE_BENEFICIARY, TRANSFER_DEATH_JT
from mhr_api.models import MhrRegistration
from mhr_api.reports.v2.report_utils import ReportTypes
from mhr_api.resources import utils as resource_utils, registration_utils as reg_utils
from mhr_api.services.payment import TransactionTypes
from mhr_api.services.payment.exceptions import SBCPaymentException


bp = Blueprint('TRANSFERS1',  # pylint: disable=invalid-name
               __name__, url_prefix='/api/v1/transfers')


@bp.route('/<string:mhr_number>', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def post_transfers(mhr_number: str):  # pylint: disable=too-many-return-statements
    """Create a new Transfer of Sale/Ownership registration."""
    account_id = ''
    try:
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None or account_id.strip() == '':
            return resource_utils.account_required_response()
        # Verify request JWT role
        request_json = request.get_json(silent=True)
        if not request_json.get('deathOfOwner') and not authorized_role(jwt, TRANSFER_SALE_BENEFICIARY):
            current_app.logger.error('User not staff or missing required role: ' + TRANSFER_SALE_BENEFICIARY)
            return resource_utils.unauthorized_error_response(account_id)
        if request_json.get('deathOfOwner') and not authorized_role(jwt, TRANSFER_DEATH_JT):
            current_app.logger.error('User not staff or missing required role: ' + TRANSFER_DEATH_JT)
            return resource_utils.unauthorized_error_response(account_id)

        # Not found or not allowed to access throw exceptions.
        current_reg: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_number,
                                                                              account_id,
                                                                              is_all_staff_account(account_id))

        # Validate request against the schema.
        valid_format, errors = schema_utils.validate(request_json, 'transfer', 'mhr')
        # Additional validation not covered by the schema.
        extra_validation_msg = resource_utils.validate_transfer(current_reg, request_json, is_staff(jwt))
        if not valid_format or extra_validation_msg != '':
            return resource_utils.validation_error_response(errors, reg_utils.VAL_ERROR, extra_validation_msg)
        # Set up the registration, pay, and save the data.
        registration = reg_utils.pay_and_save_transfer(request,
                                                       current_reg,
                                                       request_json,
                                                       account_id,
                                                       get_group(jwt),
                                                       TransactionTypes.TRANSFER)
        current_app.logger.debug(f'building transfer response json for {mhr_number}')
        response_json = registration.json
        # Return report if request header Accept MIME type is application/pdf.
        if resource_utils.is_pdf(request):
            current_app.logger.info('Report not yet available: returning JSON.')
        # Report data include all active owners.
        setup_report(registration, response_json, current_reg)
        return jsonify(response_json), HTTPStatus.CREATED

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id,
                                                    'POST mhr registration id=' + account_id)
    except SBCPaymentException as pay_exception:
        return resource_utils.pay_exception_response(pay_exception, account_id)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


def setup_report(registration: MhrRegistration, response_json, current_reg: MhrRegistration):
    """Include all active owners in the transfer report request data and add it to the queue."""
    add_groups = response_json.get('addOwnerGroups')
    current_reg.current_view = True
    current_json = current_reg.new_registration_json
    new_groups = []
    for group in current_json.get('ownerGroups'):
        deleted: bool = False
        for delete_group in response_json.get('deleteOwnerGroups'):
            if delete_group.get('groupId') == group.get('groupId'):
                deleted = True
        if not deleted:
            new_groups.append(group)
    for add_group in add_groups:
        added: bool = False
        for new_group in new_groups:
            if add_group.get('groupId') == new_group.get('groupId'):
                added = True
        if not added:
            new_groups.append(add_group)
    response_json['addOwnerGroups'] = new_groups
    reg_utils.enqueue_registration_report(registration, response_json, ReportTypes.MHR_TRANSFER)
    response_json['addOwnerGroups'] = add_groups
