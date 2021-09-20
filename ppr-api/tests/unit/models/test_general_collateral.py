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

"""Tests to assure the General Collateral Model.

Test-Suite to ensure that the General Collateral Model is working as expected.
"""
import copy

from registry_schemas.example_data.ppr import FINANCING_STATEMENT, AMENDMENT_STATEMENT

from ppr_api.models import GeneralCollateral


def test_find_by_id(session):
    """Assert that find general collateral by collateral ID contains all expected elements."""
    collateral = GeneralCollateral.find_by_id(200000000)
    assert collateral
    assert collateral.id == 200000000
    assert collateral.registration_id == 200000000
    assert collateral.financing_id == 200000000
    assert collateral.description
    assert not collateral.registration_id_end
    json_data = collateral.json
    assert json_data['collateralId'] == 200000000
    assert json_data['description']


def test_find_by_registration_id(session):
    """Assert that find general collateral by registration id contains all expected elements."""
    collateral = GeneralCollateral.find_by_registration_id(200000000)
    assert collateral
    assert len(collateral) == 2
    assert collateral[0].id
    assert collateral[0].registration_id
    assert collateral[0].financing_id
    assert collateral[0].description
    assert collateral[1].id
    assert collateral[1].registration_id
    assert collateral[1].financing_id
    assert collateral[1].description


def test_find_by_financing_id(session):
    """Assert that find general collateral by financing statement ID contains all expected elements."""
    collateral = GeneralCollateral.find_by_financing_id(200000000)
    assert collateral
    assert len(collateral) >= 2
    assert collateral[0].id
    assert collateral[0].registration_id
    assert collateral[0].financing_id
    assert collateral[0].description
    assert collateral[1].id
    assert collateral[1].registration_id
    assert collateral[1].financing_id
    assert collateral[1].description


def test_find_by_id_invalid(session):
    """Assert that find general collateral by non-existent collateral ID returns the expected result."""
    collateral = GeneralCollateral.find_by_id(300000000)
    assert not collateral


def test_find_by_financing_id_invalid(session):
    """Assert that find general collateral by non-existent financing statement ID returns the expected result."""
    collateral = GeneralCollateral.find_by_financing_id(300000000)
    assert not collateral


def test_find_by_reg_id_invalid(session):
    """Assert that find general collateral by non-existent registration ID returns the expected result."""
    collateral = GeneralCollateral.find_by_registration_id(300000000)
    assert not collateral


def test_general_collateral_json(session):
    """Assert that the general collateral model renders to a json format correctly."""
    collateral = GeneralCollateral(
        id=1000,
        description='TEST',
    )

    collateral_json = {
        'collateralId': collateral.id,
        'description': collateral.description,
        'addedDateTime': '',
        'added': False,
        'removed': False,
        'legacy': False
    }
    assert collateral.json == collateral_json


def test_create_from_json(session):
    """Assert that the general collateral json renders to a general collateral model correctly."""
    json_data = {
        'description': 'description'
    }

    collateral = GeneralCollateral.create_from_json(json_data, 12345)
    assert collateral
    assert collateral.registration_id == 12345
    assert collateral.description


def test_create_from_financing_json(session):
    """Assert that the financing statement json renders to a list of general collateral models correctly."""
    json_data = copy.deepcopy(FINANCING_STATEMENT)
    collateral = GeneralCollateral.create_from_financing_json(json_data, 12345)
    assert collateral
    assert len(collateral) == 1
    for c in collateral:
        assert c.registration_id == 12345
        assert c.description


def test_create_from_statement_json(session):
    """Assert that the amendment/change statement json renders to a list of general collateral models correctly."""
    json_data = copy.deepcopy(AMENDMENT_STATEMENT)
    collateral = GeneralCollateral.create_from_statement_json(json_data, 11111, 22222)
    assert collateral
    assert len(collateral) >= 1
    for c in collateral:
        assert c.registration_id == 11111
        assert c.financing_id == 22222
        assert c.description
