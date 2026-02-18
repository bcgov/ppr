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
"""API endpoints for requests to maintain MH documents."""

from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.models import MhrRegistration
from mhr_api.models.registration_utils import get_qs_document_id
from mhr_api.models.type_tables import MhrRegistrationTypes
from mhr_api.reports.v2.report_utils import ReportTypes
from mhr_api.resources import registration_utils as reg_utils
from mhr_api.resources import utils as resource_utils
from mhr_api.services.authz import authorized, get_group, is_all_staff_account, is_staff
from mhr_api.services.doc_service import doc_id_lookup
from mhr_api.utils import validator_utils as registration_validator
from mhr_api.utils.auth import jwt
from mhr_api.utils.logging import logger

bp = Blueprint("DOCUMENTS1", __name__, url_prefix="/api/v1/documents")  # pylint: disable=invalid-name
# Mapping from DB registration class to API statement type
REG_TYPE_TO_REPORT_TYPE = {
    MhrRegistrationTypes.REG_STAFF_ADMIN: ReportTypes.MHR_ADMIN_REGISTRATION,
    MhrRegistrationTypes.MHREG: ReportTypes.MHR_REGISTRATION,
    MhrRegistrationTypes.MHREG_CONVERSION: ReportTypes.MHR_REGISTRATION,
    MhrRegistrationTypes.PERMIT: ReportTypes.MHR_TRANSPORT_PERMIT,
    MhrRegistrationTypes.PERMIT_EXTENSION: ReportTypes.MHR_TRANSPORT_PERMIT,
    MhrRegistrationTypes.AMENDMENT: ReportTypes.MHR_TRANSPORT_PERMIT,
    MhrRegistrationTypes.REG_NOTE: ReportTypes.MHR_NOTE,
    MhrRegistrationTypes.DECAL_REPLACE: ReportTypes.MHR_NOTE,
    MhrRegistrationTypes.EXEMPTION_RES: ReportTypes.MHR_EXEMPTION,
    MhrRegistrationTypes.EXEMPTION_NON_RES: ReportTypes.MHR_EXEMPTION,
    MhrRegistrationTypes.TRAND: ReportTypes.MHR_TRANSFER,
    MhrRegistrationTypes.TRANS: ReportTypes.MHR_TRANSFER,
    MhrRegistrationTypes.TRANS_ADMIN: ReportTypes.MHR_TRANSFER,
    MhrRegistrationTypes.TRANS_AFFIDAVIT: ReportTypes.MHR_TRANSFER,
    MhrRegistrationTypes.TRANS_WILL: ReportTypes.MHR_TRANSFER,
}


@bp.route("/verify/<string:document_id>", methods=["GET", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def get_verify_ids(document_id: str):
    """Get summary status information for a an MH document ID."""
    try:
        logger.info(f"get_verify_ids document_id={document_id}")
        if document_id is None:
            return resource_utils.path_param_error_response("Document Id")
        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        # Verify the doc id, start with a valid response.
        response_json = {"documentId": document_id, "exists": False, "valid": True}
        error_msg = registration_validator.validate_doc_id(response_json)
        if error_msg and error_msg.find(registration_validator.DOC_ID_EXISTS) != -1:
            response_json["exists"] = True
        if error_msg and error_msg.find(registration_validator.DOC_ID_INVALID_CHECKSUM) != -1:
            response_json["valid"] = False
        if response_json["exists"] or not response_json["valid"]:
            return response_json, HTTPStatus.OK
        return doc_service_lookup(response_json)
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "GET verify doc id=" + document_id)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("/<string:document_id>", methods=["GET", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def get_documents(document_id: str):  # pylint: disable=too-many-return-statements
    """Get registration information by document id for a previous MH registration created by the account."""
    try:
        logger.info(f"get_documents document_id={document_id}")
        if document_id is None:
            return resource_utils.path_param_error_response("Document ID")
        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        verify_json = {"documentId": document_id}
        error_msg = registration_validator.validate_doc_id(verify_json, False)
        if error_msg != "":
            return resource_utils.validation_error_response([], reg_utils.VAL_ERROR, error_msg)

        # Try to fetch MH registration by document id.
        # Not found or not an account registration throw exceptions.
        registration: MhrRegistration = MhrRegistration.find_by_document_id(
            document_id, account_id, is_all_staff_account(account_id)
        )
        response_json = registration.json
        # Return report if request header Accept MIME type is application/pdf.
        if resource_utils.is_pdf(request):
            rep_type = map_report_type(response_json, is_staff(jwt))
            logger.info(f"Fetching registration report for doc ID= {document_id} rep_type={rep_type}.")
            response_json["usergroup"] = get_group(jwt)
            response_json["username"] = response_json.get("affirmByName", "")
            return reg_utils.get_registration_report(
                registration, response_json, rep_type, jwt.get_token_auth_header(), HTTPStatus.CREATED
            )

        return response_json, HTTPStatus.OK
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "GET MH document id=" + document_id)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("/qs-document-ids", methods=["GET", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def get_qs_document_ids():
    """Get a unique qualified supplier document ID based on the user token for DRS integration."""
    try:
        # Quick check: must provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        user_group: str = get_group(jwt)
        logger.info(f"get next QS document_id starting account_id={account_id} user group={user_group}")
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        if is_staff(jwt):
            logger.warning("Get QS document ID endpoint is not intended for staff users.")
        doc_id: str = get_qs_document_id(user_group)
        logger.info(f"New group {user_group} doc Id={doc_id}")
        response_json = {"documentId": doc_id}
        return jsonify(response_json), HTTPStatus.OK
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "GET QS document id")
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


def map_report_type(reg_json: dict, staff: bool) -> str:
    """Map the registration type to the report type."""
    if staff:
        return ReportTypes.MHR_REGISTRATION_STAFF
    reg_type = reg_json.get("registrationType")
    if REG_TYPE_TO_REPORT_TYPE.get(reg_type):
        return REG_TYPE_TO_REPORT_TYPE.get(reg_type)
    # Not all transfer registration type variations covered in the above mapping.
    return ReportTypes.MHR_TRANSFER


def doc_service_lookup(response_json: dict):
    """Map the registration type to the report type."""
    try:
        doc_id: str = response_json.get("documentId")
        logger.info(f"doc_service_lookup on doc id={doc_id}")
        ds_result = doc_id_lookup(doc_id)
        if ds_result and ds_result.get("resultCount", 0) > 0:
            response_json["exists"] = True
    except Exception as err:  # noqa: B902; return nicer default error
        logger.warning(f"doc_service_lookup failed: {err}")
    return response_json, HTTPStatus.OK
