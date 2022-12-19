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

"""Tests to assure the MHR owner group Model.

Test-Suite to ensure that the MHR owner group Model is working as expected.
"""
import copy

import pytest
from registry_schemas.example_data.mhr import OWNER_GROUP

from mhr_api.models import MhrOwnerGroup
from mhr_api.models.type_tables import MhrTenancyTypes, MhrOwnerStatusTypes


# testdata pattern is ({id}, {has_results})
TEST_ID_DATA = [
    (200000000, True),
    (300000000, False)
]
TEST_GROUP = MhrOwnerGroup(id=1,
    group_id=1,
    status_type=MhrOwnerStatusTypes.ACTIVE,
    tenancy_type=MhrTenancyTypes.COMMON,
    interest='UNDIVIDED',
    interest_numerator=1,
    interest_denominator=2,
    tenancy_specified='Y')


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_id(session, id, has_results):
    """Assert that find group by primary key contains all expected elements."""
    group: MhrOwnerGroup = MhrOwnerGroup.find_by_id(id)
    if has_results:
        assert group
        assert group.id == 200000000
        assert group.registration_id == 200000000
        assert group.change_registration_id == 200000000
        assert group.tenancy_type == MhrTenancyTypes.COMMON
        assert group.status_type == MhrOwnerStatusTypes.ACTIVE
        assert group.tenancy_specified == 'Y'
        assert group.group_id == 1
        assert group.interest == 'UNDIVIDED'
        assert group.interest_numerator == 1
        assert group.interest_denominator == 2
    else:
        assert not group


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_registration_id(session, id, has_results):
    """Assert that find group by registration id contains all expected elements."""
    groups = MhrOwnerGroup.find_by_registration_id(id)
    if has_results:
        assert groups
        group = groups[0]
        assert group.id == 200000000
        assert group.registration_id == 200000000
        assert group.change_registration_id == 200000000
        assert group.tenancy_type == MhrTenancyTypes.COMMON
        assert group.status_type == MhrOwnerStatusTypes.ACTIVE
        assert group.tenancy_specified == 'Y'
        assert group.group_id == 1
        assert group.interest == 'UNDIVIDED'
        assert group.interest_numerator == 1
        assert group.interest_denominator == 2
    else:
        assert not groups

@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_change_registration_id(session, id, has_results):
    """Assert that find group by change registration id contains all expected elements."""
    groups = MhrOwnerGroup.find_by_change_registration_id(id)
    if has_results:
        assert groups
        group = groups[0]
        assert group.id == 200000000
        assert group.registration_id == 200000000
        assert group.change_registration_id == 200000000
        assert group.tenancy_type == MhrTenancyTypes.COMMON
        assert group.status_type == MhrOwnerStatusTypes.ACTIVE
        assert group.tenancy_specified == 'Y'
        assert group.group_id == 1
        assert group.interest == 'UNDIVIDED'
        assert group.interest_numerator == 1
        assert group.interest_denominator == 2
    else:
        assert not groups


def test_group_json(session):
    """Assert that the document model renders to a json format correctly."""
    group: MhrOwnerGroup = TEST_GROUP
    group_json = {
        'groupId': group.group_id,
        'type': group.tenancy_type,
        'status': group.status_type,
        'tenancySpecified': True,
        'interest': group.interest,
        'interestNumerator': group.interest_numerator,
        'interestDenominator': group.interest_denominator
    }
    assert group.json == group_json


def test_create_from_json(session):
    """Assert that the new MHR group is created from MH registration json data correctly."""
    json_data = copy.deepcopy(OWNER_GROUP)
    group: MhrOwnerGroup = MhrOwnerGroup.create_from_json(json_data, 1000)
    assert group
    assert group.group_id == 1
    assert group.registration_id == 1000
    assert group.change_registration_id == 1000
    assert group.tenancy_specified == 'Y'
    assert group.tenancy_type == MhrTenancyTypes.COMMON
    assert group.status_type == MhrOwnerStatusTypes.ACTIVE
    assert group.interest == 'UNDIVIDED'
    assert group.interest_numerator == 4
    assert group.interest_denominator == 5
