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

"""Tests to assure the ClientParty Model.

Test-Suite to ensure that the ClientParty Model is working as expected.
"""

from ppr_api.models import ClientParty


def test_find_by_code(session):
    """Assert that find client party by code contains all expected elements."""
    party = ClientParty.find_by_code('200000000')
    assert party
    assert party['code'] == '200000000'
    assert party['businessName']


def test_find_by_code_invalid(session):
    """Assert that find client party by non-existent code returns the expected result."""
    party = ClientParty.find_by_code('12345')
    assert not party


def test_client_party_json(session):
    """Assert that the client party model renders to a json format correctly."""
    party = ClientParty(
        client_party_id=1000,
        business_name='BUSINESS'
    )

    party_json = {
        'code': '1000',
        'businessName': party.business_name
    }

    assert party.json == party_json
