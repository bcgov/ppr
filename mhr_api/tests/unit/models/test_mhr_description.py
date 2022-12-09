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

"""Tests to assure the MHR description Model.

Test-Suite to ensure that the MHR description Model is working as expected.
"""
import copy

import pytest
from registry_schemas.example_data.mhr import DESCRIPTION

from mhr_api.models import MhrDescription
from mhr_api.models.type_tables import MhrStatusTypes


# testdata pattern is ({id}, {has_results})
TEST_ID_DATA = [
    (200000000, True),
    (300000000, False)
]
TEST_DESCRIPTION = MhrDescription(id=1,
                                  registration_id=1,
                                  change_registration_id=1,
                                  status_type=MhrStatusTypes.ACTIVE,
                                  csa_number='77777',
                                  csa_standard='1234',
                                  number_of_sections=1,
                                  square_feet=2000,
                                  year_made=2015,
                                  circa='N',
                                  manufacturer_name='manufacturer',
                                  make='make',
                                  model='model',
                                  engineer_name='engineerName',
                                  rebuilt_remarks='rebuiltRemarks',
                                  other_remarks='otherRemarks')


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_id(session, id, has_results):
    """Assert that find description by description ID contains all expected elements."""
    description: MhrDescription = MhrDescription.find_by_id(id)
    if has_results:
        assert description
        assert description.id == 200000000
        assert description.registration_id == 200000000
        assert description.change_registration_id == 200000000
        assert description.status_type == MhrStatusTypes.ACTIVE
        assert description.csa_number == '7777700000'
        assert description.csa_standard == '1234'
        assert description.number_of_sections == 1
        assert description.circa == 'Y'
        assert description.square_feet == 2000
        assert description.year_made == 2015
        assert description.engineer_name == 'engineer name'
        assert description.engineer_date
        assert description.make == 'make'
        assert description.model == 'model'
        assert description.manufacturer_name == 'manufacturer'
        assert description.rebuilt_remarks == 'rebuilt'
        assert description.other_remarks == 'other'
    else:
        assert not description


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_registration_id(session, id, has_results):
    """Assert that find descriptions by registration id contains all expected elements."""
    descriptions = MhrDescription.find_by_registration_id(id)
    if has_results:
        assert descriptions
        assert len(descriptions) == 1
        assert descriptions[0].id == 200000000
        assert descriptions[0].registration_id == 200000000
        assert descriptions[0].change_registration_id == 200000000
        assert descriptions[0].status_type == MhrStatusTypes.ACTIVE
    else:
        assert not descriptions


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_change_registration_id(session, id, has_results):
    """Assert that find description by change registration id contains all expected elements."""
    description = MhrDescription.find_by_change_registration_id(id)
    if has_results:
        assert description
        assert description.id == 200000000
        assert description.registration_id == 200000000
        assert description.change_registration_id == 200000000
        assert description.status_type == MhrStatusTypes.ACTIVE
    else:
        assert not description


def test_description_json(session):
    """Assert that the description model renders to a json format correctly."""
    description: MhrDescription = TEST_DESCRIPTION
    description_json = {
        'status': description.status_type,
        'sectionCount': description.number_of_sections,
        'baseInformation': {
            'make': description.make,
            'model': description.model,
            'circa': False,
            'year': description.year_made
        },
        'csaNumber': description.csa_number,
        'csaStandard': description.csa_standard,
        'squareFeet': description.square_feet,
        'manufacturer': description.manufacturer_name,
        'engineerName': description.engineer_name,
        'rebuiltRemarks': description.rebuilt_remarks,
        'otherRemarks': description.other_remarks
    }
    assert description.json == description_json


def test_create_from_json(session):
    """Assert that the new MHR description is created from json data correctly."""
    json_data = copy.deepcopy(DESCRIPTION)
    description: MhrDescription = MhrDescription.create_from_json(json_data, 1000)
    assert description
    assert description.registration_id == 1000
    assert description.change_registration_id == 1000
    assert description.status_type == MhrStatusTypes.ACTIVE
    assert description.number_of_sections
    assert description.csa_number
    assert description.csa_standard
    assert description.engineer_date
    assert description.engineer_name
    assert description.manufacturer_name
    assert description.rebuilt_remarks
    assert description.other_remarks
    assert description.year_made
    assert description.make
    assert description.model
