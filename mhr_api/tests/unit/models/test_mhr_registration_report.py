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

"""Tests to assure the MhrRegistrationReport Model.

Test-Suite to ensure that the MHR Registraton Model for report tracking is working as expected.
"""
import json

import pytest

from mhr_api.models import MhrRegistrationReport
from mhr_api.models.utils import format_ts, now_ts
from mhr_api.reports import ReportTypes


# testdata pattern is ({id}, {has_results})
TEST_ID_DATA = [
    (200000000, True),
    (300000000, False)
]
TEST_REPORT_DATA = {
    'test': 'junk'
}


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_id(session, id, has_results):
    """Assert that finding a registration report by ID contains all expected elements."""
    report: MhrRegistrationReport = MhrRegistrationReport.find_by_id(id)
    if has_results:
        assert report
        assert report.id == id
        assert report.create_ts
        assert report.registration_id
        assert report.report_data
        assert report.report_type
        assert not report.doc_storage_url
    else:
        assert not report


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_registration_id(session, id, has_results):
    """Assert that finding a registration report by registration id contains all expected elements."""
    report: MhrRegistrationReport = MhrRegistrationReport.find_by_registration_id(id)
    if has_results:
        assert report
        assert report.id == id
        assert report.create_ts
        assert report.registration_id
        assert report.report_data
        assert report.report_type
        assert not report.doc_storage_url
    else:
        assert not report


def test_save(session):
    """Assert that saving a registration report works as expected."""
    report: MhrRegistrationReport = MhrRegistrationReport(
        create_ts=now_ts(),
        registration_id=200000000,
        report_data=TEST_REPORT_DATA,
        report_type=ReportTypes.MHR_REGISTRATION)
    report.save()
    assert report.id
    assert not report.doc_storage_url


def test_update(session):
    """Assert that updating a registration report works as expected."""
    report: MhrRegistrationReport = MhrRegistrationReport(
        create_ts=now_ts(),
        registration_id=200000000,
        report_data=TEST_REPORT_DATA,
        report_type=ReportTypes.MHR_REGISTRATION)
    report.save()
    assert report.id
    assert not report.doc_storage_url
    report.update_storage_url('doc_url')
    new_report: MhrRegistrationReport = MhrRegistrationReport.find_by_id(report.id)
    assert new_report.doc_storage_url == 'doc_url'


def test_registration_report_json(session):
    """Assert that the registration report model renders to a json format correctly."""
    report: MhrRegistrationReport = MhrRegistrationReport(
        id=1000,
        create_ts=now_ts(),
        registration_id=2000,
        report_data= json.dumps(TEST_REPORT_DATA),
        report_type=ReportTypes.MHR_REGISTRATION,
        doc_storage_url='http%3A%2F%2Fmocktarget.apigee.net'
    )
    report_json = {
        'id': report.id,
        'createDateTime': format_ts(report.create_ts),
        'registrationId': report.registration_id,
        'reportData': report.report_data,
        'reportType': report.report_type,
        'documentStorageURL': report.doc_storage_url
    }
    assert report.json == report_json
