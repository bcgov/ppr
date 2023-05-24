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
from mhr_api.models import MhrManufacturer
from mhr_api.resources import utils as resource_utils


bp = Blueprint('MANUFACTURER1', __name__, url_prefix='/api/v1/manufacturers')  # pylint: disable=invalid-name


@bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_account_manufacturer():
    """Get account manufacturer information."""
    try:
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        # Try to get bcol account from account ID: from business an account should have at most 1 bcol number.
        current_app.logger.info(f'Getting manufacturer information for account number for {account_id}.')
        manufacturer: MhrManufacturer = MhrManufacturer.find_by_account_id(account_id)
        if manufacturer:
            return jsonify(manufacturer.json), HTTPStatus.OK
        current_app.logger.info(f'No manufacturer info found for account {account_id}.')
        return resource_utils.not_found_error_response('manufacturer information', account_id)

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, 'GET manufacturer info')
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)
