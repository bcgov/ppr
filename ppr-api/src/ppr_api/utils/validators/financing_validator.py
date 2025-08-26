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
"""This module holds non-party financing validation for rules not covered by the schema.

Validation includes rules captured in the PPR Registration Types spreadsheet:
https://docs.google.com/spreadsheets/d/18eTumnf5H6TG2qWXwXJ_iAA-Gc7iNMpnm0ly7ctceTI/edit#gid=0
"""
# pylint: disable=superfluous-parens

from ppr_api.models import ClientCode, VehicleCollateral
from ppr_api.models import utils as model_utils
from ppr_api.models.registration import MiscellaneousTypes, PPSATypes

# Error messages
AUTHORIZATION_INVALID = "The registration must include an authorization received indicator. "
TYPE_NOT_ALLOWED = "The selected registration type does not support creating a new Financing Statement. "
GC_NOT_ALLOWED = "General Collateral cannot be included with this registration type. "
GC_REQUIRED = "This registration type requires General Collateral. "
LA_NOT_ALLOWED = "This registration type does not support specifying a lien amount. "
LY_NOT_ALLOWED = "This registration type does not support specifying life in years. "
LI_NOT_ALLOWED = "This registration type does not support infinite life. "
LI_INVALID = "Infinite life must be set to true for this registration type. "
LIFE_MISSING = "Specify either life in years or infinite life for this registration type. "
LIFE_INVALID = "Specify one: either life in years or infinite life. "
OT_MISSING_DESCRIPTION = "Provide a description when using OT Other Type. "
OT_NOT_ALLOWED = "This registration type does not support Other Type Description. "
RL_AMOUNT_REQUIRED = "Lien Amount is required with a Repairer's Lien. "
RL_AMOUNT_INVALID = "The Lien Amount must be a number greater than 0. "
RL_DATE_REQUIRED = "Surrender Date is required with a Repairer's Lien. "
RL_DATE_INVALID = "The Surrender Date cannot be more than 21 days in the past. "
SD_NOT_ALLOWED = "Surrender Date cannot be used with this registration type. "
TI_NOT_ALLOWED = "Trust Indenture is not applicable for this registration type. "
VC_NOT_ALLOWED = "Vehicle Collateral cannot be included with this registration type. "
VC_REQUIRED = "This registration type requires Vehicle Collateral. "
VC_MH_ONLY = "Only MH type Vehicle Collateral is permitted for this registration type. "
VC_MH_NOT_ALLOWED = "MH type Vehicle Collateral is not permitted for this registration type. "
VC_AP_NOT_ALLOWED = "AP type Vehicle Collateral is not allowed. "
SE_NOTICES_MISSING = "SE type registrations must include securitiesActNotices data. "
SE_SECURED_COUNT_INVALID = "Only one Secured Party is allowed for SE type registrations. "
SE_ACCESS_INVALID = "The account ID does not have permission to register SE type notices. "
SE_RP_MISSING_CODE = "Registering Party for SE registration type must use a valid account party code. "
SE_SP_MISSING_CODE = "Secured Party for SE registration type must use a valid account party code. "
SE_RP_INVALID_CODE = "The client party code for Registering Party in SE registration type is not valid. "
SE_SP_INVALID_CODE = "The client party code for Secured Party in SE registration type is invalid. "
RL_NOT_ALLOWED = "The RL lien type is not permitted; use CL Commercial Lien type instead. "
CL_NOT_ALLOWED = "The Commercial Lien CL type is not allowed: use the RL Repairer's Lien type instead. "

GC_NOT_ALLOWED_LIST = [
    MiscellaneousTypes.MH_NOTICE.value,
    PPSATypes.MARRIAGE_SEPARATION.value,
    PPSATypes.REPAIRER_LIEN.value,
    PPSATypes.MH_LIEN.value,
    PPSATypes.LAND_TAX.value,
]
GC_ONLY_LIST = [
    PPSATypes.FORESTRY_CHARGE.value,
    PPSATypes.FORESTRY_LIEN.value,
    PPSATypes.FORESTRY_SUB_CHARGE.value,
    MiscellaneousTypes.HC_NOTICE.value,
    MiscellaneousTypes.WAGES_UNPAID.value,
]
VC_REQUIRED_LIST = [
    MiscellaneousTypes.MH_NOTICE.value,
    PPSATypes.MARRIAGE_SEPARATION.value,
    PPSATypes.REPAIRER_LIEN.value,
    PPSATypes.MH_LIEN.value,
    PPSATypes.LAND_TAX.value,
]
VC_MH_ONLY_LIST = [
    MiscellaneousTypes.MH_NOTICE.value,
    PPSATypes.MARRIAGE_SEPARATION.value,
    PPSATypes.MH_LIEN.value,
    PPSATypes.LAND_TAX.value,
]
LIFE_INFINITE_LIST = [PPSATypes.MARRIAGE_SEPARATION.value, PPSATypes.MH_LIEN.value, PPSATypes.LAND_TAX.value]


def validate(json_data: dict, account_id: str) -> str:
    """Apply validation rules for all financing statement registration types."""
    error_msg = ""
    try:
        if "type" not in json_data:
            return error_msg

        reg_type = json_data["type"]
        error_msg = validate_allowed_type(reg_type)
        if error_msg != "":
            return error_msg

        reg_class = get_registration_class(reg_type)
        if reg_class is None:
            return error_msg

        if "authorizationReceived" not in json_data or not json_data["authorizationReceived"]:
            error_msg += AUTHORIZATION_INVALID
        error_msg += validate_life(json_data, reg_type, reg_class)
        error_msg += validate_vehicle_collateral(json_data, reg_type)
        error_msg += validate_general_collateral(json_data, reg_type, reg_class)
        error_msg += validate_trust_indenture(json_data, reg_type)
        error_msg += validate_other_description(json_data, reg_type)
        if "lienAmount" in json_data and json_data["lienAmount"]:
            error_msg = LA_NOT_ALLOWED
        if "surrenderDate" in json_data and json_data["surrenderDate"]:
            error_msg += SD_NOT_ALLOWED
        if reg_type == model_utils.REG_TYPE_SECURITIES_NOTICE:
            error_msg += validate_securities_act(json_data, account_id)
        return error_msg
    except ValueError:
        return error_msg


def validate_securities_act(json_data: dict, account_id: str) -> str:  # pylint: disable=too-many-branches; 1 more
    """Validate rules specific to the securities act registration type."""
    error_msg = ""
    if not json_data.get("securitiesActNotices"):
        error_msg += SE_NOTICES_MISSING
    if json_data.get("securedParties") and len(json_data["securedParties"]) > 1:
        error_msg += SE_SECURED_COUNT_INVALID
    parties = ClientCode.find_by_account_id(account_id, False, True)
    if not parties:
        error_msg += SE_ACCESS_INVALID
    else:
        rp_code = None
        sp_code = None
        if json_data.get("registeringParty") and not json_data["registeringParty"].get("code"):
            error_msg += SE_RP_MISSING_CODE
        else:
            rp_code = json_data["registeringParty"].get("code")
        if json_data.get("securedParties") and not json_data["securedParties"][0].get("code"):
            error_msg += SE_SP_MISSING_CODE
        else:
            sp_code = json_data["securedParties"][0].get("code")
        for client_party in parties:
            if client_party.get("code") == rp_code:
                rp_code = "found"
            if client_party.get("code") == sp_code:
                sp_code = "found"
        if rp_code and rp_code != "found":
            error_msg += SE_RP_INVALID_CODE
        if sp_code and sp_code != "found":
            error_msg += SE_SP_INVALID_CODE
    return error_msg


def validate_life(json_data, reg_type: str, reg_class: str):
    """Validate lifeYears and lifeInfinite by registration type."""
    error_msg = ""
    if reg_type in LIFE_INFINITE_LIST or reg_class in (model_utils.REG_CLASS_CROWN, model_utils.REG_CLASS_MISC):
        if "lifeYears" in json_data:
            error_msg = LY_NOT_ALLOWED
        if "lifeInfinite" in json_data and not json_data["lifeInfinite"]:
            error_msg += LI_INVALID
    elif "lifeYears" not in json_data and "lifeInfinite" not in json_data:
        error_msg += LIFE_MISSING
    elif json_data.get("lifeYears", -1) > 0 and json_data.get("lifeInfinite"):
        error_msg += LIFE_INVALID
    return error_msg


def validate_general_collateral(json_data, reg_type: str, reg_class: str):
    """Validate generalCollateral by registration type."""
    error_msg = ""
    if reg_type in GC_NOT_ALLOWED_LIST and "generalCollateral" in json_data and json_data["generalCollateral"]:
        error_msg = GC_NOT_ALLOWED
    elif (reg_class == model_utils.REG_CLASS_CROWN or reg_type in GC_ONLY_LIST) and (
        "generalCollateral" not in json_data
        or not json_data["generalCollateral"]
        or str(json_data["generalCollateral"][0]).strip() == ""
    ):
        error_msg = GC_REQUIRED

    return error_msg


def validate_vehicle_collateral(json_data, reg_type: str):
    """Validate vehicleCollateral by registration type."""
    error_msg = ""
    if (
        reg_type in GC_ONLY_LIST
        and reg_type != MiscellaneousTypes.WAGES_UNPAID.value
        and "vehicleCollateral" in json_data
        and json_data["vehicleCollateral"]
    ):
        error_msg = VC_NOT_ALLOWED
    elif reg_type in VC_REQUIRED_LIST and ("vehicleCollateral" not in json_data or not json_data["vehicleCollateral"]):
        error_msg = VC_REQUIRED
    elif reg_type in VC_MH_ONLY_LIST:
        for collateral in json_data["vehicleCollateral"]:
            if "type" in collateral and collateral["type"] != VehicleCollateral.SerialTypes.MANUFACTURED_HOME.value:
                error_msg = VC_MH_ONLY
    elif reg_type == model_utils.REG_TYPE_REPAIRER_LIEN:
        for collateral in json_data["vehicleCollateral"]:
            if "type" in collateral and collateral["type"] == VehicleCollateral.SerialTypes.MANUFACTURED_HOME.value:
                error_msg = VC_MH_NOT_ALLOWED
    if "vehicleCollateral" in json_data and json_data["vehicleCollateral"]:
        for collateral in json_data["vehicleCollateral"]:
            if "type" in collateral and collateral["type"] == VehicleCollateral.SerialTypes.AIRPLANE.value:
                error_msg += VC_AP_NOT_ALLOWED

    return error_msg


def validate_other_description(json_data, reg_type: str):
    """Validate otherTypeDescription by registration type."""
    if reg_type == model_utils.REG_TYPE_OTHER and (
        "otherTypeDescription" not in json_data or str(json_data["otherTypeDescription"]).strip() == ""
    ):
        return OT_MISSING_DESCRIPTION
    if reg_type != model_utils.REG_TYPE_OTHER and (
        "otherTypeDescription" in json_data and str(json_data["otherTypeDescription"]).strip() != ""
    ):
        return OT_NOT_ALLOWED
    return ""


def validate_trust_indenture(json_data, reg_type: str):
    """Validate trustIndenture by registration type."""
    if reg_type != model_utils.REG_TYPE_SECURITY_AGREEMENT and "trustIndenture" in json_data:
        return TI_NOT_ALLOWED
    return ""


def validate_allowed_type(reg_type: str) -> str:
    """Check if the submitted type is allowed for new financing statements."""
    try:
        test = model_utils.REG_TYPE_NEW_FINANCING_EXCLUDED[reg_type]
        if test:
            return TYPE_NOT_ALLOWED
        return ""
    except KeyError:
        return ""


def get_registration_class(reg_type: str):
    """Derive the registration class from the registration type."""
    try:
        if (reg_class := model_utils.REG_TYPE_TO_REG_CLASS[reg_type]) in (
            model_utils.REG_CLASS_CROWN,
            model_utils.REG_CLASS_MISC,
            model_utils.REG_CLASS_PPSA,
        ):
            return reg_class

        return ""
    except KeyError:
        return ""
