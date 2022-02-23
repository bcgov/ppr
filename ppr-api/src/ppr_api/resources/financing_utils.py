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
import json
from http import HTTPStatus

from flask import request, current_app, g

from ppr_api.exceptions import BusinessException, DatabaseException
from ppr_api.models import EventTracking, FinancingStatement, Party, Registration, VerificationReport
from ppr_api.models import utils as model_utils
from ppr_api.reports import ReportTypes, get_callback_pdf, get_pdf, get_report_api_payload
from ppr_api.resources import utils as resource_utils
from ppr_api.services.authz import is_reg_staff_account, is_sbc_office_account
from ppr_api.services.payment import TransactionTypes
from ppr_api.services.payment.client import SBCPaymentClient
from ppr_api.services.payment.exceptions import SBCPaymentException
from ppr_api.services.payment.payment import Payment
from ppr_api.callback.utils.exceptions import ReportDataException, ReportException, StorageException
from ppr_api.callback.document_storage.storage_service import DocumentTypes, GoogleStorageService
from ppr_api.utils.auth import jwt


VAL_ERROR = 'Financing Statement request data validation errors.'  # Default validation error prefix
VAL_ERROR_AMEND = 'Amendment Statement request data validation errors.'  # Amendment validation error prefix
VAL_ERROR_CHANGE = 'Change Statement request data validation errors.'  # Change validation error prefix
VAL_ERROR_RENEWAL = 'Renewal Statement request data validation errors.'  # Renewal validation error prefix
VAL_ERROR_DISCHARGE = 'Discharge Statement request data validation errors.'  # Discharge validation error prefix
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
COLLAPSE_PARAM = 'collapse'
CURRENT_PARAM = 'current'
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


def pay_and_save(req: request,  # pylint: disable=too-many-arguments,too-many-locals,too-many-branches
                 request_json, registration_class, financing_statement, registration_num, account_id):
    """Set up the registration, pay if there is an account id, and save the data."""
    token: dict = g.jwt_oidc_token_info
    registration = Registration.create_from_json(request_json,
                                                 registration_class,
                                                 financing_statement,
                                                 registration_num,
                                                 account_id)
    registration.user_id = token.get('username', None)
    pay_trans_type = TransactionTypes.CHANGE.value
    fee_quantity = 1
    pay_ref = None
    if registration_class == model_utils.REG_CLASS_AMEND:
        pay_trans_type = TransactionTypes.AMENDMENT.value
        if resource_utils.no_fee_amendment(financing_statement.registration[0].registration_type):
            pay_trans_type = TransactionTypes.AMENDMENT_NO_FEE.value
    elif registration_class == model_utils.REG_CLASS_RENEWAL and registration.life == model_utils.LIFE_INFINITE:
        pay_trans_type = TransactionTypes.RENEWAL_INFINITE.value
    elif registration_class == model_utils.REG_CLASS_RENEWAL:
        fee_quantity = registration.life
        pay_trans_type = TransactionTypes.RENEWAL_LIFE_YEAR.value
    elif registration_class == model_utils.REG_CLASS_DISCHARGE:
        pay_trans_type = TransactionTypes.DISCHARGE.value
    processing_fee = None
    is_dicharge = pay_trans_type == TransactionTypes.DISCHARGE.value
    if not is_reg_staff_account(account_id):
        # if sbc staff and not 'no fee' then add processing fee
        if not is_dicharge and is_sbc_office_account(jwt.get_token_auth_header(), account_id):
            processing_fee = TransactionTypes.CHANGE_STAFF_PROCESS_FEE.value
        pay_account_id: str = account_id
        payment = Payment(jwt=jwt.get_token_auth_header(),
                          account_id=pay_account_id,
                          details=resource_utils.get_payment_details(registration))
        pay_ref = payment.create_payment(
            pay_trans_type, fee_quantity, None, registration.client_reference_id, processing_fee)
    else:
        # if not discharge add process fee
        if not is_dicharge:
            processing_fee = TransactionTypes.CHANGE_STAFF_PROCESS_FEE.value
        payment_info = resource_utils.build_staff_registration_payment(req, pay_trans_type, fee_quantity)
        payment = Payment(jwt=jwt.get_token_auth_header(),
                          account_id=None,
                          details=resource_utils.get_payment_details(registration))
        pay_ref = payment.create_payment_staff_registration(
            payment_info, registration.client_reference_id, processing_fee)
    invoice_id = pay_ref['invoiceId']
    registration.pay_invoice_id = int(invoice_id)
    registration.pay_path = pay_ref['receipt']
    # Try to save the registration: failure will rollback the payment if one was made.
    try:
        registration.save()
    except BusinessException as bus_exception:
        # just pass it along
        raise bus_exception
    except Exception as db_exception:   # noqa: B902; handle all db related errors.
        current_app.logger.error(SAVE_ERROR_MESSAGE.format(account_id, registration_class, repr(db_exception)))
        if account_id and invoice_id is not None:
            current_app.logger.info(PAY_REFUND_MESSAGE.format(account_id, registration_class, invoice_id))
            try:
                payment = Payment(jwt=jwt.get_token_auth_header(), account_id=account_id)
                payment.cancel_payment(invoice_id)
            except SBCPaymentException as cancel_exception:
                current_app.logger.error(PAY_REFUND_ERROR.format(account_id, registration_class, invoice_id,
                                                                 repr(cancel_exception)))
        raise DatabaseException(db_exception)
    return registration


def pay_and_save_financing(req: request, request_json, account_id):  # pylint: disable=too-many-locals
    """Set up the financing statement, pay if there is an account id, and save the data."""
    # Charge a fee.
    token: dict = g.jwt_oidc_token_info
    statement = FinancingStatement.create_from_json(request_json, account_id, token.get('username', None))
    invoice_id = None
    registration = statement.registration[0]
    pay_trans_type, fee_quantity = resource_utils.get_payment_type_financing(registration)
    pay_ref = None
    processing_fee = None
    is_no_fee = pay_trans_type == TransactionTypes.FINANCING_NO_FEE.value
    if not is_reg_staff_account(account_id):
        # if sbc staff and not 'no fee' then add processing fee
        if not is_no_fee and is_sbc_office_account(jwt.get_token_auth_header(), account_id):
            processing_fee = TransactionTypes.FINANCING_STAFF_PROCESS_FEE.value
        pay_account_id: str = account_id
        payment = Payment(jwt=jwt.get_token_auth_header(),
                          account_id=pay_account_id,
                          details=resource_utils.get_payment_details_financing(registration))
        pay_ref = payment.create_payment(
            pay_trans_type, fee_quantity, None, registration.client_reference_id, processing_fee)
    else:
        # if not 'no fee' then add processing fee
        if not is_no_fee:
            processing_fee = TransactionTypes.FINANCING_STAFF_PROCESS_FEE.value
        payment_info = resource_utils.build_staff_registration_payment(req, pay_trans_type, fee_quantity)
        payment = Payment(jwt=jwt.get_token_auth_header(),
                          account_id=None,
                          details=resource_utils.get_payment_details_financing(registration))
        pay_ref = payment.create_payment_staff_registration(
            payment_info, registration.client_reference_id, processing_fee)
    invoice_id = pay_ref['invoiceId']
    registration.pay_invoice_id = int(invoice_id)
    registration.pay_path = pay_ref['receipt']
    # Try to save the financing statement: failure throws an exception.
    try:
        statement.save()
    except Exception as db_exception:   # noqa: B902; handle all db related errors.
        current_app.logger.error(SAVE_ERROR_MESSAGE.format(account_id, 'financing', repr(db_exception)))
        if account_id and invoice_id is not None:
            current_app.logger.info(PAY_REFUND_MESSAGE.format(account_id, 'financing', invoice_id))
            try:
                payment.cancel_payment(invoice_id)
            except SBCPaymentException as cancel_exception:
                current_app.logger.error(PAY_REFUND_ERROR.format(account_id, 'financing', invoice_id,
                                                                 repr(cancel_exception)))
        raise DatabaseException(db_exception)
    return statement


def get_mail_verification_data(registration_id: int, registration: Registration, party: Party):
    """Generate json for a surface mail verification statement report."""
    try:
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
        return report_data
    except Exception as err:  # pylint: disable=broad-except # noqa F841;
        msg = f'Mail verification json data generation failed for id={registration_id}: ' + repr(err)
        # current_app.logger.error(msg)
        raise ReportDataException(msg)


def get_verification_report_data(registration_id: int, json_data, account_id: str, account_name: str = None):
    """Generate report data json for a surface mail verification statement report."""
    try:
        cover_data = get_report_api_payload(json_data, account_id, ReportTypes.COVER_PAGE_REPORT.value, account_name)
        verification_data = get_report_api_payload(json_data,
                                                   account_id,
                                                   ReportTypes.FINANCING_STATEMENT_REPORT.value,
                                                   account_name)
        report_data = {
            'coverLetterData': cover_data,
            'verificationData': verification_data
        }
        return report_data
    except Exception as err:  # pylint: disable=broad-except # noqa F841;
        msg = f'Mail verification report data generation failed for id={registration_id}: ' + repr(err)
        # current_app.logger.error(msg)
        raise ReportDataException(msg)


def callback_error(code: str, registration_id: int, status_code, party_id: int, message: str = None):
    """Return the event listener callback error response based on the code."""
    error: str = CALLBACK_MESSAGES[code].format(key_id=registration_id)
    if message:
        error += ' ' + message
    # Track event here.
    EventTracking.create(registration_id, EventTracking.EventTrackingTypes.SURFACE_MAIL, status_code, message)
    if status_code != HTTPStatus.BAD_REQUEST and code not in (resource_utils.CallbackExceptionCodes.MAX_RETRIES,
                                                              resource_utils.CallbackExceptionCodes.UNKNOWN_ID,
                                                              resource_utils.CallbackExceptionCodes.SETUP_ERR):
        # set up retry
        resource_utils.enqueue_verification_report(registration_id, party_id)
    return resource_utils.error_response(status_code, error)


def registration_callback_error(code: str, registration_id: int, status_code, message: str = None):
    """Return the registration report event listener callback error response based on the code."""
    error: str = CALLBACK_MESSAGES[code].format(key_id=registration_id)
    if message:
        error += ' ' + message
    # Track event here.
    EventTracking.create(registration_id, EventTracking.EventTrackingTypes.REGISTRATION_REPORT, status_code, message)
    if status_code != HTTPStatus.BAD_REQUEST and code not in (resource_utils.CallbackExceptionCodes.MAX_RETRIES,
                                                              resource_utils.CallbackExceptionCodes.UNKNOWN_ID,
                                                              resource_utils.CallbackExceptionCodes.SETUP_ERR):
        # set up retry
        resource_utils.enqueue_registration_report(registration_id, None, None)
    return resource_utils.error_response(status_code, error)


def get_registration_callback_report(registration: Registration):  # pylint: disable=too-many-return-statements
    """Attempt to generate and store a registration report. Record the status."""
    try:
        registration_id: int = registration.id
        # Check if report already generated.
        report_info: VerificationReport = registration.verification_report
        doc_name = report_info.doc_storage_url
        if doc_name is not None:
            current_app.logger.warn(f'Registration report for {registration_id} already exists: {doc_name}.')
            return {}, HTTPStatus.OK

        # Generate the report
        token = SBCPaymentClient.get_sa_token()
        current_app.logger.info(f'Generating registration report for {registration_id}.')
        raw_data, status_code, headers = get_callback_pdf(report_info.report_data,
                                                          registration.account_id,
                                                          report_info.report_type,
                                                          token,
                                                          None)
        if not raw_data or not status_code:
            return registration_callback_error(resource_utils.CallbackExceptionCodes.REPORT_DATA_ERR,
                                               registration_id,
                                               HTTPStatus.INTERNAL_SERVER_ERROR,
                                               'No data or status code.')
        current_app.logger.debug('report api call status=' + str(status_code) + ' headers=' + json.dumps(headers))
        if status_code not in (HTTPStatus.OK, HTTPStatus.CREATED):
            message = f'Status code={status_code}. Response: ' + raw_data.get_data(as_text=True)
            return registration_callback_error(resource_utils.CallbackExceptionCodes.REPORT_ERR,
                                               registration_id,
                                               HTTPStatus.INTERNAL_SERVER_ERROR,
                                               message)
        doc_name = model_utils.get_doc_storage_name(registration)
        current_app.logger.info(f'Saving registration report output to doc storage: name={doc_name}.')
        response = GoogleStorageService.save_document(doc_name, raw_data, DocumentTypes.REGISTRATION)
        current_app.logger.info('Save document storage response: ' + json.dumps(response))
        report_info.doc_storage_url = doc_name
        report_info.save()
        # Track success event.
        EventTracking.create(registration_id,
                             EventTracking.EventTrackingTypes.REGISTRATION_REPORT,
                             int(HTTPStatus.OK))
        return response, HTTPStatus.OK
    except ReportException as report_err:
        return registration_callback_error(resource_utils.CallbackExceptionCodes.REPORT_ERR,
                                           registration_id,
                                           HTTPStatus.INTERNAL_SERVER_ERROR,
                                           str(report_err))
    except ReportDataException as report_data_err:
        return registration_callback_error(resource_utils.CallbackExceptionCodes.REPORT_DATA_ERR,
                                           registration_id,
                                           HTTPStatus.INTERNAL_SERVER_ERROR,
                                           str(report_data_err))
    except StorageException as storage_err:
        return registration_callback_error(resource_utils.CallbackExceptionCodes.STORAGE_ERR,
                                           registration_id,
                                           HTTPStatus.INTERNAL_SERVER_ERROR,
                                           str(storage_err))
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, None, 'POST registration report event')
    except Exception as default_err:  # noqa: B902; return nicer default error
        return registration_callback_error(resource_utils.CallbackExceptionCodes.DEFAULT,
                                           registration_id,
                                           HTTPStatus.INTERNAL_SERVER_ERROR,
                                           str(default_err))


def get_registration_report(registration: Registration,  # pylint: disable=too-many-return-statements,too-many-locals
                            report_data: dict,
                            report_type: str,
                            token=None,
                            response_status: int = HTTPStatus.OK):
    """Generate a PDF of the provided report type using the provided data."""
    registration_id = registration.id
    try:
        report_info: VerificationReport = VerificationReport.find_by_registration_id(registration_id)
        if report_info and report_info.doc_storage_url:
            doc_name = report_info.doc_storage_url
            current_app.logger.info(f'{registration_id} fetching doc storage report {doc_name}.')
            raw_data = GoogleStorageService.get_document(doc_name, DocumentTypes.REGISTRATION)
            return raw_data, response_status, {'Content-Type': 'application/pdf'}

        if report_info and not report_info.doc_storage_url:
            current_app.logger.info(f'Pending report generation for reg id={registration_id}.')
            return report_data, HTTPStatus.ACCEPTED, {'Content-Type': 'application/json'}
        # Edge case: too large to print in real time.
        results_length = len(json.dumps(report_data))
        if results_length > current_app.config.get('MAX_SIZE_SEARCH_RT'):
            current_app.logger.info(f'Registration {registration_id} queued, size too large: {results_length}.')
            resource_utils.enqueue_registration_report(registration, report_data, report_type)
            return report_data, HTTPStatus.ACCEPTED, {'Content-Type': 'application/json'}
        # No report in doc storage: generate, store.
        raw_data, status_code, headers = get_pdf(report_data,
                                                 registration.account_id,
                                                 report_type,
                                                 token)
        current_app.logger.debug(f'Report api call status={status_code}.')
        if status_code not in (HTTPStatus.OK, HTTPStatus.CREATED):
            current_app.logger.error(f'{registration_id} report api call failed: ' + raw_data.get_data(as_text=True))
        else:
            doc_name = model_utils.get_doc_storage_name(registration)
            current_app.logger.info(f'Saving registration report output to doc storage: name={doc_name}.')
            response = GoogleStorageService.save_document(doc_name, raw_data, DocumentTypes.REGISTRATION)
            current_app.logger.info('Save document storage response: ' + json.dumps(response))
            verification_report: VerificationReport = VerificationReport(create_ts=model_utils.now_ts(),
                                                                         registration_id=registration.id,
                                                                         report_data=report_data,
                                                                         report_type=report_type,
                                                                         doc_storage_url=doc_name)
            verification_report.save()
        return raw_data, response_status, headers
    except ReportException as report_err:
        return resource_utils.service_exception_response('Report API error: ' + str(report_err))
    except ReportDataException as report_data_err:
        return resource_utils.service_exception_response('Report API data error: ' + str(report_data_err))
    except StorageException as storage_err:
        return resource_utils.service_exception_response('Report storage API error: ' + str(storage_err))
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, None, 'Generate registration report state.')
