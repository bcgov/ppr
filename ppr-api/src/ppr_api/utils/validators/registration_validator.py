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
"""This module holds non-party registration validation for rules not covered by the schema.

Validation includes verifying delete collateral ID's and timestamps.
"""


AUTHORIZATION_INVALID = 'Authorization Received indicator is required with this registration.\n'
DELETE_MISSING_ID_VEHICLE = 'Required vehicleId missing in delete Vehicle Collateral.\n'
DELETE_MISSING_ID_GENERAL = 'Required collateralId missing in delete General Collateral.\n'
DELETE_INVALID_ID_VEHICLE = 'Invalid vehicleId {} in delete Vehicle Collateral.\n'
DELETE_INVALID_ID_GENERAL = 'Invalid collateralId {} in delete General Collateral.\n'


def validate_registration(json_data, financing_statement=None):
    """Perform all registration data validation checks not covered by schema validation."""
    error_msg = ''
    if 'authorizationReceived' not in json_data or not json_data['authorizationReceived']:
        error_msg += AUTHORIZATION_INVALID
    error_msg += validate_collateral_ids(json_data, financing_statement)
    return error_msg


def validate_collateral_ids(json_data, financing_statement=None):
    """Check amendment, change registration delete collateral ID's are valid."""
    error_msg = ''
    # Check delete vehicle ID's
    if 'deleteVehicleCollateral' in json_data:
        for collateral in json_data['deleteVehicleCollateral']:
            if 'vehicleId' not in collateral:
                error_msg += DELETE_MISSING_ID_VEHICLE
            elif financing_statement:
                collateral_id = collateral['vehicleId']
                existing = find_vehicle_collateral_by_id(collateral_id, financing_statement.vehicle_collateral)
                if not existing:
                    error_msg += DELETE_INVALID_ID_VEHICLE.format(str(collateral_id))

    # Check delete general collateral ID's.
    # Removed: with th "add only" model the check on delete general collateral ID is no longer required.
    # if 'deleteGeneralCollateral' in json_data:
    #    for collateral in json_data['deleteGeneralCollateral']:
    #        if 'collateralId' not in collateral:
    #            error_msg += DELETE_MISSING_ID_GENERAL
    #        elif financing_statement:
    #            collateral_id = collateral['collateralId']
    #            existing = find_general_collateral_by_id(collateral_id, financing_statement.general_collateral)
    #            if not existing:
    #                error_msg += DELETE_INVALID_ID_GENERAL.format(str(collateral_id))

    return error_msg


def find_vehicle_collateral_by_id(vehicle_id: int, vehicle_collateral):
    """Search existing list of vehicle_collateral objects for a matching vehicle id."""
    collateral = None

    if vehicle_id and vehicle_collateral:
        for v_collateral in vehicle_collateral:
            if v_collateral.id == vehicle_id and not v_collateral.registration_id_end:
                collateral = v_collateral
    return collateral


def find_general_collateral_by_id(collateral_id: int, general_collateral):
    """Search existing list of general_collateral objects for a matching collateral id."""
    collateral = None

    if collateral_id and general_collateral:
        for g_collateral in general_collateral:
            if g_collateral.id == collateral_id and not g_collateral.registration_id_end:
                collateral = g_collateral
    return collateral
