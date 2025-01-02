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
"""This module holds owner group and owner validation functions.

Refactored from validator_utils.
"""
from mhr_api.models import MhrOwnerGroup, MhrParty, MhrRegistration
from mhr_api.models import registration_utils as reg_utils
from mhr_api.models.registration_json_utils import is_identical_owner_name
from mhr_api.models.type_tables import MhrOwnerStatusTypes, MhrPartyTypes, MhrRegistrationTypes, MhrTenancyTypes
from mhr_api.utils.logging import logger

from .validator_utils import validate_individual_name, validate_text

DELETE_GROUP_ID_INVALID = "The owner group with ID {group_id} is not active and cannot be changed. "
DELETE_GROUP_ID_NONEXISTENT = "No owner group with ID {group_id} exists. "
DELETE_GROUP_TYPE_INVALID = "The owner group tenancy type with ID {group_id} is invalid. "
DELETE_GROUPS_MISSING = "The delete owner groups are required. "
DELETE_GROUP_ID_MISSING = "Delete owner group ID is missing. "
GROUP_INTEREST_MISMATCH = "The owner group interest numerator sum does not equal the interest common denominator. "
GROUP_NUMERATOR_MISSING = "The owner group interest numerator is required and must be an integer greater than 0. "
GROUP_DENOMINATOR_MISSING = "The owner group interest denominator is required and must be an integer greater than 0. "
TENANCY_TYPE_NA_INVALID = "Tenancy type NA is not allowed when there is 1 active owner group with 1 owner. "
TENANCY_TYPE_NA_INVALID2 = (
    "Tenancy type NA is only allowed when all owners are ADMINISTRATOR, EXECUTOR, or TRUSTEE party types. "
)
OWNERS_JOINT_INVALID = "The owner group must contain at least 2 owners. "
OWNERS_COMMON_INVALID = "Each COMMON owner group must contain exactly 1 owner. "
OWNERS_COMMON_SOLE_INVALID = (
    "SOLE owner group tenancy type is not allowed when there is more than 1 " + "owner group. Use COMMON instead. "
)
GROUP_COMMON_INVALID = "More than 1 group is required with the Tenants in Common owner group type. "
ADD_SOLE_OWNER_INVALID = "Only one sole owner and only one sole owner group can be added. "
OWNER_DESCRIPTION_REQUIRED = "Owner description is required for the owner party type. "
TRANSFER_PARTY_TYPE_INVALID = "Owner party type of administrator, executor, trustee not allowed for this registration. "
TENANCY_PARTY_TYPE_INVALID = "Owner group tenancy type must be NA for executors, trustees, or administrators. "
GROUP_PARTY_TYPE_INVALID = (
    "For TRUSTEE, ADMINISTRATOR, or EXECUTOR, all owner party types within the group must be identical. "
)
TRAN_DEATH_GROUP_COUNT = "Only one owner group can be modified in a transfer due to death registration. "
TRAN_DEATH_DELETE_MISSING = "Death transfer excluding owner edits no request deleteOwnerGroups group found. "
TRAN_DEATH_ADD_MISSING = "Death transfer excluding owner edits no request addOwnerGroups group found. "


def get_existing_group_count(registration: MhrRegistration) -> int:
    """Count number of existing owner groups."""
    group_count: int = 0
    if not registration:
        return group_count
    for existing in registration.owner_groups:
        if existing.status_type in (MhrOwnerStatusTypes.ACTIVE, MhrOwnerStatusTypes.EXEMPT):
            group_count += 1
    if registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.owner_groups:
                for existing in reg.owner_groups:
                    if existing.status_type in (MhrOwnerStatusTypes.ACTIVE, MhrOwnerStatusTypes.EXEMPT):
                        group_count += 1
    return group_count


def owner_name_match(registration: MhrRegistration = None, request_owner=None):  # pylint: disable=too-many-branches
    """Verify the request owner name matches one of the current owner names."""
    if not registration or not request_owner:
        return False
    request_name: str = ""
    first_name: str = ""
    last_name: str = ""
    match: bool = False
    is_business = request_owner.get("organizationName")
    if is_business:
        request_name = request_owner.get("organizationName").strip().upper()
    elif (
        request_owner.get("individualName")
        and request_owner["individualName"].get("first")
        and request_owner["individualName"].get("last")
    ):
        first_name = request_owner["individualName"].get("first").strip().upper()
        last_name = request_owner["individualName"].get("last").strip().upper()
    if not request_name and not last_name:
        return False
    if registration.owner_groups:
        for group in registration.owner_groups:
            if group.status_type == MhrOwnerStatusTypes.ACTIVE:
                for owner in group.owners:
                    if is_business and owner.business_name == request_name:
                        match = True
                    elif not is_business and owner.first_name == first_name and owner.last_name == last_name:
                        match = True
    if not match and registration.change_registrations:  # pylint: disable=too-many-nested-blocks
        for reg in registration.change_registrations:
            for group in reg.owner_groups:
                if group.status_type == MhrOwnerStatusTypes.ACTIVE:
                    for owner in group.owners:
                        if is_business and owner.business_name == request_name:
                            match = True
                        elif not is_business and owner.first_name == first_name and owner.last_name == last_name:
                            match = True
    return match


def get_existing_owner_groups(registration: MhrRegistration) -> dict:
    """Get the existing active/exempt owner groups."""
    groups = []
    for existing in registration.owner_groups:
        if existing.status_type in (MhrOwnerStatusTypes.ACTIVE, MhrOwnerStatusTypes.EXEMPT):
            groups.append(existing.json)
    if registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.owner_groups:
                for existing in reg.owner_groups:
                    if existing.status_type in (MhrOwnerStatusTypes.ACTIVE, MhrOwnerStatusTypes.EXEMPT):
                        groups.append(existing.json)
    return groups


def is_valid_dealer_transfer_owner(registration: MhrRegistration, qs: dict) -> bool:
    """Check qs dealer name matches owner name and owner is a sole owner."""
    qs_name: str = str(qs.get("businessName", "")).strip().upper()
    dba_name: str = qs.get("dbaName", "")
    if dba_name:
        dba_name = dba_name.strip().upper()
    logger.debug(f"is_valid_dealer_transfer_owner checking dealer name={qs_name} dba_name={dba_name}")
    groups = get_existing_owner_groups(registration)
    if not groups or len(groups) > 1:
        return False
    owners = groups[0].get("owners")
    if owners and len(owners) == 1:
        owner_name: str = owners[0].get("organizationName", "")
        if owner_name:
            logger.debug(f"Comparing owner name={owner_name} with qs name and dba name")
            owner_name = owner_name.strip().upper()
            if owner_name == qs_name or (dba_name and owner_name == dba_name):
                return True
    return False


def validate_delete_owners(  # pylint: disable=too-many-branches
    registration: MhrRegistration = None, json_data: dict = None
) -> str:
    """Check groups id's and owners are valid for deleted groups."""
    error_msg = ""
    if not registration or not json_data.get("deleteOwnerGroups"):
        return error_msg
    for deleted in json_data["deleteOwnerGroups"]:  # pylint: disable=too-many-nested-blocks
        if deleted.get("groupId"):
            deleted_group = None
            group_id = deleted["groupId"]
            for existing in registration.owner_groups:
                if existing.group_id == group_id:
                    deleted_group = existing
            if not deleted_group and registration.change_registrations:
                for reg in registration.change_registrations:
                    if reg.owner_groups:
                        for existing in reg.owner_groups:
                            if existing.group_id == group_id:
                                deleted_group = existing
            if deleted_group:
                tenancy_type = deleted.get("type")
                # Data migration legacy owner group can have a status of EXEMPT.
                if deleted_group.status_type not in (MhrOwnerStatusTypes.ACTIVE, MhrOwnerStatusTypes.EXEMPT):
                    error_msg += DELETE_GROUP_ID_INVALID.format(group_id=group_id)
                if tenancy_type and deleted_group.tenancy_type != tenancy_type and tenancy_type != MhrTenancyTypes.NA:
                    error_msg += DELETE_GROUP_TYPE_INVALID.format(group_id=group_id)
            else:
                error_msg += DELETE_GROUP_ID_NONEXISTENT.format(group_id=group_id)
    return error_msg


def delete_group(group_id: int, delete_groups):
    """Check if owner group is flagged for deletion."""
    if not delete_groups or group_id < 1:
        return False
    for group in delete_groups:
        if group.get("groupId", 0) == group_id:
            return True
    return False


def interest_required(groups, registration: MhrRegistration = None, delete_groups=None) -> bool:
    """Determine if group interest is required."""
    group_count: int = len(groups)  # Verify interest if multiple groups or existing interest.
    if group_count > 1:
        return True
    if not registration:
        return False
    for existing in registration.owner_groups:
        if (
            existing.status_type == MhrOwnerStatusTypes.ACTIVE
            and existing.tenancy_type != MhrTenancyTypes.SOLE
            and not delete_group(existing.group_id, delete_groups)
            and existing.interest_denominator > 0
        ):
            group_count += 1
    if registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.owner_groups:
                for existing in reg.owner_groups:
                    if (
                        existing.status_type == MhrOwnerStatusTypes.ACTIVE
                        and existing.tenancy_type != MhrTenancyTypes.SOLE
                        and not delete_group(existing.group_id, delete_groups)
                        and existing.interest_denominator > 0
                    ):
                        group_count += 1
    return group_count > 1


def validate_group_interest(  # pylint: disable=too-many-branches
    groups,
    denominator: int,
    registration: MhrRegistration = None,
    delete_groups=None,
):
    """Verify owner group interest values are valid."""
    error_msg = ""
    numerator_sum: int = 0
    group_count: int = len(groups)  # Verify interest if multiple groups or existing interest.
    if registration:  # pylint: disable=too-many-nested-blocks
        for existing in registration.owner_groups:
            if (
                existing.status_type == MhrOwnerStatusTypes.ACTIVE
                and existing.tenancy_type != MhrTenancyTypes.SOLE
                and not delete_group(existing.group_id, delete_groups)
            ):
                den = existing.interest_denominator
                if den > 0:
                    group_count += 1
                    if den == denominator:
                        numerator_sum += existing.interest_numerator
                    elif den < denominator:
                        numerator_sum += denominator / den * existing.interest_numerator
                    else:
                        numerator_sum += int((denominator * existing.interest_numerator) / den)
        if registration.change_registrations:
            for reg in registration.change_registrations:
                if reg.owner_groups:
                    for existing in reg.owner_groups:
                        if (
                            existing.status_type == MhrOwnerStatusTypes.ACTIVE
                            and existing.tenancy_type != MhrTenancyTypes.SOLE
                            and not delete_group(existing.group_id, delete_groups)
                        ):
                            den = existing.interest_denominator
                            if den > 0:
                                group_count += 1
                                if den == denominator:
                                    numerator_sum += existing.interest_numerator
                                elif den < denominator:
                                    numerator_sum += denominator / den * existing.interest_numerator
                                else:
                                    numerator_sum += int((denominator * existing.interest_numerator) / den)
    logger.debug(f"group_count={group_count} denominator={denominator}")
    if group_count < 2:  # Could have transfer of joint tenants with no interest.
        return error_msg
    for group in groups:
        num = group.get("interestNumerator", 0)
        den = group.get("interestDenominator", 0)
        if num and den and num > 0 and den > 0:
            if den == denominator:
                numerator_sum += num
            else:
                numerator_sum += denominator / den * num
    if numerator_sum != denominator:
        error_msg = GROUP_INTEREST_MISMATCH
    return error_msg


def get_modified_group(registration: MhrRegistration, group_id: int) -> dict:
    """Find the existing owner group as JSON, matching on the group id."""
    group = {}
    if not registration:
        return group
    for existing in registration.owner_groups:
        if existing.group_id == group_id:
            group = existing.json
            break
    if not group and registration.change_registrations:
        for reg in registration.change_registrations:
            if reg.owner_groups:
                for existing in reg.owner_groups:
                    if existing.group_id == group_id:
                        group = existing.json
                        break
    return group


def validate_owner_group(group, int_required: bool = False, staff: bool = False):
    """Verify owner group is valid."""
    error_msg = ""
    if not group:
        return error_msg
    tenancy_type: str = group.get("type", "")
    if tenancy_type == MhrTenancyTypes.COMMON or int_required:
        if not group.get("interestNumerator") or group.get("interestNumerator", 0) < 1:
            error_msg += GROUP_NUMERATOR_MISSING
        if not group.get("interestDenominator") or group.get("interestDenominator", 0) < 1:
            error_msg += GROUP_DENOMINATOR_MISSING
    if tenancy_type == MhrTenancyTypes.NA and group.get("owners") and len(group.get("owners")) > 1:
        owner_count: int = 0
        for owner in group.get("owners"):
            if not owner.get("partyType") or owner.get("partyType") in (
                MhrPartyTypes.OWNER_BUS,
                MhrPartyTypes.OWNER_IND,
            ):
                owner_count += 1
        if owner_count != 0 and not staff:
            error_msg += TENANCY_TYPE_NA_INVALID2
    if tenancy_type == MhrTenancyTypes.JOINT and (not group.get("owners") or len(group.get("owners")) < 2):
        error_msg += OWNERS_JOINT_INVALID
    elif tenancy_type == MhrTenancyTypes.COMMON and (not group.get("owners") or len(group.get("owners")) > 1):
        error_msg += OWNERS_COMMON_INVALID
    elif tenancy_type == MhrTenancyTypes.SOLE and int_required:
        error_msg += OWNERS_COMMON_SOLE_INVALID
    return error_msg


def validate_owner(owner: dict) -> str:
    """Verify owner names are valid and legacy suffix length is valid."""
    error_msg = ""
    if not owner:
        return error_msg
    desc: str = "owner"
    if owner.get("organizationName"):
        error_msg += validate_text(owner.get("organizationName"), desc + " organization name")
    elif owner.get("individualName"):
        error_msg += validate_individual_name(owner.get("individualName"), desc)
    return error_msg


def common_tenancy(groups, new: bool, active_count: int = 0) -> bool:
    """Determine if the owner groups is a tenants in common scenario."""
    if new and groups and len(groups) == 1:
        return False
    for group in groups:
        group_type = group.get("type", "")
        if group_type and group_type != MhrTenancyTypes.SOLE and active_count > 1:
            return True
    return False


def validate_owner_groups_common(groups, registration: MhrRegistration = None, delete_groups=None):
    """Verify tenants in common owner groups are valid."""
    error_msg = ""
    tc_owner_count_invalid: bool = False
    staff: bool = False
    if registration:
        staff = registration.staff
    common_denominator: int = 0
    int_required: bool = interest_required(groups, registration, delete_groups)
    for group in groups:
        if common_denominator == 0:
            common_denominator = group.get("interestDenominator", 0)
        elif group.get("interestDenominator", 0) > common_denominator:
            common_denominator = group.get("interestDenominator", 0)
        if not group.get("owners"):
            tc_owner_count_invalid = True
        error_msg += validate_owner_group(group, int_required, staff)
        for owner in group.get("owners"):
            error_msg += validate_owner(owner)
    error_msg += validate_group_interest(groups, common_denominator, registration, delete_groups)
    if tc_owner_count_invalid:
        error_msg += OWNERS_COMMON_INVALID
    return error_msg


def validate_owner_groups(  # pylint: disable=too-many-branches
    groups, new: bool, registration: MhrRegistration = None, delete_groups=None, active_count: int = 0
):
    """Verify owner groups are valid."""
    error_msg: str = ""
    if not groups:
        return error_msg
    so_count: int = 0
    staff: bool = False

    if not new and delete_groups is None:
        error_msg += DELETE_GROUPS_MISSING
    elif not new and delete_groups:
        for del_group in delete_groups:
            if not del_group.get("groupId"):
                error_msg += DELETE_GROUP_ID_MISSING
    if registration:
        staff = registration.staff
    if common_tenancy(groups, new, active_count):
        error_msg += validate_owner_groups_common(groups, registration, delete_groups)
        return error_msg
    for group in groups:
        tenancy_type: str = group.get("type", "")
        if new and tenancy_type == MhrTenancyTypes.COMMON:
            error_msg += GROUP_COMMON_INVALID
        error_msg += validate_owner_group(group, False, staff)
        for owner in group.get("owners"):
            if tenancy_type == MhrTenancyTypes.SOLE:
                so_count += 1
            error_msg += validate_owner(owner)
    if so_count > 1 or (so_count == 1 and len(groups) > 1):
        error_msg += ADD_SOLE_OWNER_INVALID
    if not new and active_count == 1 and tenancy_type == MhrTenancyTypes.COMMON:
        error_msg += GROUP_COMMON_INVALID
    return error_msg


def get_active_group_count(json_data, registration: MhrRegistration) -> int:
    """Count number of active owner groups."""
    group_count: int = 0
    if json_data.get("ownerGroups"):
        group_count += len(json_data.get("ownerGroups"))
    else:
        if json_data.get("addOwnerGroups"):
            group_count += len(json_data.get("addOwnerGroups"))
        if json_data.get("deleteOwnerGroups"):
            group_count -= len(json_data.get("deleteOwnerGroups"))
        group_count += get_existing_group_count(registration)
    return group_count


def owner_name_address_match(owner1, owner2) -> bool:
    """Check if 2 owner json name and addresses are identical."""
    address_match: bool = False
    name_match: bool = False
    if owner1.get("address") and owner2.get("address") and owner1.get("address") == owner2.get("address"):
        address_match = True
    if (
        owner1.get("organizationName")
        and owner2.get("organizationName")
        and owner1.get("organizationName") == owner2.get("organizationName")
    ):
        name_match = True
    elif (
        owner1.get("individualName")
        and owner2.get("individualName")
        and owner1.get("individualName") == owner2.get("individualName")
    ):
        name_match = True
    return address_match and name_match


def group_owners_unchanged(json_data, add_group) -> bool:
    """Check if the owners in an added group are identical to the owners in a deleted group."""
    if not json_data.get("deleteOwnerGroups") or not add_group.get("owners"):
        return False
    for group in json_data.get("deleteOwnerGroups"):
        if group.get("owners") and len(group["owners"]) == len(add_group["owners"]):
            identical: bool = True
            for add_owner in add_group.get("owners"):
                owner_match: bool = False
                for del_owner in group.get("owners"):
                    if owner_name_address_match(add_owner, del_owner):
                        owner_match = True
                if not owner_match:
                    identical = False
            if identical:
                return True
    return False


def validate_owner_party_type(  # pylint: disable=too-many-branches
    json_data: dict, groups, new: bool, active_group_count: int, staff: bool
):
    """Verify owner groups are valid."""
    error_msg = ""
    owner_death: bool = reg_utils.is_transfer_due_to_death_staff(json_data.get("registrationType"))
    if not groups:
        return error_msg
    for group in groups:
        if not new and len(groups) > 1 and group_owners_unchanged(json_data, group):
            continue
        party_count: int = 0
        owner_count: int = 0
        group_parties_invalid: bool = False
        first_party_type: str = None
        if group.get("owners"):
            owner_count = len(group.get("owners"))
            for owner in group["owners"]:
                party_type = owner.get("partyType", None)
                if party_type and party_type in (
                    MhrPartyTypes.ADMINISTRATOR,
                    MhrPartyTypes.EXECUTOR,
                    MhrPartyTypes.TRUSTEE,
                ):
                    party_count += 1
                    if not first_party_type:
                        first_party_type = party_type
                    if first_party_type and party_type != first_party_type:
                        group_parties_invalid = True
                if (
                    party_type
                    and not owner.get("description")
                    and party_type
                    in (MhrPartyTypes.ADMINISTRATOR, MhrPartyTypes.EXECUTOR, MhrPartyTypes.TRUST, MhrPartyTypes.TRUSTEE)
                ):
                    error_msg += OWNER_DESCRIPTION_REQUIRED
                if (
                    not new
                    and not owner_death
                    and not json_data.get("transferDocumentType")
                    and party_type
                    and party_type
                    in (MhrPartyTypes.ADMINISTRATOR, MhrPartyTypes.EXECUTOR, MhrPartyTypes.TRUST, MhrPartyTypes.TRUSTEE)
                ):
                    if not staff:
                        error_msg += TRANSFER_PARTY_TYPE_INVALID
        if active_group_count < 2 and group.get("type", "") == MhrTenancyTypes.NA and owner_count == 1:
            error_msg += TENANCY_TYPE_NA_INVALID  # SOLE owner cannot be NA
        elif active_group_count > 1 and party_count > 0 and group.get("type", "") != MhrTenancyTypes.NA:
            error_msg += TENANCY_PARTY_TYPE_INVALID  # COMMON scenario
        elif (
            active_group_count == 1
            and owner_count > 1
            and party_count > 0
            and group.get("type", "") != MhrTenancyTypes.NA
        ):
            error_msg += TENANCY_PARTY_TYPE_INVALID  # JOINT scenario
        if group_parties_invalid or (not new and not owner_death and party_count > 0 and party_count != owner_count):
            error_msg += GROUP_PARTY_TYPE_INVALID
    return error_msg


def is_delete_exec_admin(reg_type: str, owner_json: dict) -> bool:
    """Evaluate if a deleted owner is an executor or an administrator for one of the death transfers types."""
    if reg_type == MhrRegistrationTypes.TRANS_WILL and owner_json.get("partyType", "") in (
        MhrPartyTypes.EXECUTOR,
        MhrPartyTypes.ADMINISTRATOR,
        MhrPartyTypes.TRUST,
        MhrPartyTypes.TRUSTEE,
    ):
        return True
    if reg_type == MhrRegistrationTypes.TRANS_ADMIN and owner_json.get("partyType", "") in (
        MhrPartyTypes.EXECUTOR,
        MhrPartyTypes.ADMINISTRATOR,
        MhrPartyTypes.TRUST,
        MhrPartyTypes.TRUSTEE,
    ):
        return True
    return False


def new_owner_exists(modified_group, owner) -> bool:
    """Check if the new owner name matches an existing group owner name."""
    if owner and modified_group and modified_group.get("owners"):
        for owner_json in modified_group.get("owners"):
            if (
                owner_json.get("individualName")
                and owner.get("individualName")
                and owner_json["individualName"].get("last") == owner["individualName"].get("last")
                and owner_json["individualName"].get("first") == owner["individualName"].get("first")
            ):
                if owner_json["individualName"].get("middle", "") == owner["individualName"].get("middle", ""):
                    return True
            elif (
                owner_json.get("organizationName")
                and owner.get("organizationName")
                and owner_json.get("organizationName") == owner.get("organizationName")
            ):
                return True
    return False


def existing_owner_added(new_owners, owner) -> bool:
    """Check if the existing owner name matches an owner name in the new group."""
    if owner and new_owners:
        for owner_json in new_owners:
            if (
                owner_json.get("individualName")
                and owner.get("individualName")
                and owner_json["individualName"].get("last") == owner["individualName"].get("last")
                and owner_json["individualName"].get("first") == owner["individualName"].get("first")
            ):
                if owner_json["individualName"].get("middle", "") == owner["individualName"].get("middle", ""):
                    return True
            elif (
                owner_json.get("organizationName")
                and owner.get("organizationName")
                and owner_json.get("organizationName") == owner.get("organizationName")
            ):
                return True
    return False


def match_group_owner(group: MhrOwnerGroup, owner_id: int) -> MhrParty:
    """Find owner matching the owner id."""
    if group.status_type in (MhrOwnerStatusTypes.ACTIVE, MhrOwnerStatusTypes.EXEMPT):
        for owner in group.owners:
            logger.info(f"match_group_owner group id={group.id} owner id={owner.id}")
            if owner.id == owner_id:
                return owner
    return None


def is_deleted_owner_match(registration: MhrRegistration, request_owner) -> bool:
    """For owner edits try and find the existing owner that matches by id and name."""
    if not registration or not request_owner or not request_owner.get("previousOwnerId"):
        return False
    owner_id: int = request_owner.get("previousOwnerId")
    deleted_owner: MhrParty = None
    logger.info(f"is_deleted_owner_match owner_id={owner_id}")
    for group in registration.owner_groups:
        deleted_owner = match_group_owner(group, owner_id)
        if deleted_owner:
            break
    if not deleted_owner and registration.change_registrations:
        for reg in registration.change_registrations:
            for group in reg.owner_groups:
                if not deleted_owner:
                    deleted_owner = match_group_owner(group, owner_id)
                else:
                    break
    if not deleted_owner:
        return False
    deleted_json = deleted_owner.json
    if is_identical_owner_name(deleted_json, request_owner):
        logger.info(f"owner_name_match id match on deleted owner={deleted_json}")
        return True
    return False


def is_edit_group(registration: MhrRegistration, add_group: dict) -> bool:
    """Look for a valid edit owner in the added group."""
    edit_owner: dict = None
    for owner in add_group.get("owners"):
        if owner.get("previousOwnerId"):
            edit_owner = owner
            break
    if not edit_owner:
        return False
    return is_deleted_owner_match(registration, edit_owner)


def is_edit_owner_id(add_groups, owner_id: int) -> bool:
    """Look for new owner group with the matching deleted owner ID."""
    if not add_groups or not owner_id or owner_id < 0:
        return False
    for group in add_groups:
        for owner in group.get("owners"):
            if owner.get("previousOwnerId", 0) == owner_id:
                return True
    return False


def get_death_group_count(registration: MhrRegistration, json_data: dict) -> int:
    """Transfer death registration get group changed count ignoring owner edits."""
    del_count: int = len(json_data.get("deleteOwnerGroups"))
    add_count: int = len(json_data.get("addOwnerGroups"))
    if del_count == 1 and add_count == 1:
        return 1
    # Either no owner edits or number of deleted and added groups with edits should match
    if del_count != add_count:
        if del_count < add_count:
            return add_count
        return del_count
    # Ignore groups with valid owner edits.
    edit_count: int = 0
    for group in json_data.get("addOwnerGroups"):
        if is_edit_group(registration, group):
            edit_count += 1
    if edit_count == 0:
        return add_count
    if add_count - edit_count == 0:
        return 1
    return add_count - edit_count


def get_delete_group_count(registration: MhrRegistration, json_data: dict) -> int:
    """Transfer non-staff registration get deleted group count ignoring owner edits."""
    del_count: int = len(json_data.get("deleteOwnerGroups"))
    if del_count == 1:
        return 1
    # Ignore groups with valid owner edits.
    edit_count: int = 0
    for group in json_data.get("addOwnerGroups"):
        if is_edit_group(registration, group):
            edit_count += 1
    if edit_count == 0:
        return del_count
    if del_count - edit_count == 0:
        return 1
    return del_count - edit_count


def get_death_add_group(json_data: dict) -> dict:
    """Transfer death registration get single added group ignoring owner edits."""
    if len(json_data.get("addOwnerGroups")) == 1:
        return json_data["addOwnerGroups"][0]
    for group in json_data.get("addOwnerGroups"):
        edit_group: bool = False
        for owner in group.get("owners"):
            if owner.get("previousOwnerId"):
                edit_group = True
                break
        if not edit_group:
            return group
    return None


def get_death_delete_group(registration: MhrRegistration, json_data: dict):
    """Transfer death registration get single added group ignoring owner edits."""
    del_group: dict = None
    modified_group: dict = None
    if len(json_data.get("deleteOwnerGroups")) == 1:
        del_group = json_data["deleteOwnerGroups"][0]
    elif json_data.get("addOwnerGroups"):
        # Look for a deleted owner group with no corresponding add owner group edit Ids.
        for group in json_data.get("deleteOwnerGroups"):
            edit_group: bool = False
            for owner in group.get("owners"):
                if is_edit_owner_id(json_data.get("addOwnerGroups"), owner.get("ownerId")):
                    edit_group = True
                    break
            if not edit_group:
                del_group = group
                break
    if del_group:
        modified_group = get_modified_group(registration, del_group.get("groupId", 0))
    return del_group, modified_group


def validate_death_group_counts(registration: MhrRegistration, json_data: dict, del_group, new_group) -> str:
    """Transfer death registration check add/delete group counts ignoring edits."""
    error_msg: str = ""
    if get_death_group_count(registration, json_data) != 1:
        error_msg += TRAN_DEATH_GROUP_COUNT
    if not del_group:
        error_msg += TRAN_DEATH_DELETE_MISSING
    if not new_group:
        error_msg += TRAN_DEATH_ADD_MISSING
    return error_msg
