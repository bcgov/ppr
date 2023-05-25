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
"""This module holds data for MHR manufacturers."""

from flask import current_app

from mhr_api.exceptions import DatabaseException

from mhr_api.models.type_tables import MhrLocationTypes
from .db import db


class MhrManufacturer(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the MHR manufacturer information."""

    __tablename__ = 'mhr_manufacturers'

    id = db.Column('id', db.Integer, db.Sequence('mhr_manufacturer_id_seq'), primary_key=True)
    manufacturer_name = db.Column('manufacturer_name', db.String(150), nullable=False)
    account_id = db.Column('account_id', db.String(20), nullable=True)
    bcol_account = db.Column('bcol_account', db.String(8), nullable=True)

    # parent keys
    registration_id = db.Column('registration_id', db.Integer, db.ForeignKey('mhr_registrations.id'), nullable=False,
                                index=True)
    submitting_party_id = db.Column('submitting_party_id', db.Integer, db.ForeignKey('mhr_parties.id'), nullable=False)
    owner_party_id = db.Column('owner_party_id', db.Integer, db.ForeignKey('mhr_parties.id'), nullable=False)
    dealer_party_id = db.Column('dealer_party_id', db.Integer, db.ForeignKey('mhr_parties.id'), nullable=False)

    # Relationships
    submitting_party = db.relationship('MhrParty', foreign_keys=[submitting_party_id], uselist=False)
    owner = db.relationship('MhrParty', foreign_keys=[owner_party_id], uselist=False)
    dealer = db.relationship('MhrParty', foreign_keys=[dealer_party_id], uselist=False)

    @property
    def json(self) -> dict:
        """Return the manufacturer as a json object."""
        manufacturer = {
            'submittingParty': self.submitting_party.json,
            'ownerGroups': [],
            'location': {
                'locationType': MhrLocationTypes.MANUFACTURER.value,
                'leaveProvince': False,
                'dealerName': self.dealer.business_name,
                'address': self.dealer.address.json
            },
            'description': {
                'manufacturer': self.manufacturer_name
            }
        }
        owners = []
        owner = {
            'organizationName': self.owner.business_name,
            'partyType': self.owner.party_type.value,
            'address': self.owner.address.json
        }
        owners.append(owner)
        group = {
            'groupId': 1,
            'type': 'SOLE',
            'owners': owners
        }
        manufacturer['ownerGroups'].append(group)
        return manufacturer

    @classmethod
    def find_by_id(cls, pkey: int = None):
        """Return a manufacturer object by primary key."""
        manufacturer = None
        if pkey:
            try:
                manufacturer = cls.query.get(pkey)
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('MhrManufacturerfind_by_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        return manufacturer

    @classmethod
    def find_by_registration_id(cls, reg_id: int):
        """Return a manufacturer object by registration id."""
        manufacturer = None
        if reg_id:
            try:
                manufacturer = cls.query.filter(MhrManufacturer.registration_id == reg_id).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('MhrManufacturer.find_by_registration_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        return manufacturer

    @classmethod
    def find_by_account_id(cls, account_id: str):
        """Return a manufacturer object by account id."""
        manufacturer = None
        if account_id:
            try:
                manufacturer = cls.query.filter(MhrManufacturer.account_id == account_id).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('MhrManufacturer.find_by_account_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        return manufacturer
