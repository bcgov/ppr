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
from ppr_api.models import Draft, User
from ppr_api.models.registration_utils import AccountRegistrationParams
from ppr_api.resources import utils as resource_utils
from ppr_api.services.authz import authorized
from ppr_api.utils.auth import jwt


bp = Blueprint('DRAFTS1',  # pylint: disable=invalid-name
               __name__, url_prefix='/api/v1/drafts')
VAL_ERROR = 'Draft request data validation errors.'  # Validation error prefix


@bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
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
        username = 'anonymous'
        user = User.find_by_jwt_token(g.jwt_oidc_token_info, account_id)
        if user and user.username:
            username = user.username
        new_feature_enabled = current_app.extensions['featureflags'].variation(
            'enable-new-feature-api', {'key': username}, False)

        # Try to fetch draft list for account ID
        params: AccountRegistrationParams = AccountRegistrationParams(account_id=account_id,
                                                                      collapse=True,
                                                                      account_name=None,
                                                                      sbc_staff=False)
        params = resource_utils.get_account_registration_params(request, params)
        draft_list = Draft.find_all_by_account_id(account_id, params, new_feature_enabled)
        return jsonify(draft_list), HTTPStatus.OK

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, 'GET drafts')
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*')
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
        draft = Draft.create_from_json(request_json, account_id, token.get('username', None))
        try:
            draft.save()
        except Exception as db_exception:   # noqa: B902; return nicer default error
            return resource_utils.db_exception_response(db_exception, account_id, 'POST draft')

        return draft.json, HTTPStatus.CREATED
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('/<string:document_id>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_drafts(document_id: str):  # pylint: disable=too-many-return-statements
    """Get a draft registration by draft document ID."""
    try:
        if document_id is None:
            return resource_utils.path_param_error_response('document ID')

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
        return resource_utils.db_exception_response(db_exception, account_id, 'GET draft id=' + document_id)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('/<string:document_id>', methods=['PUT', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def put_drafts(document_id: str):  # pylint: disable=too-many-return-statements
    """Update a draft by draft document ID with data in the request body."""
    try:
        if document_id is None:
            return resource_utils.path_param_error_response('document ID')

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
        except Exception as db_exception:   # noqa: B902; return nicer default error
            return resource_utils.db_exception_response(db_exception, account_id, 'PUT draft id=' + document_id)

    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('/<string:document_id>', methods=['DELETE', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def delete_drafts(document_id: str):  # pylint: disable=too-many-return-statements
    """Delete a draft registration by draft document ID."""
    try:
        if document_id is None:
            return resource_utils.path_param_error_response('document ID')

        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        # Try to delete draft statement by document ID
        try:
            Draft.delete(document_id)
        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as db_exception:   # noqa: B902; return nicer default error
            return resource_utils.db_exception_response(db_exception, account_id, 'DELETE draft id=' + document_id)

        return '', HTTPStatus.NO_CONTENT

    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)
