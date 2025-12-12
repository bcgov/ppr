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
"""API callback endpoint to complete credit card payment requests based on the payment status."""
from http import HTTPStatus

# import requests
from flask import Blueprint, request
from flask_cors import cross_origin

from mhr_api.exceptions import DatabaseException
from mhr_api.models import EventTracking, MhrDraft, MhrRegistration, MhrReviewRegistration, SearchResult
from mhr_api.models.mhr_draft import DRAFT_PAY_PENDING_PREFIX, DRAFT_STAFF_REVIEW_PREFIX
from mhr_api.models.registration_json_utils import cleanup_owner_groups, sort_owner_groups
from mhr_api.models.type_tables import (
    MhrOwnerStatusTypes,
    MhrRegistrationStatusTypes,
    MhrRegistrationTypes,
    MhrReviewStatusTypes,
)
from mhr_api.reports.v2.report_utils import ReportTypes
from mhr_api.resources import cc_payment_utils
from mhr_api.resources import registration_utils as reg_utils
from mhr_api.resources import utils as resource_utils
from mhr_api.resources.v1.search_results import enqueue_search_report
from mhr_api.resources.v1.transfers import set_owner_edit
from mhr_api.services.authz import is_reg_staff_account
from mhr_api.services.payment import StatusCodes
from mhr_api.utils.logging import logger

bp = Blueprint("PAY_CALLBACK", __name__, url_prefix="/api/v1/pay-callback")  # pylint: disable=invalid-name
ALLOWED_PAY_STATUS = [
    StatusCodes.CANCELLED.value,
    StatusCodes.COMPLETED.value,
    StatusCodes.DELETED.value,
    StatusCodes.PAID.value,
]
CALLBACK_MESSAGES = {
    resource_utils.CallbackExceptionCodes.UNKNOWN_ID: "01: no draft data found for invoice id={key_id}.",
    resource_utils.CallbackExceptionCodes.INVALID_ID: "02: payment previously processed for invoice id={key_id}.",
    resource_utils.CallbackExceptionCodes.DEFAULT: "04: default error for invoice id={key_id}.",
    resource_utils.CallbackExceptionCodes.SETUP_ERR: "10: setup failed for invoice id={key_id}.",
}
PAY_STATUS_MISSING_MSG = "Expected payment status missing in payload."
PAY_STATUS_INVALID_MSG = "Payment status {pay_status} not an allowed value."
PAY_CANCELLED_MSG = "Payment status cancelled/deleted: draft reverted."
PAY_NO_REG_MSG = "Change no MH found for MHR#={mhr_num}."
PAY_REG_SUCCESS_MSG = "Registration created reg_id={reg_id} MHR#={mhr_num}."
PAY_SEARCH_SUCCESS_MSG = "Search set to completed for search id={search_id}."
STAFF_REVIEW_PAY_CANCELLED = {"statusType": MhrReviewStatusTypes.PAY_CANCELLED.value}
STAFF_REVIEW_PAY_NEW = {"statusType": MhrReviewStatusTypes.NEW.value}


@bp.route("/<string:invoice_id>", methods=["POST", "OPTIONS"])
@cross_origin(origin="*")
def post_payment_callback(invoice_id: str):  # pylint: disable=too-many-return-statements
    """Resource to complete a credit card payment request."""
    try:
        logger.info(f"Payment callback starting invoice id={invoice_id}.")
        if invoice_id is None:
            return resource_utils.path_param_error_response("invoice ID")
        # Authenticate with request api key
        if not resource_utils.valid_api_key(request):
            return resource_utils.unauthorized_error_response("MHR pay callback invalid key.")
        # Verify the payload pay api status:
        request_json = request.get_json(silent=True)
        pay_status: str = request_json.get("statusCode") if request_json else None
        logger.info(f"pay callback request payload={request_json}")
        if not pay_status:
            return pay_callback_error("02", invoice_id, HTTPStatus.BAD_REQUEST, PAY_STATUS_MISSING_MSG)
        elif pay_status == StatusCodes.REVERSED.value:
            logger.warning(f"Ignoring pay status={pay_status} for invoice={invoice_id}: staff declined.")
            return {}, HTTPStatus.OK
        elif pay_status not in ALLOWED_PAY_STATUS:
            error_msg: str = PAY_STATUS_INVALID_MSG.format(pay_status=pay_status)
            return pay_callback_error("02", invoice_id, HTTPStatus.BAD_REQUEST, error_msg)

        search_id: int = get_search_id(invoice_id)
        if search_id and search_id > 0:
            return pay_callback_search(search_id, invoice_id)

        draft: MhrDraft = MhrDraft.find_by_invoice_id(invoice_id)
        if not draft:
            # Handles payment notification update previously successful.
            # PAY API is sending notifications for other payment methods, just log as a warning.
            logger.warning(f"No draft or search ID found matching invoice {invoice_id}, ignoring notification.")
            return {}, HTTPStatus.OK
        base_reg: MhrRegistration = None
        if draft.mhr_number and draft.registration_type != MhrRegistrationTypes.MHREG:
            base_reg = MhrRegistration.find_all_by_mhr_number(draft.mhr_number, draft.account_id, True)
        if not base_reg and draft.mhr_number and draft.registration_type != MhrRegistrationTypes.MHREG:
            error_msg: str = PAY_NO_REG_MSG.format(mhr_num=draft.mhr_number)
            return pay_callback_error("04", invoice_id, HTTPStatus.NOT_FOUND, error_msg)
        logger.info(f"Request valid for invoice id={invoice_id} draft id={draft.id}, creating registration.")
        cc_payment_utils.track_event("09", invoice_id, HTTPStatus.OK, f"Draft id={draft.id}")
        return complete_registration(draft, base_reg, request_json, invoice_id)
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, None, "POST pay callback event")
    except Exception as default_err:  # noqa: B902; return nicer default error
        return pay_callback_error(
            resource_utils.CallbackExceptionCodes.DEFAULT,
            invoice_id,
            HTTPStatus.INTERNAL_SERVER_ERROR,
            str(default_err),
        )


def get_search_id(invoice_id: str):
    """Try to get the search id if the payment is for a search request."""
    events = EventTracking.find_by_key_id(int(invoice_id))
    if not events:
        return None
    for event in events:
        if event.event_tracking_type == EventTracking.EventTrackingTypes.MHR_PAYMENT.value and event.message:
            message: str = str(event.message)
            if message.startswith("11"):
                tokens = message.split("*")
                if tokens and len(tokens) > 1:
                    search_id = int(tokens[1])
                    logger.info(f"get_search_id found id={search_id}")
                    return search_id
    return None


def pay_callback_search(search_id: int, invoice_id: str):
    """Handle a payment complete notification for a search request."""
    search_result: SearchResult = SearchResult.find_by_search_id(search_id)
    if not search_result:
        return pay_callback_error("13", invoice_id, HTTPStatus.NOT_FOUND)
    if not search_result.is_payment_pending():
        return pay_callback_error("14", invoice_id, HTTPStatus.BAD_REQUEST, f"Search id={search_id}")
    logger.info(f"Request valid for invoice id={invoice_id} search id={search_id}, marking search as completed.")
    cc_payment_utils.track_event("09", invoice_id, HTTPStatus.OK, f"Search id={search_id}")
    search_result.score = None
    search_result.save()
    logger.info(f"Search pending payment status removed for {search_id}.")
    enqueue_search_report(search_id)
    logger.info(f"Search report queued for {search_id}.")
    msg = PAY_SEARCH_SUCCESS_MSG.format(search_id=search_id)
    cc_payment_utils.track_event("10", invoice_id, HTTPStatus.OK, msg)
    return {}, HTTPStatus.OK


def pay_callback_error(code: str, key_id: int, status_code, message: str = None):
    """Return the payment event listener callback error response based on the code."""
    error: str = cc_payment_utils.track_event(code, key_id, status_code, message)
    return resource_utils.error_response(status_code, error)


def update_registration_status(draft: MhrDraft, base_reg: MhrRegistration):
    """For a change registration unlock the home. Update the ."""
    if base_reg and base_reg.status_type == MhrRegistrationStatusTypes.DRAFT:
        orig_status = draft.draft.get("status")
        logger.info(f"Reverting mhr {base_reg.mhr_number} status to {orig_status}")
        base_reg.status_type = orig_status
        base_reg.save()
        logger.info(f"Home status for MHR# {base_reg.mhr_number} restored to {orig_status}")
    else:
        logger.info("No existing home found: unlock status update skipped.")


def update_draft(draft: MhrDraft):
    """Update the draft to post registration state instead of payment pending."""
    draft_json = draft.draft
    if not draft_json.get("reviewPending"):
        draft.user_id = draft_json.get("username", None)
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
    elif draft_num.startswith(DRAFT_PAY_PENDING_PREFIX):
        draft.draft_number = draft_num[1:]
    draft.save()
    logger.info(f"Updated draft id={draft.id} number={draft.draft_number} userid={draft.user_id}")
    return {}, HTTPStatus.OK


def queue_report(new_reg: MhrRegistration, draft: MhrDraft, response_json: dict, report_type, current_json: dict):
    """Common report queue set up steps for the registration verification report generation."""
    response_json["usergroup"] = draft.draft.get("usergroup")
    if is_reg_staff_account(draft.account_id):
        if draft.draft.get("affirmByName"):
            response_json["username"] = draft.draft.get("affirmByName")
        reg_utils.enqueue_registration_report(new_reg, response_json, ReportTypes.MHR_REGISTRATION_STAFF, current_json)
    else:
        reg_utils.enqueue_registration_report(new_reg, response_json, report_type, current_json)


def queue_new_reg(draft: MhrDraft, current_reg: MhrRegistration, new_reg: MhrRegistration):
    """Set up the registration verification report generation."""
    new_reg.report_view = True
    response_json = new_reg.new_registration_json
    response_json = cleanup_owner_groups(response_json)
    queue_report(new_reg, draft, response_json, ReportTypes.MHR_REGISTRATION, None)


def queue_exemption(draft: MhrDraft, current_reg: MhrRegistration, new_reg: MhrRegistration):
    """Set up the registration verification report generation."""
    response_json = new_reg.json
    response_json["status"] = MhrRegistrationStatusTypes.EXEMPT
    # Add current location and owners for reporting
    current_reg.current_view = True
    current_json = current_reg.new_registration_json
    response_json["location"] = current_json.get("location")
    response_json["ownerGroups"] = current_json.get("ownerGroups")
    queue_report(new_reg, draft, response_json, ReportTypes.MHR_EXEMPTION, current_json)


def queue_permit(
    draft: MhrDraft, current_reg: MhrRegistration, new_reg: MhrRegistration, current_location, existing_status
):
    """Set up the registration verification report generation."""
    response_json = new_reg.json
    current_json = current_reg.new_registration_json
    current_json["location"] = current_location
    response_json["description"] = current_json.get("description")
    response_json["status"] = current_json.get("status")
    response_json["ownerGroups"] = current_json.get("ownerGroups")
    if response_json.get("amendment") or response_json.get("extension"):
        response_json["permitRegistrationNumber"] = current_json.get("permitRegistrationNumber", "")
        response_json["permitDateTime"] = current_json.get("permitDateTime", "")
        if response_json.get("note") and response_json["note"].get("expiryDateTime"):
            response_json["permitExpiryDateTime"] = response_json["note"].get("expiryDateTime")
            response_json["permitStatus"] = response_json["note"].get("status", "")
        else:
            response_json["permitExpiryDateTime"] = current_json.get("permitExpiryDateTime", "")
            response_json["permitStatus"] = current_json.get("permitStatus", "")
        if existing_status != current_json.get("status"):
            response_json["previousStatus"] = existing_status
    queue_report(new_reg, draft, response_json, ReportTypes.MHR_TRANSPORT_PERMIT, current_json)


def queue_transfer(draft: MhrDraft, current_reg: MhrRegistration, new_reg: MhrRegistration, current_owners):
    """Set up the registration verification report generation."""
    new_reg.change_registrations = [current_reg, *current_reg.change_registrations]
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


def complete_registration(draft: MhrDraft, base_reg: MhrRegistration, request_json: dict, invoice_id: str):
    """Process the registration based on the payload status and draft registration type."""
    invoice_id: str = draft.user_id
    try:
        update_registration_status(draft, base_reg)
        status: str = request_json.get("statusCode")
        reg_type: str = draft.registration_type
        logger.info(f"Completing registration for pay status={status} reg_type={reg_type}")
        if request_json.get("statusCode") in (StatusCodes.CANCELLED.value, StatusCodes.DELETED.value):
            cc_payment_utils.track_event("05", draft.user_id, HTTPStatus.OK, PAY_CANCELLED_MSG)
            if str(draft.draft_number).startswith(DRAFT_STAFF_REVIEW_PREFIX):
                review_reg: MhrReviewRegistration = MhrReviewRegistration.find_by_invoice_id(int(invoice_id))
                if review_reg:
                    logger.info(f"Cancelled/deleted payment updating staff review reg id={review_reg.id}")
                    review_reg.save_update(STAFF_REVIEW_PAY_CANCELLED, "System Pay API Callback")
            return update_draft(draft)
        if str(draft.draft_number).startswith(DRAFT_STAFF_REVIEW_PREFIX):
            review_reg: MhrReviewRegistration = MhrReviewRegistration.find_by_invoice_id(int(invoice_id))
            if review_reg:
                logger.info(f"Completed payment updating staff review reg id={review_reg.id}")
                review_reg.save_update(STAFF_REVIEW_PAY_NEW, "System Pay API Callback")
                return {}, HTTPStatus.OK
        new_reg: MhrRegistration = None
        if reg_type == MhrRegistrationTypes.MHREG:
            new_reg = cc_payment_utils.create_new_registration(draft)
            queue_new_reg(draft, base_reg, new_reg)
        elif reg_type == MhrRegistrationTypes.PERMIT:
            base_reg.current_view = True
            current_location = reg_utils.get_active_location(base_reg)
            existing_status: str = base_reg.status_type
            new_reg = cc_payment_utils.create_change_registration(draft, base_reg)
            queue_permit(draft, base_reg, new_reg, current_location, existing_status)
        elif reg_type == MhrRegistrationTypes.TRANS:
            base_reg.current_view = True
            current_owners = reg_utils.get_active_owners(base_reg)
            new_reg = cc_payment_utils.create_change_registration(draft, base_reg)
            queue_transfer(draft, base_reg, new_reg, current_owners)
        elif reg_type in (MhrRegistrationTypes.EXEMPTION_RES, MhrRegistrationTypes.EXEMPTION_NON_RES):
            new_reg = cc_payment_utils.create_change_registration(draft, base_reg)
            queue_exemption(draft, base_reg, new_reg)
        msg: str = None
        if new_reg:
            msg = PAY_REG_SUCCESS_MSG.format(reg_id=new_reg.id, mhr_num=new_reg.mhr_number)
        cc_payment_utils.track_event("10", draft.user_id, HTTPStatus.OK, msg)
        return update_draft(draft)
    except Exception as default_err:  # noqa: B902; return nicer default error
        return pay_callback_error(
            resource_utils.CallbackExceptionCodes.DEFAULT,
            invoice_id,
            HTTPStatus.INTERNAL_SERVER_ERROR,
            str(default_err),
        )
