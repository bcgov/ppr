# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests to verify the V2 registration PDF report setup.

Test-Suite to ensure that the report service registration report is working as expected.
"""
from http import HTTPStatus
import json

from flask import current_app

from ppr_api.reports.v2.report import Report
from ppr_api.reports.v2.report_utils import ReportTypes


DISCHARGE_DATAFILE_COVER = 'tests/unit/reports/data/discharge-example-cover.json'
DISCHARGE_PDFFILE_COVER = 'tests/unit/reports/data/discharge-example-cover.pdf'
AMENDMENT_DATAFILE_COVER = 'tests/unit/reports/data/amendment-example-cover.json'
AMENDMENT_PDFFILE_COVER = 'tests/unit/reports/data/amendment-example-cover.pdf'

FINANCING_SA_DATAFILE = 'tests/unit/reports/data/financing-sa-example.json'
FINANCING_SA_PDFFILE = 'tests/unit/reports/data/financing-sa-example.pdf'
FINANCING_SG_DATAFILE = 'tests/unit/reports/data/financing-sg-example.json'
FINANCING_SG_PDFFILE = 'tests/unit/reports/data/financing-sg-example.pdf'
FINANCING_RL_DATAFILE = 'tests/unit/reports/data/financing-rl-example.json'
FINANCING_RL_PDFFILE = 'tests/unit/reports/data/financing-rl-example.pdf'
FINANCING_NO_CHANGE_DATAFILE = 'tests/unit/reports/data/financing-sa-no-changes-example.json'
FINANCING_NO_CHANGE_PDFFILE = 'tests/unit/reports/data/financing-sa-no-changes-example.pdf'

CHANGE_DT_DATAFILE = 'tests/unit/reports/data/change-dt-example.json'
CHANGE_DT_PDFFILE = 'tests/unit/reports/data/change-dt-example.pdf'
CHANGE_AC_DATAFILE = 'tests/unit/reports/data/change-ac-example.json'
CHANGE_AC_PDFFILE = 'tests/unit/reports/data/change-ac-example.pdf'

AMENDMENT_DATAFILE = 'tests/unit/reports/data/amendment-example.json'
AMENDMENT_PDFFILE = 'tests/unit/reports/data/amendment-example.pdf'
AMENDMENT_CO_DATAFILE = 'tests/unit/reports/data/amendment-co-example.json'
AMENDMENT_CO_PDFFILE = 'tests/unit/reports/data/amendment-co-example.pdf'

DISCHARGE_DATAFILE = 'tests/unit/reports/data/discharge-example.json'
DISCHARGE_PDFFILE = 'tests/unit/reports/data/discharge-example.pdf'
RENEWAL_DATAFILE = 'tests/unit/reports/data/renewal-example.json'
RENEWAL_PDFFILE = 'tests/unit/reports/data/renewal-example.pdf'
RENEWAL_RL_DATAFILE = 'tests/unit/reports/data/renewal-rl-example.json'
RENEWAL_RL_PDFFILE = 'tests/unit/reports/data/renewal-rl-example.pdf'
DISCHARGE_VERIFICATION_PDFFILE = 'tests/unit/reports/data/discharge-verification-mail.pdf'
AMENDMENT_VERIFICATION_PDFFILE = 'tests/unit/reports/data/amendment-verification-mail.pdf'
REPORT_VERSION_V2 = '2'


def test_financing_sa(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(FINANCING_SA_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.FINANCING_STATEMENT_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, FINANCING_SA_PDFFILE)


def test_financing_sg(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(FINANCING_SG_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.FINANCING_STATEMENT_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, FINANCING_SG_PDFFILE)


def test_financing_rl(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(FINANCING_RL_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.FINANCING_STATEMENT_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, FINANCING_RL_PDFFILE)


def test_financing_nc(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(FINANCING_NO_CHANGE_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.FINANCING_STATEMENT_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, FINANCING_NO_CHANGE_PDFFILE)


def test_change_ac(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(CHANGE_AC_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.FINANCING_STATEMENT_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, CHANGE_AC_PDFFILE)


def test_change_dt(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(CHANGE_DT_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.FINANCING_STATEMENT_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, CHANGE_DT_PDFFILE)


def test_amend_am(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(AMENDMENT_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.FINANCING_STATEMENT_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, AMENDMENT_PDFFILE)


def test_amend_co(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(AMENDMENT_CO_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.FINANCING_STATEMENT_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, AMENDMENT_CO_PDFFILE)


def test_discharge(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(DISCHARGE_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.FINANCING_STATEMENT_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, DISCHARGE_PDFFILE)


def test_renewal(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(RENEWAL_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.FINANCING_STATEMENT_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, RENEWAL_PDFFILE)


def test_renewal_rl(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(RENEWAL_RL_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.FINANCING_STATEMENT_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, RENEWAL_RL_PDFFILE)


def test_cover_discharge(session, client, jwt):
    """Assert that generation of a mail cover page report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(DISCHARGE_DATAFILE_COVER)
        report = Report(json_data, 'PS12345', ReportTypes.COVER_PAGE_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, DISCHARGE_PDFFILE_COVER)


def test_cover_amendment(session, client, jwt):
    """Assert that generation of a mail cover page report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(AMENDMENT_DATAFILE_COVER)
        report = Report(json_data, 'PS12345', ReportTypes.COVER_PAGE_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, AMENDMENT_PDFFILE_COVER)


def test_verification_discharge(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(DISCHARGE_DATAFILE_COVER)
        report = Report(json_data, 'PS12345', ReportTypes.VERIFICATION_STATEMENT_MAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, DISCHARGE_VERIFICATION_PDFFILE)


def test_verification_amendment(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(AMENDMENT_DATAFILE_COVER)
        report = Report(json_data, 'PS12345', ReportTypes.VERIFICATION_STATEMENT_MAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, AMENDMENT_VERIFICATION_PDFFILE)


def get_json_from_file(data_file: str):
    """Get json data from report data file."""
    text_data = None
    with open(data_file, 'r') as data_file:
        text_data = data_file.read()
        data_file.close()
    # print(text_data)
    json_data = json.loads(text_data)
    return json_data


def check_response(content, status_code, filename: str = None):
    """Assert that report api response is as expected."""
    assert status_code
    assert content
    if status_code != HTTPStatus.OK:
        err_content = content.decode('ascii')
        current_app.logger.warn(f'RS Status code={status_code}. Response: {err_content}.')
    elif filename:
        with open(filename, "wb") as pdf_file:
            pdf_file.write(content)
            pdf_file.close()
    current_app.logger.debug('PDF report generation completed.')


def is_report_v2() -> bool:
    return  current_app.config.get('REPORT_VERSION', '') == REPORT_VERSION_V2
