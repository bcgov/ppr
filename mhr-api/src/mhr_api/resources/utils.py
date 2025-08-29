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
from enum import Enum
from http import HTTPStatus

from flask import current_app, jsonify, request

from mhr_api.exceptions import ResourceErrorCodes
from mhr_api.models import registration_utils as reg_utils
from mhr_api.models import utils as model_utils
from mhr_api.models.registration_utils import AccountRegistrationParams
from mhr_api.services.authz import is_bcol_help, is_reg_staff_account, is_sbc_office_account, user_orgs
from mhr_api.services.payment.exceptions import SBCPaymentException
from mhr_api.utils import admin_validator, manufacturer_validator, note_validator, registration_validator
from mhr_api.utils.logging import logger

# Resource error messages
# Model business error messages in models.utils.py
ACCOUNT_REQUIRED = "{code}: The request is missing the required Account-Id header."
UNAUTHORIZED = "{code}: The user {account_id} does not have the necessary role to submit this registration request."
UNAUTHORIZED_HELPDESK = "{code}: Help desk users are not permitted to create this type of registration ({reg_type})."
ACCOUNT_ACCESS = (
    "{code}: the account ID {account_id} cannot access statement information for " + "mhr number {mhr_num}."
)
STAFF_SEARCH_BCOL_FAS = "{code}: provide either a BCOL Account Number or a Routing Slip Number but not both."
SBC_SEARCH_NO_PAYMENT = "{code}: provide either a BCOL Account Number or a Routing Slip Number."
DATABASE = "{code}: An error occurred while accessing the database for the given account ({account_id}). {context}."
NOT_FOUND = "{code}: no {item} found for {key}."
PATH_PARAM = "{code}: A required path parameter {param_name} is missing from the request URL."
PATH_MISMATCH = "{code}: the path value ({path_value}) does not match the data {description} value ({data_value})."
REPORT = "{code}: error generating report. Detail: {detail}"
DEFAULT = "{code}: An unexpected error occurred while processing the request."
PAYMENT = "{code}: A payment processing error occurred for the specified account ({account_id}). {status}."
DUPLICATE_REGISTRATION_ERROR = "MH Registration {0} is already available to the account."

CERTIFIED_PARAM = "certified"
ROUTING_SLIP_PARAM = "routingSlipNumber"
DAT_NUMBER_PARAM = "datNumber"
BCOL_NUMBER_PARAM = "bcolAccountNumber"
PRIORITY_PARAM = "priority"
CLIENT_REF_PARAM = "clientReferenceId"

REG_STAFF_DESC = "BC Registries Staff"
SBC_STAFF_DESC = "SBC Staff"
BCOL_STAFF_DESC = "BC Online Help"
# Account registration request parameters
FROM_UI_PARAM = "fromUI"


class CallbackExceptionCodes(str, Enum):
    """Render an Enum of exception codes to facilitate source of exception."""

    UNKNOWN_ID = "01"
    MAX_RETRIES = "02"
    INVALID_ID = "03"
    DEFAULT = "04"
    REPORT_DATA_ERR = "05"
    REPORT_ERR = "06"
    STORAGE_ERR = "07"
    NOTIFICATION_ERR = "08"
    FILE_TRANSFER_ERR = "09"
    SETUP_ERR = "10"


def serialize(errors):
    """Serialize errors."""
    error_message = []
    if errors:
        for error in errors:
            error_message.append("Schema validation: " + error.message + ".")
    return error_message


def get_account_id(req):
    """Get account ID from request headers."""
    return req.headers.get("Account-Id")


def get_staff_account_id(req):
    """Get reg staff account ID from request headers."""
    return req.headers.get("Staff-Account-Id")


def is_pdf(req):
    """Check if request headers Accept is application/pdf."""
    accept = req.headers.get("Accept")
    return accept and accept.upper() == "APPLICATION/PDF"


def get_apikey(req):
    """Get gateway api key from request headers or parameter."""
    key = req.headers.get("x-apikey")
    if not key:
        key = request.args.get("x-apikey")
    return key


def account_required_response():
    """Build account required error response."""
    message = ACCOUNT_REQUIRED.format(code=ResourceErrorCodes.ACCOUNT_REQUIRED_ERR.value)
    return jsonify({"message": message}), HTTPStatus.BAD_REQUEST


def error_response(status_code, message):
    """Build generic error response."""
    return jsonify({"message": message}), status_code


def bad_request_response(message):
    """Build generic bad request response."""
    return jsonify({"message": message}), HTTPStatus.BAD_REQUEST


def staff_payment_bcol_fas():
    """Build staff payment info error response."""
    message = STAFF_SEARCH_BCOL_FAS.format(code=ResourceErrorCodes.VALIDATION_ERR.value)
    return jsonify({"message": message}), HTTPStatus.BAD_REQUEST


def sbc_payment_invalid():
    """Build sbc payment info error response."""
    message = SBC_SEARCH_NO_PAYMENT.format(code=ResourceErrorCodes.VALIDATION_ERR.value)
    return jsonify({"message": message}), HTTPStatus.BAD_REQUEST


def validation_error_response(errors, cause, additional_msg: str = None):
    """Build a schema validation error response."""
    message = ResourceErrorCodes.VALIDATION_ERR + ": " + cause
    details = serialize(errors)
    if additional_msg:
        details.append("Additional validation: " + additional_msg)
    return jsonify({"message": message, "detail": details}), HTTPStatus.BAD_REQUEST


def db_exception_response(exception, account_id: str, context: str):
    """Build a database error response."""
    message = DATABASE.format(code=ResourceErrorCodes.DATABASE_ERR.value, context=context, account_id=account_id)
    logger.error(message)
    return jsonify({"message": message, "detail": str(exception)}), HTTPStatus.INTERNAL_SERVER_ERROR


def business_exception_response(exception):
    """Build business exception error response."""
    logger.error(str(exception))
    return jsonify({"message": exception.error}), exception.status_code


def pay_exception_response(exception: SBCPaymentException, account_id: str = None):
    """Build pay 402 exception error response."""
    status = exception.status_code
    message = PAYMENT.format(code=ResourceErrorCodes.PAY_ERR.value, status=status, account_id=account_id)
    if exception.json_data:
        detail = exception.json_data.get("detail", "")
        err_type = exception.json_data.get("type", "")
        return (
            jsonify({"message": message, "status_code": status, "type": err_type, "detail": detail}),
            HTTPStatus.PAYMENT_REQUIRED,
        )

    logger.error(str(exception))
    return jsonify({"message": message, "detail": str(exception)}), HTTPStatus.PAYMENT_REQUIRED


def default_exception_response(exception):
    """Build default 500 exception error response."""
    logger.error(str(exception))
    message = DEFAULT.format(code=ResourceErrorCodes.DEFAULT_ERR.value)
    return jsonify({"message": message, "detail": str(exception)}), HTTPStatus.INTERNAL_SERVER_ERROR


def service_exception_response(message):
    """Build 500 exception error response."""
    return jsonify({"message": message}), HTTPStatus.INTERNAL_SERVER_ERROR


def not_found_error_response(item, key):
    """Build a not found error response."""
    message = NOT_FOUND.format(code=ResourceErrorCodes.NOT_FOUND_ERR.value, item=item, key=key)
    logger.info(str(HTTPStatus.NOT_FOUND.value) + ": " + message)
    return jsonify({"message": message}), HTTPStatus.NOT_FOUND


def duplicate_error_response(message):
    """Build a duplicate request error response."""
    err_msg = ResourceErrorCodes.DUPLICATE_ERR + ": " + message
    logger.info(str(HTTPStatus.CONFLICT.value) + ": " + message)
    return jsonify({"message": err_msg}), HTTPStatus.CONFLICT


def unauthorized_error_response(account_id):
    """Build an unauthorized error response."""
    message = UNAUTHORIZED.format(code=ResourceErrorCodes.UNAUTHORIZED_ERR.value, account_id=account_id)
    logger.info(str(HTTPStatus.UNAUTHORIZED.value) + ": " + message)
    return jsonify({"message": message}), HTTPStatus.UNAUTHORIZED


def helpdesk_unauthorized_error_response(reg_type: str):
    """Build an helpdesk registration unauthorized error response."""
    message = UNAUTHORIZED_HELPDESK.format(code=ResourceErrorCodes.UNAUTHORIZED_ERR.value, reg_type=reg_type)
    logger.error(str(HTTPStatus.UNAUTHORIZED.value) + ": " + message)
    return jsonify({"message": message}), HTTPStatus.UNAUTHORIZED


def path_param_error_response(param_name):
    """Build a bad request param missing error response."""
    message = PATH_PARAM.format(code=ResourceErrorCodes.PATH_PARAM_ERR.value, param_name=param_name)
    logger.info(str(HTTPStatus.BAD_REQUEST.value) + ": " + message)
    return jsonify({"message": message}), HTTPStatus.BAD_REQUEST


def unprocessable_error_response(description):
    """Build an unprocessable entity error response."""
    message = f"The {description} request could not be processed (no change/results)."
    logger.info(str(HTTPStatus.UNPROCESSABLE_ENTITY.value) + ": " + message)
    return jsonify({"message": message}), HTTPStatus.UNPROCESSABLE_ENTITY


def path_data_mismatch_error_response(path_value, description, data_value):
    """Build a bad request path param - payload data mismatch error."""
    message = PATH_MISMATCH.format(
        code=ResourceErrorCodes.DATA_MISMATCH_ERR.value,
        path_value=path_value,
        description=description,
        data_value=data_value,
    )
    logger.info(str(HTTPStatus.BAD_REQUEST.value) + ": " + message)
    return jsonify({"message": message}), HTTPStatus.BAD_REQUEST


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
        if orgs and "orgs" in orgs and orgs["orgs"]:
            if len(orgs["orgs"]) == 1 or not account_id or not account_id.isdigit():
                return orgs["orgs"][0]["name"]
            for org in orgs["orgs"]:
                if org["id"] == int(account_id):
                    return org["name"]
        return None
    except Exception as err:  # pylint: disable=broad-except # noqa F841;
        logger.error("get_account_name failed: " + str(err))
        return None


def validate_registration(json_data, is_staff: bool = False):
    """Perform non-schema extra validation on a MH new registration."""
    return registration_validator.validate_registration(json_data, is_staff)


def validate_registration_manufacturer(json_data, manufacturer):
    """Perform non-schema extra validation on a MH new registration for a manufacturer."""
    return manufacturer_validator.validate_registration(json_data, manufacturer)


def validate_transfer(registration, json_data, is_staff: bool, group: str):
    """Perform non-schema extra validation on a transfer registration."""
    return registration_validator.validate_transfer(registration, json_data, is_staff, group)


def validate_exemption(registration, json_data, is_staff: bool = False):
    """Perform non-schema extra validation on an exemption registration."""
    return registration_validator.validate_exemption(registration, json_data, is_staff)


def validate_permit(registration, json_data, account_id: str, is_staff: bool = False, group_name: str = None):
    """Perform non-schema extra validation on a transport permit registration."""
    return registration_validator.validate_permit(registration, json_data, account_id, is_staff, group_name)


def validate_note(registration, json_data, is_staff: bool, group: str):
    """Perform non-schema extra validation on a unit note registration."""
    return note_validator.validate_note(registration, json_data, is_staff, group)


def validate_admin_registration(registration, json_data, is_staff: bool):
    """Perform non-schema extra validation on an admin registration."""
    return admin_validator.validate_admin_reg(registration, json_data, is_staff)


def valid_api_key(req) -> bool:
    """Verify the callback request api key is valid."""
    key = get_apikey(req)
    if not key:
        return False
    apikey = current_app.config.get("SUBSCRIPTION_API_KEY")
    if not apikey:
        return True
    return key == apikey


def get_account_registration_params(req: request, params: AccountRegistrationParams) -> AccountRegistrationParams:
    """Extract account registration query parameters from the request."""
    params.from_ui = req.args.get(FROM_UI_PARAM, False)
    params.page_number = int(req.args.get(reg_utils.PAGE_NUM_PARAM, -1))
    params.sort_direction = req.args.get(reg_utils.SORT_DIRECTION_PARAM, reg_utils.SORT_DESCENDING)
    params.sort_criteria = req.args.get(reg_utils.SORT_CRITERIA_PARAM, None)
    params.filter_mhr_number = req.args.get(reg_utils.MHR_NUMBER_PARAM, None)
    params.filter_registration_type = req.args.get(reg_utils.REG_TYPE_PARAM, None)
    params.filter_status_type = req.args.get(reg_utils.STATUS_PARAM, None)
    params.filter_client_reference_id = req.args.get(reg_utils.CLIENT_REF_PARAM, None)
    params.filter_submitting_name = req.args.get(reg_utils.SUBMITTING_NAME_PARAM, None)
    params.filter_username = req.args.get(reg_utils.USER_NAME_PARAM, None)
    params.filter_reg_start_date = req.args.get(reg_utils.START_TS_PARAM, None)
    params.filter_reg_end_date = req.args.get(reg_utils.END_TS_PARAM, None)
    params.filter_document_id = req.args.get(reg_utils.DOCUMENT_ID_PARAM, None)
    params.filter_manufacturer = req.args.get(reg_utils.MANUFACTURER_NAME_PARAM, None)
    # start_ts = req.args.get(reg_utils.START_TS_PARAM, None)
    # end_ts = req.args.get(reg_utils.END_TS_PARAM, None)
    # if start_ts and end_ts:
    #    params.start_date_time = start_ts
    #    params.end_date_time = end_ts
    if params.sort_direction:
        params.sort_direction = params.sort_direction.lower()
        if params.sort_direction == "asc":
            params.sort_direction = reg_utils.SORT_ASCENDING
        elif params.sort_direction == "desc":
            params.sort_direction = reg_utils.SORT_DESCENDING
    if params.filter_mhr_number:
        params.filter_mhr_number = model_utils.format_mhr_number(params.filter_mhr_number)
        params.filter_mhr_number = remove_quotes(params.filter_mhr_number)
    if params.filter_submitting_name:
        params.filter_submitting_name = params.filter_submitting_name.strip().upper()
        params.filter_submitting_name = remove_quotes(params.filter_submitting_name)
    if params.filter_username:
        params.filter_username = params.filter_username.strip().upper()
        params.filter_username = remove_quotes(params.filter_username)
    if params.filter_client_reference_id:
        params.filter_client_reference_id = params.filter_client_reference_id.strip().upper()
        params.filter_client_reference_id = remove_quotes(params.filter_client_reference_id)
    if params.filter_reg_start_date:
        params.filter_reg_start_date = remove_quotes(params.filter_reg_start_date)
    if params.filter_reg_end_date:
        params.filter_reg_end_date = remove_quotes(params.filter_reg_end_date)
    if params.filter_manufacturer:
        params.filter_manufacturer = params.filter_manufacturer.strip().upper()
        params.filter_manufacturer = remove_quotes(params.filter_manufacturer)
    return params


def remove_quotes(text: str) -> str:
    """Remove single and double quotation marks from request parameters."""
    if text:
        text = text.replace("'", "''")
        text = text.replace('"', '""')
    return text
