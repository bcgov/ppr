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
"""API endpoints for maintainging draft registrations."""

from http import HTTPStatus

from flask import Blueprint, g, jsonify, request
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils

from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.models import MhrDraft, MhrRegistration
from mhr_api.models.mhr_draft import DRAFT_PAY_PENDING_PREFIX
from mhr_api.models.registration_utils import AccountRegistrationParams
from mhr_api.models.type_tables import MhrRegistrationStatusTypes, MhrRegistrationTypes
from mhr_api.resources import utils as resource_utils
from mhr_api.resources.cc_payment_utils import track_event
from mhr_api.services.authz import authorized, is_staff
from mhr_api.services.payment.client import SBCPaymentClient
from mhr_api.utils.auth import jwt
from mhr_api.utils.logging import logger

bp = Blueprint("DRAFTS1", __name__, url_prefix="/api/v1/drafts")  # pylint: disable=invalid-name
VAL_ERROR = "Draft request data validation errors."  # Validation error prefix


@bp.route("", methods=["GET", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def get_account_drafts():
    """Get the list of draft statements belonging to the header account ID."""
    account_id = ""
    try:
        # Quick check: must provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        params: AccountRegistrationParams = AccountRegistrationParams(account_id=account_id, sbc_staff=is_staff(jwt))
        params = resource_utils.get_account_registration_params(request, params)

        # Try to fetch draft list for account ID
        draft_list = MhrDraft.find_all_by_account_id(params)
        return jsonify(draft_list), HTTPStatus.OK
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "GET account drafts id=" + account_id)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("", methods=["POST", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def post_drafts():  # pylint: disable=too-many-return-statements
    """Create a new draft registration."""
    account_id = ""
    try:
        # Quick check: must provide an account ID.
        account_id = resource_utils.get_account_id(request)
        logger.info(f"post_drafts account_id={account_id}")
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            logger.debug("unauthorized")
            return resource_utils.unauthorized_error_response(account_id)
        request_json = request.get_json(silent=True)
        valid_format, errors = schema_utils.validate(request_json, "draft", "mhr")
        if not valid_format:
            return resource_utils.validation_error_response(errors, VAL_ERROR, None)
        # Save new draft statement: BusinessException raised if failure.
        token: dict = g.jwt_oidc_token_info
        draft = MhrDraft.create_from_json(request_json, account_id, token.get("username", None))
        draft.save()
        return draft.json, HTTPStatus.CREATED
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "POST mhr draft id=" + account_id)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("/<string:draft_number>", methods=["GET", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def get_drafts(draft_number: str):  # pylint: disable=too-many-return-statements
    """Get a draft registration by draft number."""
    try:
        logger.info(f"get_drafts draft_number={draft_number}")
        if draft_number is None:
            return resource_utils.path_param_error_response("draft number")
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        # Try to fetch draft by draft number
        draft = MhrDraft.find_by_draft_number(draft_number, False)
        return draft.json, HTTPStatus.OK
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "GET draft id=" + draft_number)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("/<string:draft_number>", methods=["PUT", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def put_drafts(draft_number: str):  # pylint: disable=too-many-return-statements
    """Update a draft by draft number with data in the request body."""
    try:
        logger.info(f"put_drafts draft_number={draft_number}")
        if draft_number is None:
            return resource_utils.path_param_error_response("draft number")
        # Quick check: must provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        if draft_number.startswith(DRAFT_PAY_PENDING_PREFIX):
            error_msg: str = f"Draft number {draft_number} is in a pending state: update not allowed."
            logger.error(error_msg)
            return resource_utils.bad_request_response(error_msg)
        request_json = request.get_json(silent=True)
        # Save draft statement update: BusinessException raised if failure.
        draft = MhrDraft.update(request_json, draft_number)
        draft.save()
        return draft.json, HTTPStatus.OK
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except DatabaseException as db_exception:  # noqa: B902; return nicer default error
        return resource_utils.db_exception_response(db_exception, account_id, "PUT draft id=" + draft_number)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("/<string:draft_number>", methods=["DELETE", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def delete_drafts(draft_number: str):  # pylint: disable=too-many-return-statements
    """Delete a draft registration by draft number."""
    try:
        logger.info(f"delete_drafts draft_number={draft_number}")
        if draft_number is None:
            return resource_utils.path_param_error_response("draft number")
        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        draft: MhrDraft = MhrDraft.find_by_draft_number(draft_number, False)
        # Try to delete draft by draft number.
        MhrDraft.delete(draft_number)
        draft_number: str = draft.draft_number
        logger.info(f"Draft number {draft_number} deleted.")
        if (
            draft_number.startswith(DRAFT_PAY_PENDING_PREFIX)
            and draft.registration_type != MhrRegistrationTypes.MHREG.value
            and draft.mhr_number
        ):
            staff: bool = is_staff(jwt)
            invoice_id: str = draft.user_id
            orig_status: str = draft.draft.get("status")
            mhr_reg: MhrRegistration = MhrRegistration.find_all_by_mhr_number(draft.mhr_number, draft.account_id, staff)
            if mhr_reg and mhr_reg.status_type == MhrRegistrationStatusTypes.DRAFT:
                logger.info(f"Reverting mhr {mhr_reg.mhr_number} status to {orig_status}")
                mhr_reg.status_type = orig_status
                mhr_reg.save()
                logger.info(f"Home status for MHR# {mhr_reg.mhr_number} restored to {orig_status}")
            track_event("06", invoice_id, HTTPStatus.OK, None)
            cancel_pending_payment(jwt.get_token_auth_header(), account_id, invoice_id)
        return "", HTTPStatus.NO_CONTENT
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except DatabaseException as db_exception:  # noqa: B902; return nicer default error
        return resource_utils.db_exception_response(db_exception, account_id, "DELETE draft id=" + draft_number)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("/cancel/<string:draft_number>", methods=["PATCH", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def cancel_pending_drafts(draft_number: str):
    """Cancel a payment pending draft by draft number: restore to a draft state."""
    try:
        logger.info(f"cancel_pending_drafts draft_number={draft_number}")
        if draft_number is None:
            return resource_utils.path_param_error_response("draft number")
        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        staff: bool = is_staff(jwt)
        if not staff and not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        if not draft_number.startswith(DRAFT_PAY_PENDING_PREFIX):
            error_msg: str = f"Draft number {draft_number} is not in a pending state."
            logger.error(error_msg)
            return resource_utils.bad_request_response(error_msg)
        draft: MhrDraft = MhrDraft.find_by_draft_number(draft_number, False)
        invoice_id: str = draft.user_id
        orig_status: str = draft.draft.get("status")
        revert_pending_draft(draft)
        # Now unlock home if draft is not for a new home registration.
        if draft.registration_type != MhrRegistrationTypes.MHREG.value and draft.mhr_number:
            mhr_reg: MhrRegistration = MhrRegistration.find_all_by_mhr_number(draft.mhr_number, draft.account_id, staff)
            if mhr_reg and mhr_reg.status_type == MhrRegistrationStatusTypes.DRAFT:
                logger.info(f"Reverting mhr {mhr_reg.mhr_number} status to {orig_status}")
                mhr_reg.status_type = orig_status
                mhr_reg.save()
                logger.info(f"Home status for MHR# {mhr_reg.mhr_number} restored to {orig_status}")
        track_event("06", invoice_id, HTTPStatus.OK, None)
        cancel_pending_payment(jwt.get_token_auth_header(), account_id, invoice_id)
        return draft.json, HTTPStatus.OK
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except DatabaseException as db_exception:  # noqa: B902; return nicer default error
        return resource_utils.db_exception_response(db_exception, account_id, "DELETE draft id=" + draft_number)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


def cancel_pending_payment(token: str, account_id: str, invoice_id: str):
    """Attempt to mark the pending pay api transaction as deleted."""
    try:
        logger.info(f"Submitting pay api delete pending payment account={account_id}, invoice={invoice_id}")
        pay_client = SBCPaymentClient(token, account_id)
        api_response = pay_client.delete_pending_payment(invoice_id)
        logger.info(f"Pay api delete pending payment response: invoice={invoice_id} response status={api_response}")
    except Exception as err:  # noqa: B902; wrapping exception
        logger.error(f"Cancel pending payment failed: account={account_id}, invoice={invoice_id}: {str(err)}")


def revert_pending_draft(draft: MhrDraft):
    """Update the draft to post registration state instead of payment pending."""
    draft_json = draft.draft
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
    draft.draft = draft_json
    draft_num: str = str(draft.draft_number)
    if draft_num.startswith(DRAFT_PAY_PENDING_PREFIX):
        draft.draft_number = draft_num[1:]
    draft.save()
    logger.info(f"Updated draft id={draft.id} number={draft.draft_number} userid={draft.user_id}")
