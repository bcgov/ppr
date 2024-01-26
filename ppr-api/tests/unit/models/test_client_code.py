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
# testdata pattern is ({description}, {account_id}, {results_size}, {crown_charge})
TEST_DATA_ACCOUNT_NUMBER = [
    ('CC account with bcol number mapping', 'PS12345', 2, True),
    ('Non CC account with bcol number mapping', 'PS00001', 1, False),
    ('Account with no bcol number mapping', 'PS1234X', 0, False)
]
# testdata pattern is ({description}, {results_size}, {search_value})
TEST_DATA_BRANCH_CODE = [
    ('No results exact', 0, '000'),
    ('No results start 3', 0, '998'),
    ('Results start 3', 4, '999'),
    ('No results start 4', 0, '9998'),
    ('Results start 4', 4, '9999'),
    ('Results start 5', 4, '99990'),
    ('Results start 6', 4, '999900'),
    ('Results start 7', 4, '9999000'),
    ('Results start 8 exact', 1, '99990002')
]
# testdata pattern is ({description}, {results_size}, {search_value}, {fuzzy_search})
TEST_DATA_HEAD_OFFICE = [
    ('Code exists 3 digits', 4, '999', False),
    ('No code exists 3 digits', 0, '998', False),
    ('Code exists 4 digits', 4, '9999', False),
    ('No code exists 4', 0, '9998', False),
    ('Code exists 5 digits', 4, '99990', False),
    ('Name exists', 4, 'rbc royal bank', False),
    ('Name does not exist', 0, 'XXX royal bank', False),
    ('Fuzzy name search exists', 4, 'rbc', True),
    ('Fuzzy name search does not exist', 0, 'xxx', True),
]
# testdata pattern is ({code}, {formatted_code})
TEST_DATA_FORMAT_CODE = [
    (1, '00000001'),
    (11, '00000011'),
    (111, '00000111'),
    (1111, '00001111'),
    (11111, '00011111'),
    (111111, '00111111'),
    (1111111, '01111111'),
    (11111111, '11111111')
]


@pytest.mark.parametrize('desc,exists,search_value', TEST_DATA_PARTY_CODE)
def test_find_by_code(session, desc, exists, search_value):
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


@pytest.mark.parametrize('desc,results_size,search_value', TEST_DATA_BRANCH_CODE)
def test_find_by_branch_start(session, desc, results_size, search_value):
    """Assert that find client parties by branch code matching contains all expected elements."""
    parties = ClientCode.find_by_branch_start(search_value)
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


@pytest.mark.parametrize('desc,results_size,search_value', TEST_DATA_BRANCH_CODE)
def test_find_by_code_start(session, desc, results_size, search_value):
    """Assert that find client parties by party code start matching contains all expected elements."""
    parties = ClientCode.find_by_code_start(search_value)
    if results_size > 0:
        assert parties
        assert len(parties) >= results_size
        for party in parties:
            assert len(party['code']) == 8
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


@pytest.mark.parametrize('desc,account_id,results_size,crown_charge', TEST_DATA_ACCOUNT_NUMBER)
def test_find_by_account_id(session, desc, account_id, results_size, crown_charge):
    """Assert that find client parties by account id contains all expected elements."""
    parties = ClientCode.find_by_account_id(account_id, crown_charge)
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


@pytest.mark.parametrize('desc,results_size,search_value,fuzzy_search', TEST_DATA_HEAD_OFFICE)
def test_find_by_head_office(session, desc, results_size, search_value, fuzzy_search):
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


@pytest.mark.parametrize('code,formatted_code', TEST_DATA_FORMAT_CODE)
def test_format_party_code(session, code, formatted_code):
    """Assert that client party code formatting is as expected."""
    party = ClientCode(id=code)
    assert party.format_party_code() == formatted_code


def test_client_party_json(session):
    """Assert that the client party model renders to a json format correctly."""
    party = ClientCode(
        id=10001,
        name='BUSINESS NAME',
        contact_name='CONTACT',
        contact_area_cd='250',
        contact_phone_number='1234567',
        email_id='test@gmail.com'
    )

    party_json = {
        'code': party.format_party_code(),
        'businessName': party.name,
        'contact': {
            'name': party.contact_name,
            'phoneNumber': party.contact_phone_number,
            'areaCode': party.contact_area_cd
        },
        'emailAddress': party.email_id
    }
    assert party.json == party_json
