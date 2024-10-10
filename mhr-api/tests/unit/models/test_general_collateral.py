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

from mhr_api.models import GeneralCollateral


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


def test_general_collateral_add_json(session):
    """Assert that the general collateral model renders add collateral json format correctly."""
    collateral = GeneralCollateral(
        id=1000,
        description='TEST ADD',
        status='A'
    )

    collateral_json = {
        'collateralId': collateral.id,
        'descriptionAdd': collateral.description,
        'addedDateTime': ''
    }
    assert collateral.current_json == collateral_json


def test_general_collateral_delete_json(session):
    """Assert that the general collateral model renders delete collateral json format correctly."""
    collateral = GeneralCollateral(
        id=1000,
        description='TEST DELETE',
        status='D'
    )

    collateral_json = {
        'collateralId': collateral.id,
        'descriptionDelete': collateral.description,
        'addedDateTime': ''
    }
    assert collateral.current_json == collateral_json


def test_general_collateral_json(session):
    """Assert that the general collateral model renders to a json format correctly."""
    collateral = GeneralCollateral(
        id=1000,
        description='TEST',
    )

    collateral_json = {
        'collateralId': collateral.id,
        'description': collateral.description,
        'addedDateTime': ''
    }
    assert collateral.json == collateral_json
    assert collateral.current_json == collateral_json
