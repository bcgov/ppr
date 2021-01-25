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
"""API endpoints for executing PPR searches."""

from http import HTTPStatus

from flask import abort, g, jsonify, request
from flask_restplus import Namespace, Resource, cors
from flask_jwt_oidc import JwtManager

from ppr_api.utils.auth import jwt
from ppr_api.utils.util import cors_preflight
from ppr_api.exceptions import BusinessException
from ppr_api.services.authz import is_staff, authorized
from ppr_api.models import Search, SearchDetail

from registry_schemas import utils as schema_utils
from .utils import get_account_id, account_required_response, \
                   validation_error_response, business_exception_response
from .utils import unauthorized_error_response, unprocessable_error_response, \
                   path_param_error_response, default_exception_response
#from auth_api.tracer import Tracer


API = Namespace('searches', description='Endpoints for PPR searches.')
#TRACER = Tracer.get_instance()

VAL_ERROR = "Search request data validation errors."  # Validation error prefix


@cors_preflight('POST,OPTIONS')
@API.route('', methods=['POST', 'OPTIONS'])
class SearchResource(Resource):
    """Resource for executing PPR searches."""

    @staticmethod
#    @TRACER.trace()
    @cors.crossdomain(origin='*')
#    @jwt.requires_auth
    def post():
        """Execute a new search request using criteria in the request body."""
#        token = g.jwt_oidc_token_info

        try:

            # Quick check: must be staff or provide an account ID. 
            account_id = get_account_id(request)
            if not is_staff(jwt) and account_id is None:
                return account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate request against the schema.
            valid_format, errors = schema_utils.validate(request_json, 'searchQuery', 'ppr')
            if not valid_format:
                return validation_error_response(errors, VAL_ERROR)
            # Perform any extra data validation such as start and end dates here
            Search.validate_query(request_json)

            # TODO: charge a search fee.

            # Execute the search query: if no results return a 422 status.  
            query = Search.create_from_json(request_json, account_id)
            query.search()
            if not query.search_response or query.returned_results_size == 0:
                return unprocessable_error_response('search query')

            return query.json, HTTPStatus.CREATED

        except BusinessException as exception:
            return business_exception_response(exception)
        except Exception as ex:
            return default_exception_response(ex)


@cors_preflight('PUT,OPTIONS')
@API.route('/<path:searchId>', methods=['PUT', 'OPTIONS'])
class SearchDetailResource(Resource):
    """Resource for processing PPR search detail (second step) requests."""

    @staticmethod
#    @TRACER.trace()
    @cors.crossdomain(origin='*')
#    @jwt.requires_auth
    def put(searchId):
        """Execute a search detail request using criteria in the request body."""
#        token = g.jwt_oidc_token_info

        try:
            if searchId is None:
                return path_param_error_response('search ID')

            # Quick check: must be staff or provide an account ID. 
            account_id = get_account_id(request)
            if not is_staff(jwt) and account_id is None:
                return account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return unauthorized_error_response(account_id)

            request_json = request.get_json(silent=True)
            # Validate schema.
            valid_format, errors = schema_utils.validate(request_json, 'searchSummary', 'ppr')
            if not valid_format:
                return validation_error_response(errors, VAL_ERROR)

            # Perform any extra data validation such as start and end dates here
            SearchDetail.validate_search_select(request_json, searchId)

            # Try to fetch requested search details: failure throws a business exception.  
            results = SearchDetail.create_from_json(request_json, searchId)
            if not results.search_response:
                return unprocessable_error_response('search result details')

            return results.json, HTTPStatus.OK

        except BusinessException as exception:
            return business_exception_response(exception)
        except Exception as ex:
            return default_exception_response(ex)

