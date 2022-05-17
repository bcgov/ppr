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

import pytest

from mhr_api.reports import Report, ReportTypes


SEARCH_RESULT_MHR_DATAFILE = 'tests/unit/reports/data/search-detail-mhr-example.json'
SEARCH_RESULT_SERIAL_DATAFILE = 'tests/unit/reports/data/search-detail-serial-example.json'
SEARCH_RESULT_OWNER_DATAFILE = 'tests/unit/reports/data/search-detail-owner-example.json'
SEARCH_RESULT_ORG_DATAFILE = 'tests/unit/reports/data/search-detail-org-example.json'
SEARCH_RESULT_COMBO_DATAFILE = 'tests/unit/reports/data/search-detail-combo-example.json'
SEARCH_RESULT_NIL_DATAFILE = 'tests/unit/reports/data/search-detail-no-results-example.json'

SEARCH_RESULT_REQUESTFILE = 'tests/unit/reports/data/search-detail-request.json'

TEST_REPORT_DATA = [
    ('MM', SEARCH_RESULT_MHR_DATAFILE, SEARCH_RESULT_REQUESTFILE),
    ('MS', SEARCH_RESULT_SERIAL_DATAFILE, SEARCH_RESULT_REQUESTFILE),
    ('MI', SEARCH_RESULT_OWNER_DATAFILE, SEARCH_RESULT_REQUESTFILE),
    ('MB', SEARCH_RESULT_ORG_DATAFILE, SEARCH_RESULT_REQUESTFILE),
    ('MM', SEARCH_RESULT_COMBO_DATAFILE, SEARCH_RESULT_REQUESTFILE),
    ('MH', SEARCH_RESULT_NIL_DATAFILE, SEARCH_RESULT_REQUESTFILE)
]

TEST_DATETIME_DATA = [
    ('2021-03-12T01:53:54+00:00', 'March 11, 2021 at 5:53:54 pm Pacific time', True),
    ('2021-03-12T01:53:54+00:00', 'March 11, 2021', False)
]


@pytest.mark.parametrize('type,json_data_file,report_data_file', TEST_REPORT_DATA)
def test_search_result_config(session, client, jwt, type, json_data_file, report_data_file):
    """Assert that the setup for search result report with all search type data is as expected."""
    # setup
    text_data = None
    with open(json_data_file, 'r') as data_file:
        text_data = data_file.read()
        data_file.close()
    # print(text_data)
    json_data = json.loads(text_data)
    report = Report(json_data, 'PS12345', ReportTypes.SEARCH_DETAIL_REPORT, 'Account Name')

    # test
    request_data = report._setup_report_data()
    assert request_data
    assert request_data['reportName']
    assert request_data['template']
    assert request_data['templateVars']
    # print(request_data['reportName'])
    # print(request_data['templateVars'])
    report_data = request_data['templateVars']
    assert report_data['meta_subject']
    assert report_data['meta_title']
    assert report_data['meta_account_id']
    assert report_data['searchDateTime'].endswith('Pacific time')


@pytest.mark.parametrize('test_value,expected_value,is_date_time', TEST_DATETIME_DATA)
def test_report_datetime(test_value, expected_value, is_date_time):
    """Assert that formatting a UTC ISO formatted date time string is converted to the report format as expected."""
    # test
    report_value = Report._to_report_datetime(test_value, is_date_time)

    # verify
    # print(report_value)
    assert report_value == expected_value
