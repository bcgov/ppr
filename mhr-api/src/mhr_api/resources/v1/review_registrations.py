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
"""API endpoints for requests to view and update staff review registrations."""
from http import HTTPStatus

from flask import Blueprint, g, jsonify, request
from flask_cors import cross_origin

from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.models import MhrDraft, MhrRegistration, MhrReviewRegistration
from mhr_api.models.mhr_draft import DRAFT_STAFF_REVIEW_PREFIX
from mhr_api.models.registration_json_utils import sort_owner_groups
from mhr_api.models.registration_utils import AccountRegistrationParams
from mhr_api.models.type_tables import MhrOwnerStatusTypes, MhrRegistrationStatusTypes, MhrReviewStatusTypes
from mhr_api.reports.v2.report_utils import ReportTypes
from mhr_api.resources import registration_utils as reg_utils
from mhr_api.resources import staff_review_utils
from mhr_api.resources import utils as resource_utils
from mhr_api.resources.v1.transfers import set_owner_edit
from mhr_api.services.authz import authorized, is_staff
from mhr_api.services.doc_service import doc_id_lookup_staff
from mhr_api.services.payment.exceptions import SBCPaymentException
from mhr_api.services.payment.payment import Payment
from mhr_api.utils.auth import jwt
from mhr_api.utils.logging import logger

bp = Blueprint("REVIEWS1", __name__, url_prefix="/api/v1/reviews")  # pylint: disable=invalid-name

STATUS_CHANGE_INVALID = "Request payload statusType={status_type} is not allowed with the current state {current}."


@bp.route("", methods=["GET", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def get_review_registrations_summary():
    """Get staff review registrations summary list."""
    account_id = ""
    try:
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt) or not is_staff(jwt):
            return resource_utils.unauthorized_error_response(account_id)
        params: AccountRegistrationParams = AccountRegistrationParams(account_id=account_id, sbc_staff=True)
        params = resource_utils.get_account_registration_params(request, params)
        reg_list = MhrReviewRegistration.find_all(params)
        return jsonify(reg_list), HTTPStatus.OK

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "GET staff review registrations summary.")
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("/<string:review_id>", methods=["GET", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def get_review_registrations(review_id: str):
    """Get registration information for an individual registration by review ID."""
    try:
        logger.info(f"get_review_registrations review_id={review_id}")
        if review_id is None:
            return resource_utils.path_param_error_response("Review Registration ID")
        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt) or not is_staff(jwt):
            return resource_utils.unauthorized_error_response(account_id)

        review_reg: MhrReviewRegistration = MhrReviewRegistration.find_by_id(review_id)
        if not review_reg:
            return resource_utils.not_found_error_response("Staff Review Registration", review_id)
        if review_reg.document_id and request.args.get("includeDocuments", False):
            reg_json = review_reg.json
            reg_json["documents"] = doc_id_lookup_staff(
                review_reg.document_id, account_id, request.headers.get("Authorization")
            )
            return jsonify(reg_json), HTTPStatus.OK
        return jsonify(review_reg.json), HTTPStatus.OK
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, f"GET review reg id={review_id}.")
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("/<string:review_id>", methods=["PATCH", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def update_review_registrations(review_id: str):
    """Update registration information for an individual registration by review ID."""
    try:
        logger.info(f"update_review_registrations review_id={review_id}")
        if review_id is None:
            return resource_utils.path_param_error_response("Review Registration ID")
        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt) or not is_staff(jwt):
            return resource_utils.unauthorized_error_response(account_id)
        review_reg: MhrReviewRegistration = MhrReviewRegistration.find_by_id(review_id)
        if not review_reg:
            return resource_utils.not_found_error_response("Staff Review Registration", review_id)
        request_json = request.get_json(silent=True)
        error_msg: str = validate_request_data(request_json, review_reg)
        if error_msg:
            return resource_utils.bad_request_response(error_msg)
        if review_reg.is_approved(request_json.get("statusType")):
            approve_registration(review_id, review_reg)
        elif review_reg.is_declined(request_json.get("statusType")):
            decline_registration(review_id, review_reg, request_json)
        review_reg.save_update(request_json, g.jwt_oidc_token_info.get("name"))
        return jsonify(review_reg.json), HTTPStatus.OK
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, f"PATCH review reg id={review_id}.")
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


def approve_registration(review_id: int, review_reg: MhrReviewRegistration):
    """Draft and registration updates when the registration is approved."""
    logger.info(f"Review approved for id {review_id}: creating registration.")
    draft: MhrDraft = MhrDraft.find_by_id(review_reg.draft_id)
    current_reg: MhrRegistration = MhrRegistration.find_all_by_mhr_number(
        review_reg.mhr_number, review_reg.account_id, True
    )
    current_reg.current_view = True
    current_owners = reg_utils.get_active_owners(current_reg)
    update_registration_status(review_reg, current_reg)
    new_reg: MhrRegistration = staff_review_utils.create_change_registration(draft, current_reg, review_reg)
    queue_transfer_report(draft, current_reg, new_reg, current_owners)
    update_draft(draft)


def decline_registration(review_id: int, review_reg: MhrReviewRegistration, request_json: dict):
    """Draft and registration updates when the registration is declined."""
    logger.info(f"Review declined for id {review_id} MHR {review_reg.mhr_number} {review_reg.registration_type}.")
    draft: MhrDraft = MhrDraft.find_by_id(review_reg.draft_id)
    current_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(
        review_reg.mhr_number, review_reg.account_id, True
    )
    update_registration_status(review_reg, current_reg)
    logger.info(f"Review id {review_id} refunding payment for invoice {review_reg.pay_invoice_id}")
    try:
        pay_response = Payment().cancel_payment(review_reg.pay_invoice_id)
        request_json["payRefund"] = f"Pay API refund response: {pay_response}"
        logger.info(f" Refund for invoice {review_reg.pay_invoice_id} response: {pay_response}")
    except SBCPaymentException as err:  # noqa: B902; wrapping exception
        request_json["payRefund"] = f"Pay API refund failed: {err.status_code}: {err.message}"
        logger.info(f" Refund for invoice {review_reg.pay_invoice_id} failed: {err.status_code}: {err.message}")
    update_draft(draft)


def update_registration_status(review_reg: MhrReviewRegistration, base_reg: MhrRegistration):
    """For a change registration unlock the home. Restore the home status type."""
    if base_reg.status_type == MhrRegistrationStatusTypes.DRAFT:
        orig_status = review_reg.registration_data.get("status")
        logger.info(f"Reverting mhr {base_reg.mhr_number} status to {orig_status}")
        base_reg.status_type = orig_status
        base_reg.save()
        logger.info(f"Home status for MHR# {base_reg.mhr_number} restored to {orig_status}")
    else:
        logger.info(f"MHR {base_reg.mhr_number} not in DRAFT state: unlock status update skipped.")


def update_draft(draft: MhrDraft):
    """Update the draft to post registration state instead of payment pending."""
    draft_json = draft.draft
    if draft_json.get("username"):
        del draft_json["username"]
    if draft_json.get("usergroup"):
        del draft_json["usergroup"]
    if draft_json.get("accountId"):
        del draft_json["accountId"]
    if draft_json.get("status"):
        del draft_json["status"]
    if "paymentPending" in draft_json:
        del draft_json["paymentPending"]
    if "reviewPending" in draft_json:
        del draft_json["reviewPending"]
    draft.draft = draft_json
    draft_num: str = str(draft.draft_number)
    if draft_num.startswith(DRAFT_STAFF_REVIEW_PREFIX):
        draft.draft_number = draft_num[2:]
    draft.save()
    logger.info(f"Draft {draft.id} updated for MHR {draft.mhr_number} reg type {draft.registration_type}")


def queue_transfer_report(draft: MhrDraft, current_reg: MhrRegistration, new_reg: MhrRegistration, current_owners):
    """Set up the registration verification report generation."""
    new_reg.change_registrations = current_reg.change_registrations
    response_json = new_reg.json
    current_reg.current_view = True
    current_json = current_reg.new_registration_json
    current_json["ownerGroups"] = current_owners
    add_groups = response_json.get("addOwnerGroups")
    add_groups = set_owner_edit(add_groups, current_reg, new_reg.reg_json, new_reg.id)
    new_groups = []
    if not response_json.get("deleteOwnerGroups"):
        delete_groups = []
        for group in current_reg.owner_groups:
            if group.change_registration_id == new_reg.id and group.status_type == MhrOwnerStatusTypes.PREVIOUS:
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
    if response_json.get("status") == "FROZEN":
        response_json["status"] = MhrRegistrationStatusTypes.ACTIVE
    queue_report(new_reg, draft, response_json, ReportTypes.MHR_TRANSFER, current_json)
    logger.info(f"Report queued reg id {new_reg.id} MHR {new_reg.mhr_number} reg type {new_reg.registration_type}")


def queue_report(new_reg: MhrRegistration, draft: MhrDraft, response_json: dict, report_type, current_json: dict):
    """Common report queue set up steps for the registration verification report generation."""
    response_json["usergroup"] = draft.draft.get("usergroup")
    reg_utils.enqueue_registration_report(new_reg, response_json, report_type, current_json)


def validate_request_data(request_json: dict, review_reg: MhrReviewRegistration) -> str:
    """Verify update request payload data."""
    if not request_json:
        return "Update review registration invalid: no payload data."
    error_msg: str = validate_status_type(request_json, review_reg)
    return error_msg


def validate_status_type(request_json: dict, review_reg: MhrReviewRegistration) -> str:
    """Verify request payload status type."""
    error_msg: str = ""
    if not request_json.get("statusType"):
        error_msg += "Required request payload statusType is missing."
    status_type: str = request_json.get("statusType")
    current: str = review_reg.status_type.value
    if status_type == current:
        return error_msg
    if status_type not in MhrReviewStatusTypes:
        error_msg += f"Request payload statusType={status_type} is invalid."
    elif (
        review_reg.status_type
        in (
            MhrReviewStatusTypes.PAY_CANCELLED,
            MhrReviewStatusTypes.PAY_PENDING,
            MhrReviewStatusTypes.APPROVED,
            MhrReviewStatusTypes.DECLINED,
        )
        and status_type != current
    ):
        error_msg += STATUS_CHANGE_INVALID.format(status_type=status_type, current=current)
    elif current == MhrReviewStatusTypes.NEW.value and status_type != MhrReviewStatusTypes.IN_REVIEW.value:
        error_msg += STATUS_CHANGE_INVALID.format(status_type=status_type, current=current)
    elif current == MhrReviewStatusTypes.IN_REVIEW.value and status_type not in (
        MhrReviewStatusTypes.DECLINED.value,
        MhrReviewStatusTypes.APPROVED.value,
        MhrReviewStatusTypes.NEW.value,
    ):
        error_msg += STATUS_CHANGE_INVALID.format(status_type=status_type, current=current)
    return error_msg
