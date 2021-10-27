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

from flask import request, g, current_app
from flask_restx import Namespace, Resource, cors
from registry_schemas import utils as schema_utils

from ppr_api.exceptions import BusinessException
from ppr_api.models import User, UserProfile
from ppr_api.services.authz import is_staff, authorized
from ppr_api.utils.auth import jwt
from ppr_api.utils.util import cors_preflight
from ppr_api.resources import utils as resource_utils


API = Namespace('user-profile', description='Endpoints for maintaining user profile UI settings.')
VAL_ERROR = 'User Profile request data validation errors.'  # Validation error prefix


@cors_preflight('GET,PATCH,OPTIONS')
@API.route('', methods=['GET', 'PATCH', 'OPTIONS'])
class UserProfileResource(Resource):
    """Resource for maintaining user profile UI preferences."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def get():
        """Get existing user profile UI settings for the user represented by the request JWT."""
        try:
            # Quick check: always require an account ID.
            account_id = resource_utils.get_account_id(request)
            if not is_staff(jwt) and account_id is None:
                return resource_utils.account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)

            token = g.jwt_oidc_token_info
            current_app.logger.debug(f'Getting user profile for account {account_id} with token: {token}')

            # Try to fetch existing user from JWT.
            user = User.find_by_jwt_token(token, account_id)
            current_app.logger.debug(f'User profile query completed for account {account_id}.')
            if not user:
                # If user does not exist, create user and user profile with the default settings.
                current_app.logger.debug(f'No user found for {account_id} request token: creating records.')
                user = User.create_from_jwt_token(token, account_id)
                user.user_profile = UserProfile.create_from_json(None, user.id)
                user.user_profile.save()

            return user.user_profile.json, HTTPStatus.OK

        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            current_app.logger.error(f'Get user profile {account_id} failed: ' + repr(default_exception))
            return resource_utils.default_exception_response(default_exception)

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def patch():
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
            current_app.logger.debug(f'Updating user profile for {account_id} with values: {request_json}')
            # Validate against the schema.
            if not bypass_validation(request_json):
                valid_format, errors = schema_utils.validate(request_json, 'userProfile', 'common')
                if not valid_format:
                    return resource_utils.validation_error_response(errors, VAL_ERROR)

            token = g.jwt_oidc_token_info
            current_app.logger.debug(f'Updating user profile for {account_id} with token: {token}')

            # Try to fetch existing user from JWT.
            user = User.find_by_jwt_token(token)
            if not user:
                # If user does not exist, create user and user profile with the default settings.
                current_app.logger.error(f'Update user profile no user found for {account_id} request token.')
                return resource_utils.not_found_error_response('user profile', account_id)

            user_profile = user.user_profile
            user_profile.update_profile(request_json)
            return user_profile.json, HTTPStatus.OK

        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            current_app.logger.error(f'Get user profile {account_id} failed: ' + repr(default_exception))
            return resource_utils.default_exception_response(default_exception)


def bypass_validation(request_json) -> bool:
    """If only updating registrations table or miscelaneous preferences skip schema validation."""
    if 'registrationsTable' in request_json or 'miscellaneousPreferences' in request_json:
        if 'paymentConfirmationDialog' not in request_json and \
                'selectConfirmationDialog' not in request_json and \
                'defaultDropDowns' not in request_json and \
                'defaultTableFilters' not in request_json:
            return True
    return False
