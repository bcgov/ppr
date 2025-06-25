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
"""API endpoints for maintaining processing aysnchronous callback. Initially mail verification reports."""
import json
from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

from ppr_api.callback.document_storage.storage_service import DocumentTypes, GoogleStorageService
from ppr_api.callback.utils.exceptions import ReportDataException, ReportException, StorageException
from ppr_api.exceptions import DatabaseException
from ppr_api.models import Draft, EventTracking, FinancingStatement, MailReport, Registration, SearchResult
from ppr_api.models import utils as model_utils
from ppr_api.reports import get_callback_pdf
from ppr_api.reports.v2.report_utils import ReportTypes
from ppr_api.resources import cc_payment_utils
from ppr_api.resources import utils as resource_utils
from ppr_api.services.payment import StatusCodes
from ppr_api.utils.logging import logger

bp = Blueprint("CALLBACKS1", __name__, url_prefix="/api/v1/callbacks")  # pylint: disable=invalid-name
START_TS_PARAM = "startDateTime"
END_TS_PARAM = "endDateTime"
JOB_ID_PARAM = "jobId"
PAY_STATUS_MISSING_MSG = "Expected payment status missing in payload."
PAY_STATUS_INVALID_MSG = "Payment status {pay_status} not an allowed value."
PAY_CANCELLED_MSG = "Payment status cancelled/deleted: draft reverted."
PAY_NO_REG_MSG = "Change no financing statement found for base reg num={reg_num}."
PAY_REG_SUCCESS_MSG = "Registration created fs id={fs_id} reg_id={reg_id} reg num={reg_num}."
PAY_SEARCH_SUCCESS_MSG = "Search selection allowed for search id={search_id}."
ALLOWED_PAY_STATUS = [
    StatusCodes.CANCELLED.value,
    StatusCodes.COMPLETED.value,
    StatusCodes.DELETED.value,
    StatusCodes.PAID.value,
]


@bp.route("/mail-report", methods=["POST", "OPTIONS"])
@cross_origin(origin="*")
def post_mail_report():  # pylint: disable=too-many-return-statements
    """Registration id and party id are in the payload."""
    request_json = request.get_json(silent=True)
    registration_id: int = request_json.get("registrationId", -1)
    party_id: int = request_json.get("partyId", -1)
    try:
        # Authenticate with request api key
        if not resource_utils.valid_api_key(request):
            return resource_utils.unauthorized_error_response("Verification report callback")

        message: str = None
        status = HTTPStatus.BAD_REQUEST
        if registration_id < 0:
            message = "Mail verification statement no registration ID."
        elif party_id < 0:
            message = "Mail verification statement no party ID."
        else:
            # If no mail report record we're done.
            mail_report: MailReport = MailReport.find_by_registration_party_id(registration_id, party_id)
            if not mail_report:
                message = "No mail report data found for the registration id, party id."
                status = HTTPStatus.NOT_FOUND

        if message:
            return resource_utils.error_response(status, message)

        if mail_report.doc_storage_url:
            logger.debug("Report {mail_report.doc_storage_url} already exists.")
            return {}, HTTPStatus.OK, {"Content-Type": "application/json"}
        # Generate the report, upload it to cloud storage, update the status.
        return generate_mail_callback_report(mail_report)
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(
            db_exception, None, "POST callback mail verification report DB error."
        )
    except Exception as default_err:  # noqa: B902; return nicer default error
        return mail_callback_error(
            mail_report, HTTPStatus.INTERNAL_SERVER_ERROR, "Callback default error: " + str(default_err)
        )


@bp.route("/mail-report", methods=["GET", "OPTIONS"])
@cross_origin(origin="*")
def get_mail_list():
    """Fetch recent event storage names by request parameter startDateTime and optional endDateTime."""
    start_ts = request.args.get(START_TS_PARAM, None)
    end_ts = request.args.get(END_TS_PARAM, None)
    job_id = request.args.get(JOB_ID_PARAM, None)
    try:
        # Authenticate with request api key
        if not resource_utils.valid_api_key(request):
            return resource_utils.unauthorized_error_response("Verification report callback")

        message: str = None
        status = HTTPStatus.BAD_REQUEST
        start = None
        end = None
        if not start_ts:
            message = "Request parameter startDateTime is required."
        else:
            try:
                start = model_utils.ts_from_iso_format(start_ts)
            except Exception:  # noqa: B902; validation error.
                message = "Request parameter startDateTime value is invalid"
        if end_ts:
            try:
                end = model_utils.ts_from_iso_format(end_ts)
            except Exception:  # noqa: B902; validation error
                message = "Request parameter endDateTime value is invalid"
        if end and start and end <= start:
            message = "Request timestamp range is invalid"

        if message:
            return resource_utils.error_response(status, message)
        results = MailReport.find_list_by_timestamp(start, end, job_id)
        return jsonify(results), HTTPStatus.OK
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, None, "GET callback mail reports list DB error.")
    except Exception as default_err:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_err)


@bp.route("/pay/<string:invoice_id>", methods=["POST", "OPTIONS"])
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
        elif pay_status not in ALLOWED_PAY_STATUS:
            error_msg: str = PAY_STATUS_INVALID_MSG.format(pay_status=pay_status)
            return pay_callback_error("02", invoice_id, HTTPStatus.BAD_REQUEST, error_msg)

        search_id: int = get_search_id(invoice_id)
        if search_id and search_id > 0:
            return pay_callback_search(search_id, invoice_id)

        draft: Draft = Draft.find_by_invoice_id(invoice_id)
        if not draft:
            # PAY API is sending notifications for other payment methods, just log as a warning.
            logger.warning(f"No draft or search ID found matching invoice {invoice_id}, ignoring notification.")
            return {}, HTTPStatus.OK
        statement: FinancingStatement = None
        if draft.registration_number:
            statement = FinancingStatement.find_by_registration_number(
                draft.registration_number, draft.account_id, True, True
            )
        if not statement and draft.registration_number:
            error_msg: str = PAY_NO_REG_MSG.format(reg_num=draft.registration_number)
            return pay_callback_error("04", invoice_id, HTTPStatus.NOT_FOUND, error_msg)
        logger.info(f"Request valid for invoice id={invoice_id}, creating registration.")
        cc_payment_utils.track_event("09", invoice_id, HTTPStatus.OK, None)
        return complete_registration(draft, statement, request_json)
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, None, "POST pay callback event")
    except Exception as default_err:  # noqa: B902; return nicer default error
        return pay_callback_error("00", invoice_id, HTTPStatus.INTERNAL_SERVER_ERROR, str(default_err))


def get_search_id(invoice_id: str):
    """Try to get the search id if the payment is for a search request."""
    events = EventTracking.find_by_key_id(int(invoice_id))
    if not events:
        return None
    for event in events:
        if event.event_tracking_type == EventTracking.EventTrackingTypes.PPR_PAYMENT.value and event.message:
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
    msg = PAY_SEARCH_SUCCESS_MSG.format(search_id=search_id)
    cc_payment_utils.track_event("15", invoice_id, HTTPStatus.OK, msg)
    return {}, HTTPStatus.OK


def pay_callback_error(code: str, key_id: int, status_code, message: str = None):
    """Return the payment event listener callback error response based on the code."""
    error: str = cc_payment_utils.track_event(code, key_id, status_code, message)
    return resource_utils.error_response(status_code, error)


def complete_registration(draft: Draft, statement: FinancingStatement, request_json: dict):
    """Process the registration based on the payload status and draft registration type."""
    invoice_id: str = draft.user_id
    try:
        if statement:
            update_registration_status(statement.registration[0])
        else:
            logger.info("No existing financing statemen: unlock base registration skipped.")
        status: str = request_json.get("statusCode")
        reg_type: str = draft.registration_type
        reg_class: str = draft.registration_type_cl
        logger.info(f"Completing registration for pay status={status} reg type={reg_type} class={reg_class}")
        if request_json.get("statusCode") in (StatusCodes.CANCELLED.value, StatusCodes.DELETED.value):
            cc_payment_utils.track_event("05", draft.user_id, HTTPStatus.OK, PAY_CANCELLED_MSG)
            return update_draft(draft)
        new_reg: Registration = None
        report_json: dict = None
        report_type: str = ReportTypes.FINANCING_STATEMENT_REPORT.value
        if reg_class == model_utils.REG_CLASS_RENEWAL:
            new_reg: Registration = cc_payment_utils.create_change_registration(draft, statement)
            report_json = new_reg.verification_json("renewalRegistrationNumber")
        elif reg_class in (model_utils.REG_CLASS_AMEND, model_utils.REG_CLASS_AMEND_COURT):
            new_reg: Registration = cc_payment_utils.create_change_registration(draft, statement)
            resource_utils.queue_secured_party_verification(new_reg)
            report_json = new_reg.verification_json("amendmentRegistrationNumber")
        elif reg_class in (model_utils.REG_CLASS_PPSA, model_utils.REG_CLASS_MISC, model_utils.REG_CLASS_CROWN):
            statement: FinancingStatement = cc_payment_utils.create_new_statement(draft)
            new_reg = statement.registration[0]
            report_json = statement.json

        resource_utils.enqueue_registration_report(new_reg, report_json, report_type)
        msg = PAY_REG_SUCCESS_MSG.format(
            fs_id=new_reg.financing_id, reg_id=new_reg.id, reg_num=new_reg.registration_num
        )
        cc_payment_utils.track_event("10", draft.user_id, HTTPStatus.OK, msg)
        return update_draft(draft)
    except Exception as default_err:  # noqa: B902; return nicer default error
        return pay_callback_error("00", invoice_id, HTTPStatus.INTERNAL_SERVER_ERROR, str(default_err))


def update_registration_status(base_reg: Registration):
    """For a change registration unlock the home. Update the ."""
    if base_reg and base_reg.ver_bypassed == cc_payment_utils.REG_STATUS_LOCKED:
        base_reg.ver_bypassed = "N"
        base_reg.save()
        logger.info(f"Unlocked base_registration {base_reg.registration_num}")


def update_draft(draft: Draft):
    """Update the draft to post registration state instead of payment pending."""
    draft_json = draft.draft
    draft.user_id = draft_json.get("username", None)
    if draft_json.get("username"):
        del draft_json["username"]
    if draft_json.get("accountId"):
        del draft_json["accountId"]
    if "paymentPending" in draft_json:
        del draft_json["paymentPending"]
    draft.draft = draft_json
    doc_num: str = str(draft.document_number)
    if doc_num.startswith(cc_payment_utils.DRAFT_PAY_PENDING_PREFIX):
        draft.document_number = doc_num[1:]
    draft.save()
    logger.info(f"Updated draft id={draft.id} number={draft.document_number} userid={draft.user_id}")
    return {}, HTTPStatus.OK


def mail_callback_error(mail_report: MailReport, status_code: int = 500, message: str = None):
    """Update the status and return an error response."""
    logger.error(message)
    if mail_report:
        try:
            mail_report.update_retry_count(status_code, message)
            mail_report.save()
            # if mail_report.retry_count < current_app.config.get('EVENT_MAX_RETRIES'):
            #    resource_utils.enqueue_verification_report(mail_report.registration_id, mail_report.party_id)
        except Exception as default_err:  # noqa: B902; return nicer default error
            logger.error("Attempt to setup callback retry failed: " + str(default_err))
    return resource_utils.error_response(status_code, message)


def generate_mail_callback_report(mail_report: MailReport):  # pylint: disable=too-many-return-statements
    """Attempt to generate and store a mail report. Record the status."""
    try:
        logger.info(f"Generating mail report for mail report id={mail_report.id}.")
        raw_data, status_code, headers = get_callback_pdf(
            mail_report.report_data, None, ReportTypes.VERIFICATION_STATEMENT_MAIL_REPORT, None, None
        )
        if not raw_data or not status_code:
            return mail_callback_error(
                mail_report, HTTPStatus.INTERNAL_SERVER_ERROR, "Callback report generation no data or status code."
            )
        logger.debug("report api call status=" + str(status_code) + " headers=" + json.dumps(headers))
        if status_code not in (HTTPStatus.OK, HTTPStatus.CREATED):
            message = f"Status code={status_code}. Response: " + raw_data.get_data(as_text=True)
            return mail_callback_error(mail_report, HTTPStatus.INTERNAL_SERVER_ERROR, message)
        doc_name = model_utils.get_mail_doc_storage_name(
            mail_report.create_ts, mail_report.registration_id, mail_report.party_id
        )
        logger.info(f"Saving mail report output to doc storage: name={doc_name}.")
        response = GoogleStorageService.save_document(doc_name, raw_data, DocumentTypes.MAIL_DEFAULT)
        logger.info(f"Save document storage response: {response}.")
        mail_report.update_storage_url(doc_name, HTTPStatus.OK)
        mail_report.save()
        return {}, HTTPStatus.OK, {"Content-Type": "application/json"}
    except ReportException as report_err:
        return mail_callback_error(
            mail_report, HTTPStatus.INTERNAL_SERVER_ERROR, "Callback report generation error: " + str(report_err)
        )
    except ReportDataException as report_data_err:
        return mail_callback_error(
            mail_report, HTTPStatus.INTERNAL_SERVER_ERROR, "Callback report data error: " + str(report_data_err)
        )
    except StorageException as storage_err:
        return mail_callback_error(
            mail_report, HTTPStatus.INTERNAL_SERVER_ERROR, "Callback report cloud storage error: " + str(storage_err)
        )
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(
            db_exception, None, "POST callback mail verification report DB error."
        )
    except Exception as default_err:  # noqa: B902; return nicer default error
        return mail_callback_error(
            mail_report, HTTPStatus.INTERNAL_SERVER_ERROR, "Callback default error: " + str(default_err)
        )
