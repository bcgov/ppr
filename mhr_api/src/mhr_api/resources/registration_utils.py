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
import copy
import json
from http import HTTPStatus

from flask import request, current_app, g

from mhr_api.exceptions import DatabaseException
from mhr_api.models import EventTracking, MhrRegistration, MhrRegistrationReport, SearchResult
from mhr_api.models import utils as model_utils
from mhr_api.models.registration_utils import (
    save_admin,
    save_cancel_note,
    save_active,
    get_registration_description,
    get_document_description
)
from mhr_api.models.type_tables import MhrDocumentTypes, MhrRegistrationTypes
from mhr_api.reports import get_pdf
from mhr_api.resources import utils as resource_utils
from mhr_api.services.notify import Notify
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
EMAIL_DOWNLOAD = '\n\nTo access the file,\n\n[[{0}]]({1})'
EVENT_KEY_BATCH_MAN_REG: int = 99000000


def get_pay_details(reg_type: str, trans_id: str = None) -> dict:
    """Build pay api transaction description details."""
    label = PAY_DETAILS_LABEL
    if trans_id:
        label = PAY_DETAILS_LABEL_TRANS_ID.format(trans_id=trans_id)
    details = {
        'label': label,
        'value': get_registration_description(reg_type)
    }
    return details


def get_pay_details_doc(doc_type: str, trans_id: str = None) -> dict:
    """Build pay api transaction description details using the registration document type."""
    label = PAY_DETAILS_LABEL
    if trans_id:
        label = PAY_DETAILS_LABEL_TRANS_ID.format(trans_id=trans_id)
    details = {
        'label': label,
        'value': get_document_description(doc_type)
    }
    return details


def pay(req: request, request_json: dict, account_id: str, trans_type: str, trans_id: str = None):
    """Set up and submit a pay-api request."""
    payment: Payment = None
    pay_ref = None
    client_ref: str = request_json.get('clientReferenceId', '')
    details: dict = get_pay_details(request_json.get('registrationType'), trans_id)
    if not is_reg_staff_account(account_id):
        payment = Payment(jwt=jwt.get_token_auth_header(), account_id=account_id, details=details)
        pay_ref = payment.create_payment(trans_type, 1, trans_id, client_ref, False)
    else:
        payment_info = build_staff_payment(req, trans_type, 1, trans_id)
        payment = Payment(jwt=jwt.get_token_auth_header(), account_id=None, details=details)
        pay_ref = payment.create_payment_staff(payment_info, client_ref)
    return payment, pay_ref


def pay_staff(req: request, request_json: dict, trans_type: str, trans_id: str = None):
    """Set up and submit a staff pay-api request for note and admin registrations."""
    payment: Payment = None
    pay_ref = None
    client_ref: str = request_json.get('clientReferenceId', '')
    doc_type: str = request_json.get('documentType')
    if not doc_type:
        doc_type = request_json['note'].get('documentType')
    details: dict = get_pay_details_doc(doc_type, trans_id)
    payment_info = build_staff_payment(req, trans_type, 1, trans_id)
    payment = Payment(jwt=jwt.get_token_auth_header(), account_id=None, details=details)
    pay_ref = payment.create_payment_staff(payment_info, client_ref)
    return payment, pay_ref


def pay_and_save_registration(req: request,  # pylint: disable=too-many-arguments
                              request_json: dict,
                              account_id: str,
                              user_group: str,
                              trans_type: str,
                              trans_id: str = None):
    """Set up the registration statement, pay, and save the data."""
    # Charge a fee.
    token: dict = g.jwt_oidc_token_info
    request_json['affirmByName'] = get_affirmby(token)
    request_json['registrationType'] = MhrRegistrationTypes.MHREG
    payment, pay_ref = pay(req, request_json, account_id, trans_type, trans_id)
    invoice_id = pay_ref['invoiceId']
    # Try to save the registration: failure throws an exception.
    try:
        registration: MhrRegistration = MhrRegistration.create_new_from_json(request_json,
                                                                             account_id,
                                                                             token.get('username', None),
                                                                             user_group)
        registration.pay_invoice_id = int(invoice_id)
        registration.pay_path = pay_ref['receipt']
        registration.save()
        return registration
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
    request_json['affirmByName'] = get_affirmby(token)
    if not request_json.get('registrationType'):
        request_json['registrationType'] = MhrRegistrationTypes.TRANS
    payment, pay_ref = pay(req, request_json, account_id, trans_type, trans_id)
    invoice_id = pay_ref['invoiceId']
    # Try to save the registration: failure throws an exception.
    try:
        registration: MhrRegistration = MhrRegistration.create_transfer_from_json(current_reg,
                                                                                  request_json,
                                                                                  account_id,
                                                                                  token.get('username', None),
                                                                                  user_group)
        registration.pay_invoice_id = int(invoice_id)
        registration.pay_path = pay_ref['receipt']
        registration.save()
        if current_reg.id and current_reg.id > 0 and current_reg.owner_groups:
            current_reg.save_transfer(request_json, registration.id)
        return registration
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


def pay_and_save_exemption(req: request,  # pylint: disable=too-many-arguments
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
    request_json['affirmByName'] = get_affirmby(token)
    if request_json.get('nonResidential'):
        request_json['registrationType'] = MhrRegistrationTypes.EXEMPTION_NON_RES
    else:
        request_json['registrationType'] = MhrRegistrationTypes.EXEMPTION_RES
    payment, pay_ref = pay(req, request_json, account_id, trans_type, trans_id)
    invoice_id = pay_ref['invoiceId']
    # Try to save the registration: failure throws an exception.
    try:
        registration: MhrRegistration = MhrRegistration.create_exemption_from_json(current_reg,
                                                                                   request_json,
                                                                                   account_id,
                                                                                   token.get('username', None),
                                                                                   user_group)
        registration.pay_invoice_id = int(invoice_id)
        registration.pay_path = pay_ref['receipt']
        registration.save()
        current_reg.save_exemption()
        return registration
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


def pay_and_save_permit(req: request,  # pylint: disable=too-many-arguments
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
    request_json['affirmByName'] = get_affirmby(token)
    if not request_json.get('registrationType'):
        request_json['registrationType'] = MhrRegistrationTypes.PERMIT
    payment, pay_ref = pay(req, request_json, account_id, trans_type, trans_id)
    invoice_id = pay_ref['invoiceId']
    # Try to save the registration: failure throws an exception.
    try:
        registration: MhrRegistration = MhrRegistration.create_permit_from_json(current_reg,
                                                                                request_json,
                                                                                account_id,
                                                                                token.get('username', None),
                                                                                user_group)
        registration.pay_invoice_id = int(invoice_id)
        registration.pay_path = pay_ref['receipt']
        registration.save()
        if current_reg.id and current_reg.id > 0 and current_reg.locations:
            current_reg.save_permit(request_json, registration.id)
        return registration
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


def pay_and_save_note(req: request,  # pylint: disable=too-many-arguments
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
    request_json['affirmByName'] = get_affirmby(token)
    if not request_json.get('registrationType'):
        request_json['registrationType'] = MhrRegistrationTypes.REG_NOTE
    payment, pay_ref = pay_staff(req, request_json, trans_type, trans_id)
    invoice_id = pay_ref['invoiceId']
    # Try to save the registration: failure throws an exception.
    try:
        registration: MhrRegistration = MhrRegistration.create_note_from_json(current_reg,
                                                                              request_json,
                                                                              account_id,
                                                                              token.get('username', None),
                                                                              user_group)
        registration.pay_invoice_id = int(invoice_id)
        registration.pay_path = pay_ref['receipt']
        registration.save()
        if request_json.get('cancelDocumentId') and request_json['note'].get('documentType') == MhrDocumentTypes.NCAN:
            save_cancel_note(current_reg, request_json, registration.id)
        return registration
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


def pay_and_save_admin(req: request,  # pylint: disable=too-many-arguments
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
    request_json['affirmByName'] = get_affirmby(token)
    if not request_json.get('registrationType'):
        request_json['registrationType'] = MhrRegistrationTypes.REG_STAFF_ADMIN
    payment, pay_ref = pay_staff(req, request_json, trans_type, trans_id)
    invoice_id = pay_ref['invoiceId']
    # Try to save the registration: failure throws an exception.
    try:
        registration: MhrRegistration = MhrRegistration.create_admin_from_json(current_reg,
                                                                               request_json,
                                                                               account_id,
                                                                               token.get('username', None),
                                                                               user_group)
        registration.pay_invoice_id = int(invoice_id)
        registration.pay_path = pay_ref['receipt']
        registration.save()
        if request_json.get('cancelDocumentId') and request_json['note'].get('documentType') == MhrDocumentTypes.NCAN:
            save_cancel_note(current_reg, request_json, registration.id)
        elif request_json.get('updateDocumentId') and request_json.get('documentType') in (MhrDocumentTypes.NCAN,
                                                                                           MhrDocumentTypes.NRED,
                                                                                           MhrDocumentTypes.EXRE):
            save_cancel_note(current_reg, request_json, registration.id)
        if request_json.get('documentType') == MhrDocumentTypes.EXRE:
            save_active(current_reg)
        elif request_json.get('documentType') in (MhrDocumentTypes.REGC, MhrDocumentTypes.STAT, MhrDocumentTypes.PUBA):
            save_admin(current_reg, request_json, registration.id)
        return registration
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


def build_staff_payment(req: request, trans_type: str, quantity: int = 1, transaction_id: str = None):
    """Extract staff payment information from request parameters."""
    payment_info = {
        'transactionType': trans_type,
        'quantity': quantity,
        'waiveFees': True,
        'accountId': resource_utils.get_staff_account_id(req)
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
            reg_report.batch_report_data = get_batch_report_data(registration, json_data)
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


def get_batch_report_data(registration: MhrRegistration, json_data: dict):
    """Conditionally setup batch report data initially for NOC location registrations."""
    batch_data = None
    try:
        if registration.registration_type == MhrRegistrationTypes.PERMIT or \
                (registration.registration_type == MhrRegistrationTypes.REG_STAFF_ADMIN and json_data.get('location')):
            current_app.logger.debug(f'batch report setup PPR lien check for reg_type={registration.registration_type}')
            if json_data.get('documentType'):
                current_app.logger.debug('doc type=' + json_data.get('documentType'))
            current_app.logger.info(f'Searching PPR for MHR num {registration.mhr_number}.')
            ppr_registrations = SearchResult.search_ppr_by_mhr_number(registration.mhr_number)
            if not ppr_registrations:
                current_app.logger.debug('No PPR lien found in batch NOC location report setup.')
                return batch_data
            batch_data = copy.deepcopy(json_data)
            batch_data['nocLocation'] = True
            if json_data.get('addOwnerGroups'):
                batch_data['ownerGroups'] = json_data.get('addOwnerGroups')
                del batch_data['addOwnerGroups']
            if json_data.get('newLocation'):
                batch_data['location'] = json_data.get('newLocation')
                del batch_data['newLocation']
            batch_data['ppr'] = {
                'baseRegistrationNumber': ppr_registrations[0]['financingStatement'].get('baseRegistrationNumber'),
                'registrationDescription': ppr_registrations[0]['financingStatement'].get('registrationDescription')
            }
            secured_parties = []
            debtors = []
            for reg in ppr_registrations:
                for secured_party in reg['financingStatement'].get('securedParties'):
                    secured_parties.append(secured_party)
                for debtor in reg['financingStatement'].get('debtors'):
                    debtors.append(debtor)
            batch_data['ppr']['securedParties'] = secured_parties
            batch_data['ppr']['debtors'] = debtors
            current_app.logger.debug('batch NOC location report setup complete.')
    except Exception as err:  # noqa: B902; do not alter app processing
        msg = f'Enqueue MHR registration report batch data setup failed for id={registration.id}: ' + str(err)
        current_app.logger.error(msg)
        EventTracking.create(registration.id,
                             EventTracking.EventTrackingTypes.EMAIL_REPORT,
                             int(HTTPStatus.INTERNAL_SERVER_ERROR),
                             msg)
    return batch_data


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


def get_affirmby(token) -> str:
    """Get the registration legacy affirm by name (user name) from the user token."""
    firstname = token.get('given_name', None)
    if not firstname:
        firstname = token.get('firstname', '')
    lastname = token.get('family_name', None)
    if not lastname:
        lastname = token.get('lastname', '')
    return firstname + ' ' + lastname


def notify_man_reg_config() -> dict:
    """Build the notify configuration for a staff manufacturer registrations batch job."""
    env_var: str = current_app.config.get('NOTIFY_MAN_REG_CONFIG', None)
    if not env_var:
        return None
    return json.loads(env_var)


def email_batch_man_report_data(config: dict, report_url: str) -> dict:
    """Build email notification to reg staff with report download link."""
    body: str = config.get('body') if report_url else config.get('bodyNone')
    now_local = model_utils.today_local()
    rep_date: str = now_local.strftime('%B %-d, %Y')
    body = body.format(rep_date=rep_date)
    if report_url:
        body += EMAIL_DOWNLOAD.format(config.get('filename'), report_url)
    email_data = {
        'recipients': config.get('recipients'),
        'content': {
            'subject': config.get('subject'),
            'body': body
        }
    }
    return email_data


def email_batch_man_report_staff(report_url: str):
    """Send email notification to reg staff with batch manufacturer reg report download link."""
    config = notify_man_reg_config()
    email_data = email_batch_man_report_data(config, report_url)
    current_app.logger.debug(email_data)
    # Send email
    notify_url = config.get('url')
    notify = Notify(**{'url': notify_url})
    status_code = notify.send_email(email_data)
    message: str = f'Email sent to {notify_url}, return code: {status_code}'
    current_app.logger.info(message)
    if status_code != HTTPStatus.OK:
        EventTracking.create(EVENT_KEY_BATCH_MAN_REG,
                             EventTracking.EventTrackingTypes.MHR_REGISTRATION_REPORT,
                             status_code,
                             message)
