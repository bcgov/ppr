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
"""API endpoints for requests to view registrations created by another account."""

# pylint: disable=too-many-return-statements

from http import HTTPStatus

from flask import Blueprint
from flask import request, current_app
from flask_cors import cross_origin

from mhr_api.utils.auth import jwt
from mhr_api.exceptions import DatabaseException
from mhr_api.services.authz import authorized, is_staff
from mhr_api.models import MhrRegistration, MhrExtraRegistration
from mhr_api.resources import utils as resource_utils


bp = Blueprint('OTHER_REGISTRATIONS1',  # pylint: disable=invalid-name
               __name__, url_prefix='/api/v1/other-registrations')


@bp.route('/<string:mhr_number>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_other_registration(mhr_number: str):
    """Get summary information for a registration created by another account."""
    try:
        if mhr_number is None:
            return resource_utils.path_param_error_response('MHR Number')

        current_app.logger.debug(f'get_other_registration mhr_number={mhr_number}.')
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        # Try to fetch summary registration by mhr number
        registration = MhrRegistration.find_summary_by_mhr_number(account_id, mhr_number, is_staff(jwt))
        if not registration:
            return resource_utils.not_found_error_response('Manufactured Home registration', mhr_number)
        return registration, HTTPStatus.OK

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id,
                                                    'GET Registration Summary id=' + mhr_number)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('/<string:mhr_number>', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def post_other_registration(mhr_number: str):
    """Add a registration created by another account to the current account list."""
    try:
        if mhr_number is None:
            return resource_utils.path_param_error_response('MHR Number')

        current_app.logger.debug(f'post_other_registration mhr_number={mhr_number}.')
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        # Try to fetch summary registration by mhr number
        registration = MhrRegistration.find_summary_by_mhr_number(account_id, mhr_number)
        if not registration:
            return resource_utils.not_found_error_response('Manufactured Home registration', mhr_number)

        # Check if duplicate.
        extra_existing = MhrExtraRegistration.find_by_mhr_number(mhr_number, account_id)
        if extra_existing:
            message = resource_utils.DUPLICATE_REGISTRATION_ERROR.format(mhr_number)
            return resource_utils.duplicate_error_response(message)

        extra_registration = MhrExtraRegistration(account_id=account_id, mhr_number=mhr_number)
        extra_registration.save()

        if 'inUserList' in registration:
            del registration['inUserList']
        return registration, HTTPStatus.CREATED

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id,
                                                    'Add account extra registration id=' + mhr_number)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('/<string:mhr_number>', methods=['DELETE', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def delete_other_registration(mhr_number: str):
    """Remove a registration created by another account from the current account list."""
    try:
        if mhr_number is None:
            return resource_utils.path_param_error_response('MHR Number')

        current_app.logger.debug(f'delete_other_registration mhr_number={mhr_number}.')
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        # Try to find extra registration.
        extra_registration = MhrExtraRegistration.find_by_mhr_number(mhr_number, account_id)
        if extra_registration is None:
            return resource_utils.not_found_error_response('user account registration', mhr_number)
        # Remove another account's financing statement registration.
        if extra_registration and not extra_registration.removed_ind:
            MhrExtraRegistration.delete(mhr_number, account_id)
        return '', HTTPStatus.NO_CONTENT

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id,
                                                    'Delete account extra registration id=' + mhr_number)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)
