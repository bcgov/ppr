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
"""API endpoints for requests to maintain MH documents."""

from http import HTTPStatus

from flask import Blueprint
from flask import current_app, request
from flask_cors import cross_origin

from mhr_api.utils.auth import jwt
from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.models import MhrRegistration
from mhr_api.services.authz import authorized, is_all_staff_account
from mhr_api.reports.v2.report_utils import ReportTypes
from mhr_api.resources import utils as resource_utils, registration_utils as reg_utils
from mhr_api.utils import registration_validator


bp = Blueprint('DOCUMENTS1',  # pylint: disable=invalid-name
               __name__, url_prefix='/api/v1/documents')


@bp.route('/verify/<string:document_id>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_verify_ids(document_id: str):
    """Get summary status information for a an MH document ID."""
    try:
        current_app.logger.info(f'get_verify_ids document_id={document_id}')
        if document_id is None:
            return resource_utils.path_param_error_response('Document Id')
        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        # Verify the doc id, start with a valid response.
        response_json = {
            'documentId': document_id,
            'exists': False,
            'valid': True
        }
        error_msg = registration_validator.validate_doc_id(response_json)
        if error_msg and error_msg.find(registration_validator.DOC_ID_EXISTS) != -1:
            response_json['exists'] = True
        if error_msg and error_msg.find(registration_validator.DOC_ID_INVALID_CHECKSUM) != -1:
            response_json['valid'] = False
        return response_json, HTTPStatus.OK
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id,
                                                    'GET verify doc id=' + document_id)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route('/<string:document_id>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='*')
@jwt.requires_auth
def get_documents(document_id: str):  # pylint: disable=too-many-return-statements
    """Get registration information by document id for a previous MH registration created by the account."""
    try:
        current_app.logger.info(f'get_documents document_id={document_id}')
        if document_id is None:
            return resource_utils.path_param_error_response('Document ID')
        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        verify_json = {
            'documentId': document_id
        }
        error_msg = registration_validator.validate_doc_id(verify_json, False)
        if error_msg != '':
            return resource_utils.validation_error_response([], reg_utils.VAL_ERROR, error_msg)

        # Try to fetch MH registration by document id.
        # Not found or not an account registration throw exceptions.
        registration: MhrRegistration = MhrRegistration.find_by_document_id(document_id,
                                                                            account_id,
                                                                            is_all_staff_account(account_id))
        response_json = registration.json
        # Return report if request header Accept MIME type is application/pdf.
        if resource_utils.is_pdf(request):
            current_app.logger.info(f'Fetching registration report for doc ID= {document_id}.')
            return reg_utils.get_registration_report(registration,
                                                     response_json,
                                                     ReportTypes.MHR_TRANSFER,
                                                     jwt.get_token_auth_header(),
                                                     HTTPStatus.CREATED)

        return response_json, HTTPStatus.OK
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id,
                                                    'GET MH document id=' + document_id)
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)
