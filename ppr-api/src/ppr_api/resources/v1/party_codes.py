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

from flask import Blueprint, g, jsonify, request
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils

from ppr_api.exceptions import BusinessException, DatabaseException
from ppr_api.models import ClientCode, ClientCodeRegistration
from ppr_api.models.type_tables import ClientCodeTypes
from ppr_api.resources import financing_utils as fs_utils
from ppr_api.resources import utils as resource_utils
from ppr_api.services.authz import authorized, is_staff
from ppr_api.utils.auth import jwt
from ppr_api.utils.logging import logger
from ppr_api.utils.validators import party_validator

bp = Blueprint("PARTY_CODES1", __name__, url_prefix="/api/v1/party-codes")  # pylint: disable=invalid-name
FUZZY_NAME_SEARCH_PARAM = "fuzzyNameSearch"
SECURITIES_ACT_PARAM = "securitiesActCodes"
QUERY_ACCOUNT_PARAM = "searchAccountId"  # Used by staff when looking up codes by BCRS account ID.


@bp.route("/<string:code>", methods=["GET", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def get_party_codes(code: str):
    """Get a preset registering or secured party by client code."""
    try:
        if code is None:
            return resource_utils.path_param_error_response("code")

        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if not is_staff(jwt) and account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        # Try to fetch client party by code
        logger.debug(f"Getting party code for account {account_id} with code = {code}.")
        party = ClientCode.find_by_code(code)
        if not party:
            return resource_utils.not_found_error_response("party", code)

        return party, HTTPStatus.OK

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "GET client party code=" + code)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("/head-offices/<string:name_or_code>", methods=["GET", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def get_head_office_party_codes(name_or_code: str):
    """Get a list of client parties (registering or secured parties) associated with a head office code or name."""
    try:
        if name_or_code is None:
            return resource_utils.path_param_error_response("nameOrCode")
        fuzzy_param = request.args.get(FUZZY_NAME_SEARCH_PARAM)

        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if not is_staff(jwt) and account_id is None:
            return resource_utils.account_required_response()

        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)

        # Try to fetch client parties: no results is an empty list.
        logger.debug(f"Getting {account_id} head office party codes searching on {name_or_code}.")
        parties = ClientCode.find_by_head_office(name_or_code, fuzzy_param)
        # if not parties:
        #    return resource_utils.not_found_error_response('party', code)
        return jsonify(parties), HTTPStatus.OK

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "GET client party matches")
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("/accounts", methods=["GET", "OPTIONS"])
@cross_origin(origin="*")
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
        if request.args.get(QUERY_ACCOUNT_PARAM):
            search_account_id: str = request.args.get(QUERY_ACCOUNT_PARAM)
            logger.info(f"Account {account_id} getting all party codes for {search_account_id}.")
            parties = ClientCode.find_by_bcrs_account(search_account_id)
            logger.info(f"Found {len(parties)} party codes for account {search_account_id}.")
            return jsonify(parties), HTTPStatus.OK
        # Default filter is crown charge account party codes.
        logger.info(f"Getting {account_id} party codes.")
        is_crown_charge: bool = True
        is_securities_act: bool = False
        securities_act_param = request.args.get(SECURITIES_ACT_PARAM)
        if securities_act_param:
            is_crown_charge = False
            is_securities_act = True
        parties = ClientCode.find_by_account_id(account_id, is_crown_charge, is_securities_act)
        return jsonify(parties), HTTPStatus.OK

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(
            db_exception, account_id, "GET account client party codes account=" + account_id
        )
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("/accounts", methods=["POST", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def post_account_codes():
    """Create a new client party code as either a new head office and branch or as a new branch."""
    try:
        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        request_json = request.get_json(silent=True)
        # Validate request data against the schema.
        valid_format, errors = schema_utils.validate(request_json, "clientParty", "ppr")
        if not valid_format:
            return resource_utils.validation_error_response(errors, fs_utils.VAL_ERROR)
        staff: bool = is_staff(jwt)
        if not request_json.get("headOfficeCode") and not staff:
            codes = ClientCode.find_by_bcrs_account(account_id)
            if codes:
                head_office = codes[0].get("headOfficeCode")
                logger.info(f"Account {account_id} found existing head office code {head_office}, creating branch")
                request_json["headOfficeCode"] = head_office
        extra_validation_msg = party_validator.validate_client_code_registration(
            request_json, ClientCodeTypes.CREATE_CODE, account_id, staff
        )
        if extra_validation_msg != "":
            return resource_utils.validation_error_response(errors, fs_utils.VAL_ERROR, extra_validation_msg)
        req_account_id = account_id if not staff else request_json.get("accountId")
        logger.info(f"New client party code request staff={staff} account ID={req_account_id}")
        token: dict = g.jwt_oidc_token_info
        reg: ClientCodeRegistration = ClientCodeRegistration.create_new_from_json(
            request_json, req_account_id, token.get("username")
        )
        reg.save()
        return jsonify(reg.client_code.json), HTTPStatus.CREATED
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "POST account client party code")
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)
