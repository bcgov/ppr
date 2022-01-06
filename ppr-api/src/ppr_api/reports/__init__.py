# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
"""Module to manage the calls and content to the reporting service."""
from http import HTTPStatus

import fitz  # noqa: I001
from flask import current_app, jsonify
from flask_babel import _

from ppr_api.exceptions import BusinessException, ResourceErrorCodes
from ppr_api.resources.utils import get_account_name

from .report import Report, ReportTypes


DEFAULT_ERROR_MSG = '{code}: Data related error generating report.'.format(code=ResourceErrorCodes.REPORT_ERR)


def get_pdf(report_data, account_id, report_type=None, token=None):
    """Generate a PDF of the provided report type using the provided data."""
    try:
        account_name = get_account_name(token, account_id)
        return Report(report_data, account_id, report_type, account_name).get_pdf()
    except FileNotFoundError:
        # We don't have a template for it, so it must only be available on paper.
        return jsonify({'message': _('No PDF report found.')}), HTTPStatus.NOT_FOUND
    except Exception as err:   # noqa: B902; return nicer default error
        current_app.logger.error(f'Generate report failed for account {account_id}, type {report_type}: ' + repr(err))
        raise BusinessException(error=DEFAULT_ERROR_MSG, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


def get_callback_pdf(report_data, account_id, report_type, token, account_name):
    """Event callback generate a PDF of the provided report type using the provided data."""
    try:
        return Report(report_data, account_id, report_type, account_name).get_pdf(token=token)
    except FileNotFoundError:
        # We don't have a template for it, so it must only be available on paper.
        return jsonify({'message': _('No PDF report found.')}), HTTPStatus.NOT_FOUND
    except Exception as err:   # noqa: B902; return nicer default error
        current_app.logger.error(f'Generate report failed for account {account_id}, type {report_type}: ' + repr(err))
        raise BusinessException(error=DEFAULT_ERROR_MSG, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


def get_verification_mail(  # pylint: disable=too-many-locals
        report_data, account_id, token, account_name, registration_id: int):
    """Event callback for verification surface mail: concatenate cover letter and verification statement."""
    try:
        event_id = str(registration_id)
        report_type = ReportTypes.COVER_PAGE_REPORT.value
        cover_output, status_code, headers = Report(report_data,
                                                    account_id,
                                                    report_type,
                                                    account_name).get_pdf(token=token)
        if status_code != HTTPStatus.OK:
            current_app.logger.error(f'Get mail cover letter report failed for id {event_id}: status=' +
                                     str(status_code))
            return cover_output, status_code, headers

        report_type = ReportTypes.FINANCING_STATEMENT_REPORT.value
        statement_output, status_code, headers = Report(report_data,
                                                        account_id,
                                                        report_type,
                                                        account_name).get_pdf(token=token)
        if status_code != HTTPStatus.OK:
            current_app.logger.error(f'Get mail verification statement report failed for id {event_id}: status=' +
                                     str(status_code))
            return cover_output, status_code, headers

        doc1 = fitz.open(stream=cover_output, filetype='pdf')
        doc2 = fitz.open(stream=statement_output, filetype='pdf')
        doc1.insert_pdf(doc2)
        final_output = doc1.convert_to_pdf()
        doc2.close()
        doc1.close()
        current_app.logger.info(f'Verification mail report generation successful for id={event_id}.')
        return final_output, HTTPStatus.OK, headers
    except FileNotFoundError:
        # We don't have a template for it, so it must only be available on paper.
        return jsonify({'message': _('No PDF report found.')}), HTTPStatus.NOT_FOUND
    except Exception as err:   # noqa: B902; return nicer default error
        msg = f'Get verification mail report failed for id {event_id}, type {report_type}: ' + repr(err)
        current_app.logger.error(msg)
        raise BusinessException(error=msg, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
