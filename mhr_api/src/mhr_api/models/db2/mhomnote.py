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
"""This module holds data for legacy DB2 MHR note information."""

from flask import current_app

from mhr_api.exceptions import DatabaseException
from mhr_api.models import db, utils as model_utils, Db2Document
from mhr_api.utils.base import BaseEnum


class Db2Mhomnote(db.Model):
    """This class manages all of the legacy DB2 MHR note information."""

    class StatusTypes(BaseEnum):
        """Render an Enum of the legacy note status types."""

        ACTIVE = 'A'
        CANCELLED = 'C'
        EXPIRED = 'E'
        CORRECTED = 'F'

    __bind_key__ = 'db2'
    __tablename__ = 'mhomnote'

    manuhome_id = db.Column('MANHOMID', db.Integer, primary_key=True)
    note_id = db.Column('MHNOTEID', db.Integer, primary_key=True)
    note_number = db.Column('MHNOTENO', db.Integer, primary_key=True)
    reg_document_id = db.Column('REGDOCID', db.String(8), nullable=False)
    can_document_id = db.Column('CANDOCID', db.String(8), nullable=False)
    document_type = db.Column('DOCUTYPE', db.String(4), nullable=False)
    status = db.Column('STATUS', db.String(1), nullable=False)
    destroyed = db.Column('DESTROYD', db.String(1), nullable=False)
    expiry_date = db.Column('EXPIRYDA', db.Date, nullable=False)
    phone_number = db.Column('PHONE', db.String(10), nullable=False)
    name = db.Column('NAME', db.String(40), nullable=False)
    legacy_address = db.Column('ADDRESS', db.String(160), nullable=False)
    remarks = db.Column('REMARKS', db.String(420), nullable=False)

    document: Db2Document = None
    # parent keys

    # Relationships

    def save(self):
        """Save the object to the database immediately. Only used for unit testing."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('Db2Mhomnote.save exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    def strip(self):
        """Strip all string properties."""
        self.reg_document_id = self.reg_document_id.strip()
        self.can_document_id = self.can_document_id.strip()
        self.document_type = self.document_type.strip()
        self.phone_number = self.phone_number.strip()
        self.name = self.name.strip()
        self.legacy_address = self.legacy_address.strip()
        self.remarks = self.remarks.strip()

    @classmethod
    def find_by_manuhome_id(cls, manuhome_id: int):
        """Return the all notes matching the manuhome id."""
        notes = None
        if manuhome_id and manuhome_id > 0:
            try:
                notes = cls.query.filter(Db2Mhomnote.manuhome_id == manuhome_id).all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('Db2Mhomnote.find_by_manuhome_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if notes:
            for note in notes:
                note.strip()
                if note.reg_document_id:
                    note.document = Db2Document.find_by_doc_id(note.reg_document_id)
        return notes

    @classmethod
    def find_by_manuhome_id_active(cls, manuhome_id: int):
        """Return all active notes matching the manuhome id."""
        notes = None
        if manuhome_id and manuhome_id > 0:
            try:
                notes = cls.query.filter(Db2Mhomnote.manuhome_id == manuhome_id,
                                         Db2Mhomnote.status == 'A').all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('Db2Mhomnote.find_by_manuhome_id_active exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if notes:
            for note in notes:
                note.strip()
                if note.reg_document_id:
                    note.document = Db2Document.find_by_doc_id(note.reg_document_id)
        return notes

    @classmethod
    def find_by_document_id(cls, document_id: str):
        """Return the all notes matching the manuhome id."""
        notes = None
        if document_id:
            try:
                notes = cls.query.filter(Db2Mhomnote.reg_document_id == document_id).all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('Db2Mhomnote.find_by_document_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if notes:
            for note in notes:
                note.strip()
        return notes

    @property
    def json(self):
        """Return a dict of this object, with keys in JSON format."""
        note = {
            'documentType': self.document_type,
            'documentId': self.reg_document_id,
            'remarks': self.remarks,
            'destroyed': False
        }
        if self.expiry_date and self.expiry_date.isoformat() != '0001-01-01':
            note['expiryDate'] = model_utils.format_local_date(self.expiry_date)
        if self.destroyed and self.destroyed == 'Y':
            note['destroyed'] = True
        if self.document_type not in (Db2Document.DocumentTypes.RES_EXEMPTION,
                                      Db2Document.DocumentTypes.NON_RES_EXEMPTION):
            note['contactName'] = self.name
            note['contactAddress'] = model_utils.get_address_from_db2(self.legacy_address, '')
        return note

    @property
    def registration_json(self):
        """Return a search registration dict of this object, with keys in JSON format."""
        note = {
            'documentType': self.document_type,
            'documentId': self.reg_document_id,
            'remarks': self.remarks,
            'contactName': self.name,
            'contactAddress': model_utils.get_address_from_db2(self.legacy_address, '')
        }
        if self.expiry_date and self.expiry_date.isoformat() != '0001-01-01':
            note['expiryDate'] = model_utils.format_local_date(self.expiry_date)
        if self.document and self.document.registration_ts:
            current_app.logger.debug(f'Db2Mhomnote setting createDateTime for doc id {self.reg_document_id}.')
            note['createDateTime'] = model_utils.format_local_ts(self.document.registration_ts)
            # current_app.logger.debug('Db2Mhomnote.registration_ts createDateTime set.')
        return note

    @staticmethod
    def create_from_dict(new_info: dict):
        """Create a note object from dict/json."""
        note = Db2Mhomnote(status=new_info.get('status', ''),
                           reg_document_id=new_info.get('registrationDocumentId', ''),
                           can_document_id=new_info.get('canDocumentId', ''),
                           document_type=new_info.get('documentType', ''),
                           destroyed=new_info.get('destroyed', ''),
                           phone_number=new_info.get('phoneNumber', ''),
                           name=new_info.get('name', ''),
                           legacy_address=new_info.get('legacyAddress', ''),
                           remarks=new_info.get('remarks', ''))

        if new_info.get('expiryDate', None):
            date_val: str = str(new_info.get('expiryDate'))[0:10]
            note.expiry_date = model_utils.date_from_iso_format(date_val)
        return note

    @staticmethod
    def create_from_json(json_data):
        """Create a note object from a json note schema object: map json to db."""
        note = Db2Mhomnote.create_from_dict(json_data)

        return note

    @staticmethod
    def create_from_registration(json_data, document: Db2Document, manhomid: int):
        """Create a new registration note object."""
        note = Db2Mhomnote(manuhome_id=manhomid,
                           note_id=json_data.get('noteId', 1),
                           note_number=0,
                           status=Db2Mhomnote.StatusTypes.ACTIVE,
                           reg_document_id=document.id,
                           document_type=json_data.get('documentType', document.document_type),
                           destroyed='N',
                           phone_number=document.phone_number,
                           name=document.name,
                           legacy_address=document.legacy_address,
                           remarks=json_data.get('remarks', ''),
                           can_document_id='')

        if json_data.get('contactName'):
            note.name = str(json_data.get('contactName'))[0: 40]
        if json_data.get('contactAddress'):
            note.legacy_address = model_utils.to_db2_address(json_data.get('contactAddress'))
        if json_data.get('status'):
            note.status = json_data.get('status')
        if json_data.get('destroyed'):
            note.destroyed = 'Y'
        if json_data.get('expiryDate', None):
            date_val: str = str(json_data.get('expiryDate'))[0:10]
            note.expiry_date = model_utils.date_from_iso_format(date_val)
        else:
            note.expiry_date = model_utils.date_from_iso_format('0001-01-01')
        return note
