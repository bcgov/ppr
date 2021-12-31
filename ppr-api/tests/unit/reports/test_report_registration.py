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

"""Tests to verify the registration PDF report setup.

Test-Suite to ensure that the report service for registration reports is working as expected.
"""
from http import HTTPStatus
import json

import pytest

from ppr_api.reports import Report, ReportTypes, get_verification_mail
from ppr_api.services.payment.client import SBCPaymentClient


FINANCING_SA_DATAFILE = 'tests/unit/reports/data/financing-sa-example.json'
FINANCING_RL_DATAFILE = 'tests/unit/reports/data/financing-rl-example.json'
FINANCING_NO_CHANGE_DATAFILE = 'tests/unit/reports/data/financing-sa-no-changes-example.json'
RENEWAL_DATAFILE = 'tests/unit/reports/data/renewal-example.json'
RENEWAL_RL_DATAFILE = 'tests/unit/reports/data/renewal-rl-example.json'
CHANGE_DT_DATAFILE = 'tests/unit/reports/data/change-dt-example.json'
CHANGE_AC_DATAFILE = 'tests/unit/reports/data/change-ac-example.json'
AMENDMENT_DATAFILE = 'tests/unit/reports/data/amendment-example.json'
AMENDMENT_CO_DATAFILE = 'tests/unit/reports/data/amendment-co-example.json'
DISCHARGE_DATAFILE = 'tests/unit/reports/data/discharge-example.json'
DISCHARGE_DATAFILE_COVER = 'tests/unit/reports/data/discharge-example-cover.json'
AMENDMENT_DATAFILE_COVER = 'tests/unit/reports/data/amendment-example-cover.json'
VERIFICATION_MAIL_PDFFILE = 'tests/unit/reports/data/verification-mail-discharge-example.pdf'

TEST_REPORT_DATA = [
    (ReportTypes.FINANCING_STATEMENT_REPORT.value, FINANCING_RL_DATAFILE),
    (ReportTypes.FINANCING_STATEMENT_REPORT.value, FINANCING_SA_DATAFILE),
    (ReportTypes.FINANCING_STATEMENT_REPORT.value, FINANCING_NO_CHANGE_DATAFILE),
    (ReportTypes.FINANCING_STATEMENT_REPORT.value, RENEWAL_DATAFILE),
    (ReportTypes.FINANCING_STATEMENT_REPORT.value, RENEWAL_RL_DATAFILE),
    (ReportTypes.FINANCING_STATEMENT_REPORT.value, AMENDMENT_DATAFILE),
    (ReportTypes.FINANCING_STATEMENT_REPORT.value, AMENDMENT_CO_DATAFILE),
    (ReportTypes.FINANCING_STATEMENT_REPORT.value, CHANGE_AC_DATAFILE),
    (ReportTypes.FINANCING_STATEMENT_REPORT.value, CHANGE_DT_DATAFILE),
    (ReportTypes.FINANCING_STATEMENT_REPORT.value, DISCHARGE_DATAFILE),
    (ReportTypes.COVER_PAGE_REPORT.value, DISCHARGE_DATAFILE_COVER),
    (ReportTypes.COVER_PAGE_REPORT.value, AMENDMENT_DATAFILE_COVER)
]


@pytest.mark.parametrize('type,json_data_file', TEST_REPORT_DATA)
def test_registration_config(client, jwt, type, json_data_file):
    """Assert that the setup for all registration report types is as expected."""
    # setup
    text_data = None
    with open(json_data_file, 'r') as data_file:
        text_data = data_file.read()
        data_file.close()
    # print(text_data)
    json_data = json.loads(text_data)
    report = Report(json_data, 'PS12345', type, 'Account Name')

    # test
    request_data = report._setup_report_data()
    assert request_data
    assert request_data['reportName']
    assert request_data['template']
    assert request_data['templateVars']
    # print(request_data['reportName'])
    # print(request_data['templateVars'])
    report_data = request_data['templateVars']
    assert report_data['meta_title']
    assert report_data['meta_account_id']
    assert report_data['environment']
    if type != ReportTypes.COVER_PAGE_REPORT.value:
        assert report_data['createDateTime'].endswith('Pacific time')
        assert report_data['registeringParty']['address']['country'] == 'Canada'
    else:
        assert report_data['cover']['line1']
        assert report_data['cover']['line2']
        assert report_data['cover']['line4']


def test_verification_mail(client, jwt):
    """Assert that merging a cover page with a verification statement works as expected."""
    # setup
    text_data = None
    with open(DISCHARGE_DATAFILE_COVER, 'r') as data_file:
        text_data = data_file.read()
        data_file.close()
    # print(text_data)
    report_data = json.loads(text_data)
    token = SBCPaymentClient.get_sa_token()
    pdf_output, status, headers = get_verification_mail(report_data, 'PS12345', token, 'UNIT TEST ACCOUNT', 99999999)
    # test
    assert pdf_output
    assert status == HTTPStatus.OK
    with open(VERIFICATION_MAIL_PDFFILE, "wb") as pdf_file:
        pdf_file.write(pdf_output)
        pdf_file.close()
