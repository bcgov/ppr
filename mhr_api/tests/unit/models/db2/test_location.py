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

import pytest

from flask import current_app

from mhr_api.models import Db2Location


# testdata pattern is ({exists}, {manuhome_id}, {park_name}, {pad}, {street_num}, {street}, {city}. {count})
TEST_DATA = [
    (True, 1, '', '', '4004', 'POPLAR AVENUE', 'FORT NELSON', 2),
    (False, 0, None, None, None, None, None, 0)
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
def test_find_by_manuhome_id_active(session, exists, manuhome_id, park_name, pad, street_num, street, city, count):
    """Assert that find the active location by manuhome id contains all expected elements."""
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


def test_location_json(session):
    """Assert that the location renders to a json format correctly."""
    location = Db2Location(location_id=1,
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
        'parkPad': location.park_pad,
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
        'leaveBc': location.leave_bc,
        'exceptPlan': location.except_plan,
        'dealerName': location.dealer_name,
        'additionalDescription': location.additional_description
    }
    assert location.json == test_json
