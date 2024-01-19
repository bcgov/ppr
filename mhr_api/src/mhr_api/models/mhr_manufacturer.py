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
from mhr_api.models import utils as model_utils, registration_utils as reg_utils

from .address import Address
from .mhr_party import MhrParty
from .mhr_registration import MhrRegistration
from .type_tables import (
    MhrLocationTypes,
    MhrOwnerStatusTypes,
    MhrPartyTypes,
    MhrRegistrationTypes,
    MhrRegistrationStatusTypes
)
from .db import db


MANUFACTURER_MHR_NUMBER: str = 'MAN000'
MANUFACTURER_DRAFT_ID: int = 0
COMBINED_NAME: str = '{owner_name} / {dba_name}'


class MhrManufacturer(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the MHR manufacturer information."""

    __tablename__ = 'mhr_manufacturers'

    id = db.Column('id', db.Integer, db.Sequence('mhr_manufacturer_id_seq'), primary_key=True)
    manufacturer_name = db.Column('manufacturer_name', db.String(150), nullable=False)
    dba_name = db.Column('dba_name', db.String(150), nullable=True)
    authorization_name = db.Column('authorization_name', db.String(150), nullable=True)
    account_id = db.Column('account_id', db.String(20), nullable=True)
    bcol_account = db.Column('bcol_account', db.String(8), nullable=True)
    terms_accepted = db.Column('terms_accepted', db.String(1), nullable=True)

    # parent keys
    registration_id = db.Column('registration_id', db.Integer, db.ForeignKey('mhr_registrations.id'), nullable=False,
                                index=True)
    submitting_party_id = db.Column('submitting_party_id', db.Integer, db.ForeignKey('mhr_parties.id'), nullable=False)
    owner_party_id = db.Column('owner_party_id', db.Integer, db.ForeignKey('mhr_parties.id'), nullable=False)
    dealer_party_id = db.Column('dealer_party_id', db.Integer, db.ForeignKey('mhr_parties.id'), nullable=False)

    # Relationships
    registration = db.relationship('MhrRegistration', foreign_keys=[registration_id], uselist=False)
    submitting_party = db.relationship('MhrParty', foreign_keys=[submitting_party_id], uselist=False)
    owner = db.relationship('MhrParty', foreign_keys=[owner_party_id], uselist=False)
    dealer = db.relationship('MhrParty', foreign_keys=[dealer_party_id], uselist=False)

    @property
    def json(self) -> dict:
        """Return the manufacturer as a json object."""
        manufacturer = {
            'termsAccepted': bool(self.terms_accepted and self.terms_accepted == 'Y'),
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
        if self.owner.email_id:
            owner['emailAddress'] = self.owner.email_id
        if self.owner.phone_number:
            owner['phoneNumber'] = self.owner.phone_number
        if self.owner.phone_extension:
            owner['phoneExtension'] = self.owner.phone_extension
        owners.append(owner)
        group = {
            'groupId': 1,
            'type': 'SOLE',
            'owners': owners
        }
        manufacturer['ownerGroups'].append(group)
        if self.dba_name:
            manufacturer['dbaName'] = self.dba_name
            name: str = COMBINED_NAME.format(owner_name=self.owner.business_name, dba_name=self.dba_name)
            manufacturer['location']['dealerName'] = name
            manufacturer['description']['manufacturer'] = name
        if self.authorization_name:
            manufacturer['authorizationName'] = self.authorization_name
        return manufacturer

    def save(self):
        """Render a registration to the local cache."""
        db.session.add(self)
        db.session.commit()

    def update(self, json_data: dict):
        """Update the manufacturer information."""
        if not json_data:
            return
        if json_data.get('dbaName'):
            self.dba_name = json_data['dbaName'].strip().upper()
        else:
            self.dba_name = None
        if json_data.get('authorizationName'):
            self.authorization_name = json_data['authorizationName'].strip()
        else:
            self.authorization_name = None
        self.terms_accepted = 'Y' if json_data.get('termsAccepted') else None
        owner = json_data['ownerGroups'][0]['owners'][0]
        self.owner.email_id = owner['emailAddress'].strip() if owner.get('emailAddress') else None
        self.owner.phone_number = owner['phoneNumber'].strip() if owner.get('phoneNumber') else None
        self.owner.phone_extension = owner['phoneExtension'].strip() if owner.get('phoneExtension') else None
        if owner.get('organizationName'):
            self.owner.business_name = owner['organizationName'].strip().upper()
            self.owner.last_name = None
            self.owner.first_name = None
            self.owner.middle_name = None
        else:
            self.owner.business_name = None
            self.owner.last_name = owner['individualName']['last'].strip().upper()
            self.owner.first_name = owner['individualName']['first'].strip().upper()
            if owner['individualName'].get('middle'):
                self.owner.middle_name = owner['individualName']['middle'].strip().upper()
        if self.owner.address.json != owner.get('address'):
            self.owner.address = Address.create_from_json(owner.get('address'))
        self.dealer.business_name = str(json_data['location'].get('dealerName')).strip().upper()
        if self.dealer.address.json != json_data['location'].get('address'):
            self.dealer.address = Address.create_from_json(json_data['location']['address'])
        self.manufacturer_name = str(json_data['description'].get('manufacturer')).strip().upper()
        db.session.add(self)
        db.session.commit()

    @classmethod
    def delete(cls, account_id: str):
        """Delete a manufacturer by account ID."""
        manufacturer = None
        if account_id:
            manufacturer = cls.find_by_account_id(account_id)
        if manufacturer:
            db.session.delete(manufacturer)
            db.session.commit()
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

    @staticmethod
    def create_manufacturer_from_json(json_data, account_id: str, user_id: str):
        """Create manufacturer objects from dict/json."""
        manufacturer: MhrManufacturer = MhrManufacturer(account_id=account_id)
        registration: MhrRegistration = MhrRegistration(registration_type=MhrRegistrationTypes.MANUFACTURER,
                                                        mhr_number=MANUFACTURER_MHR_NUMBER,
                                                        status_type=MhrRegistrationStatusTypes.ACTIVE,
                                                        draft_id=MANUFACTURER_DRAFT_ID,
                                                        account_id=account_id,
                                                        user_id=user_id)
        registration.id = reg_utils.get_registration_id()
        registration.registration_ts = model_utils.now_ts()
        manufacturer.registration = registration
        manufacturer.registration_id = registration.id
        party = json_data.get('submittingParty')
        manufacturer.submitting_party = MhrParty.create_from_json(party, MhrPartyTypes.SUBMITTING, registration.id)
        owner = json_data['ownerGroups'][0]['owners'][0]
        manufacturer.owner = MhrParty.create_from_json(owner, MhrPartyTypes.OWNER_BUS, registration.id)
        name: str = json_data['location'].get('dealerName')
        dealer: MhrParty = MhrParty(party_type=MhrPartyTypes.MANUFACTURER,
                                    registration_id=registration.id,
                                    change_registration_id=registration.id,
                                    status_type=MhrOwnerStatusTypes.ACTIVE,
                                    business_name=name.strip().upper())
        dealer.address = Address.create_from_json(json_data['location'].get('address'))
        manufacturer.dealer = dealer
        name = json_data['description'].get('manufacturer')
        manufacturer.manufacturer_name = name.strip().upper()
        if json_data.get('dbaName'):
            manufacturer.dba_name = json_data['dbaName'].strip().upper()
        if json_data.get('authorizationName'):
            manufacturer.authorization_name = json_data['authorizationName'].strip()
        if json_data.get('termsAccepted'):
            manufacturer.terms_accepted = 'Y'
        return manufacturer
