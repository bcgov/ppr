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
"""API endpoints for maintaining preset client registering and secured parties."""

# pylint: disable=too-many-return-statements

from http import HTTPStatus

from flask import Blueprint, current_app, jsonify, request
from flask_cors import cross_origin
from ppr_api.exceptions import BusinessException, DatabaseException
from ppr_api.models import ClientCode
from ppr_api.resources import utils as resource_utils
from ppr_api.services.authz import authorized, is_staff
from ppr_api.utils.auth import jwt


bp = Blueprint('PARTY_CODES1',  # pylint: disable=invalid-name
               __name__, url_prefix='/api/v1/party-codes')
FUZZY_NAME_SEARCH_PARAM = 'fuzzyNameSearch'


@bp.route('/<string:code>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_party_codes(code: str):
    """Get a preset registering or secured party by client code."""
    try:
        if code is None:
            return resource_utils.path_param_error_response('code')

        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if not is_staff(jwt) and account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        # Try to fetch client party by code
        current_app.logger.debug(f'Getting party code for account {account_id} with code = {code}.')
        party = ClientCode.find_by_code(code)
        if not party:
            return resource_utils.not_found_error_response('party', code)

        return party, HTTPStatus.OK

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, 'GET client party code=' + code)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('/head-offices/<string:name_or_code>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_head_office_party_codes(name_or_code: str):
    """Get a list of client parties (registering or secured parties) associated with a head office code or name."""
    try:
        if name_or_code is None:
            return resource_utils.path_param_error_response('nameOrCode')
        fuzzy_param = request.args.get(FUZZY_NAME_SEARCH_PARAM)

        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if not is_staff(jwt) and account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        # Try to fetch client parties: no results is an empty list.
        current_app.logger.debug(f'Getting {account_id} head office party codes searching on {name_or_code}.')
        parties = ClientCode.find_by_head_office(name_or_code, fuzzy_param)
        # if not parties:
        #    return resource_utils.not_found_error_response('party', code)
        return jsonify(parties), HTTPStatus.OK

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, 'GET client party matches')
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('/accounts', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_account_codes():
    """Get a list of client parties associated with an account-BCOL number pair."""
    try:
        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        # Try to fetch client parties: no results is an empty list.
        current_app.logger.debug(f'Getting {account_id}  party codes.')
        parties = ClientCode.find_by_account_id(account_id, True)
        return jsonify(parties), HTTPStatus.OK

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id,
                                                    'GET account client party codes account=' + account_id)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)
