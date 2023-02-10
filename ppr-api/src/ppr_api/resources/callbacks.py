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
"""API endpoints for maintaining processing aysnchronous callback. Initially mail verification reports."""
import json
from http import HTTPStatus

from flask import request, current_app, jsonify
from flask_restx import Namespace, Resource, cors

from ppr_api.exceptions import DatabaseException
from ppr_api.models import MailReport
from ppr_api.models import utils as model_utils
from ppr_api.resources import utils as resource_utils
from ppr_api.utils.util import cors_preflight
from ppr_api.reports import get_callback_pdf
from ppr_api.reports.v2.report_utils import ReportTypes
from ppr_api.callback.utils.exceptions import ReportDataException, ReportException, StorageException
from ppr_api.callback.document_storage.storage_service import DocumentTypes, GoogleStorageService


API = Namespace('callbacks', description='Endpoints for processing aysnchronous callback requests.')
START_TS_PARAM = 'startDateTime'
END_TS_PARAM = 'endDateTime'


@cors_preflight('GET,POST,OPTIONS')
@API.route('/mail-report', methods=['GET', 'POST', 'OPTIONS'])
class MailReportResource(Resource):
    """Resource to handle a verification report mail requests for a callback events."""

    @staticmethod
    @cors.crossdomain(origin='*')
    def post():
        """Registration id and party id are in the payload."""
        request_json = request.get_json(silent=True)
        registration_id: int = request_json.get('registrationId', -1)
        party_id: int = request_json.get('partyId', -1)
        try:
            # Authenticate with request api key
            if not resource_utils.valid_api_key(request):
                return resource_utils.unauthorized_error_response('Verification report callback')

            message: str = None
            status = HTTPStatus.BAD_REQUEST
            if registration_id < 0:
                message = 'Mail verification statement no registration ID.'
            elif party_id < 0:
                message = 'Mail verification statement no party ID.'
            else:
                # If no mail report record we're done.
                mail_report: MailReport = MailReport.find_by_registration_party_id(registration_id, party_id)
                if not mail_report:
                    message = 'No mail report data found for the registration id, party id.'
                    status = HTTPStatus.NOT_FOUND

            if message:
                return resource_utils.error_response(status, message)

            if mail_report.doc_storage_url:
                current_app.logger.debug('Report {mail_report.doc_storage_url} already exists.')
                return {}, HTTPStatus.OK, {'Content-Type': 'application/json'}
            # Generate the report, upload it to cloud storage, update the status.
            return generate_mail_callback_report(mail_report)
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception,
                                                        None,
                                                        'POST callback mail verification report DB error.')
        except Exception as default_err:  # noqa: B902; return nicer default error
            return mail_callback_error(mail_report,
                                       HTTPStatus.INTERNAL_SERVER_ERROR,
                                       'Callback default error: ' + str(default_err))

    @staticmethod
    @cors.crossdomain(origin='*')
    def get():
        """Fetch recent event storage names by request parameter startDateTime and optional endDateTime."""
        start_ts = request.args.get(START_TS_PARAM, None)
        end_ts = request.args.get(END_TS_PARAM, None)
        try:
            # Authenticate with request api key
            if not resource_utils.valid_api_key(request):
                return resource_utils.unauthorized_error_response('Verification report callback')

            message: str = None
            status = HTTPStatus.BAD_REQUEST
            start = None
            end = None
            if not start_ts:
                message = 'Request parameter startDateTime is required.'
            else:
                try:
                    start = model_utils.ts_from_iso_format(start_ts)
                except Exception:
                    message = 'Request parameter startDateTime value is invalid'
            if end_ts:
                try:
                    end = model_utils.ts_from_iso_format(end_ts)
                except Exception:
                    message = 'Request parameter endDateTime value is invalid'
            if end and start and end <= start:
                message = 'Request timestamp range is invalid'

            if message:
                return resource_utils.error_response(status, message)
            results = MailReport.find_list_by_timestamp(start, end)
            return jsonify(results), HTTPStatus.OK
        except DatabaseException as db_exception:
            return resource_utils.db_exception_response(db_exception,
                                                        None,
                                                        'GET callback mail reports list DB error.')
        except Exception as default_err:  # noqa: B902; return nicer default error
            return resource_utils.default_exception_response(default_err)


def mail_callback_error(mail_report: MailReport, status_code: int = 500, message: str = None):
    """Update the status and return an error response."""
    current_app.logger.error(message)
    if mail_report:
        try:
            mail_report.update_retry_count(status_code, message)
            mail_report.save()
            # if mail_report.retry_count < current_app.config.get('EVENT_MAX_RETRIES'):
            #    resource_utils.enqueue_verification_report(mail_report.registration_id, mail_report.party_id)
        except Exception as default_err:  # noqa: B902; return nicer default error
            current_app.logger.error('Attempt to setup callback retry failed: ' + str(default_err))
    return resource_utils.error_response(status_code, message)


def generate_mail_callback_report(mail_report: MailReport):  # pylint: disable=too-many-return-statements
    """Attempt to generate and store a mail report. Record the status."""
    try:
        current_app.logger.info(f'Generating mail report for mail report id={mail_report.id}.')
        raw_data, status_code, headers = get_callback_pdf(mail_report.report_data,
                                                          None,
                                                          ReportTypes.VERIFICATION_STATEMENT_MAIL_REPORT,
                                                          None,
                                                          None)
        if not raw_data or not status_code:
            return mail_callback_error(mail_report,
                                       HTTPStatus.INTERNAL_SERVER_ERROR,
                                       'Callback report generation no data or status code.')
        current_app.logger.debug('report api call status=' + str(status_code) + ' headers=' + json.dumps(headers))
        if status_code not in (HTTPStatus.OK, HTTPStatus.CREATED):
            message = f'Status code={status_code}. Response: ' + raw_data.get_data(as_text=True)
            return mail_callback_error(mail_report,
                                       HTTPStatus.INTERNAL_SERVER_ERROR,
                                       message)
        doc_name = model_utils.get_mail_doc_storage_name(mail_report.create_ts,
                                                         mail_report.registration_id,
                                                         mail_report.party_id)
        current_app.logger.info(f'Saving mail report output to doc storage: name={doc_name}.')
        response = GoogleStorageService.save_document(doc_name, raw_data, DocumentTypes.MAIL_DEFAULT)
        current_app.logger.info('Save document storage response: ' + json.dumps(response))
        mail_report.update_storage_url(doc_name, HTTPStatus.OK)
        mail_report.save()
        return {}, HTTPStatus.OK, {'Content-Type': 'application/json'}
    except ReportException as report_err:
        return mail_callback_error(mail_report,
                                   HTTPStatus.INTERNAL_SERVER_ERROR,
                                   'Callback report generation error: ' + str(report_err))
    except ReportDataException as report_data_err:
        return mail_callback_error(mail_report,
                                   HTTPStatus.INTERNAL_SERVER_ERROR,
                                   'Callback report data error: ' + str(report_data_err))
    except StorageException as storage_err:
        return mail_callback_error(mail_report,
                                   HTTPStatus.INTERNAL_SERVER_ERROR,
                                   'Callback report cloud storage error: ' + str(storage_err))
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception,
                                                    None,
                                                    'POST callback mail verification report DB error.')
    except Exception as default_err:  # noqa: B902; return nicer default error
        return mail_callback_error(mail_report,
                                   HTTPStatus.INTERNAL_SERVER_ERROR,
                                   'Callback default error: ' + str(default_err))
