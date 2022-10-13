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

"""Tests to assure the MHR location Model.

Test-Suite to ensure that the MHR location Model is working as expected.
"""
import copy

import pytest
from registry_schemas.example_data.mhr import REGISTRATION

from mhr_api.models import MhrLocation
from mhr_api.models.type_tables import MhrLocationTypes, MhrStatusTypes


# testdata pattern is ({id}, {has_results})
TEST_ID_DATA = [
    (200000000, True),
    (300000000, False)
]
LTSA_DESCRIPTION = 'LOT 1 DISTRICT LOT 16 QUEEN CHARLOTTE DISTRICT PLAN PRP14213'
TEST_LOCATION = MhrLocation(id=1,
    location_type=MhrLocationTypes.OTHER,
    status_type=MhrStatusTypes.ACTIVE,
    ltsa_description=LTSA_DESCRIPTION,
    park_name='LAZY WHEEL MOBILE HOME PARK',
    park_pad='37',
    pid_number='012777846',
    lot='54',
    parcel='A 1',
    block='block',
    district_lot='1535',
    part_of='part',
    section='N.E. 6',
    township='9',
    range='range',
    meridian='merid',
    land_district='PEACE RIVER',
    plan='25262',
    tax_certification='Y',
    leave_province='N',
    exception_plan='except',
    dealer_name='dealer',
    additional_description='additional',
    address_id=1)


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_id(session, id, has_results):
    """Assert that find location by location ID contains all expected elements."""
    location: MhrLocation = MhrLocation.find_by_id(id)
    if has_results:
        assert location
        assert location.id == 200000000
        assert location.registration_id == 200000000
        assert location.change_registration_id == 200000000
        assert location.address_id > 0
        assert location.location_type == MhrLocationTypes.OTHER
        assert location.status_type == MhrStatusTypes.ACTIVE
        assert location.ltsa_description
        assert location.additional_description == 'additional'
        assert location.dealer_name == 'dealer'
        assert location.exception_plan == 'except'
        assert location.leave_province == 'N'
        assert location.tax_certification == 'Y'
        assert location.tax_certification_date
        assert location.park_name == 'park name'
        assert location.park_pad == 'pad'
        assert location.pid_number == '123456789'
        assert location.lot == 'lot'
        assert location.parcel == 'parcel'
        assert location.block == 'block'
        assert location.district_lot == 'dist lot'
        assert location.part_of == 'part of'
        assert location.section == 'section'
        assert location.township == 'town'
        assert location.range == 'range'
        assert location.meridian == 'merid'
        assert location.land_district == 'land district'
        assert location.plan == 'plan'
    else:
        assert not location


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_registration_id(session, id, has_results):
    """Assert that find location by registration id contains all expected elements."""
    locations = MhrLocation.find_by_registration_id(id)
    if has_results:
        assert locations
        assert len(locations) == 1
        assert locations[0].location_type == MhrLocationTypes.OTHER
    else:
        assert not locations


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_change_registration_id(session, id, has_results):
    """Assert that find location by change registration id contains all expected elements."""
    locations = MhrLocation.find_by_change_registration_id(id)
    if has_results:
        assert locations
        assert len(locations) == 1
        assert locations[0].location_type == MhrLocationTypes.OTHER
    else:
        assert not locations


def test_location_json(session):
    """Assert that the location model renders to a json format correctly."""
    location: MhrLocation = TEST_LOCATION
    location_json = {
        'locationId': location.id,
        'status': location.status_type,
        'locationType': location.location_type,
        'legalDescription': location.ltsa_description,
        'parkName': location.park_name,
        'pad': location.park_pad,
        'pidNumber': location.pid_number,
        'lot': location.lot,
        'parcel': location.parcel,
        'block': location.block,
        'districtLot': location.district_lot,
        'partOf': location.part_of,
        'section': location.section,
        'township': location.township,
        'range': location.range,
        'meridian': location.meridian,
        'landDistrict': location.land_district,
        'plan': location.plan,
        'leaveProvince': False,
        'taxCertificate': True,
        'exceptionPlan': location.exception_plan,
        'dealerName': location.dealer_name,
        'additionalDescription': location.additional_description
    }
    assert location.json == location_json


def test_create_from_json(session):
    """Assert that the new MHR location is created from json data correctly."""
    json_data = copy.deepcopy(REGISTRATION)
    loc_json = json_data.get('location')
    loc_json['locationType'] = MhrLocationTypes.MH_PARK
    loc_json['legalDescription'] = LTSA_DESCRIPTION
    location: MhrLocation = MhrLocation.create_from_json(loc_json, 1000)
    assert location
    assert location.registration_id == 1000
    assert location.change_registration_id == 1000
    assert location.location_type == MhrLocationTypes.MH_PARK
    assert location.status_type == MhrStatusTypes.ACTIVE
    assert location.ltsa_description == LTSA_DESCRIPTION
    assert location.park_name
    assert location.park_pad
    assert location.address
    assert location.dealer_name
