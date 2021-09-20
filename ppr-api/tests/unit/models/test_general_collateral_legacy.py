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

from ppr_api.models import GeneralCollateralLegacy


def test_find_by_id(session):
    """Assert that find general collateral by collateral ID contains all expected elements."""
    collateral = GeneralCollateralLegacy.find_by_id(200000004)
    assert collateral
    assert collateral.id == 200000004
    assert collateral.registration_id == 200000024
    assert collateral.financing_id == 200000012
    assert collateral.description
    assert not collateral.registration_id_end
    json_data = collateral.json
    assert json_data['collateralId'] == 200000004
    assert json_data['description'] == 'TEST0018 GC 1'


def test_find_by_registration_id(session):
    """Assert that find general collateral by registration id contains all expected elements."""
    collateral = GeneralCollateralLegacy.find_by_registration_id(200000024)
    assert collateral and len(collateral) == 3
    for gen_coll in collateral:
        assert gen_coll.id
        assert gen_coll.registration_id == 200000024
        assert gen_coll.financing_id == 200000012
        assert gen_coll.description


def test_find_by_financing_id(session):
    """Assert that find general collateral by financing statement ID contains all expected elements."""
    collateral = GeneralCollateralLegacy.find_by_financing_id(200000012)
    assert collateral
    assert collateral and len(collateral) >= 5
    for gen_coll in collateral:
        assert gen_coll.id
        assert gen_coll.registration_id
        assert gen_coll.financing_id == 200000012
        assert gen_coll.description


def test_find_by_id_invalid(session):
    """Assert that find general collateral by non-existent collateral ID returns the expected result."""
    collateral = GeneralCollateralLegacy.find_by_id(300000000)
    assert not collateral


def test_find_by_financing_id_invalid(session):
    """Assert that find general collateral by non-existent financing statement ID returns the expected result."""
    collateral = GeneralCollateralLegacy.find_by_financing_id(300000000)
    assert not collateral


def test_find_by_reg_id_invalid(session):
    """Assert that find general collateral by non-existent registration ID returns the expected result."""
    collateral = GeneralCollateralLegacy.find_by_registration_id(300000000)
    assert not collateral


def test_general_collateral_json(session):
    """Assert that the general collateral model renders to a json format correctly."""
    collateral = GeneralCollateralLegacy(
        id=1000,
        description='TEST',
    )

    collateral_json = {
        'collateralId': collateral.id,
        'description': collateral.description,
        'addedDateTime': '',
        'added': False,
        'removed': False,
        'legacy': True
    }
    # print(collateral.json)
    assert collateral.json == collateral_json
    collateral.status = 'D'
    collateral_json['removed'] = True
    assert collateral.json == collateral_json
    collateral.status = 'A'
    collateral_json['removed'] = False
    collateral_json['added'] = True
    assert collateral.json == collateral_json
