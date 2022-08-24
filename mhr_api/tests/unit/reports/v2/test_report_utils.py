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
"""Report helper function tests."""
import json

from flask import current_app
# import pytest

from mhr_api.reports.v2.report import Report
from mhr_api.reports.v2 import report_utils
from mhr_api.reports.v2.report_utils import ReportTypes


SEARCH_RESULT_MHR_DATAFILE = 'tests/unit/reports/data/search-detail-mhr-example.json'


def test_get_header_data(session):
    """Assert that getting the report header data works as expected."""
    # setup
    title = 'Test Title'
    # test
    data = report_utils.get_header_data(title)
    # verify
    assert data
    assert data.find(title) != -1


def test_get_footer_data(session):
    """Assert that getting the report footer data works as expected."""
    # setup
    text = 'Test Text'
    # test
    data = report_utils.get_footer_data(text)
    # verify
    assert data
    assert data.find(text) != -1


def test_get_report_meta_data(session):
    """Assert that getting the report generaton meta data works as expected."""
    data = report_utils.get_report_meta_data()
    assert data
    assert data.get('marginTop')
    assert data.get('marginBottom')
    assert data.get('marginLeft')
    assert data.get('marginRight')
    assert data.get('printBackground')


def test_get_html_from_data(session):
    """Assert that getting the report source html from report data works as expected."""
    json_data = get_json_from_file(SEARCH_RESULT_MHR_DATAFILE)
    report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
    request_data = report._setup_report_data()
    html_data = report_utils.get_html_from_data(request_data)
    assert html_data
    current_app.logger.info('html_data length=' + str(len(html_data)))


def test_get_report_files(session):
    """Assert that getting the report source files from report data works as expected."""
    json_data = get_json_from_file(SEARCH_RESULT_MHR_DATAFILE)
    report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')
    request_data = report._setup_report_data()
    files = report_utils.get_report_files(request_data, ReportTypes.SEARCH_DETAIL_REPORT)
    assert files
    assert files.get('index.html')
    assert files.get('header.html')
    assert files.get('footer.html')
    current_app.logger.info('file body length=' + str(len(files.get('index.html'))))
    current_app.logger.info('file header length=' + str(len(files.get('header.html'))))
    current_app.logger.info('file footer length=' + str(len(files.get('footer.html'))))


def get_json_from_file(data_file: str):
    """Get json data from report data file."""
    text_data = None
    with open(data_file, 'r') as data_file:
        text_data = data_file.read()
        data_file.close()
    # print(text_data)
    json_data = json.loads(text_data)
    return json_data
