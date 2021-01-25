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

"""Tests to assure the Expiry Model.

Test-Suite to ensure that the Expiry Model is working as expected.
"""
from http import HTTPStatus

import pytest

from ppr_api.models import Expiry

import copy
from registry_schemas.example_data.ppr import FINANCING_STATEMENT, RENEWAL_STATEMENT


def test_find_by_id(session):
    """Assert that find expiry by expiry ID contains all expected elements."""
    expiry = Expiry.find_by_id(200000000)
    assert expiry
    assert expiry.expiry_id == 200000000
    assert expiry.registration_id == 200000000
    assert expiry.financing_id == 200000000
    assert expiry.expiry_dt
    assert expiry.life_infinite == 'N'
    assert expiry.life_years == 2


def test_find_by_registration_id(session):
    """Assert that find expiry by registration id contains all expected elements."""
    expiry = Expiry.find_by_registration_id(200000000)
    assert expiry
    assert expiry.expiry_id == 200000000
    assert expiry.registration_id == 200000000
    assert expiry.financing_id == 200000000
    assert expiry.expiry_dt
    assert expiry.life_infinite == 'N'
    assert expiry.life_years == 2

def test_find_by_financing_id(session):
    """Assert that find expiry by financing statement ID contains all expected elements."""
    expiry = Expiry.find_by_financing_id(200000000)
    assert expiry
    assert len(expiry) == 1
    assert expiry[0].expiry_id
    assert expiry[0].registration_id
    assert expiry[0].financing_id
    assert expiry[0].expiry_dt
    assert expiry[0].life_infinite == 'N'
    assert expiry[0].life_years == 2

def test_find_by_id_invalid(session):
    """Assert that find expiry by non-existent expiry ID returns the expected result."""
    expiry = Expiry.find_by_id(300000000)
    assert not expiry

def test_find_by_financing_id_invalid(session):
    """Assert that find expiry by non-existent financing statement ID returns the expected result."""
    expiry = Expiry.find_by_financing_id(300000000)
    assert not expiry

def test_find_by_reg_id_invalid(session):
    """Assert that find expiry by non-existent registration ID returns the expected result."""
    expiry = Expiry.find_by_registration_id(300000000)
    assert not expiry

def test_create_from_json(session):
    """Assert that the expiry model renders from a json format correctly."""
            
    test_json = copy.deepcopy(FINANCING_STATEMENT)
    expiry = Expiry.create_from_json(test_json, 'SA', 1234)

    assert expiry[0].life_infinite
    assert expiry[0].life_years
    assert expiry[0].expiry_dt


def test_create_from_renewal_json(session):
    """Assert that the expiry model renders from a renewal statement json format correctly."""
            
    test_json = copy.deepcopy(RENEWAL_STATEMENT)
    expiry = Expiry.create_from_renewal_json(test_json, 1234, 'SA', 4321)
    assert expiry.life_infinite == 'N'
    assert expiry.life_years == 0
    assert expiry.expiry_dt
    assert expiry.financing_id == 1234
    assert expiry.registration_id == 4321

    del test_json['expiryDate']
    expiry = Expiry.create_from_renewal_json(test_json, 12345, 'RL', 4321)
    assert expiry.life_infinite == 'N'
    assert expiry.life_years == 0
    assert expiry.expiry_dt
    assert expiry.financing_id == 12345
    assert expiry.registration_id == 4321
