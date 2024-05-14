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
# from flask import current_app

from ppr_api.models import ClientCode, FinancingStatement, registration_utils as reg_utils, utils as model_utils, \
    VehicleCollateral
from ppr_api.models.registration import MiscellaneousTypes


COURT_ORDER_INVALID = 'CourtOrderInformation is not allowed with a base registration type of {}. '
COURT_ORDER_MISSING = 'Required courtOrderInformation is missing. '
COURT_ORDER_INVALID_DATE = 'Invalid courtOrderInformation.orderDate: the value must be between the base ' + \
                           'registration date and the current system date. '
AUTHORIZATION_INVALID = 'Authorization Received indicator is required with this registration. '
DELETE_MISSING_ID_VEHICLE = 'Required vehicleId missing in delete Vehicle Collateral. '
DELETE_MISSING_ID_GENERAL = 'Required collateralId missing in delete General Collateral. '
DELETE_INVALID_ID_VEHICLE = 'Invalid vehicleId {} in delete Vehicle Collateral. '
DELETE_INVALID_ID_GENERAL = 'Invalid collateralId {} in delete General Collateral. '
LI_NOT_ALLOWED = 'Life Infinite is not allowed with this registration type. '
RENEWAL_INVALID = 'Renewal registration is now allowed: the base registration has an infinite life. '
LIFE_MISSING = 'Either Life Years or Life Infinite is required with this registration type. '
LIFE_INVALID = 'Only one of Life Years or Life Infinite is allowed. '
VC_AP_NOT_ALLOWED = 'Vehicle Collateral type AP is not allowed. '
SE_ACCESS_INVALID = 'Not authorized: the Securities Act Notice SE type is restricted by account ID. '
SE_AMEND_SP_INVALID = 'Secured Parties may not be changed when amending a Securities Act Notice. '
SE_DELETE_INVALID = 'At least one Securities Act Notice is required. '
SE_DELETE_MISSING_ID = 'Required noticeId missing in delete Securities Act Notice. '
SE_DELETE_INVALID_ID = 'Invalid deleteId {} in delete Securities Act Notice. '


def validate_registration(json_data: dict, account_id: str, financing_statement=None):
    """Perform all registration data validation checks not covered by schema validation."""
    error_msg = ''
    if 'authorizationReceived' not in json_data or not json_data['authorizationReceived']:
        error_msg += AUTHORIZATION_INVALID
    error_msg += validate_collateral(json_data, financing_statement)
    error_msg += validate_securities_act_access(account_id, financing_statement)
    error_msg += validate_securities_act_notices(financing_statement, json_data)
    return error_msg


def validate_renewal(json_data, financing_statement):
    """Perform all renewal registration data validation checks not covered by schema validation."""
    error_msg = ''
    if 'authorizationReceived' not in json_data or not json_data['authorizationReceived']:
        error_msg += AUTHORIZATION_INVALID

    if not financing_statement:
        return error_msg

    error_msg += validate_life(json_data, financing_statement)
    if model_utils.REG_TYPE_REPAIRER_LIEN == financing_statement.registration[0].registration_type:
        if 'courtOrderInformation' not in json_data:
            error_msg += COURT_ORDER_MISSING
        elif 'orderDate' in json_data['courtOrderInformation'] and \
                len(json_data['courtOrderInformation']['orderDate']) >= 10:
            co_date = json_data['courtOrderInformation']['orderDate']
            # order date must be between base registration date and current date.
            if not model_utils.valid_court_order_date(financing_statement.registration[0].registration_ts, co_date):
                error_msg += COURT_ORDER_INVALID_DATE
    elif 'courtOrderInformation' in json_data:
        error_msg += COURT_ORDER_INVALID.format(financing_statement.registration[0].registration_type)
    return error_msg


def validate_collateral(json_data, financing_statement=None):
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

    if 'addVehicleCollateral' in json_data:
        for collateral in json_data['addVehicleCollateral']:
            if 'type' in collateral and collateral['type'] == VehicleCollateral.SerialTypes.AIRPLANE.value:
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


def validate_life(json_data, financing_statement):
    """Validate renewal lifeYears and lifeInfinite by registration type."""
    error_msg = ''
    reg_type = financing_statement.registration[0].registration_type
    if financing_statement.life == model_utils.LIFE_INFINITE:
        error_msg += RENEWAL_INVALID
    elif reg_type == model_utils.REG_TYPE_REPAIRER_LIEN and 'lifeInfinite' in json_data and json_data['lifeInfinite']:
        error_msg += LI_NOT_ALLOWED
    elif reg_type != model_utils.REG_TYPE_REPAIRER_LIEN and 'lifeYears' not in json_data and \
            'lifeInfinite' not in json_data:
        error_msg += LIFE_MISSING
    elif json_data.get('lifeYears', -1) > 0 and json_data.get('lifeInfinite'):
        error_msg += LIFE_INVALID

    return error_msg


def validate_securities_act_access(account_id: str, statement: FinancingStatement) -> str:
    """Validate securities act registration type restricted access by account id."""
    error_msg = ''
    is_sec_act: bool = statement and statement.registration[0].registration_type == MiscellaneousTypes.SECURITIES_NOTICE
    if account_id and is_sec_act:
        parties = ClientCode.find_by_account_id(account_id, False, True)
        if not parties:
            error_msg += SE_ACCESS_INVALID
    return error_msg


def validate_securities_act_notices(statement: FinancingStatement, json_data: dict = None) -> str:
    """Validate securities act registration type amendment notices."""
    error_msg = ''
    if not json_data or not statement or \
            statement.registration[0].registration_type != MiscellaneousTypes.SECURITIES_NOTICE:
        return error_msg
    if json_data.get('addSecuredParties') or json_data.get('deleteSecuredParties'):
        error_msg += SE_AMEND_SP_INVALID
    if json_data.get('deleteSecuritiesActNotices'):
        delete_count: int = len(json_data.get('deleteSecuritiesActNotices'))
        # current_app.logger.debug(f'Delete notice count = {delete_count}')
        if delete_count > reg_utils.get_securities_act_notices_count(statement, json_data):
            error_msg += SE_DELETE_INVALID
        for delete_notice in json_data.get('deleteSecuritiesActNotices'):
            if not delete_notice.get('noticeId'):
                error_msg += SE_DELETE_MISSING_ID
            else:
                notice_id: int = delete_notice.get('noticeId')
                notice = reg_utils.find_securities_notice_by_id(notice_id, statement)
                if not notice or notice.registration_id_end is not None:
                    error_msg += SE_DELETE_INVALID_ID.format(str(notice_id))
    return error_msg
