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
from enum import Enum

from flask import current_app

from mhr_api.exceptions import DatabaseException
from mhr_api.models import db


class Db2Owngroup(db.Model):
    """This class manages all of the legacy DB2 MHR owner group information."""

    class TenancyTypes(str, Enum):
        """Render an Enum of the owner group tenancy types."""

        SOLE = 'SO'
        JOINT = 'JT'
        COMMON = 'TC'

    class StatusTypes(str, Enum):
        """Render an Enum of the owner group status types."""

        ACTIVE = '3'
        PREVIOUS = '4'
        EXEMPT = '5'

    __bind_key__ = 'db2'
    __tablename__ = 'owngroup'

    manuhome_id = db.Column('MANHOMID', db.Integer, primary_key=True)
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

    def save(self):
        """Save the object to the database immediately. Only used for unit testing."""
        try:
            db.session.add(self)
            db.session.commit()
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
    def find_by_reg_doc_id(cls, manuhome_id: int, reg_document_id: str):
        """Return the owner group matching the manuhome id and registration document id."""
        owngroup = None
        if manuhome_id and manuhome_id > 0 and reg_document_id:
            try:
                owngroup = cls.query.filter(Db2Owngroup.manuhome_id == manuhome_id,
                                            Db2Owngroup.reg_document_id == reg_document_id).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2Owngroup.find_by_reg_doc_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if owngroup:
            owngroup.strip()
        return owngroup

    @property
    def json(self):
        """Return a dict of this object, with keys in JSON format."""
        owngroup = {
            'groupId': self.group_id,
            'copyId': self.copy_id,
            'sequenceNumber': self.sequence_number,
            'status': self.status,
            'pendingFlag': self.pending_flag,
            'registrationDocumentId': self.reg_document_id,
            'canDocumentId': self.can_document_id,
            'tenancyType': self.tenancy_type,
            'lessee': self.lessee,
            'lessor': self.lessor,
            'interest': self.interest,
            'interestNumerator': self.interest_numerator,
            'tenancySpecified': self.tenancy_specified
        }
        return owngroup

    @property
    def registration_json(self):
        """Return a search registration dict of this object, with keys in JSON format."""
        # Response legacy data: allow for any column to be null.
        owngroup = {
            'tenancyType': self.tenancy_type
        }
        return owngroup

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
                               tenancy_specified=new_info.get('tenancySpecified', ''))
        return owngroup

    @staticmethod
    def create_from_json(json_data):
        """Create a document object from a json document schema object: map json to db."""
        owngroup = Db2Owngroup.create_from_dict(json_data)

        return owngroup
