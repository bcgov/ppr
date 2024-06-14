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
from sqlalchemy.sql import text
from mhr_api.exceptions import DatabaseException
from mhr_api.models import db, utils as model_utils
from mhr_api.models.db2 import address_utils
from mhr_api.models.type_tables import MhrPartyTypes


OWNERS_QUERY = """
select o.manhomid, o.owngrpid, o.ownerid, o.ownseqno, o.verified, o.ownrfone, o.ownrpoco, o.ownrname, o.ownrsuff,
       o.ownraddr, og.status, og.tenytype, o.ownrtype
  from owner o, owngroup og
 where o.manhomid = :query_value
   and og.manhomid = o.manhomid
   and o.owngrpid = og.owngrpid
   and og.status in ('3', '4')
"""
EXECUTOR_SUFFIX = 'EXEC'
TRUST_SUFFIX = 'TRUST'
TRUSTEE_SUFFIX = 'BANKRUPT'
ADMIN_SUFFIX = 'ADMIN'


class Db2Owner(db.Model):
    """This class manages all of the legacy DB2 MHR owner nformation."""

    class OwnerTypes(str, Enum):
        """Render an Enum of the owner types."""

        INDIVIDUAL = 'I'
        BUSINESS = 'B'

    __bind_key__ = 'db2'
    __tablename__ = 'owner'
    __allow_unmapped__ = True

    manuhome_id = db.mapped_column('MANHOMID', db.Integer, db.ForeignKey('manuhome.manhomid'))
    group_id = db.mapped_column('OWNGRPID', db.Integer)
    owner_id = db.mapped_column('OWNERID', db.Integer)
    sequence_number = db.mapped_column('OWNSEQNO', db.Integer, nullable=False)
    verified_flag = db.mapped_column('VERIFIED', db.String(1), nullable=False)
    owner_type = db.mapped_column('OWNRTYPE', db.String(1), nullable=False)
    compressed_name = db.mapped_column('COMPNAME', db.String(30), nullable=False)
    phone_number = db.mapped_column('OWNRFONE', db.String(10), nullable=False)
    postal_code = db.mapped_column('OWNRPOCO', db.String(10), nullable=False)
    name = db.mapped_column('OWNRNAME', db.String(70), nullable=False)
    suffix = db.mapped_column('OWNRSUFF', db.String(70), nullable=False)
    legacy_address = db.mapped_column('OWNRADDR', db.String(160), nullable=False)

    # parent keys

    # Relationships
    registration = db.relationship('Db2Manuhome', foreign_keys=[manuhome_id],
                                   back_populates='owners', cascade='all, delete', uselist=False)
    owner_group = db.relationship('Db2Owngroup', foreign_keys=[manuhome_id, group_id], overlaps='registration')

    __table_args__ = (
        db.PrimaryKeyConstraint('MANHOMID', 'OWNGRPID', 'OWNERID'),
        db.ForeignKeyConstraint(
            ['MANHOMID', 'OWNGRPID'], ['owngroup.MANHOMID', 'owngroup.OWNGRPID']
        )
    )

    type: str = None
    status: str = None

    def save(self):
        """Save the object to the database immediately."""
        try:
            # current_app.logger.info('saving owner')
            db.session.add(self)
            # current_app.logger.info(self.json)
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
                owners = db.session.query(Db2Owner).filter(Db2Owner.manuhome_id == manuhome_id).all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2Owner.find_by_manuhome_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if owners:
            for owner in owners:
                owner.strip()
        return owners

    @classmethod
    def find_by_manuhome_id_registration(cls, manuhome_id: int):
        """Return the owners matching the manuhome id."""
        owners = None
        rows = None
        if manuhome_id and manuhome_id > 0:
            try:
                query = text(OWNERS_QUERY)
                with db.engines['db2'].connect() as conn:
                    result = conn.execute(query, {'query_value': manuhome_id})
                    rows = result.fetchall()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2Owner.find_by_manuhome_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if rows is not None:
            owners = []
            for row in rows:
                owner: Db2Owner = Db2Owner(manuhome_id=manuhome_id)
                owner.group_id = int(row[1])
                owner.owner_id = int(row[2])
                owner.sequence_number = int(row[3])
                owner.verified_flag = str(row[4])
                owner.phone_number = str(row[5])
                owner.postal_code = str(row[6])
                owner.name = str(row[7])
                owner.suffix = str(row[8])
                owner.legacy_address = str(row[9])
                owner.status = str(row[10])
                owner.type = str(row[11])
                owner.owner_type = str(row[12])
                owners.append(owner)
        return owners

    @property
    def json(self):
        """Return a dict of this object, with keys in JSON format."""
        return self.registration_json

    @property
    def registration_json(self):
        """Return a search registration dict of this object, with keys in JSON format."""
        # Response legacy data: allow for any column to be null.
        self.strip()
        owner = {}
        if self.status and self.status == '5':
            return owner
        if self.owner_type == Db2Owner.OwnerTypes.INDIVIDUAL:
            owner['individualName'] = model_utils.get_ind_name_from_db2(self.name)
        else:
            owner['organizationName'] = self.name
        if self.phone_number:
            owner['phoneNumber'] = self.phone_number
        owner['address'] = address_utils.get_address_from_db2_owner(self.legacy_address, self.postal_code)
        owner['type'] = self.type
        if self.status == '3':
            owner['status'] = 'ACTIVE'
        elif self.status == '4':
            owner['status'] = 'EXEMPT'
        else:
            owner['status'] = 'PREVIOUS'
        owner['partyType'] = self.get_party_type()
        owner = self.adjust_suffix(owner)
        return owner

    @property
    def new_registration_json(self):
        """Return a new registration dict of this object, with keys in JSON format."""
        self.strip()
        owner = {
            'type': self.owner_type
        }
        if self.owner_type == Db2Owner.OwnerTypes.INDIVIDUAL:
            owner['individualName'] = model_utils.get_ind_name_from_db2(self.name)
        else:
            owner['organizationName'] = self.name
        if self.phone_number:
            owner['phoneNumber'] = self.phone_number
        owner['address'] = address_utils.get_address_from_db2_owner(self.legacy_address, self.postal_code)
        owner['partyType'] = self.get_party_type()
        owner = self.adjust_suffix(owner)
        return owner

    def get_party_type(self) -> str:
        """Derive the party type from the owner type and suffix value."""
        party_type: str = MhrPartyTypes.OWNER_BUS
        if self.owner_type == Db2Owner.OwnerTypes.INDIVIDUAL:
            party_type = MhrPartyTypes.OWNER_IND
        if self.suffix:
            suffix: str = str(self.suffix)
            if suffix.find(EXECUTOR_SUFFIX) != -1:
                party_type = MhrPartyTypes.EXECUTOR
            elif suffix.find(TRUSTEE_SUFFIX) != -1:
                party_type = MhrPartyTypes.TRUSTEE
            # elif suffix.find(TRUST_SUFFIX) != -1:
            #    party_type = MhrPartyTypes.TRUST
            elif suffix.find(ADMIN_SUFFIX) != -1:
                party_type = MhrPartyTypes.ADMINISTRATOR
        return party_type

    def adjust_suffix(self, owner_json: dict) -> dict:
        """Conditionally derive the suffix and adjust the middle names and description.."""
        if not self.suffix:
            return owner_json
        if owner_json['partyType'] == MhrPartyTypes.OWNER_BUS:
            owner_json['suffix'] = self.suffix
        elif owner_json['partyType'] == MhrPartyTypes.OWNER_IND:
            if self.suffix == 'JUNIOR' or self.suffix.find('TRUST') != -1 or self.suffix.find('WILL') != -1 or \
                    self.suffix.find('INTEREST') != -1 or \
                    self.suffix[0:2] in ('MR', 'MS', 'JR', 'DR', 'SR', 'N/', 'II'):
                owner_json['suffix'] = self.suffix
            else:  # suffix is extra middle names.
                middle_name = str(owner_json['individualName'].get('middle', '') + ' ' + self.suffix)
                name_list = middle_name.split(',', 1)
                if name_list and len(name_list) > 1:
                    owner_json['individualName']['middle'] = name_list[0]
                    owner_json['suffix'] = name_list[1].strip()
                else:
                    owner_json['individualName']['middle'] = middle_name.strip()
        else:
            suffix_list = self.suffix.split(',', 1)
            if suffix_list and len(suffix_list) > 1:
                extra_names = suffix_list[0]
                if extra_names.find('ADMIN') < 0 and extra_names.find('EXEC') < 0 and extra_names.find('TRUST') < 0 \
                        and extra_names.find('BANKRUP') < 0 \
                        and extra_names[0:2] not in ('MR', 'MS', 'JR', 'DR', 'SR'):
                    owner_json['description'] = suffix_list[1].strip()
                    middle_name = str(owner_json['individualName'].get('middle', '') + ' ' + extra_names)
                    owner_json['individualName']['middle'] = middle_name.strip()
                else:
                    owner_json['description'] = self.suffix
            else:
                owner_json['description'] = self.suffix
        return owner_json

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
        """Create an owner object from a json document schema object: map json to db."""
        owner = Db2Owner.create_from_dict(json_data)
        return owner

    @staticmethod
    def create_from_registration(registration, new_info, group_id: int, owner_id: int):
        """Create a new owner object from a new MH registration."""
        # current_app.logger.info('owner group id=' + str(group_id) + ' owner id=' + str(owner_id))
        # current_app.logger.info(new_info)
        address = new_info['address']
        name = ''
        owner_type = Db2Owner.OwnerTypes.BUSINESS.value if new_info.get('organizationName') \
            else Db2Owner.OwnerTypes.INDIVIDUAL.value
        if new_info.get('organizationName'):
            name = str(new_info.get('organizationName')).upper()
        else:
            name = Db2Owner.to_legacy_individual_name(new_info)
        compressed_name = model_utils.get_compressed_key(name)
        suffix: str = Db2Owner.to_legacy_suffix(new_info)
        owner = Db2Owner(manuhome_id=registration.id,
                         group_id=group_id,
                         owner_id=owner_id,
                         sequence_number=owner_id,  # Identical value to owner_id in the legacy db.
                         owner_type=owner_type,
                         verified_flag='',
                         phone_number=str(new_info.get('phoneNumber', ''))[0:10],
                         postal_code=address_utils.format_postal_code(address),
                         name=name[0:70],
                         compressed_name=compressed_name,
                         suffix=suffix,
                         legacy_address=address_utils.to_db2_owner_address(address))
        return owner

    @staticmethod
    def to_legacy_individual_name(new_info: dict) -> str:
        """Format an individual name as a DB2 legacy name."""
        name_json = new_info.get('individualName')
        db2_name = str(name_json['last']).upper().ljust(25, ' ')
        if name_json.get('middle'):
            first = str(name_json['first']).upper().ljust(15, ' ')
            middle = str(name_json['middle']).upper()
            # If multiple middle names, all but the first go in the suffix.
            middle_list = middle.split(' ', 1)
            if middle_list:
                db2_name += first + middle_list[0].ljust(30, ' ')
            else:
                db2_name += first + middle.ljust(30, ' ')
        else:
            first = str(name_json['first']).upper().ljust(45, ' ')
            db2_name += first
        return db2_name[:70]

    @staticmethod
    def to_legacy_suffix(new_info: dict) -> str:
        """Format an owner suffix as a DB2 legacy name suffix."""
        suffix: str = new_info.get('suffix', '')
        if suffix:
            suffix = suffix.strip().upper()
        # Prepend exta middle names if present
        suffix_name: str = ''
        if new_info.get('individualName') and new_info['individualName'].get('middle'):
            middle = str(new_info['individualName'].get('middle')).upper()
            middle_list = middle.split(' ', 1)
            if middle_list and len(middle_list) > 1:
                suffix_name = middle_list[1].strip()
        # Description is only for TRUSTEE/ADMINISTRATOR/EXECUTOR: ignore for owners.
        if new_info.get('partyType') and new_info.get('description') and \
                new_info.get('partyType') not in (MhrPartyTypes.OWNER_BUS, MhrPartyTypes.OWNER_IND):
            suffix = str(new_info.get('description')).strip().upper()
            if new_info.get('partyType') == MhrPartyTypes.TRUSTEE and suffix.find(TRUSTEE_SUFFIX) < 0:
                suffix = TRUSTEE_SUFFIX + ' ' + suffix
            elif suffix.find(new_info.get('partyType')) < 0:
                suffix = new_info.get('partyType') + ' ' + suffix
        if suffix and suffix_name:
            suffix = suffix_name + ', ' + suffix
        elif suffix_name:
            suffix = suffix_name
        if len(suffix) > 70:
            suffix = suffix[0:70]
        return suffix
