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
"""This module holds data for legacy DB2 MHR manufauctured home base information."""
from enum import Enum
from http import HTTPStatus

from flask import current_app

from mhr_api.exceptions import BusinessException, DatabaseException, ResourceErrorCodes
from mhr_api.models import utils as model_utils
from mhr_api.models import db

from .descript import Db2Descript
from .document import Db2Document
from .location import Db2Location
from .mhomnote import Db2Mhomnote
from .owner import Db2Owner
from .owngroup import Db2Owngroup


LEGACY_STATUS_DESCRIPTION = {
    'R': 'ACTIVE',
    'E': 'EXEMPT',
    'D': 'DRAFT',
    'C': 'HISTORICAL'
}
DOCUMENT_TYPE_REG = '101'
DOCUMENT_TYPE_CONV = 'CONV'


class Db2Manuhome(db.Model):
    """This class manages all of the legacy DB2 MHR manufauctured home base information."""

    class StatusTypes(str, Enum):
        """Render an Enum of the MH status types."""

        CANCELLED = 'C'
        DRAFT = 'D'
        EXEMPT = 'E'
        REGISTERED = 'R'

    __bind_key__ = 'db2'
    __tablename__ = 'manuhome'

    id = db.Column('manhomid', db.Integer, primary_key=True)
    mhr_number = db.Column('mhregnum', db.String(6), nullable=False)
    mh_status = db.Column('mhstatus', db.String(1), nullable=False)
    reg_document_id = db.Column('regdocid', db.String(8), nullable=False)
    exempt_flag = db.Column('exemptfl', db.String(1), nullable=False)
    presold_decal = db.Column('presold', db.String(1), nullable=False)
    update_count = db.Column('updatect', db.Integer, nullable=False)
    update_id = db.Column('updateid', db.String(8), nullable=False)
    update_date = db.Column('updateda', db.Date, nullable=False)
    update_time = db.Column('updateti', db.Time, nullable=False)
    accession_number = db.Column('accnum', db.Integer, nullable=False)
    box_number = db.Column('boxnum', db.Integer, nullable=False)

    # parent keys

    # relationships

    reg_documents = []
    reg_owners = []
    reg_location = None
    reg_descript = None
    reg_notes = []
    reg_owner_groups = []
    current_view: bool = False

    def save(self):
        """Save the object to the database immediately."""
        try:
            db.session.add(self)
            db.session.commit()
            if self.reg_documents:
                doc: Db2Document = self.reg_documents[0]
                doc.save()
            if self.reg_location:
                self.reg_location.save()
            if self.reg_descript:
                self.reg_descript.save()
            if self.reg_owner_groups:
                for group in self.reg_owner_groups:
                    group.save()
            db.session.commit()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('Db2Manuhome.save exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    def save_transfer(self):
        """Save the object with transfer changes to the database immediately."""
        try:
            db.session.add(self)
            if self.reg_documents:
                index: int = len(self.reg_documents) - 1
                doc: Db2Document = self.reg_documents[index]
                doc.save()
            if self.reg_owner_groups:
                for group in self.reg_owner_groups:
                    if group.modified:
                        group.save()
            db.session.commit()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('Db2Manuhome.save_transfer exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    @classmethod
    def find_by_id(cls, id: int):
        """Return the mh matching the id."""
        manuhome = None
        if id and id > 0:
            try:
                current_app.logger.debug('Db2Manuhome.find_by_id query.')
                manuhome = cls.query.get(id)
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('Db2Manuhome.find_by_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if manuhome:
            current_app.logger.debug('Db2Manuhome.find_by_id Db2Document query.')
            documents = []
            doc = Db2Document.find_by_id(manuhome.reg_document_id)
            if doc:
                documents.append(doc)
            manuhome.reg_documents = documents
            current_app.logger.debug('Db2Manuhome.find_by_id Db2Owngroup query.')
            manuhome.reg_owner_groups = Db2Owngroup.find_all_by_manuhome_id(manuhome.id)
            # manuhome.reg_owners = Db2Owner.find_by_manuhome_id_registration(manuhome.id)
            current_app.logger.debug('Db2Manuhome.find_by_id Db2Descript query.')
            manuhome.reg_descript = Db2Descript.find_by_manuhome_id_active(manuhome.id)
            current_app.logger.debug('Db2Manuhome.find_by_id Db2Location query.')
            manuhome.reg_location = Db2Location.find_by_manuhome_id_active(manuhome.id)
            current_app.logger.debug('Db2Manuhome.find_by_id Db2Mhomnote query.')
            manuhome.reg_notes = Db2Mhomnote.find_by_manuhome_id_active(manuhome.id)
            current_app.logger.debug('Db2Manuhome.find_by_id completed.')
        return manuhome

    @classmethod
    def find_by_document_id(cls, document_id: str):
        """Return the mh information that matches the document id."""
        doc: Db2Document = None
        manuhome: Db2Manuhome = None
        if document_id:
            try:
                current_app.logger.debug(f'Db2Document.find_by_document_id Db2Document query id={document_id}.')
                doc = Db2Document.find_by_id(document_id)
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('Db2Manuhome.find_by_document_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)

        if not doc:
            raise BusinessException(
                error=model_utils.ERR_DOCUMENT_NOT_FOUND_ID.format(code=ResourceErrorCodes.NOT_FOUND_ERR,
                                                                   document_id=document_id),
                status_code=HTTPStatus.NOT_FOUND
            )

        current_app.logger.debug(f'Db2Manuhome.find_by_document_id Db2Manuhome query mhrNum={doc.mhr_number}.')
        manuhome = Db2Manuhome.find_by_mhr_number(doc.mhr_number, True, True)
        current_app.logger.debug('Db2Manuhome.find_by_id Db2Document query.')
        manuhome.reg_documents = [doc]
        # Document type specific from now on.
        if doc.document_type in (Db2Document.DocumentTypes.TRAND,
                                 Db2Document.DocumentTypes.TRANS):
            current_app.logger.debug('Db2Manuhome.find_by_document_id Db2Owngroup query.')
            all_groups = Db2Owngroup.find_all_by_manuhome_id(manuhome.id)
            manuhome.reg_owner_groups = []
            for group in all_groups:
                if group.can_document_id and group.can_document_id == document_id:
                    manuhome.reg_owner_groups.append(group)
                elif group.reg_document_id == document_id:
                    manuhome.reg_owner_groups.append(group)
        return manuhome

    @classmethod
    def find_by_mhr_number(cls, mhr_number: str, owner_groups: bool = True, just_manuhome: bool = False):
        """Return the MH registration matching the MHR number."""
        manuhome = None
        current_app.logger.debug(f'Db2Manuhome.find_by_mhr_number {mhr_number}.')
        if mhr_number:
            try:
                manuhome: Db2Manuhome = cls.query.filter(Db2Manuhome.mhr_number == mhr_number).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('Db2Manuhome.find_by_mhr_number exception: ' + str(db_exception))
                raise DatabaseException(db_exception)

        if not manuhome:
            raise BusinessException(
                error=model_utils.ERR_REGISTRATION_NOT_FOUND_MHR.format(code=ResourceErrorCodes.NOT_FOUND_ERR,
                                                                        mhr_number=mhr_number),
                status_code=HTTPStatus.NOT_FOUND
            )
        if just_manuhome:
            return manuhome
        current_app.logger.debug('Db2Manuhome.find_by_mhr_number Db2Document query.')
        manuhome.reg_documents = Db2Document.find_by_mhr_number(manuhome.mhr_number)
        if owner_groups:
            current_app.logger.debug('Db2Manuhome.find_by_mhr_number Db2Owngroup query.')
            manuhome.reg_owner_groups = Db2Owngroup.find_all_by_manuhome_id(manuhome.id)
        else:
            current_app.logger.debug('Db2Manuhome.find_by_mhr_number Db2Owner query.')
            manuhome.reg_owners = Db2Owner.find_by_manuhome_id_registration(manuhome.id)
        current_app.logger.debug('Db2Manuhome.find_by_mhr_number Db2Descript query.')
        manuhome.reg_descript = Db2Descript.find_by_manuhome_id_active(manuhome.id)
        current_app.logger.debug('Db2Manuhome.find_by_mhr_number Db2Location query.')
        manuhome.reg_location = Db2Location.find_by_manuhome_id_active(manuhome.id)
        current_app.logger.debug('Db2Manuhome.find_by_mhr_number Db2Mhomnote query.')
        manuhome.reg_notes = Db2Mhomnote.find_by_manuhome_id_active(manuhome.id)
        current_app.logger.debug('Db2Manuhome.find_by_mhr_number completed.')
        return manuhome

    @classmethod
    def find_original_by_mhr_number(cls, mhr_number: str):
        """Return the original MH registration information matching the MHR number."""
        manuhome = None
        current_app.logger.debug(f'Db2Manuhome.find_original_by_mhr_number {mhr_number}.')
        if mhr_number:
            try:
                manuhome: Db2Manuhome = cls.query.filter(Db2Manuhome.mhr_number == mhr_number).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('Db2Manuhome.find_original_by_mhr_number exception: ' + str(db_exception))
                raise DatabaseException(db_exception)

        if not manuhome:
            raise BusinessException(
                error=model_utils.ERR_REGISTRATION_NOT_FOUND_MHR.format(code=ResourceErrorCodes.NOT_FOUND_ERR,
                                                                        mhr_number=mhr_number),
                status_code=HTTPStatus.NOT_FOUND
            )
        current_app.logger.debug('Db2Manuhome.find_original_by_mhr_number Db2Document query.')
        manuhome.reg_documents = [Db2Document.find_by_id(manuhome.reg_document_id)]
        current_app.logger.debug('Db2Manuhome.find_original_by_mhr_number Db2Owngroup query.')
        manuhome.reg_owner_groups = Db2Owngroup.find_by_reg_doc_id(manuhome.id, manuhome.reg_document_id)
        current_app.logger.debug('Db2Manuhome.find_original_by_mhr_number Db2Descript query.')
        manuhome.reg_descript = Db2Descript.find_by_doc_id(manuhome.reg_document_id)
        current_app.logger.debug('Db2Manuhome.find_original_by_mhr_number Db2Location query.')
        manuhome.reg_location = Db2Location.find_by_doc_id(manuhome.reg_document_id)
        current_app.logger.debug('Db2Manuhome.find_original_by_mhr_number completed.')
        return manuhome

    @property
    def json(self):
        """Return a dict of this object representing only the registration changes, with keys in JSON format."""
        doc_index: int = len(self.reg_documents) - 1
        doc: Db2Document = self.reg_documents[doc_index]
        doc_id: int = doc.id
        doc_json = doc.registration_json
        man_home = {
            'mhrNumber': self.mhr_number,
            'status': LEGACY_STATUS_DESCRIPTION.get(self.mh_status),
            'documentId': doc_json.get('documentId', ''),
            'documentRegistrationNumber': doc_json.get('documentRegistrationNumber', ''),
            'documentType': doc_json.get('documentType', ''),
            'createDateTime': doc_json.get('createDateTime', ''),
            'clientReferenceId': doc_json.get('clientReferenceId', ''),
            'submittingParty': doc_json.get('submittingParty')
        }
        if doc_json.get('attentionReference'):
            man_home['attentionReference'] = doc_json.get('attentionReference')

        if doc.document_type in (Db2Document.DocumentTypes.TRANS, Db2Document.DocumentTypes.TRAND):
            add_groups = []
            delete_groups = []
            for group in self.reg_owner_groups:
                if group.can_document_id == doc_id:
                    delete_groups.append(group.registration_json)
                elif group.reg_document_id == doc_id:
                    add_groups.append(group.registration_json)
            man_home['addOwnerGroups'] = add_groups
            man_home['deleteOwnerGroups'] = delete_groups
            man_home['declaredValue'] = doc_json.get('declaredValue')
            man_home['consideration'] = doc_json.get('consideration')
            man_home['ownLand'] = doc_json.get('ownLand')
            man_home['affirmByName'] = doc_json.get('affirmByName')
            if doc_json.get('transferDate'):
                man_home['transferDate'] = doc_json.get('transferDate')
        else:
            if self.reg_owner_groups:
                groups = []
                for group in self.reg_owner_groups:
                    groups.append(group.registration_json)
                man_home['ownerGroups'] = groups
            if self.reg_location:
                man_home['location'] = self.reg_location.registration_json
            if self.reg_descript:
                man_home['description'] = self.reg_descript.registration_json
            if self.reg_notes:
                notes = []
                for note in self.reg_notes:
                    notes.append(note.registration_json)
                # Now sort in descending timestamp order.
                man_home['notes'] = Db2Manuhome.__sort_notes(notes)

        return man_home

    @property
    def registration_json(self):
        """Return a search dict of this object, with keys in JSON format."""
        man_home = {
            'mhrNumber': self.mhr_number,
            'status': self.mh_status
        }
        declared_value: int = 0
        declared_ts: str = None
        if self.reg_documents:
            for doc in self.reg_documents:
                if self.reg_document_id and self.reg_document_id == doc.id:
                    doc_json = doc.registration_json
                    man_home['documentId'] = doc_json.get('documentId', '')
                    man_home['createDateTime'] = doc_json.get('createDateTime', '')
                    man_home['clientReferenceId'] = doc_json.get('clientReferenceId', '')
                    man_home['attentionReference'] = doc_json.get('attentionReference', '')
                if doc.declared_value > 0 and declared_value == 0:
                    declared_value = doc.declared_value
                    declared_ts = doc.registration_ts
                elif doc.declared_value > 0 and doc.registration_ts and declared_ts and \
                        doc.registration_ts > declared_ts:
                    declared_value = doc.declared_value
                    declared_ts = doc.registration_ts

        man_home['declaredValue'] = declared_value
        if declared_ts:
            man_home['declaredDateTime'] = model_utils.format_local_ts(declared_ts)

        if self.reg_owner_groups:
            groups = []
            for group in self.reg_owner_groups:
                if group.status != Db2Owngroup.StatusTypes.PREVIOUS:
                    groups.append(group.registration_json)
            man_home['ownerGroups'] = groups
        if self.reg_location:
            man_home['location'] = self.reg_location.registration_json
        if self.reg_descript:
            man_home['description'] = self.reg_descript.registration_json
        if self.reg_notes:
            notes = []
            for note in self.reg_notes:
                notes.append(note.registration_json)
            # Now sort in descending timestamp order.
            man_home['notes'] = Db2Manuhome.__sort_notes(notes)
        return man_home

    @property
    def new_registration_json(self):
        """Return a new registration dict of this object, with keys in JSON format."""
        man_home = {
            'mhrNumber': self.mhr_number,
            'status': LEGACY_STATUS_DESCRIPTION.get(self.mh_status)
        }
        declared_value: int = 0
        declared_ts: str = None
        if self.reg_documents:
            for doc in self.reg_documents:
                if self.reg_document_id and self.reg_document_id == doc.id and \
                        doc.document_type.strip() in (DOCUMENT_TYPE_REG, DOCUMENT_TYPE_CONV):
                    doc_json = doc.registration_json
                    man_home['documentId'] = doc_json.get('documentId', '')
                    man_home['createDateTime'] = doc_json.get('createDateTime', '')
                    man_home['clientReferenceId'] = doc_json.get('clientReferenceId', '')
                    man_home['attentionReference'] = doc_json.get('attentionReference', '')
                if doc.declared_value > 0 and declared_value == 0:
                    declared_value = doc.declared_value
                    declared_ts = doc.registration_ts
                elif doc.declared_value > 0 and doc.registration_ts and declared_ts and \
                        doc.registration_ts > declared_ts:
                    declared_value = doc.declared_value
                    declared_ts = doc.registration_ts
        man_home['declaredValue'] = declared_value
        if declared_ts:
            man_home['declaredDateTime'] = model_utils.format_local_ts(declared_ts)

        if self.reg_owner_groups:
            groups = []
            for group in self.reg_owner_groups:
                if self.current_view and group.status == Db2Owngroup.StatusTypes.ACTIVE:
                    groups.append(group.registration_json)
                elif not self.current_view:
                    groups.append(group.registration_json)
            man_home['ownerGroups'] = groups
        if self.reg_location:
            man_home['location'] = self.reg_location.new_registration_json
        if self.reg_descript:
            man_home['description'] = self.reg_descript.registration_json
        return man_home

    @classmethod
    def __sort_notes(cls, notes):
        """Sort notes by registration timesamp."""
        notes.sort(key=Db2Manuhome.__sort_key_notes_ts, reverse=True)
        return notes

    @classmethod
    def __sort_key_notes_ts(cls, item):
        """Sort the notes registration timestamp."""
        return item.get('createDateTime', '')

    @staticmethod
    def create_from_dict(new_info: dict):
        """Create an manufactured home base object from dict/json."""
        manuhome = Db2Manuhome(mhr_number=new_info.get('mhrNumber'),
                               mh_status=new_info.get('status'),
                               reg_document_id=new_info.get('registrationDocumentId'),
                               exempt_flag=new_info.get('exemptFlag', ''),
                               presold_decal=new_info.get('presoldDecal', ''),
                               update_count=new_info.get('updateCount', 0),
                               update_id=new_info.get('updateId', ''),
                               accession_number=new_info.get('accessionNumber', ''),
                               box_number=new_info.get('boxNumber', ''))
        if new_info.get('updateDate', None):
            manuhome.update_date = model_utils.date_from_iso_format(new_info.get('updateDate'))
        if new_info.get('updateTime', None):
            manuhome.update_time = model_utils.time_from_iso_format(new_info.get('updateTime'))
        return manuhome

    @staticmethod
    def create_from_json(json_data):
        """Create a manufactured home base object from a json Manuhome schema object: map json to db."""
        manuhome = Db2Manuhome.create_from_dict(json_data)
        if manuhome.update_id:
            manuhome.update_id = manuhome.update_id.strip()

        return manuhome

    @staticmethod
    def create_from_registration(registration, reg_json):
        """Create a new manufactured home object from a new MH registration."""
        doc_id = reg_json.get('documentId', '')
        manuhome: Db2Manuhome = Db2Manuhome(id=registration.id,
                                            mhr_number=registration.mhr_number,
                                            mh_status=Db2Manuhome.StatusTypes.REGISTERED.value,
                                            reg_document_id=doc_id,
                                            exempt_flag='',
                                            presold_decal='',
                                            update_count=0,
                                            update_id='',
                                            accession_number=0,
                                            box_number=0)
        now_local = model_utils.today_local()
        manuhome.update_date = now_local.date()
        manuhome.update_time = now_local.time()
        manuhome.reg_documents = []
        manuhome.reg_owners = []
        manuhome.reg_location = None
        manuhome.reg_descript = None
        manuhome.reg_notes = []
        manuhome.reg_owner_groups = []

        # Create document if doc id
        if doc_id:
            manuhome.reg_documents.append(Db2Document.create_from_registration(registration,
                                                                               reg_json,
                                                                               Db2Document.DocumentTypes.MHREG,
                                                                               now_local))
        manuhome.reg_location = Db2Location.create_from_registration(registration, reg_json)
        # Adjust location address info.
        address = reg_json['location']['address']
        extra: str = ''
        if len(address.get('street')) > 31:
            extra = str(address['street'])[31:]
        if address.get('streetAdditional'):
            extra += ' ' + str(address.get('streetAdditional')).strip()
        manuhome.reg_location.additional_description = extra.strip() + ' ' + \
            manuhome.reg_location.additional_description
        if len(manuhome.reg_location.additional_description) > 80:
            manuhome.reg_location.additional_description = manuhome.reg_location.additional_description[0:80]
        manuhome.reg_descript = Db2Descript.create_from_registration(registration, reg_json)
        if reg_json.get('ownerGroups'):
            for i, new_group in enumerate(reg_json.get('ownerGroups')):
                new_group['documentId'] = reg_json.get('documentId')
                # current_app.logger.info('ownerGroups i=' + str(i))
                group = Db2Owngroup.create_from_registration(registration, new_group, (i + 1))
                manuhome.reg_owner_groups.append(group)
        return manuhome

    @staticmethod
    def create_from_transfer(registration, reg_json):
        """Create a new transfer registration: update manuhome, create document, update owner groups."""
        if not registration.manuhome:
            current_app.logger.info(f'registration id={registration.id} no manuhome: nothing to save.')
            return
        manuhome = registration.manuhome
        now_local = model_utils.today_local()
        manuhome.update_date = now_local.date()
        manuhome.update_time = now_local.time()
        doc_type = Db2Document.DocumentTypes.TRANS
        if reg_json.get('deathOfOwner'):
            doc_type = Db2Document.DocumentTypes.TRAND
        # Create document
        manuhome.reg_documents.append(Db2Document.create_from_registration(registration,
                                                                           reg_json,
                                                                           doc_type,
                                                                           now_local))
        # Update owner groups: group ID increments with each change.
        if reg_json.get('deleteOwnerGroups'):
            for group in reg_json.get('deleteOwnerGroups'):
                for existing in manuhome.reg_owner_groups:
                    if existing.group_id == group.get('groupId'):
                        current_app.logger.info(f'Existing group id={existing.group_id}, status={existing.status}')
                        existing.status = Db2Owngroup.StatusTypes.PREVIOUS
                        existing.modified = True
                        existing.can_document_id = reg_json.get('documentId')
                        current_app.logger.info(f'Found owner group to remove id={existing.group_id}')
        group_id: int = len(manuhome.reg_owner_groups) + 1
        if reg_json.get('addOwnerGroups'):
            reg_id = registration.id
            registration.id = manuhome.id  # Temporarily replace to save with original registration manhomid.
            for new_group in reg_json.get('addOwnerGroups'):
                current_app.logger.info(f'Creating owner group id={group_id}')
                new_group['documentId'] = reg_json.get('documentId')
                group = Db2Owngroup.create_from_registration(registration, new_group, group_id)
                group.modified = True
                group_id += 1
                manuhome.reg_owner_groups.append(group)
            registration.id = reg_id
        return manuhome
