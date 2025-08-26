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

from ppr_api.models import ClientCode, FinancingStatement, Registration, VehicleCollateral
from ppr_api.models import registration_utils as reg_utils
from ppr_api.models import utils as model_utils
from ppr_api.models.registration import MiscellaneousTypes

# from ppr_api.utils.logging import logger

REG_STATUS_LOCKED = "L"
COURT_ORDER_INVALID = "Court order information cannot be included with the specified base registration type {}. "
COURT_ORDER_MISSING = "Court order information is required but not provided. "
COURT_ORDER_INVALID_DATE = (
    "The court order date must be within the valid registration period: between the base "
    + "registration date and the current system date. "
)
AUTHORIZATION_INVALID = "Authorization Received indicator is required with this registration. "
DELETE_MISSING_ID_VEHICLE = "A vehicle ID is required to delete vehicle collateral. "
DELETE_MISSING_ID_GENERAL = "A collateral ID is required to delete general collateral. "
DELETE_INVALID_ID_VEHICLE = "The vehicle ID provided for deletion is invalid ({}). "
DELETE_INVALID_ID_GENERAL = "The collateral ID provided for deletion is invalid ({}). "
LI_NOT_ALLOWED = "This type of registration does not support an infinite durations. "
RENEWAL_INVALID = "Renewal registration is now allowed: the base registration is set to never expire. "
LIFE_MISSING = "Specify either a fixed duration in years or infinite for this registration type. "
LIFE_INVALID = "Either duration in Years or Infinite Life is allowed but not both. "
VC_AP_NOT_ALLOWED = "The AP type for vehicle collateral is not permitted. "
SE_ACCESS_INVALID = "The SE type notice under the Securities Act is restricted based on account authorization. "
SE_AMEND_SP_INVALID = "Secured parties cannot be modified during an amendment to a Securities Act Notice. "
SE_DELETE_INVALID = "At least one Securities Act Notice is required. "
SE_DELETE_MISSING_ID = "A notice ID is required to delete a Securities Act Notice. "
SE_DELETE_INVALID_ID = "The delete ID provided for the Securities Act Notice is invalid ({}). "
STATE_INVALID_PAY_LOCKED = "New registration is blocked because a previous one has an unresolved credit card payment. "


def validate_registration(json_data: dict, account_id: str, financing_statement=None) -> str:
    """Perform all registration data validation checks not covered by schema validation."""
    error_msg: str = ""
    if "authorizationReceived" not in json_data or not json_data["authorizationReceived"]:
        error_msg += AUTHORIZATION_INVALID
    if financing_statement:
        error_msg += validate_pending_state(financing_statement.registration[0])
    error_msg += validate_collateral(json_data, financing_statement)
    error_msg += validate_securities_act_access(account_id, financing_statement)
    error_msg += validate_securities_act_notices(financing_statement, json_data)
    return error_msg


def validate_renewal(json_data: dict, financing_statement: FinancingStatement) -> str:
    """Perform all renewal registration data validation checks not covered by schema validation."""
    error_msg: str = ""
    if "authorizationReceived" not in json_data or not json_data["authorizationReceived"]:
        error_msg += AUTHORIZATION_INVALID

    if not financing_statement:
        return error_msg
    error_msg += validate_pending_state(financing_statement.registration[0])
    error_msg += validate_life(json_data, financing_statement)
    if "courtOrderInformation" in json_data:
        error_msg += COURT_ORDER_INVALID.format(financing_statement.registration[0].registration_type)
    return error_msg


def validate_collateral(json_data, financing_statement=None) -> str:
    """Check amendment, change registration delete collateral ID's are valid."""
    error_msg: str = ""
    # Check delete vehicle ID's
    if "deleteVehicleCollateral" in json_data:
        for collateral in json_data["deleteVehicleCollateral"]:
            if "vehicleId" not in collateral:
                error_msg += DELETE_MISSING_ID_VEHICLE
            elif financing_statement:
                collateral_id = collateral["vehicleId"]
                existing = find_vehicle_collateral_by_id(collateral_id, financing_statement.vehicle_collateral)
                if not existing:
                    error_msg += DELETE_INVALID_ID_VEHICLE.format(str(collateral_id))

    if "addVehicleCollateral" in json_data:
        for collateral in json_data["addVehicleCollateral"]:
            if "type" in collateral and collateral["type"] == VehicleCollateral.SerialTypes.AIRPLANE.value:
                error_msg += VC_AP_NOT_ALLOWED

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


def validate_life(json_data: dict, financing_statement) -> str:
    """Validate renewal lifeYears and lifeInfinite by registration type."""
    error_msg: str = ""
    if financing_statement.life == model_utils.LIFE_INFINITE:
        error_msg += RENEWAL_INVALID
    elif "lifeYears" not in json_data and "lifeInfinite" not in json_data:
        error_msg += LIFE_MISSING
    elif json_data.get("lifeYears", -1) > 0 and json_data.get("lifeInfinite"):
        error_msg += LIFE_INVALID
    return error_msg


def validate_securities_act_access(account_id: str, statement: FinancingStatement) -> str:
    """Validate securities act registration type restricted access by account id."""
    error_msg: str = ""
    is_sec_act: bool = statement and statement.registration[0].registration_type == MiscellaneousTypes.SECURITIES_NOTICE
    if account_id and is_sec_act:
        parties = ClientCode.find_by_account_id(account_id, False, True)
        if not parties:
            error_msg += SE_ACCESS_INVALID
    return error_msg


def validate_securities_act_notices(statement: FinancingStatement, json_data: dict = None) -> str:
    """Validate securities act registration type amendment notices."""
    error_msg: str = ""
    if (
        not json_data
        or not statement
        or statement.registration[0].registration_type != MiscellaneousTypes.SECURITIES_NOTICE
    ):
        return error_msg
    if json_data.get("addSecuredParties") or json_data.get("deleteSecuredParties"):
        error_msg += SE_AMEND_SP_INVALID
    if json_data.get("deleteSecuritiesActNotices"):
        delete_count: int = len(json_data.get("deleteSecuritiesActNotices"))
        # logger.debug(f'Delete notice count = {delete_count}')
        if delete_count > reg_utils.get_securities_act_notices_count(statement, json_data):
            error_msg += SE_DELETE_INVALID
        for delete_notice in json_data.get("deleteSecuritiesActNotices"):
            if not delete_notice.get("noticeId"):
                error_msg += SE_DELETE_MISSING_ID
            else:
                notice_id: int = delete_notice.get("noticeId")
                notice = reg_utils.find_securities_notice_by_id(notice_id, statement)
                if not notice or notice.registration_id_end is not None:
                    error_msg += SE_DELETE_INVALID_ID.format(str(notice_id))
    return error_msg


def validate_pending_state(base_reg: Registration) -> str:
    """Verify base registration is not locked because of previous change pending payment completion."""
    error_msg: str = ""
    if base_reg and base_reg.ver_bypassed == REG_STATUS_LOCKED:
        error_msg += STATE_INVALID_PAY_LOCKED
    return error_msg
