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

from flask import Blueprint, g, jsonify, request
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils

from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.models import MhrManufacturer
from mhr_api.resources import registration_utils as reg_utils
from mhr_api.resources import utils as resource_utils
from mhr_api.services.authz import authorized
from mhr_api.utils import manufacturer_validator
from mhr_api.utils.auth import jwt
from mhr_api.utils.logging import logger

bp = Blueprint("MANUFACTURER1", __name__, url_prefix="/api/v1/manufacturers")  # pylint: disable=invalid-name


@bp.route("", methods=["GET", "OPTIONS"])
@cross_origin(origin="*")
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
        # Try to get manufacturer by account ID: only one per account.
        logger.info(f"Getting manufacturer information for account {account_id}.")
        manufacturer: MhrManufacturer = MhrManufacturer.find_by_account_id(account_id)
        if manufacturer:
            return jsonify(manufacturer.json), HTTPStatus.OK
        logger.info(f"No manufacturer info found for account {account_id}.")
        return resource_utils.not_found_error_response("manufacturer information", account_id)

    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "GET manufacturer info")
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("", methods=["POST", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def post_account_manufacturer():
    """Create manufacturer information for an account."""
    try:
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        logger.info(f"Creating manufacturer information for account id {account_id}.")
        manufacturer: MhrManufacturer = MhrManufacturer.find_by_account_id(account_id)
        if manufacturer:
            msg: str = f"Manufacturer information already exists for account {account_id}."
            logger.error(msg)
            return resource_utils.bad_request_response(msg)
        request_json = request.get_json(silent=True)
        valid_format, errors = schema_utils.validate(request_json, "manufacturerInfo", "mhr")
        # Additional validation not covered by the schema.
        extra_validation_msg = manufacturer_validator.validate_manufacturer(request_json)
        if not valid_format or extra_validation_msg != "":
            return resource_utils.validation_error_response(errors, reg_utils.VAL_ERROR, extra_validation_msg)
        token: dict = g.jwt_oidc_token_info
        manufacturer = MhrManufacturer.create_manufacturer_from_json(
            request_json, account_id, token.get("username", None)
        )
        manufacturer.save()
        return jsonify(manufacturer.json), HTTPStatus.OK
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "GET manufacturer info")
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("", methods=["DELETE", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def delete_account_manufacturer():
    """Delete a manufacturer by account id."""
    try:
        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        logger.info(f"delete_account_manufacturer account_id={account_id}")
        # Try to delete the account manufacturer.
        MhrManufacturer.delete(account_id)
        return "", HTTPStatus.NO_CONTENT
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except DatabaseException as db_exception:  # noqa: B902; return nicer default error
        return resource_utils.db_exception_response(db_exception, account_id, f"DELETE account id={account_id}")
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("", methods=["PUT", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def put_account_manufacturer():
    """Replace existing account manufacturer information with updated values."""
    try:
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        request_json = request.get_json(silent=True)
        valid_format, errors = schema_utils.validate(request_json, "manufacturerInfo", "mhr")
        # Additional validation not covered by the schema.
        extra_validation_msg = manufacturer_validator.validate_manufacturer(request_json)
        if not valid_format or extra_validation_msg != "":
            return resource_utils.validation_error_response(errors, reg_utils.VAL_ERROR, extra_validation_msg)
        manufacturer: MhrManufacturer = MhrManufacturer.find_by_account_id(account_id)
        if not manufacturer:
            logger.info(f"No manufacturer info found for account {account_id}.")
            return resource_utils.not_found_error_response("manufacturer information", account_id)
        logger.info(f"Updating manufacturer information for account {account_id}.")
        manufacturer.update(request_json)
        return jsonify(manufacturer.json), HTTPStatus.OK
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "PUT manufacturer info")
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)
