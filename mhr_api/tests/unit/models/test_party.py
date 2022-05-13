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

from mhr_api.models import Party


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


def test_verify_party_code_true(session):
    """Assert that Party.verify_party_code works correctly with a valid code."""
    result = Party.verify_party_code('200000000')
    assert result


def test_verify_party_code_false(session):
    """Assert that Party.verify_party_code works correctly with an invalid code."""
    result = Party.verify_party_code('300000000')
    assert not result
