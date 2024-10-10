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
OWNER_ORG = {
    'organizationName': 'ORG NAME HERE.',
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
# testdata pattern is ({middle}, {email}, {phone}, {phoneExtension}, {ptype}, {desc}, {suffix}, {data})
TEST_IND_DATA = [
    (None, None, None, None, None, None, None, OWNER_IND),
    (None, None, None, None, MhrPartyTypes.EXECUTOR, 'EXECUTOR DESC', "JR", OWNER_IND),
    (None, None, None, None, None, None, None, SUBMITTING_IND)
]
# testdata pattern is ({id}, {has_results})
TEST_ID_DATA = [
    (200000003, True),
    (300000000, False)
]
# testdata pattern is ({data}, {party_type}, {expected})
TEST_PARTY_TYPE_DATA = [
    (OWNER_IND, None, MhrPartyTypes.OWNER_IND),
    (OWNER_ORG, None, MhrPartyTypes.OWNER_BUS),
    (OWNER_IND, MhrPartyTypes.ADMINISTRATOR, MhrPartyTypes.ADMINISTRATOR),
    (OWNER_ORG, MhrPartyTypes.ADMINISTRATOR, MhrPartyTypes.ADMINISTRATOR),
    (OWNER_IND, MhrPartyTypes.EXECUTOR, MhrPartyTypes.EXECUTOR),
    (OWNER_ORG, MhrPartyTypes.EXECUTOR, MhrPartyTypes.EXECUTOR),
    (OWNER_IND, MhrPartyTypes.TRUSTEE, MhrPartyTypes.TRUSTEE),
    (OWNER_ORG, MhrPartyTypes.TRUSTEE, MhrPartyTypes.TRUSTEE),
    (OWNER_IND, MhrPartyTypes.TRUST, MhrPartyTypes.TRUST),
    (OWNER_ORG, MhrPartyTypes.TRUST, MhrPartyTypes.TRUST)
]
# testdata pattern is ({party_type}, {corp_num})
TEST_CORP_NUM_DATA = [
    (MhrPartyTypes.OWNER_IND, None),
    (MhrPartyTypes.OWNER_BUS, None),
    (MhrPartyTypes.OWNER_BUS, '0777777')
]


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_id(session, id, has_results):
    """Assert that find party by party ID contains all expected elements."""
    party: MhrParty = MhrParty.find_by_id(id)
    if has_results:
        assert party
        assert party.id == id
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
        assert len(parties) >= 1
        assert parties[0].party_type == MhrPartyTypes.SUBMITTING
    else:
        assert not parties


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_change_registration_id(session, id, has_results):
    """Assert that find party by change registration id contains all expected elements."""
    parties = MhrParty.find_by_change_registration_id(id)
    if has_results:
        assert parties
        assert len(parties) >= 1
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
        'ownerId': party.id,
        'status': party.status_type,
        'partyType': party.party_type,
        'organizationName': party.business_name,
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
    assert not party.compressed_name
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
        assert not party.compressed_name
        assert party.business_name or party.last_name
        if party.last_name:
            assert party.first_name
            assert not party.business_name
        else:
            assert not party.first_name
            assert not party.middle_name
            assert not party.last_name


@pytest.mark.parametrize('middle, email, phone, phone_extension, ptype, desc, suffix, data', TEST_IND_DATA)
def test_create_ind_from_json(session, middle, email, phone, phone_extension, ptype, desc, suffix, data):
    """Assert that creating an individual owner from json works as expected."""
    json_data = copy.deepcopy(data)
    if json_data.get('personName'):
        json_data['personName']['middle'] = middle
    elif json_data.get('individualName'):
        json_data['individualName']['middle'] = middle
    json_data['emailAddress'] = email
    json_data['phoneNumber'] = phone
    json_data['phoneExtension'] = phone_extension
    party_type = ptype if ptype else MhrPartyTypes.SUBMITTING
    if ptype:
        json_data['partyType'] = ptype
    if desc:
        json_data['description'] = desc
    if suffix:
        json_data['suffix'] = suffix
    party: MhrParty = MhrParty.create_from_json(json_data, party_type, 1000)
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
    if ptype:
        assert party.party_type == ptype
    if desc:
        assert party.description
    else:
        assert not party.description
    if suffix:
        assert party.suffix
    else:
        assert not party.suffix


@pytest.mark.parametrize('data, party_type, expected', TEST_PARTY_TYPE_DATA)
def test_party_type_from_json(session, data, party_type, expected):
    """Assert that setting an owner party type from json works as expected."""
    json_data = copy.deepcopy(data)
    if party_type:
        json_data['partyType'] = party_type
        p_type = party_type
    elif json_data.get('individualName'):
        p_type = MhrPartyTypes.OWNER_IND
    else:
        p_type = MhrPartyTypes.OWNER_BUS
    party: MhrParty = MhrParty.create_from_json(json_data, p_type, 1000)
    assert party
    assert party.party_type == expected


@pytest.mark.parametrize('party_type, corp_num', TEST_CORP_NUM_DATA)
def test_party_corp_num(session, party_type, corp_num):
    """Assert that creating a business owner with a corp number works as expected."""
    json_data = copy.deepcopy(OWNER_ORG) if party_type == MhrPartyTypes.OWNER_BUS else copy.deepcopy(OWNER_IND)
    json_data['partyType'] = party_type
    if corp_num:
        json_data['corpNumber'] = corp_num
    party: MhrParty = MhrParty.create_from_json(json_data, party_type, 1000)
    assert party
    assert party.party_type == party_type
    party_json = party.json
    if corp_num:
        assert party.corp_number == corp_num
        assert party_json.get('corpNumber') == corp_num
    else:
        assert not party_json.get('corpNumber')
