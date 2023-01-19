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

from mhr_api.reports.v2.report import Report
from mhr_api.reports.v2.report_utils import ReportTypes


SEARCH_RESULT_NOTES_DATAFILE = 'tests/unit/reports/data/search-detail-notes-example.json'
SEARCH_RESULT_NOTES_PDFFILE = 'tests/unit/reports/data/search-detail-notes-example.pdf'
SEARCH_RESULT_MHR_DATAFILE = 'tests/unit/reports/data/search-detail-mhr-example.json'
SEARCH_RESULT_SERIAL_DATAFILE = 'tests/unit/reports/data/search-detail-serial-example.json'
SEARCH_RESULT_OWNER_DATAFILE = 'tests/unit/reports/data/search-detail-owner-example.json'
SEARCH_RESULT_ORG_DATAFILE = 'tests/unit/reports/data/search-detail-org-example.json'
SEARCH_RESULT_COMBO_DATAFILE = 'tests/unit/reports/data/search-detail-combo-example.json'
SEARCH_RESULT_COMBO_NIL_DATAFILE = 'tests/unit/reports/data/search-detail-combo-nil-example.json'
SEARCH_RESULT_COMBO_HDC_DATAFILE = 'tests/unit/reports/data/search-detail-combo-discharged-example.json'
SEARCH_RESULT_COMBO_HEX_DATAFILE = 'tests/unit/reports/data/search-detail-combo-expired-example.json'
SEARCH_RESULT_MHR_PDFFILE = 'tests/unit/reports/data/search-detail-mhr-example.pdf'
SEARCH_RESULT_SERIAL_PDFFILE = 'tests/unit/reports/data/search-detail-serial-example.pdf'
SEARCH_RESULT_OWNER_PDFFILE = 'tests/unit/reports/data/search-detail-owner-example.pdf'
SEARCH_RESULT_ORG_PDFFILE = 'tests/unit/reports/data/search-detail-org-example.pdf'
SEARCH_RESULT_COMBO_PDFFILE = 'tests/unit/reports/data/search-detail-combo-example.pdf'
SEARCH_RESULT_COMBO_NIL_PDFFILE = 'tests/unit/reports/data/search-detail-combo-nil-example.pdf'
SEARCH_RESULT_COMBO_HDC_PDFFILE = 'tests/unit/reports/data/search-detail-combo-discharged-example.pdf'
SEARCH_RESULT_COMBO_HEX_PDFFILE = 'tests/unit/reports/data/search-detail-combo-expired-example.pdf'
SEARCH_RESULT_NIL_DATAFILE = 'tests/unit/reports/data/search-detail-no-results-example.json'
SEARCH_RESULT_NIL_PDFFILE = 'tests/unit/reports/data/search-detail-no-results-example.pdf'
SEARCH_RESULT_TEST_DATAFILE = 'tests/unit/reports/data/search-test-example.json'
SEARCH_RESULT_TEST_PDFFILE = 'tests/unit/reports/data/search-test-example.pdf'
SEARCH_RESULT_EXECUTOR_DATAFILE = 'tests/unit/reports/data/search-detail-executor-example.json'
SEARCH_RESULT_EXECUTOR_PDFFILE = 'tests/unit/reports/data/search-detail-executor-example.pdf'
SEARCH_LOC_DEALER_DATAFILE = 'tests/unit/reports/data/search-location-dealer-example.json'
SEARCH_LOC_DEALER_PDFFILE = 'tests/unit/reports/data/search-location-dealer-example.pdf'
SEARCH_LOC_PARK_DATAFILE = 'tests/unit/reports/data/search-location-park-example.json'
SEARCH_LOC_PARK_PDFFILE = 'tests/unit/reports/data/search-location-park-example.pdf'
SEARCH_LOC_PID_DATAFILE = 'tests/unit/reports/data/search-location-pid-example.json'
SEARCH_LOC_PID_PDFFILE = 'tests/unit/reports/data/search-location-pid-example.pdf'
SEARCH_LOC_RESERVE_DATAFILE = 'tests/unit/reports/data/search-location-reserve-example.json'
SEARCH_LOC_RESERVE_PDFFILE = 'tests/unit/reports/data/search-location-reserve-example.pdf'
SEARCH_LOC_NOPID_DATAFILE = 'tests/unit/reports/data/search-location-no-pid-example.json'
SEARCH_LOC_NOPID_PDFFILE = 'tests/unit/reports/data/search-location-no-pid-example.pdf'

REPORT_VERSION_V2 = '2'


def test_search_loc_dealer_test(session, client, jwt):
    """Assert that setup for a test result report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(SEARCH_LOC_DEALER_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_LOC_DEALER_PDFFILE)


def test_search_loc_park_test(session, client, jwt):
    """Assert that setup for a test result report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(SEARCH_LOC_PARK_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_LOC_PARK_PDFFILE)


def test_search_loc_pid_test(session, client, jwt):
    """Assert that setup for a test result report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(SEARCH_LOC_PID_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_LOC_PID_PDFFILE)


def test_search_loc_reserve_test(session, client, jwt):
    """Assert that setup for a test result report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(SEARCH_LOC_RESERVE_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_LOC_RESERVE_PDFFILE)


def test_search_loc_nopid_test(session, client, jwt):
    """Assert that setup for a test result report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(SEARCH_LOC_NOPID_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_LOC_NOPID_PDFFILE)


def test_search_result_test(session, client, jwt):
    """Assert that setup for a test result report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(SEARCH_RESULT_TEST_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_TEST_PDFFILE)


def test_search_result_executor(session, client, jwt):
    """Assert that setup for a test result report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(SEARCH_RESULT_EXECUTOR_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_EXECUTOR_PDFFILE)


def test_search_result_mhr(session, client, jwt):
    """Assert that setup for an mhr number search type result report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(SEARCH_RESULT_MHR_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_MHR_PDFFILE)


def test_search_result_serial(session, client, jwt):
    """Assert that setup for an mhr serial number search type result report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(SEARCH_RESULT_SERIAL_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_SERIAL_PDFFILE)


def test_search_result_owner(session, client, jwt):
    """Assert that setup for an mhr owner name search type result report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(SEARCH_RESULT_OWNER_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_OWNER_PDFFILE)


def test_search_result_org(session, client, jwt):
    """Assert that setup for an mhr orgainization name search type result report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(SEARCH_RESULT_ORG_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_ORG_PDFFILE)


def test_search_result_combo(session, client, jwt):
    """Assert that setup for an mhr-ppr combo mhr number search type result report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(SEARCH_RESULT_COMBO_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_COMBO_PDFFILE)


def test_search_result_combo_nil(session, client, jwt):
    """Assert that setup for an mhr-ppr combo mhr number search type nil result report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(SEARCH_RESULT_COMBO_NIL_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_COMBO_NIL_PDFFILE)


def test_search_result_combo_discharged(session, client, jwt):
    """Assert that setup for an mhr-ppr combo mhr number search type discharged result report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(SEARCH_RESULT_COMBO_HDC_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_COMBO_HDC_PDFFILE)


def test_search_result_combo_expired(session, client, jwt):
    """Assert that setup for an mhr-ppr combo mhr number search type expired result report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(SEARCH_RESULT_COMBO_HEX_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_COMBO_HEX_PDFFILE)


def test_search_result_nil(session, client, jwt):
    """Assert that setup for a nil result report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(SEARCH_RESULT_NIL_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_NIL_PDFFILE)


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


def test_search_result_notes(session, client, jwt):
    """Assert that setup for an search result report with unit notes is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(SEARCH_RESULT_NOTES_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, SEARCH_RESULT_NOTES_PDFFILE)
