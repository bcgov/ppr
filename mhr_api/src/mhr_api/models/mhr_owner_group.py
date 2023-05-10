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
"""This module holds data for MHR owner groups."""

from flask import current_app
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from mhr_api.exceptions import DatabaseException
from mhr_api.models import utils as model_utils

from .db import db
from .type_tables import MhrTenancyTypes, MhrOwnerStatusTypes


class MhrOwnerGroup(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the MHR owner group information."""

    __tablename__ = 'mhr_owner_groups'

    id = db.Column('id', db.Integer, db.Sequence('mhr_owner_group_id_seq'), primary_key=True)
    group_id = db.Column('sequence_number', db.Integer, nullable=True)
    interest = db.Column('interest', db.String(20), nullable=True)
    interest_numerator = db.Column('interest_numerator', db.Integer, nullable=False)
    interest_denominator = db.Column('interest_denominator', db.Integer, nullable=False)
    tenancy_specified = db.Column('tenancy_specified', db.String(1), nullable=False)

    # parent keys
    registration_id = db.Column('registration_id', db.Integer, db.ForeignKey('mhr_registrations.id'), nullable=False,
                                index=True)
    change_registration_id = db.Column('change_registration_id', db.Integer, nullable=False, index=True)
    tenancy_type = db.Column('tenancy_type', PG_ENUM(MhrTenancyTypes),
                             db.ForeignKey('mhr_tenancy_types.tenancy_type'), nullable=False)
    status_type = db.Column('status_type', PG_ENUM(MhrOwnerStatusTypes),
                            db.ForeignKey('mhr_owner_status_types.status_type'), nullable=False)

    # Relationships - MhrRegistration
    registration = db.relationship('MhrRegistration', foreign_keys=[registration_id],
                                   back_populates='owner_groups', cascade='all, delete', uselist=False)
    owners = db.relationship('MhrParty', order_by='asc(MhrParty.id)', back_populates='owner_group')

    modified: bool = False

    @property
    def json(self) -> dict:
        """Return the owner group as a json object."""
        group = {
            'groupId': self.group_id,
            'type': self.tenancy_type,
            'status': self.status_type,
            'tenancySpecified': True
        }
        # Add owners here
        owners = []
        for owner in self.owners:
            owner_json = owner.json
            owner_json['type'] = self.tenancy_type
            owners.append(owner_json)
        group['owners'] = owners
        if self.tenancy_specified == 'N':
            group['tenancySpecified'] = False
        if self.interest:
            group['interest'] = self.interest
        if self.interest_numerator and self.interest_numerator > 0:
            group['interestNumerator'] = self.interest_numerator
        if self.interest_denominator and self.interest_denominator > 0:
            group['interestDenominator'] = self.interest_denominator
        return group

    @classmethod
    def find_by_id(cls, pkey: int = None):
        """Return an owner group object by primary key."""
        group = None
        if pkey:
            try:
                group = cls.query.get(pkey)
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('MhrOwnerGroup.find_by_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        return group

    @classmethod
    def find_by_registration_id(cls, reg_id: int):
        """Return a list of owner group objects by registration id."""
        groups = None
        if reg_id:
            try:
                groups = cls.query.filter(MhrOwnerGroup.registration_id == reg_id).order_by(MhrOwnerGroup.id).all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('MhrOwnerGroup.find_by_registration_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        return groups

    @classmethod
    def find_by_change_registration_id(cls, reg_id: int):
        """Return a list of owner group objects by change registration id."""
        groups = None
        if reg_id:
            try:
                groups = cls.query.filter(MhrOwnerGroup.change_registration_id == reg_id)\
                                  .order_by(MhrOwnerGroup.id).all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('MhrOwnerGroup.find_by_change_reg_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        return groups

    @staticmethod
    def create_from_json(reg_json, registration_id: int):
        """Create a new owner group object from a new MH registration."""
        group: MhrOwnerGroup = MhrOwnerGroup(registration_id=registration_id,
                                             group_id=reg_json.get('groupId'),
                                             status_type=MhrOwnerStatusTypes.ACTIVE,
                                             tenancy_type=reg_json.get('type'),
                                             tenancy_specified='Y')
        group.change_registration_id = registration_id
        if reg_json.get('status'):
            group.status_type = reg_json['status']
        if group.tenancy_type != MhrTenancyTypes.SOLE:
            group.interest = reg_json.get('interest', None)
            group.interest_numerator = reg_json.get('interestNumerator', 0)
            group.interest_denominator = reg_json.get('interestDenominator', 0)
        if group.interest_numerator and group.interest_denominator:  # JOINT may have group interest; COMMON always.
            if not group.interest:
                group.interest = model_utils.OWNER_INTEREST_UNDIVIDED
            else:  # Tidy up interest description
                ratio: str = f'{group.interest_numerator}/{group.interest_denominator}'
                if group.interest.find(ratio) > -1:
                    group.interest = group.interest.replace(ratio, '').strip()
                if not group.interest:
                    group.interest = model_utils.OWNER_INTEREST_UNDIVIDED
        group.owners = []
        return group

    @staticmethod
    def create_from_change_json(reg_json, registration_id: int, change_registration_id: int, group_id: int):
        """Create a new owner group object from a change registration."""
        group: MhrOwnerGroup = MhrOwnerGroup(registration_id=registration_id,
                                             change_registration_id=change_registration_id,
                                             group_id=group_id,
                                             status_type=MhrOwnerStatusTypes.ACTIVE,
                                             tenancy_type=reg_json.get('type'),
                                             tenancy_specified='Y')
        if reg_json.get('status'):
            group.status_type = reg_json['status']
        if group.tenancy_type != MhrTenancyTypes.SOLE:
            group.interest = reg_json.get('interest', None)
            group.interest_numerator = reg_json.get('interestNumerator', 0)
            group.interest_denominator = reg_json.get('interestDenominator', 0)
        if group.interest_numerator and group.interest_denominator:  # JOINT may have group interest; COMMON always.
            if not group.interest:
                group.interest = model_utils.OWNER_INTEREST_UNDIVIDED
            else:  # Tidy up interest description
                ratio: str = f'{group.interest_numerator}/{group.interest_denominator}'
                if group.interest.find(ratio) > -1:
                    group.interest = group.interest.replace(ratio, '').strip()
                if not group.interest:
                    group.interest = model_utils.OWNER_INTEREST_UNDIVIDED
        # TBD: only applies to JOINT tenancy type with 2 or more executors:
        # if not reg_json.get('tenancySpecified'):
        #    group.tenancy_specified = 'N'
        group.owners = []
        group.modified = True
        return group
