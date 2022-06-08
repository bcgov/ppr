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

"""Tests to assure the legacy DB2 Cmpserno Model.

Test-Suite to ensure that the legacy DB2 Cmpserno Model is working as expected.
"""
import pytest

from flask import current_app

from mhr_api.models import Db2Cmpserno, utils as model_utils


# testdata pattern is ({exists}, {manuhome_id}, {compressed_id})
TEST_DATA = [
    (True, 1, 1),
    (False, 0, 0)
]


@pytest.mark.parametrize('exists,manuhome_id,compressed_id', TEST_DATA)
def test_find_by_manuhome_id(session, exists, manuhome_id, compressed_id):
    """Assert that find compressed serial number key by manuhome id contains all expected elements."""
    cmpserno = Db2Cmpserno.find_by_manuhome_id(manuhome_id)
    if exists:
        assert cmpserno
        for key in cmpserno:
            assert key.manuhome_id == manuhome_id
            assert key.compressed_id == compressed_id
            assert key.compressed_key
            current_app.logger.debug(f'Compressed key=${key.compressed_key}$')
    else:
        assert not cmpserno


def test_compressed_key(session):
    """Assert that setting a compressed serial number key by manuhome id works as expected."""
    keys = Db2Cmpserno.find_by_manuhome_id(47715)
    if keys:
        cmpserno: Db2Cmpserno = keys[0]
        cmpserno.compressed_key =  model_utils.get_serial_number_key('123')
        current_app.logger.debug(f'Updated key for {cmpserno.json}')
        cmpserno.save()
