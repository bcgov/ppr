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
"""Helper methods for financing statements and updates to financing statements."""
# import json
# from http import HTTPStatus

from flask import request, current_app, g

from mhr_api.exceptions import DatabaseException
from mhr_api.models import MhrRegistration
# from mhr_api.models import utils as model_utils
# from mhr_api.reports import ReportTypes, get_callback_pdf, get_pdf, get_report_api_payload
from mhr_api.resources import utils as resource_utils
from mhr_api.services.authz import is_reg_staff_account
from mhr_api.services.payment.exceptions import SBCPaymentException
from mhr_api.services.payment.payment import Payment
# from mhr_api.services.utils.exceptions import ReportDataException, ReportException, StorageException
# from mhr_api.services.document_storage.storage_service import DocumentTypes, GoogleStorageService
from mhr_api.utils.auth import jwt


VAL_ERROR = 'Registration request data validation errors.'  # Default validation error prefix
SAVE_ERROR_MESSAGE = 'Account {0} create {1} statement db save failed: {2}'
PAY_REFUND_MESSAGE = 'Account {0} create {1} statement refunding payment for invoice {2}.'
PAY_REFUND_ERROR = 'Account {0} create {1} statement payment refund failed for invoice {2}: {3}.'
DUPLICATE_REGISTRATION_ERROR = 'Registration {0} is already available to the account.'
# Payment detail/transaction description by registration.
REG_CLASS_TO_STATEMENT_TYPE = {
    'AMENDMENT': 'Register an Amendment Statement',
    'COURTORDER': 'Register an Amendment Statement',
    'CHANGE': 'Register a Change Statement',
    'RENEWAL': 'Register a Renewal Statement',
    'DISCHARGE': 'Register a Discharge Statement'
}
CALLBACK_MESSAGES = {
    resource_utils.CallbackExceptionCodes.UNKNOWN_ID: '01: no registration data found for id={key_id}.',
    resource_utils.CallbackExceptionCodes.MAX_RETRIES: '02: maximum retries reached for id={key_id}.',
    resource_utils.CallbackExceptionCodes.INVALID_ID: '03: no registration found for id={key_id}.',
    resource_utils.CallbackExceptionCodes.DEFAULT: '04: default error for id={key_id}.',
    resource_utils. CallbackExceptionCodes.REPORT_DATA_ERR: '05: report data error for id={key_id}.',
    resource_utils. CallbackExceptionCodes.REPORT_ERR: '06: generate report failed for id={key_id}.',
    resource_utils.CallbackExceptionCodes.FILE_TRANSFER_ERR: '09: SFTP failed for id={key_id}.',
    resource_utils.CallbackExceptionCodes.SETUP_ERR: '10: setup failed for id={key_id}.'
}
PAY_DETAILS_LABEL = 'MH Registration Type:'
PAY_DETAILS_LABEL_TRANS_ID = 'MH Registration {trans_id} Type:'


def pay_and_save_registration(req: request, request_json, account_id: str, trans_type: str, trans_id: str = None):
    """Set up the registration statement, pay, and save the data."""
    # Charge a fee.
    token: dict = g.jwt_oidc_token_info
    registration: MhrRegistration = MhrRegistration.create_new_from_json(request_json,
                                                                         account_id,
                                                                         token.get('username', None))
    invoice_id = None
    pay_ref = None
    if not is_reg_staff_account(account_id):
        payment = Payment(jwt=jwt.get_token_auth_header(),
                          account_id=account_id,
                          details=get_payment_details(registration, trans_id))
        pay_ref = payment.create_payment(trans_type, 1, trans_id, registration.client_reference_id, False)
    else:
        payment_info = build_staff_payment(req, trans_type, 1, trans_id)
        payment = Payment(jwt=jwt.get_token_auth_header(),
                          account_id=None,
                          details=get_payment_details(registration, trans_id))
        pay_ref = payment.create_payment_staff(payment_info, registration.client_reference_id)
    invoice_id = pay_ref['invoiceId']
    registration.pay_invoice_id = int(invoice_id)
    registration.pay_path = pay_ref['receipt']
    # Try to save the financing statement: failure throws an exception.
    try:
        registration.save()
    except Exception as db_exception:   # noqa: B902; handle all db related errors.
        current_app.logger.error(SAVE_ERROR_MESSAGE.format(account_id, 'registration', str(db_exception)))
        if account_id and invoice_id is not None:
            current_app.logger.info(PAY_REFUND_MESSAGE.format(account_id, 'registration', invoice_id))
            try:
                payment.cancel_payment(invoice_id)
            except SBCPaymentException as cancel_exception:
                current_app.logger.error(PAY_REFUND_ERROR.format(account_id, 'registration', invoice_id,
                                                                 str(cancel_exception)))
        raise DatabaseException(db_exception)
    return registration


def build_staff_payment(req: request, trans_type: str, quantity: int = 1, transaction_id: str = None):
    """Extract staff payment information from request parameters."""
    payment_info = {
        'transactionType': trans_type,
        'quantity': quantity,
        'waiveFees': True
    }
    if transaction_id:
        payment_info['transactionId'] = transaction_id

    certified = req.args.get(resource_utils.CERTIFIED_PARAM)
    routing_slip = req.args.get(resource_utils.ROUTING_SLIP_PARAM)
    bcol_number = req.args.get(resource_utils.BCOL_NUMBER_PARAM)
    dat_number = req.args.get(resource_utils.DAT_NUMBER_PARAM)
    priority = req.args.get(resource_utils.PRIORITY_PARAM)
    if certified is not None and isinstance(certified, bool) and certified:
        payment_info[resource_utils.CERTIFIED_PARAM] = True
    elif certified is not None and isinstance(certified, str) and \
            certified.lower() in ['true', '1', 'y', 'yes']:
        payment_info[resource_utils.CERTIFIED_PARAM] = True
    if routing_slip is not None:
        payment_info[resource_utils.ROUTING_SLIP_PARAM] = str(routing_slip)
    if bcol_number is not None:
        payment_info[resource_utils.BCOL_NUMBER_PARAM] = str(bcol_number)
    if dat_number is not None:
        payment_info[resource_utils.DAT_NUMBER_PARAM] = str(dat_number)
    if priority is not None and isinstance(priority, bool) and priority:
        payment_info[resource_utils.PRIORITY_PARAM] = True
    elif priority is not None and isinstance(priority, str) and \
            priority.lower() in ['true', '1', 'y', 'yes']:
        payment_info[resource_utils.PRIORITY_PARAM] = True

    if resource_utils.ROUTING_SLIP_PARAM in payment_info or resource_utils.BCOL_NUMBER_PARAM in payment_info:
        payment_info['waiveFees'] = False
    current_app.logger.debug(payment_info)
    return payment_info


def get_payment_details(registration: MhrRegistration, trans_id: str = None):
    """Build pay api transaction description details."""
    if not registration.reg_type:
        registration.get_registration_type()

    label = PAY_DETAILS_LABEL
    if trans_id:
        label = PAY_DETAILS_LABEL_TRANS_ID.format(trans_id=trans_id)
    details = {
        'label': label,
        'value': registration.reg_type.registration_type_desc
    }
    return details
