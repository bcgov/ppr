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
from datetime import timedelta as _timedelta

import pytest

from flask import current_app

from mhr_api.models import utils as model_utils, registration_utils as reg_utils


# testdata pattern is ({start_ts}, {end_ts})
TEST_DATA_MANUFACTURER_MHREG = [
    ('2023-05-25T07:01:00+00:00', '2023-05-26T07:01:00+00:00'),
    (None, '2023-05-26T07:01:00+00:00'),
    ('2023-05-25T07:01:00+00:00', None),
    (None, None)
]
# testdata pattern is ({start_ts}, {end_ts})
TEST_DATA_MANUFACTURER_MHREG_UPDATE = [
    ('2023-05-25T07:01:00+00:00', '2023-05-26T07:01:00+00:00'),
    (None, None)
]
# testdata pattern is ({description}, {mhr_number}, {ppr_reg_type})
TEST_DATA_PPR_REG_TYPE = [
    ('Valid request no lien', '100000', None)
]
# testdata pattern is ({description}, {mhr_number}, {valid})
TEST_DATA_MHR_CHECK = [
    ('Valid', '000899', True),
    ('Invalid exists', '000900', False),
    ('Invalid too high', '999900', False)
]


@pytest.mark.parametrize('start_ts,end_ts', TEST_DATA_MANUFACTURER_MHREG)
def test_get_batch_manufacturer_reg_report_data(session, start_ts, end_ts):
    """Assert that fetching manufacturer MHREG data by optional timestamp range works as expected."""
    results_json = reg_utils.get_batch_manufacturer_reg_report_data(start_ts, end_ts)
    if results_json:
        for result in results_json:
            assert result.get('registrationId')
            assert result.get('accountId')
            assert result.get('reportId')
            assert result.get('reportData')
            assert 'batchStorageUrl' in result


def test_get_batch_manufacturer_reg_report_name(session):
    """Assert that fetching manufacturer MHREG data by optional timestamp range works as expected."""
    now_ts = model_utils.now_ts()
    time = str(now_ts.hour) + '_' + str(now_ts.minute)
    test_name: str = reg_utils.BATCH_DOC_NAME_MANUFACTURER_MHREG.format(time=time)
    storage_name: str = reg_utils.get_batch_storage_name_manufacturer_mhreg()
    assert storage_name.find(test_name) > -1


@pytest.mark.parametrize('start_ts,end_ts', TEST_DATA_MANUFACTURER_MHREG_UPDATE)
def test_update_manufacturer_reg_report_batch_url(session, start_ts, end_ts):
    """Assert that batch updating of the registration report batch storage url works as expected."""
    results_json = reg_utils.get_batch_manufacturer_reg_report_data(start_ts, end_ts)
    if results_json:
        batch_url: str = reg_utils.get_batch_storage_name_manufacturer_mhreg()
        update_count: int = reg_utils.update_reg_report_batch_url(results_json, batch_url)
        assert update_count > 0


@pytest.mark.parametrize('desc, mhr_number, ppr_reg_type', TEST_DATA_PPR_REG_TYPE)
def test_validate_ppr_reg_type(session, desc, mhr_number, ppr_reg_type):
    """Assert that the PPR reg type query works as expected."""
    reg_type = reg_utils.get_ppr_registration_type(mhr_number)
    assert reg_type == ppr_reg_type


@pytest.mark.parametrize('desc, mhr_number, valid', TEST_DATA_MHR_CHECK)
def test_validate_mhr_number(session, desc, mhr_number, valid):
    """Assert that the staff new MH MHR number check works as expected."""
    result: bool = reg_utils.validate_mhr_number(mhr_number)
    assert result == valid
