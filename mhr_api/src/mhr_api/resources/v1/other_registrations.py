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

ID_TYPE_PARAM = 'identifierType'
MHR_NUM_PARAM = 'mhrNumber'  # Default if no request parameter.
DOC_REG_NUM_PARAM = 'documentRegistrationNumber'


@bp.route('/<string:identifier>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_other_registration(identifier: str):
    """Get summary information for a registration created by another account."""
    try:
        if identifier is None:
            return resource_utils.path_param_error_response('MHR Number')

        current_app.logger.debug(f'get_other_registration identifier={identifier}.')
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        # Use request parameter to determine if look up is by mhr (default) or doc reg number.
        registration = None
        id_type = request.args.get(ID_TYPE_PARAM)
        if id_type and id_type == DOC_REG_NUM_PARAM:
            # Try to fetch summary registration by document registration number
            registration = MhrRegistration.find_summary_by_doc_reg_number(account_id, identifier, is_staff(jwt))
        else:
            # Try to fetch summary registration by mhr number
            registration = MhrRegistration.find_summary_by_mhr_number(account_id, identifier, is_staff(jwt))
        if not registration:
            return resource_utils.not_found_error_response('Manufactured Home registration', identifier)
        return registration, HTTPStatus.OK

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id,
                                                    'GET Registration Summary id=' + identifier)
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
        registration = MhrRegistration.find_summary_by_mhr_number(account_id, mhr_number, is_staff(jwt))
        if not registration:
            return resource_utils.not_found_error_response('Manufactured Home registration', mhr_number)

        extra_existing: MhrExtraRegistration = MhrExtraRegistration.find_by_mhr_number(mhr_number, account_id)
        # Check if registration was created by the account and removed. If so, restore it.
        if extra_existing and extra_existing.removed_ind == MhrExtraRegistration.REMOVE_IND:
            current_app.logger.info(f'Restoring MHR# {mhr_number} for account {account_id}')
            MhrExtraRegistration.delete(mhr_number, account_id)
            if 'inUserList' in registration:
                del registration['inUserList']
            return registration, HTTPStatus.CREATED

        # Check if duplicate.
        if extra_existing:
            message = resource_utils.DUPLICATE_REGISTRATION_ERROR.format(mhr_number)
            return resource_utils.duplicate_error_response(message)
        if not extra_existing and registration.get('inUserList'):
            message = resource_utils.DUPLICATE_REGISTRATION_ERROR.format(mhr_number)
            return resource_utils.duplicate_error_response(message)

        current_app.logger.info(f'Adding another account MHR# {mhr_number} for account {account_id}')
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
    """Remove a registration from the current account registrations list."""
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
        # Try to find user registration
        registration = MhrRegistration.find_summary_by_mhr_number(account_id, mhr_number, is_staff(jwt))
        # Try to find extra registration.
        extra_registration = MhrExtraRegistration.find_by_mhr_number(mhr_number, account_id)
        if not registration and not extra_registration:
            return resource_utils.not_found_error_response('user account registration', mhr_number)
        if registration and not registration.get('inUserList') and not extra_registration:
            return resource_utils.not_found_error_response('user account registration', mhr_number)
        # Remove another account's registration.
        if extra_registration and not extra_registration.removed_ind:
            current_app.logger.info(f'Removing another account MHR# {mhr_number} for account {account_id}')
            MhrExtraRegistration.delete(mhr_number, account_id)
        # Or mark user account's registration as removed.
        elif not extra_registration:
            current_app.logger.info(f'Marking MHR# {mhr_number} as removed for account {account_id}')
            extra_registration = MhrExtraRegistration(account_id=account_id, mhr_number=mhr_number)
            extra_registration.removed_ind = MhrExtraRegistration.REMOVE_IND
            extra_registration.save()
        return '', HTTPStatus.NO_CONTENT

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id,
                                                    'Delete account extra registration id=' + mhr_number)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)
