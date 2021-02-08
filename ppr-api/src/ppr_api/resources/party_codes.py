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

from flask import request
from flask_restx import Namespace, Resource, cors

from ppr_api.utils.auth import jwt
from ppr_api.utils.util import cors_preflight
from ppr_api.exceptions import BusinessException
from ppr_api.services.authz import is_staff, authorized
from ppr_api.models import ClientParty

from .utils import get_account_id, account_required_response, business_exception_response
from .utils import unauthorized_error_response, not_found_error_response, \
                   path_param_error_response, default_exception_response

API = Namespace('party-codes', description='Endpoints for maintaining client registering and secured parties.')


@cors_preflight('GET,OPTIONS')
@API.route('/<path:code>', methods=['GET', 'OPTIONS'])
class ClientPartyResource(Resource):
    """Resource for maintaining existing client parties."""

    @staticmethod
    @cors.crossdomain(origin='*')
    def get(code):
        """Get a preset registering or secured party by client code."""

        try:
            if code is None:
                return path_param_error_response('code')

            # Quick check: must be staff or provide an account ID.
            account_id = get_account_id(request)
            if not is_staff(jwt) and account_id is None:
                return account_required_response()

            # Verify request JWT and account ID
            if not authorized(account_id, jwt):
                return unauthorized_error_response(account_id)

            # Try to fetch client party by code
            party = ClientParty.find_by_code(code)
            if not party:
                return not_found_error_response('party', code)

            return party, HTTPStatus.OK

        except BusinessException as exception:
            return business_exception_response(exception)
        except Exception as default_exception:
            return default_exception_response(default_exception)
