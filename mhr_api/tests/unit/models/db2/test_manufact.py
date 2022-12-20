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

"""Tests to assure the legacy DB2 Manufacturer Model.

Test-Suite to ensure that the legacy DB2 Manufacturer Model is working as expected.
"""

import pytest

from flask import current_app

from mhr_api.models import Db2Manufact
from mhr_api.models.db2 import address_utils


# testdata pattern is ({exists}, {id}, {park_name}, {pad}, {street_num}, {street}, {city}. {count})
TEST_DATA = [
    (True, 3, '', '', '4004', 'POPLAR AVENUE', 'FORT NELSON', 1),
    (False, 0, None, None, None, None, None, 0)
]
TEST_BCOL_DATA = [
    (True, '251256', '', '', '4004', 'POPLAR AVENUE', 'FORT NELSON', 1),
    (False, 0, None, None, None, None, None, 0)
]


@pytest.mark.parametrize('exists,id,park_name,pad,street_num,street,city,count', TEST_DATA)
def test_find_by_id(session, exists, id, park_name, pad, street_num, street, city, count):
    """Assert that find manufacturer by id contains all expected elements."""
    manufacturer: Db2Manufact = Db2Manufact.find_by_id(id)
    if exists:
        assert manufacturer
        assert manufacturer.id == id
        assert manufacturer.bcol_account_number
        assert manufacturer.dealer_name
        assert manufacturer.submitting_party_name
        assert manufacturer.submitting_party_phone
        assert manufacturer.submitting_party_address
        assert manufacturer.owner_name
        assert manufacturer.owner_phone_number
        assert manufacturer.street_number
        assert manufacturer.owner_address
        assert manufacturer.street_name
        assert manufacturer.town_city
        assert manufacturer.province
        assert manufacturer.manufacturer_name
        reg_json = manufacturer.json
        current_app.logger.debug(reg_json)
        assert reg_json.get('bcolAccountNumber') is not None
        assert reg_json.get('dealerName') is not None
        assert reg_json['submittingParty']
        assert reg_json['submittingParty']['businessName']
        assert reg_json['submittingParty']['phoneNumber']
        assert reg_json['submittingParty']['address']
        assert reg_json['submittingParty']['address']['street']
        assert reg_json['submittingParty']['address']['city']
        assert reg_json['submittingParty']['address']['region']
        assert reg_json['submittingParty']['address']['country']
        assert reg_json['submittingParty']['address']['postalCode']
        assert reg_json['owner']
        assert reg_json['owner']['businessName']
        assert reg_json['owner']['phoneNumber']
        assert reg_json['owner']['address']
        assert reg_json['owner']['address']['street']
        assert reg_json['owner']['address']['city']
        assert reg_json['owner']['address']['region']
        assert reg_json['owner']['address']['country']
        assert reg_json['owner']['address']['postalCode']
        assert reg_json.get('manufacturerName') is not None
    else:
        assert not manufacturer


@pytest.mark.parametrize('exists,bcol_num,park_name,pad,street_num,street,city,count', TEST_BCOL_DATA)
def test_find_by_bcol_account(session, exists, bcol_num, park_name, pad, street_num, street, city, count):
    """Assert that find manufacturer by BCOL account number contains all expected elements."""
    manufacturers = Db2Manufact.find_by_bcol_account(bcol_num)
    if exists:
        assert manufacturers
        assert len(manufacturers) == count
        for manufacturer in manufacturers:
            assert manufacturer.id
            assert manufacturer.bcol_account_number == bcol_num
            assert manufacturer.dealer_name
            assert manufacturer.submitting_party_name
            assert manufacturer.submitting_party_phone
            assert manufacturer.submitting_party_address
            assert manufacturer.owner_name
            assert manufacturer.owner_phone_number
            assert manufacturer.street_number
            assert manufacturer.owner_address
            assert manufacturer.street_name
            assert manufacturer.town_city
            assert manufacturer.province
            assert manufacturer.manufacturer_name
            reg_json = manufacturer.json
            current_app.logger.debug(reg_json)
            assert reg_json.get('bcolAccountNumber') is not None
            assert reg_json.get('dealerName') is not None
            assert reg_json['submittingParty']
            assert reg_json['submittingParty']['businessName']
            assert reg_json['submittingParty']['phoneNumber']
            assert reg_json['submittingParty']['address']
            assert reg_json['submittingParty']['address']['street']
            assert reg_json['submittingParty']['address']['city']
            assert reg_json['submittingParty']['address']['region']
            assert reg_json['submittingParty']['address']['country']
            assert reg_json['submittingParty']['address']['postalCode']
            assert reg_json['owner']
            assert reg_json['owner']['businessName']
            assert reg_json['owner']['phoneNumber']
            assert reg_json['owner']['address']
            assert reg_json['owner']['address']['street']
            assert reg_json['owner']['address']['city']
            assert reg_json['owner']['address']['region']
            assert reg_json['owner']['address']['country']
            assert reg_json['owner']['address']['postalCode']
            assert reg_json.get('manufacturerName') is not None

    else:
        assert not manufacturers


def test_manufact_json(session):
    """Assert that the manufacturer renders to a json format correctly."""
    manufacturer = Db2Manufact(bcol_account_number='123456',
                               dealer_name='dealerName',
                               submitting_party_name='submittingPartyName',
                               submitting_party_phone='6041234567',
                               submitting_party_address='106 1704 GOVERNMENT STREET              PENTICTON, BC V2A 6K3',
                               owner_name='ownerName',
                               owner_phone_number='2501234567',
                               owner_address='ownerAddress',
                               owner_postal_code='ownerCode',
                               street_number='1234',
                               street_name='streetName',
                               town_city='townCity',
                               province='BC',
                               manufacturer_name='manufacturerName')

    test_json = {
        'bcolAccountNumber': manufacturer.bcol_account_number,
        'dealerName': manufacturer.dealer_name,
        'submittingParty': {
            'businessName': manufacturer.submitting_party_name,
            'phoneNumber': manufacturer.submitting_party_phone,
            'address': address_utils.get_address_from_db2_manufact(manufacturer.submitting_party_address)
        },
        'owner': {
            'businessName': manufacturer.owner_name,
            'phoneNumber': manufacturer.owner_phone_number,
            'address': {
                'street': manufacturer.street_number + ' ' + manufacturer.street_name,
                'city': manufacturer.town_city,
                'region': manufacturer.province,
                'country': 'CA',
                'postalCode': manufacturer.owner_postal_code
            }
        },
        'manufacturerName': manufacturer.manufacturer_name
    }
    assert manufacturer.json == test_json
