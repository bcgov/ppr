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

from flask import Blueprint
from flask import current_app, request, jsonify, g
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils

from mhr_api.utils.auth import jwt
from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.models import MhrDraft
from mhr_api.resources import utils as resource_utils
from mhr_api.services.authz import authorized


bp = Blueprint('DRAFTS1',  # pylint: disable=invalid-name
               __name__, url_prefix='/api/v1/drafts')
VAL_ERROR = 'Draft request data validation errors.'  # Validation error prefix


@bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_account_drafts():
    """Get the list of draft statements belonging to the header account ID."""
    account_id = ''
    try:
        # Quick check: must provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        # Try to fetch draft list for account ID
        draft_list = MhrDraft.find_all_by_account_id(account_id)
        return jsonify(draft_list), HTTPStatus.OK
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id,
                                                    'GET account drafts id=' + account_id)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def post_drafts():  # pylint: disable=too-many-return-statements
    """Create a new draft registration."""
    account_id = ''
    try:
        # Quick check: must provide an account ID.
        account_id = resource_utils.get_account_id(request)
        current_app.logger.info(f'post_drafts account_id={account_id}')
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        request_json = request.get_json(silent=True)
        valid_format, errors = schema_utils.validate(request_json, 'draft', 'mhr')
        if not valid_format:
            return resource_utils.validation_error_response(errors, VAL_ERROR, None)
        # Save new draft statement: BusinessException raised if failure.
        token: dict = g.jwt_oidc_token_info
        draft = MhrDraft.create_from_json(request_json, account_id, token.get('username', None))
        draft.save()
        return draft.json, HTTPStatus.CREATED
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id,
                                                    'POST mhr draft id=' + account_id)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('/<string:draft_number>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_drafts(draft_number: str):  # pylint: disable=too-many-return-statements
    """Get a draft registration by draft number."""
    try:
        current_app.logger.info(f'get_drafts draft_number={draft_number}')
        if draft_number is None:
            return resource_utils.path_param_error_response('draft number')
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
        return resource_utils.db_exception_response(db_exception, account_id, 'GET draft id=' + draft_number)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('/<string:draft_number>', methods=['PUT', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def put_drafts(draft_number: str):  # pylint: disable=too-many-return-statements
    """Update a draft by draft number with data in the request body."""
    try:
        current_app.logger.info(f'put_drafts draft_number={draft_number}')
        if draft_number is None:
            return resource_utils.path_param_error_response('draft number')
        # Quick check: must provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        request_json = request.get_json(silent=True)
        # Save draft statement update: BusinessException raised if failure.
        draft = MhrDraft.update(request_json, draft_number)
        draft.save()
        return draft.json, HTTPStatus.OK
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except DatabaseException as db_exception:   # noqa: B902; return nicer default error
        return resource_utils.db_exception_response(db_exception, account_id, 'PUT draft id=' + draft_number)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('/<string:draft_number>', methods=['DELETE', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def delete_drafts(draft_number: str):  # pylint: disable=too-many-return-statements
    """Delete a draft registration by draft number."""
    try:
        current_app.logger.info(f'delete_drafts draft_number={draft_number}')
        if draft_number is None:
            return resource_utils.path_param_error_response('draft number')
        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        # Try to delete draft by draft number.
        MhrDraft.delete(draft_number)
        return '', HTTPStatus.NO_CONTENT
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except DatabaseException as db_exception:   # noqa: B902; return nicer default error
        return resource_utils.db_exception_response(db_exception, account_id, 'DELETE draft id=' + draft_number)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)
