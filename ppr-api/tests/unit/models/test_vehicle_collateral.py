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

"""Tests to assure the Vehicle Collateral Model.

Test-Suite to ensure that the Vehicle Collateral Model is working as expected.
"""
from http import HTTPStatus

import pytest

from ppr_api.models import VehicleCollateral

import copy
from registry_schemas.example_data.ppr import FINANCING_STATEMENT, AMENDMENT_STATEMENT


def test_find_by_id(session):
    """Assert that find vehicle collateral by vehicle collateral ID contains all expected elements."""
    collateral = VehicleCollateral.find_by_id(200000000)
    assert collateral
    assert collateral.vehicle_id == 200000000
    assert collateral.registration_id == 200000000
    assert collateral.financing_id == 200000000
    assert collateral.vehicle_type_cd == 'MV'
    assert collateral.make
    assert collateral.model
    assert collateral.serial_number
    assert not collateral.registration_id_end
    assert not collateral.mhr_number

def test_find_by_financing_id(session):
    """Assert that find vehicle collateral by financing statement ID contains all expected elements."""
    collateral = VehicleCollateral.find_by_financing_id(200000000)
    assert collateral
    assert len(collateral) >= 2
    assert collateral[0].vehicle_id == 200000000
    assert collateral[0].registration_id == 200000000
    assert collateral[0].financing_id == 200000000
    assert not collateral[0].registration_id_end
    assert not collateral[0].mhr_number
    assert collateral[0].vehicle_type_cd
    assert collateral[1].vehicle_id
    assert collateral[1].registration_id
    assert collateral[1].vehicle_type_cd == 'MH'
    assert collateral[1].mhr_number


def test_find_by_registration_id(session):
    """Assert that find vehicle collateral by registration ID contains all expected elements."""
    collateral = VehicleCollateral.find_by_registration_id(200000000)
    assert collateral
    assert len(collateral) == 2
    assert collateral[0].vehicle_id
    assert collateral[0].registration_id
    assert collateral[0].vehicle_type_cd
    assert collateral[1].vehicle_id
    assert collateral[1].registration_id
    assert collateral[1].vehicle_type_cd == 'MH'
    assert collateral[1].mhr_number

def test_find_by_id_invalid(session):
    """Assert that find vehicle collateral by non-existent vehicle collateral ID returns the expected result."""
    collateral = VehicleCollateral.find_by_id(300000000)
    assert not collateral

def test_find_by_financing_id_invalid(session):
    """Assert that find vehicle collateral by non-existent financing statement ID returns the expected result."""
    collateral = VehicleCollateral.find_by_financing_id(300000000)
    assert not collateral

def test_find_by_reg_id_invalid(session):
    """Assert that find vehicle collateral by non-existent registration ID returns the expected result."""
    collateral = VehicleCollateral.find_by_registration_id(300000000)
    assert not collateral

def test_vehicle_collateral_json(session):
    """Assert that the general collateral model renders to a json format correctly."""
    collateral = VehicleCollateral(
        vehicle_id=1000,
        vehicle_type_cd='MV',
        year=2004,
        make='MAKE',
        model='MODEL',
        serial_number='SERIAL_NUMBER',
        mhr_number='MHR_NUMBER'
    )

    collateral_json = {
        'vehicleId': collateral.vehicle_id,
        'type': collateral.vehicle_type_cd,
        'year': collateral.year,
        'make': collateral.make,
        'model': collateral.model,
        'serialNumber': collateral.serial_number,
        'manufacturedHomeRegistrationNumber': collateral.mhr_number
    }

    assert collateral.json == collateral_json

def test_create_from_json(session):
    """Assert that the vehicle collateral json renders to a vehicle collateral model correctly."""

    json_data = {
        'type': 'MV',
        'year': 2004,
        'make': 'MAKE',
        'model': 'MODEL',
        'serialNumber': 'SERIAL',
        'manufacturedHomeRegistrationNumber': 'MHR_NUMBER'
    }

    collateral = VehicleCollateral.create_from_json(json_data, 12345)
    assert collateral
    assert collateral.registration_id == 12345
    assert collateral.vehicle_type_cd == 'MV'
    assert collateral.serial_number == 'SERIAL'
    assert collateral.year == 2004
    assert collateral.make == 'MAKE'
    assert collateral.model == 'MODEL'
    assert collateral.mhr_number == 'MHR_NUMBER'


def test_create_from_financing_json(session):
    """Assert that the financing statement json renders to a list of vehicle collateral models correctly."""
    json_data = copy.deepcopy(FINANCING_STATEMENT)
    collateral = VehicleCollateral.create_from_financing_json(json_data, 12345)
    assert collateral
    assert len(collateral) == 1
    for c in collateral:
        assert c.registration_id == 12345
        assert c.vehicle_type_cd
        assert c.serial_number



def test_create_from_statement_json(session):
    """Assert that the financing statement json renders to a list of vehicle collateral models correctly."""
    json_data = copy.deepcopy(AMENDMENT_STATEMENT)
    collateral = VehicleCollateral.create_from_statement_json(json_data, 11111, 22222)
    assert collateral
    assert len(collateral) >= 1
    for c in collateral:
        assert c.registration_id == 11111
        assert c.financing_id == 22222
        assert c.vehicle_type_cd
        assert c.serial_number
