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
"""Test Suite to ensure the model utility functions are working as expected."""
import copy
from http import HTTPStatus

import pytest

from flask import current_app

from mhr_api.models import utils as model_utils, batch_utils
from mhr_api.models.type_tables import MhrDocumentTypes
from mhr_api.resources.v1.registrations import get_batch_noc_location_report
from tests.unit.api.test_registrations import MANUFACTURER_VALID


# testdata pattern is ({start_ts}, {end_ts})
TEST_DATA_NOC_LOCATION = [
    ('2023-12-01T08:01:00+00:00', '2023-12-02T08:01:00+00:00'),
    (None, '2023-12-02T08:01:00+00:00'),
    ('2023-12-01T08:01:00+00:00', None),
    (None, None)
]
# testdata pattern is ({start_ts}, {end_ts})
TEST_DATA_NOC_REPORT = [
    ('2023-12-01T08:01:00+00:00', '2023-12-02T08:01:00+00:00'),
    ('2023-11-28T08:01:00+00:00', '2023-11-29T08:01:00+00:00')
]
# testdata pattern is ({start_ts}, {end_ts})
TEST_DATA_NOC_LOCATION_UPDATE = [
    ('2023-12-01T08:01:00+00:00', '2023-12-02T08:01:00+00:00'),
    (None, None)
]
# testdata pattern is ({start_ts}, {end_ts})
TEST_DATA_BATCH_REGISTRATION = [
    ('2023-12-15T08:01:00+00:00', '2023-12-22T08:01:00+00:00'),
    ('2023-12-15T00:01:00-08:00', '2023-12-22T00:01:00-00:00'),
    ('2023-12-15T00:01:00', '2023-12-22T00:01:00'),
    (None, None)
]


@pytest.mark.parametrize('start_ts,end_ts', TEST_DATA_NOC_LOCATION)
def test_get_batch_location_report_data(session, start_ts, end_ts):
    """Assert that fetching noc location data by optional timestamp range works as expected."""
    results_json = batch_utils.get_batch_location_report_data(start_ts, end_ts)
    if results_json:
        current_app.logger.debug(f'results length={len(results_json)}')
        for result in results_json:
            assert result.get('registrationId')
            assert result.get('reportId')
            assert result.get('reportData')
            assert 'batchStorageUrl' in result


def test_get_batch_location_report_name(session):
    """Assert that creating a bath noc location report name for doc storage works as expected."""
    now_ts = model_utils.now_ts()
    time = str(now_ts.hour) + '_' + str(now_ts.minute)
    test_name: str = batch_utils.BATCH_DOC_NAME_NOC_LOCATION.format(time=time)
    storage_name: str = batch_utils.get_batch_storage_name_noc_location()
    current_app.logger.debug(f'report storage name={storage_name}')
    assert storage_name.find(test_name) > -1


@pytest.mark.parametrize('start_ts,end_ts', TEST_DATA_NOC_LOCATION_UPDATE)
def test_update_location_report_batch_url(session, start_ts, end_ts):
    """Assert that batch updating of the noc location report batch storage url works as expected."""
    results_json = batch_utils.get_batch_location_report_data(start_ts, end_ts)
    if results_json:
        batch_url: str = batch_utils.get_batch_storage_name_noc_location()
        update_count: int = batch_utils.update_reg_report_batch_url(results_json, batch_url)
        current_app.logger.debug(f'update count={update_count}')
        assert update_count > 0


@pytest.mark.parametrize('start_ts,end_ts', TEST_DATA_NOC_REPORT)
def test_save_noc_location_report(session, start_ts, end_ts):
    """Assert that conditionally generating and storing a noc location report works as expected."""
    results_json = batch_utils.get_batch_location_report_data(start_ts, end_ts)
    if results_json:
        raw_data, response_status, headers = get_batch_noc_location_report(results_json)
        assert response_status == HTTPStatus.OK
        report_url: str = batch_utils.save_batch_location_report(results_json, raw_data, True)
        current_app.logger.debug(f'doc storage report link:\n{report_url}')
        raw_data, response_status, headers = batch_utils.batch_location_report_response(raw_data, report_url, False)
        assert response_status == HTTPStatus.OK
        assert headers
        assert raw_data
    else:
        data, response_status = batch_utils.batch_location_report_empty(False, start_ts, end_ts)
        assert response_status == HTTPStatus.NO_CONTENT
        assert not data


def test_is_batch_doc_type(session):
    """Assert that the batch document type check works as expected."""
    for doc_type in batch_utils.BATCH_DOC_TYPES:
        assert batch_utils.is_batch_doc_type(doc_type)
    assert not batch_utils.is_batch_doc_type(MhrDocumentTypes.NPUB.value)


def test_is_previous_location_doc_type(session):
    """Assert that the previous location document type check works as expected."""
    for doc_type in batch_utils.PREVIOUS_LOCATION_DOC_TYPES:
        assert batch_utils.is_previous_location_doc_type(doc_type, MANUFACTURER_VALID)
    assert not batch_utils.is_previous_location_doc_type(MhrDocumentTypes.REG_101.value, MANUFACTURER_VALID)
    test_reg = copy.deepcopy(MANUFACTURER_VALID)
    del test_reg['location']
    assert not batch_utils.is_previous_location_doc_type(MhrDocumentTypes.PUBA.value, test_reg)
    assert not batch_utils.is_previous_location_doc_type(MhrDocumentTypes.REGC.value, test_reg)


def test_is_previous_owner_doc_type(session):
    """Assert that the previous owner document type check works as expected."""
    for doc_type in batch_utils.PREVIOUS_OWNER_DOC_TYPES:
        assert batch_utils.is_previous_owner_doc_type(doc_type, MANUFACTURER_VALID)
    assert not batch_utils.is_previous_owner_doc_type(MhrDocumentTypes.REG_101.value, MANUFACTURER_VALID)
    test_reg = copy.deepcopy(MANUFACTURER_VALID)
    del test_reg['ownerGroups']
    assert not batch_utils.is_previous_owner_doc_type(MhrDocumentTypes.PUBA.value, test_reg)
    assert not batch_utils.is_previous_owner_doc_type(MhrDocumentTypes.REGC.value, test_reg)


@pytest.mark.parametrize('start_ts,end_ts', TEST_DATA_BATCH_REGISTRATION)
def test_get_batch_registration_data(session, start_ts, end_ts):
    """Assert that fetching batch registration data with/without optional timestamp range works as expected."""
    results_json = batch_utils.get_batch_registration_data(start_ts, end_ts)
    if results_json:
        current_app.logger.debug(f'results length={len(results_json)}')
        for result in results_json:
            mhr_number = result.get('mhrNumber')
            if int(mhr_number) > 107000:
                assert result.get('documentType')
                assert result.get('description')
                assert result.get('location')
                assert result.get('ownerGroups')
    else:
        current_app.logger.debug('No batch registration results within the specified timestamp range.')
