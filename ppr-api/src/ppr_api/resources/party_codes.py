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

from flask import request, current_app, jsonify
from flask_restx import Namespace, Resource, cors

from ppr_api.exceptions import BusinessException
from ppr_api.models import ClientCode
from ppr_api.resources import utils as resource_utils
from ppr_api.services.authz import is_staff, authorized
from ppr_api.utils.auth import jwt
from ppr_api.utils.util import cors_preflight


API = Namespace('party-codes', description='Endpoints for maintaining client registering and secured parties.')
FUZZY_NAME_SEARCH_PARAM = 'fuzzyNameSearch'


@cors_preflight('GET,OPTIONS')
@API.route('/<path:code>', methods=['GET', 'OPTIONS'])
class ClientPartyResource(Resource):
    """Resource for maintaining existing client parties."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def get(code):
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

        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('GET,OPTIONS')
@API.route('/head-offices/<path:name_or_code>', methods=['GET', 'OPTIONS'])
class ClientPartyHeadOfficeResource(Resource):
    """Resource for looking up client parties belonging to a head office."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def get(name_or_code):
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

        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)


@cors_preflight('GET,OPTIONS')
@API.route('/accounts', methods=['GET', 'OPTIONS'])
class ClientPartyAccountResource(Resource):
    """Resource for looking up client parties belonging to an account linke to a BCOL number."""

    @staticmethod
    @cors.crossdomain(origin='*')
    @jwt.requires_auth
    def get():
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

        except BusinessException as exception:
            return resource_utils.business_exception_response(exception)
        except Exception as default_exception:   # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_exception)
