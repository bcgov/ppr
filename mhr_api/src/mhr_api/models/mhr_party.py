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

# from flask import current_app
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from mhr_api.models import utils as model_utils

from .db import db
from .address import Address  # noqa: F401 pylint: disable=unused-import
from .type_tables import MhrPartyTypes, MhrOwnerStatusTypes


class MhrParty(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the MHR parties (people and organizations)."""

    __tablename__ = 'mhr_parties'

    id = db.Column('id', db.Integer, db.Sequence('mhr_party_id_seq'), primary_key=True)
    # party person
    first_name = db.Column('first_name', db.String(50), nullable=True)
    middle_name = db.Column('middle_name', db.String(50), nullable=True, index=True)
    last_name = db.Column('last_name', db.String(50), nullable=True)
    # or party business
    business_name = db.Column('business_name', db.String(150), index=True, nullable=True)
    # Search key
    compressed_name = db.Column('compressed_name', db.String(30), nullable=False, index=True)
    email_id = db.Column('email_address', db.String(250), nullable=True)
    phone_number = db.Column('phone_number', db.String(20), nullable=True)
    phone_extension = db.Column('phone_extension', db.String(10), nullable=True)

    # parent keys
    address_id = db.Column('address_id', db.Integer, db.ForeignKey('addresses.id'), nullable=True, index=True)
    registration_id = db.Column('registration_id', db.Integer, db.ForeignKey('mhr_registrations.id'), nullable=False,
                                index=True)
    change_registration_id = db.Column('change_registration_id', db.Integer, nullable=False, index=True)
    party_type = db.Column('party_type', PG_ENUM(MhrPartyTypes),
                           db.ForeignKey('mhr_party_types.party_type'), nullable=False)
    status_type = db.Column('status_type', PG_ENUM(MhrOwnerStatusTypes),
                            db.ForeignKey('mhr_owner_status_types.status_type'), nullable=False)
    # owner_group_id = db.Column('owner_group_id', db.Integer, nullable=True)
    owner_group_id = db.Column('owner_group_id', db.Integer, db.ForeignKey('mhr_owner_groups.id'), nullable=True)

    # Relationships - Address
    address = db.relationship('Address', foreign_keys=[address_id], uselist=False,
                              back_populates='mhr_party', cascade='all, delete')
    # Relationships - MhrRegistration
    registration = db.relationship('MhrRegistration', foreign_keys=[registration_id],
                                   back_populates='parties', cascade='all, delete', uselist=False)
    # Relationships - MhrOwnerGroup
    owner_group = db.relationship('MhrOwnerGroup', foreign_keys=[owner_group_id],
                                  back_populates='owners', cascade='all, delete', uselist=False)
    # Relationships - PartyType Don't need for now.
    # party_types = db.relationship('MhrPartyType', foreign_keys=[party_type],
    #                               back_populates='party', cascade='all, delete', uselist=False)

    @property
    def json(self) -> dict:
        """Return the party as a json object."""
        party = {
        }
        if self.party_type != MhrPartyTypes.SUBMITTING:
            party['partyId'] = self.id
            party['status'] = self.status_type
            party['partyType'] = self.party_type

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
        if self.phone_number:
            party['phoneNumber'] = self.phone_number
        if self.phone_extension:
            party['phoneExtension'] = self.phone_extension
        return party

    @classmethod
    def find_by_id(cls, party_id: int = None):
        """Return a party object by party ID."""
        party = None
        if party_id:
            party = cls.query.get(party_id)

        return party

    @classmethod
    def find_by_registration_id(cls, registration_id: int = None):
        """Return a list of party objects by registration id."""
        parties = None
        if registration_id:
            parties = cls.query.filter(MhrParty.registration_id == registration_id) \
                               .order_by(MhrParty.id).all()

        return parties

    @classmethod
    def find_by_change_registration_id(cls, registration_id: int = None):
        """Return a list of party objects by change registration id."""
        parties = None
        if registration_id:
            parties = cls.query.filter(MhrParty.change_registration_id == registration_id) \
                               .order_by(MhrParty.id).all()

        return parties

    @staticmethod
    def create_from_json(json_data, party_type: str, registration_id: int = None, change_registration_id: int = None):
        """Create a party object from a json schema object: map json to db."""
        # current_app.logger.info(json_data)
        party: MhrParty = MhrParty()
        party.party_type = party_type
        party.status_type = MhrOwnerStatusTypes.ACTIVE
        if json_data.get('businessName'):
            party.business_name = json_data['businessName'].strip().upper()
            party.compressed_name = model_utils.get_compressed_key(party.business_name)
        elif json_data.get('organizationName'):
            party.business_name = json_data['organizationName'].strip().upper()
            party.compressed_name = model_utils.get_compressed_key(party.business_name)
        elif json_data.get('individualName'):
            party.last_name = json_data['individualName']['last'].strip().upper()
            party.first_name = json_data['individualName']['first'].strip().upper()
            name = party.last_name + ' ' + party.first_name
            if json_data['individualName'].get('middle'):
                party.middle_name = json_data['individualName']['middle'].strip().upper()
                name += ' ' + party.middle_name
            party.compressed_name = model_utils.get_compressed_key(name)
        else:
            party.last_name = json_data['personName']['last'].strip().upper()
            party.first_name = json_data['personName']['first'].strip().upper()
            name = party.last_name + ' ' + party.first_name
            if json_data['personName'].get('middle'):
                party.middle_name = json_data['personName']['middle'].strip().upper()
                name += ' ' + party.middle_name
            party.compressed_name = model_utils.get_compressed_key(name)

        if json_data.get('emailAddress'):
            party.email_id = json_data['emailAddress'].strip()
        if json_data.get('phoneNumber'):
            party.phone_number = json_data['phoneNumber'].strip()
        if json_data.get('phoneExtension'):
            party.phone_extension = json_data['phoneExtension'].strip()

        party.address = Address.create_from_json(json_data['address'])

        if registration_id:
            party.registration_id = registration_id
            if not change_registration_id:
                party.change_registration_id = registration_id
        if change_registration_id:
            party.change_registration_id = change_registration_id
        return party

    @staticmethod
    def create_from_registration_json(json_data, registration_id: int = None):
        """Create a list of party objects from a financing statement json schema object: map json to db."""
        parties = []
        party = json_data.get('submittingParty')
        if party:
            parties.append(MhrParty.create_from_json(party, MhrPartyTypes.SUBMITTING, registration_id))
        # owners and owner groups here.
        return parties
