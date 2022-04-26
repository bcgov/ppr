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
"""API endpoints for executing PPR search history requests."""

# pylint: disable=too-many-return-statements

from http import HTTPStatus

from flask import Blueprint
from flask import request, jsonify, current_app
from flask_cors import cross_origin

from mhr_api.utils.auth import jwt
from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.services.authz import authorized
from mhr_api.models import SearchRequest
from mhr_api.resources import utils as resource_utils


bp = Blueprint('SEARCH_HISTORY1', __name__, url_prefix='/api/v1/search-history')  # pylint: disable=invalid-name
VAL_ERROR = 'Search history request data validation errors.'  # Validation error prefix


@bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_search_history():
    """Get account search history."""
    try:
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        # Try to fetch search history by account id.
        # No results throws a not found business exception.
        current_app.logger.info(f'Fetching search history for {account_id}.')
        from_ui = request.args.get('from_ui', False)
        history = SearchRequest.find_all_by_account_id(account_id, from_ui)
        return jsonify(history), HTTPStatus.OK

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, 'GET search history')
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)
