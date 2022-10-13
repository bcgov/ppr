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

from mhr_api.exceptions import DatabaseException
from mhr_api.models import EventTracking, MhrRegistration, MhrRegistrationReport
from mhr_api.models import utils as model_utils
from mhr_api.reports import get_pdf  # get_callback_pdf, get_report_api_payload
from mhr_api.resources import utils as resource_utils
from mhr_api.services.authz import is_reg_staff_account
from mhr_api.services.payment.exceptions import SBCPaymentException
from mhr_api.services.payment.payment import Payment
from mhr_api.services.queue_service import GoogleQueueService
from mhr_api.services.utils.exceptions import ReportDataException, ReportException, StorageException
from mhr_api.services.document_storage.storage_service import DocumentTypes, GoogleStorageService
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


def pay_and_save_transfer(req: request,  # pylint: disable=too-many-arguments
                          current_reg: MhrRegistration,
                          request_json,
                          account_id: str,
                          user_group: str,
                          trans_type: str,
                          trans_id: str = None):
    """Set up the registration statement, pay, and save the data."""
    # Charge a fee.
    token: dict = g.jwt_oidc_token_info
    current_app.logger.debug(f'user_group={user_group}')
    registration: MhrRegistration = MhrRegistration.create_transfer_from_json(current_reg,
                                                                              request_json,
                                                                              account_id,
                                                                              token.get('username', None),
                                                                              user_group)
    request_json['affirmByName'] = get_transfer_affirmby(token)
    invoice_id = None
    pay_ref = None
    if not is_reg_staff_account(account_id):
        payment = Payment(jwt=jwt.get_token_auth_header(),
                          account_id=account_id,
                          details=get_payment_details(registration, trans_id))
        current_app.logger.info('Creating non-staff payment')
        pay_ref = payment.create_payment(trans_type, 1, trans_id, registration.client_reference_id, False)
    else:
        payment_info = build_staff_payment(req, trans_type, 1, trans_id)
        payment = Payment(jwt=jwt.get_token_auth_header(),
                          account_id=None,
                          details=get_payment_details(registration, trans_id))
        current_app.logger.info('Creating staff payment')
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


def add_payment_json(registration, reg_json):
    """Add registration payment info json if payment exists."""
    if registration.pay_invoice_id and registration.pay_path:
        payment = {
            'invoiceId': str(registration.pay_invoice_id),
            'receipt': registration.pay_path
        }
        reg_json['payment'] = payment
    return reg_json


def enqueue_registration_report(registration: MhrRegistration, json_data: dict, report_type: str):
    """Add the registration report request to the registration queue."""
    try:
        if json_data and report_type:
            # Signal registration report request is pending: record exists but no doc_storage_url.
            reg_report: MhrRegistrationReport = MhrRegistrationReport(create_ts=registration.registration_ts,
                                                                      registration_id=registration.id,
                                                                      report_data=json_data,
                                                                      report_type=report_type)
            reg_report.save()
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
        msg = f'Enqueue MHR registration report type {report_type} db error for id={registration.id}: ' + str(db_err)
        current_app.logger.error(msg)
    except Exception as err:  # noqa: B902; do not alter app processing
        msg = f'Enqueue MHR registration report type {report_type} failed for id={registration.id}: ' + str(err)
        current_app.logger.error(msg)
        EventTracking.create(registration.id,
                             EventTracking.EventTrackingTypes.MHR_REGISTRATION_REPORT,
                             int(HTTPStatus.INTERNAL_SERVER_ERROR),
                             msg)


def get_registration_report(registration: MhrRegistration,  # pylint: disable=too-many-return-statements,too-many-locals
                            report_data: dict,
                            report_type: str,
                            token=None,
                            response_status: int = HTTPStatus.OK):
    """Generate a PDF of the provided report type using the provided data."""
    registration_id = registration.id
    try:
        report_info: MhrRegistrationReport = MhrRegistrationReport.find_by_registration_id(registration_id)
        if report_info and report_info.doc_storage_url:
            doc_name = report_info.doc_storage_url
            current_app.logger.info(f'{registration_id} fetching doc storage report {doc_name}.')
            raw_data = GoogleStorageService.get_document(doc_name, DocumentTypes.REGISTRATION)
            return raw_data, response_status, {'Content-Type': 'application/pdf'}

        if report_info and not report_info.doc_storage_url:
            # Check if report api error: more than 15 minutes has elapsed since the request was queued and no report.
            if not model_utils.report_retry_elapsed(report_info.create_ts):
                current_app.logger.info(f'Pending report generation for reg id={registration_id}.')
                return report_data, HTTPStatus.ACCEPTED, {'Content-Type': 'application/json'}

            current_app.logger.info(f'Retrying report generation for reg id={registration_id}.')
            raw_data, status_code, headers = get_pdf(report_data,
                                                     registration.account_id,
                                                     report_type,
                                                     token)
            current_app.logger.debug(f'Retry report api call status={status_code}.')
            if status_code not in (HTTPStatus.OK, HTTPStatus.CREATED):
                current_app.logger.error(f'{registration_id} retry report api call failed: ' +
                                         raw_data.get_data(as_text=True))
            else:
                doc_name = model_utils.get_doc_storage_name(registration)
                current_app.logger.info(f'Saving registration report output to doc storage: name={doc_name}.')
                response = GoogleStorageService.save_document(doc_name, raw_data, DocumentTypes.REGISTRATION)
                current_app.logger.info(f'Save document storage response: {response}')
                report_info.create_ts = model_utils.now_ts()
                report_info.doc_storage_url = doc_name
                report_info.save()
            return raw_data, response_status, headers

        # Edge case: too large to generate in real time.
        results_length = len(json.dumps(report_data))
        if results_length > current_app.config.get('MAX_SIZE_SEARCH_RT'):
            current_app.logger.info(f'Registration {registration_id} queued, size too large: {results_length}.')
            enqueue_registration_report(registration, report_data, report_type)
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
            current_app.logger.info(f'Save document storage response: {response}')
            reg_report: MhrRegistrationReport = MhrRegistrationReport(create_ts=model_utils.now_ts(),
                                                                      registration_id=registration.id,
                                                                      report_data=report_data,
                                                                      report_type=report_type,
                                                                      doc_storage_url=doc_name)
            reg_report.save()
        return raw_data, response_status, headers
    except ReportException as report_err:
        return resource_utils.service_exception_response('MHR reg report API error: ' + str(report_err))
    except ReportDataException as report_data_err:
        return resource_utils.service_exception_response('MHR reg report API data error: ' + str(report_data_err))
    except StorageException as storage_err:
        return resource_utils.service_exception_response('MHR reg report storage API error: ' + str(storage_err))
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, None, 'Generate MHR registration report state.')


def get_transfer_affirmby(token) -> str:
    """Get the transfer registration affirm by name from the user token."""
    firstname = token.get('given_name', None)
    if not firstname:
        firstname = token.get('firstname', '')
    lastname = token.get('family_name', None)
    if not lastname:
        lastname = token.get('lastname', '')
    return firstname + ' ' + lastname
