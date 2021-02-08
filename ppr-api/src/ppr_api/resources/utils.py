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
"""Resource helper utilities for processing requests."""

from http import HTTPStatus
from flask import jsonify


ACCOUNT_REQUIRED = "Account-Id header required."


def serialize(errors):
    """Serialize errors."""
    error_message = []
    for error in errors:
        error_message.append('Schema validation: ' + error.message + '.')
    return error_message

def get_account_id(req):
    """Get account ID from request headers."""
    return req.headers.get('Account-Id')


def account_required_response():
    """Build account required error response."""
    return jsonify({'message': ACCOUNT_REQUIRED}), HTTPStatus.BAD_REQUEST


def validation_error_response(errors, cause):
    """Build a schema validation error response."""
    return jsonify({'message': cause, 'detail': serialize(errors)}), HTTPStatus.BAD_REQUEST
#    return {'cause': cause, 'message': schema_utils.serialize(errors)}, HTTPStatus.BAD_REQUEST

def business_exception_response(exception):
    """Build business exception error response."""
    return jsonify({'message': exception.error}), exception.status_code

def default_exception_response(exception):
    """Build default 500 exception error response."""
    return jsonify({'message': repr(exception)}), HTTPStatus.INTERNAL_SERVER_ERROR

def not_found_error_response(item, key):
    """Build a not found error response."""
    return jsonify({'message': f'No {item} found for {key}.'}), HTTPStatus.NOT_FOUND

def unauthorized_error_response(account_id):
    """Build an unauthorized error response."""
    return jsonify({'message': f'Authorization failure submitting a request for {account_id}.'}), \
           HTTPStatus.UNAUTHORIZED

def path_param_error_response(param_name):
    """Build a bad request param missing error response."""
    return jsonify({'message': f'A {param_name} path parameter is required.'}), HTTPStatus.BAD_REQUEST

def unprocessable_error_response(description):
    """Build an unprocessable entity error response."""
    return jsonify({'message': f'The {description} request could not be processed (no change/results).'}), \
            HTTPStatus.UNPROCESSABLE_ENTITY

def path_data_mismatch_error_response(path_value, description, data_value):
    """Build a bad request path param - payload data mismatch error."""
    message = f'The path value ({path_value}) does not match the data ' + \
              f'{description} value ({data_value}).'
    return jsonify({'message': message}), HTTPStatus.BAD_REQUEST

def historical_error_response(reg_num):
    """Build a bad request financing statement discharged (non-staff) error response."""
    return jsonify({'message': f'The Financing Statement for registration number {reg_num} has been discharged.'}), \
           HTTPStatus.BAD_REQUEST

def base_debtor_invalid_response():
    """Build an error response for no match on base debtor name."""
    message = 'No exact match found for provided base debtor name.'
    return jsonify({'message': message}), HTTPStatus.BAD_REQUEST
