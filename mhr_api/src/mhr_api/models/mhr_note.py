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
"""This module holds data for MHR notes."""

from flask import current_app
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from mhr_api.exceptions import DatabaseException
from mhr_api.models import utils as model_utils, MhrDocument

from .db import db
from .type_tables import MhrDocumentTypes, MhrNoteStatusTypes, MhrPartyTypes, MhrDocumentType


class MhrNote(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the MHR note information."""

    __tablename__ = 'mhr_notes'

    id = db.Column('id', db.Integer, db.Sequence('mhr_note_id_seq'), primary_key=True)
    remarks = db.Column('remarks', db.String(500), nullable=True)
    destroyed = db.Column('destroyed', db.String(1), nullable=True)
    expiry_date = db.Column('expiry_date', db.DateTime, nullable=True)
    effective_ts = db.Column('effective_ts', db.DateTime, nullable=False, index=True)

    # parent keys
    document_id = db.Column('document_id', db.Integer, db.ForeignKey('mhr_documents.id'), nullable=False,
                            index=True)
    registration_id = db.Column('registration_id', db.Integer, db.ForeignKey('mhr_registrations.id'), nullable=False,
                                index=True)
    change_registration_id = db.Column('change_registration_id', db.Integer, nullable=False, index=True)
    document_type = db.Column('document_type', PG_ENUM(MhrDocumentTypes),
                              db.ForeignKey('mhr_document_types.document_type'), nullable=False)
    status_type = db.Column('status_type', PG_ENUM(MhrNoteStatusTypes),
                            db.ForeignKey('mhr_note_status_types.status_type'), nullable=False)

    # Relationships - MhrRegistration
    registration = db.relationship('MhrRegistration', foreign_keys=[registration_id],
                                   back_populates='notes', cascade='all, delete', uselist=False)

    @property
    def json(self) -> dict:
        """Return the note as a json object."""
        note = {
            'documentId': str(self.document_id).rjust(8, '0'),
            'documentType': self.document_type,
            'status': self.status_type,
            'remarks': self.remarks if self.remarks is not None else '',
            'destroyed': False
        }
        if self.registration:
            note['createDateTime'] = model_utils.format_ts(self.registration.registration_ts)
        doc: MhrDocument = self.get_document()
        notice = self.get_giving_notice()
        doc_type: MhrDocumentType = MhrDocumentType.find_by_doc_type(self.document_type)
        if doc_type:
            note['documentDescription'] = doc_type.document_type_desc
        if doc:
            note['documentRegistrationNumber'] = model_utils.format_doc_reg_number(doc.document_registration_number)
            note['documentId'] = doc.document_id
        if self.effective_ts:
            note['effectiveDateTime'] = model_utils.format_ts(self.effective_ts)
        if notice:
            note['givingNoticeParty'] = notice.json
        if self.destroyed == 'Y':
            note['destroyed'] = True
        if self.expiry_date:
            note['expiryDateTime'] = model_utils.format_ts(self.expiry_date)
        return note

    def get_document(self) -> MhrDocument:
        """Return the document for the registration the note was created for."""
        if self.registration and self.registration.documents:
            for doc in self.registration.documents:
                if doc.registration_id == self.registration_id:
                    return doc
        return None

    def get_giving_notice(self):
        """Return the contact party for the registration the note was created for."""
        if self.registration and self.registration.parties:
            for party in self.registration.parties:
                if party.registration_id == self.registration_id and party.party_type == MhrPartyTypes.CONTACT:
                    return party
        return None

    @classmethod
    def find_by_id(cls, pkey: int = None):
        """Return a note object by primary key."""
        note = None
        if pkey:
            try:
                note = cls.query.get(pkey)
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('MhrNote.find_by_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        return note

    @classmethod
    def find_by_registration_id(cls, registration_id: int):
        """Return a note object by registration id."""
        notes = None
        if registration_id:
            try:
                notes = cls.query.filter(MhrNote.registration_id == registration_id).order_by(MhrNote.id).all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('MhrNote.find_by_registration_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        return notes

    @classmethod
    def find_by_document_id(cls, document_id: int):
        """Return the note matching the document id."""
        note = None
        if document_id:
            try:
                note = cls.query.filter(MhrNote.document_id == document_id).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('MhrNote.find_by_document_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        return note

    @classmethod
    def find_by_change_registration_id(cls, registration_id: int = None):
        """Return a list of note objects by change registration id."""
        notes = None
        if registration_id:
            try:
                notes = cls.query.filter(MhrNote.change_registration_id == registration_id).order_by(MhrNote.id).all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('MhrNote.find_by_change_registration_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        return notes

    @staticmethod
    def create_from_json(reg_json,
                         registration_id: int,
                         document_id: int,
                         registration_ts,
                         change_registration_id: int = None):
        """Create a new note object from a registration."""
        note = MhrNote(registration_id=registration_id,
                       document_id=document_id,
                       document_type=reg_json.get('documentType'),
                       destroyed='N',
                       status_type=MhrNoteStatusTypes.ACTIVE)
        if not change_registration_id:
            note.change_registration_id = registration_id
        else:
            note.change_registration_id = change_registration_id
        if reg_json.get('remarks'):
            note.remarks = reg_json['remarks']
        if reg_json.get('destroyed'):
            note.destroyed = 'Y'
        if reg_json.get('effectiveDateTime'):
            note.effective_ts = model_utils.ts_from_iso_format(reg_json['effectiveDateTime'])
        else:
            note.effective_ts = registration_ts
        if note.document_type == MhrDocumentTypes.CAU:  # Compute expiry date.
            note.expiry_date = model_utils.compute_caution_expiry(note.effective_ts, True)
        elif reg_json.get('expiryDateTime'):
            note.expiry_date = model_utils.expiry_datetime(reg_json['expiryDateTime'])
        return note
