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

"""Tests to assure the Party Model.

Test-Suite to ensure that the Party Model is working as expected.
"""
import copy

from registry_schemas.example_data.ppr import FINANCING_STATEMENT

from ppr_api.models import Party


def test_find_by_id(session):
    """Assert that find party by party ID contains all expected elements."""
    party = Party.find_by_id(200000000)
    assert party
    assert party.id == 200000000
    assert party.address_id
    assert party.party_type == 'RG'
    assert party.first_name
    assert party.middle_initial
    assert party.last_name
    assert party.registration_id
    assert not party.branch_id
    assert not party.business_name
    assert not party.birth_date
    assert not party.registration_id_end


def test_find_by_id_client(session):
    """Assert that find party by party ID for a client party contains all expected elements."""
    party = Party.find_by_id(200000004)
    assert party
    assert party.party_type == 'SP'
    assert party.id == 200000004
    assert party.registration_id
    assert not party.first_name
    assert not party.middle_initial
    assert not party.last_name
    assert not party.birth_date
    assert not party.registration_id_end

    json_data = party.json
    assert json_data['code'] == '200000000'
    assert json_data['businessName']
    assert json_data['address']


def test_find_by_financing_id(session):
    """Assert that find party by registration number contains all expected elements."""
    parties = Party.find_by_financing_id(200000000)
    assert parties
    assert len(parties) >= 5
    assert parties[0].party_type == 'RG'
    assert parties[1].party_type == 'DI'
    assert parties[2].party_type == 'DB'
    assert parties[3].party_type == 'SP'
    assert parties[4].party_type == 'SP'


def test_find_by_registration_id(session):
    """Assert that find party by registration id contains all expected elements."""
    parties = Party.find_by_registration_id(200000000)
    assert parties
    assert len(parties) == 5
    assert parties[0].party_type == 'RG'
    assert parties[1].party_type == 'DI'
    assert parties[2].party_type == 'DB'
    assert parties[3].party_type == 'SP'
    assert parties[4].party_type == 'SP'


def test_find_by_id_invalid(session):
    """Assert that find party by non-existent party ID returns the expected result."""
    party = Party.find_by_id(300000000)
    assert not party


def test_find_by_financing_id_invalid(session):
    """Assert that find party by non-existent financing statement ID returns the expected result."""
    party = Party.find_by_financing_id(300000000)
    assert not party


def test_find_by_reg_id_invalid(session):
    """Assert that find party by non-existent registration id eturns the expected result."""
    parties = Party.find_by_registration_id(300000000)
    assert not parties


def test_party_json(session):
    """Assert that the party model renders to a json format correctly."""
    party = Party(
        id=1000,
        first_name='FIRST',
        middle_initial='MIDDLE',
        last_name='LAST',
        business_name='BUSINESS',
        registration_id=1000,
        address_id=1000
    )

    party_json = {
        'partyId': party.id,
        'businessName': party.business_name,
        'personName': {
            'first': party.first_name,
            'last': party.last_name,
            'middle': party.middle_initial
        }
    }

    assert party.json == party_json


def test_create_from_json(session):
    """Assert that the party json renders to a party model correctly."""
    party_bus_json = {
        'businessName': 'business\'s, inc',
        'emailAddress': 'asmith@gmail.com',
        'address': {
            'street': 'street',
            'streetAdditional': 'additional',
            'city': 'city',
            'region': 'BC',
            'country': 'CA',
            'postalCode': 'V8S2J4'
        }
    }

    party_ind_json = {
        'personName': {
            'first': 'first',
            'last': 'last',
            'middle': 'middle'
        },
        'emailAddress': 'asmith@gmail.com',
        'birthDate': '1990-06-15',
        'address': {
            'street': 'street',
            'streetAdditional': 'additional',
            'city': 'city',
            'region': 'BC',
            'country': 'CA',
            'postalCode': 'V8S2J4'
        }
    }

    party_bus = Party.create_from_json(party_bus_json, 'SP', 1234)
    assert party_bus.registration_id
    assert party_bus.party_type == 'SP'
    assert party_bus.business_name
    assert party_bus.address
    assert party_bus.address.street
    assert party_bus.address.street_additional
    assert party_bus.address.city
    assert party_bus.address.region
    assert party_bus.address.country
    assert party_bus.address.postal_code
    assert not party_bus.last_name

    party_ind = Party.create_from_json(party_ind_json, 'DB', 1234)
    assert party_ind.registration_id
    assert party_ind.party_type == 'DI'
    assert party_ind.last_name
    assert party_ind.first_name
    assert party_ind.middle_initial
    assert party_ind.address
    assert party_ind.address.street
    assert party_ind.address.street_additional
    assert party_ind.address.city
    assert party_ind.address.region
    assert party_ind.address.country
    assert party_ind.address.postal_code
    assert not party_ind.business_name


def test_create_from_financing_json(session):
    """Assert that the financing statement json renders to a list of party models correctly."""
    json_data = copy.deepcopy(FINANCING_STATEMENT)
    del json_data['securedParties']

    secured = [{
            'code': '200000000'
        }
    ]
    json_data['securedParties'] = secured
    parties = Party.create_from_financing_json(json_data, None)
    assert parties
    assert len(parties) == 3
    for party in parties:
        assert party.party_type
        if not party.branch_id:
            assert party.address


def test_verify_party_code_true(session):
    """Assert that Party.verify_party_code works correctly with a valid code."""
    result = Party.verify_party_code('200000000')
    assert result


def test_verify_party_code_false(session):
    """Assert that Party.verify_party_code works correctly with an invalid code."""
    result = Party.verify_party_code('300000000')
    assert not result


def test_save_business(session):
    """Assert that saving a business name party works correctly."""
    party_bus_json = {
        'businessName': 'business\'s, inc',
        'emailAddress': 'asmith@gmail.com',
        'address': {
            'street': 'street',
            'streetAdditional': 'additional',
            'city': 'city',
            'region': 'BC',
            'country': 'CA',
            'postalCode': 'V8S2J4'
        }
    }

    party_bus = Party.create_from_json(party_bus_json, Party.PartyTypes.DEBTOR_COMPANY.value, 1234)
    party_bus.registration_id = 200000000
    party_bus.financing_id = 200000000
    party_bus.save()
    assert party_bus.business_search_key
    assert party_bus.id


def test_save_individual(session):
    """Assert that saving a business name party works correctly."""
    party_ind_json = {
        'personName': {
            'first': 'first\'s name',
            'last': 'last, name',
            'middle': 'middle'
        },
        'emailAddress': 'asmith@gmail.com',
        'birthDate': '1990-06-15',
        'address': {
            'street': 'street',
            'streetAdditional': 'additional',
            'city': 'city',
            'region': 'BC',
            'country': 'CA',
            'postalCode': 'V8S2J4'
        }
    }

    party = Party.create_from_json(party_ind_json, Party.PartyTypes.DEBTOR_INDIVIDUAL.value, 1234)
    party.registration_id = 200000000
    party.financing_id = 200000000
    party.save()
    assert party.first_name_key
    assert party.id
