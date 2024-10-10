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
import copy
import json

from flask import current_app

from mhr_api.reports.v2.report import Report
from mhr_api.reports.v2.report_utils import ReportTypes


REGISTRATON_TEST_DATAFILE = 'tests/unit/reports/data/registration-test-example.json'
REGISTRATON_TEST_PDFFILE = 'tests/unit/reports/data/registration-test-example.pdf'
REGISTRATON_SOLE_DATAFILE = 'tests/unit/reports/data/registration-sole-example.json'
REGISTRATON_SOLE_PDFFILE = 'tests/unit/reports/data/registration-sole-example.pdf'
REGISTRATON_COMMON_DATAFILE = 'tests/unit/reports/data/registration-common-example.json'
REGISTRATON_COMMON_PDFFILE = 'tests/unit/reports/data/registration-common-example.pdf'
REGISTRATON_JOINT_DATAFILE = 'tests/unit/reports/data/registration-joint-example.json'
REGISTRATON_JOINT_PDFFILE = 'tests/unit/reports/data/registration-joint-example.pdf'
REGISTRATON_MAIL_PDFFILE = 'tests/unit/reports/data/registration-mail-example.pdf'
REGISTRATON_COVER_PDFFILE = 'tests/unit/reports/data/registration-cover-example.pdf'
REGISTRATON_STAFF_PDFFILE = 'tests/unit/reports/data/registration-staff-example.pdf'
REGISTRATON_BATCH_PDFFILE = 'tests/unit/reports/data/registration-batch-example.pdf'

TRANSFER_TEST_SO_DATAFILE = 'tests/unit/reports/data/trans-test-example.json'
TRANSFER_TEST_SO_PDFFILE = 'tests/unit/reports/data/trans-test-example-so.pdf'
TRANSFER_TEST_JT_DATAFILE = 'tests/unit/reports/data/trans-test-example-jt.json'
TRANSFER_TEST_JT_PDFFILE = 'tests/unit/reports/data/trans-test-example-jt.pdf'
TRANSFER_TEST_TC_DATAFILE = 'tests/unit/reports/data/trans-test-example-tc.json'
TRANSFER_TEST_TC_PDFFILE = 'tests/unit/reports/data/trans-test-example-tc.pdf'
TRANSFER_TEST_DEATH_DATAFILE = 'tests/unit/reports/data/trans-test-example-death.json'
TRANSFER_TEST_DEATH_PDFFILE = 'tests/unit/reports/data/trans-test-example-death.pdf'
TRANSFER_TEST_WILL_DATAFILE = 'tests/unit/reports/data/trans-test-example-will.json'
TRANSFER_TEST_WILL_PDFFILE = 'tests/unit/reports/data/trans-test-example-will.pdf'
TRANSFER_TEST_AFFIDAVIT_DATAFILE = 'tests/unit/reports/data/trans-test-example-affidavit.json'
TRANSFER_TEST_AFFIDAVIT_PDFFILE = 'tests/unit/reports/data/trans-test-example-affidavit.pdf'
TRANSFER_TEST_ADMIN_DATAFILE = 'tests/unit/reports/data/trans-test-example-admin.json'
TRANSFER_TEST_ADMIN_PDFFILE = 'tests/unit/reports/data/trans-test-example-admin.pdf'

EXEMPTION_TEST_RES_DATAFILE = 'tests/unit/reports/data/exempt-res-test-example.json'
EXEMPTION_TEST_RES_PDFFILE = 'tests/unit/reports/data/exempt-res-test-example.pdf'

PERMIT_TEST_DATAFILE = 'tests/unit/reports/data/permit-test-example.json'
PERMIT_TEST_PDFFILE = 'tests/unit/reports/data/permit-test-example.pdf'

NOTE_TEST_DATAFILE = 'tests/unit/reports/data/note-test-example.json'
NOTE_TEST_PDFFILE = 'tests/unit/reports/data/note-test-example.pdf'
ADMIN_TEST_DATAFILE = 'tests/unit/reports/data/admin-registration-example.json'
ADMIN_TEST_PDFFILE = 'tests/unit/reports/data/admin-registration-example.pdf'
NOC_LOCATION_TEST_DATAFILE = 'tests/unit/reports/data/noc-location-example.json'
NOC_LOCATION_TEST_PDFFILE = 'tests/unit/reports/data/noc-location-example.pdf'

REPORT_VERSION_V2 = '2'


def test_transport_permit(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(PERMIT_TEST_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.MHR_TRANSPORT_PERMIT, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, PERMIT_TEST_PDFFILE)


def test_transfer_trans_so(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(TRANSFER_TEST_SO_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.MHR_TRANSFER, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, TRANSFER_TEST_SO_PDFFILE)


def test_transfer_trans_jt(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(TRANSFER_TEST_JT_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.MHR_TRANSFER, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, TRANSFER_TEST_JT_PDFFILE)


def test_transfer_trans_tc(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(TRANSFER_TEST_TC_DATAFILE)
        report = Report(json_data, 'ppr_staff', ReportTypes.MHR_TRANSFER, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, TRANSFER_TEST_TC_PDFFILE)


def test_transfer_death(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(TRANSFER_TEST_DEATH_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.MHR_TRANSFER, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, TRANSFER_TEST_DEATH_PDFFILE)


def test_transfer_will(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(TRANSFER_TEST_WILL_DATAFILE)
        report = Report(json_data, 'ppr_staff', ReportTypes.MHR_TRANSFER, '')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, TRANSFER_TEST_WILL_PDFFILE)


def test_transfer_admin(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(TRANSFER_TEST_ADMIN_DATAFILE)
        report = Report(json_data, 'ppr_staff', ReportTypes.MHR_TRANSFER, '')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, TRANSFER_TEST_ADMIN_PDFFILE)


def test_transfer_affidavit(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(TRANSFER_TEST_AFFIDAVIT_DATAFILE)
        report = Report(json_data, 'ppr_staff', ReportTypes.MHR_TRANSFER, '')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, TRANSFER_TEST_AFFIDAVIT_PDFFILE)


def test_registration_test(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2():
        json_data = get_json_from_file(REGISTRATON_TEST_DATAFILE)
        report = Report(json_data, '2617', ReportTypes.MHR_REGISTRATION, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, REGISTRATON_TEST_PDFFILE)


def test_registration_sole(session, client, jwt):
    """Assert that generation of a sole owner report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(REGISTRATON_SOLE_DATAFILE)
        report = Report(json_data, 'ppr_staff', ReportTypes.MHR_REGISTRATION, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, REGISTRATON_SOLE_PDFFILE)


def test_registration_common(session, client, jwt):
    """Assert that generation of a tenants in common owner report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(REGISTRATON_COMMON_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.MHR_REGISTRATION, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, REGISTRATON_COMMON_PDFFILE)


def test_registration_joint(session, client, jwt):
    """Assert that generation of an owner joint tenants type report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(REGISTRATON_JOINT_DATAFILE)
        report = Report(json_data, 'PS12345', ReportTypes.MHR_REGISTRATION, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, REGISTRATON_JOINT_PDFFILE)


def test_cover_registration(session, client, jwt):
    """Assert that generation of a mail cover page report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(REGISTRATON_TEST_DATAFILE)
        report = Report(json_data, 'ppr_staff', ReportTypes.MHR_REGISTRATION_COVER, 'Account Name')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, REGISTRATON_COVER_PDFFILE)


def test_staff_registration(session, client, jwt):
    """Assert that generation of a staff registration report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(PERMIT_TEST_DATAFILE)
#        json_data = get_json_from_file(TRANSFER_TEST_SO_DATAFILE)
#        json_data = get_json_from_file(REGISTRATON_TEST_DATAFILE)
#        json_data = get_json_from_file(REGISTRATON_SOLE_DATAFILE)
#        json_data = get_json_from_file(REGISTRATON_COMMON_DATAFILE)
#        json_data = get_json_from_file(NOTE_TEST_DATAFILE)
#        json_data = get_json_from_file(ADMIN_TEST_DATAFILE)
#        json_data = get_json_from_file(EXEMPTION_TEST_RES_DATAFILE)
#        json_data = get_json_from_file(TRANSFER_TEST_DEATH_DATAFILE)
#        json_data = get_json_from_file(TRANSFER_TEST_TC_DATAFILE)

        report = Report(json_data, 'ppr_staff', ReportTypes.MHR_REGISTRATION_STAFF, '')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, REGISTRATON_STAFF_PDFFILE)


def test_noc_location(session, client, jwt):
    """Assert that generation of a  NOC location registration report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(NOC_LOCATION_TEST_DATAFILE)
        report = Report(json_data, 'ppr_staff', ReportTypes.MHR_REGISTRATION_STAFF, '')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, NOC_LOCATION_TEST_PDFFILE)


def test_batch_merge(session, client, jwt):
    """Assert that generation of a batch merge of registration reports is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        reports = []
        json_data = get_json_from_file(REGISTRATON_TEST_DATAFILE)
        create_ts = json_data.get('createDateTime')
        report = Report(json_data, '2523', ReportTypes.MHR_REGISTRATION_COVER, 'Account Name')
        content, status, headers = report.get_pdf()
        reports.append(content)
        json_data['createDateTime'] = create_ts
        report = Report(json_data, '2523', ReportTypes.MHR_REGISTRATION, 'Account Name')
        content, status, headers = report.get_pdf()
        reports.append(content)
        # test
        content, status, headers = Report.batch_merge(reports)
        assert headers
        # verify
        check_response(content, status, REGISTRATON_BATCH_PDFFILE)


def test_exemption_res(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(EXEMPTION_TEST_RES_DATAFILE)
        report = Report(json_data, '3026', ReportTypes.MHR_EXEMPTION, '')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, EXEMPTION_TEST_RES_PDFFILE)


def test_unit_note(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(NOTE_TEST_DATAFILE)
        report = Report(json_data, 'ppr_staff', ReportTypes.MHR_NOTE, '')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, NOTE_TEST_PDFFILE)


def test_admin_reg(session, client, jwt):
    """Assert that generation of a test report is as expected."""
    # setup
    if is_report_v2() and not is_ci_testing():
        json_data = get_json_from_file(ADMIN_TEST_DATAFILE)
        report = Report(json_data, 'ppr_staff', ReportTypes.MHR_ADMIN_REGISTRATION, '')
        # test
        content, status, headers = report.get_pdf()
        assert headers
        # verify
        check_response(content, status, ADMIN_TEST_PDFFILE)


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
