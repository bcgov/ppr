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

"""Tests to assure the legacy DB2 Location Model.

Test-Suite to ensure that the legacy DB2 Location Model is working as expected.
"""
import copy

import pytest

from flask import current_app
from registry_schemas.example_data.mhr import REGISTRATION

from mhr_api.models import Db2Location, MhrRegistration


TEST_LOCATION = Db2Location(location_id=1,
    status='A',
    reg_document_id='1234',
    can_document_id='5678',
    street_number='1234',
    street_name='street name',
    town_city='town',
    province='BC',
    area='',
    jurisdiction='',
    roll_number='',
    park_name='LAZY WHEEL MOBILE HOME PARK',
    park_pad='37',
    pid_number='012777846',
    lot='54',
    parcel='A 1',
    block='',
    district_lot='1535',
    part_of='',
    section='N.E. 6',
    township='9',
    range='',
    meridian='',
    land_district='PEACE RIVER',
    plan='25262',
    tax_certificate='Y',
    leave_bc='N',
    except_plan='except',
    dealer_name='dealer',
    additional_description='additional')
# testdata pattern is ({exists}, {manuhome_id}, {park_name}, {pad}, {street_num}, {street}, {city}. {count})
TEST_DATA = [
    (True, 1, '', '', '4004', 'POPLAR AVENUE', 'FORT NELSON', 2),
    (False, 0, None, None, None, None, None, 0)
]
# testdata pattern is ({street_num}, {street_name}, {street_json})
TEST_ADDRESS_DATA = [
    ('4004', 'POPLAR AVENUE', '4004 POPLAR AVENUE'),
    ('101-40', '04 POPLAR AVENUE', '101-4004 POPLAR AVENUE')
]


@pytest.mark.parametrize('exists,manuhome_id,park_name,pad,street_num,street,city,count', TEST_DATA)
def test_find_by_manuhome_id(session, exists, manuhome_id, park_name, pad, street_num, street, city, count):
    """Assert that find locations by manuhome id contains all expected elements."""
    locations: Db2Location = Db2Location.find_by_manuhome_id(manuhome_id)
    if exists:
        assert locations
        assert len(locations) == count
        for location in locations:
            assert location.manuhome_id == manuhome_id
            assert location.location_id > 0
            assert location.status
            if location.status == 'A':
                assert location.street_number == street_num
                assert location.street_name == street
                assert location.town_city == city
                assert location.park_name == park_name
                assert location.park_pad == pad
            reg_json = location.registration_json
            current_app.logger.debug(reg_json)
            assert reg_json.get('parkName') is not None
            assert reg_json.get('pad') is not None
            assert reg_json.get('address')
            assert reg_json['address']['street']
            assert reg_json['address']['city']
            assert reg_json['address']['region']
            assert reg_json['address']['country']
            assert reg_json['address']['postalCode'] is not None

    else:
        assert not locations


@pytest.mark.parametrize('exists,manuhome_id,park_name,pad,street_num,street,city,count', TEST_DATA)
def test_find_by_manuhome_id(session, exists, manuhome_id, park_name, pad, street_num, street, city, count):
    """Assert that find locations by manuhome id contains all expected elements."""
    location: Db2Location = Db2Location.find_by_manuhome_id_active(manuhome_id)
    if exists:
        assert location.manuhome_id == manuhome_id
        assert location.location_id > 0
        assert location.status
        assert location.street_number == street_num
        assert location.street_name == street
        assert location.town_city == city
        assert location.park_name == park_name
        assert location.park_pad == pad
        assert location.reg_document_id
        assert location.can_document_id is not None
        assert location.province == 'BC'
        assert location.roll_number is not None
        assert location.area is not None
        assert location.jurisdiction is not None
        assert location.pid_number is not None
        assert location.lot is not None
        assert location.parcel is not None
        assert location.block is not None
        assert location.district_lot is not None
        assert location.part_of is not None
        assert location.section is not None
        assert location.township is not None
        assert location.range is not None
        assert location.meridian is not None
        assert location.land_district is not None
        assert location.plan is not None
        assert location.tax_certificate is not None
        assert location.tax_certificate_date is not None
        assert location.leave_bc is not None
        assert location.dealer_name is not None
        assert location.except_plan is not None
        assert location.additional_description is not None
        reg_json = location.registration_json
        current_app.logger.debug(reg_json)
        assert reg_json.get('parkName') is not None
        assert reg_json.get('pad') is not None
        assert reg_json.get('address')
        assert reg_json['address']['street']
        assert reg_json['address']['city']
        assert reg_json['address']['region']
        assert reg_json['address']['country']
        assert reg_json['address']['postalCode'] is not None
    else:
        assert not location


@pytest.mark.parametrize('street_num,street_name,street_json', TEST_ADDRESS_DATA)
def test_create_from_registration(session, street_num, street_name, street_json):
    """Assert that creating location address data from json works as expected."""
    json_data = copy.deepcopy(REGISTRATION)
    json_data['location']['address']['street'] = street_json
    registration: MhrRegistration = MhrRegistration(id=1)
    location: Db2Location = Db2Location.create_from_registration(registration, json_data)
    assert location.street_number == street_num
    assert location.street_name == street_name


@pytest.mark.parametrize('street_num,street_name,street_json', TEST_ADDRESS_DATA)
def test_registration_json(session, street_num, street_name, street_json):
    """Assert that creating location json for search from address data works as expected."""
    location = TEST_LOCATION
    location.street_number = street_num
    location.street_name = street_name
    json_data = location.registration_json
    assert json_data.get('address')
    assert json_data['address']['street'] == street_json


@pytest.mark.parametrize('street_num,street_name,street_json', TEST_ADDRESS_DATA)
def test_new_registration_json(session, street_num, street_name, street_json):
    """Assert that creating location json for new registrations from address data works as expected."""
    location = TEST_LOCATION
    location.street_number = street_num
    location.street_name = street_name
    json_data = location.new_registration_json
    assert json_data.get('address')
    assert json_data['address']['street'] == street_json


def test_location_json(session):
    """Assert that the location renders to a json format correctly."""
    location = TEST_LOCATION
    test_json = {
        'locationId': location.location_id,
        'status': location.status,
        'registrationDocumentId': location.reg_document_id,
        'canDocumentId': location.can_document_id,
        'streetNumber': location.street_number,
        'streetName': location.street_name,
        'townCity': location.town_city,
        'province': location.province,
        'area': location.area,
        'jurisdiction': location.jurisdiction,
        'rollNumber': location.roll_number,
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
        'taxCertificate': location.tax_certificate,
        'leaveProvince': location.leave_bc,
        'exceptionPlan': location.except_plan,
        'dealerName': location.dealer_name,
        'additionalDescription': location.additional_description
    }
    assert location.json == test_json
