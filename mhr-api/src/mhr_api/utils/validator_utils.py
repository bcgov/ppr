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
"""This module holds common registration validation functions.

Refactored from registration_validator.
"""
import copy

from mhr_api.models import MhrDraft, MhrRegistration, registration_json_utils
from mhr_api.models import registration_utils as reg_utils
from mhr_api.models import utils as model_utils
from mhr_api.models.type_tables import (
    MhrDocumentTypes,
    MhrLocationTypes,
    MhrNoteStatusTypes,
    MhrRegistrationStatusTypes,
    MhrRegistrationTypes,
    MhrStatusTypes,
)
from mhr_api.services import ltsa
from mhr_api.utils import valid_charset
from mhr_api.utils.logging import logger

HOME_DESCRIPTION_MIN_YEAR: int = 1900
DOC_ID_REQUIRED = "Document ID is required for staff registrations. "
DOC_ID_EXISTS = "Document ID must be unique: provided value already exists. "
DOC_ID_INVALID_CHECKSUM = "Document ID is invalid: checksum failed. "
STATE_FROZEN_PAYMENT = "Registration not allowed: a previous registration with a pending payment exists. "
STATE_NOT_ALLOWED = "The MH registration is not in a state where changes are allowed. "
STATE_FROZEN_AFFIDAVIT = "A transfer to a beneficiary is pending after an AFFIDAVIT transfer. "
STATE_FROZEN_NOTE = "Registration not allowed: this manufactured home has an active TAXN, NCON, or REST unit note. "
STATE_FROZEN_PERMIT = "Registration not allowed: this manufactured home has an active transport permit. "
STATE_FROZEN_EXEMPT = "Registration not allowed: this manufactured home has an active exemption registration. "
STATE_ACTIVE_PERMIT = (
    "New transport permit registration not allowed: an active permit registration exists. "
    + "Staff or the account that created the active transport permit can resubmit with moveCompleted set to true. "
)
DRAFT_NOT_ALLOWED = "The draft for this registration is out of date: delete the draft and resubmit. "
CHARACTER_SET_UNSUPPORTED = "The character set is not supported for {desc} value {value}. "
PPR_LIEN_EXISTS = (
    "This registration is not allowed to complete as an outstanding Personal Property Registry lien "
    + "exists on the manufactured home. "
)
LOCATION_PID_INVALID = (
    "Location PID verification failed: either the PID is invalid or the LTSA service is " + "unavailable. "
)
SUBMITTING_REQUIRED = "Submitting Party is required for MH registrations. "
DESCRIPTION_CSA_ENGINEER_REQUIRED = "Either a CSA number or engineer information is required for this registration. "
DESCRIPTION_MAKE_MODEL_REQUIRED = "Either description make or description model is required. "
DESCRIPTION_YEAR_INVALID = (
    "Description manufactured home year invalid: it must be between 1900 and 1 year after " + "the current year. "
)
DESCRIPTION_YEAR_REQUIRED = "Description manufactured home year is required. "
DESCRIPTION_INVALID_IDENTICAL = "The new description cannot be identical to the existing description. "
EXEMPT_EXNR_INVALID = "Registration not allowed: the home is exempt because of an existing non-residential exemption. "
EXEMPT_EXRS_INVALID = "Residential exemption registration not allowed: the home is already exempt. "
EXEMPT_PERMIT_INVALID = "Registration not allowed: the home is not exempt because of a transport permit location. "
MHR_NUMBER_INVALID = "MHR number {mhr_num} either is greater than the existng maximum MHR number or already exists. "
LOCATION_INVALID_IDENTICAL = "The new location cannot be identical to the existing location. "
LOCATION_DEALER_REQUIRED = "Location dealer/manufacturer name is required for this registration. "
LOCATION_PARK_NAME_REQUIRED = "Location park name is required for this registration. "
LOCATION_PARK_PAD_REQUIRED = "Location park PAD is required for this registration. "
LOCATION_STRATA_REQUIRED = "Location parcel ID or all of lot, plan, land district are required for this registration. "
LOCATION_OTHER_REQUIRED = (
    "Location parcel ID or all of lot, plan, land district or all of land district, district "
    + "lot are required for this registration. "
)
BAND_NAME_REQUIRED = "The location Indian Reserve band name is required for this registration. "
RESERVE_NUMBER_REQUIRED = "The location Indian Reserve number is required for this registration. "
LOCATION_MANUFACTURER_ALLOWED = (
    "Park name, PAD, band name, reserve number, parcel ID, and LTSA details are "
    + "not allowed with a MANUFACTURER location type. "
)
LOCATION_PARK_ALLOWED = (
    "Dealer/manufacturer name, band name, reserve number, parcel ID, and LTSA details are "
    + "not allowed with a MH_PARK location type. "
)
LOCATION_RESERVE_ALLOWED = "Dealer/manufacturer name, park name, and PAD are not allowed with a RESERVE location type. "
LOCATION_STRATA_ALLOWED = (
    "Dealer/manufacturer name, park name, PAD, band name, and reserve number are not allowed "
    + "with a STRATA location type. "
)
LOCATION_OTHER_ALLOWED = (
    "Dealer/manufacturer name, park name, PAD, band name, and reserve number are not allowed "
    + "with an OTHER location type. "
)
LOCATION_TAX_DATE_INVALID = "Location tax certificate date is invalid: it cannot be before the registration date. "
LOCATION_TAX_DATE_INVALID_QS = (
    "Location tax certificate date is invalid: it must be within the same year as the " + "current date. "
)
LOCATION_TAX_CERT_REQUIRED = "Location tax certificate and tax certificate expiry date are required. "
STATUS_CONFIRMATION_REQUIRED = "The land status confirmation is required for this registration. "
CANCEL_PERMIT_INVALID = "Cancel Transport Permit not allowed: no active, non-expired transport permit exists. "
PPR_REG_TYPE_ALL = " SA_TAX TA_TAX TM_TAX "
PPR_REG_TYPE_GOV = " SA_GOV TA_GOV TM_GOV "
PPR_REG_TYPE_EXEMPTION = PPR_REG_TYPE_ALL + PPR_REG_TYPE_GOV + " FR LT ML MN SG "
PPR_REG_TYPE_TRANSFER = PPR_REG_TYPE_ALL + PPR_REG_TYPE_GOV + " FR LT ML MN SG "
PPR_REG_TYPE_PERMIT = PPR_REG_TYPE_ALL + " LT ML MN "
PPR_RESTRICTED_REG_TYPES = {
    MhrRegistrationTypes.EXEMPTION_RES: PPR_REG_TYPE_EXEMPTION,
    MhrRegistrationTypes.TRANS: PPR_REG_TYPE_TRANSFER,
    MhrRegistrationTypes.PERMIT: PPR_REG_TYPE_PERMIT,
}


def validate_doc_id(json_data, check_exists: bool = True):
    """Validate the registration document id."""
    doc_id = json_data.get("documentId")
    logger.debug(f"Validating doc_id={doc_id}.")
    error_msg = ""
    if not doc_id:
        return error_msg
    # Staff generated doc ID's now have a length of 10 - skip checksum validation.
    if len(doc_id) == 8 and not checksum_valid(doc_id):
        error_msg += DOC_ID_INVALID_CHECKSUM
    if check_exists:
        exists_count = MhrRegistration.get_doc_id_count(doc_id)
        if exists_count > 0:
            error_msg += DOC_ID_EXISTS
    return error_msg


def checksum_valid(doc_id: str) -> bool:
    """Validate the document id with a checksum algorithm."""
    if not doc_id or len(doc_id) != 8:
        return False
    if doc_id.startswith("1") or doc_id.startswith("9") or doc_id.startswith("8") or doc_id.startswith("REG"):
        return True
    if not doc_id.isnumeric():
        return False
    dig1: int = int(doc_id[0:1])
    dig2: int = int(doc_id[1:2]) * 2
    dig3: int = int(doc_id[2:3])
    dig4: int = int(doc_id[3:4]) * 2
    dig5: int = int(doc_id[4:5])
    dig6: int = int(doc_id[5:6]) * 2
    dig7: int = int(doc_id[6:7])
    check_digit: int = int(doc_id[7:])
    dig_sum = dig1 + dig3 + dig5 + dig7
    if dig2 > 9:
        dig_sum += 1 + (dig2 % 10)
    else:
        dig_sum += dig2
    if dig4 > 9:
        dig_sum += 1 + (dig4 % 10)
    else:
        dig_sum += dig4
    if dig6 > 9:
        dig_sum += 1 + (dig6 % 10)
    else:
        dig_sum += dig6
    mod_sum = dig_sum % 10
    logger.debug(f"sum={dig_sum}, checkdigit= {check_digit}, mod_sum={mod_sum}")
    if mod_sum == 0:
        return mod_sum == check_digit
    return (10 - mod_sum) == check_digit


def validate_registration_state(  # pylint: disable=too-many-branches,too-many-return-statements
    reg: MhrRegistration,
    staff: bool,
    reg_type: str,
    doc_type: str = None,
    reg_json: dict = None,
):
    """Validate registration state: changes are only allowed on active homes."""
    error_msg = ""
    if not reg:
        return error_msg
    if reg and reg.status_type == MhrRegistrationStatusTypes.DRAFT:
        return STATE_FROZEN_PAYMENT
    if doc_type and doc_type == MhrDocumentTypes.EXRE:
        return validate_registration_state_reregister(reg)
    if reg_type and reg_type in (MhrRegistrationTypes.EXEMPTION_NON_RES, MhrRegistrationTypes.EXEMPTION_RES):
        return validate_registration_state_exemption(reg, reg_type, staff)
    if reg_type and reg_type == MhrRegistrationTypes.PERMIT:  # Prevent if active permit exists.
        if not doc_type or doc_type not in (MhrDocumentTypes.AMEND_PERMIT, MhrDocumentTypes.REG_103E):
            error_msg += validate_no_active_permit(reg, reg_json)
    if reg.status_type != MhrRegistrationStatusTypes.ACTIVE:
        if doc_type and doc_type == MhrDocumentTypes.EXRE:
            logger.debug(f"Allowing EXEMPT/CANCELLED state registration for doc type={doc_type}")
        elif (
            reg.status_type == MhrRegistrationStatusTypes.EXEMPT
            and doc_type
            and doc_type in (MhrDocumentTypes.PUBA, MhrDocumentTypes.REGC_STAFF, MhrDocumentTypes.REGC_CLIENT)
        ):
            logger.debug(f"Allowing EXEMPT state registration for doc type={doc_type}")
        elif (
            reg.status_type == MhrRegistrationStatusTypes.EXEMPT
            and doc_type
            and doc_type == MhrDocumentTypes.CANCEL_PERMIT
            and reg.change_registrations
        ):
            return check_state_cancel_permit(reg, error_msg)
        elif (
            reg.status_type == MhrRegistrationStatusTypes.EXEMPT
            and doc_type
            and doc_type in (MhrDocumentTypes.AMEND_PERMIT, MhrDocumentTypes.REG_103E)
            and reg.change_registrations
        ):
            return check_exempt_permit(reg, staff, error_msg)
        elif (
            reg.status_type == MhrRegistrationStatusTypes.CANCELLED
            or doc_type is None
            or doc_type
            not in (MhrDocumentTypes.NPUB, MhrDocumentTypes.NCON, MhrDocumentTypes.NCAN, MhrDocumentTypes.NRED)
        ):
            error_msg += STATE_NOT_ALLOWED
    elif reg.change_registrations:
        last_reg: MhrRegistration = reg.change_registrations[-1]
        if not staff and last_reg.registration_type == MhrRegistrationTypes.TRANS_AFFIDAVIT:
            error_msg += STATE_NOT_ALLOWED
        elif (
            staff
            and last_reg.registration_type == MhrRegistrationTypes.TRANS_AFFIDAVIT
            and (not reg_type or reg_type != MhrRegistrationTypes.TRANS)
        ):
            error_msg += STATE_NOT_ALLOWED
            error_msg += STATE_FROZEN_AFFIDAVIT
    return check_state_note(reg, staff, error_msg, reg_type, doc_type)


def validate_no_active_permit(registration: MhrRegistration, reg_json: dict) -> str:
    """Verify no existing acive transport permit exists on the home."""
    error_msg = ""
    if not registration or not registration.change_registrations:
        return error_msg
    if reg_json and reg_json.get("moveCompleted"):  # Skip rule check for all users if true.
        return error_msg
    for reg in registration.change_registrations:
        if (
            reg.notes
            and reg.notes[0]
            and reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE
            and reg.notes[0].document_type == MhrDocumentTypes.REG_103
            and not reg.notes[0].is_expired()
        ):
            error_msg = STATE_ACTIVE_PERMIT
    return error_msg


def validate_registration_state_reregister(registration: MhrRegistration):
    """Validate registration state for re-register a cancelled/exempt home requests."""
    error_msg = ""
    if registration and registration.status_type and registration.status_type == MhrRegistrationStatusTypes.ACTIVE:
        return STATE_NOT_ALLOWED
    return error_msg


def validate_registration_state_exemption(registration: MhrRegistration, reg_type: str, staff: bool):
    """Validate registration state for residential/non-residential exemption requests."""
    error_msg = ""
    if registration.status_type:
        if registration.status_type == MhrRegistrationStatusTypes.ACTIVE:
            return check_state_note(registration, staff, error_msg, reg_type)
        if registration.status_type == MhrRegistrationStatusTypes.CANCELLED:
            error_msg += STATE_NOT_ALLOWED
        elif reg_type == MhrRegistrationTypes.EXEMPTION_RES:
            error_msg += EXEMPT_EXRS_INVALID
    return error_msg


def validate_draft_state(json_data):
    """Validate draft state: no change registration on the home after the draft was created."""
    error_msg = ""
    if not json_data.get("draftNumber"):
        return error_msg
    draft: MhrDraft = MhrDraft.find_by_draft_number(json_data.get("draftNumber"))
    if draft and draft.stale_count > 0:
        error_msg += DRAFT_NOT_ALLOWED
    return error_msg


def validate_submitting_party(json_data):
    """Verify submitting party names are valid."""
    error_msg = ""
    if not json_data.get("submittingParty"):
        return SUBMITTING_REQUIRED
    party = json_data.get("submittingParty")
    desc: str = "submitting party"
    if party.get("businessName"):
        error_msg += validate_text(party.get("businessName"), desc + " business name")
    elif party.get("personName"):
        error_msg += validate_individual_name(party.get("personName"), desc)
    return error_msg


def validate_party(party: dict, desc: str):
    """Verify party names are valid."""
    error_msg = ""
    if party.get("businessName"):
        error_msg += validate_text(party.get("businessName"), desc + " business name")
    elif party.get("personName"):
        error_msg += validate_individual_name(party.get("personName"), desc + " person name")
    return error_msg


def validate_individual_name(name_json, desc: str = ""):
    """Verify individual name is valid."""
    error_msg = validate_text(name_json.get("first"), desc + " first")
    error_msg += validate_text(name_json.get("last"), desc + " last")
    error_msg += validate_text(name_json.get("middle"), desc + " middle")
    return error_msg


def validate_text(value: str, desc: str = ""):
    """Verify text characters are valid."""
    if value and not valid_charset(value):
        return CHARACTER_SET_UNSUPPORTED.format(desc=desc, value=value)
    return ""


def validate_ppr_lien(mhr_number: str, mhr_reg_type: str, staff: bool) -> str:
    """Validate that there are no PPR liens for a change registration."""
    logger.debug(f"Validating mhr_number={mhr_number} mhr_reg_type={mhr_reg_type} staff={staff}.")
    error_msg = ""
    if staff or not mhr_number or not mhr_reg_type or not PPR_RESTRICTED_REG_TYPES.get(mhr_reg_type):
        return error_msg
    ppr_reg_type: str = reg_utils.get_ppr_registration_type(mhr_number)
    if ppr_reg_type:
        restricted_reg_types: str = PPR_RESTRICTED_REG_TYPES.get(mhr_reg_type)
        logger.debug(f"Found PPR reg type {ppr_reg_type}, checking against {restricted_reg_types}")
        if restricted_reg_types.find((ppr_reg_type + " ")) > 0:
            error_msg += PPR_LIEN_EXISTS
    return error_msg


def get_existing_location(registration: MhrRegistration) -> dict:
    """Get the currently active location JSON."""
    if not registration:
        return {}
    if registration.locations and registration.locations[0].status_type == MhrStatusTypes.ACTIVE:
        return registration.locations[0].json
    if registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.locations and reg.locations[0].status_type == MhrStatusTypes.ACTIVE:
                return reg.locations[0].json
    return {}


def get_existing_description(registration: MhrRegistration) -> dict:
    """Get the currently active description JSON."""
    if not registration:
        return {}
    description = None
    if registration.descriptions and registration.descriptions[0].status_type == MhrStatusTypes.ACTIVE:
        description = registration.descriptions[0]
    elif registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.descriptions and reg.descriptions[0].status_type == MhrStatusTypes.ACTIVE:
                description = reg.descriptions[0]
    if description:
        description_json = description.json
        description_json["sections"] = registration_json_utils.get_sections_json(
            registration, description.registration_id
        )
        return description_json
    return {}


def get_permit_count(mhr_number: str, name: str) -> int:
    """Execute a query to count existing transport permit registrations on a home."""
    return reg_utils.get_permit_count(mhr_number, name)


def validate_pid(pid: str):
    """Validate location pid exists with an LTSA lookup."""
    error_msg = ""
    if not pid:
        return error_msg
    lookup_result = ltsa.pid_lookup(pid)
    if not lookup_result:
        error_msg = LOCATION_PID_INVALID
    return error_msg


def check_state_note(
    registration: MhrRegistration, staff: bool, error_msg: str, reg_type: str, doc_type: str = None
) -> str:
    """Check registration state for non-staff: frozen if active TAXN, NCON, or REST unit note."""
    if not registration or staff:
        return error_msg
    if registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.notes:
                if (
                    reg.notes[0].document_type in (MhrDocumentTypes.TAXN, MhrDocumentTypes.NCON, MhrDocumentTypes.REST)
                    and reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE
                ):
                    error_msg += STATE_FROZEN_NOTE
                # STATE_FROZEN_PERMIT rule removed for QS residential exemptions 21424.
                elif (
                    reg.registration_type in (MhrRegistrationTypes.PERMIT, MhrRegistrationTypes.PERMIT_EXTENSION)
                    and reg_type
                    not in (
                        MhrRegistrationTypes.PERMIT,
                        MhrRegistrationTypes.PERMIT_EXTENSION,
                        MhrRegistrationTypes.EXEMPTION_RES,
                    )
                    and reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE
                    and not model_utils.is_transfer(reg_type)
                    and not reg.notes[0].is_expired()
                ):
                    if not doc_type or doc_type != MhrDocumentTypes.CANCEL_PERMIT:
                        error_msg += STATE_FROZEN_PERMIT
    return error_msg


def check_state_cancel_permit(registration: MhrRegistration, error_msg: str) -> str:
    """Check no active exemption registration exists: cancel permit not allowed in this state."""
    if not registration:
        return error_msg
    if registration.change_registrations:
        for reg in registration.change_registrations:
            if (
                reg.notes
                and reg.notes[0].document_type in (MhrDocumentTypes.EXRS, MhrDocumentTypes.EXMN, MhrDocumentTypes.EXNR)
                and reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE
            ):
                error_msg += STATE_FROZEN_EXEMPT
    return error_msg


def check_exempt_permit(registration: MhrRegistration, staff: bool, error_msg: str) -> str:
    """Check home is exempt because active permit location is outside of BC."""
    if not registration or staff:
        return error_msg
    if not registration.change_registrations:
        error_msg += EXEMPT_PERMIT_INVALID
        return error_msg
    for reg in registration.change_registrations:
        if (
            reg.notes
            and reg.notes[0].document_type
            in (MhrDocumentTypes.REG_103, MhrDocumentTypes.AMEND_PERMIT, MhrDocumentTypes.REG_103E)
            and reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE
        ):
            if (
                reg.locations
                and reg.locations[0].status_type == MhrStatusTypes.ACTIVE
                and reg.locations[0].address
                and reg.locations[0].address.region != "BC"
            ):
                logger.debug("Exempt because transport permit location not BC.")
                return error_msg
    error_msg += EXEMPT_PERMIT_INVALID
    return error_msg


def valid_manufacturer_year(year: int) -> bool:
    """Check if a manufacturer MH home year is within 1 year of the current year."""
    now = model_utils.now_ts()
    return now.year in (year, year + 1, year - 1)


def valid_description_year(year: int, staff: bool) -> bool:
    """Check if a MH home year is within a valid range year."""
    if not staff:
        return valid_manufacturer_year(year)
    if year < HOME_DESCRIPTION_MIN_YEAR:
        return False
    now = model_utils.now_ts()
    return year <= (now.year + 1)


def validate_description(description, staff: bool):
    """Verify the description values."""
    error_msg = ""
    if not description:
        return error_msg
    if description.get("baseInformation"):
        base_info = description.get("baseInformation")
        if not base_info.get("year"):
            error_msg += DESCRIPTION_YEAR_REQUIRED
        elif not valid_description_year(base_info.get("year"), staff):
            error_msg += DESCRIPTION_YEAR_INVALID
        if not base_info.get("make") and not base_info.get("model"):
            error_msg += DESCRIPTION_MAKE_MODEL_REQUIRED
    if not staff and not description.get("csaNumber") and not description.get("engineerDate"):
        error_msg += DESCRIPTION_CSA_ENGINEER_REQUIRED
    return error_msg


def validate_mhr_number(mhr_number: str, staff: bool) -> str:
    """Validate that a staff provide new MH mhr number is valid."""
    error_msg = ""
    if not staff or not mhr_number:
        return error_msg
    if not reg_utils.validate_mhr_number(mhr_number):
        error_msg += MHR_NUMBER_INVALID.format(mhr_num=mhr_number)
    return error_msg


def validate_location_different(current_loc: dict, new_loc: dict) -> str:
    """Verify the new location is not identical to the existing location."""
    error_msg = ""
    if not current_loc or not new_loc:
        return error_msg
    loc_1 = copy.deepcopy(current_loc)
    loc_2 = copy.deepcopy(new_loc)
    loc_1["status"] = ""
    loc_1["locationId"] = ""
    loc_1["leaveProvince"] = False
    loc_2["status"] = ""
    loc_2["locationId"] = ""
    loc_2["leaveProvince"] = False
    if (
        loc_1.get("address")
        and loc_1["address"].get("postalCode")
        and str(loc_1["address"]["postalCode"]).strip() == ""
    ):
        del loc_1["address"]["postalCode"]
    if (
        loc_2.get("address")
        and loc_2["address"].get("postalCode")
        and str(loc_2["address"]["postalCode"]).strip() == ""
    ):
        del loc_2["address"]["postalCode"]
    if loc_1 == loc_2:
        error_msg += LOCATION_INVALID_IDENTICAL
    return error_msg


def validate_description_different(current_description: dict, new_description: dict) -> str:
    """Verify the new description is not identical to the existing description."""
    error_msg = ""
    if not current_description or not new_description:
        return error_msg
    desc_1 = copy.deepcopy(current_description)
    desc_2 = copy.deepcopy(new_description)
    desc_1["status"] = ""
    desc_2["status"] = ""
    if desc_2.get("baseInformation"):
        base_1 = desc_1.get("baseInformation")
        base_2 = desc_2.get("baseInformation")
        if not base_1.get("model") and base_2.get("model"):
            base_2["make"] = base_2["make"] + " " + base_2.get("model")
            del base_2["model"]
    if desc_1 == desc_2:
        error_msg += DESCRIPTION_INVALID_IDENTICAL
    return error_msg


def validate_location(location):  # pylint: disable=too-many-branches
    """Verify the combination of location values is valid."""
    error_msg = ""
    if not location or not location.get("locationType"):  # No point validating if no no required locationType.
        return error_msg
    loc_type = location["locationType"]
    if loc_type == MhrLocationTypes.RESERVE:
        if not location.get("bandName"):
            error_msg += BAND_NAME_REQUIRED
        if not location.get("reserveNumber"):
            error_msg += RESERVE_NUMBER_REQUIRED
    elif loc_type == MhrLocationTypes.MANUFACTURER:
        if not location.get("dealerName"):
            error_msg += LOCATION_DEALER_REQUIRED
    elif loc_type == MhrLocationTypes.MH_PARK:
        if not location.get("parkName"):
            error_msg += LOCATION_PARK_NAME_REQUIRED
        if not location.get("pad"):
            error_msg += LOCATION_PARK_PAD_REQUIRED
    elif loc_type == MhrLocationTypes.STRATA:
        if not location.get("pidNumber") and (
            not location.get("lot") or not location.get("plan") or not location.get("landDistrict")
        ):
            error_msg += LOCATION_STRATA_REQUIRED
    elif loc_type == MhrLocationTypes.OTHER and not location.get("pidNumber"):
        if not location.get("landDistrict"):
            error_msg += LOCATION_OTHER_REQUIRED
        elif location.get("plan") and location.get("lot"):
            error_msg += ""
        elif not location.get("districtLot"):
            error_msg += LOCATION_OTHER_REQUIRED
    error_msg += validate_location_allowed(location, loc_type)
    return error_msg


def validate_location_allowed(location, loc_type):
    """Verify the allowed location values by location type."""
    error_msg = ""
    if loc_type == MhrLocationTypes.MANUFACTURER:
        if (
            location.get("bandName")
            or location.get("parkName")
            or location.get("reserveNumber")
            or location.get("pad")
            or has_location_ltsa_details(location)
        ):
            error_msg = LOCATION_MANUFACTURER_ALLOWED
    elif loc_type == MhrLocationTypes.MH_PARK and (
        location.get("bandName")
        or location.get("reserveNumber")
        or location.get("dealerName")
        or has_location_ltsa_details(location)
    ):
        error_msg = LOCATION_PARK_ALLOWED
    elif loc_type == MhrLocationTypes.RESERVE and (
        location.get("dealerName") or location.get("parkName") or location.get("pad")
    ):
        error_msg = LOCATION_RESERVE_ALLOWED
    elif loc_type in (MhrLocationTypes.STRATA, MhrLocationTypes.OTHER):
        if (
            location.get("dealerName")
            or location.get("parkName")
            or location.get("pad")
            or location.get("bandName")
            or location.get("reserveNumber")
        ):
            if loc_type == MhrLocationTypes.STRATA:
                error_msg = LOCATION_STRATA_ALLOWED
            else:
                error_msg = LOCATION_OTHER_ALLOWED
    return error_msg


def has_location_ltsa_details(location) -> bool:
    """Verify the location has ltsa detail properties."""
    if (
        location.get("lot")
        or location.get("parcel")
        or location.get("block")
        or location.get("districtLot")
        or location.get("partOf")
    ):
        return True
    if (
        location.get("section")
        or location.get("township")
        or location.get("range")
        or location.get("plan")
        or location.get("meridian")
    ):
        return True
    if location.get("pidNumber") or location.get("legalDescription") or location.get("landDistrict"):
        return True
    return False


def validate_tax_certificate(request_location: dict, current_location: dict, staff: bool) -> str:
    """Validate transport permit business rules specific to a tax certificate."""
    error_msg = ""
    if staff:  # Skip for staff.
        return error_msg
    if request_location and request_location.get("taxExpiryDate"):
        tax_ts = model_utils.ts_from_iso_format(request_location.get("taxExpiryDate"))
        current_ts = model_utils.now_ts()
        if not model_utils.valid_tax_cert_date(current_ts, tax_ts):
            error_msg += LOCATION_TAX_DATE_INVALID
        elif not request_location.get("taxCertificate"):
            error_msg += LOCATION_TAX_CERT_REQUIRED
        if not staff and tax_ts.year != current_ts.year:
            error_msg += LOCATION_TAX_DATE_INVALID_QS
    else:
        if current_location and current_location.get("dealerName"):
            return error_msg
        if current_location.get("parkName") and request_location.get("parkName"):
            park_1 = current_location.get("parkName").strip().upper()
            park_2 = request_location.get("parkName").strip().upper()
            if park_1 == park_2:
                return error_msg
        # Current location out of province: no tax certificate required.
        if current_location["address"].get("region") != model_utils.PROVINCE_BC:
            return error_msg
        error_msg += LOCATION_TAX_CERT_REQUIRED
    return error_msg


def has_active_permit(registration: MhrRegistration) -> bool:
    """Verify an existing transport permit exists on the home."""
    if not registration:
        return False
    if not registration.change_registrations:
        return False
    for reg in registration.change_registrations:
        if (
            reg.notes
            and reg.notes[0]
            and reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE
            and reg.notes[0].document_type
            in (MhrDocumentTypes.REG_103, MhrDocumentTypes.REG_103E, MhrDocumentTypes.AMEND_PERMIT)
            and not reg.notes[0].is_expired()
        ):
            return True
    return False


def validate_cancel_permit(registration: MhrRegistration) -> str:
    """Validate an active, unexpired transport permit exists."""
    error_msg: str = ""
    if not registration:
        return error_msg
    if not has_active_permit(registration):
        error_msg += CANCEL_PERMIT_INVALID
    return error_msg
