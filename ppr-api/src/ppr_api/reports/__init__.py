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

from flask import current_app, jsonify
from flask_babel import _

from ppr_api.exceptions import BusinessException, ResourceErrorCodes
from ppr_api.resources.utils import get_account_name

from .report import Report, ReportTypes
from .v2.report import Report as ReportV2


REPORT_VERSION_V2 = '2'
DEFAULT_ERROR_MSG = '{code}: Data related error generating report.'.format(code=ResourceErrorCodes.REPORT_ERR)


def get_pdf(report_data, account_id, report_type=None, token=None):
    """Generate a PDF of the provided report type using the provided data."""
    try:
        account_name = get_account_name(token, account_id)
        if current_app.config.get('REPORT_VERSION', REPORT_VERSION_V2) == REPORT_VERSION_V2:
            return ReportV2(report_data, account_id, report_type, account_name).get_pdf()
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
        if current_app.config.get('REPORT_VERSION', REPORT_VERSION_V2) == REPORT_VERSION_V2:
            return ReportV2(report_data, account_id, report_type, account_name).get_pdf()
        return Report(report_data, account_id, report_type, account_name).get_pdf(token=token)
    except FileNotFoundError:
        # We don't have a template for it, so it must only be available on paper.
        return jsonify({'message': _('No PDF report found.')}), HTTPStatus.NOT_FOUND
    except Exception as err:   # noqa: B902; return nicer default error
        current_app.logger.error(f'Generate report failed for account {account_id}, type {report_type}: ' + repr(err))
        raise BusinessException(error=DEFAULT_ERROR_MSG, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


def get_report_api_payload(report_data, account_id, report_type, account_name):
    """Get the report api payload data without calling the service."""
    try:
        # Used by separate surface mail (BCMail+) service. Coordinate update with that service.
        # if current_app.config.get('REPORT_VERSION', REPORT_VERSION_V2) == REPORT_VERSION_V2:
        #    return ReportV2(report_data, account_id, report_type, account_name).get_payload_data()
        return Report(report_data, account_id, report_type, account_name).get_payload_data()
    except Exception as err:   # noqa: B902; return nicer default error
        current_app.logger.error(f'Get report payload data failed for account {account_id}, type {report_type}: ' +
                                 repr(err))
        raise BusinessException(error=DEFAULT_ERROR_MSG, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


def get_verification_mail(  # pylint: disable=too-many-locals
        report_data, account_id, token, account_name, registration_id: int):  # pylint: disable=unused-argument
    """Event callback for verification surface mail: concatenate cover letter and verification statement."""
    try:
        current_app.logger.info(f'Not implemented: account id={account_id}, name={account_name}')
        current_app.logger.info(f'Not implemented: reg id={registration_id}')
        if report_data:
            current_app.logger.info(f'report data length={len(report_data)}')
        if token:
            current_app.logger.info(f'token length={len(token)}')
        raise NotImplementedError('Not implemented yet.')
    except NotImplementedError as err:
        msg = f'Get verification mail report failed for registration id {registration_id}'
        current_app.logger.error(msg)
        raise BusinessException(error=msg, status_code=HTTPStatus.INTERNAL_SERVER_ERROR) from err
