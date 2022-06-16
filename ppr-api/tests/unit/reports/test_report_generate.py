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

"""Tests to generate a search results PDF report.

Requires installation of WeazyPrint 53.4: pip install weazyprint 53.4.
Uncomment the line of this file that calls ReportService (ReportService.create_report_from_template).
For search, copy the response JSON of the API GET search results to the SEARCH_RESULT_DATAFILE file.
For registraionts, copy the response JSON of the API GET registration to the VERIFICATION_DATAFILE file.
Verify the local env variable is set to PROD to produce the correct report watermark: POD_NAMESPACE="prod".
Generate the search report from the ppr-api directory with the command:
pytest -v ./tests/unit/reports/test_search_report_generate.py::test_search_results_report
Generate the verification report from the ppr-api directory with the command:
pytest -v ./tests/unit/reports/test_search_report_generate.py::test_verification_report
"""
import json

from flask import current_app

from ppr_api.reports import Report, ReportTypes
from tests.unit.services.report_service import ReportService


SEARCH_RESULT_DATAFILE = 'tests/unit/reports/data/search-results-report.json'
SEARCH_RESULT_REQUESTFILE = 'tests/unit/reports/data/search-results-request.json'
SEARCH_RESULT_PDFFILE = 'tests/unit/reports/data/search-results-report.pdf'

VERIFICATION_DATAFILE = 'tests/unit/reports/data/verification-report.json'
VERIFICATION_REQUESTFILE = 'tests/unit/reports/data/verification-report-request.json'
VERIFICATION_PDFFILE = 'tests/unit/reports/data/verification-report.pdf'


def test_search_results_report(client, jwt):
    """Generate locally a search results report."""
    # setup
    text_data = None
    pdf_output = None
    current_app.logger.debug(f'Loading test data from file {SEARCH_RESULT_DATAFILE}')
    with open(SEARCH_RESULT_DATAFILE, 'r') as data_file:
        text_data = data_file.read()
        data_file.close()
    # print(text_data)
    json_data = json.loads(text_data)
    report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT.value, '')

    # test
    current_app.logger.debug('Calling report._setup_report_data')
    request_data = report._setup_report_data()
    assert request_data
    assert request_data['reportName']
    assert request_data['template']
    assert request_data['templateVars']
    with open(SEARCH_RESULT_REQUESTFILE, "w") as request_file:
        request_file.write(json.dumps(request_data['templateVars']))
        # request_file.write(json.dumps(request_data))
        request_file.close()
    current_app.logger.debug('Calling ReportService.create_report_from_template')
    # pdf_output = ReportService.create_report_from_template(request_data['template'], request_data['templateVars'])
    if pdf_output:
        with open(SEARCH_RESULT_PDFFILE, "wb") as pdf_file:
            pdf_file.write(pdf_output)
            pdf_file.close()
        current_app.logger.debug('PDF report generation completed.')


def test_verification_report(client, jwt):
    """Assert that setup for a financing statement sa report is as expected."""
    # setup
    text_data = None
    pdf_output = None
    with open(VERIFICATION_DATAFILE, 'r') as data_file:
        text_data = data_file.read()
        data_file.close()
    # print(text_data)
    json_data = json.loads(text_data)
    report = Report(json_data, 'PS12345', ReportTypes.FINANCING_STATEMENT_REPORT.value, '')

    # test
    request_data = report._setup_report_data()
    assert request_data
    assert request_data['reportName']
    assert request_data['template']
    assert request_data['templateVars']
    with open(VERIFICATION_REQUESTFILE, "w") as request_file:
        request_file.write(json.dumps(request_data['templateVars']))
        # request_file.write(json.dumps(request_data))
        request_file.close()
    # pdf_output = ReportService.create_report_from_template(request_data['template'], request_data['templateVars'])
    if pdf_output:
        with open(VERIFICATION_PDFFILE, "wb") as pdf_file:
            pdf_file.write(pdf_output)
            pdf_file.close()
