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

from ppr_api.reports import Report, ReportTypes


SEARCH_RESULT_RG_DATAFILE = 'tests/unit/reports/data/search-detail-reg-num-example.json'
SEARCH_RESULT_RG_REQUESTFILE = 'tests/unit/reports/data/search-detail-reg-num-request.json'

SEARCH_RESULT_SS_DATAFILE = 'tests/unit/reports/data/search-detail-serial-num-example.json'
SEARCH_RESULT_SS_REQUESTFILE = 'tests/unit/reports/data/search-detail-serial-num-request.json'

SEARCH_RESULT_MH_DATAFILE = 'tests/unit/reports/data/search-detail-mhr-num-example.json'
SEARCH_RESULT_MH_REQUESTFILE = 'tests/unit/reports/data/search-detail-mhr-num-request.json'

SEARCH_RESULT_AC_DATAFILE = 'tests/unit/reports/data/search-detail-ac-num-example.json'
SEARCH_RESULT_AC_REQUESTFILE = 'tests/unit/reports/data/search-detail-ac-num-request.json'

SEARCH_RESULT_BS_DATAFILE = 'tests/unit/reports/data/search-detail-bus-debtor-example.json'
SEARCH_RESULT_BS_REQUESTFILE = 'tests/unit/reports/data/search-detail-bus-debtor-request.json'

SEARCH_RESULT_IS_DATAFILE = 'tests/unit/reports/data/search-detail-ind-debtor-example.json'
SEARCH_RESULT_IS_REQUESTFILE = 'tests/unit/reports/data/search-detail-ind-debtor-request.json'

SEARCH_RESULT_DISCHARGED_DATAFILE = 'tests/unit/reports/data/search-detail-discharged-example.json'
SEARCH_RESULT_DISCHARGED_REQUESTFILE = 'tests/unit/reports/data/search-detail-discharged-request.json'

SEARCH_RESULT_RENEWED_DATAFILE = 'tests/unit/reports/data/search-detail-renewed-example.json'
SEARCH_RESULT_RENEWED_REQUESTFILE = 'tests/unit/reports/data/search-detail-renewed-request.json'

SEARCH_RESULT_NO_RESULTS_DATAFILE = 'tests/unit/reports/data/search-detail-no-results-example.json'
SEARCH_RESULT_NO_RESULTS_REQUESTFILE = 'tests/unit/reports/data/search-detail-no-results-request.json'

TEST_REPORT_DATA = [
    ('RG', SEARCH_RESULT_RG_DATAFILE, SEARCH_RESULT_RG_REQUESTFILE),
    ('AC', SEARCH_RESULT_AC_DATAFILE, SEARCH_RESULT_AC_REQUESTFILE),
    ('MH', SEARCH_RESULT_MH_DATAFILE, SEARCH_RESULT_MH_REQUESTFILE),
    ('SS', SEARCH_RESULT_SS_DATAFILE, SEARCH_RESULT_SS_REQUESTFILE),
    ('IS', SEARCH_RESULT_IS_DATAFILE, SEARCH_RESULT_IS_REQUESTFILE),
    ('BS', SEARCH_RESULT_BS_DATAFILE, SEARCH_RESULT_BS_REQUESTFILE),
    ('DISCHARGED', SEARCH_RESULT_DISCHARGED_DATAFILE, SEARCH_RESULT_DISCHARGED_REQUESTFILE),
    ('RENEWED', SEARCH_RESULT_RENEWED_DATAFILE, SEARCH_RESULT_RENEWED_REQUESTFILE),
    ('NO_RESULTS', SEARCH_RESULT_NO_RESULTS_DATAFILE, SEARCH_RESULT_NO_RESULTS_REQUESTFILE),
]

TEST_DATETIME_DATA = [
    ('2021-03-12T01:53:54+00:00', 'March 11, 2021 05:53:54 PM Pacific Time', True),
    ('2021-03-12T01:53:54+00:00', 'March 11, 2021', False)
]


@pytest.mark.parametrize('type,json_data_file,report_data_file', TEST_REPORT_DATA)
def test_search_result_config(client, jwt, type, json_data_file, report_data_file):
    """Assert that the setup for search result report with all search type data is as expected."""
    # setup
    text_data = None
    with open(json_data_file, 'r') as data_file:
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
    report_data = request_data['templateVars']
    assert report_data['meta_subject']
    assert report_data['meta_title']
    assert report_data['meta_account_id']
    assert report_data['environment']
    assert report_data['searchDateTime'].endswith('Pacific Time')
    if type != 'NO_RESULTS':
        financing = report_data['details'][0]['financingStatement']
        assert financing['registeringParty']['address']['country'] == 'Canada'


@pytest.mark.parametrize('test_value,expected_value,is_date_time', TEST_DATETIME_DATA)
def test_report_datetime(test_value, expected_value, is_date_time):
    """Assert that formatting a UTC ISO formatted date time string is converted to the report format as expected."""
    # test
    report_value = Report._to_report_datetime(test_value, is_date_time)

    # verify
    # print(report_value)
    assert report_value == expected_value
