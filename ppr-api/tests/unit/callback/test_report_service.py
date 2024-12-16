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
"""Callback report-api service tests."""
from http import HTTPStatus

from flask import current_app

from ppr_api.callback.reports.report_service import get_search_report, get_mail_verification_statement
from ppr_api.models import Party, Registration, SearchResult, SearchRequest

TEST_SEARCH_REPORT_FILE = 'tests/unit/callback/test-get-search-report.pdf'
TEST_VERIFICATION_MAIL_FILE = 'tests/unit/callback/test-get-verification-mail.pdf'


def test_get_search_report(session):
    """Assert that a callback request to generate a search result report works as expected."""
    if is_ci_testing():
        return
    # setup
    json_data = {
        'type': 'SERIAL_NUMBER',
        'criteria': {
            'value': 'JU622994'
        },
        'clientReferenceId': 'UT-SS-1001'
    }
    search_query = SearchRequest.create_from_json(json_data, 'PS12345')
    search_query.search()
    query_json = search_query.json
    search_detail = SearchResult.create_from_search_query(search_query)
    search_detail.save()
    select_json = query_json['results']
    search_detail.update_selection(select_json, 'UNIT TEST INC.')

    # test
    raw_data, status_code, headers = get_search_report(str(search_detail.search_id))
    # print(status_code)
    # check
    assert raw_data
    assert status_code
    assert headers
    assert len(raw_data) > 0
    with open(TEST_SEARCH_REPORT_FILE, "wb") as pdf_file:
        pdf_file.write(raw_data)
        pdf_file.close()


def is_ci_testing() -> bool:
    """Check unit test environment: exclude most reports for CI testing."""
    return  current_app.config.get("DEPLOYMENT_ENV", "testing") == "testing"
