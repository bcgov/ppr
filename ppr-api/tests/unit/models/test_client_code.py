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

"""Tests to assure the ClientCode Model.

Test-Suite to ensure that the ClientCode Model is working as expected.
"""
import pytest

from ppr_api.models import ClientCode


# testdata pattern is ({description}, {exists}, {search_value})
TEST_DATA_PARTY_CODE = [
    ('Exists', True, '200000000'),
    ('Does not exist', False, '12345')
]
# testdata pattern is ({description}, {exists}, {search_value}, {results_size}, {fuzzy_search})
TEST_DATA_HEAD_OFFICE = [
    ('Code exists', 4, '9999', False),
    ('Name exists', 4, 'rbc royal bank', False),
    ('Code does not exist', 0, '9998', False),
    ('Name does not exist', 0, 'XXX royal bank', False),
    ('Fuzzy name search exists', 4, 'rbc', True),
    ('Fuzzy name search does not exist', 0, 'xxx', True),
]


@pytest.mark.parametrize('desc,exists,search_value', TEST_DATA_PARTY_CODE)
def test_find_party_code(session, desc, exists, search_value):
    """Assert that find client party by code contains all expected elements."""
    party = ClientCode.find_by_code(search_value)
    if exists:
        assert party
        assert party['code'] == search_value
        assert party['address']
        assert party['address']['street']
        assert party['address']['city']
        assert party['address']['region']
        assert party['address']['postalCode']
        assert party['contact']
        assert party['contact']['name']
        assert party['contact']['areaCode']
        assert party['contact']['phoneNumber']
        assert party['businessName']
        assert party['emailAddress']
    else:
        assert not party


@pytest.mark.parametrize('desc,results_size,search_value,fuzzy_search', TEST_DATA_HEAD_OFFICE)
def test_find_head_office_codes(session, desc, results_size, search_value, fuzzy_search):
    """Assert that find client party by head office contains all expected elements."""
    parties = ClientCode.find_by_head_office(search_value, fuzzy_search)
    if results_size > 0:
        assert parties
        assert len(parties) >= results_size
        for party in parties:
            assert len(party['code']) >= 5
            assert party['businessName']
            assert party['address']
            assert party['address']['street']
            assert party['address']['city']
            assert party['address']['region']
            assert party['address']['postalCode']
            assert party['contact']
            assert party['contact']['name']
            assert party['contact']['areaCode']
            assert party['contact']['phoneNumber']
            assert party['emailAddress']
    else:
        assert not parties


def test_client_party_json(session):
    """Assert that the client party model renders to a json format correctly."""
    party = ClientCode(
        id=1000,
        name='BUSINESS NAME',
        contact_name='CONTACT',
        contact_area_cd='250',
        contact_phone_number='1234567',
        email_id='test@gmail.com'
    )

    party_json = {
        'code': '1000',
        'businessName': party.name,
        'contact': {
            'name': party.contact_name,
            'phoneNumber': party.contact_phone_number,
            'areaCode': party.contact_area_cd
        },
        'emailAddress': party.email_id
    }

    assert party.json == party_json
