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
"""This module holds data for parties and client parties (debtors, registering parties, secured parties)."""
from __future__ import annotations

from enum import Enum

from sqlalchemy import event, text

from ppr_api.models import utils as model_utils

from .db import db
from .address import Address  # noqa: F401 pylint: disable=unused-import
from .client_code import ClientCode  # noqa: F401 pylint: disable=unused-import


BUSINESS_UPDATE_QUERY = """
    SELECT (select searchkey_business_name(:actual_name)) AS search_key,
           (select business_name_strip_designation(:actual_name)) AS bus_name_base
"""
INDIVIDUAL_UPDATE_QUERY = """
    SELECT (select searchkey_individual(:last_name, :first_name)) AS first_search_key,
           (select searchkey_last_name(:last_name)) AS last_search_key,
           (select individual_split_1(:first_name)) AS first_split1,
           (select individual_split_2(:first_name)) AS first_split2,
           (select individual_split_1(:last_name)) AS last_split1,
           (select individual_split_2(:last_name)) AS last_split2,
           (select individual_split_3(:last_name)) AS last_split3
"""


class Party(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the parties (people and organizations)."""

    class PartyTypes(Enum):
        """Render an Enum of the party types."""

        DEBTOR_COMPANY = 'DB'
        DEBTOR_INDIVIDUAL = 'DI'
        REGISTERING_PARTY = 'RG'
        SECURED_PARTY = 'SP'

    __tablename__ = 'parties'

    id = db.Column('id', db.Integer, db.Sequence('party_id_seq'), primary_key=True)
    party_type = db.Column('party_type', db.String(2), db.ForeignKey('party_types.party_type'), nullable=False)
    # party person
    first_name = db.Column('first_name', db.String(50), nullable=True)
    middle_initial = db.Column('middle_initial', db.String(50), nullable=True, index=True)
    last_name = db.Column('last_name', db.String(50), nullable=True)
    # or party business
    business_name = db.Column('business_name', db.String(150), index=True, nullable=True)
    birth_date = db.Column('birth_date', db.DateTime, nullable=True)
    email_id = db.Column('email_address', db.String(250), nullable=True)

    # Search keys
    first_name_key = db.Column('first_name_key', db.String(100), nullable=True, index=True)
    last_name_key = db.Column('last_name_key', db.String(50), nullable=True, index=True)
    business_search_key = db.Column('business_srch_key', db.String(150), nullable=True, index=True)

    # For ind debtor searching
    last_name_split1 = db.Column('last_name_split1', db.String(50), nullable=True, index=True)
    last_name_split2 = db.Column('last_name_split2', db.String(50), nullable=True, index=True)
    last_name_split3 = db.Column('last_name_split3', db.String(50), nullable=True, index=True)
    first_name_split1 = db.Column('first_name_split1', db.String(50), nullable=True, index=True)
    first_name_split2 = db.Column('first_name_split2', db.String(50), nullable=True, index=True)
    first_name_char1 = db.Column('first_name_char1', db.String(1), nullable=True)
    first_name_char2 = db.Column('first_name_char2', db.String(1), nullable=True)
    first_name_key_char1 = db.Column('first_name_key_char1', db.String(1), nullable=True)

    # For bus debtor searching
    bus_name_base = db.Column('bus_name_base', db.String(150), nullable=True)
    bus_name_key_char1 = db.Column('bus_name_key_char1', db.String(1), nullable=True)
    # For amendment distinguishing party edit from remove/add
    previous_party_id = db.Column('previous_party_id', db.Integer, nullable=True)

    # parent keys
    address_id = db.Column('address_id', db.Integer, db.ForeignKey('addresses.id'), nullable=True, index=True)
    branch_id = db.Column('branch_id', db.Integer, db.ForeignKey('client_codes.id'), nullable=True, index=True)
    registration_id = db.Column('registration_id', db.Integer, db.ForeignKey('registrations.id'), nullable=False,
                                index=True)
    financing_id = db.Column('financing_id', db.Integer, db.ForeignKey('financing_statements.id'), nullable=False,
                             index=True)
    registration_id_end = db.Column('registration_id_end', db.Integer, nullable=True, index=True)
#                                db.ForeignKey('registration.registration_id'), nullable=True)

    # Relationships - Address
    address = db.relationship('Address', foreign_keys=[address_id], uselist=False,
                              back_populates='party', cascade='all, delete')

    # Relationships - ClientCode
    client_code = db.relationship('ClientCode', foreign_keys=[branch_id], uselist=False, back_populates='party')

    # Relationships - Registration
    registration = db.relationship('Registration', foreign_keys=[registration_id],
                                   back_populates='parties', cascade='all, delete', uselist=False)

    # Relationships - FinancingStatement
    financing_statement = db.relationship('FinancingStatement', foreign_keys=[financing_id],
                                          back_populates='parties', cascade='all, delete',
                                          uselist=False)
    # Relationships - PartyType
    party_types = db.relationship('PartyType', foreign_keys=[party_type],
                                  back_populates='party', cascade='all, delete', uselist=False)

    @property
    def json(self) -> dict:  # pylint: disable=too-many-branches
        """Return the party as a json object."""
        party = {
        }
        if self.party_type != model_utils.PARTY_REGISTERING:
            party['partyId'] = self.id

        if self.client_code and self.branch_id:
            party['code'] = str(self.branch_id)
            if self.client_code.name:
                party['businessName'] = self.client_code.name

            if self.client_code.address:
                cp_address = self.client_code.address.json
                party['address'] = cp_address

            if self.client_code.email_id:
                party['emailAddress'] = self.client_code.email_id
        else:
            if self.business_name:
                party['businessName'] = self.business_name
            if self.last_name:
                person_name = {
                    'first': self.first_name,
                    'last': self.last_name
                }
                if self.middle_initial:
                    person_name['middle'] = self.middle_initial
                party['personName'] = person_name

            if self.address:
                cp_address = self.address.json
                party['address'] = cp_address

            if self.email_id:
                party['emailAddress'] = self.email_id

            if self.birth_date:
                party['birthDate'] = model_utils.format_ts(self.birth_date)

        if self.party_type in (Party.PartyTypes.DEBTOR_COMPANY.value,
                               Party.PartyTypes.DEBTOR_INDIVIDUAL.value,
                               Party.PartyTypes.SECURED_PARTY.value) and self.previous_party_id is not None:
            party['amendPartyId'] = self.previous_party_id
        return party

    def save(self):
        """Save the object to the database immediately."""
        db.session.add(self)
        db.session.commit()

        return self.json

    @property
    def name(self) -> str:
        """Return the full name of the party for comparison."""
        if self.last_name:
            if self.middle_initial:
                return ' '.join((self.first_name, self.middle_initial, self.last_name)).strip().upper()
            return ' '.join((self.first_name, self.last_name)).strip().upper()
        return self.business_name.strip().upper()

    @classmethod
    def find_by_id(cls, party_id: int = None):
        """Return a party object by party ID."""
        party = None
        if party_id:
            party = cls.query.get(party_id)

        return party

    @classmethod
    def find_by_registration_id(cls, registration_id: int = None):
        """Return a list of party objects by registration number."""
        parties = None
        if registration_id:
            parties = cls.query.filter(Party.registration_id == registration_id) \
                               .order_by(Party.id).all()

        return parties

    @classmethod
    def find_by_financing_id(cls, financing_id: int = None):
        """Return a list of party objects by financing statement ID."""
        parties = None
        if financing_id:
            parties = cls.query.filter(Party.financing_id == financing_id) \
                               .order_by(Party.id).all()

        return parties

    @staticmethod
    def create_from_json(json_data, party_type: str, registration_id: int = None):  # pylint: disable=too-many-branches
        """Create a party object from a json schema object: map json to db."""
        party = Party()
        if party_type != model_utils.PARTY_DEBTOR_BUS:
            party.party_type = party_type
        elif 'businessName' in json_data:
            party.party_type = party_type
        else:
            party.party_type = model_utils.PARTY_DEBTOR_IND

        if party_type != model_utils.PARTY_DEBTOR_BUS and 'code' in json_data:
            party.branch_id = int(json_data['code'])
        else:
            if party_type == model_utils.PARTY_DEBTOR_BUS and 'birthDate' in json_data:
                party.birth_date = model_utils.ts_from_date_iso_format(json_data['birthDate'])
            if 'businessName' in json_data:
                party.business_name = json_data['businessName'].strip().upper()
            else:
                party.last_name = json_data['personName']['last'].strip().upper()
                party.first_name = json_data['personName']['first'].strip().upper()
                party.first_name_char1 = party.first_name[0:1]
                if len(party.first_name) > 1:
                    party.first_name_char2 = party.first_name[1:2]
                if 'middle' in json_data['personName']:
                    party.middle_initial = json_data['personName']['middle'].strip().upper()

            if 'emailAddress' in json_data:
                party.email_id = json_data['emailAddress']

            party.address = Address.create_from_json(json_data['address'])

        if registration_id:
            party.registration_id = registration_id
        if party.party_type in (Party.PartyTypes.DEBTOR_COMPANY.value,
                                Party.PartyTypes.DEBTOR_INDIVIDUAL.value,
                                Party.PartyTypes.SECURED_PARTY.value) and 'amendPartyId' in json_data:
            party.previous_party_id = json_data['amendPartyId']
        return party

    @staticmethod
    def create_from_financing_json(json_data, registration_id: int = None):
        """Create a list of party objects from a financing statement json schema object: map json to db."""
        parties = []

        parties.append(Party.create_from_json(json_data['registeringParty'],
                                              model_utils.PARTY_REGISTERING,
                                              registration_id))
        if 'securedParties' in json_data:
            for secured in json_data['securedParties']:
                parties.append(Party.create_from_json(secured,
                                                      model_utils.PARTY_SECURED,
                                                      registration_id))
        if 'debtors' in json_data:
            for debtor in json_data['debtors']:
                parties.append(Party.create_from_json(debtor,
                                                      model_utils.PARTY_DEBTOR_BUS,
                                                      registration_id))

        return parties

    @staticmethod
    def create_from_statement_json(json_data,
                                   registration_type_cl: str,
                                   financing_id: int):
        """Create a list of party objects from a non-financing statement json schema object: map json to db."""
        parties = []

        # All statements have a registering party
        registering = Party.create_from_json(json_data['registeringParty'],
                                             model_utils.PARTY_REGISTERING,
                                             None)
        registering.financing_id = financing_id
        parties.append(registering)

        if registration_type_cl in ('AMENDMENT', 'COURTORDER', 'CHANGE'):
            if 'addSecuredParties' in json_data:
                for secured in json_data['addSecuredParties']:
                    secured_party = Party.create_from_json(secured,
                                                           model_utils.PARTY_SECURED,
                                                           None)
                    secured_party.financing_id = financing_id
                    parties.append(secured_party)
            if 'addDebtors' in json_data:
                for debtor in json_data['addDebtors']:
                    debtor_party = Party.create_from_json(debtor,
                                                          model_utils.PARTY_DEBTOR_BUS,
                                                          None)
                    debtor_party.financing_id = financing_id
                    parties.append(debtor_party)

        return parties

    @staticmethod
    def verify_party_code(code: str):
        """Verify registering party or secured party code is legitimate."""
        if code and ClientCode.find_by_code(code):
            return True

        return False


@event.listens_for(Party, 'before_insert')
def party_before_insert_listener(mapper, connection, target):   # pylint: disable=unused-argument; don't use mapper
    """Conditionally set debtor search key values."""
    if target.party_type == target.PartyTypes.DEBTOR_COMPANY.value:
        stmt = text(BUSINESS_UPDATE_QUERY)
        stmt = stmt.bindparams(actual_name=target.business_name)
        result = connection.execute(stmt)
        row = result.first()
        mapping = row._mapping  # pylint: disable=protected-access; follows documentation
        target.business_search_key = str(mapping['search_key'])
        target.bus_name_base = str(mapping['bus_name_base'])
        target.bus_name_key_char1 = target.business_search_key[0:1]

    elif target.party_type == target.PartyTypes.DEBTOR_INDIVIDUAL.value:
        stmt = text(INDIVIDUAL_UPDATE_QUERY)
        stmt = stmt.bindparams(last_name=target.last_name, first_name=target.first_name)
        result = connection.execute(stmt)
        row = result.first()
        mapping = row._mapping  # pylint: disable=protected-access; follows documentation
        target.first_name_key = str(mapping['first_search_key'])
        target.last_name_key = str(mapping['last_search_key'])
        target.first_name_split1 = str(mapping['first_split1'])
        target.first_name_split2 = str(mapping['first_split2'])
        target.last_name_split1 = str(mapping['last_split1'])
        target.last_name_split2 = str(mapping['last_split2'])
        target.last_name_split3 = str(mapping['last_split3'])
        target.first_name_key_char1 = target.first_name_key[0:1]
