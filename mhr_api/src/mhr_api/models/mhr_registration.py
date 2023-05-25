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
"""This module holds common statement registration data."""
# pylint: disable=too-many-statements, too-many-branches

from http import HTTPStatus

from flask import current_app
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from mhr_api.exceptions import BusinessException, DatabaseException, ResourceErrorCodes
from mhr_api.models import utils as model_utils, Db2Manuhome
from mhr_api.models.mhr_extra_registration import MhrExtraRegistration
from mhr_api.models.db2 import utils as legacy_utils
import mhr_api.models.registration_utils as reg_utils

from .db import db
from .mhr_description import MhrDescription
from .mhr_document import MhrDocument
from .mhr_draft import MhrDraft
from .mhr_location import MhrLocation
from .mhr_note import MhrNote
from .mhr_owner_group import MhrOwnerGroup
from .mhr_party import MhrParty
from .mhr_section import MhrSection
from .type_tables import MhrDocumentType, MhrRegistrationType, MhrRegistrationTypes, MhrRegistrationStatusTypes
from .type_tables import MhrOwnerStatusTypes, MhrPartyTypes, MhrTenancyTypes, MhrNoteStatusTypes, MhrStatusTypes


REG_TO_DOC_TYPE = {
    'DECAL_REPLACE': 'REG_102',
    'EXEMPTION_NON_RES': 'EXNR',
    'EXEMPTION_RES': 'EXRS',
    'MHREG': 'REG_101',
    'PERMIT': 'REG_103',
    'PERMIT_EXTENSION': 'REG_103E',
    'TRAND': 'DEAT',
    'TRANS': 'TRAN',
    'TRANS_AFFIDAVIT': 'AFFE',
    'TRANS_ADMIN': 'LETA',
    'TRANS_WILL': 'WILL'
}


class MhrRegistration(db.Model):  # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """This class manages all MHR registration model information."""

    __tablename__ = 'mhr_registrations'

    # Always use get_generated_values() to generate PK.
    id = db.Column('id', db.Integer, primary_key=True)
    registration_ts = db.Column('registration_ts', db.DateTime, nullable=False, index=True)
    mhr_number = db.Column('mhr_number', db.String(7), nullable=False, index=True)
    account_id = db.Column('account_id', db.String(20), nullable=True, index=True)
    client_reference_id = db.Column('client_reference_id', db.String(50), nullable=True)
    pay_invoice_id = db.Column('pay_invoice_id', db.Integer, nullable=True)
    pay_path = db.Column('pay_path', db.String(256), nullable=True)
    user_id = db.Column('user_id', db.String(1000), nullable=True)
    doc_id = db.Column('document_id', db.String(10), nullable=True)

    # parent keys
    draft_id = db.Column('draft_id', db.Integer, db.ForeignKey('mhr_drafts.id'), nullable=False, index=True)
    registration_type = db.Column('registration_type', PG_ENUM(MhrRegistrationTypes),
                                  db.ForeignKey('mhr_registration_types.registration_type'), nullable=False)
    status_type = db.Column('status_type', PG_ENUM(MhrRegistrationStatusTypes),
                            db.ForeignKey('mhr_registration_status_types.status_type'), nullable=False)

    # relationships
    reg_type = db.relationship('MhrRegistrationType', foreign_keys=[registration_type],
                               back_populates='registration', cascade='all, delete', uselist=False)
    draft = db.relationship('MhrDraft', foreign_keys=[draft_id], uselist=False)
    parties = db.relationship('MhrParty', order_by='asc(MhrParty.id)', back_populates='registration')
    locations = db.relationship('MhrLocation', order_by='asc(MhrLocation.id)', back_populates='registration')
    documents = db.relationship('MhrDocument', order_by='asc(MhrDocument.id)', back_populates='registration')
    notes = db.relationship('MhrNote', order_by='asc(MhrNote.id)', back_populates='registration')
    owner_groups = db.relationship('MhrOwnerGroup', order_by='asc(MhrOwnerGroup.id)', back_populates='registration')
    descriptions = db.relationship('MhrDescription', order_by='asc(MhrDescription.id)', back_populates='registration')
    sections = db.relationship('MhrSection', order_by='asc(MhrSection.id)', back_populates='registration')

    draft_number: str = None
    doc_reg_number: str = None
    doc_pkey: int = None
    manuhome: Db2Manuhome = None
    mail_version: bool = False
    reg_json: dict = None
    current_view: bool = False
    change_registrations = []
    staff: bool = False
    report_view: bool = False

    @property
    def json(self) -> dict:
        """Return the current/composite view of the registration as a json object."""
        if self.id and self.id > 0:
            doc_json = self.documents[0].json
            reg_json = {
                'mhrNumber': self.mhr_number,
                'createDateTime': model_utils.format_ts(self.registration_ts),
                'registrationType': self.registration_type,
                'status': self.status_type,
                'declaredValue': doc_json.get('declaredValue', 0),
                'documentDescription': MhrRegistration.get_doc_desc(doc_json.get('documentType')),
                'documentId': doc_json.get('documentId'),
                'documentRegistrationNumber': doc_json.get('documentRegistrationNumber')
            }
            if self.client_reference_id:
                reg_json['clientReferenceId'] = self.client_reference_id
            if doc_json.get('attentionReference'):
                reg_json['attentionReference'] = doc_json.get('attentionReference')
            reg_json = self.set_submitting_json(reg_json)
            if self.registration_type in (MhrRegistrationTypes.PERMIT, MhrRegistrationTypes.PERMIT_EXTENSION):
                reg_json = self.set_location_json(reg_json, False)
                reg_json = self.set_note_json(reg_json, False)
            elif self.is_transfer():
                reg_json['transferDate'] = doc_json.get('transferDate')
                reg_json['consideration'] = doc_json.get('consideration')
                reg_json['ownLand'] = doc_json.get('ownLand')
                reg_json['affirmByName'] = doc_json.get('affirmByName')
                reg_json = self.set_transfer_group_json(reg_json)
            elif self.registration_type in (MhrRegistrationTypes.EXEMPTION_NON_RES, MhrRegistrationTypes.EXEMPTION_RES):
                reg_json = self.set_note_json(reg_json, False)
            elif self.registration_type == MhrRegistrationTypes.MHREG:
                reg_json['ownLand'] = doc_json.get('ownLand')
            current_app.logger.debug(f'Built registration JSON for type={self.registration_type}.')
            return self.set_payment_json(reg_json)

        if model_utils.is_legacy() and self.manuhome:
            return legacy_utils.get_registration_json(self)
        # Definition after data migration.
        registration = {
            'mhrNumber': self.mhr_number,
            'createDateTime': model_utils.format_ts(self.registration_ts)
        }
        if self.client_reference_id:
            registration['clientReferenceId'] = self.client_reference_id

        # registration_id = self.id
        return self.set_payment_json(registration)

    @property
    def registration_json(self) -> dict:
        """Return the search version of the registration as a json object."""
        if model_utils.is_legacy() and self.manuhome:
            return legacy_utils.get_search_json(self)
        return self.json

    @property
    def new_registration_json(self) -> dict:
        """Return the new registration version of the registration as a json object."""
        if self.id and self.id > 0 and (self.report_view or not model_utils.is_legacy()):
            doc_json = self.documents[0].json
            reg_json = {
                'mhrNumber': self.mhr_number,
                'createDateTime': model_utils.format_ts(self.registration_ts),
                'registrationType': self.registration_type,
                'status': self.status_type,
                'declaredValue': doc_json.get('declaredValue', 0),
                'documentDescription': MhrRegistration.get_doc_desc(doc_json.get('documentType')),
                'documentId': doc_json.get('documentId'),
                'documentRegistrationNumber': doc_json.get('documentRegistrationNumber'),
                'ownLand': doc_json.get('ownLand'),
                'affirmByName': doc_json.get('affirmByName')
            }
            if self.client_reference_id:
                reg_json['clientReferenceId'] = self.client_reference_id
            if doc_json.get('attentionReference'):
                reg_json['attentionReference'] = doc_json.get('attentionReference')
            reg_json = self.set_submitting_json(reg_json)
            reg_json = self.set_location_json(reg_json, self.current_view)
            reg_json = self.set_description_json(reg_json, self.current_view)
            reg_json = self.set_group_json(reg_json, self.current_view)
            current_app.logger.debug('Built new registration JSON')
            return self.set_payment_json(reg_json)

        if model_utils.is_legacy() and self.manuhome:
            return legacy_utils.get_new_registration_json(self)
        return self.json

    def set_payment_json(self, registration):
        """Add registration payment info json if payment exists."""
        if self.pay_invoice_id and self.pay_path:
            payment = {
                'invoiceId': str(self.pay_invoice_id),
                'receipt': self.pay_path
            }
            registration['payment'] = payment
        return registration

    def set_description_json(self, reg_json, current: bool) -> dict:
        """Build the description JSON conditional on current."""
        if reg_json and self.descriptions:
            description = None
            for existing in self.descriptions:
                if (current or self.current_view) and existing.status_type == MhrStatusTypes.ACTIVE:
                    description = existing
                    current_app.logger.debug('Using PostgreSQL current description json.')
                elif existing.registration_id == self.id:
                    description = existing
                    current_app.logger.debug('Using PostgreSQL registration description json.')
            if description:
                sections = []
                if self.sections:
                    for section in self.sections:
                        if (current or self.current_view) and section.status_type == MhrStatusTypes.ACTIVE:
                            sections.append(section.json)
                        elif section.registration_id == self.id:
                            sections.append(section.json)
                description_json = description.json
                description_json['sections'] = sections
                reg_json['description'] = description_json
        return reg_json

    def set_location_json(self, reg_json, current: bool) -> dict:
        """Build the location JSON conditional on current."""
        if reg_json and self.locations:
            location = None
            for existing in self.locations:
                if (current or self.current_view) and existing.status_type == MhrStatusTypes.ACTIVE:
                    location = existing
                    current_app.logger.debug('Using PostgreSQL current location in json.')
                elif existing.registration_id == self.id:
                    location = existing
                    current_app.logger.debug('Using PostgreSQL registration location in json.')
            if location:
                if reg_json.get('registrationType', '') in (MhrRegistrationTypes.PERMIT,
                                                            MhrRegistrationTypes.PERMIT_EXTENSION):
                    reg_json['newLocation'] = location.json
                else:
                    reg_json['location'] = location.json
        return reg_json

    def set_group_json(self, reg_json, current: bool) -> dict:
        """Build the owner group JSON conditional on current."""
        owner_groups = []
        if reg_json and self.owner_groups:
            for group in self.owner_groups:
                if (current or self.current_view) and group.status_type in (MhrOwnerStatusTypes.ACTIVE,
                                                                            MhrOwnerStatusTypes.EXEMPT):
                    owner_groups.append(group.json)
                elif group.registration_id == self.id:
                    owner_groups.append(group.json)
        reg_json['ownerGroups'] = owner_groups
        return reg_json

    def set_transfer_group_json(self, reg_json) -> dict:
        """Build the transfer registration owner groups JSON."""
        add_groups = []
        delete_groups = []
        if reg_json and self.owner_groups:
            for group in self.owner_groups:
                if group.registration_id == self.id:
                    add_groups.append(group.json)
                elif group.change_registration_id == self.id:
                    delete_groups.append(group.json)
        reg_json['addOwnerGroups'] = add_groups
        reg_json['deleteOwnerGroups'] = delete_groups
        return reg_json

    def set_submitting_json(self, reg_json) -> dict:
        """Build the submitting party JSON if available."""
        if reg_json and self.parties:
            submitting = self.parties[0]
            reg_json['submittingParty'] = submitting.json
        return reg_json

    def set_note_json(self, reg_json, current: bool) -> dict:
        """Build the note JSON conditional on current."""
        notes = []
        reg_note = {}
        if reg_json and self.notes:
            for note in self.notes:
                if (current or self.current_view) and note.status_type == MhrNoteStatusTypes.ACTIVE:
                    notes.append(note.json)
                elif note.registration_id == self.id:
                    reg_note = note.json
        if notes:
            reg_json['notes'] = notes
        else:
            reg_json['note'] = reg_note
        return reg_json

    def save(self):
        """Render a registration to the local cache."""
        db.session.add(self)
        # Now save legacy data.
        if model_utils.is_legacy():
            if not self.manuhome:
                manuhome: Db2Manuhome = Db2Manuhome.create_from_registration(self, self.reg_json)
                manuhome.save()
                self.manuhome = manuhome
            elif self.registration_type in (MhrRegistrationTypes.TRAND,
                                            MhrRegistrationTypes.TRANS,
                                            MhrRegistrationTypes.TRANS_ADMIN,
                                            MhrRegistrationTypes.TRANS_AFFIDAVIT,
                                            MhrRegistrationTypes.TRANS_WILL):
                self.manuhome = Db2Manuhome.create_from_transfer(self, self.reg_json)
                self.manuhome.save_transfer()
            elif self.registration_type in (MhrRegistrationTypes.EXEMPTION_RES, MhrRegistrationTypes.EXEMPTION_NON_RES):
                self.manuhome = Db2Manuhome.create_from_exemption(self, self.reg_json)
                self.manuhome.save_exemption()
            elif self.registration_type == MhrRegistrationTypes.PERMIT:
                self.manuhome = Db2Manuhome.create_from_permit(self, self.reg_json)
                self.manuhome.save_permit()
        db.session.commit()

    def save_exemption(self):
        """Set the state of the original MH registration to exempt."""
        # Save draft first
        self.status_type = MhrRegistrationStatusTypes.EXEMPT
        db.session.commit()

    def save_transfer(self, json_data, new_reg_id):
        """Update the original MH removed owner groups."""
        self.remove_groups(json_data, new_reg_id)
        db.session.commit()

    def save_permit(self, new_reg_id):
        """Update the existing location state to historical."""
        if self.locations and self.locations[0].status_type == MhrStatusTypes.ACTIVE:
            self.locations[0].status_type = MhrStatusTypes.HISTORICAL
            self.locations[0].change_registration_id = new_reg_id
        elif self.change_registrations:
            for reg in self.change_registrations:  # Updating a change registration location.
                for existing in reg.locations:
                    if existing.status_type == MhrStatusTypes.ACTIVE and existing.registration_id != new_reg_id:
                        existing.status_type = MhrStatusTypes.HISTORICAL
                        existing.change_registration_id = new_reg_id

    def get_registration_type(self):
        """Lookup registration type record if it has not already been fetched."""
        if self.reg_type is None and self.registration_type:
            self.reg_type = db.session.query(MhrRegistrationType).\
                            filter(MhrRegistrationType.registration_type == self.registration_type).\
                            one_or_none()

    def is_transfer(self) -> bool:
        """Determine if the registration is one of the transfer types."""
        return self.registration_type in (MhrRegistrationTypes.TRANS, MhrRegistrationTypes.TRAND,
                                          MhrRegistrationTypes.TRANS_ADMIN, MhrRegistrationTypes.TRANS_AFFIDAVIT,
                                          MhrRegistrationTypes.TRANS_WILL)

    @classmethod
    def find_by_id(cls, registration_id: int, legacy: bool = False, search: bool = False):
        """Return the registration matching the id."""
        registration = None
        if registration_id:
            registration = cls.query.get(registration_id)
            if legacy:
                if not registration:
                    current_app.logger.debug(f'No new registration found for id={registration_id}')
                    registration = MhrRegistration()
                registration.manuhome = legacy_utils.find_by_id(registration_id, search)
        return registration

    @classmethod
    def find_summary_by_mhr_number(cls, account_id: str, mhr_number: str, staff: bool = False):
        """Return the MHR registration summary information matching the MH registration number."""
        formatted_mhr = model_utils.format_mhr_number(mhr_number)
        current_app.logger.debug(f'Account_id={account_id}, mhr_number={formatted_mhr}')
        if model_utils.is_legacy():
            return legacy_utils.find_summary_by_mhr_number(account_id, formatted_mhr, staff)
        raise DatabaseException('MhrRegistration.find_summary_by_mhr_number PosgreSQL not yet implemented.')

    @classmethod
    def find_summary_by_doc_reg_number(cls, account_id: str, doc_reg_number: str, staff: bool = False):
        """Return the MHR registration summary information matching the document registration number."""
        formatted_reg_num = model_utils.format_doc_reg_number(doc_reg_number)
        current_app.logger.debug(f'Account_id={account_id}, doc_reg_number={formatted_reg_num}')
        if model_utils.is_legacy():
            return legacy_utils.find_summary_by_doc_reg_number(account_id, formatted_reg_num, staff)
        raise DatabaseException('MhrRegistration.find_summary_by_doc_reg_number PosgreSQL not yet implemented.')

    @classmethod
    def find_all_by_account_id(cls, params: reg_utils.AccountRegistrationParams):
        """Return a summary list of recent MHR registrations belonging to an account."""
        current_app.logger.debug(f'Account_id={params.account_id}')
        if model_utils.is_legacy():
            return legacy_utils.find_all_by_account_id(params)

        raise DatabaseException('MhrRegistration.find_all_by_account_id PosgreSQL not yet implemented.')

    @classmethod
    def get_doc_id_count(cls, doc_id):
        """Execute a query to count existing document id (must not exist check)."""
        current_app.logger.debug(f'document id={doc_id}')
        if model_utils.is_legacy():
            return legacy_utils.get_doc_id_count(doc_id)

        raise DatabaseException('MhrRegistration.get_doc_id_count PosgreSQL not yet implemented.')

    @classmethod
    def find_by_mhr_number(cls, mhr_number: str, account_id: str, staff: bool = False, reg_type=None):
        """Return the registration matching the MHR number."""
        current_app.logger.debug(f'Account={account_id}, mhr_number={mhr_number}')
        registration = None
        formatted_mhr = model_utils.format_mhr_number(mhr_number)
        registration_type = MhrRegistrationTypes.MHREG
        if reg_type and reg_type in MhrRegistrationTypes:
            registration_type = reg_type
        if formatted_mhr:
            try:
                registration = cls.query.filter(MhrRegistration.mhr_number == formatted_mhr,
                                                MhrRegistration.registration_type == registration_type).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB find_by_mhr_number exception: ' + str(db_exception))
                raise DatabaseException(db_exception)

        if not registration and not model_utils.is_legacy():
            raise BusinessException(
                error=model_utils.ERR_MHR_REGISTRATION_NOT_FOUND.format(code=ResourceErrorCodes.NOT_FOUND_ERR,
                                                                        mhr_number=formatted_mhr),
                status_code=HTTPStatus.NOT_FOUND
            )

        if not staff and account_id and (not registration or registration.account_id != account_id):
            # Check extra registrations
            extra_reg = MhrExtraRegistration.find_by_mhr_number(formatted_mhr, account_id)
            if not extra_reg:
                raise BusinessException(
                    error=model_utils.ERR_REGISTRATION_ACCOUNT.format(code=ResourceErrorCodes.UNAUTHORIZED_ERR,
                                                                      account_id=account_id,
                                                                      mhr_number=formatted_mhr),
                    status_code=HTTPStatus.UNAUTHORIZED
                )
        if registration and registration.documents:
            registration.doc_id = registration.documents[0].id
        # Authorized. If legacy transition load legacy data.
        if model_utils.is_legacy():
            if not registration:
                registration: MhrRegistration = MhrRegistration()
            registration.manuhome = legacy_utils.find_by_mhr_number(formatted_mhr)
            registration.mhr_number = registration.manuhome.mhr_number
        return registration

    @classmethod
    def find_all_by_mhr_number(cls, mhr_number: str, account_id: str, staff: bool = False):
        """Return the base registration matching the MHR number with the associated change registrations."""
        current_app.logger.debug(f'Account={account_id}, mhr_number={mhr_number}')
        base_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_number, account_id, staff)
        if not base_reg:
            return base_reg
        formatted_mhr = model_utils.format_mhr_number(mhr_number)
        reg_type = MhrRegistrationTypes.MHREG
        try:
            base_reg.change_registrations = cls.query.filter(MhrRegistration.mhr_number == formatted_mhr,
                                                             MhrRegistration.registration_type != reg_type).all()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB find_all_by_mhr_number exception: ' + str(db_exception))
            raise DatabaseException(db_exception)
        return base_reg

    @classmethod
    def find_original_by_mhr_number(cls, mhr_number: str, account_id: str, staff: bool = False):
        """Return the original MH registration information matching the MHR number."""
        current_app.logger.debug(f'Account={account_id}, mhr_number={mhr_number}')
        registration = None
        formatted_mhr = model_utils.format_mhr_number(mhr_number)
        if formatted_mhr:
            reg_type = MhrRegistrationTypes.MHREG
            try:
                registration = cls.query.filter(MhrRegistration.mhr_number == formatted_mhr,
                                                MhrRegistration.registration_type == reg_type).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB find_by_mhr_number exception: ' + str(db_exception))
                raise DatabaseException(db_exception)

        if not registration and not model_utils.is_legacy():
            raise BusinessException(
                error=model_utils.ERR_MHR_REGISTRATION_NOT_FOUND.format(code=ResourceErrorCodes.NOT_FOUND_ERR,
                                                                        mhr_number=formatted_mhr),
                status_code=HTTPStatus.NOT_FOUND
            )

        if not staff and account_id and (not registration or registration.account_id != account_id):
            # Check extra registrations
            extra_reg = MhrExtraRegistration.find_by_mhr_number(formatted_mhr, account_id)
            if not extra_reg:
                raise BusinessException(
                    error=model_utils.ERR_REGISTRATION_ACCOUNT.format(code=ResourceErrorCodes.UNAUTHORIZED_ERR,
                                                                      account_id=account_id,
                                                                      mhr_number=formatted_mhr),
                    status_code=HTTPStatus.UNAUTHORIZED
                )
        if registration and registration.documents:
            registration.doc_id = registration.documents[0].id
        # Authorized. If legacy transition load legacy data.
        if model_utils.is_legacy():
            if not registration:
                registration: MhrRegistration = MhrRegistration()
            registration.manuhome = legacy_utils.find_original_by_mhr_number(formatted_mhr)
            registration.mhr_number = registration.manuhome.mhr_number
        return registration

    @classmethod
    def find_by_document_id(cls, document_id: str, account_id: str, staff: bool = False):
        """Return the registration matching the MHR document ID."""
        current_app.logger.debug(f'Account={account_id}, document_id={document_id}')
        registration = None
        if document_id:
            try:
                registration = cls.query.filter(MhrRegistration.doc_id == document_id).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB find_by_document_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)

        if not registration and not model_utils.is_legacy():
            raise BusinessException(
                error=model_utils.ERR_DOCUMENT_NOT_FOUND_ID.format(code=ResourceErrorCodes.NOT_FOUND_ERR,
                                                                   document_id=document_id),
                status_code=HTTPStatus.NOT_FOUND
            )

        if not staff and account_id and registration and registration.account_id != account_id:
            # Check extra registrations
            extra_reg = MhrExtraRegistration.find_by_mhr_number(registration.mhr_number, account_id)
            if not extra_reg:
                raise BusinessException(
                    error=model_utils.ERR_REGISTRATION_ACCOUNT.format(code=ResourceErrorCodes.UNAUTHORIZED_ERR,
                                                                      account_id=account_id,
                                                                      mhr_number=registration.mhr_number),
                    status_code=HTTPStatus.UNAUTHORIZED
                )
        # Authorized, exists. If legacy transition load legacy data.
        if model_utils.is_legacy():
            if not registration:
                registration: MhrRegistration = MhrRegistration()
            registration.manuhome = legacy_utils.find_by_document_id(document_id)
            registration.mhr_number = registration.manuhome.mhr_number
        return registration

    @staticmethod
    def create_new_from_json(json_data, account_id: str = None, user_id: str = None, user_group: str = None):
        """Create a new registration object from dict/json."""
        # Create or update draft.
        draft = reg_utils.find_draft(json_data)
        reg_vals: MhrRegistration = reg_utils.get_generated_values(MhrRegistration(), draft, user_group)
        registration: MhrRegistration = MhrRegistration()
        registration.id = reg_vals.id  # pylint: disable=invalid-name; allow name of id.
        registration.mhr_number = reg_vals.mhr_number
        registration.doc_reg_number = reg_vals.doc_reg_number
        registration.doc_pkey = reg_vals.doc_pkey
        registration.registration_ts = model_utils.now_ts()
        registration.registration_type = MhrRegistrationTypes.MHREG
        registration.status_type = MhrRegistrationStatusTypes.ACTIVE
        registration.account_id = account_id
        registration.user_id = user_id
        if json_data.get('documentId'):
            registration.doc_id = json_data.get('documentId')
        else:
            registration.doc_id = reg_vals.doc_id
            json_data['documentId'] = registration.doc_id
        registration.reg_json = json_data
        if not draft:
            registration.draft_number = reg_vals.draft_number
            registration.draft_id = reg_vals.draft_id
            draft = MhrDraft.create_from_registration(registration, json_data)
        else:
            draft.draft = json_data
            registration.draft_id = draft.id
        registration.draft = draft

        if 'clientReferenceId' in json_data:
            registration.client_reference_id = json_data['clientReferenceId']

        registration.create_new_groups(json_data)
        # Other parties
        registration.parties = MhrParty.create_from_registration_json(json_data, registration.id)
        registration.locations = [MhrLocation.create_from_json(json_data['location'], registration.id)]
        doc: MhrDocument = MhrDocument.create_from_json(registration,
                                                        json_data,
                                                        REG_TO_DOC_TYPE[registration.registration_type])
        doc.registration_id = registration.id
        registration.documents = [doc]
        description: MhrDescription = MhrDescription.create_from_json(json_data.get('description'), registration.id)
        registration.descriptions = [description]
        registration.sections = MhrRegistration.get_sections(json_data, registration.id)
        return registration

    @staticmethod
    def create_change_from_json(base_reg,
                                json_data,
                                account_id: str = None,
                                user_id: str = None,
                                user_group: str = None):
        """Create common change registration objects from dict/json."""
        # Create or update draft.
        draft = reg_utils.find_draft(json_data)
        reg_vals: MhrRegistration = reg_utils.get_change_generated_values(MhrRegistration(), draft, user_group)
        registration: MhrRegistration = MhrRegistration()
        registration.id = reg_vals.id  # pylint: disable=invalid-name; allow name of id.
        registration.mhr_number = base_reg.mhr_number
        registration.doc_reg_number = reg_vals.doc_reg_number
        registration.doc_id = reg_vals.doc_id
        registration.doc_pkey = reg_vals.doc_pkey
        registration.registration_type = json_data.get('registrationType')
        registration.registration_ts = model_utils.now_ts()
        registration.status_type = MhrRegistrationStatusTypes.ACTIVE
        registration.account_id = account_id
        registration.user_id = user_id
        registration.reg_json = json_data
        if not draft:
            registration.draft_number = reg_vals.draft_number
            registration.draft_id = reg_vals.draft_id
            draft = MhrDraft.create_from_registration(registration, json_data)
        else:
            draft.draft = json_data
            registration.draft_id = draft.id
        registration.draft = draft
        if 'clientReferenceId' in json_data:
            registration.client_reference_id = json_data['clientReferenceId']
        registration.parties = MhrParty.create_from_registration_json(json_data, registration.id)
        json_data['documentId'] = registration.doc_id
        doc: MhrDocument = MhrDocument.create_from_json(registration,
                                                        json_data,
                                                        REG_TO_DOC_TYPE[registration.registration_type])
        doc.registration_id = base_reg.id
        registration.documents = [doc]
        return registration

    @staticmethod
    def create_transfer_from_json(base_reg,
                                  json_data,
                                  account_id: str = None,
                                  user_id: str = None,
                                  user_group: str = None):
        """Create transfer registration objects from dict/json."""
        if not json_data.get('registrationType'):
            json_data['registrationType'] = MhrRegistrationTypes.TRANS
        registration: MhrRegistration = MhrRegistration.create_change_from_json(base_reg,
                                                                                json_data,
                                                                                account_id,
                                                                                user_id,
                                                                                user_group)
        if base_reg.owner_groups:
            registration.add_new_groups(json_data, reg_utils.get_owner_group_count(base_reg))
        if base_reg:
            registration.manuhome = base_reg.manuhome
        return registration

    @staticmethod
    def create_exemption_from_json(base_reg,
                                   json_data,
                                   account_id: str = None,
                                   user_id: str = None,
                                   user_group: str = None):
        """Create exemption registration objects from dict/json."""
        if json_data.get('nonResidential'):
            json_data['registrationType'] = MhrRegistrationTypes.EXEMPTION_NON_RES
        else:
            json_data['registrationType'] = MhrRegistrationTypes.EXEMPTION_RES
        registration: MhrRegistration = MhrRegistration.create_change_from_json(base_reg,
                                                                                json_data,
                                                                                account_id,
                                                                                user_id,
                                                                                user_group)
        doc: MhrDocument = registration.documents[0]
        if json_data.get('note'):
            if base_reg and base_reg.manuhome and base_reg.manuhome.reg_notes:
                json_data['note']['noteId'] = len(base_reg.manuhome.reg_notes) + 1
            else:
                json_data['note']['noteId'] = 1
            registration.notes = [MhrNote.create_from_json(json_data.get('note'), base_reg.id, doc.id, registration.id)]
        if base_reg:
            registration.manuhome = base_reg.manuhome
        return registration

    @staticmethod
    def create_permit_from_json(base_reg,
                                json_data,
                                account_id: str = None,
                                user_id: str = None,
                                user_group: str = None):
        """Create transfer registration objects from dict/json."""
        json_data['registrationType'] = MhrRegistrationTypes.PERMIT
        registration: MhrRegistration = MhrRegistration.create_change_from_json(base_reg,
                                                                                json_data,
                                                                                account_id,
                                                                                user_id,
                                                                                user_group)
        doc: MhrDocument = registration.documents[0]
        # Save permit expiry date as a note.
        if base_reg and base_reg.manuhome and base_reg.manuhome.reg_notes:
            json_data['note'] = {
                'noteId': (len(base_reg.manuhome.reg_notes) + 1)
            }
        else:
            json_data['note'] = {
                'noteId': 1
            }
        note: MhrNote = MhrNote(registration_id=base_reg.id,
                                document_id=doc.id,
                                document_type=doc.document_type,
                                destroyed='N',
                                status_type=MhrNoteStatusTypes.ACTIVE,
                                remarks='',
                                change_registration_id=registration.id,
                                expiry_date=model_utils.today_ts_offset(30, True))
        registration.notes = [note]
        # New location
        registration.locations.append(MhrLocation.create_from_json(json_data.get('newLocation'), registration.id))
        if base_reg:
            registration.manuhome = base_reg.manuhome
        return registration

    def adjust_group_interest(self, new: bool):
        """For tenants in common groups adjust group interest to a common denominator."""
        tc_count: int = 0
        common_denominator: int = 0
        for group in self.owner_groups:
            if group.tenancy_type == MhrTenancyTypes.COMMON and \
                    group.status_type == MhrOwnerStatusTypes.ACTIVE:
                tc_count += 1
                if common_denominator == 0:
                    common_denominator = group.interest_denominator
                elif group.interest_denominator > common_denominator:
                    common_denominator = group.interest_denominator
        if tc_count > 0:
            for group in self.owner_groups:
                if new or (group.modified and group.status_type == MhrOwnerStatusTypes.ACTIVE):
                    num = group.interest_numerator
                    den = group.interest_denominator
                    if num > 0 and den > 0:
                        if den != common_denominator:
                            group.interest_denominator = common_denominator
                            group.interest_numerator = (common_denominator/den * num)

    def create_new_groups(self, json_data):
        """Create owner groups and owners for a new MH registration."""
        self.owner_groups = []
        sequence: int = 0
        for group_json in json_data.get('ownerGroups'):
            sequence += 1
            group: MhrOwnerGroup = MhrOwnerGroup.create_from_json(group_json, self.id)
            group.group_id = sequence
            # Add owners
            for owner_json in group_json.get('owners'):
                party_type = owner_json.get('partyType', None)
                if not party_type and owner_json.get('individualName'):
                    party_type = MhrPartyTypes.OWNER_IND
                elif not party_type:
                    party_type = MhrPartyTypes.OWNER_BUS
                group.owners.append(MhrParty.create_from_json(owner_json, party_type, self.id))
            self.owner_groups.append(group)
        # Update interest common denominator
        # self.adjust_group_interest(True)

    def add_new_groups(self, json_data, existing_count: int):
        """Create owner groups and owners for a change (transfer) registration."""
        self.owner_groups = []
        # Update owner groups: group ID increments with each change.
        group_id: int = existing_count + 1
        if json_data.get('addOwnerGroups'):
            for group_json in json_data.get('addOwnerGroups'):
                current_app.logger.info(f'Creating owner group id={group_id}')
                new_group: MhrOwnerGroup = MhrOwnerGroup.create_from_change_json(group_json, self.id, self.id,
                                                                                 group_id)
                group_id += 1
                # Add owners
                for owner_json in group_json.get('owners'):
                    party_type = owner_json.get('partyType', None)
                    if not party_type and owner_json.get('individualName'):
                        party_type = MhrPartyTypes.OWNER_IND
                    elif not party_type:
                        party_type = MhrPartyTypes.OWNER_BUS
                    new_group.owners.append(MhrParty.create_from_json(owner_json, party_type, self.id))
                current_app.logger.info(f'Creating owner group id={group_id} reg id={new_group.registration_id}')
                self.owner_groups.append(new_group)
            # self.adjust_group_interest(False)

    def remove_groups(self, json_data, new_reg_id):
        """Set change registration id for removed owner groups and owners for a transfer registration."""
        for group in json_data.get('deleteOwnerGroups'):  # pylint: disable=too-many-nested-blocks
            for existing in self.owner_groups:  # Updating a base registration owner group.
                if existing.group_id == group.get('groupId'):
                    existing.status_type = MhrOwnerStatusTypes.PREVIOUS
                    existing.change_registration_id = new_reg_id
                    existing.modified = True
                    current_app.logger.info(f'Removing base owner group id={existing.id}, reg id={self.id}')
                    for owner in existing.owners:
                        owner.status_type = MhrOwnerStatusTypes.PREVIOUS
                        owner.change_registration_id = new_reg_id
                        if reg_utils.is_transfer_due_to_death(json_data.get('registrationType')):
                            reg_utils.update_deceased(group.get('owners'), owner)
            for reg in self.change_registrations:  # Updating a change registration (previous transfer) group.
                for existing in reg.owner_groups:
                    if existing.group_id == group.get('groupId'):
                        existing.status_type = MhrOwnerStatusTypes.PREVIOUS
                        existing.change_registration_id = new_reg_id
                        existing.modified = True
                        current_app.logger.info(f'Removing base owner group id={existing.id}, reg id={self.id}')
                        for owner in existing.owners:
                            owner.status_type = MhrOwnerStatusTypes.PREVIOUS
                            owner.change_registration_id = new_reg_id
                            if reg_utils.is_transfer_due_to_death(json_data.get('registrationType')):
                                reg_utils.update_deceased(group.get('owners'), owner)

    @staticmethod
    def get_doc_desc(doc_type) -> str:
        """Try to find the document description by document type."""
        if doc_type:
            doc_type_info: MhrDocumentType = MhrDocumentType.find_by_doc_type(doc_type)
            if doc_type_info:
                return doc_type_info.document_type_desc
        return ''

    @staticmethod
    def get_sections(json_data, registration_id: int):
        """Build sections from the json_data."""
        sections = []
        if not json_data.get('description') or 'sections' not in json_data.get('description'):
            return sections
        for section in json_data['description']['sections']:
            sections.append(MhrSection.create_from_json(section, registration_id))
        return sections
