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
"""API endpoints for requests to maintain MH transport permit registration requests."""

from http import HTTPStatus

from flask import Blueprint, g, jsonify, request
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils

from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.models import MhrManufacturer, MhrQualifiedSupplier, MhrRegistration
from mhr_api.reports.v2.report_utils import ReportTypes
from mhr_api.resources import registration_utils as reg_utils
from mhr_api.resources import utils as resource_utils
from mhr_api.services.authz import (
    DEALERSHIP_GROUP,
    MANUFACTURER_GROUP,
    REQUEST_TRANSPORT_PERMIT,
    authorized_role,
    get_group,
    is_bcol_help,
    is_sbc_office_account,
    is_staff,
)
from mhr_api.services.payment import TransactionTypes
from mhr_api.services.payment.exceptions import SBCPaymentException
from mhr_api.utils.auth import jwt
from mhr_api.utils.logging import logger

bp = Blueprint("PERMITS1", __name__, url_prefix="/api/v1/permits")  # pylint: disable=invalid-name


@bp.route("/<string:mhr_number>", methods=["POST", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def post_permits(mhr_number: str):  # pylint: disable=too-many-return-statements,too-many-locals
    """Create a new Transport Permit registration."""
    account_id = ""
    try:
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        sbc_staff: bool = is_sbc_office_account(jwt.get_token_auth_header(), account_id, jwt)
        verify_error_response = verify_request(account_id, jwt, sbc_staff)
        if verify_error_response:
            return verify_error_response

        # Not found or not allowed to access throw exceptions.
        is_all_staff: bool = sbc_staff or is_staff(jwt)
        current_reg: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_number, account_id, is_all_staff)
        request_json = request.get_json(silent=True)
        # Validate request against the schema.
        logger.debug(f"Extra validation on transport permit json for {mhr_number}")
        # Location may have no street - replace with blank to pass validation
        if request_json.get("newLocation") and request_json["newLocation"].get("address"):
            if not request_json["newLocation"]["address"].get("street"):
                request_json["newLocation"]["address"]["street"] = " "
            # Location may not have a postal code when in Canada
            # Address schema validation requires a postal code in Canada.
            # Add an empty value to pass schema validation.
            if not request_json["newLocation"]["address"].get("postalCode"):
                request_json["newLocation"]["address"]["postalCode"] = ""
        valid_format, errors = schema_utils.validate(request_json, "permit", "mhr")
        # Additional validation not covered by the schema.
        group: str = get_group(jwt)
        request_json = get_qs_location(request_json, group, account_id)
        extra_validation_msg = resource_utils.validate_permit(
            current_reg, request_json, account_id, is_all_staff, group
        )
        if not valid_format or extra_validation_msg != "":
            return resource_utils.validation_error_response(errors, reg_utils.VAL_ERROR, extra_validation_msg)
        # Set up the registration, pay, and save the data.
        # Get current location before updating for batch JSON.
        current_reg.current_view = True
        current_location = reg_utils.get_active_location(current_reg)
        existing_status: str = current_reg.status_type
        registration = reg_utils.pay_and_save_permit(
            request, current_reg, request_json, account_id, group, get_transaction_type(request_json)
        )
        logger.debug(f"building transport permit response json for {mhr_number}")
        response_json = registration.json
        # Return report if request header Accept MIME type is application/pdf.
        if resource_utils.is_pdf(request):
            logger.info("Report not yet available: returning JSON.")
        # Add current description for reporting
        current_json = current_reg.new_registration_json
        current_json["location"] = current_location
        response_json["description"] = current_json.get("description")
        response_json["status"] = current_json.get("status")
        response_json["ownerGroups"] = current_json.get("ownerGroups")
        if response_json.get("amendment") or response_json.get("extension"):
            response_json["permitRegistrationNumber"] = current_json.get("permitRegistrationNumber", "")
            response_json["permitDateTime"] = current_json.get("permitDateTime", "")
            response_json["permitExpiryDateTime"] = current_json.get("permitExpiryDateTime", "")
            response_json["permitStatus"] = current_json.get("permitStatus", "")
            if existing_status != current_json.get("status"):
                response_json["previousStatus"] = existing_status
        setup_report(registration, response_json, group, jwt, current_json)
        return jsonify(response_json), HTTPStatus.CREATED
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "POST mhr registration id=" + account_id)
    except SBCPaymentException as pay_exception:
        return resource_utils.pay_exception_response(pay_exception, account_id)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


def setup_report(registration: MhrRegistration, response_json: dict, group: str, j_token, current_json: dict):
    """Perform all extra set up of the transfer report request data and add it to the queue."""
    response_json["usergroup"] = group
    if is_staff(j_token):
        response_json["username"] = reg_utils.get_affirmby(g.jwt_oidc_token_info)
        reg_utils.enqueue_registration_report(
            registration, response_json, ReportTypes.MHR_REGISTRATION_STAFF, current_json
        )
        del response_json["username"]
    else:
        if not response_json.get("affirmbyName"):
            response_json["affirmByName"] = reg_utils.get_affirmby(g.jwt_oidc_token_info)
        reg_utils.enqueue_registration_report(
            registration, response_json, ReportTypes.MHR_TRANSPORT_PERMIT, current_json
        )
    del response_json["usergroup"]
    if response_json.get("previousStatus"):
        del response_json["previousStatus"]
    if response_json.get("ownerGroups"):
        del response_json["ownerGroups"]


def get_transaction_type(request_json) -> str:
    """Derive the payment transaction type from the request payload."""
    tran_type: str = TransactionTypes.TRANSPORT_PERMIT
    if "amendment" in request_json and request_json.get("amendment"):
        tran_type = TransactionTypes.AMEND_PERMIT
    elif "extension" in request_json and request_json.get("extension"):
        tran_type = TransactionTypes.TRANSPORT_PERMIT_EXT
    return tran_type


def verify_request(account_id: str, jwt_manager, sbc_staff: bool):
    """Derive the payment transaction type from the request payload."""
    if account_id is None or account_id.strip() == "":
        return resource_utils.account_required_response()
    # Verify request JWT role
    if is_bcol_help(account_id, jwt_manager):
        return resource_utils.helpdesk_unauthorized_error_response("transport permit")
    if not authorized_role(jwt_manager, REQUEST_TRANSPORT_PERMIT):
        logger.error("User not staff or missing required role: " + REQUEST_TRANSPORT_PERMIT)
        # SBC staff can create permits and do not use MHR keycloak roles: allow if SBC staff
        if sbc_staff:
            logger.info(f"Identified SBC staff account {account_id}: request authorized.")
        else:
            return resource_utils.unauthorized_error_response(account_id)
    return None


def get_qs_location(request_json: dict, group: str, account_id: str) -> dict:
    """Try to get the qualified supplier information by account id and add it to the request for validation."""
    if group not in (DEALERSHIP_GROUP, MANUFACTURER_GROUP):
        return request_json
    qs_location: dict = None
    if group == MANUFACTURER_GROUP:
        manufacturer: MhrManufacturer = MhrManufacturer.find_by_account_id(account_id)
        if manufacturer:
            man_json = manufacturer.json
            qs_location = man_json.get("location")
    else:
        supplier = MhrQualifiedSupplier.find_by_account_id(account_id)
        if supplier:
            qs_location = supplier.json
    if qs_location:
        request_json["qsLocation"] = qs_location
    return request_json
