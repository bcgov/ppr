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

"""Tests to assure the MHR section Model.

Test-Suite to ensure that the MHR section Model is working as expected.
"""
import copy

import pytest
from registry_schemas.example_data.mhr import DESCRIPTION

from mhr_api.models import MhrSection
from mhr_api.models.type_tables import MhrStatusTypes


# testdata pattern is ({id}, {has_results})
TEST_ID_DATA = [
    (200000000, True),
    (300000000, False)
]
TEST_SECTION = MhrSection(id=1,
                          registration_id=1,
                          change_registration_id=1,
                          status_type=MhrStatusTypes.ACTIVE,
                          compressed_key='002783',
                          serial_number='003000ZA002783A',
                          length_feet=60,
                          width_feet=14,
                          length_inches=10,
                          width_inches=11)


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_id(session, id, has_results):
    """Assert that find section by section ID contains all expected elements."""
    section: MhrSection = MhrSection.find_by_id(id)
    if has_results:
        assert section
        assert section.id == 200000000
        assert section.registration_id == 200000000
        assert section.change_registration_id == 200000000
        assert section.status_type == MhrStatusTypes.ACTIVE
        assert section.compressed_key == '002783'
        assert section.serial_number == '003000ZA002783A'
        assert section.length_feet == 60
        assert section.width_feet == 14
        assert section.length_inches == 10
        assert section.width_inches == 11
    else:
        assert not section


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_registration_id(session, id, has_results):
    """Assert that find sections by registration id contains all expected elements."""
    sections = MhrSection.find_by_registration_id(id)
    if has_results:
        assert sections
        assert len(sections) == 1
        assert sections[0].id == 200000000
        assert sections[0].registration_id == 200000000
        assert sections[0].change_registration_id == 200000000
        assert sections[0].status_type == MhrStatusTypes.ACTIVE
    else:
        assert not sections


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_change_registration_id(session, id, has_results):
    """Assert that find sections by change registration id contains all expected elements."""
    sections = MhrSection.find_by_change_registration_id(id)
    if has_results:
        assert sections
        assert len(sections) == 1
        assert sections[0].id == 200000000
        assert sections[0].registration_id == 200000000
        assert sections[0].change_registration_id == 200000000
        assert sections[0].status_type == MhrStatusTypes.ACTIVE
    else:
        assert not sections


def test_section_json(session):
    """Assert that the section model renders to a json format correctly."""
    section: MhrSection = TEST_SECTION
    test_json = {
        'serialNumber': section.serial_number,
        'lengthFeet': section.length_feet,
        'widthFeet': section.width_feet,
        'lengthInches': section.length_inches,
        'widthInches': section.width_inches
    }
    assert section.json == test_json


def test_create_from_json(session):
    """Assert that the new MHR section is created from json data correctly."""
    json_data = copy.deepcopy(DESCRIPTION)
    section_data = json_data.get('sections')
    section: MhrSection = MhrSection.create_from_json(section_data[0], 1000)
    assert section
    assert section.registration_id == 1000
    assert section.change_registration_id == 1000
    assert section.status_type == MhrStatusTypes.ACTIVE
    assert section.serial_number == '52D70556'
    assert section.length_feet == 52
    assert section.width_feet == 12
    assert section.length_inches == 0
    assert section.width_inches == 0
    assert section.compressed_key == '070556'
