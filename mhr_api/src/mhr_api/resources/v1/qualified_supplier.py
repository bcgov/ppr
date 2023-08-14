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
"""API endpoints for executing MHR qualified supplier contact information requests."""

# pylint: disable=too-many-return-statements

from http import HTTPStatus

from flask import Blueprint
from flask import request, jsonify, current_app
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils

from mhr_api.utils.auth import jwt
from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.services.authz import authorized
from mhr_api.models import MhrQualifiedSupplier
from mhr_api.models.type_tables import MhrPartyTypes
from mhr_api.resources import utils as resource_utils, registration_utils as reg_utils
from mhr_api.utils import validator_utils


bp = Blueprint('SUPPLIER1', __name__, url_prefix='/api/v1/qualified-suppliers')  # pylint: disable=invalid-name


@bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_account_qualified_supplier():
    """Get account qualified supplier information."""
    try:
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        current_app.logger.info(f'Getting qualified supplier information for account {account_id}.')
        supplier: MhrQualifiedSupplier = MhrQualifiedSupplier.find_by_account_id(account_id)
        if supplier:
            return jsonify(supplier.json), HTTPStatus.OK
        current_app.logger.info(f'No qualified supplier info found for account {account_id}.')
        return resource_utils.not_found_error_response('qualified supplier information', account_id)
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, 'GET manufacturer info')
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def post_account_qualified_supplier():
    """Create qualified supplier information for an account."""
    try:
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        current_app.logger.info(f'Creating qualified supplier  information for account {account_id}.')
        supplier: MhrQualifiedSupplier = MhrQualifiedSupplier.find_by_account_id(account_id)
        if supplier:
            msg: str = f'Qualified supplier information already exists for account {account_id}.'
            current_app.logger.error(msg)
            return resource_utils.bad_request_response(msg)
        request_json = request.get_json(silent=True)
        valid_format, errors = schema_utils.validate(request_json, 'party', 'common')
        # Additional validation not covered by the schema.
        extra_validation_msg = validator_utils.validate_party(request_json, 'qualified supplier')
        if not valid_format or extra_validation_msg != '':
            return resource_utils.validation_error_response(errors, reg_utils.VAL_ERROR, extra_validation_msg)
        supplier = MhrQualifiedSupplier.create_from_json(request_json, account_id, MhrPartyTypes.CONTACT)
        supplier.save()
        return jsonify(supplier.json), HTTPStatus.OK
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, 'GET manufacturer info')
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)
