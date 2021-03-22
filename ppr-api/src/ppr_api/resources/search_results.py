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
"""API endpoints for executing PPR search detail requests (search step 2)."""

# pylint: disable=too-many-return-statements

from http import HTTPStatus

from flask import request, current_app, jsonify
from flask_restx import Namespace, Resource, cors

from registry_schemas import utils as schema_utils
from ppr_api.utils.auth import jwt
from ppr_api.utils.util import cors_preflight
from ppr_api.exceptions import BusinessException
from ppr_api.services.authz import is_staff, authorized
from ppr_api.models import SearchResult
from ppr_api.resources import utils as resource_utils


API = Namespace('search-results', description='Endpoints for PPR search details (Search step 2).')
VAL_ERROR = 'Search details request data validation errors.'  # Validation error prefix


@cors_preflight('GET,POST,OPTIONS')
@API.route('/<path:search_id>', methods=['GET', 'POST', 'OPTIONS'])
class SearchResultsResource(Resource):
    """Resource for submitting PPR search detail (second step) requests."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def post(search_id):
        """Execute a search detail request using selection choices in the request body."""
        try:
            if search_id is None:
                return resource_utils.path_param_error_response('search ID')

            # Quick check: must be staff or provide an account ID.
            account_id = resource_utils.get_account_id(request)
            if not is_staff(jwt) and account_id is None:
                return resource_utils.account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate schema.
            valid_format, errors = schema_utils.validate(request_json, 'searchSummary', 'ppr')
            if not valid_format:
                return resource_utils.validation_error_response(errors, VAL_ERROR)

            # Perform any extra data validation such as start and end dates here
            search_detail = SearchResult.validate_search_select(request_json, search_id)

            # Save the search query selection and details that match the selection.
            search_detail.update_selection(request_json)
            if not search_detail.search_response:
                return resource_utils.unprocessable_error_response('search result details')

            response_data = search_detail.json
            if resource_utils.is_pdf(request):
                # TODO: if request header Accept MIME type is application/pdf, format as pdf.
                return response_data, HTTPStatus.OK

            return jsonify(response_data), HTTPStatus.OK

        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:
            return resource_utils.default_exception_response(default_exception)

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def get(search_id):
        """Get search detail information for a previous search."""
        try:
            if search_id is None:
                return resource_utils.path_param_error_response('search ID')

            # Quick check: must have an account ID.
            account_id = resource_utils.get_account_id(request)
            if account_id is None:
                return resource_utils.account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return resource_utils.unauthorized_error_response(account_id)

            # Try to fetch search detail by search id.
            current_app.logger.info(f'Fetching search detail for {search_id}.')
            search_detail = SearchResult.find_by_search_id(search_id, True)
            if not search_detail:
                return resource_utils.not_found_error_response('searchId', search_id)

            response_data = search_detail.json
            # TODO: if request header Accept MIME type is application/pdf, format as pdf.
            return jsonify(response_data), HTTPStatus.OK

        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:
            return resource_utils.default_exception_response(default_exception)
