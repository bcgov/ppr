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
from ppr_api.models import Address, ClientCode, ClientCodeHistorical, ClientCodeRegistration, db
from ppr_api.models.type_tables import ClientCodeTypes
from ppr_api.resources import financing_utils as fs_utils
from ppr_api.resources import utils as resource_utils
from ppr_api.services.authz import authorized, is_staff
from ppr_api.services.payment import TransactionTypes
from ppr_api.services.payment.exceptions import SBCPaymentException
from ppr_api.services.payment.payment import Payment
from ppr_api.utils.auth import jwt
from ppr_api.utils.logging import logger
from ppr_api.utils.validators import party_validator

bp = Blueprint("PARTY_CODES1", __name__, url_prefix="/api/v1/party-codes")  # pylint: disable=invalid-name
FUZZY_NAME_SEARCH_PARAM = "fuzzyNameSearch"
SECURITIES_ACT_PARAM = "securitiesActCodes"
QUERY_ACCOUNT_PARAM = "searchAccountId"  # Used by staff when looking up codes by BCRS account ID.
TO_PAY_DESCRIPTION = {
    ClientCodeTypes.CREATE_CODE.value: "Create client party code:",
    ClientCodeTypes.CHANGE_NAME.value: "Change client party code name:",
    ClientCodeTypes.CHANGE_ADDRESS.value: "Change client party code address:",
    ClientCodeTypes.CHANGE_NAME_ADDRESS.value: "Change client party code name and address:",
}
ROUTING_SLIP_PARAM = "routingSlipNumber"
DAT_NUMBER_PARAM = "datNumber"
BCOL_NUMBER_PARAM = "bcolAccountNumber"
SAVE_ERROR_MESSAGE = "Account {0} client party code save failed: {1}"
PAY_REFUND_MESSAGE = "Account {0} client party code refunding payment for invoice {1}."
PAY_REFUND_ERROR = "Account {0} client party code payment refund failed for invoice {1}: {2}."


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


@bp.route("/accounts/names", methods=["PATCH", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def change_account_code_name():
    """Change a client party code name either at the head office level or at the branch level."""
    try:
        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        request_json = request.get_json(silent=True)
        codes = []
        head_code: str = request_json.get("headOfficeCode")
        branch_code: str = request_json.get("code")
        if head_code:
            codes = ClientCode.find_by_head_office_code(head_code, False)
            if not codes:
                return resource_utils.not_found_error_response("client party head office code", head_code)
        elif branch_code:
            code = ClientCode.find_by_code(branch_code, False)
            if not code:
                return resource_utils.not_found_error_response("client party code", branch_code)
            else:
                codes.append(code)
        # Validate request data against the schema.
        staff: bool = is_staff(jwt)
        extra_validation_msg = party_validator.validate_client_code_registration(
            request_json, ClientCodeTypes.CHANGE_NAME, account_id, staff
        )
        if extra_validation_msg != "":
            return resource_utils.validation_error_response("", fs_utils.VAL_ERROR, extra_validation_msg)
        reg: ClientCodeRegistration = pay_and_save_name_change(request_json, codes, staff, account_id)
        return jsonify(reg.client_code.json), HTTPStatus.OK
    except SBCPaymentException as pay_exception:
        return resource_utils.pay_exception_response(pay_exception, account_id)
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "POST account client party code")
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("/accounts/addresses", methods=["PATCH", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def change_account_code_address():
    """Change a client party code address."""
    try:
        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        request_json = request.get_json(silent=True)
        branch_code: str = request_json.get("code")
        if branch_code:
            code = ClientCode.find_by_code(branch_code, False)
            if not code:
                return resource_utils.not_found_error_response("client party code", branch_code)
        # Validate request data against the schema.
        staff: bool = is_staff(jwt)
        extra_validation_msg = party_validator.validate_client_code_registration(
            request_json, ClientCodeTypes.CHANGE_ADDRESS, account_id, staff
        )
        if extra_validation_msg != "":
            return resource_utils.validation_error_response("", fs_utils.VAL_ERROR, extra_validation_msg)
        reg: ClientCodeRegistration = pay_and_save_address_change(request_json, code, staff, account_id)
        return jsonify(reg.client_code.json), HTTPStatus.OK
    except SBCPaymentException as pay_exception:
        return resource_utils.pay_exception_response(pay_exception, account_id)
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "POST account client party code")
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


@bp.route("/accounts", methods=["PATCH", "OPTIONS"])
@cross_origin(origin="*")
@jwt.requires_auth
def change_account_code():
    """Change a client party code name and address."""
    try:
        # Quick check: must be staff or provide an account ID.
        account_id = resource_utils.get_account_id(request)
        if account_id is None:
            return resource_utils.account_required_response()
        # Verify request JWT and account ID
        if not authorized(account_id, jwt):
            return resource_utils.unauthorized_error_response(account_id)
        request_json = request.get_json(silent=True)
        branch_code: str = request_json.get("code")
        if branch_code:
            code = ClientCode.find_by_code(branch_code, False)
            if not code:
                return resource_utils.not_found_error_response("client party code", branch_code)
        # Validate request data against the schema.
        staff: bool = is_staff(jwt)
        extra_validation_msg = party_validator.validate_client_code_registration(
            request_json, ClientCodeTypes.CHANGE_NAME_ADDRESS, account_id, staff
        )
        if extra_validation_msg != "":
            return resource_utils.validation_error_response("", fs_utils.VAL_ERROR, extra_validation_msg)
        reg: ClientCodeRegistration = pay_and_save_change(request_json, code, staff, account_id)
        return jsonify(reg.client_code.json), HTTPStatus.OK
    except SBCPaymentException as pay_exception:
        return resource_utils.pay_exception_response(pay_exception, account_id)
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, account_id, "POST account client party code")
    except BusinessException as exception:
        return resource_utils.business_exception_response(exception)
    except Exception as default_exception:  # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)


def pay_and_save_name_change(request_json: dict, codes: list, staff: bool, account_id: str) -> ClientCodeRegistration:
    """Pay for a client party code change and save name change registration data."""
    logger.info(f"New client party code name change request staff={staff} account ID={account_id}")
    token: dict = g.jwt_oidc_token_info
    reg: ClientCodeRegistration = ClientCodeRegistration.create_name_change_from_json(
        request_json, token.get("username"), codes[0]
    )
    payment, pay_ref = pay(request_json, account_id, reg.client_code_type, staff)
    invoice_id = pay_ref["invoiceId"]
    reg.pay_invoice_id = int(invoice_id)
    reg.pay_path = pay_ref["receipt"]
    try:
        save_name_change(request_json, codes, account_id, reg.create_ts)
        reg.save()
    except Exception as db_exception:  # noqa: B902; handle all db related errors.
        logger.error(SAVE_ERROR_MESSAGE.format(account_id, str(db_exception)))
        if invoice_id is not None:
            logger.info(PAY_REFUND_MESSAGE.format(account_id, invoice_id))
            try:
                payment.cancel_payment(invoice_id)
            except Exception as cancel_exception:  # noqa: B902; log exception
                logger.error(PAY_REFUND_ERROR.format(account_id, invoice_id, str(cancel_exception)))
        raise db_exception
    return reg


def pay_and_save_address_change(
    request_json: dict, code: ClientCode, staff: bool, account_id: str
) -> ClientCodeRegistration:
    """Pay for a client party code change and save address change registration data."""
    logger.info(f"New client party code address change request staff={staff} account ID={account_id}")
    token: dict = g.jwt_oidc_token_info
    reg: ClientCodeRegistration = ClientCodeRegistration.create_address_change_from_json(
        request_json, token.get("username"), code
    )
    payment, pay_ref = pay(request_json, account_id, reg.client_code_type, staff)
    invoice_id = pay_ref["invoiceId"]
    reg.pay_invoice_id = int(invoice_id)
    reg.pay_path = pay_ref["receipt"]
    try:
        save_address_change(request_json, code, account_id, reg.create_ts)
        reg.save()
    except Exception as db_exception:  # noqa: B902; handle all db related errors.
        logger.error(SAVE_ERROR_MESSAGE.format(account_id, str(db_exception)))
        if invoice_id is not None:
            logger.info(PAY_REFUND_MESSAGE.format(account_id, invoice_id))
            try:
                payment.cancel_payment(invoice_id)
            except Exception as cancel_exception:  # noqa: B902; log exception
                logger.error(PAY_REFUND_ERROR.format(account_id, invoice_id, str(cancel_exception)))
        raise db_exception
    return reg


def pay_and_save_change(request_json: dict, code: ClientCode, staff: bool, account_id: str) -> ClientCodeRegistration:
    """Pay for a client party code change and save name and address change registration data."""
    logger.info(f"New client party code name and address change request staff={staff} account ID={account_id}")
    token: dict = g.jwt_oidc_token_info
    reg: ClientCodeRegistration = ClientCodeRegistration.create_name_address_change_from_json(
        request_json, token.get("username"), code
    )
    payment, pay_ref = pay(request_json, account_id, reg.client_code_type, staff)
    invoice_id = pay_ref["invoiceId"]
    reg.pay_invoice_id = int(invoice_id)
    reg.pay_path = pay_ref["receipt"]
    try:
        save_name_address_change(request_json, code, account_id, reg.create_ts)
        reg.save()
    except Exception as db_exception:  # noqa: B902; handle all db related errors.
        logger.error(SAVE_ERROR_MESSAGE.format(account_id, str(db_exception)))
        if invoice_id is not None:
            logger.info(PAY_REFUND_MESSAGE.format(account_id, invoice_id))
            try:
                payment.cancel_payment(invoice_id)
            except Exception as cancel_exception:  # noqa: B902; log exception
                logger.error(PAY_REFUND_ERROR.format(account_id, invoice_id, str(cancel_exception)))
        raise db_exception
    return reg


def save_name_change(request_json: dict, codes: list, account_id: str, reg_ts):
    """Save name change registration data."""
    req_account_id: str = request_json.get("accountId") if request_json.get("accountId") else account_id
    new_name: str = str(request_json.get("businessName")).strip().upper()
    head_name: str = codes[0].name
    hist_type: str = ClientCodeHistorical.HistoricalTypes.NAME.value
    for code in codes:
        hist_code: ClientCodeHistorical = ClientCodeHistorical.create_from_client_code(code, hist_type)
        hist_code.save()
        code.name = str(code.name).replace(head_name, new_name)  # May be changed to code.name = new_name.
        code.date_ts = reg_ts
        if not code.account_id:
            code.account_id = req_account_id
        db.session.add(code)
        logger.info(f"Code {code.id} updating name from {hist_code.name} to {code.name}")


def save_name_address_change(request_json: dict, code: ClientCode, account_id: str, reg_ts):
    """Save name change registration data."""
    req_account_id: str = request_json.get("accountId") if request_json.get("accountId") else account_id
    new_name: str = str(request_json.get("businessName")).strip().upper()
    current_name: str = code.name
    hist_type: str = ClientCodeHistorical.HistoricalTypes.BOTH.value
    hist_code: ClientCodeHistorical = ClientCodeHistorical.create_from_client_code(code, hist_type)
    hist_code.save()
    code.address = Address.create_from_json(request_json.get("address"))
    code.name = str(code.name).replace(current_name, new_name)  # May be changed to code.name = new_name.
    code.date_ts = reg_ts
    if not code.account_id:
        code.account_id = req_account_id
    db.session.add(code)
    logger.info(f"Code {code.id} updated name to {code.name}, address to {code.address.json}")


def save_address_change(request_json: dict, code: ClientCode, account_id: str, reg_ts):
    """Save name change registration data."""
    req_account_id: str = request_json.get("accountId") if request_json.get("accountId") else account_id
    hist_type: str = ClientCodeHistorical.HistoricalTypes.ADDRESS.value
    hist_code: ClientCodeHistorical = ClientCodeHistorical.create_from_client_code(code, hist_type)
    hist_code.save()
    code.address = Address.create_from_json(request_json.get("address"))
    code.date_ts = reg_ts
    if not code.account_id:
        code.account_id = req_account_id
    db.session.add(code)
    logger.info(f"Code {code.id} updated address to {code.address.json}")


def get_payment_details(request_json: dict, reg_type: str) -> dict:
    """Extract the payment details value from the change party code request."""
    details = {"label": TO_PAY_DESCRIPTION[reg_type]}
    if request_json.get("code"):
        details["value"] = request_json.get("code")
    elif request_json.get("headOfficeCode"):
        details["value"] = request_json.get("headOfficeCode")
    else:
        details["value"] = ""
    return details


def pay(request_json: dict, account_id: str, req_type: str, staff: bool):
    """Set up and submit a pay-api request."""
    pay_ref = None
    payment = Payment(
        jwt=jwt.get_token_auth_header(),
        account_id=account_id,
        details=get_payment_details(request_json, req_type),
    )
    # Staff has special payment rules and setup.
    if staff:
        payment_info = build_staff_payment(account_id)
        # bcol help is no fee; reg staff can be no fee.
        # FAS is routing slip only.
        # BCOL is dat number (optional) and BCOL account number (mandatory).
        # All staff roles including SBC can submit no fee searches.
        logger.info(f"Staff payment info: {payment_info}")
        pay_ref = payment.create_payment_staff_client_code(payment_info)
    else:
        transaction_type = TransactionTypes.CLIENT_CODE_CHANGE.value
        pay_ref = payment.create_payment(transaction_type, 1, None, None)
    return payment, pay_ref


def build_staff_payment(req_account_id: str):
    """Extract payment information from request parameters."""
    account_id: str = resource_utils.get_staff_account_id(request)
    if not account_id:
        account_id = req_account_id
    logger.info(f"Setting up staff payment for {account_id}.")
    payment_info = {
        "transactionType": TransactionTypes.CLIENT_CODE_CHANGE.value,
        "feeQuantity": 1,
        "accountId": account_id,
    }
    routing_slip = request.args.get(ROUTING_SLIP_PARAM)
    bcol_number = request.args.get(BCOL_NUMBER_PARAM)
    dat_number = request.args.get(DAT_NUMBER_PARAM)
    if routing_slip is not None:
        payment_info[ROUTING_SLIP_PARAM] = str(routing_slip)
    if bcol_number is not None:
        payment_info[BCOL_NUMBER_PARAM] = str(bcol_number)
    if dat_number is not None:
        payment_info[DAT_NUMBER_PARAM] = str(dat_number)
    if ROUTING_SLIP_PARAM not in payment_info and BCOL_NUMBER_PARAM not in payment_info:
        payment_info["waiveFees"] = True
        # payment_info["transactionType"] = TransactionTypes.CLIENT_CODE_STAFF_NO_FEE.value
    return payment_info
