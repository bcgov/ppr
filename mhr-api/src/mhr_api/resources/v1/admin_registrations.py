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
import copy
from http import HTTPStatus

from flask import Blueprint, g, jsonify, request
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils

from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.models import MhrRegistration, registration_json_utils
from mhr_api.models.registration_json_utils import cleanup_owner_groups, sort_owner_groups
from mhr_api.models.type_tables import (
    MhrDocumentTypes,
    MhrNoteStatusTypes,
    MhrOwnerStatusTypes,
    MhrRegistrationStatusTypes,
    MhrRegistrationTypes,
)
from mhr_api.reports.v2.report_utils import ReportTypes
from mhr_api.resources import registration_utils as reg_utils
from mhr_api.resources import utils as resource_utils
from mhr_api.services.authz import get_group, is_all_staff_account, is_bcol_help, is_sbc_office_account, is_staff
from mhr_api.services.payment import TransactionTypes
from mhr_api.services.payment.exceptions import SBCPaymentException
from mhr_api.utils.auth import jwt
from mhr_api.utils.logging import logger

bp = Blueprint(
    "ADMIN_REGISTRATIONS1", __name__, url_prefix="/api/v1/admin-registrations"  # pylint: disable=invalid-name
)
# Mapping from doc type to pay transaction type
DOC_TO_TRANSACTION_TYPE = {
    MhrDocumentTypes.NRED: TransactionTypes.UNIT_NOTE.value,
    MhrDocumentTypes.STAT: TransactionTypes.ADMIN_RLCHG.value,
    MhrDocumentTypes.REGC_STAFF: TransactionTypes.CORRECTION.value,
    MhrDocumentTypes.REGC_CLIENT: TransactionTypes.CORRECTION.value,
    MhrDocumentTypes.PUBA: TransactionTypes.AMENDMENT.value,
    MhrDocumentTypes.EXRE: TransactionTypes.REGISTRATION.value,
    MhrDocumentTypes.CANCEL_PERMIT: TransactionTypes.CANCEL_PERMIT.value,
}


@bp.route("/<string:mhr_number>", methods=["POST", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def post_admin_registration(mhr_number: str):  # pylint: disable=too-many-return-statements,too-many-branches
    """Create a new admin registration."""
    account_id = ""
    try:
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        logger.info(f"Starting new admin reg mhr={mhr_number}, account={account_id}")
        if account_id is None or account_id.strip() == "":
            return resource_utils.account_required_response()
        # Verify request JWT role
        request_json = request.get_json(silent=True)
        doc_type = request_json.get("documentType", "")
        if is_bcol_help(account_id, jwt) or (not is_staff(jwt) and doc_type != MhrDocumentTypes.CANCEL_PERMIT):
            logger.error("User not staff or not cancel permit: admin registrations are staff only.")
            return resource_utils.unauthorized_error_response(account_id)
        # Not found throws exception.
        current_reg: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_number, account_id, True)
        is_all_staff: bool = is_staff(jwt) or is_all_staff_account(account_id)
        if (
            not is_all_staff
            and doc_type == MhrDocumentTypes.CANCEL_PERMIT
            and is_sbc_office_account(jwt.get_token_auth_header(), account_id, jwt)
        ):
            is_all_staff = True
        if not is_all_staff and doc_type == MhrDocumentTypes.CANCEL_PERMIT:
            can_edit: bool = False
            if current_reg.change_registrations:
                for reg in current_reg.change_registrations:
                    if (
                        reg.registration_type in (MhrRegistrationTypes.PERMIT, MhrRegistrationTypes.AMENDMENT)
                        and reg.notes
                        and reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE
                        and account_id == reg.account_id
                    ):
                        can_edit = True
            if not can_edit:
                logger.error(f"Non-staff cancel permit account id={account_id} does not match permit.")
                return resource_utils.unauthorized_error_response(account_id)

        if request_json.get("location") and request_json["location"].get("address"):
            # Location may have no street - replace with blank to pass validation
            if not request_json["location"]["address"].get("street"):
                request_json["location"]["address"]["street"] = " "
            # Location may not have a postal code when in Canada
            # Address schema validation requires a postal code in Canada.
            # Add an empty value to pass schema validation.
            if not request_json["location"]["address"].get("postalCode"):
                request_json["location"]["address"]["postalCode"] = ""
        # Validate request against the schema.
        valid_format, errors = schema_utils.validate(request_json, "adminRegistration", "mhr")
        # Additional validation not covered by the schema.
        extra_validation_msg = resource_utils.validate_admin_registration(current_reg, request_json, is_all_staff)
        if not valid_format or extra_validation_msg != "":
            return resource_utils.validation_error_response(errors, reg_utils.VAL_ERROR, extra_validation_msg)

        return save_registration(request, request_json, current_reg, account_id, mhr_number)
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "POST mhr note id=" + account_id)
    except SBCPaymentException as pay_exception:
        return resource_utils.pay_exception_response(pay_exception, account_id)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


def save_registration(req: request, request_json: dict, current_reg: MhrRegistration, account_id: str, mhr_number: str):
    """Perform the remaining set up the registration, pay, save the data, set up the report request."""
    group: str = get_group(jwt)
    # Get current location and owners before updating for batch JSON (amendment, correction, location change).
    current_reg.current_view = True
    current_json = current_reg.new_registration_json
    existing_status = current_json.get("status")
    if request_json.get("documentType", "") == MhrDocumentTypes.CANCEL_PERMIT:
        request_json["location"] = registration_json_utils.get_permit_previous_location_json(current_reg)
    registration = reg_utils.pay_and_save_admin(
        req, current_reg, request_json, account_id, group, get_transaction_type(request_json)
    )
    logger.debug(f"building admin reg response json for {mhr_number}")
    registration.change_registrations = current_reg.change_registrations
    response_json = registration.json
    # logger.info(response_json)
    response_json = registration_json_utils.set_home_status_json(current_reg, response_json, existing_status)
    if resource_utils.is_pdf(request):
        logger.info("Report not yet available: returning JSON.")
    if request_json.get("documentType", "") == MhrDocumentTypes.EXRE:
        setup_report_exre(registration, response_json, current_json, group, current_reg)
        response_json = cleanup_owner_groups(response_json)
        return jsonify(response_json), HTTPStatus.CREATED

    if request_json.get("documentType", "") == MhrDocumentTypes.CANCEL_PERMIT:
        response_json["previousLocation"] = current_json.get("location")
    setup_report(registration, response_json, current_json, group, current_reg)
    response_json = cleanup_owner_groups(response_json)
    return jsonify(response_json), HTTPStatus.CREATED


def setup_report_exre(
    registration: MhrRegistration,  # pylint: disable=too-many-branches; 1 more
    response_json: dict,
    current_json: dict,
    group: str,
    current_reg: MhrRegistration,
):
    """Update the registration data for reporting and publish the registration event."""
    report_json = copy.deepcopy(response_json)
    report_json["usergroup"] = group
    report_json["username"] = reg_utils.get_affirmby(g.jwt_oidc_token_info)
    if not report_json.get("location"):
        report_json["location"] = current_json.get("location")
    else:
        report_json["location"]["corrected"] = True
    if not report_json.get("description"):
        report_json["description"] = current_json.get("description")
    else:
        report_json["description"]["corrected"] = True
    if not response_json.get("addOwnerGroups") and not response_json.get("deleteOwnerGroups"):
        report_json["ownerGroups"] = current_json.get("ownerGroups")
    else:  # owners changed, set the current owners in the report.
        add_groups = response_json.get("addOwnerGroups")  # Use same report setup as transfers
        if add_groups:
            if not response_json.get("deleteOwnerGroups"):
                delete_groups = []
                for delete_group in current_reg.owner_groups:
                    if (
                        delete_group.change_registration_id == registration.id
                        and delete_group.status_type == MhrOwnerStatusTypes.PREVIOUS
                    ):
                        delete_groups.append(delete_group.json)
                response_json["deleteOwnerGroups"] = delete_groups
        report_json["ownerGroups"] = get_report_groups(response_json, current_json, add_groups)
    if "deleteOwnerGroups" in report_json:
        del report_json["deleteOwnerGroups"]
    if "addOwnerGroups" in report_json:
        del report_json["addOwnerGroups"]
    reg_utils.enqueue_registration_report(registration, report_json, ReportTypes.MHR_REGISTRATION_STAFF, current_json)


def setup_report(
    registration: MhrRegistration, response_json: dict, current_json: dict, group: str, current_reg: MhrRegistration
):
    """Update the registration data for reporting and publish the registration event."""
    report_json = copy.deepcopy(response_json)
    report_json["usergroup"] = group
    report_json["username"] = reg_utils.get_affirmby(g.jwt_oidc_token_info)
    if response_json.get("addOwnerGroups") or response_json.get("deleteOwnerGroups"):
        add_groups = response_json.get("addOwnerGroups")  # Use same report setup as transfers
        if add_groups:
            if not response_json.get("deleteOwnerGroups"):
                delete_groups = []
                for delete_group in current_reg.owner_groups:
                    if (
                        delete_group.change_registration_id == registration.id
                        and delete_group.status_type == MhrOwnerStatusTypes.PREVIOUS
                    ):
                        delete_groups.append(delete_group.json)
                response_json["deleteOwnerGroups"] = delete_groups
        report_json["ownerGroups"] = get_report_groups(response_json, current_json, add_groups)
    if "deleteOwnerGroups" in report_json:
        del report_json["deleteOwnerGroups"]
    if "addOwnerGroups" in report_json:
        del report_json["addOwnerGroups"]
    reg_utils.enqueue_registration_report(registration, report_json, ReportTypes.MHR_REGISTRATION_STAFF, current_json)


def get_report_groups(response_json: dict, current_json: dict, add_groups: dict) -> dict:
    """Get the current owner groups after a correction or amendment change."""
    new_groups = []
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
    return sort_owner_groups(new_groups, True)


def get_transaction_type(request_json: dict) -> str:
    """Map the admin registration document type to the pay transaction type."""
    if DOC_TO_TRANSACTION_TYPE.get(request_json.get("documentType", "")):
        return DOC_TO_TRANSACTION_TYPE.get(request_json.get("documentType"))
    return TransactionTypes.UNIT_NOTE


def get_previous_status(existing_status: str, current_reg: MhrRegistration, reg_id: int) -> str:
    """Conditinally set the registration status before a correction/amendment status update."""
    prev_status = existing_status
    if prev_status == MhrRegistrationStatusTypes.EXEMPT and current_reg.change_registrations:
        for reg in current_reg.change_registrations:
            if (
                reg.notes
                and reg.notes[0].document_type in (MhrDocumentTypes.EXNR, MhrDocumentTypes.EXRS)
                and reg.notes[0].change_registration_id == reg_id
                and reg.notes[0].status_type == MhrNoteStatusTypes.CANCELLED
            ):
                prev_status = "EXEMPT_EXEMPTION"
    return prev_status
