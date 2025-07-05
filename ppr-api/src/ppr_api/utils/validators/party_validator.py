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
"""This module holds party validation for rules not covered by the schema.

Validation includes verifying party codes and address region and country codes.
"""
import pycountry

from ppr_api.models import ClientCode, ClientCodeType, Party
from ppr_api.models import utils as model_utils
from ppr_api.models.type_tables import ClientCodeTypes
from ppr_api.utils.validators import valid_charset

REGISTERING_CODE_MSG = "No registering party client party found for code {}. "
SECURED_CODE_MSG = "No secured party client party found for code {}. "
DELETE_MISSING_ID_SECURED = "Required partyId missing in delete Secured Parties. "
DELETE_MISSING_ID_DEBTOR = "Required partyId missing in delete Debtors. "
INVALID_PARTY_ID_SECURED = "Invalid partyId {} in delete Secured Parties. "
INVALID_PARTY_ID_DEBTOR = "Invalid partyId {} in delete Debtors. "
INVALID_COUNTRY_REGISTERING = "Registering Party country {} is invalid. "
INVALID_REGION_REGISTERING = "Registering Party region {} is invalid. "
INVALID_COUNTRY_SECURED = "Secured Party country {} is invalid. "
INVALID_REGION_SECURED = "Secured Party region {} is invalid. "
INVALID_COUNTRY_DEBTOR = "Debtor country {} is invalid. "
INVALID_REGION_DEBTOR = "Debtor region {} is invalid. "
CHARACTER_SET_UNSUPPORTED = "The character set is not supported for name {}. "
DUPLICATE_SECURED_PARTY_BUSINESS = "Duplicate Secured Party Business. "
DUPLICATE_SECURED_PARTY_PERSON = "Duplicate Secured Party Person. "
INVALID_AMEND_PARTY_ID_SECURED = "Invalid amendPartyId {} in add Secured Parties. "
INVALID_AMEND_PARTY_ID_DEBTOR = "Invalid amendPartyId {} in add Debtors. "
INVALID_COUNTRY_CLIENT_CODE = "Client party code address country {} is invalid. "
INVALID_REGION_CLIENT_CODE = "Client party code region {} is invalid. "
CLIENT_CODE_STAFF_ACCOUNT_MISSING = "Invalid staff client code request: client account ID missing in payload. "
CLIENT_CODE_INVALID_HEAD_OFFICE = "Invalid client code request: head office code {head_code} not found. "
CLIENT_CODE_INVALID_ACCOUNT = (
    "Invalid client code request: existing head office code {head_code} belongs to another account. "
)
CLIENT_CODE_INVALID_BRANCH = "Invalid client code request: party code {branch_code} not found. "
CLIENT_CODE_INVALID_ACCOUNT_BRANCH = (
    "Invalid client code request: existing party code {branch_code} belongs to another account. "
)
CLIENT_CODE_CHANGE_INVALID = "Invalid client code change request: no code or valid headOfficeCode in payload. "
CLIENT_CODE_NAME_MISSING = "Invalid client code change name request: required businessName missing in payload. "
CLIENT_CODE_NAME_IDENTICAL = "Invalid client code change name request: businessName identical to existing name. "
CLIENT_CODE_CHANGE_INVALID2 = "Invalid client code change request: no code in payload. "
CLIENT_CODE_ADDRESS_MISSING = "Invalid client code change name request: required address missing in payload. "
CLIENT_CODE_ADDRESS_IDENTICAL = "Invalid client code change address request: new address identical to existing one. "


def validate_financing_parties(json_data):
    """Verify party data for all parties in json_data representing a financing statement."""
    error_msg = validate_party_codes(json_data)
    error_msg += validate_party_addresses(json_data)
    error_msg += validate_party_names(json_data)
    return error_msg


def validate_registration_parties(json_data, financing_statement=None):
    """Verify party data for all parties in json_data representing a registration."""
    error_msg = validate_party_codes(json_data)
    error_msg += validate_party_addresses(json_data)
    error_msg += validate_party_names(json_data)
    error_msg += validate_party_ids(json_data, financing_statement)

    return error_msg


def validate_client_code_registration(json_data: dict, reg_type: ClientCodeType, account_id: str, staff: bool) -> str:
    """Verify new client party code registration request JSON."""
    error_msg: str = ""
    if not json_data or not reg_type:
        return error_msg
    if staff and not json_data.get("accountId"):
        error_msg += CLIENT_CODE_STAFF_ACCOUNT_MISSING
    code: ClientCode = None
    if json_data.get("headOfficeCode"):
        head_code = json_data.get("headOfficeCode")
        codes = ClientCode.find_by_head_office_code(head_code)
        if not codes:
            error_msg += CLIENT_CODE_INVALID_HEAD_OFFICE.format(head_code=head_code)
        else:
            code = codes[0]
            if not staff and code.get("accountId") and code.get("accountId") != account_id:
                error_msg += CLIENT_CODE_INVALID_ACCOUNT.format(head_code=head_code)
            elif staff and code.get("accountId") and code.get("accountId") != json_data.get("accountId"):
                error_msg += CLIENT_CODE_INVALID_ACCOUNT.format(head_code=head_code)
    if reg_type != ClientCodeTypes.CREATE_CODE:
        error_msg += validate_client_code_change(json_data, reg_type, code, staff, account_id)
    if json_data.get("businessName"):
        error_msg += validate_party_name(json_data)
    error_msg += validate_address(json_data, INVALID_COUNTRY_CLIENT_CODE, INVALID_REGION_CLIENT_CODE)
    return error_msg


def validate_client_code_change(
    json_data: dict, reg_type: ClientCodeType, code: ClientCode, staff: bool, account_id: str
) -> str:
    """Verify new client party code change request JSON."""
    error_msg: str = ""
    if reg_type in (ClientCodeTypes.CHANGE_ADDRESS, ClientCodeTypes.CHANGE_NAME_ADDRESS) and not json_data.get("code"):
        error_msg += CLIENT_CODE_CHANGE_INVALID2
    elif not code and not json_data.get("code"):
        error_msg += CLIENT_CODE_CHANGE_INVALID
    elif not code:
        branch_code: str = json_data.get("code")
        code = ClientCode.find_by_code(branch_code)
        if not code:
            error_msg += CLIENT_CODE_INVALID_BRANCH.format(branch_code=branch_code)
        elif not staff and code.get("accountId") and code.get("accountId") != account_id:
            error_msg += CLIENT_CODE_INVALID_ACCOUNT_BRANCH.format(branch_code=branch_code)
        elif staff and code.get("accountId") and code.get("accountId") != json_data.get("accountId"):
            error_msg += CLIENT_CODE_INVALID_ACCOUNT_BRANCH.format(branch_code=branch_code)
    if reg_type in (ClientCodeTypes.CHANGE_NAME, ClientCodeTypes.CHANGE_NAME_ADDRESS):
        if not json_data.get("businessName"):
            error_msg += CLIENT_CODE_NAME_MISSING
        elif code and str(json_data.get("businessName")).strip().upper() == code.get("businessName"):
            error_msg += CLIENT_CODE_NAME_IDENTICAL
    if reg_type in (ClientCodeTypes.CHANGE_ADDRESS, ClientCodeTypes.CHANGE_NAME_ADDRESS):
        if not json_data.get("address"):
            error_msg += CLIENT_CODE_ADDRESS_MISSING
        elif code and json_data.get("address") == code.get("address"):
            error_msg += CLIENT_CODE_ADDRESS_IDENTICAL
    return error_msg


def validate_party_codes(json_data):
    """Verify party codes exist in the database for all parties in json_data."""
    error_msg = ""
    code = None

    if "registeringParty" in json_data and "code" in json_data["registeringParty"]:
        code = json_data["registeringParty"]["code"]
        if not Party.verify_party_code(code):
            error_msg += REGISTERING_CODE_MSG.format(code)

    if "securedParties" in json_data:
        for party in json_data["securedParties"]:
            if "code" in party:
                code = party["code"]
                if not Party.verify_party_code(code):
                    error_msg += SECURED_CODE_MSG.format(code)

    if "addSecuredParties" in json_data:
        for party in json_data["addSecuredParties"]:
            if "code" in party:
                code = party["code"]
                if not Party.verify_party_code(code):
                    error_msg += SECURED_CODE_MSG.format(code)

    return error_msg


def validate_party_names(json_data):
    """Verify party names for all added parties in json_data."""
    error_msg = ""
    if "registeringParty" in json_data:
        error_msg += validate_party_name(json_data["registeringParty"])

    if "securedParties" in json_data:
        for party in json_data["securedParties"]:
            error_msg += validate_party_name(party)
            error_msg += validate_party_duplicates(json_data["securedParties"])

    if "addSecuredParties" in json_data:
        for party in json_data["addSecuredParties"]:
            error_msg += validate_party_name(party)
            error_msg += validate_party_duplicates(json_data["addSecuredParties"])

    if "debtors" in json_data:
        for party in json_data["debtors"]:
            error_msg += validate_party_name(party)

    if "addDebtors" in json_data:
        for party in json_data["addDebtors"]:
            error_msg += validate_party_name(party)

    return error_msg


def validate_party_name(party_json):
    """Verify party name is valid."""
    error_msg = ""
    name = party_json.get("businessName", None)
    if name:
        if not valid_charset(name):
            error_msg += CHARACTER_SET_UNSUPPORTED.format(name)
        return error_msg
    person = party_json.get("personName", None)
    if person:
        name = person["first"]
        if not valid_charset(name):
            error_msg += CHARACTER_SET_UNSUPPORTED.format(name)
        name = person["last"]
        if not valid_charset(name):
            error_msg += CHARACTER_SET_UNSUPPORTED.format(name)
        name = person.get("middle", None)
        if name and not valid_charset(name):
            error_msg += CHARACTER_SET_UNSUPPORTED.format(name)
    return error_msg


def validate_party_addresses(json_data):
    """Verify all party address country and region values in json_data."""
    error_msg = ""

    if "registeringParty" in json_data and "address" in json_data["registeringParty"]:
        error_msg += validate_address(
            json_data["registeringParty"], INVALID_COUNTRY_REGISTERING, INVALID_REGION_REGISTERING
        )

    if "securedParties" in json_data:
        for party in json_data["securedParties"]:
            error_msg += validate_address(party, INVALID_COUNTRY_SECURED, INVALID_REGION_SECURED)

    if "addSecuredParties" in json_data:
        for party in json_data["addSecuredParties"]:
            error_msg += validate_address(party, INVALID_COUNTRY_SECURED, INVALID_REGION_SECURED)

    if "debtors" in json_data:
        for party in json_data["debtors"]:
            error_msg += validate_address(party, INVALID_COUNTRY_DEBTOR, INVALID_REGION_DEBTOR)

    if "addDebtors" in json_data:
        for party in json_data["addDebtors"]:
            error_msg += validate_address(party, INVALID_COUNTRY_DEBTOR, INVALID_REGION_DEBTOR)

    return error_msg


def validate_address(json_party, country_message: str, region_message: str):
    """Verify the address country and region values in json_address."""
    if not json_party or "address" not in json_party:
        return ""

    error_msg = ""
    json_address = json_party["address"]
    if "country" in json_address:
        json_country = json_address["country"].strip().upper()
        country = None
        if len(json_country) == 2:
            country = pycountry.countries.get(alpha_2=json_country)
        elif len(json_country) == 3:
            country = pycountry.countries.get(alpha_3=json_country)
        else:
            country = pycountry.countries.search_fuzzy(json_address["country"].strip())
        if not country:
            error_msg += country_message.format(json_address["country"])
        if "region" in json_address:  # Validate region.
            region_code = None
            if len(json_address["region"].strip()) == 2:
                country_prefix = country.alpha_2 + "-" if country else "CA-"
                # test_code = country_prefix + json_address['region'].strip().upper()
                region_code = pycountry.subdivisions.get(code=(country_prefix + json_address["region"].strip().upper()))
            if not region_code and json_country in ("CA", "US"):
                error_msg += region_message.format(json_address["region"])
            # not checking region validity for outside CA + US but still must be under 2 chars
            if len(json_address["region"].strip()) > 2:
                error_msg += region_message.format(json_address["region"])

    return error_msg


def validate_party_ids(json_data, financing_statement=None):
    """Verify party ID's. when removing secured parties and debtors."""
    error_msg = ""

    if "deleteSecuredParties" in json_data:
        for party in json_data["deleteSecuredParties"]:
            if "partyId" not in party:
                error_msg += DELETE_MISSING_ID_SECURED
            elif financing_statement and financing_statement.parties:
                existing = find_party_by_id(party["partyId"], model_utils.PARTY_SECURED, financing_statement.parties)
                if not existing:
                    error_msg += INVALID_PARTY_ID_SECURED.format(str(party["partyId"]))

    if "deleteDebtors" in json_data:
        for party in json_data["deleteDebtors"]:
            if "partyId" not in party:
                error_msg += DELETE_MISSING_ID_DEBTOR
            elif financing_statement and financing_statement.parties:
                existing = find_party_by_id(party["partyId"], model_utils.PARTY_DEBTOR_BUS, financing_statement.parties)
                if not existing:
                    error_msg += INVALID_PARTY_ID_DEBTOR.format(str(party["partyId"]))
    error_msg += validate_amend_party_ids(json_data)
    return error_msg


def validate_amend_party_ids(json_data):
    """Verify amend party ID's. when editing secured parties and debtors."""
    error_msg = ""
    if "addSecuredParties" in json_data:  # Verify amendPartyId if present for amendment added secured parties
        for party in json_data["addSecuredParties"]:
            if party.get("amendPartyId", 0) > 0:
                existing = find_deleted_party_by_id(party["amendPartyId"], json_data.get("deleteSecuredParties"))
                if not existing:
                    error_msg += INVALID_AMEND_PARTY_ID_SECURED.format(str(party["amendPartyId"]))

    if "addDebtors" in json_data:  # Verify amendPartyId if present for amendment added debtors
        for party in json_data["addDebtors"]:
            if party.get("amendPartyId", 0) > 0:
                existing = find_deleted_party_by_id(party["amendPartyId"], json_data.get("deleteDebtors"))
                if not existing:
                    error_msg += INVALID_AMEND_PARTY_ID_DEBTOR.format(str(party["amendPartyId"]))
    return error_msg


def find_party_by_id(party_id: int, party_type: str, parties):
    """Search existing list of party objects for a matching party id and type."""
    party = None

    if party_id and party_type and parties:
        for eval_party in parties:
            if eval_party.id == party_id and party_type == eval_party.party_type and not eval_party.registration_id_end:
                party = eval_party
            elif (
                eval_party.id == party_id
                and party_type == model_utils.PARTY_DEBTOR_BUS
                and eval_party.party_type == model_utils.PARTY_DEBTOR_IND
                and not eval_party.registration_id_end
            ):
                party = eval_party

    return party


def find_deleted_party_by_id(party_id: int, parties):
    """Search list of deleted parties for a matching amended party id."""
    party = None
    if party_id and parties:
        for eval_party in parties:
            if eval_party.get("partyId", 0) == party_id:
                party = eval_party
                break
    return party


def validate_party_duplicates(party_json):
    """Verify no party name/address duplicates when creating or adding secured parties."""
    error_msg = ""

    for party in party_json:
        business_name = party.get("businessName", None)
        person_name = party.get("personName", None)

        if business_name:
            matches = [
                i
                for i, x in enumerate(party_json)
                if x.get("businessName", None) and x["businessName"].upper() == business_name.upper()
            ]

            if len(matches) >= 2:
                address_a = dict((k.upper(), v.upper()) for k, v in party_json[matches[0]]["address"].items())
                address_b = dict((k.upper(), v.upper()) for k, v in party_json[matches[1]]["address"].items())

                if address_a == address_b:
                    error_msg = DUPLICATE_SECURED_PARTY_BUSINESS

        if person_name:
            person_name = dict((k.upper(), v.upper()) for k, v in person_name.items())
            matches = [
                i
                for i, x in enumerate(party_json)
                if x.get("personName", None)
                and dict((k.upper(), v.upper()) for k, v in x["personName"].items()) == person_name
            ]

            if len(matches) >= 2:
                address_a = dict((k.upper(), v.upper()) for k, v in party_json[matches[0]]["address"].items())
                address_b = dict((k.upper(), v.upper()) for k, v in party_json[matches[1]]["address"].items())

                if address_a == address_b:
                    error_msg = DUPLICATE_SECURED_PARTY_PERSON

    return error_msg
