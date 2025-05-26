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
"""API endpoints for maintainging draft statements."""

# pylint: disable=too-many-return-statements

from http import HTTPStatus

from flask import Blueprint, current_app, g, jsonify, request
from flask_cors import cross_origin

from ppr_api.exceptions import BusinessException, DatabaseException
from ppr_api.models import Draft, Registration, User
from ppr_api.models import utils as model_utils
from ppr_api.models.draft import DRAFT_PAY_PENDING_PREFIX
from ppr_api.models.registration_utils import AccountRegistrationParams
from ppr_api.resources import utils as resource_utils
from ppr_api.resources.cc_payment_utils import REG_STATUS_LOCKED, REG_STATUS_UNLOCKED, track_event
from ppr_api.services.authz import authorized, is_staff
from ppr_api.services.payment.client import SBCPaymentClient
from ppr_api.utils.auth import jwt
from ppr_api.utils.logging import logger

bp = Blueprint("DRAFTS1", __name__, url_prefix="/api/v1/drafts")  # pylint: disable=invalid-name
VAL_ERROR = "Draft request data validation errors."  # Validation error prefix


@bp.route("", methods=["GET", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def get_account_drafts():
    """Get the list of draft statements belonging to the header account ID."""
    try:

        # Quick check: must provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        # Set feature flag value
        username = "anonymous"
        user = User.find_by_jwt_token(g.jwt_oidc_token_info, account_id)
        if user and user.username:
            username = user.username
        new_feature_enabled = current_app.extensions["featureflags"].variation(
            "enable-new-feature-api", {"key": username}, False
        )

        # Try to fetch draft list for account ID
        params: AccountRegistrationParams = AccountRegistrationParams(
            account_id=account_id, collapse=True, account_name=None, sbc_staff=False
        )
        params = resource_utils.get_account_registration_params(request, params)
        draft_list = Draft.find_all_by_account_id(account_id, params, new_feature_enabled)
        return jsonify(draft_list), HTTPStatus.OK

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "GET drafts")
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("", methods=["POST", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def post_drafts():  # pylint: disable=too-many-return-statements
    """Create a new draft registration."""
    try:
        # Quick check: must provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        request_json = request.get_json(silent=True)
        # Disable schema validation: draft may be partial/incomplele.
        # valid_format, errors = schema_utils.validate(request_json, 'draft', 'ppr')
        # if not valid_format:
        #   return validation_error_response(errors, VAL_ERROR)

        # Save new draft statement: BusinessException raised if failure.
        token: dict = g.jwt_oidc_token_info
        draft = Draft.create_from_json(request_json, account_id, token.get("username", None))
        try:
            draft.save()
        except Exception as db_exception:  # noqa: B902; return nicer default error
            return resource_utils.db_exception_response(db_exception, account_id, "POST draft")

        return draft.json, HTTPStatus.CREATED
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("/<string:document_id>", methods=["GET", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def get_drafts(document_id: str):  # pylint: disable=too-many-return-statements
    """Get a draft registration by draft document ID."""
    try:
        if document_id is None:
            return resource_utils.path_param_error_response("document ID")

        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        # Try to fetch draft statement by document ID
        draft = Draft.find_by_document_number(document_id, False)
        return draft.json, HTTPStatus.OK

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "GET draft id=" + document_id)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("/<string:document_id>", methods=["PUT", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def put_drafts(document_id: str):  # pylint: disable=too-many-return-statements
    """Update a draft by draft document ID with data in the request body."""
    try:
        if document_id is None:
            return resource_utils.path_param_error_response("document ID")

        # Quick check: must provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        request_json = request.get_json(silent=True)
        # Disable schema validation: draft may be partial/incomplele.
        # valid_format, errors = schema_utils.validate(request_json, 'draft', 'ppr')
        # if not valid_format:
        #   return validation_error_response(errors, VAL_ERROR)

        # Save draft statement update: BusinessException raised if failure.
        try:
            draft = Draft.update(request_json, document_id)
            draft.save()
            return draft.json, HTTPStatus.OK
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as db_exception:  # noqa: B902; return nicer default error
            return resource_utils.db_exception_response(db_exception, account_id, "PUT draft id=" + document_id)

    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("/<string:document_id>", methods=["DELETE", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def delete_drafts(document_id: str):  # pylint: disable=too-many-return-statements
    """Delete a draft registration by draft document ID."""
    try:
        if document_id is None:
            return resource_utils.path_param_error_response("document ID")

        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        # Try to delete draft statement by document ID
        try:
            draft: Draft = Draft.find_by_document_number(document_id, False)
            Draft.delete(document_id)
            doc_number: str = draft.document_number
            logger.info(f"Draft doc number {doc_number} deleted.")
            if doc_number.startswith(DRAFT_PAY_PENDING_PREFIX):
                staff: bool = is_staff(jwt)
                invoice_id: str = draft.user_id
                reg_num: str = draft.registration_number
                if not model_utils.is_financing(draft.registration_type_cl) and reg_num:
                    reg: Registration = Registration.find_by_registration_number(reg_num, account_id, staff)
                    if reg and reg.ver_bypassed == REG_STATUS_LOCKED:
                        reg.ver_bypassed = REG_STATUS_UNLOCKED
                        reg.save()
                        logger.info(f"Unlocked pending payment for base registration {reg_num}")
                    track_event("06", invoice_id, HTTPStatus.OK, f"Reg num = {reg_num} draft id={draft.id}")
                else:
                    track_event("06", invoice_id, HTTPStatus.OK, f"Draft id={draft.id}")
                cancel_pending_payment(jwt.get_token_auth_header(), account_id, invoice_id)
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as db_exception:  # noqa: B902; return nicer default error
            return resource_utils.db_exception_response(db_exception, account_id, "DELETE draft id=" + document_id)

        return "", HTTPStatus.NO_CONTENT

    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("/cancel/<string:document_id>", methods=["PATCH", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def cancel_pending_drafts(document_id: str):
    """Cancel a payment pending draft by draft number: restore to a draft state."""
    try:
        if document_id is None:
            return resource_utils.path_param_error_response("document ID")

        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        if not document_id.startswith(DRAFT_PAY_PENDING_PREFIX):
            error_msg: str = f"Draft doc number {document_id} is not in a pending state."
            logger.error(error_msg)
            return resource_utils.bad_request_response(error_msg)

        # Try to delete draft statement by document ID
        draft: Draft = Draft.find_by_document_number(document_id, False)
        invoice_id: str = draft.user_id
        revert_pending_draft(draft)
        # Now unlock base registration if draft is not for a new financing statement.
        if not model_utils.is_financing(draft.registration_type_cl) and draft.registration_number:
            staff: bool = is_staff(jwt)
            reg: Registration = Registration.find_by_registration_number(draft.registration_number, account_id, staff)
            if reg and reg.ver_bypassed == REG_STATUS_LOCKED:
                reg.ver_bypassed = REG_STATUS_UNLOCKED
                reg.save()
                logger.info(f"Unlocked pending payment for base registration {reg.registration_num}")
            track_event("06", invoice_id, HTTPStatus.OK, f"Reg num = {reg.registration_num} draft id={draft.id}")
        else:
            track_event("06", invoice_id, HTTPStatus.OK, f"Draft id={draft.id}")
        cancel_pending_payment(jwt.get_token_auth_header(), account_id, invoice_id)
        return draft.json, HTTPStatus.OK
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
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


def revert_pending_draft(draft: Draft):
    """Update the draft to regular state instead of payment pending."""
    draft_json = draft.draft
    draft.user_id = draft_json.get("username", None)
    if draft_json.get("username"):
        del draft_json["username"]
    if draft_json.get("accountId"):
        del draft_json["accountId"]
    if draft_json.get("status"):
        del draft_json["status"]
    if "paymentPending" in draft_json:
        del draft_json["paymentPending"]
    draft.draft = draft_json
    draft_num: str = str(draft.document_number)
    if draft_num.startswith(DRAFT_PAY_PENDING_PREFIX):
        draft.document_number = draft_num[1:]
    draft.save()
    logger.info(f"Updated draft id={draft.id} number={draft.document_number} userid={draft.user_id}")
