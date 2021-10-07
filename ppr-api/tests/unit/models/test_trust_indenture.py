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

"""Tests to assure the Trust Indenture Model.

Test-Suite to ensure that the Trust Indenture Model is working as expected.
"""
import copy

from registry_schemas.example_data.ppr import FINANCING_STATEMENT

from ppr_api.models import TrustIndenture


def test_find_by_id(session):
    """Assert that find trust indenture by trust indenture ID contains all expected elements."""
    trust_indenture = TrustIndenture.find_by_id(200000000)
    assert trust_indenture
    assert trust_indenture.id == 200000000
    assert trust_indenture.registration_id == 200000000
    assert trust_indenture.financing_id == 200000000
    assert trust_indenture.trust_indenture == 'Y'


def test_find_by_registration_id(session):
    """Assert that find trust indenture by registration ID contains all expected elements."""
    trust_indenture = TrustIndenture.find_by_registration_id(200000000)
    assert trust_indenture
    assert trust_indenture.id == 200000000
    assert trust_indenture.registration_id == 200000000
    assert trust_indenture.financing_id == 200000000
    assert trust_indenture.trust_indenture == 'Y'


def test_find_by_financing_id(session):
    """Assert that find trust indenture by financing statement ID contains all expected elements."""
    trust_indenture = TrustIndenture.find_by_financing_id(200000000)
    assert trust_indenture
    assert len(trust_indenture) == 1
    assert trust_indenture[0].id == 200000000
    assert trust_indenture[0].registration_id == 200000000
    assert trust_indenture[0].financing_id == 200000000
    assert trust_indenture[0].trust_indenture == 'Y'


def test_find_by_id_invalid(session):
    """Assert that find trust indenture by non-existent trust indenture ID returns the expected result."""
    trust_indenture = TrustIndenture.find_by_id(300000000)
    assert not trust_indenture


def test_find_by_financing_id_invalid(session):
    """Assert that find trust indenture by non-existent financing statement ID returns the expected result."""
    trust_indenture = TrustIndenture.find_by_financing_id(300000000)
    assert not trust_indenture


def test_find_by_reg_id_invalid(session):
    """Assert that find trust indenture by non-existent registration ID returns the expected result."""
    trust_indenture = TrustIndenture.find_by_registration_id('300000000')
    assert not trust_indenture


def test_create_from_json(session):
    """Assert that the expiry model renders from a json format correctly."""
    test_json = copy.deepcopy(FINANCING_STATEMENT)
    test_json['trustIndenture'] = True
    trust_indenture = TrustIndenture.create_from_json(test_json, 1234)

    assert trust_indenture[0].trust_indenture == 'Y'
