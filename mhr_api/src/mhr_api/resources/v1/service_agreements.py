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
"""API endpoints for executing MHR service agreement information requests."""

# pylint: disable=too-many-return-statements

from http import HTTPStatus

from flask import Blueprint
from flask import request, jsonify, current_app, g
from flask_cors import cross_origin
from registry_schemas import utils as schema_utils

from mhr_api.utils.auth import jwt
from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.services.authz import authorized
from mhr_api.models import MhrServiceAgreement, utils as model_utils, MhrQualifiedSupplier, MhrManufacturer
from mhr_api.resources import utils as resource_utils
from mhr_api.services.abstract_storage_service import DocumentTypes
from mhr_api.services.document_storage.storage_service import GoogleStorageService
from mhr_api.services.utils.exceptions import StorageException


VAL_ERROR = 'Service agreements request data validation errors.'  # Validation error prefix
ACCEPT_REQUIRED = 'Accepted must be true to indicate the service agreement terms have been accepted. '
NO_EXISTING_ACCOUNT = 'No existing Qualified Supplier/Manufacturer found for account id {account_id}'
bp = Blueprint('AGREEMENT1', __name__, url_prefix='/api/v1/service-agreements')  # pylint: disable=invalid-name


@bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_service_agreements():
    """Get information for all existing service agreements."""
    try:
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        current_app.logger.info(f'Getting service agreement information for account {account_id}.')
        agreements_json = MhrServiceAgreement.find_all_json()
        return jsonify(agreements_json), HTTPStatus.OK
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, 'GET service agreement info')
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('/<string:version>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_agreement_versions(version: str):  # pylint: disable=too-many-return-statements
    """Get a service agreement pdf or info by version number."""
    try:
        current_app.logger.info(f'get_agreement_versions version={version}')
        if version is None:
            return resource_utils.path_param_error_response('version')
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        # Try to fetch service agreement information by version number
        agreement: MhrServiceAgreement = MhrServiceAgreement.find_by_version(version.lower())
        if not agreement:
            return resource_utils.not_found_error_response('termsVersion', version)

        if resource_utils.is_pdf(request):
            doc_name = agreement.doc_storage_url
            current_app.logger.info(f'Fetching service agreement pdf {doc_name} from doc storage.')
            raw_data = GoogleStorageService.get_document(doc_name, DocumentTypes.SERVICE_AGREEMENT)
            return raw_data, HTTPStatus.OK, {'Content-Type': 'application/pdf'}

        return jsonify(agreement.json), HTTPStatus.OK
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception,
                                                    account_id,
                                                    f'GET service agreement version={version}')
    except StorageException as storage_err:
        msg: str = 'Error getting service agreement pdf from storage: ' + str(storage_err)
        return resource_utils.error_response(HTTPStatus.INTERNAL_SERVER_ERROR, msg)
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('/<string:version>', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def post_agreement_versions(version: str):  # pylint: disable=too-many-return-statements
    """POST user acceptance of a service agreement version."""
    try:
        current_app.logger.info(f'post_agreement_versions version={version}')
        if version is None:
            return resource_utils.path_param_error_response('version')
        # Quick check: must have an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        request_json = request.get_json(silent=True)
        # Validate schema.
        valid_format, errors = schema_utils.validate(request_json, 'termsSummary', 'mhr')
        extra_validation_msg = validate_agreement(request_json)
        if not valid_format or extra_validation_msg != '':
            return resource_utils.validation_error_response(errors, VAL_ERROR, extra_validation_msg)

        # Try to fetch service agreement information by version number
        agreement: MhrServiceAgreement = MhrServiceAgreement.find_by_version(version.lower())
        if not agreement:
            return resource_utils.not_found_error_response('termsVersion', version)
        manufacturer: MhrManufacturer = None
        supplier: MhrQualifiedSupplier = MhrQualifiedSupplier.find_by_account_id(account_id)
        if not supplier:
            manufacturer: MhrManufacturer = MhrManufacturer.find_by_account_id(account_id)
        if not supplier and not manufacturer:
            return resource_utils.bad_request_response(NO_EXISTING_ACCOUNT.format(account_id=account_id))
        # Record the acceptance for the account if not yet accepted.
        accept_agreement_account(supplier, manufacturer)
        agreement_json = agreement.json
        del agreement_json['createDateTime']
        agreement_json['accepted'] = True
        agreement_json['acceptedDateTime'] = model_utils.format_ts(model_utils.now_ts())
        # Record acceptance for the user.
        token: dict = g.jwt_oidc_token_info
        MhrServiceAgreement.update_user_profile(agreement_json, account_id, token.get('username', ''))
        return jsonify(agreement_json), HTTPStatus.OK
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception,
                                                    account_id,
                                                    f'POST service agreement version={version}')
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


def accept_agreement_account(supplier: MhrQualifiedSupplier, manufacturer: MhrManufacturer):
    """Record the agreement as accepted at the account level."""
    if supplier and (supplier.terms_accepted is None or supplier.terms_accepted != 'Y'):
        supplier.terms_accepted = 'Y'
        supplier.save()
        current_app.logger.debug(f'Setting supplier.terms_accepted for account_id={supplier.account_id}')
    elif manufacturer and (manufacturer.terms_accepted is None or manufacturer.terms_accepted != 'Y'):
        manufacturer.terms_accepted = 'Y'
        manufacturer.save()
        current_app.logger.debug(f'Setting manufacturer.terms_accepted for account_id={manufacturer.account_id}')


def validate_agreement(json_data) -> str:
    """Perform all extra service agreement data validation checks not covered by schema validation."""
    if not json_data.get('accepted'):
        return ACCEPT_REQUIRED
    return ''
