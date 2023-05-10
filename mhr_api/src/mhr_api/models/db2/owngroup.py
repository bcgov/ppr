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
"""This module holds data for legacy DB2 MHR owner group information."""
from flask import current_app

from mhr_api.exceptions import DatabaseException
from mhr_api.models import db, utils as model_utils
from mhr_api.models.type_tables import MhrTenancyTypes
from mhr_api.models.db2.owner import Db2Owner
from mhr_api.utils.base import BaseEnum


LEGACY_STATUS_NEW = {
    '3': 'ACTIVE',
    '4': 'EXEMPT',
    '5': 'PREVIOUS'
}
LEGACY_TENANCY_NEW = {
    'JT': 'JOINT',
    'TC': 'COMMON',
    'SO': 'SOLE'
}
NEW_TENANCY_LEGACY = {
    'JOINT': 'JT',
    'COMMON': 'TC',
    'SOLE': 'SO',
    'NA': 'TC',
    'JT': 'JT',
    'TC': 'TC',
    'SO': 'SO'
}


class Db2Owngroup(db.Model):
    """This class manages all of the legacy DB2 MHR owner group information."""

    class TenancyTypes(BaseEnum):
        """Render an Enum of the owner group tenancy types."""

        SOLE = 'SO'
        JOINT = 'JT'
        COMMON = 'TC'

    class StatusTypes(BaseEnum):
        """Render an Enum of the owner group status types."""

        DRAFT = '1'
        ACTIVE = '3'
        EXEMPT = '4'
        PREVIOUS = '5'

    __bind_key__ = 'db2'
    __tablename__ = 'owngroup'

    manuhome_id = db.Column('MANHOMID', db.Integer, db.ForeignKey('manuhome.manhomid'), primary_key=True)
    group_id = db.Column('OWNGRPID', db.Integer, primary_key=True)
    copy_id = db.Column('COPGRPID', db.Integer, nullable=False)
    sequence_number = db.Column('GRPSEQNO', db.Integer, nullable=False)
    status = db.Column('status', db.String(1), nullable=False)
    pending_flag = db.Column('pending', db.String(1), nullable=False)
    reg_document_id = db.Column('REGDOCID', db.String(8), nullable=False)
    can_document_id = db.Column('CANDOCID', db.String(8), nullable=False)
    tenancy_type = db.Column('TENYTYPE', db.String(2), nullable=False)
    lessee = db.Column('LESSEE', db.String(1), nullable=False)
    lessor = db.Column('LESSOR', db.String(1), nullable=False)
    interest = db.Column('interest', db.String(20), nullable=False)
    interest_numerator = db.Column('INTNUMER', db.Integer, nullable=False)
    tenancy_specified = db.Column('TENYSPEC', db.String(1), nullable=False)

    # parent keys

    # Relationships
    registration = db.relationship('Db2Manuhome', foreign_keys=[manuhome_id],
                                   back_populates='owner_groups', cascade='all, delete', uselist=False)
    group_owners = db.relationship('Db2Owner', overlaps='owner_group,registration')

    owners = []
    modified: bool = False
    interest_denominator: int = 0

    def save(self):
        """Save the object to the database immediately."""
        try:
            # current_app.logger.info('saving owner group')
            db.session.add(self)
            # current_app.logger.info(self.json)
            if self.owners and self.status != Db2Owngroup.StatusTypes.PREVIOUS:
                for owner in self.owners:
                    owner.save()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB2Owngroup.save exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    def strip(self):
        """Strip all string properties."""
        self.reg_document_id = self.reg_document_id.strip()
        self.can_document_id = self.can_document_id.strip()
        self.tenancy_type = self.tenancy_type.strip()
        self.interest = self.interest.strip()

    @classmethod
    def find_by_manuhome_id(cls, manuhome_id: int, group_id: int):
        """Return the owner group matching the manuhome id and group id."""
        owngroup = None
        if manuhome_id and manuhome_id > 0 and group_id and group_id > 0:
            try:
                owngroup = cls.query.filter(Db2Owngroup.manuhome_id == manuhome_id,
                                            Db2Owngroup.group_id == group_id).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2Owngroup.find_by_manuhome_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if owngroup:
            owngroup.strip()
        return owngroup

    @classmethod
    def find_all_by_manuhome_id(cls, manuhome_id: int):
        """Return the owner groups and owners matching the manuhome id."""
        groups = []
        if manuhome_id and manuhome_id > 0:
            try:
                groups = cls.query.filter(Db2Owngroup.manuhome_id == manuhome_id,
                                          Db2Owngroup.status != '1').order_by(Db2Owngroup.group_id).all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2Owngroup.find_all_by_manuhome_id groups exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if groups:
            owners = []
            try:
                owners = Db2Owner.find_by_manuhome_id(manuhome_id)
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2Owngroup.find_all_by_manuhome_id owners exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
            for group in groups:
                group.strip()
                group.owners = []
                for owner in owners:
                    if owner.group_id == group.group_id:
                        group.owners.append(owner)
        return groups

    @classmethod
    def find_by_reg_doc_id(cls, manuhome_id: int, reg_document_id: str):
        """Return the owner group matching the manuhome id and registration document id."""
        # current_app.logger.debug(f'manhomid={manuhome_id} doc_id={reg_document_id}')
        groups = []
        if manuhome_id and manuhome_id > 0 and reg_document_id:
            try:
                groups = cls.query.filter(Db2Owngroup.manuhome_id == manuhome_id,
                                          Db2Owngroup.reg_document_id == reg_document_id)\
                                  .order_by(Db2Owngroup.group_id).all()
                # current_app.logger.info(len(groups))
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2Owngroup.find_by_reg_doc_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if groups:
            owners = []
            try:
                owners = Db2Owner.find_by_manuhome_id(manuhome_id)
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2Owngroup.find_all_by_manuhome_id owners exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
            for group in groups:
                group.strip()
                group.owners = []
                for owner in owners:
                    if owner.group_id == group.group_id:
                        group.owners.append(owner)
        return groups

    @property
    def json(self):
        """Return a dict of this object, with keys in JSON format."""
        return self.registration_json

    @property
    def registration_json(self):
        """Return a search registration dict of this object, with keys in JSON format."""
        self.strip()
        group = {
            'groupId': self.group_id,
            'type': LEGACY_TENANCY_NEW.get(self.tenancy_type),
            'status': LEGACY_STATUS_NEW.get(self.status),
            'interest': self.interest,
            'interestNumerator': self.get_interest_fraction(True),
            'interestDenominator': self.get_interest_fraction(False),
            'tenancySpecified': True
        }
        # Remove fraction from interest description for UI.
        if self.tenancy_type in (self.TenancyTypes.COMMON, self.TenancyTypes.JOINT) and self.interest:
            fraction: str = str(group.get('interestNumerator')) + '/' + str(group.get('interestDenominator'))
            interest_json: str = group.get('interest')
            interest_json = interest_json.replace(fraction, '')
            if self.interest != interest_json:
                group['interest'] = interest_json.strip()
        if self.tenancy_specified == 'N':
            group['tenancySpecified'] = False
        owners = []
        if self.owners:
            for owner in self.owners:
                owner_json = owner.new_registration_json
                owner_json['type'] = group['type']
                owners.append(owner_json)
        group['owners'] = owners
        return group

    def get_interest_fraction(self, numerator: bool = False) -> int:
        """For tenants in common try to get the numerator or denominator from the interest."""
        value: int = 0
        if not self.interest or self.tenancy_type == self.TenancyTypes.SOLE:
            return value
        tokens = str(self.interest).split()
        for token in tokens:
            if token.find('/') > 0:
                fraction = token.split('/')
                if numerator:
                    value = int(fraction[0])
                else:
                    value = int(fraction[1])
        return value

    @staticmethod
    def create_from_dict(new_info: dict):
        """Create an owngroup object from dict/json."""
        owngroup = Db2Owngroup(status=new_info.get('status', ''),
                               pending_flag=new_info.get('pendingFlag', ''),
                               reg_document_id=new_info.get('registrationDocumentId', ''),
                               can_document_id=new_info.get('canDocumentId', ''),
                               tenancy_type=new_info.get('tenancyType', ''),
                               lessee=new_info.get('lessee', ''),
                               lessor=new_info.get('lessor', ''),
                               interest=new_info.get('interest', ''),
                               interest_numerator=new_info.get('interestNumerator', 0),
                               tenancy_specified=new_info.get('tenancySpecified', 'Y'))
        return owngroup

    @staticmethod
    def create_from_json(json_data):
        """Create a document object from a json document schema object: map json to db."""
        owngroup = Db2Owngroup.create_from_dict(json_data)

        return owngroup

    @staticmethod
    def create_from_registration(registration, new_info, group_id: int):
        """Create a new owner group object from a new MH registration."""
        # current_app.logger.info('group group id=' + str(group_id))
        # current_app.logger.info(new_info)
        tenancy: str = new_info.get('type', Db2Owngroup.TenancyTypes.SOLE)
        tenancy_type: str = NEW_TENANCY_LEGACY.get(tenancy)
        if tenancy == MhrTenancyTypes.NA and len(new_info.get('owners')) > 1:
            tenancy_type = Db2Owngroup.TenancyTypes.JOINT
        interest: str = new_info.get('interest', '')
        if tenancy_type == Db2Owngroup.TenancyTypes.COMMON or \
                (tenancy_type == Db2Owngroup.TenancyTypes.JOINT and new_info.get('interestDenominator') and
                 new_info.get('interestDenominator') > 0):
            if not interest:  # This should never happen.
                interest = model_utils.OWNER_INTEREST_UNDIVIDED
            elif interest and len(interest) <= 10 and not interest.startswith(model_utils.OWNER_INTEREST_UNDIVIDED):
                interest = model_utils.OWNER_INTEREST_UNDIVIDED + ' ' + interest
        owngroup = Db2Owngroup(manuhome_id=registration.id,
                               group_id=group_id,
                               copy_id=0,
                               sequence_number=1,
                               status=Db2Owngroup.StatusTypes.ACTIVE,
                               pending_flag='',
                               reg_document_id=new_info.get('documentId', ''),
                               can_document_id='',
                               tenancy_type=tenancy_type,
                               lessee=new_info.get('lessee', ''),
                               lessor=new_info.get('lessor', ''),
                               interest=interest,
                               interest_numerator=new_info.get('interestNumerator', 0),
                               tenancy_specified=new_info.get('tenancySpecified', 'Y'))
        owngroup.interest_denominator = new_info.get('interestDenominator', 0)
        owngroup.owners = []
        # TBD: only applies to JOINT tenancy type with 2 or more executors:
        # if not new_info.get('tenancySpecified'):
        #    owngroup.tenancy_specified = 'N'
        for i, owner in enumerate(new_info.get('owners')):
            new_owner = Db2Owner.create_from_registration(registration, owner, group_id, (i + 1))
            # current_app.logger.info('adding new owner i=' + str(i))
            owngroup.owners.append(new_owner)
        # current_app.logger.info('new owners size=' + str(len(owngroup.owners)))
        return owngroup
