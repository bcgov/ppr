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

"""Tests to verify the search results PDF report setup.

Test-Suite to ensure that the report service search results report is working as expected.
"""
from http import HTTPStatus
import json

from flask import current_app

from ppr_api.reports.v2.report import Report
from ppr_api.reports.v2.report_utils import ReportTypes, merge_pdfs


SEARCH_RESULT_RG_DATAFILE = 'tests/unit/reports/data/search-detail-reg-num-example.json'
SEARCH_RESULT_RG_PDFFILE = 'tests/unit/reports/data/search-detail-reg-num-example.pdf'
SEARCH_RESULT_RG_SA_RENEW_DATAFILE = 'tests/unit/reports/data/search-detail-reg-num-sa-renew-example.json'
SEARCH_RESULT_RG_SA_RENEW_PDFFILE = 'tests/unit/reports/data/search-detail-reg-num-sa-renew-example.pdf'
SEARCH_RESULT_RG_RL_RENEW_DATAFILE = 'tests/unit/reports/data/search-detail-reg-num-rl-renew-example.json'
SEARCH_RESULT_RG_RL_RENEW_PDFFILE = 'tests/unit/reports/data/search-detail-reg-num-rl-renew-example.pdf'
SEARCH_RESULT_RG_CERTIFIED_DATAFILE = 'tests/unit/reports/data/search-detail-reg-num-certified-example.json'
SEARCH_RESULT_RG_CERTIFIED_PDFFILE = 'tests/unit/reports/data/search-detail-reg-num-certified-example.pdf'

SEARCH_RESULT_SS_DATAFILE = 'tests/unit/reports/data/search-detail-serial-num-example.json'
SEARCH_RESULT_SS_PDFFILE = 'tests/unit/reports/data/search-detail-serial-num-example.pdf'

SEARCH_RESULT_MH_DATAFILE = 'tests/unit/reports/data/search-detail-mhr-num-example.json'
SEARCH_RESULT_MH_PDFFILE = 'tests/unit/reports/data/search-detail-mhr-num-example.pdf'

SEARCH_RESULT_AC_DATAFILE = 'tests/unit/reports/data/search-detail-ac-num-example.json'
SEARCH_RESULT_AC_PDFFILE = 'tests/unit/reports/data/search-detail-ac-num-example.pdf'

SEARCH_RESULT_BS_DATAFILE = 'tests/unit/reports/data/search-detail-bus-debtor-example.json'
SEARCH_RESULT_BS_PDFFILE = 'tests/unit/reports/data/search-detail-bus-debtor-example.pdf'

SEARCH_RESULT_IS_DATAFILE = 'tests/unit/reports/data/search-detail-ind-debtor-example.json'
SEARCH_RESULT_IS_PDFFILE = 'tests/unit/reports/data/search-detail-ind-debtor-example.pdf'

SEARCH_RESULT_DISCHARGED_DATAFILE = 'tests/unit/reports/data/search-detail-discharged-example.json'
SEARCH_RESULT_DISCHARGED_PDFFILE = 'tests/unit/reports/data/search-detail-discharged-example.pdf'

SEARCH_RESULT_RENEWED_DATAFILE = 'tests/unit/reports/data/search-detail-renewed-example.json'
SEARCH_RESULT_RENEWED_PDFFILE = 'tests/unit/reports/data/search-detail-renewed-example.pdf'

SEARCH_RESULT_NIL_DATAFILE = 'tests/unit/reports/data/search-detail-no-results-example.json'
SEARCH_RESULT_NIL_PDFFILE = 'tests/unit/reports/data/search-detail-no-results-example.pdf'

SEARCH_RESULT_75_DATAFILE = 'tests/unit/reports/data/search-detail-75-example.json'
SEARCH_RESULT_75_PDFFILE = 'tests/unit/reports/data/search-detail-75-example.pdf'
SEARCH_COVER_DATAFILE = 'tests/unit/reports/data/search-cover-example.json'
SEARCH_COVER_PDFFILE = 'tests/unit/reports/data/search-cover-example.pdf'
REPORT_VERSION_V2 = '2'
MERGE_PDFFILE = 'tests/unit/reports/data/search-merge.pdf'


def test_merge(session, client, jwt):
    """Assert that merging pdf's in memory works."""
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(SEARCH_COVER_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_COVER_REPORT, 'Account Name')
        # test
        content1, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content1, status, SEARCH_COVER_PDFFILE)

        json_data = get_json_from_file(SEARCH_RESULT_RG_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content2, status, headers = report.get_pdf()
        check_response(content2, status, SEARCH_RESULT_RG_PDFFILE)
        report_files = {
            'cover.pdf': content1,
            'pdf1.pdf': content2
        }
        merge_content = merge_pdfs(report_files)
        with open(MERGE_PDFFILE, "wb") as pdf_file:
            pdf_file.write(merge_content)
            pdf_file.close()



def test_search_rg(session, client, jwt):
    """Assert that setup for a reg number search type result report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(SEARCH_RESULT_RG_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_RG_PDFFILE)


def test_search_rg_sa(session, client, jwt):
    """Assert that setup for a reg number search type result report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(SEARCH_RESULT_RG_SA_RENEW_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_RG_SA_RENEW_PDFFILE)


def test_search_rg_rl(session, client, jwt):
    """Assert that setup for a reg number search type result report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(SEARCH_RESULT_RG_RL_RENEW_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_RG_RL_RENEW_PDFFILE)


def test_search_rg_cert(session, client, jwt):
    """Assert that setup for a reg number search type result report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(SEARCH_RESULT_RG_CERTIFIED_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_RG_CERTIFIED_PDFFILE)


def test_search_result_ss(session, client, jwt):
    """Assert that setup for a serial number search type result report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(SEARCH_RESULT_SS_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, '')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_SS_PDFFILE)


def test_search_result_mh(session, client, jwt):
    """Assert that setup for a mhr number search type result report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(SEARCH_RESULT_MH_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_MH_PDFFILE)


def test_search_result_ac(session, client, jwt):
    """Assert that setup for an aircraft search type result report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(SEARCH_RESULT_AC_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_AC_PDFFILE)


def test_search_result_bs(session, client, jwt):
    """Assert that setup for a business debtor search type result report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(SEARCH_RESULT_BS_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, '')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_BS_PDFFILE)


def test_search_result_is(session, client, jwt):
    """Assert that setup for an individual debtor search type result report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(SEARCH_RESULT_IS_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_IS_PDFFILE)


def test_search_result_discharged(session, client, jwt):
    """Assert that setup for a search result report with a a discharge is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(SEARCH_RESULT_DISCHARGED_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_DISCHARGED_PDFFILE)


def test_search_result_renewed(session, client, jwt):
    """Assert that setup for a search result report with a renewal is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(SEARCH_RESULT_RENEWED_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_RENEWED_PDFFILE)


def test_search_result_nil(session, client, jwt):
    """Assert that setup for a nil result report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(SEARCH_RESULT_NIL_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_NIL_PDFFILE)


def test_search_result_75(session, client, jwt):
    """Assert that setup for a search result report with 75 registrations is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(SEARCH_RESULT_75_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_75_PDFFILE)


def test_search_cover(session, client, jwt):
    """Assert that setup for a large search result cover summary report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(SEARCH_COVER_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_COVER_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_COVER_PDFFILE)


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


def is_ci_testing() -> bool:
    """Check unit test environment: exclude most reports for CI testing."""
    return  current_app.config.get("DEPLOYMENT_ENV", "testing") == "testing"
