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

"""Tests to assure the MailReport Model.

Test-Suite to ensure that the Mail Report Model is working as expected.
"""
import json

import pytest

from ppr_api.models import MailReport
from ppr_api.models.utils import format_ts, now_ts, ts_from_iso_format, now_ts_offset


TEST_REPORT_DATA = {
    'test': 'junk'
}
# testdata pattern is ({has_data}, {id}, {reg_id}, {party_id}, {has_doc}, {has_retry})
TEST_FIND_DATA = [
    (False, 300000000, None, None, False, False),
    (True, 200000000, 200000004, 200000013, True, False),
    (True, 200000002, 200000008, 200000023, False, True)
]
# testdata pattern is ({desc}, {has_data}, {start_ts}, {end_ts}, job_id)
TEST_MAIL_LIST_DATA = [
    ('Valid start', True, '2023-02-08T00:00:01-08:00', None, None),
    ('Valid range', True, '2023-02-08T00:00:01-08:00', None, None),
    ('Valid range with job id', True, '2023-02-08T00:00:01-08:00', None, 1234),
    ('Valid range no data', False, '2023-02-01T00:00:01-08:00', '2023-02-03T00:00:01-08:00', None)
]
# testdata pattern is ({desc}, {start_ts}, job_id)
TEST_MAIL_LIST_JOB_DATA = [
    ('Valid start', '2023-02-08T00:00:01-08:00', 1234),
    ('Valid range', '2023-02-08T00:00:01-08:00', 1234)
]


@pytest.mark.parametrize('has_data,id,reg_id,party_id,has_doc,has_retry', TEST_FIND_DATA)
def test_find_by_id(session, has_data, id, reg_id, party_id, has_doc, has_retry):
    """Assert that find Mail report by ID contains all expected elements."""
    mail_report: MailReport = MailReport.find_by_id(id)
    if has_data:
        assert mail_report
        assert mail_report.id == id
        assert mail_report.create_ts
        assert mail_report.registration_id == reg_id
        assert mail_report.party_id == party_id
        assert mail_report.report_data
        if has_doc:
            assert mail_report.doc_storage_url
            assert mail_report.status
        else:
            assert not mail_report.doc_storage_url
        if has_retry:
            assert mail_report.retry_count
        else:
            assert not mail_report.retry_count
    else:
        assert not mail_report


@pytest.mark.parametrize('has_data,id,reg_id,party_id,has_doc,has_retry', TEST_FIND_DATA)
def test_find_by_registration_party_id(session, has_data, id, reg_id, party_id, has_doc, has_retry):
    """Assert that find Mail Report by registration and party id contains all expected elements."""
    mail_report = MailReport.find_by_registration_party_id(reg_id, party_id)
    if has_data:
        assert mail_report
        assert mail_report.id == id
        assert mail_report.create_ts
        assert mail_report.registration_id == reg_id
        assert mail_report.party_id == party_id
        assert mail_report.report_data
        if has_doc:
            assert mail_report.doc_storage_url
            assert mail_report.status
        else:
            assert not mail_report.doc_storage_url
        if has_retry:
            assert mail_report.retry_count
        else:
            assert not mail_report.retry_count
    else:
        assert not mail_report


def test_save(session):
    """Assert that saving a Mail Report works as expected."""
    mail_report: MailReport = MailReport(
        create_ts=now_ts(),
        registration_id=200000001,
        party_id=200000001,
        report_data=TEST_REPORT_DATA)
    mail_report.save()
    assert mail_report.id
    assert not mail_report.doc_storage_url


def test_update_doc_storage(session):
    """Assert that updating a Mail Report doc storage path works as expected."""
    mail_report: MailReport = MailReport(
        create_ts=now_ts(),
        registration_id=200000001,
        party_id=200000001,
        report_data=TEST_REPORT_DATA)
    mail_report.save()
    assert mail_report.id
    assert not mail_report.doc_storage_url
    mail_report.update_storage_url('doc_url', 200)
    new_report: MailReport = MailReport.find_by_id(mail_report.id)
    assert new_report.doc_storage_url == 'doc_url'


def test_update_retry(session):
    """Assert that updating a Mail Report retry count works as expected."""
    mail_report: MailReport = MailReport(
        create_ts=now_ts(),
        registration_id=200000001,
        party_id=200000001,
        report_data=TEST_REPORT_DATA)
    mail_report.save()
    assert mail_report.id
    assert not mail_report.doc_storage_url
    assert not mail_report.retry_count
    mail_report.update_retry_count(503, 'gateway unavailable')
    new_report: MailReport = MailReport.find_by_id(mail_report.id)
    assert new_report.retry_count == 1
    assert new_report.status == 503
    assert new_report.message == 'gateway unavailable'


def test_mail_report_json(session):
    """Assert that the Mail Report model renders to a json format correctly."""
    mail_report: MailReport = MailReport(
        id=1000,
        create_ts=now_ts(),
        registration_id=2000,
        party_id=3000,
        report_data=json.dumps(TEST_REPORT_DATA),
        doc_storage_url='/2025/10/25/test-report.pdf',
        status=200,
        batch_job_id=1234
    )
    report_json = {
        'id': mail_report.id,
        'createDateTime': format_ts(mail_report.create_ts),
        'registrationId': mail_report.registration_id,
        'partyId': mail_report.party_id,
        'reportData': mail_report.report_data,
        'documentStorageURL': mail_report.doc_storage_url,
        'retryCount': 0,
        'status': mail_report.status,
        'message': '',
        'jobId': mail_report.batch_job_id
    }
    assert mail_report.json == report_json


@pytest.mark.parametrize('desc,has_data,start_ts,end_ts,job_id', TEST_MAIL_LIST_DATA)
def test_find_list_by_timestamp(session, desc, has_data, start_ts, end_ts, job_id):
    start = None
    end = None
    if start_ts:
        start = ts_from_iso_format(start_ts)
    if desc in ('Valid range', 'Valid range with job id'):
        end = now_ts_offset(1, True)
    elif end_ts:
        end = ts_from_iso_format(end_ts)
    list_json = MailReport.find_list_by_timestamp(start, end, job_id)
    if has_data:
        assert list_json
        for result in list_json:
            assert result.get('id')
            assert result.get('dateTime')
            assert result.get('docStorageRef')
            if job_id and job_id > 0:
                assert result.get('jobId') == job_id
            else:
                assert 'jobId' not in result
    else:
        assert not list_json


@pytest.mark.parametrize('desc,start_ts,job_id', TEST_MAIL_LIST_JOB_DATA)
def test_list_job_update(session, desc, start_ts, job_id):
    start = None
    end = None
    if start_ts:
        start = ts_from_iso_format(start_ts)
    if desc == 'Valid range':
        end = now_ts()
    MailReport.save_job_id(start, end, job_id)
