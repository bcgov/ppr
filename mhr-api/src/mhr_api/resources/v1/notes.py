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

from flask import Blueprint, g, jsonify, request
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils

from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.models import MhrRegistration
from mhr_api.models.type_tables import MhrDocumentTypes
from mhr_api.reports.v2.report_utils import ReportTypes
from mhr_api.resources import registration_utils as reg_utils
from mhr_api.resources import utils as resource_utils
from mhr_api.resources.v1.exemptions import submit_exemption
from mhr_api.services.authz import get_group, is_staff
from mhr_api.services.payment import TransactionTypes
from mhr_api.services.payment.exceptions import SBCPaymentException
from mhr_api.utils.auth import jwt
from mhr_api.utils.logging import logger

bp = Blueprint("NOTES1", __name__, url_prefix="/api/v1/notes")  # pylint: disable=invalid-name


@bp.route("/<string:mhr_number>", methods=["POST", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def post_notes(mhr_number: str):  # pylint: disable=too-many-return-statements,too-many-branches,too-many-locals
    """Create a new unit note registration."""
    account_id = ""
    try:
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        logger.info(f"Starting new note mhr={mhr_number}, account={account_id}")
        if account_id is None or account_id.strip() == "":
            return resource_utils.account_required_response()
        # Verify request JWT role
        request_json = request.get_json(silent=True)
        if not is_staff(jwt):
            logger.error("User not staff: unit note registrations are registries staff only.")
            return resource_utils.unauthorized_error_response(account_id)

        # Not found or not allowed to access throw exceptions.
        current_reg: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_number, account_id, True)
        if request_json.get("note") and request_json["note"].get("documentType", "") in (
            MhrDocumentTypes.EXRS,
            MhrDocumentTypes.EXNR,
        ):
            request_json["documentId"] = request_json["note"].get("documentId", "")
            request_json["nonResidential"] = request_json["note"].get("documentType", "") == MhrDocumentTypes.EXNR
            return submit_exemption(current_reg, account_id, request_json, request, jwt)

        # Validate request against the schema.
        valid_format, errors = schema_utils.validate(request_json, "noteRegistration", "mhr")
        # Additional validation not covered by the schema.
        extra_validation_msg = resource_utils.validate_note(current_reg, request_json, is_staff(jwt), get_group(jwt))

        if not valid_format or extra_validation_msg != "":
            return resource_utils.validation_error_response(errors, reg_utils.VAL_ERROR, extra_validation_msg)
        # Set up the registration, pay, and save the data.
        group: str = get_group(jwt)
        registration = reg_utils.pay_and_save_note(
            request, current_reg, request_json, account_id, group, get_transaction_type(request_json)
        )
        logger.debug(f"building note response json for {mhr_number}")
        registration.change_registrations = [current_reg, *current_reg.change_registrations]
        response_json = registration.json
        # Return report if request header Accept MIME type is application/pdf.
        if resource_utils.is_pdf(request):
            logger.info("Report not yet available: returning JSON.")
        # reg_utils.enqueue_registration_report(registration, response_json, ReportTypes.MHR_EXEMPTION)
        current_reg.current_view = True
        current_json = current_reg.new_registration_json
        response_json["usergroup"] = group
        if is_staff(jwt):
            response_json["username"] = reg_utils.get_affirmby(g.jwt_oidc_token_info)
            reg_utils.enqueue_registration_report(
                registration, response_json, ReportTypes.MHR_REGISTRATION_STAFF, current_json
            )
            del response_json["username"]
        else:
            reg_utils.enqueue_registration_report(registration, response_json, ReportTypes.MHR_NOTE, current_json)
        del response_json["usergroup"]
        return jsonify(response_json), HTTPStatus.CREATED
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "POST mhr note id=" + account_id)
    except SBCPaymentException as pay_exception:
        return resource_utils.pay_exception_response(pay_exception, account_id)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


def get_transaction_type(request_json) -> str:
    """Derive the payment transaction type from unit note document type."""
    tran_type: str = TransactionTypes.UNIT_NOTE
    if request_json.get("note") and request_json["note"].get("documentType", ""):
        doc_type: str = request_json["note"].get("documentType")
        if doc_type == MhrDocumentTypes.TAXN:
            tran_type = TransactionTypes.UNIT_NOTE_TAXN
        elif doc_type == MhrDocumentTypes.REG_102:
            tran_type = TransactionTypes.UNIT_NOTE_102
        elif doc_type in (MhrDocumentTypes.REST, MhrDocumentTypes.NPUB, MhrDocumentTypes.NCON, MhrDocumentTypes.CAUE):
            tran_type = TransactionTypes.UNIT_NOTE_OTHER
    return tran_type
