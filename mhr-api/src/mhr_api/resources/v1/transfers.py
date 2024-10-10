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

from flask import Blueprint, g, jsonify, request
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils

from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.models import MhrQualifiedSupplier, MhrRegistration
from mhr_api.models import registration_utils as model_reg_utils
from mhr_api.models import utils as model_utils
from mhr_api.models.registration_json_utils import cleanup_owner_groups, sort_owner_groups
from mhr_api.models.type_tables import MhrOwnerStatusTypes, MhrRegistrationStatusTypes
from mhr_api.reports.v2.report_utils import ReportTypes
from mhr_api.resources import registration_utils as reg_utils
from mhr_api.resources import utils as resource_utils
from mhr_api.services.authz import (
    DEALERSHIP_GROUP,
    TRANSFER_DEATH_JT,
    TRANSFER_SALE_BENEFICIARY,
    authorized_role,
    get_group,
    is_all_staff_account,
    is_bcol_help,
    is_reg_staff_account,
    is_staff,
)
from mhr_api.services.payment import TransactionTypes
from mhr_api.services.payment.exceptions import SBCPaymentException
from mhr_api.utils.auth import jwt
from mhr_api.utils.logging import logger

bp = Blueprint("TRANSFERS1", __name__, url_prefix="/api/v1/transfers")  # pylint: disable=invalid-name


@bp.route("/<string:mhr_number>", methods=["POST", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def post_transfers(mhr_number: str):  # pylint: disable=too-many-return-statements
    """Create a new Transfer of Sale/Ownership registration."""
    account_id = ""
    try:
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None or account_id.strip() == "":
            return resource_utils.account_required_response()
        # Verify request JWT role
        if is_bcol_help(account_id, jwt):
            return resource_utils.helpdesk_unauthorized_error_response("transfer of ownership")
        request_json = request.get_json(silent=True)
        group: str = get_group(jwt)
        if (
            not model_reg_utils.is_transfer_due_to_death(request_json.get("registrationType"))
            and not authorized_role(jwt, TRANSFER_SALE_BENEFICIARY)
            and group != DEALERSHIP_GROUP
        ):
            logger.error("User not staff ({group}) or missing required role: " + TRANSFER_SALE_BENEFICIARY)
            return resource_utils.unauthorized_error_response(account_id)
        if model_reg_utils.is_transfer_due_to_death(request_json.get("registrationType")) and not authorized_role(
            jwt, TRANSFER_DEATH_JT
        ):
            logger.error("User not staff or missing required role: " + TRANSFER_DEATH_JT)
            return resource_utils.unauthorized_error_response(account_id)

        # Not found or not allowed to access throw exceptions.
        current_reg: MhrRegistration = MhrRegistration.find_all_by_mhr_number(
            mhr_number, account_id, is_all_staff_account(account_id)
        )
        request_json = get_qs_dealer(request_json, group, account_id)
        # Validate request against the schema.
        valid_format, errors = schema_utils.validate(request_json, "transfer", "mhr")
        # Additional validation not covered by the schema.
        extra_validation_msg = resource_utils.validate_transfer(current_reg, request_json, is_staff(jwt), group)
        if not valid_format or extra_validation_msg != "":
            return resource_utils.validation_error_response(errors, reg_utils.VAL_ERROR, extra_validation_msg)
        current_reg.current_view = True
        # Get current owners before updating for batch JSON.
        current_owners = reg_utils.get_active_owners(current_reg)
        # Set up the registration, pay, and save the data.
        registration = reg_utils.pay_and_save_transfer(
            request, current_reg, request_json, account_id, group, TransactionTypes.TRANSFER
        )
        logger.debug(f"building transfer response json for {mhr_number}")
        registration.change_registrations = current_reg.change_registrations
        response_json = registration.json
        # Return report if request header Accept MIME type is application/pdf.
        if resource_utils.is_pdf(request):
            logger.info("Report not yet available: returning JSON.")
        # Report data include all active owners.
        setup_report(registration, response_json, current_reg, account_id, current_owners)
        return jsonify(response_json), HTTPStatus.CREATED

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "POST mhr registration id=" + account_id)
    except SBCPaymentException as pay_exception:
        return resource_utils.pay_exception_response(pay_exception, account_id)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


def setup_report(  # pylint: disable=too-many-locals,too-many-branches
    registration: MhrRegistration,
    response_json,
    current_reg: MhrRegistration,
    account_id: str,
    current_owners,
):
    """Include all active owners in the transfer report request data and add it to the queue."""
    current_reg.current_view = True
    current_json = current_reg.new_registration_json
    current_json["ownerGroups"] = current_owners
    add_groups = response_json.get("addOwnerGroups")
    new_groups = []
    if not response_json.get("deleteOwnerGroups"):
        delete_groups = []
        for group in current_reg.owner_groups:
            if group.change_registration_id == registration.id and group.status_type == MhrOwnerStatusTypes.PREVIOUS:
                delete_groups.append(group.json)
        response_json["deleteOwnerGroups"] = delete_groups
    for group in current_json.get("ownerGroups"):
        deleted: bool = False
        for delete_group in response_json.get("deleteOwnerGroups"):
            if delete_group.get("groupId") == group.get("groupId"):
                deleted = True
        if not deleted:
            new_groups.append(group)
    for add_group in add_groups:
        added: bool = False
        for new_group in new_groups:
            if add_group.get("groupId") == new_group.get("groupId"):
                added = True
        if not added:
            new_groups.append(add_group)
    response_json["addOwnerGroups"] = sort_owner_groups(new_groups)
    # Report setup is current view except for FROZEN status: update report data.
    status: str = response_json.get("status")
    if status == model_utils.STATUS_FROZEN:
        response_json["status"] = MhrRegistrationStatusTypes.ACTIVE
    if is_reg_staff_account(account_id):
        token = g.jwt_oidc_token_info
        username: str = token.get("firstname", "") + " " + token.get("lastname", "")
        response_json["username"] = username
        reg_utils.enqueue_registration_report(
            registration, response_json, ReportTypes.MHR_REGISTRATION_STAFF, current_json
        )
        del response_json["username"]
    else:
        reg_utils.enqueue_registration_report(registration, response_json, ReportTypes.MHR_TRANSFER, current_json)
    response_add_groups = []
    for add_group in add_groups:
        if not add_group.get("existing"):
            response_add_groups.append(add_group)
    response_json["addOwnerGroups"] = response_add_groups
    response_json["status"] = status
    response_json = cleanup_owner_groups(response_json)


def get_qs_dealer(request_json: dict, group: str, account_id: str) -> dict:
    """Try to get the qualified supplier information by account id and add it to the request for validation."""
    if not group or group != DEALERSHIP_GROUP:
        return request_json
    supplier = MhrQualifiedSupplier.find_by_account_id(account_id)
    if supplier:
        request_json["supplier"] = supplier.json
    return request_json
