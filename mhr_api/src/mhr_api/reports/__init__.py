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

from mhr_api.exceptions import BusinessException, ResourceErrorCodes
from mhr_api.resources.utils import get_account_name

from .report import Report
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
        current_app.logger.error(f'Generate report failed for account {account_id}, type {report_type}: ' + str(err))
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
        current_app.logger.error(f'Generate report failed for account {account_id}, type {report_type}: ' + str(err))
        raise BusinessException(error=DEFAULT_ERROR_MSG, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


def get_report_api_payload(report_data, account_id, report_type, account_name):
    """Get the report api payload data without calling the service."""
    try:
        if current_app.config.get('REPORT_VERSION', REPORT_VERSION_V2) == REPORT_VERSION_V2:
            return ReportV2(report_data, account_id, report_type, account_name).get_payload_data()
        return Report(report_data, account_id, report_type, account_name).get_payload_data()
    except Exception as err:   # noqa: B902; return nicer default error
        current_app.logger.error(f'Get report payload data failed for account {account_id}, type {report_type}: ' +
                                 str(err))
        raise BusinessException(error=DEFAULT_ERROR_MSG, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
