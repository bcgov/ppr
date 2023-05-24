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

"""Tests to assure the MHR manufacturer Model.

Test-Suite to ensure that the MHR manufacturer Model is working as expected.
"""
from flask import current_app

import pytest

from mhr_api.models import Address, MhrManufacturer, MhrParty
from  mhr_api.models.type_tables import MhrPartyTypes


# testdata pattern is ({id}, {has_results})
TEST_ID_DATA = [
    (200000000, True),
    (300000000, False)
]
# testdata pattern is ({reg_id}, {has_results})
TEST_REGISTRATION_ID_DATA = [
    (200000001, True),
    (300000000, False)
]
# testdata pattern is ({account_id}, {has_results})
TEST_ACCOUNT_ID_DATA = [
    ('2523', True),
    ('JUNK', False)
]
MANUFACTURER_JSON = {
  'submittingParty': {
    'businessName': 'SUB REAL ENGINEERED HOMES INC',
    'address': {
      'street': '1704 GOVERNMENT ST.',
      'city': 'PENTICTON',
      'region': 'BC',
      'postalCode': 'V2A 7A1',
      'country': 'CA'
    },
    'phoneNumber': '2507701067'
  },
  'ownerGroups': [
    {
      'groupId': 1,
      'owners': [
        {
          'businessName': 'OWNER REAL ENGINEERED HOMES INC',
          'partyType': 'OWNER_BUS',
          'address': {
            'street': '1704 GOVERNMENT ST.',
            'city': 'PENTICTON',
            'region': 'BC',
            'postalCode': 'V2A 7A1',
            'country': 'CA'
          }
        }
      ],
      'type': 'SOLE'
    }
  ],
  'location': {
    'locationType': 'MANUFACTURER',
    'dealerName': 'DEALER REAL ENGINEERED HOMES INC',
    'address': {
      'street': '1704 GOVERNMENT ST.',
      'city': 'PENTICTON',
      'region': 'BC',
      'postalCode': 'V2A 7A1',
      'country': 'CA'
    },
    'leaveProvince': False
  },
  'description': {
    'manufacturer': 'REAL ENGINEERED HOMES INC',
  }
}


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_id(session, id, has_results):
    """Assert that find manufacturer by primary key contains all expected elements."""
    manufacturer: MhrManufacturer = MhrManufacturer.find_by_id(id)
    if has_results:
        assert manufacturer
        assert manufacturer.id == id
        assert manufacturer.registration_id
        assert manufacturer.account_id
        assert manufacturer.manufacturer_name
        assert manufacturer.submitting_party
        assert manufacturer.submitting_party.address
        assert manufacturer.owner
        assert manufacturer.owner.address
        assert manufacturer.dealer
        assert manufacturer.dealer.address
    else:
        assert not manufacturer


@pytest.mark.parametrize('reg_id, has_results', TEST_REGISTRATION_ID_DATA)
def test_find_by_registration_id(session, reg_id, has_results):
    """Assert that find manufacturer by registration id contains all expected elements."""
    manufacturer: MhrManufacturer = MhrManufacturer.find_by_registration_id(reg_id)
    if has_results:
        assert manufacturer
        assert manufacturer.id
        assert manufacturer.registration_id == reg_id
        assert manufacturer.account_id
        assert manufacturer.manufacturer_name
        assert manufacturer.submitting_party
        assert manufacturer.submitting_party.address
        assert manufacturer.owner
        assert manufacturer.owner.address
        assert manufacturer.dealer
        assert manufacturer.dealer.address
    else:
        assert not manufacturer


@pytest.mark.parametrize('account_id, has_results', TEST_ACCOUNT_ID_DATA)
def test_find_by_account_id(session, account_id, has_results):
    """Assert that find manufacturer by account id contains all expected elements."""
    manufacturer: MhrManufacturer = MhrManufacturer.find_by_account_id(account_id)
    if has_results:
        assert manufacturer
        assert manufacturer.id
        assert manufacturer.registration_id
        assert manufacturer.account_id == account_id
        assert manufacturer.manufacturer_name
        assert manufacturer.submitting_party
        assert manufacturer.submitting_party.address
        assert manufacturer.owner
        assert manufacturer.owner.address
        assert manufacturer.dealer
        assert manufacturer.dealer.address
        json_data = manufacturer.json
        assert json_data
        assert json_data.get('submittingParty')
        assert json_data['submittingParty'].get('businessName')
        assert json_data['submittingParty'].get('address')
        assert json_data['submittingParty'].get('phoneNumber')
        assert json_data.get('ownerGroups')
        assert json_data['ownerGroups'][0].get('groupId') == 1
        assert json_data['ownerGroups'][0].get('type') == 'SOLE'
        assert json_data['ownerGroups'][0].get('owners')
        owner = json_data['ownerGroups'][0]['owners'][0]
        assert owner.get('businessName')
        assert owner.get('address')
        assert json_data.get('location')
        assert json_data['location'].get('locationType')
        assert json_data['location'].get('dealerName')
        assert json_data['location'].get('address')
        assert json_data.get('description')
        assert json_data['description'].get('manufacturer')
    else:
        assert not manufacturer


def test_manufacturer_json(session):
    """Assert that the manufacturer model renders to a json format correctly."""
    sub_address: Address = Address.create_from_json(MANUFACTURER_JSON['submittingParty'].get('address'))
    owner_address: Address = Address.create_from_json(MANUFACTURER_JSON['ownerGroups'][0]['owners'][0].get('address'))
    dealer_address: Address = Address.create_from_json(MANUFACTURER_JSON['location'].get('address'))
    sub_party: MhrParty = MhrParty(id=1, 
                                   party_type=MhrPartyTypes.SUBMITTING,
                                   business_name=MANUFACTURER_JSON['submittingParty'].get('businessName'),
                                   address=sub_address,
                                   phone_number=MANUFACTURER_JSON['submittingParty'].get('phoneNumber'))
    owner: MhrParty = MhrParty(id=2, 
                               party_type=MhrPartyTypes.OWNER_BUS,
                               business_name=MANUFACTURER_JSON['ownerGroups'][0]['owners'][0].get('businessName'),
                               address=owner_address)
    dealer: MhrParty = MhrParty(id=3, 
                                party_type=MhrPartyTypes.MANUFACTURER,
                                business_name=MANUFACTURER_JSON['location'].get('dealerName'),
                                address=dealer_address)
    manufacturer: MhrManufacturer = MhrManufacturer(id=1,
                                                    registration_id=1,
                                                    submitting_party_id=1,
                                                    owner_party_id=2,
                                                    dealer_party_id=3,
                                                    submitting_party=sub_party,
                                                    owner=owner,
                                                    dealer=dealer)
    manufacturer.manufacturer_name=MANUFACTURER_JSON['description'].get('manufacturer')
    current_app.logger.debug(manufacturer.json)
    assert MANUFACTURER_JSON == manufacturer.json
