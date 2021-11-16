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

from flask import jsonify, current_app

from ppr_api.exceptions import BusinessException
from ppr_api.models.registration import CrownChargeTypes, MiscellaneousTypes, PPSATypes
from ppr_api.services.authz import user_orgs
from ppr_api.utils.validators import financing_validator, party_validator, registration_validator


ACCOUNT_REQUIRED = 'Account-Id header required.'
CROWN_CHARGE_FORBIDDEN = 'The account ID {account_id} is not authorized to access a Crown Charge registration.'
ACCOUNT_ACCESS = 'The account ID {account_id} cannot access statement information for ' + \
                 'registration number {registration_num}.'
PARTY_REGISTERING = 'RG'
PARTY_SECURED = 'SP'


def serialize(errors):
    """Serialize errors."""
    error_message = []
    if errors:
        for error in errors:
            error_message.append('Schema validation: ' + error.message + '.')
    return error_message


def get_account_id(req):
    """Get account ID from request headers."""
    return req.headers.get('Account-Id')


def is_pdf(req):
    """Check if request headers Accept is application/pdf."""
    accept = req.headers.get('Accept')
    return accept and accept.upper() == 'APPLICATION/PDF'


def get_apikey(req):
    """Get gateway api key from request headers."""
    return req.headers.get('x-apikey')


def account_required_response():
    """Build account required error response."""
    return jsonify({'message': ACCOUNT_REQUIRED}), HTTPStatus.BAD_REQUEST


def validation_error_response(errors, cause, additional_msg: str = None):
    """Build a schema validation error response."""
    details = serialize(errors)
    if additional_msg:
        details.append('Additional validation: ' + additional_msg)
    return jsonify({'message': cause, 'detail': details}), HTTPStatus.BAD_REQUEST


def business_exception_response(exception):
    """Build business exception error response."""
    current_app.logger.error(repr(exception))
    return jsonify({'message': exception.error}), exception.status_code


def pay_exception_response(exception):
    """Build pay 402 exception error response."""
    current_app.logger.error(repr(exception))
    return jsonify({'message': repr(exception)}), HTTPStatus.PAYMENT_REQUIRED


def default_exception_response(exception):
    """Build default 500 exception error response."""
    current_app.logger.error(repr(exception))
    return jsonify({'message': repr(exception)}), HTTPStatus.INTERNAL_SERVER_ERROR


def not_found_error_response(item, key):
    """Build a not found error response."""
    message = f'No {item} found for {key}.'
    current_app.logger.info(str(HTTPStatus.NOT_FOUND.value) + ': ' + message)
    return jsonify({'message': message}), HTTPStatus.NOT_FOUND


def duplicate_error_response(message):
    """Build a duplicate request error response."""
    current_app.logger.info(str(HTTPStatus.CONFLICT.value) + ': ' + message)
    return jsonify({'message': message}), HTTPStatus.CONFLICT


def unauthorized_error_response(account_id):
    """Build an unauthorized error response."""
    message = f'Authorization failure submitting a request for {account_id}.'
    current_app.logger.info(str(HTTPStatus.UNAUTHORIZED.value) + ': ' + message)
    return jsonify({'message': message}), HTTPStatus.UNAUTHORIZED


def cc_forbidden_error_response(account_id):
    """Build a crown charge registration class access forbidden error response."""
    message = CROWN_CHARGE_FORBIDDEN.format(account_id=account_id)
    current_app.logger.info(str(HTTPStatus.FORBIDDEN.value) + ': ' + message)
    return jsonify({'message': message}), HTTPStatus.FORBIDDEN


def path_param_error_response(param_name):
    """Build a bad request param missing error response."""
    message = f'A {param_name} path parameter is required.'
    current_app.logger.info(str(HTTPStatus.BAD_REQUEST.value) + ': ' + message)
    return jsonify({'message': message}), HTTPStatus.BAD_REQUEST


def unprocessable_error_response(description):
    """Build an unprocessable entity error response."""
    message = f'The {description} request could not be processed (no change/results).'
    current_app.logger.info(str(HTTPStatus.UNPROCESSABLE_ENTITY.value) + ': ' + message)
    return jsonify({'message': message}), HTTPStatus.UNPROCESSABLE_ENTITY


def path_data_mismatch_error_response(path_value, description, data_value):
    """Build a bad request path param - payload data mismatch error."""
    message = f'The path value ({path_value}) does not match the data ' + \
              f'{description} value ({data_value}).'
    current_app.logger.info(str(HTTPStatus.BAD_REQUEST.value) + ': ' + message)
    return jsonify({'message': message}), HTTPStatus.BAD_REQUEST


def historical_error_response(reg_num):
    """Build a bad request financing statement discharged (non-staff) error response."""
    message = f'The Financing Statement for registration number {reg_num} has been discharged.'
    current_app.logger.info(str(HTTPStatus.BAD_REQUEST.value) + ': ' + message)
    return jsonify({'message': message}), HTTPStatus.BAD_REQUEST


def base_debtor_invalid_response():
    """Build an error response for no match on base debtor name."""
    message = 'No exact match found for provided base debtor name.'
    current_app.logger.info(str(HTTPStatus.BAD_REQUEST.value) + ': ' + message)
    return jsonify({'message': message}), HTTPStatus.BAD_REQUEST


def validate_financing(json_data):
    """Perform non-schema extra validation on a financing statement."""
    error_msg = party_validator.validate_financing_parties(json_data)
    error_msg += financing_validator.validate(json_data)
    return error_msg


def validate_registration(json_data):
    """Perform non-schema extra validation on a non-financing registrations."""
    error_msg = party_validator.validate_registration_parties(json_data)
    error_msg += registration_validator.validate_registration(json_data)
    return error_msg


def validate_renewal(json_data, financing_statement):
    """Perform non-schema extra validation on a renewal registrations."""
    error_msg = party_validator.validate_registration_parties(json_data)
    error_msg += registration_validator.validate_renewal(json_data, financing_statement)
    return error_msg


def validate_delete_ids(json_data, financing_statement):
    """Perform non-schema extra validation on a change amendment delete party, collateral ID's."""
    error_msg = party_validator.validate_party_ids(json_data, financing_statement)
    error_msg += registration_validator.validate_collateral_ids(json_data, financing_statement)
    if error_msg != '':
        raise BusinessException(
            error=error_msg,
            status_code=HTTPStatus.BAD_REQUEST
        )


def get_account_name(token: str, account_id: str = None):
    """Lookup the account organization name from the user token with an auth api call."""
    orgs = user_orgs(token)
    if orgs and 'orgs' in orgs:
        if (len(orgs['orgs']) == 1 or not account_id or not account_id.isdigit()):
            return orgs['orgs'][0]['name']
        for org in orgs['orgs']:
            if org['id'] == int(account_id):
                return org['name']
    return None


def check_access_financing(token: str, staff: bool, account_id: str, statement):
    """Extra check on account access to a financing statement."""
    if staff or (account_id and statement.registration[0].account_id == account_id):
        return

    account_name = get_account_name(token, account_id)
    access = False
    if account_name:
        for party in statement.registration[0].parties:
            if party.party_type in (PARTY_REGISTERING, PARTY_SECURED) and \
                    party.business_name and party.business_name == account_name:
                access = True
            elif party.client_code and party.client_code.name == account_name:
                access = True
    if not access:
        reg_num = statement.registration[0].registration_num
        current_app.logger.error('Account name ' + account_name + ' cannot access registration ' + reg_num)
        raise BusinessException(
            error=ACCOUNT_ACCESS.format(account_id=account_id, registration_num=reg_num),
            status_code=HTTPStatus.UNAUTHORIZED
        )


def check_access_registration(token: str, staff: bool, account_id: str, statement):
    """Extra check on account access to a registration."""
    if staff or (account_id and statement.account_id == account_id):
        return

    account_name = get_account_name(token, account_id)
    access = False
    if account_name:
        for party in statement.financing_statement.parties:
            if party.party_type in (PARTY_REGISTERING, PARTY_SECURED) and \
                    party.business_name and party.business_name == account_name:
                access = True
            elif party.client_code and party.client_code.name == account_name:
                access = True
    if not access:
        reg_num = statement.registration_num
        current_app.logger.error('Account name ' + account_name + ' cannot access registration ' + reg_num)
        raise BusinessException(
            error=ACCOUNT_ACCESS.format(account_id=account_id, registration_num=reg_num),
            status_code=HTTPStatus.UNAUTHORIZED
        )


def no_fee_amendment(registration_type: str) -> bool:
    """Amendment registration check if no fee registration type."""
    if registration_type == PPSATypes.LAND_TAX.value:
        return True
    for reg_type in MiscellaneousTypes:
        if reg_type.value == registration_type:
            return True
    for reg_type in CrownChargeTypes:
        if reg_type.value == registration_type and \
                registration_type not in (CrownChargeTypes.CORP_TAX.value,
                                          CrownChargeTypes.CONSUMPTION_TAX.value,
                                          CrownChargeTypes.MINERAL_TAX.value,
                                          CrownChargeTypes.SOCIAL_TAX.value,
                                          CrownChargeTypes.HOTEL_TAX.value,
                                          CrownChargeTypes.MINING_TAX.value):
            return True
    return False
