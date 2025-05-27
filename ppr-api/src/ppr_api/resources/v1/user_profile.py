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
"""API endpoints for maintaining user profile UI settings."""
# pylint: disable=too-many-return-statements
from http import HTTPStatus

from flask import Blueprint, g, request
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils

from ppr_api.exceptions import BusinessException
from ppr_api.models import ClientCode, User, UserProfile
from ppr_api.resources import utils as resource_utils
from ppr_api.services.authz import (
    BCOL_HELP,
    GENERAL_USER_GROUP,
    MANUFACTURER_GROUP,
    QUALIFIED_USER_GROUP,
    STAFF_ROLE,
    authorized,
    get_mhr_group,
    is_staff,
)
from ppr_api.utils.auth import jwt
from ppr_api.utils.logging import logger

bp = Blueprint("USER_PROFILE1", __name__, url_prefix="/api/v1/user-profile")  # pylint: disable=invalid-name
VAL_ERROR = "User Profile request data validation errors."  # Validation error prefix


@bp.route("", methods=["GET", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def get_user_profile():
    """Get existing user profile UI settings for the user represented by the request JWT."""
    try:
        # Quick check: always require an account ID.
        account_id = resource_utils.get_account_id(request)
        if not is_staff(jwt) and account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        # If staff/helpdesk use the original, actual account ID.
        if account_id in (BCOL_HELP, STAFF_ROLE) and resource_utils.get_staff_account_id(request):
            account_id = resource_utils.get_staff_account_id(request)
        token = g.jwt_oidc_token_info
        logger.debug(f"Getting user profile for account {account_id} with token: {token}")

        # Try to fetch existing user from JWT.
        user = User.find_by_jwt_token(token, account_id)
        logger.debug(f"User profile query completed for account {account_id}.")
        if not user:
            # If user does not exist, create user and user profile with the default settings.
            logger.debug(f"No user found for {account_id} request token: creating records.")
            user = User.create_from_jwt_token(token, account_id)
            user.user_profile = UserProfile.create_from_json(None, user.id)
            user.user_profile.save()
        profile_json = set_service_agreements(jwt, user.user_profile)
        parties = ClientCode.find_by_account_id(account_id, False, True)
        profile_json["hasSecuritiesActAccess"] = parties is not None and len(parties) > 0
        return profile_json, HTTPStatus.OK

    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        logger.error(f"Get user profile {account_id} failed: " + str(default_exception))
        return resource_utils.default_exception_response(default_exception)


@bp.route("", methods=["PATCH", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def update_user_profile():
    """Update user profile UI settings for the user represented by the request JWT."""
    try:
        # Quick check: always require an account ID.
        account_id = resource_utils.get_account_id(request)
        if not is_staff(jwt) and account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        request_json = request.get_json(silent=True)
        logger.debug(f"Updating user profile for {account_id} with values: {request_json}")
        # Validate against the schema.
        if not bypass_validation(request_json):
            valid_format, errors = schema_utils.validate(request_json, "userProfile", "common")
            if not valid_format:
                return resource_utils.validation_error_response(errors, VAL_ERROR)

        token = g.jwt_oidc_token_info
        logger.debug(f"Updating user profile for {account_id} with token: {token}")

        # Try to fetch existing user from JWT.
        user = User.find_by_jwt_token(token)
        if not user:
            # If user does not exist, create user and user profile with the default settings.
            logger.error(f"Update user profile no user found for {account_id} request token.")
            return resource_utils.not_found_error_response("user profile", account_id)

        user_profile = user.user_profile
        user_profile.update_profile(request_json)
        return user_profile.json, HTTPStatus.OK

    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        logger.error(f"Get user profile {account_id} failed: " + str(default_exception))
        return resource_utils.default_exception_response(default_exception)


def bypass_validation(request_json) -> bool:
    """If only updating registrations table or miscelaneous preferences skip schema validation."""
    if "registrationsTable" in request_json or "miscellaneousPreferences" in request_json:
        if (
            "paymentConfirmationDialog" not in request_json
            and "selectConfirmationDialog" not in request_json
            and "defaultDropDowns" not in request_json
            and "defaultTableFilters" not in request_json
        ):
            return True
    return False


def set_service_agreements(jwt_, profile: UserProfile) -> dict:
    """For MHR user requests conditionally set service agreement acceptance required."""
    profile_json: dict = profile.json
    if get_mhr_group(jwt_) in (MANUFACTURER_GROUP, QUALIFIED_USER_GROUP, GENERAL_USER_GROUP):
        if profile.service_agreements and "acceptAgreementRequired" in profile.service_agreements:
            profile_json["acceptAgreementRequired"] = profile.service_agreements.get("acceptAgreementRequired")
        else:
            profile_json["acceptAgreementRequired"] = False
    return profile_json
