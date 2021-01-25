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
from http import HTTPStatus
from datetime import date

#from sqlalchemy import event

#from ppr_api.exceptions import BusinessException

from .db import db

from .address import Address  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
from .client_party import ClientParty  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship


class Party(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the parties (people and organizations)."""

    class PartyTypes(Enum):
        """Render an Enum of the party types."""

        DEBTOR_COMPANY = 'DC'
        DEBTOR_INDIVIDUAL = 'DI'
        REGISTERING_PARTY = 'RP'
        SECURED_PARTY = 'SP'

    __versioned__ = {}
    __tablename__ = 'party'

    party_id = db.Column('party_id', db.Integer, primary_key=True, server_default=db.FetchedValue())
    party_type_cd = db.Column('party_type_cd', db.String(3), nullable=False) #, db.ForeignKey('party_type.party_type_cd'))
    # party person
    first_name = db.Column('first_name', db.String(50), index=True, nullable=True)
    middle_name = db.Column('middle_name', db.String(50), index=True, nullable=True)
    last_name = db.Column('last_name', db.String(50), index=True, nullable=True)
    # or party business
    business_name = db.Column('business_name', db.String(150), index=True, nullable=True)

    email_id = db.Column('email_id', db.String(250), nullable=True)
    birth_dt = db.Column('birth_dt', db.Date, nullable=True)

    # parent keys
    address_id = db.Column('address_id', db.Integer, db.ForeignKey('address.address_id'), nullable=True)
    client_party_id = db.Column('client_party_id', db.Integer, 
                                db.ForeignKey('client_party.client_party_id'), nullable=True)
    registration_id = db.Column('registration_id', db.Integer, 
                                db.ForeignKey('registration.registration_id'), nullable=False)
    financing_id = db.Column('financing_id', db.Integer, 
                             db.ForeignKey('financing_statement.financing_id'), nullable=False)
    registration_id_end = db.Column('registration_id_end', db.Integer, nullable=True)
#                                db.ForeignKey('registration.registration_id'), nullable=True)

    # Relationships - Address
    address = db.relationship("Address", foreign_keys=[address_id], uselist=False, 
                                back_populates="party", cascade='all, delete')

    # Relationships - ClientParty
    client_party = db.relationship("ClientParty", foreign_keys=[client_party_id], uselist=False, 
                                    back_populates="party")

    # Relationships - Registration
    registration = db.relationship("Registration", foreign_keys=[registration_id], 
                               back_populates="parties", cascade='all, delete', uselist=False)
#    registration_end = db.relationship("Registration", foreign_keys=[registration_id_end])

    # Relationships - FinancingStatement
    financing_statement = db.relationship("FinancingStatement", foreign_keys=[financing_id], 
                               back_populates="parties", cascade='all, delete', uselist=False)


    def save(self):
        """Save the object to the database immediately."""
#        db.session.add(self)
#        db.session.commit()

    @property
    def json(self) -> dict:
        """Return the party as a json object."""
        party = {
        }
        if self.party_type_cd != 'RP':
            party['partyId'] = self.party_id

        if self.client_party:
            if self.client_party_id:
                party['code'] = str(self.client_party_id)
            if self.client_party.business_name:
                party['businessName'] = self.client_party.business_name
            if self.client_party.last_name:
                person_name = {
                    'first': self.client_party.first_name,
                    'last': self.client_party.last_name
                }
                if self.client_party.middle_name:
                    person_name['middle'] = self.client_party.middle_name
                party['personName'] = person_name

            if self.client_party.address:
                cp_address = self.client_party.address.json
                party['address'] = cp_address

            if self.client_party.email_id:
                party['emailAddress'] = self.client_party.email_id
        else:
            if self.business_name:
                party['businessName'] = self.business_name
            if self.last_name:
                person_name = {
                    'first': self.first_name,
                    'last': self.last_name
                }
                if self.middle_name:
                    person_name['middle'] = self.middle_name
                party['personName'] = person_name

            if self.address:
                cp_address = self.address.json
                party['address'] = cp_address

            if self.email_id:
                party['emailAddress'] = self.email_id

            if self.birth_dt:
                party['birthDate'] = self.birth_dt.isoformat()

        return party


    @property
    def name(self) -> str:
        """Return the full name of the party for comparison."""
        if self.last_name:
            if self.middle_name:
                return ' '.join((self.first_name, self.middle_name, self.last_name)).strip().upper()
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
                               .order_by(Party.party_id).all()

        return parties


    @classmethod
    def find_by_financing_id(cls, financing_id: int = None):
        """Return a list of party objects by financing statement ID."""
        parties = None
        if financing_id:
            parties = cls.query.filter(Party.financing_id == financing_id) \
                               .order_by(Party.party_id).all()

        return parties



    @staticmethod
    def create_from_json(json_data, party_type: str, registration_id: int = None):
        """Create a party object from a json schema object: map json to db."""
        party = Party()
        if party_type != 'DC':
            party.party_type_cd = party_type
        elif 'businessName' in json_data:
            party.party_type_cd = party_type
        else:
            party.party_type_cd = 'DI'

        if party_type != 'DC' and 'code' in json_data:
            party.client_party_id = int(json_data['code'])
        else:
            if party_type == 'DC' and 'birthDate' in json_data:
                party.birth_dt = date.fromisoformat(json_data['birthDate'])
            if 'businessName' in json_data:
                party.business_name = json_data['businessName'].strip().upper()
            else:
                party.last_name = json_data['personName']['last'].strip().upper()
                party.first_name = json_data['personName']['first'].strip().upper()
                if 'middle' in json_data['personName']:
                    party.middle_name = json_data['personName']['middle'].strip().upper()

            if 'emailAddress' in json_data:
                party.email_id = json_data['emailAddress']

            party.address = Address.create_from_json(json_data['address'])

        if registration_id:
            party.registration_id = registration_id

        return party


    @staticmethod
    def create_from_financing_json(json_data, registration_id: int = None):
        """Create a list of party objects from a financing statement json schema object: map json to db."""
        parties = []

        parties.append(Party.create_from_json(json_data['registeringParty'], 'RP', registration_id))
        if 'securedParties' in json_data:
            for secured in json_data['securedParties']:
                parties.append(Party.create_from_json(secured, 'SP', registration_id))
        if 'debtors' in json_data:
            for debtor in json_data['debtors']:
                parties.append(Party.create_from_json(debtor, 'DC', registration_id))

        return parties


    @staticmethod
    def create_from_statement_json(json_data, 
                                   registration_type: str,
                                   financing_id: int):
        """Create a list of party objects from a non-financing statement json schema object: map json to db."""
        parties = []

        # All statements have a registering party
        registering = Party.create_from_json(json_data['registeringParty'], 'RP', None)
        registering.financing_id = financing_id
        parties.append(registering)

        if registration_type == 'AS' or registration_type == 'CS':
            if 'addSecuredParties' in json_data:
                for secured in json_data['addSecuredParties']:
                    secured_party = Party.create_from_json(secured, 'SP', None)
                    secured_party.financing_id = financing_id
                    parties.append(secured_party)
            if 'addDebtors' in json_data:
                for debtor in json_data['addDebtors']:
                    debtor_party = Party.create_from_json(debtor, 'DC', None)
                    debtor_party.financing_id = financing_id
                    parties.append(debtor_party)

        return parties

    @staticmethod
    def verify_party_code(code: str):
        """Verify registering party or secured party code is legitimate."""
        if code and ClientParty.find_by_code(code):
            return True

        return False

#    @property
#    def valid_party_type_data(self) -> bool:
#        """Validate the model based on the party type (DC/DI/RP/SP)."""
#        if self.party_type == Party.PartyTypes.ORGANIZATION.value:
#            if not self.organization_name or self.first_name or self.middle_initial or self.last_name:
#                return False

#        elif self.party_type == Party.PartyTypes.PERSON.value:
#            if self.organization_name or not (self.first_name or self.middle_initial or self.last_name):
#                return False
#        return True



#@event.listens_for(Party, 'before_insert')
#@event.listens_for(Party, 'before_update')
#def receive_before_change(mapper, connection, target):  # pylint: disable=unused-argument; SQLAlchemy callback signature
#    """Run checks/updates before adding/changing the party model data."""
#    party = target

#    if not party.valid_party_type_data:
#        raise BusinessException(
#            error=f'Attempt to change/add {party.party_type} had invalid data.',
#            status_code=HTTPStatus.BAD_REQUEST
#        )
