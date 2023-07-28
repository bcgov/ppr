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
"""This module holds data for qualifid supplier party information."""
from __future__ import annotations

# from flask import current_app
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from .db import db
from .address import Address  # noqa: F401 pylint: disable=unused-import
from .type_tables import MhrPartyTypes


class MhrQualifiedSupplier(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the MHR qualiifed supplier parties (people and businesses)."""

    __tablename__ = 'mhr_qualified_suppliers'

    id = db.Column('id', db.Integer, db.Sequence('mhr_supplier_id_seq'), primary_key=True)
    # party person
    first_name = db.Column('first_name', db.String(50), nullable=True)
    middle_name = db.Column('middle_name', db.String(50), nullable=True)
    last_name = db.Column('last_name', db.String(50), nullable=True)
    # or party business
    business_name = db.Column('business_name', db.String(150), nullable=True)
    account_id = db.Column('account_id', db.String(20), nullable=False)
    email_id = db.Column('email_address', db.String(250), nullable=True)
    phone_number = db.Column('phone_number', db.String(20), nullable=True)
    phone_extension = db.Column('phone_extension', db.String(10), nullable=True)

    # parent keys
    address_id = db.Column('address_id', db.Integer, db.ForeignKey('addresses.id'), nullable=True, index=True)
    party_type = db.Column('party_type', PG_ENUM(MhrPartyTypes),
                           db.ForeignKey('mhr_party_types.party_type'), nullable=False)
    # Relationships - Addressess
    address = db.relationship('Address', foreign_keys=[address_id], uselist=False)

    @property
    def json(self) -> dict:
        """Return the party as a json object."""
        party = {
            'partyType': self.party_type,
            'address': self.address.json
        }
        if self.business_name:
            party['businessName'] = self.business_name
        elif self.last_name:
            person_name = {
                'first': self.first_name,
                'last': self.last_name
            }
            if self.middle_name:
                person_name['middle'] = self.middle_name
            party['personName'] = person_name
        if self.email_id:
            party['emailAddress'] = self.email_id
        if self.phone_number:
            party['phoneNumber'] = self.phone_number
        if self.phone_extension:
            party['phoneExtension'] = self.phone_extension
        return party

    def save(self):
        """Render a qualified supplier to the local cache."""
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, supplier_id: int = None):
        """Return a qualified suppier party object by primary key ID."""
        supplier = None
        if supplier_id:
            supplier = cls.query.get(supplier_id)
        return supplier

    @classmethod
    def find_by_account_id(cls, account_id: str = None):
        """Return a list of party objects by registration id."""
        supplier = None
        if account_id:
            supplier = cls.query.filter(MhrQualifiedSupplier.account_id == account_id).one_or_none()
        return supplier

    @staticmethod
    def create_from_json(json_data, account_id: str, party_type: str):
        """Create a qualified supplier object from a json schema object: map json to db."""
        # current_app.logger.info(json_data)
        supplier: MhrQualifiedSupplier = MhrQualifiedSupplier(account_id=account_id,
                                                              party_type=party_type)
        if json_data.get('businessName'):
            supplier.business_name = json_data['businessName'].strip().upper()
        else:
            supplier.last_name = json_data['personName']['last'].strip().upper()
            supplier.first_name = json_data['personName']['first'].strip().upper()
            if json_data['personName'].get('middle'):
                supplier.middle_name = json_data['personName']['middle'].strip().upper()
        if json_data.get('emailAddress'):
            supplier.email_id = json_data['emailAddress'].strip()
        if json_data.get('phoneNumber'):
            supplier.phone_number = json_data['phoneNumber'].strip()
        if json_data.get('phoneExtension'):
            supplier.phone_extension = json_data['phoneExtension'].strip()
        supplier.address = Address.create_from_json(json_data['address'])
        return supplier
