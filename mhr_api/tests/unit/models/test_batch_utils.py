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
from http import HTTPStatus

import pytest

from flask import current_app

from mhr_api.models import utils as model_utils, batch_utils
from mhr_api.resources.v1.registrations import get_batch_noc_location_report


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
