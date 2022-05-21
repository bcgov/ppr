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
"""This module holds data for legacy DB2 MHR owner information."""
from enum import Enum

from flask import current_app

from mhr_api.exceptions import DatabaseException
from mhr_api.models import db, utils as model_utils

from .owngroup import Db2Owngroup


class Db2Owner(db.Model):
    """This class manages all of the legacy DB2 MHR owner nformation."""

    class OwnerTypes(str, Enum):
        """Render an Enum of the owner types."""

        INDIVIDUAL = 'I'
        BUSINESS = 'B'

    __bind_key__ = 'db2'
    __tablename__ = 'owner'

    manuhome_id = db.Column('MANHOMID', db.Integer, primary_key=True)
    group_id = db.Column('OWNGRPID', db.Integer, primary_key=True)
    owner_id = db.Column('OWNERID', db.Integer, primary_key=True)
    sequence_number = db.Column('OWNSEQNO', db.Integer, nullable=False)
    verified_flag = db.Column('VERIFIED', db.String(1), nullable=False)
    owner_type = db.Column('OWNRTYPE', db.String(1), nullable=False)
    compressed_name = db.Column('COMPNAME', db.String(30), nullable=False)
    phone_number = db.Column('OWNRFONE', db.String(10), nullable=False)
    postal_code = db.Column('OWNRPOCO', db.String(10), nullable=False)
    name = db.Column('OWNRNAME', db.String(70), nullable=False)
    suffix = db.Column('OWNRSUFF', db.String(70), nullable=False)
    legacy_address = db.Column('OWNRADDR', db.String(160), nullable=False)

    # parent keys

    # Relationships
    owngroup: Db2Owngroup = None

    def save(self):
        """Save the object to the database immediately. Only used for unit testing."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB2Owner.save exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    def strip(self):
        """Strip all string properties."""
        self.phone_number = self.phone_number.strip()
        self.postal_code = self.postal_code.strip()
        self.name = self.name.strip()
        self.suffix = self.suffix.strip()
        self.legacy_address = self.legacy_address.strip()

    @classmethod
    def find_by_manuhome_id(cls, manuhome_id: int):
        """Return the owners matching the manuhome id."""
        owners = None
        if manuhome_id and manuhome_id > 0:
            try:
                owners = cls.query.filter(Db2Owner.manuhome_id == manuhome_id).all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2Owner.find_by_manuhome_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if owners:
            for owner in owners:
                owner.strip()
                if owner.group_id and owner.group_id > 0:
                    owner.owngroup = Db2Owngroup.find_by_manuhome_id(owner.manuhome_id, owner.group_id)
        return owners

    @property
    def json(self):
        """Return a dict of this object, with keys in JSON format."""
        owner = {
            'groupId': self.group_id,
            'ownerId': self.owner_id,
            'sequenceNumber': self.sequence_number,
            'ownerType': self.owner_type,
            'verifiedFlag': self.verified_flag,
            'phoneNumber': self.phone_number,
            'postalCode': self.postal_code,
            'name': self.name,
            'suffix': self.suffix,
            'legacyAddress': self.legacy_address
        }
        return owner

    @property
    def registration_json(self):
        """Return a search registration dict of this object, with keys in JSON format."""
        # Response legacy data: allow for any column to be null.
        owner = {}
        if self.owner_type == Db2Owner.OwnerTypes.INDIVIDUAL:
            owner['individualName'] = model_utils.get_ind_name_from_db2(self.name)
        else:
            owner['organizationName'] = self.name
        owner['address'] = model_utils.get_address_from_db2(self.legacy_address, self.postal_code)
        if self.owngroup:
            owner['type'] = self.owngroup.tenancy_type
        return owner

    @staticmethod
    def create_from_dict(new_info: dict):
        """Create an owner object from dict/json."""
        owner = Db2Owner(owner_type=new_info.get('ownerType', ''),
                         verified_flag=new_info.get('verifiedFlag', ''),
                         phone_number=new_info.get('phoneNumber', ''),
                         postal_code=new_info.get('postalCode', ''),
                         name=new_info.get('name', ''),
                         suffix=new_info.get('suffix', ''),
                         legacy_address=new_info.get('legacyAddress', ''))
        return owner

    @staticmethod
    def create_from_json(json_data):
        """Create a document object from a json document schema object: map json to db."""
        owngroup = Db2Owngroup.create_from_dict(json_data)

        return owngroup
