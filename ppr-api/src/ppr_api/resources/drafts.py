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

from flask import request, jsonify
from flask_restx import Namespace, Resource, cors

from registry_schemas import utils as schema_utils

from ppr_api.utils.auth import jwt
from ppr_api.utils.util import cors_preflight
from ppr_api.exceptions import BusinessException
from ppr_api.services.authz import is_staff, authorized
from ppr_api.models import Draft

from .utils import get_account_id, account_required_response, validation_error_response, \
                   business_exception_response, default_exception_response
from .utils import unauthorized_error_response, path_param_error_response


API = Namespace('drafts', description='Endpoints for maintaining draft statements.')

VAL_ERROR = "Draft request data validation errors."  # Validation error prefix

@cors_preflight('GET,POST,OPTIONS')
@API.route('', methods=['GET', 'POST', 'OPTIONS'])
class DraftResource(Resource):
    """Resource for executing draft statements."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def get():
        """Get the list of draft statements belonging to the header account ID."""

        try:

            # Quick check: must provide an account ID.
            account_id = get_account_id(request)
            if account_id is None:
                return account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return unauthorized_error_response(account_id)

            # Try to fetch draft list for account ID
            draft_list = Draft.find_all_by_account_id(account_id)

            return jsonify(draft_list), HTTPStatus.OK

        except BusinessException as exception:
            return business_exception_response(exception)
        except Exception as default_exception:
            return default_exception_response(default_exception)


    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def post():
        """Create a new draft statement."""

        try:

            # Quick check: must provide an account ID.
            account_id = get_account_id(request)
            if account_id is None:
                return account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate schema.
            valid_format, errors = schema_utils.validate(request_json, 'draft', 'ppr')
            if not valid_format:
                return validation_error_response(errors, VAL_ERROR)

            # Save new draft statement: BusinessException raised if failure.
            draft = Draft.create_from_json(request_json, account_id)
            draft.save()

            return draft.json, HTTPStatus.CREATED

        except BusinessException as exception:
            return business_exception_response(exception)
        except Exception as default_exception:
            return default_exception_response(default_exception)



@cors_preflight('GET,PUT,DELETE,OPTIONS')
@API.route('/<path:document_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
class MaintainDraftResource(Resource):
    """Resource for maintaining existing, individual draft statements."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def get(document_id):
        """Get a draft statement by document ID."""

        try:
            if document_id is None:
                return path_param_error_response('document ID')

            # Quick check: must be staff or provide an account ID.
            account_id = get_account_id(request)
            if not is_staff(jwt) and account_id is None:
                return account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return unauthorized_error_response(account_id)

            # Try to fetch draft statement by document ID
            draft = Draft.find_by_document_number(document_id, False)

            return draft.json, HTTPStatus.OK

        except BusinessException as exception:
            return business_exception_response(exception)
        except Exception as default_exception:
            return default_exception_response(default_exception)


    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def put(document_id):
        """Update a draft statement by document ID with data in the request body."""

        try:
            if document_id is None:
                return path_param_error_response('document ID')

            # Quick check: must provide an account ID.
            account_id = get_account_id(request)
            if account_id is None:
                return account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate schema.
            valid_format, errors = schema_utils.validate(request_json, 'draft', 'ppr')
            if not valid_format:
                return validation_error_response(errors, VAL_ERROR)

            # Save draft statement update: BusinessException raised if failure.
            draft = Draft.update(request_json, document_id)
            draft.save()

            return draft.json, HTTPStatus.OK

        except BusinessException as exception:
            return business_exception_response(exception)
        except Exception as default_exception:
            return default_exception_response(default_exception)


    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def delete(document_id):
        """Delete a draft statement by document ID."""

        try:
            if document_id is None:
                return path_param_error_response('document ID')

            # Quick check: must be staff or provide an account ID.
            account_id = get_account_id(request)
            if not is_staff(jwt) and account_id is None:
                return account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return unauthorized_error_response(account_id)

            # Try to fetch draft statement by document ID
            Draft.delete(document_id)

            return '', HTTPStatus.NO_CONTENT

        except BusinessException as exception:
            return business_exception_response(exception)
        except Exception as default_exception:
            return default_exception_response(default_exception)
