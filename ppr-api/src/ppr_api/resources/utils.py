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

from flask import current_app, jsonify, request
from ppr_api.exceptions import BusinessException, DatabaseException, ResourceErrorCodes
from ppr_api.models import EventTracking, MailReport, Party, Registration, VerificationReport
from ppr_api.models import utils as model_utils
from ppr_api.models.registration import AccountRegistrationParams, CrownChargeTypes, MiscellaneousTypes, PPSATypes
from ppr_api.services.authz import is_bcol_help, is_reg_staff_account, is_sbc_office_account, user_orgs
from ppr_api.services.payment import TransactionTypes
from ppr_api.services.payment.exceptions import SBCPaymentException
from ppr_api.services.queue_service import GoogleQueueService
from ppr_api.utils.base import BaseEnum
from ppr_api.utils.validators import financing_validator, party_validator, registration_validator


# Resource error messages
# Model business error messages in models.utils.py
ACCOUNT_REQUIRED = '{code}: Account-Id header required.'
UNAUTHORIZED = '{code}: authorization failure submitting a request for {account_id}.'
CROWN_CHARGE_FORBIDDEN = '{code}: the account ID {account_id} is not authorized to access a Crown Charge registration.'
ACCOUNT_ACCESS = '{code}: the account ID {account_id} cannot access statement information for ' + \
                 'registration number {registration_num}.'
STAFF_SEARCH_BCOL_FAS = '{code}: provide either a BCOL Account Number or a Routing Slip Number but not both.'
SBC_SEARCH_NO_PAYMENT = '{code}: provide either a BCOL Account Number or a Routing Slip Number.'
DATABASE = '{code}: {context} database error for {account_id}.'
NOT_FOUND = '{code}: no {item} found for {key}.'
PATH_PARAM = '{code}: a {param_name} path parameter is required.'
PATH_MISMATCH = '{code}: the path value ({path_value}) does not match the data {description} value ({data_value}).'
HISTORICAL = '{code}: the Financing Statement for registration number {reg_num} has been discharged.'
DEBTOR_NAME = '{code}: No match found for the provided debtor name and registration.'
REPORT = '{code}: error generating report. Detail: {detail}'
DEFAULT = '{code}: error processing request.'
PAYMENT = '{code}:{status} payment error for account {account_id}.'

PARTY_REGISTERING = 'RG'
PARTY_SECURED = 'SP'

CERTIFIED_PARAM = 'certified'
ROUTING_SLIP_PARAM = 'routingSlipNumber'
DAT_NUMBER_PARAM = 'datNumber'
BCOL_NUMBER_PARAM = 'bcolAccountNumber'

REG_STAFF_DESC = 'BC Registries Staff'
SBC_STAFF_DESC = 'SBC Staff'
BCOL_STAFF_DESC = 'BC Online Help'
# Account registration request parameters
FROM_UI_PARAM = 'fromUI'
PAGE_NUM_PARAM = 'pageNumber'
SORT_DIRECTION_PARAM = 'sortDirection'
SORT_CRITERIA_PARAM = 'sortCriteriaName'
REG_NUMBER_PARAM = 'registrationNumber'
REG_TYPE_PARAM = 'registrationType'
START_TS_PARAM = 'startDateTime'
END_TS_PARAM = 'endDateTime'
STATUS_PARAM = 'statusType'
CLIENT_REF_PARAM = 'clientReferenceId'
REGISTER_NAME_PARAM = 'registeringName'


class CallbackExceptionCodes(BaseEnum):
    """Render an Enum of exception codes to facilitate source of exception."""

    UNKNOWN_ID = '01'
    MAX_RETRIES = '02'
    INVALID_ID = '03'
    DEFAULT = '04'
    REPORT_DATA_ERR = '05'
    REPORT_ERR = '06'
    STORAGE_ERR = '07'
    NOTIFICATION_ERR = '08'
    FILE_TRANSFER_ERR = '09'
    SETUP_ERR = '10'


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


def get_staff_account_id(req):
    """Get reg staff account ID from request headers."""
    return req.headers.get('Staff-Account-Id')


def is_pdf(req):
    """Check if request headers Accept is application/pdf."""
    accept = req.headers.get('Accept')
    return accept and accept.upper() == 'APPLICATION/PDF'


def get_apikey(req):
    """Get gateway api key from request headers."""
    return req.headers.get('x-apikey')


def account_required_response():
    """Build account required error response."""
    message = ACCOUNT_REQUIRED.format(code=ResourceErrorCodes.ACCOUNT_REQUIRED_ERR.value)
    return jsonify({'message': message}), HTTPStatus.BAD_REQUEST


def error_response(status_code, message):
    """Build generic error response."""
    return jsonify({'message': message}), status_code


def bad_request_response(message):
    """Build generic bad request response."""
    return jsonify({'message': message}), HTTPStatus.BAD_REQUEST


def staff_payment_bcol_fas():
    """Build staff payment info error response."""
    message = STAFF_SEARCH_BCOL_FAS.format(code=ResourceErrorCodes.VALIDATION_ERR.value)
    return jsonify({'message': message}), HTTPStatus.BAD_REQUEST


def sbc_payment_invalid():
    """Build sbc payment info error response."""
    message = SBC_SEARCH_NO_PAYMENT.format(code=ResourceErrorCodes.VALIDATION_ERR.value)
    return jsonify({'message': message}), HTTPStatus.BAD_REQUEST


def validation_error_response(errors, cause, additional_msg: str = None):
    """Build a schema validation error response."""
    message = ResourceErrorCodes.VALIDATION_ERR.value + ': ' + cause
    details = serialize(errors)
    if additional_msg:
        details.append('Additional validation: ' + additional_msg)
    return jsonify({'message': message, 'detail': details}), HTTPStatus.BAD_REQUEST


def db_exception_response(exception, account_id: str, context: str):
    """Build a database error response."""
    message = DATABASE.format(code=ResourceErrorCodes.DATABASE_ERR.value, context=context, account_id=account_id)
    current_app.logger.error(message)
    return jsonify({'message': message, 'detail': str(exception)}), HTTPStatus.INTERNAL_SERVER_ERROR


def business_exception_response(exception):
    """Build business exception error response."""
    current_app.logger.error(str(exception))
    return jsonify({'message': exception.error}), exception.status_code


def pay_exception_response(exception: SBCPaymentException, account_id: str = None):
    """Build pay 402 exception error response."""
    status = exception.status_code
    message = PAYMENT.format(code=ResourceErrorCodes.PAY_ERR.value, status=status, account_id=account_id)
    if exception.json_data:
        detail = exception.json_data.get('detail', '')
        err_type = exception.json_data.get('type', '')
        return jsonify({'message': message, 'status_code': status, 'type': err_type, 'detail': detail}), \
            HTTPStatus.PAYMENT_REQUIRED

    current_app.logger.error(str(exception))
    return jsonify({'message': message, 'detail': str(exception)}), HTTPStatus.PAYMENT_REQUIRED


def default_exception_response(exception):
    """Build default 500 exception error response."""
    message = DEFAULT.format(code=ResourceErrorCodes.DEFAULT_ERR.value)
    try:
        current_app.logger.error(str(exception))
        return jsonify({'message': message, 'detail': str(exception)}), HTTPStatus.INTERNAL_SERVER_ERROR
    except TypeError:
        return jsonify({'message': message, 'detail': 'Not available.'}), HTTPStatus.INTERNAL_SERVER_ERROR


def service_exception_response(message):
    """Build 500 exception error response."""
    return jsonify({'message': message}), HTTPStatus.INTERNAL_SERVER_ERROR


def not_found_error_response(item, key):
    """Build a not found error response."""
    message = NOT_FOUND.format(code=ResourceErrorCodes.NOT_FOUND_ERR.value, item=item, key=key)
    current_app.logger.info(str(HTTPStatus.NOT_FOUND.value) + ': ' + message)
    return jsonify({'message': message}), HTTPStatus.NOT_FOUND


def duplicate_error_response(message):
    """Build a duplicate request error response."""
    err_msg = ResourceErrorCodes.DUPLICATE_ERR.value + ': ' + message
    current_app.logger.info(str(HTTPStatus.CONFLICT.value) + ': ' + message)
    return jsonify({'message': err_msg}), HTTPStatus.CONFLICT


def unauthorized_error_response(account_id):
    """Build an unauthorized error response."""
    message = UNAUTHORIZED.format(code=ResourceErrorCodes.UNAUTHORIZED_ERR.value, account_id=account_id)
    current_app.logger.info(str(HTTPStatus.UNAUTHORIZED.value) + ': ' + message)
    return jsonify({'message': message}), HTTPStatus.UNAUTHORIZED


def cc_forbidden_error_response(account_id):
    """Build a crown charge registration class access forbidden error response."""
    message = CROWN_CHARGE_FORBIDDEN.format(code=ResourceErrorCodes.UNAUTHORIZED_ERR.value, account_id=account_id)
    current_app.logger.info(str(HTTPStatus.FORBIDDEN.value) + ': ' + message)
    return jsonify({'message': message}), HTTPStatus.FORBIDDEN


def path_param_error_response(param_name):
    """Build a bad request param missing error response."""
    message = PATH_PARAM.format(code=ResourceErrorCodes.PATH_PARAM_ERR.value, param_name=param_name)
    current_app.logger.info(str(HTTPStatus.BAD_REQUEST.value) + ': ' + message)
    return jsonify({'message': message}), HTTPStatus.BAD_REQUEST


def unprocessable_error_response(description):
    """Build an unprocessable entity error response."""
    message = f'The {description} request could not be processed (no change/results).'
    current_app.logger.info(str(HTTPStatus.UNPROCESSABLE_ENTITY.value) + ': ' + message)
    return jsonify({'message': message}), HTTPStatus.UNPROCESSABLE_ENTITY


def path_data_mismatch_error_response(path_value, description, data_value):
    """Build a bad request path param - payload data mismatch error."""
    message = PATH_MISMATCH.format(code=ResourceErrorCodes.DATA_MISMATCH_ERR.value, path_value=path_value,
                                   description=description, data_value=data_value)
    current_app.logger.info(str(HTTPStatus.BAD_REQUEST.value) + ': ' + message)
    return jsonify({'message': message}), HTTPStatus.BAD_REQUEST


def historical_error_response(reg_num):
    """Build a bad request financing statement discharged (non-staff) error response."""
    message = HISTORICAL.format(code=ResourceErrorCodes.HISTORICAL_ERR.value, reg_num=reg_num)
    current_app.logger.info(str(HTTPStatus.BAD_REQUEST.value) + ': ' + message)
    return jsonify({'message': message}), HTTPStatus.BAD_REQUEST


def base_debtor_invalid_response():
    """Build an error response for no match on base debtor name."""
    message = DEBTOR_NAME.format(code=ResourceErrorCodes.DEBTOR_NAME_ERR.value)
    current_app.logger.info(str(HTTPStatus.BAD_REQUEST.value) + ': ' + message)
    return jsonify({'message': message}), HTTPStatus.BAD_REQUEST


def validate_financing(json_data: dict, account_id: str) -> str:
    """Perform non-schema extra validation on a financing statement."""
    error_msg = party_validator.validate_financing_parties(json_data)
    error_msg += financing_validator.validate(json_data, account_id)
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
    error_msg += registration_validator.validate_collateral(json_data, financing_statement)
    if error_msg != '':
        raise BusinessException(
            error=error_msg,
            status_code=HTTPStatus.BAD_REQUEST
        )


def get_account_name(token: str, account_id: str = None):  # pylint: disable=too-many-return-statements; added staff
    """Lookup the account organization name from the user token with an auth api call."""
    try:
        if account_id is not None and is_reg_staff_account(account_id):
            return REG_STAFF_DESC
        if account_id is not None and is_sbc_office_account(token, account_id):
            return SBC_STAFF_DESC
        if account_id is not None and is_bcol_help(account_id):
            return BCOL_STAFF_DESC

        orgs = user_orgs(token)
        if orgs and 'orgs' in orgs and orgs['orgs']:
            if (len(orgs['orgs']) == 1 or not account_id or not account_id.isdigit()):
                return orgs['orgs'][0]['name']
            for org in orgs['orgs']:
                if org['id'] == int(account_id):
                    return org['name']
        return None
    except Exception as err:  # pylint: disable=broad-except # noqa F841;
        current_app.logger.error('get_account_name failed: ' + str(err))
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
            error=ACCOUNT_ACCESS.format(code=ResourceErrorCodes.UNAUTHORIZED_ERR.value,
                                        account_id=account_id, registration_num=reg_num),
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
            error=ACCOUNT_ACCESS.format(code=ResourceErrorCodes.UNAUTHORIZED_ERR.value,
                                        account_id=account_id, registration_num=reg_num),
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


def build_staff_registration_payment(req: request, pay_trans_type: str, fee_quantity: int):
    """Extract payment information from request parameters."""
    payment_info = {
        'transactionType': pay_trans_type,
        'feeQuantity': fee_quantity,
        'waiveFees': False,
        'accountId': get_staff_account_id(req)
    }

    routing_slip = req.args.get(ROUTING_SLIP_PARAM)
    bcol_number = req.args.get(BCOL_NUMBER_PARAM)
    dat_number = req.args.get(DAT_NUMBER_PARAM)
    if routing_slip is not None:
        payment_info[ROUTING_SLIP_PARAM] = str(routing_slip)
    if bcol_number is not None:
        payment_info[BCOL_NUMBER_PARAM] = str(bcol_number)
    if dat_number is not None:
        payment_info[DAT_NUMBER_PARAM] = str(dat_number)
    if not routing_slip and not bcol_number:
        payment_info['waiveFees'] = True

    return payment_info


def get_payment_details(registration):
    """Extract the payment details value from the registration request."""
    label = ' Registration:'
    value = registration.base_registration_num
    if registration.registration_type_cl == model_utils.REG_CLASS_DISCHARGE:
        label = 'Discharge' + label
    elif registration.registration_type_cl == model_utils.REG_CLASS_RENEWAL:
        label = 'Renew' + label
        value += ' for '
        if registration.life == 0:
            value += str(model_utils.REPAIRER_LIEN_DAYS) + ' days'
        elif registration.life == model_utils.LIFE_INFINITE:
            value += 'infinity'
        elif registration.life == 1:
            value += str(registration.life) + ' year'
        else:
            value += str(registration.life) + ' years'
    elif registration.registration_type_cl == model_utils.REG_CLASS_AMEND:
        label = 'Amendment of' + label
    elif registration.registration_type_cl == model_utils.REG_CLASS_AMEND_COURT:
        label = 'Court Order Amendment of' + label
    elif registration.registration_type_cl == model_utils.REG_CLASS_CHANGE:
        label = 'Change' + label

    details = {
        'label': label,
        'value': value
    }
    return details


def get_payment_type_financing(registration):
    """Derive the payment transaction type and quantity from the financing statement registration type or class."""
    pay_trans_type = TransactionTypes.FINANCING_LIFE_YEAR.value
    fee_quantity = registration.life
    if registration.registration_type_cl in (model_utils.REG_CLASS_CROWN, model_utils.REG_CLASS_MISC):
        pay_trans_type = TransactionTypes.FINANCING_NO_FEE.value
        fee_quantity = 1
    elif registration.registration_type in (model_utils.REG_TYPE_LAND_TAX_MH, model_utils.REG_TYPE_TAX_MH):
        pay_trans_type = TransactionTypes.FINANCING_NO_FEE.value
        fee_quantity = 1
    elif registration.registration_type == model_utils.REG_TYPE_MARRIAGE_SEPARATION:
        pay_trans_type = TransactionTypes.FINANCING_FR.value
        fee_quantity = 1
    elif registration.registration_type == model_utils.REG_TYPE_REPAIRER_LIEN:
        fee_quantity = 1
    elif registration.life == model_utils.LIFE_INFINITE:
        pay_trans_type = TransactionTypes.FINANCING_INFINITE.value
        fee_quantity = 1
    return pay_trans_type, fee_quantity


def get_payment_details_financing(registration):
    """Extract the payment details value from the request financing statement."""
    length = ' Length: '
    if registration.registration_type == model_utils.REG_TYPE_REPAIRER_LIEN:
        length += str(model_utils.REPAIRER_LIEN_DAYS) + ' days'
    elif registration.life == model_utils.LIFE_INFINITE:
        length += 'infinite'
    elif registration.life == 1:
        length += str(registration.life) + ' year'
    else:
        length += str(registration.life) + ' years'

    if not registration.reg_type:
        registration.get_registration_type()

    details = {
        'label': 'Register Financing Statement ' + registration.registration_num + ' Type:',
        'value': registration.reg_type.registration_desc + length
    }
    return details


def enqueue_verification_report(registration_id: int, party_id: int):
    """Add the mail verification report request to the mail verification queue."""
    try:
        payload = {
            'registrationId': registration_id,
            'partyId': party_id
        }
        apikey = current_app.config.get('SUBSCRIPTION_API_KEY')
        if apikey:
            payload['apikey'] = apikey
        GoogleQueueService().publish_verification_report(payload)
        current_app.logger.info(f'Enqueue mail verification report successful for id={registration_id}.')
    except Exception as err:  # noqa: B902; do not alter app processing
        msg = f'Enqueue mail verification report failed for id={registration_id}, party={party_id}: ' + str(err)
        current_app.logger.error(msg)
        EventTracking.create(registration_id,
                             EventTracking.EventTrackingTypes.SURFACE_MAIL,
                             int(HTTPStatus.INTERNAL_SERVER_ERROR),
                             msg)


def enqueue_registration_report(registration: Registration, json_data: dict, report_type: str):
    """Add the registration verification report request to the registration queue."""
    try:
        if json_data and report_type:
            # Signal registration report request is pending: record exists but no doc_storage_url.
            verification_report: VerificationReport = VerificationReport(create_ts=registration.registration_ts,
                                                                         registration_id=registration.id,
                                                                         report_data=json_data,
                                                                         report_type=report_type)
            verification_report.save()

        payload = {
            'registrationId': registration.id
        }
        apikey = current_app.config.get('SUBSCRIPTION_API_KEY')
        if apikey:
            payload['apikey'] = apikey
        GoogleQueueService().publish_registration_report(payload)
        current_app.logger.info(f'Enqueue registration report successful for id={registration.id}.')
    except DatabaseException as db_err:
        # Just log, do not return an error response.
        msg = f'Enqueue registration report db error for id={registration.id}: ' + str(db_err)
        current_app.logger.error(msg)
    except Exception as err:  # noqa: B902; do not alter app processing
        msg = f'Enqueue registration report failed for id={registration.id}: ' + str(err)
        current_app.logger.error(msg)
        EventTracking.create(registration.id,
                             EventTracking.EventTrackingTypes.REGISTRATION_REPORT,
                             int(HTTPStatus.INTERNAL_SERVER_ERROR),
                             msg)


def find_secured_party(registration: Registration, party_id: int):
    """Find secured party that belongs to a registration financing statement by id."""
    for party in registration.financing_statement.parties:
        if party.party_type == Party.PartyTypes.SECURED_PARTY.value and party.id == party_id:
            return party
    return None


def find_secured_parties(registration: Registration):
    """Find secured parties that are active at the time of the registration."""
    parties = []
    for party in registration.financing_statement.parties:
        if party.party_type == Party.PartyTypes.SECURED_PARTY.value and \
                (not party.registration_id_end or party.registration_id_end >= registration.id):
            parties.append(party)
    return parties


def same_party(party_1: dict, party_2: dict) -> bool:
    """Check that party name and address are identical (registering party is also secured party)."""
    if party_1['address'] != party_2['address']:
        return False
    if 'businessName' in party_1 and 'businessName' in party_2 and party_1['businessName'] == party_2['businessName']:
        return True
    if 'personName' in party_1 and 'personName' in party_2 and party_1['personName'] == party_2['personName']:
        return True
    return False


def queue_secured_party_verification(registration: Registration):
    """Set up mail out of verification statements to secured parties."""
    try:
        registering_json = None
        registration_id = registration.id
        for party in registration.parties:
            if party.party_type == Party.PartyTypes.REGISTERING_PARTY.value:
                registering_json = party.json
                break
        parties = find_secured_parties(registration)
        # Skip mailing verification statement if the secured party is also the registration registering party.
        for party in parties:
            if same_party(registering_json, party.json):
                msg = f'Queue secured party verification stmt skipped for id={registration_id}, partyId={party.id}.'
                current_app.logger.info(msg)
            else:
                # Setup mail report.
                statement_type = model_utils.REG_CLASS_TO_STATEMENT_TYPE[registration.registration_type_cl]
                reg_num_key = 'dischargeRegistrationNumber'
                if statement_type == model_utils.DRAFT_TYPE_AMENDMENT:
                    reg_num_key = 'amendmentRegistrationNumber'
                report_data = registration.verification_json(reg_num_key)
                cover_data = party.json
                cover_data['statementType'] = statement_type
                cover_data['partyType'] = party.party_type
                cover_data['createDateTime'] = report_data['createDateTime']
                cover_data['registrationNumber'] = registration.registration_num
                report_data['cover'] = cover_data
                mail_report: MailReport = MailReport(create_ts=registration.registration_ts,
                                                     registration_id=registration_id,
                                                     party_id=party.id,
                                                     report_data=report_data)
                mail_report.save()
                current_app.logger.debug(f'queueing reg_id={registration_id} party id={party.id}')
                enqueue_verification_report(registration_id, party.id)
    except Exception as err:  # noqa: B902; do not alter app processing
        msg = f'Queue secured party verification stmt failed for id={registration_id}: ' + str(err)
        current_app.logger.error(msg)


def get_account_registration_params(req: request, params: AccountRegistrationParams) -> AccountRegistrationParams:
    """Extract account registration query parameters from the request."""
    params.from_ui = req.args.get(FROM_UI_PARAM, False)
    params.page_number = int(req.args.get(PAGE_NUM_PARAM, -1))
    params.sort_direction = req.args.get(SORT_DIRECTION_PARAM, 'desc')
    params.sort_criteria = req.args.get(SORT_CRITERIA_PARAM, None)
    params.registration_number = req.args.get(REG_NUMBER_PARAM, None)
    params.registration_type = req.args.get(REG_TYPE_PARAM, None)
    params.status_type = req.args.get(STATUS_PARAM, None)
    params.client_reference_id = req.args.get(CLIENT_REF_PARAM, None)
    params.registering_name = req.args.get(REGISTER_NAME_PARAM, None)
    start_ts = req.args.get(START_TS_PARAM, None)
    end_ts = req.args.get(END_TS_PARAM, None)
    if start_ts and end_ts:
        params.start_date_time = start_ts
        params.end_date_time = end_ts
    if params.sort_direction is not None:
        params.sort_direction = params.sort_direction.lower()
    if params.registration_number is not None:
        params.registration_number = params.registration_number.strip().upper()
    return params


def valid_api_key(req) -> bool:
    """Verify the callback request api key is valid."""
    key = get_apikey(req)
    if not key:
        return False
    apikey = current_app.config.get('SUBSCRIPTION_API_KEY')
    if not apikey:
        return True
    return key == apikey
