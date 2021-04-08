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

"""Tests to assure the ClientPartyBranch Model.

Test-Suite to ensure that the ClientPartyBranch Model is working as expected.
"""

from ppr_api.models import ClientPartyBranch


def test_find_by_code(session):
    """Assert that find client party by code contains all expected elements."""
    party = ClientPartyBranch.find_by_code('200000000')
    assert party
    assert party['code'] == '200000000'
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


def test_find_by_code_invalid(session):
    """Assert that find client party by non-existent code returns the expected result."""
    party = ClientPartyBranch.find_by_code('12345')
    assert not party


def test_client_party_json(session):
    """Assert that the client party model renders to a json format correctly."""
    party = ClientPartyBranch(
        client_party_id=1000,
        contact_name='CONTACT',
        contact_area_cd='250',
        contact_phone_number='1234567',
        email_id='test@gmail.com'
    )

    party_json = {
        'code': '1000',
        'contact': {
            'name': party.contact_name,
            'phoneNumber': party.contact_phone_number,
            'areaCode': party.contact_area_cd
        },
        'emailAddress': party.email_id
    }

    assert party.json == party_json
