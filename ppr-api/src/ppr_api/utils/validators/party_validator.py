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

from ppr_api.models import Party
from ppr_api.models import utils as model_utils
from ppr_api.utils.validators import valid_charset


REGISTERING_CODE_MSG = 'No registering party client party found for code {}. '
SECURED_CODE_MSG = 'No secured party client party found for code {}. '
DELETE_MISSING_ID_SECURED = 'Required partyId missing in delete Secured Parties. '
DELETE_MISSING_ID_DEBTOR = 'Required partyId missing in delete Debtors. '
INVALID_PARTY_ID_SECURED = 'Invalid partyId {} in delete Secured Parties. '
INVALID_PARTY_ID_DEBTOR = 'Invalid partyId {} in delete Debtors. '
INVALID_COUNTRY_REGISTERING = 'Registering Party country {} is invalid. '
INVALID_REGION_REGISTERING = 'Registering Party region {} is invalid. '
INVALID_COUNTRY_SECURED = 'Secured Party country {} is invalid. '
INVALID_REGION_SECURED = 'Secured Party region {} is invalid. '
INVALID_COUNTRY_DEBTOR = 'Debtor country {} is invalid. '
INVALID_REGION_DEBTOR = 'Debtor region {} is invalid. '
CHARACTER_SET_UNSUPPORTED = 'The charcter set is not supported for name {}.\n'


def validate_financing_parties(json_data):
    """Verify party data for all parties in json_data representing a financing statement."""
    error_msg = validate_party_codes(json_data)
    error_msg += validate_party_addresses(json_data)
    return error_msg


def validate_registration_parties(json_data, financing_statement=None):
    """Verify party data for all parties in json_data representing a registration."""
    error_msg = validate_party_codes(json_data)
    error_msg += validate_party_addresses(json_data)
    error_msg += validate_party_ids(json_data, financing_statement)

    return error_msg


def validate_party_codes(json_data):
    """Verify party codes exist in the database for all parties in json_data."""
    error_msg = ''
    code = None

    if 'registeringParty' in json_data and 'code' in json_data['registeringParty']:
        code = json_data['registeringParty']['code']
        if not Party.verify_party_code(code):
            error_msg += REGISTERING_CODE_MSG.format(code)

    if 'securedParties' in json_data:
        for party in json_data['securedParties']:
            if 'code' in party:
                code = party['code']
                if not Party.verify_party_code(code):
                    error_msg += SECURED_CODE_MSG.format(code)

    if 'addSecuredParties' in json_data:
        for party in json_data['addSecuredParties']:
            if 'code' in party:
                code = party['code']
                if not Party.verify_party_code(code):
                    error_msg += SECURED_CODE_MSG.format(code)

    return error_msg


def validate_party_names(json_data):
    """Verify party names for all added parties in json_data."""
    error_msg = ''

    if 'registeringParty' in json_data:
        error_msg += validate_party_name(json_data['registeringParty'])

    if 'securedParties' in json_data:
        for party in json_data['securedParties']:
            error_msg += validate_party_name(party)

    if 'addSecuredParties' in json_data:
        for party in json_data['addSecuredParties']:
            error_msg += validate_party_name(party)

    if 'debtors' in json_data:
        for party in json_data['debtors']:
            error_msg += validate_party_name(party)

    if 'addDebtors' in json_data:
        for party in json_data['addDebtors']:
            error_msg += validate_party_name(party)

    return error_msg


def validate_party_name(party_json):
    """Verify party name is valid."""
    error_msg = ''
    name = party_json.get('businessName', None)
    if name:
        if not valid_charset(name):
            error_msg += CHARACTER_SET_UNSUPPORTED.format(name)
        return error_msg
    person = party_json.get('personName', None)
    if person:
        name = person['first']
        if not valid_charset(name):
            error_msg += CHARACTER_SET_UNSUPPORTED.format(name)
        name = person['last']
        if not valid_charset(name):
            error_msg += CHARACTER_SET_UNSUPPORTED.format(name)
        name = person.get('middle', None)
        if name and not valid_charset(name):
            error_msg += CHARACTER_SET_UNSUPPORTED.format(name)
    return error_msg


def validate_party_addresses(json_data):
    """Verify all party address country and region values in json_data."""
    error_msg = ''

    if 'registeringParty' in json_data and 'address' in json_data['registeringParty']:
        error_msg += validate_address(json_data['registeringParty'],
                                      INVALID_COUNTRY_REGISTERING,
                                      INVALID_REGION_REGISTERING)

    if 'securedParties' in json_data:
        for party in json_data['securedParties']:
            error_msg += validate_address(party,
                                          INVALID_COUNTRY_SECURED,
                                          INVALID_REGION_SECURED)

    if 'addSecuredParties' in json_data:
        for party in json_data['addSecuredParties']:
            error_msg += validate_address(party,
                                          INVALID_COUNTRY_SECURED,
                                          INVALID_REGION_SECURED)

    if 'debtors' in json_data:
        for party in json_data['debtors']:
            error_msg += validate_address(party,
                                          INVALID_COUNTRY_DEBTOR,
                                          INVALID_REGION_DEBTOR)

    if 'addDebtors' in json_data:
        for party in json_data['addDebtors']:
            error_msg += validate_address(party,
                                          INVALID_COUNTRY_DEBTOR,
                                          INVALID_REGION_DEBTOR)

    return error_msg


def validate_address(json_party, country_message: str, region_message: str):
    """Verify the address country and region values in json_address."""
    if not json_party or 'address' not in json_party:
        return ''

    error_msg = ''
    json_address = json_party['address']
    if 'country' in json_address:
        json_country = json_address['country'].strip().upper()
        country = None
        if len(json_country) == 2:
            country = pycountry.countries.get(alpha_2=json_country)
        elif len(json_country) == 3:
            country = pycountry.countries.get(alpha_3=json_country)
        else:
            country = pycountry.countries.search_fuzzy(json_address['country'].strip())
        if not country:
            error_msg += country_message.format(json_address['country'])
        if 'region' in json_address:  # Validate region.
            region_code = None
            if len(json_address['region'].strip()) == 2:
                country_prefix = country.alpha_2 + '-' if country else 'CA-'
                # test_code = country_prefix + json_address['region'].strip().upper()
                region_code = pycountry.subdivisions.get(code=(country_prefix + json_address['region'].strip().upper()))
            if not region_code:
                error_msg += region_message.format(json_address['region'])

    return error_msg


def validate_party_ids(json_data, financing_statement=None):
    """Verify party ID's. when removing secured parties and debtors."""
    error_msg = ''

    if 'deleteSecuredParties' in json_data:
        for party in json_data['deleteSecuredParties']:
            if 'partyId' not in party:
                error_msg += DELETE_MISSING_ID_SECURED
            elif financing_statement and financing_statement.parties:
                existing = find_party_by_id(party['partyId'],
                                            model_utils.PARTY_SECURED,
                                            financing_statement.parties)
                if not existing:
                    error_msg += INVALID_PARTY_ID_SECURED.format(str(party['partyId']))

    if 'deleteDebtors' in json_data:
        for party in json_data['deleteDebtors']:
            if 'partyId' not in party:
                error_msg += DELETE_MISSING_ID_DEBTOR
            elif financing_statement and financing_statement.parties:
                existing = find_party_by_id(party['partyId'],
                                            model_utils.PARTY_DEBTOR_BUS,
                                            financing_statement.parties)
                if not existing:
                    error_msg += INVALID_PARTY_ID_DEBTOR.format(str(party['partyId']))

    return error_msg


def find_party_by_id(party_id: int, party_type: str, parties):
    """Search existing list of party objects for a matching party id and type."""
    party = None

    if party_id and party_type and parties:
        for eval_party in parties:
            if eval_party.id == party_id and party_type == eval_party.party_type and \
                    not eval_party.registration_id_end:
                party = eval_party
            elif eval_party.id == party_id and party_type == model_utils.PARTY_DEBTOR_BUS and \
                    eval_party.party_type == model_utils.PARTY_DEBTOR_IND and \
                    not eval_party.registration_id_end:
                party = eval_party

    return party
