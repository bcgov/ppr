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

"""Tests to assure the LTSA description Model.

Test-Suite to ensure that the LTSA description Model is working as expected.
"""
import copy

import pytest

from mhr_api.models import LtsaDescription


# testdata pattern is ({id}, {pid}, {has_results})
TEST_ID_DATA = [
    (2, '005509807', True),
    (300000000, None, False)
]
# testdata pattern is ({pid}, {id}, {has_results})
TEST_PID_DATA = [
    ('005509807', 2, True),
    ('005-509-807', 2, True),
    ('995509807', 0, False)
]
# testdata pattern is ({pid}, {description}, {has_results})
TEST_UPDATE_DATA = [
    ('005509807', 'TEST UPDATE', True),
    ('005-509-807', 'TEST UPDATE', True),
    ('005509807', '', False),
    ('005509807', None, False),
    ('5509807', 'TEST UPDATE', False),
    ('995509807', 'TEST UPDATE', False)
]
# testdata pattern is ({pid}, {description}, {has_results})
TEST_SAVE_DATA = [
    ('XXXXXXXXX', 'TEST SAVE 1', True),
    ('YYY-YYY-YYY', 'TEST SAVE 2', True)
]


@pytest.mark.parametrize('id, pid, has_results', TEST_ID_DATA)
def test_find_by_id(session, id, pid, has_results):
    """Assert that find ltsa description by primary key contains all expected elements."""
    description: LtsaDescription = LtsaDescription.find_by_id(id)
    if has_results:
        assert description
        assert description.id == id
        assert description.pid_number == pid
        assert description.ltsa_description
        assert description.update_ts
    else:
        assert not description


@pytest.mark.parametrize('pid, id, has_results', TEST_PID_DATA)
def test_find_by_pid(session, pid, id, has_results):
    """Assert that find ltsa description by pid number contains all expected elements."""
    description: LtsaDescription = LtsaDescription.find_by_pid_number(pid)
    if has_results:
        assert description
        assert description.id == id
        assert description.pid_number == pid.replace('-', '')
        assert description.ltsa_description
        assert description.update_ts
    else:
        assert not description


@pytest.mark.parametrize('pid, ltsa_desc, has_results', TEST_UPDATE_DATA)
def test_update(session, pid, ltsa_desc, has_results):
    """Assert that updating an ltsa description by pid number works as expected."""
    description: LtsaDescription = LtsaDescription.update(pid, ltsa_desc)
    if has_results:
        assert description
        assert description.pid_number == pid.replace('-', '')
        assert description.ltsa_description == ltsa_desc
        assert description.update_ts
    else:
        assert not description


@pytest.mark.parametrize('pid, ltsa_desc, has_results', TEST_SAVE_DATA)
def test_save(session, pid, ltsa_desc, has_results):
    """Assert that updating an ltsa description by pid number works as expected."""
    description: LtsaDescription = LtsaDescription.create(pid, ltsa_desc)
    description.save()
    if has_results:
        assert description.id > 0
        assert description.pid_number == pid.replace('-', '')
        assert description.ltsa_description == ltsa_desc
        assert description.update_ts
    else:
        assert not description
