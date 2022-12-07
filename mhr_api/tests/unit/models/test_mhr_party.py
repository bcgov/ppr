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

"""Tests to assure the MHR Party Model.

Test-Suite to ensure that the MHR Party Model is working as expected.
"""
import copy

import pytest
from registry_schemas.example_data.mhr import REGISTRATION

from mhr_api.models import MhrParty
from mhr_api.models.type_tables import MhrPartyTypes, MhrOwnerStatusTypes


OWNER_IND = {
    'individualName': {
        'first': 'JANE',
        'middle': 'M',
        'last': 'SMITH'
    },
    'address': {
    'street': '3122B LYNNLARK PLACE',
    'city': 'VICTORIA',
    'region': 'BC',
    'postalCode': ' ',
    'country': 'CA'
    },
    'emailAddress': 'bsmith@abc-search.com',
    'phoneNumber': '6041234567',
    'phoneExtension': '546'
}
SUBMITTING_IND = {
    'personName': {
        'first': 'JANE',
        'middle': 'M',
        'last': 'SMITH'
    },
    'address': {
      'street': '222 SUMMER STREET',
      'city': 'VICTORIA',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V8W 2V8'
    },
    'emailAddress': 'bsmith@abc-search.com',
    'phoneNumber': '6041234567',
    'phoneExtension': '546'
}
# testdata pattern is ({middle}, {email}, {phone}, {phoneExtension}, {data})
TEST_IND_DATA = [
    (None, None, None, None, OWNER_IND),
    (None, None, None, None, SUBMITTING_IND)
]
# testdata pattern is ({id}, {has_results})
TEST_ID_DATA = [
    (200000000, True),
    (300000000, False)
]


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_id(session, id, has_results):
    """Assert that find party by party ID contains all expected elements."""
    party: MhrParty = MhrParty.find_by_id(id)
    if has_results:
        assert party
        assert party.id == 200000000
        assert party.address_id > 0
        assert party.party_type == MhrPartyTypes.SUBMITTING
        assert party.status_type == MhrOwnerStatusTypes.ACTIVE
        assert not party.first_name
        assert not party.middle_name
        assert not party.last_name
        assert party.business_name
        assert party.compressed_name
        assert party.registration_id
        assert party.change_registration_id
        assert party.email_id
        assert party.phone_number
    else:
        assert not party


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_registration_id(session, id, has_results):
    """Assert that find party by registration id contains all expected elements."""
    parties = MhrParty.find_by_registration_id(id)
    if has_results:
        assert parties
        assert len(parties) == 1
        assert parties[0].party_type == MhrPartyTypes.SUBMITTING
    else:
        assert not parties


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_change_registration_id(session, id, has_results):
    """Assert that find party by change registration id contains all expected elements."""
    parties = MhrParty.find_by_change_registration_id(id)
    if has_results:
        assert parties
        assert len(parties) == 1
        assert parties[0].party_type == MhrPartyTypes.SUBMITTING
    else:
        assert not parties


def test_party_json(session):
    """Assert that the party model renders to a json format correctly."""
    party = MhrParty(
        id=1000,
        party_type = MhrPartyTypes.OWNER_BUS,
        status_type = MhrOwnerStatusTypes.ACTIVE,
        business_name='BUSINESS',
        email_id='test@gmail.com',
        phone_number = '2501234567',
        phone_extension = '1234',
        registration_id=1000,
        address_id=1000
    )
    party_json = {
        'partyId': party.id,
        'status': party.status_type,
        'businessName': party.business_name,
        'emailAddress': party.email_id,
        'phoneNumber': party.phone_number,
        'phoneExtension': party.phone_extension
    }
    assert party.json == party_json


def test_create_from_json(session):
    """Assert that the new MHR party is created from json data correctly."""
    json_data = copy.deepcopy(REGISTRATION)
    party: MhrParty = MhrParty.create_from_json(json_data.get('submittingParty'), MhrPartyTypes.SUBMITTING, 1000)
    assert party
    assert party.registration_id == 1000
    assert party.change_registration_id == 1000
    assert party.party_type == MhrPartyTypes.SUBMITTING
    assert party.status_type == MhrOwnerStatusTypes.ACTIVE
    assert party.compressed_name
    assert party.business_name or party.last_name
    if party.last_name:
        assert party.first_name
        assert not party.business_name
    else:
        assert not party.first_name
        assert not party.middle_name
        assert not party.last_name


def test_create_from_registration_json(session):
    """Assert that the new MHR registration parties are created from json data correctly."""
    json_data = copy.deepcopy(REGISTRATION)
    parties = MhrParty.create_from_registration_json(json_data, 1000)
    assert parties
    assert len(parties) == 1
    for party in parties:
        assert party.registration_id == 1000
        assert party.change_registration_id == 1000
        assert party.party_type in MhrPartyTypes
        assert party.status_type in MhrOwnerStatusTypes
        assert party.compressed_name
        assert party.business_name or party.last_name
        if party.last_name:
            assert party.first_name
            assert not party.business_name
        else:
            assert not party.first_name
            assert not party.middle_name
            assert not party.last_name


@pytest.mark.parametrize('middle, email, phone, phone_extension, data', TEST_IND_DATA)
def test_create_ind_from_json(session, middle, email, phone, phone_extension, data):
    json_data = copy.deepcopy(data)
    if json_data.get('personName'):
        json_data['personName']['middle'] = middle
    elif json_data.get('individualName'):
        json_data['individualName']['middle'] = middle
    json_data['emailAddress'] = email
    json_data['phoneNumber'] = phone
    json_data['phoneExtension'] = phone_extension
    party: MhrParty = MhrParty.create_from_json(json_data, MhrPartyTypes.SUBMITTING, 1000)
    assert party
    if middle:
        assert party.middle_name
    else:
        assert not party.middle_name
    if email:
        assert party.email_id
    else:
        assert not party.email_id
    if phone:
        assert party.phone_number
    else:
        assert not party.phone_number
    if phone_extension:
        assert party.phone_extension
    else:
        assert not party.phone_extension
