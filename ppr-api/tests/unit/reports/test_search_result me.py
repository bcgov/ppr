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
import json
from http import HTTPStatus

from ppr_api.reports import Report, ReportTypes
from ppr_api.services.authz import STAFF_ROLE, PPR_ROLE, COLIN_ROLE
from tests.unit.services.report_service import ReportService


SEARCH_RESULT_RG_DATAFILE = 'tests/unit/reports/data/search-detail-reg-num-example.json'
SEARCH_RESULT_RG_REQUESTFILE = 'tests/unit/reports/data/search-detail-reg-num-request.json'
SEARCH_RESULT_RG_PDFFILE = 'tests/unit/reports/data/search-detail-reg-num-example.pdf'

SEARCH_RESULT_SS_DATAFILE = 'tests/unit/reports/data/search-detail-serial-num-example.json'
SEARCH_RESULT_SS_REQUESTFILE = 'tests/unit/reports/data/search-detail-serial-num-request.json'
SEARCH_RESULT_SS_PDFFILE = 'tests/unit/reports/data/search-detail-reg-serial-example.pdf'

SEARCH_RESULT_MH_DATAFILE = 'tests/unit/reports/data/search-detail-mhr-num-example.json'
SEARCH_RESULT_MH_REQUESTFILE = 'tests/unit/reports/data/search-detail-mhr-num-request.json'
SEARCH_RESULT_MH_PDFFILE = 'tests/unit/reports/data/search-detail-mhr-num-example.pdf'

SEARCH_RESULT_AC_DATAFILE = 'tests/unit/reports/data/search-detail-ac-num-example.json'
SEARCH_RESULT_AC_REQUESTFILE = 'tests/unit/reports/data/search-detail-ac-num-request.json'
SEARCH_RESULT_AC_PDFFILE = 'tests/unit/reports/data/search-detail-ac-num-example.pdf'

SEARCH_RESULT_BS_DATAFILE = 'tests/unit/reports/data/search-detail-bus-debtor-example.json'
SEARCH_RESULT_BS_REQUESTFILE = 'tests/unit/reports/data/search-detail-bus-debtor-request.json'
SEARCH_RESULT_BS_PDFFILE = 'tests/unit/reports/data/search-detail-bus-debtor-example.pdf'

SEARCH_RESULT_IS_DATAFILE = 'tests/unit/reports/data/search-detail-ind-debtor-example.json'
SEARCH_RESULT_IS_REQUESTFILE = 'tests/unit/reports/data/search-detail-ind-debtor-request.json'
SEARCH_RESULT_IS_PDFFILE = 'tests/unit/reports/data/search-detail-ind-debtor-example.pdf'

SEARCH_RESULT_DISCHARGED_DATAFILE = 'tests/unit/reports/data/search-detail-discharged-example.json'
SEARCH_RESULT_DISCHARGED_REQUESTFILE = 'tests/unit/reports/data/search-detail-discharged-request.json'
SEARCH_RESULT_DISCHARGED_PDFFILE = 'tests/unit/reports/data/search-detail-discharged-example.pdf'

SEARCH_RESULT_RENEWED_DATAFILE = 'tests/unit/reports/data/search-detail-renewed-example.json'
SEARCH_RESULT_RENEWED_REQUESTFILE = 'tests/unit/reports/data/search-detail-renewed-request.json'
SEARCH_RESULT_RENEWED_PDFFILE = 'tests/unit/reports/data/search-detail-renewed-example.pdf'


def test_search_result_rg(client, jwt):
    """Assert that setup for a registration number search type result report is as expected."""
    # setup
    text_data = None
    with open(SEARCH_RESULT_RG_DATAFILE, 'r') as data_file:
        text_data = data_file.read()
        data_file.close()
    # print(text_data)
    json_data = json.loads(text_data)
    report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT.value)

    # test
    request_data = report._setup_report_data()
    assert request_data
    assert request_data['reportName']
    assert request_data['template']
    assert request_data['templateVars']
    # print(request_data['reportName'])
    # print(request_data['templateVars'])
    with open(SEARCH_RESULT_RG_REQUESTFILE, "w") as request_file:
        request_file.write(json.dumps(request_data['templateVars']))
        request_file.close()
    pdf_output = ReportService.create_report_from_template(request_data['template'], request_data['templateVars'])
    assert pdf_output
    with open(SEARCH_RESULT_RG_PDFFILE, "wb") as pdf_file:
        pdf_file.write(pdf_output)
        pdf_file.close()


def test_search_result_ss(client, jwt):
    """Assert that setup for a serial number search type result report is as expected."""
    # setup
    text_data = None
    with open(SEARCH_RESULT_SS_DATAFILE, 'r') as data_file:
        text_data = data_file.read()
        data_file.close()
    # print(text_data)
    json_data = json.loads(text_data)
    report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT.value)

    # test
    request_data = report._setup_report_data()
    assert request_data
    assert request_data['reportName']
    assert request_data['template']
    assert request_data['templateVars']
    # print(request_data['reportName'])
    # print(request_data['templateVars'])
    with open(SEARCH_RESULT_SS_REQUESTFILE, "w") as request_file:
        request_file.write(json.dumps(request_data['templateVars']))
        request_file.close()
    pdf_output = ReportService.create_report_from_template(request_data['template'], request_data['templateVars'])
    assert pdf_output
    with open(SEARCH_RESULT_SS_PDFFILE, "wb") as pdf_file:
        pdf_file.write(pdf_output)
        pdf_file.close()


def test_search_result_bs(client, jwt):
    """Assert that setup for a business debtor search type result report is as expected."""
    # setup
    text_data = None
    with open(SEARCH_RESULT_BS_DATAFILE, 'r') as data_file:
        text_data = data_file.read()
        data_file.close()
    # print(text_data)
    json_data = json.loads(text_data)
    report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT.value)

    # test
    request_data = report._setup_report_data()
    assert request_data
    assert request_data['reportName']
    assert request_data['template']
    assert request_data['templateVars']
    # print(request_data['reportName'])
    # print(request_data['templateVars'])
    with open(SEARCH_RESULT_BS_REQUESTFILE, "w") as request_file:
        request_file.write(json.dumps(request_data['templateVars']))
        request_file.close()
    pdf_output = ReportService.create_report_from_template(request_data['template'], request_data['templateVars'])
    assert pdf_output
    with open(SEARCH_RESULT_BS_PDFFILE, "wb") as pdf_file:
        pdf_file.write(pdf_output)
        pdf_file.close()


def test_search_result_is(client, jwt):
    """Assert that setup for an individual debtor search type result report is as expected."""
    # setup
    text_data = None
    with open(SEARCH_RESULT_IS_DATAFILE, 'r') as data_file:
        text_data = data_file.read()
        data_file.close()
    # print(text_data)
    json_data = json.loads(text_data)
    report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT.value)

    # test
    request_data = report._setup_report_data()
    assert request_data
    assert request_data['reportName']
    assert request_data['template']
    assert request_data['templateVars']
    # print(request_data['reportName'])
    # print(request_data['templateVars'])
    with open(SEARCH_RESULT_IS_REQUESTFILE, "w") as request_file:
        request_file.write(json.dumps(request_data['templateVars']))
        request_file.close()
    pdf_output = ReportService.create_report_from_template(request_data['template'], request_data['templateVars'])
    assert pdf_output
    with open(SEARCH_RESULT_IS_PDFFILE, "wb") as pdf_file:
        pdf_file.write(pdf_output)
        pdf_file.close()


def test_search_result_mh(client, jwt):
    """Assert that setup for an MHR number search type result report is as expected."""
    # setup
    text_data = None
    with open(SEARCH_RESULT_MH_DATAFILE, 'r') as data_file:
        text_data = data_file.read()
        data_file.close()
    # print(text_data)
    json_data = json.loads(text_data)
    report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT.value)

    # test
    request_data = report._setup_report_data()
    assert request_data
    assert request_data['reportName']
    assert request_data['template']
    assert request_data['templateVars']
    # print(request_data['reportName'])
    # print(request_data['templateVars'])
    with open(SEARCH_RESULT_MH_REQUESTFILE, "w") as request_file:
        request_file.write(json.dumps(request_data['templateVars']))
        request_file.close()
    pdf_output = ReportService.create_report_from_template(request_data['template'], request_data['templateVars'])
    assert pdf_output
    with open(SEARCH_RESULT_MH_PDFFILE, "wb") as pdf_file:
        pdf_file.write(pdf_output)
        pdf_file.close()


def test_search_result_ac(client, jwt):
    """Assert that setup for an aircraft search type result report is as expected."""
    # setup
    text_data = None
    with open(SEARCH_RESULT_AC_DATAFILE, 'r') as data_file:
        text_data = data_file.read()
        data_file.close()
    # print(text_data)
    json_data = json.loads(text_data)
    report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT.value)

    # test
    request_data = report._setup_report_data()
    assert request_data
    assert request_data['reportName']
    assert request_data['template']
    assert request_data['templateVars']
    # print(request_data['reportName'])
    # print(request_data['templateVars'])
    with open(SEARCH_RESULT_AC_REQUESTFILE, "w") as request_file:
        request_file.write(json.dumps(request_data['templateVars']))
        request_file.close()
    pdf_output = ReportService.create_report_from_template(request_data['template'], request_data['templateVars'])
    assert pdf_output
    with open(SEARCH_RESULT_AC_PDFFILE, "wb") as pdf_file:
        pdf_file.write(pdf_output)
        pdf_file.close()


def test_search_result_discharged(client, jwt):
    """Assert that setup for a discharged registration number search type result report is as expected."""
    # setup
    text_data = None
    with open(SEARCH_RESULT_DISCHARGED_DATAFILE, 'r') as data_file:
        text_data = data_file.read()
        data_file.close()
    # print(text_data)
    json_data = json.loads(text_data)
    report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT.value)

    # test
    request_data = report._setup_report_data()
    assert request_data
    assert request_data['reportName']
    assert request_data['template']
    assert request_data['templateVars']
    # print(request_data['reportName'])
    # print(request_data['templateVars'])
    with open(SEARCH_RESULT_DISCHARGED_REQUESTFILE, "w") as request_file:
        request_file.write(json.dumps(request_data['templateVars']))
        request_file.close()
    pdf_output = ReportService.create_report_from_template(request_data['template'], request_data['templateVars'])
    assert pdf_output
    with open(SEARCH_RESULT_DISCHARGED_PDFFILE, "wb") as pdf_file:
        pdf_file.write(pdf_output)
        pdf_file.close()


def test_search_result_renewed(client, jwt):
    """Assert that setup for a renewed registration number search type result report is as expected."""
    # setup
    text_data = None
    with open(SEARCH_RESULT_RENEWED_DATAFILE, 'r') as data_file:
        text_data = data_file.read()
        data_file.close()
    # print(text_data)
    json_data = json.loads(text_data)
    report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT.value)

    # test
    request_data = report._setup_report_data()
    assert request_data
    assert request_data['reportName']
    assert request_data['template']
    assert request_data['templateVars']
    # print(request_data['reportName'])
    # print(request_data['templateVars'])
    with open(SEARCH_RESULT_RENEWED_REQUESTFILE, "w") as request_file:
        request_file.write(json.dumps(request_data['templateVars']))
        request_file.close()
    pdf_output = ReportService.create_report_from_template(request_data['template'], request_data['templateVars'])
    assert pdf_output
    with open(SEARCH_RESULT_RENEWED_PDFFILE, "wb") as pdf_file:
        pdf_file.write(pdf_output)
        pdf_file.close()


def test_report_datetime(client, jwt):
    """Assert that formatting a UTC ISO formatted date time string is converted to the report format as expected."""
    # test
    report_datetime = Report._to_report_datetime('2021-03-12T01:53:54+00:00')
    report_date = Report._to_report_datetime('2021-03-12T01:53:54+00:00', False)

    # verify
    print(report_datetime)
    print(report_date)
    assert report_datetime == 'March 11, 2021 05:53:54 PM Pacific Time'
    assert report_date == 'March 11, 2021'


