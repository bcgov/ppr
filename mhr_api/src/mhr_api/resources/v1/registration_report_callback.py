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
"""API callback endpoint to generate and store MHR search reports after completting search step 2."""

from http import HTTPStatus

# import requests
from flask import Blueprint, current_app  # , jsonify, request
from flask_cors import cross_origin

from mhr_api.exceptions import DatabaseException
from mhr_api.services.queue_service import GoogleQueueService
from mhr_api.models import EventTracking
from mhr_api.resources import utils as resource_utils


# from mhr_api.reports import ReportTypes, get_callback_pdf
from mhr_api.services.utils.exceptions import ReportException, ReportDataException, StorageException
# from mhr_api.services.document_storage.storage_service import GoogleStorageService


bp = Blueprint('REGISTRATION_REPORT1', __name__,  # pylint: disable=invalid-name
               url_prefix='/api/v1/registration-report-callback')

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


@bp.route('/<string:registration_id>', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*')
def post_registration_report_callback(registration_id: str):
    """Resource to generate and store a registration report as a callback request."""
    try:
        current_app.logger.info(f'Registration report callback starting id={registration_id}.')
        if registration_id is None:
            return resource_utils.path_param_error_response('registration ID')
        # If exceeded max retries we're done.
        event_count: int = 0
        events = EventTracking.find_by_key_id_type(registration_id,
                                                   EventTracking.EventTrackingTypes.REGISTRATION_REPORT)
        if events:
            event_count = len(events)
        if event_count > current_app.config.get('EVENT_MAX_RETRIES'):
            return registration_callback_error(resource_utils.CallbackExceptionCodes.MAX_RETRIES,
                                               registration_id,
                                               HTTPStatus.INTERNAL_SERVER_ERROR,
                                               'Max retries reached.')

        return registration_callback_error(resource_utils.CallbackExceptionCodes.UNKNOWN_ID,
                                           registration_id,
                                           HTTPStatus.NOT_FOUND)
        # Verify the registration ID and request:
        # registration: Registration = Registration.find_by_id(registration_id)
        # if not registration:
        #    return registration_callback_error(resource_utils.CallbackExceptionCodes.UNKNOWN_ID,
        #                                       registration_id,
        #                                       HTTPStatus.NOT_FOUND)
        # if not registration.verification_report:
        #    return registration_callback_error(resource_utils.CallbackExceptionCodes.SETUP_ERR,
        #                                       registration_id,
        #                                       HTTPStatus.BAD_REQUEST,
        #                                       'No report data found for the registration.')
        # return get_registration_callback_report(registration)
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, None, 'POST registration report event')
    except Exception as default_err:  # noqa: B902; return nicer default error
        return registration_callback_error(resource_utils.CallbackExceptionCodes.DEFAULT,
                                           registration_id,
                                           HTTPStatus.INTERNAL_SERVER_ERROR,
                                           str(default_err))


def enqueue_registration_report(registration_id):
    """Add the registration verification report request to the registration queue."""
    try:
        # if json_data and report_type:
        # Signal registration report request is pending: record exists but no doc_storage_url.
        #    verification_report: VerificationReport = VerificationReport(create_ts=registration.registration_ts,
        #                                                                 registration_id=registration.id,
        #                                                                 report_data=json_data,
        #                                                                 report_type=report_type)
        #    verification_report.save()

        payload = {
            'registrationId': registration_id
        }
        apikey = current_app.config.get('SUBSCRIPTION_API_KEY')
        if apikey:
            payload['apikey'] = apikey
        GoogleQueueService().publish_registration_report(payload)
        current_app.logger.info(f'Enqueue registration report successful for id={registration_id}.')
    except DatabaseException as db_err:
        # Just log, do not return an error response.
        msg = f'Enqueue registration report db error for id={registration_id}: ' + str(db_err)
        current_app.logger.error(msg)
    except Exception as err:  # noqa: B902; do not alter app processing
        msg = f'Enqueue registration report failed for id={registration_id}: ' + str(err)
        current_app.logger.error(msg)
        EventTracking.create(registration_id,
                             EventTracking.EventTrackingTypes.REGISTRATION_REPORT,
                             int(HTTPStatus.INTERNAL_SERVER_ERROR),
                             msg)


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
        enqueue_registration_report(registration_id)
    return resource_utils.error_response(status_code, error)


def get_registration_callback_report(registration):  # pylint: disable=too-many-return-statements
    """Attempt to generate and store a registration report. Record the status."""
    registration_id: int = 0
    try:
        if registration:
            registration_id = registration.id
        # Not yet implemented.
        return registration_callback_error(resource_utils.CallbackExceptionCodes.REPORT_ERR,
                                           9999999,
                                           HTTPStatus.INTERNAL_SERVER_ERROR,
                                           'Registration report not yet implemented.')

        # Track success event.
        # EventTracking.create(registration_id,
        #                     EventTracking.EventTrackingTypes.REGISTRATION_REPORT,
        #                     int(HTTPStatus.OK))
        # return response, HTTPStatus.OK
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
