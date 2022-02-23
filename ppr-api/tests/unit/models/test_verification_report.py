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

"""Tests to assure the VerificationReport Model.

Test-Suite to ensure that the Verification Report Model is working as expected.
"""
import json

from ppr_api.models import VerificationReport
from ppr_api.models.utils import format_ts, now_ts
from ppr_api.reports import ReportTypes


TEST_REPORT_DATA = {
    'test': 'junk'
}


def test_find_by_id(session):
    """Assert that find verification report by ID contains all expected elements."""
    verification_report: VerificationReport = VerificationReport.find_by_id(200000000)
    assert verification_report
    assert verification_report.id == 200000000
    assert verification_report.create_ts
    assert verification_report.registration_id
    assert verification_report.report_data
    assert verification_report.report_type
    assert not verification_report.doc_storage_url


def test_find_by_registration_id(session):
    """Assert that find verification report by registration id contains all expected elements."""
    verification_report = VerificationReport.find_by_registration_id(200000000)
    assert verification_report
    assert verification_report.id
    assert verification_report.create_ts
    assert verification_report.registration_id == 200000000
    assert verification_report.report_data
    assert verification_report.report_type
    assert not verification_report.doc_storage_url


def test_find_by_id_invalid(session):
    """Assert that find verification report by non-existent ID returns the expected result."""
    verification_report = VerificationReport.find_by_id(300000000)
    assert not verification_report


def test_find_by_reg_id_invalid(session):
    """Assert that find verification_report by non-existent registration id eturns the expected result."""
    verification_report = VerificationReport.find_by_registration_id(300000000)
    assert not verification_report


def test_save(session):
    """Assert that saving a verification report works as expected."""
    verification_report: VerificationReport = VerificationReport(
        create_ts=now_ts(),
        registration_id=200000001,
        report_data=TEST_REPORT_DATA,
        report_type=ReportTypes.FINANCING_STATEMENT_REPORT.value)
    verification_report.save()
    assert verification_report.id
    assert not verification_report.doc_storage_url


def test_update(session):
    """Assert that saving a verification report works as expected."""
    verification_report: VerificationReport = VerificationReport(
        create_ts=now_ts(),
        registration_id=200000001,
        report_data=TEST_REPORT_DATA,
        report_type=ReportTypes.FINANCING_STATEMENT_REPORT.value)
    verification_report.save()
    assert verification_report.id
    assert not verification_report.doc_storage_url
    verification_report.update_storage_url('doc_url')
    new_report: VerificationReport = VerificationReport.find_by_id(verification_report.id)
    assert new_report.doc_storage_url == 'doc_url'


def test_verification_report_json(session):
    """Assert that the verification report model renders to a json format correctly."""
    verification_report: VerificationReport = VerificationReport(
        id=1000,
        create_ts=now_ts(),
        registration_id=2000,
        report_data= json.dumps(TEST_REPORT_DATA),
        report_type=ReportTypes.FINANCING_STATEMENT_REPORT.value,
        doc_storage_url='http%3A%2F%2Fmocktarget.apigee.net'
    )
    report_json = {
        'id': verification_report.id,
        'createDateTime': format_ts(verification_report.create_ts),
        'registrationId': verification_report.registration_id,
        'reportData': verification_report.report_data,
        'reportType': verification_report.report_type,
        'documentStorageURL': verification_report.doc_storage_url
    }
    assert verification_report.json == report_json
