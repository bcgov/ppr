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
import json

from flask import current_app
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from mhr_api.exceptions import BusinessException, DatabaseException, ResourceErrorCodes
from mhr_api.models import utils as model_utils, Db2Manuhome
from mhr_api.models.mhr_extra_registration import MhrExtraRegistration
from mhr_api.models.db2 import utils as legacy_utils

from .db import db
from .mhr_draft import MhrDraft
from .mhr_party import MhrParty
from .type_tables import MhrDocumentType, MhrRegistrationType, MhrRegistrationTypes, MhrRegistrationStatusTypes


QUERY_PKEYS = """
select nextval('mhr_registration_id_seq') AS reg_id,
       get_mhr_number() AS mhr_number,
       get_mhr_doc_reg_number() AS doc_reg_id,
       get_mhr_draft_number() AS draft_num,
       nextval('mhr_draft_id_seq') AS draft_id
"""
QUERY_PKEYS_NO_DRAFT = """
select nextval('mhr_registration_id_seq') AS reg_id,
       get_mhr_number() AS mhr_number,
       get_mhr_doc_reg_number() AS doc_reg_id
"""
FROM_LEGACY_DOC_TYPE = {
    '101': 'REG_101',
    '102': 'REG_102',
    '103': 'REG_103',
    '103E': 'REG_103E'
}
DOC_TYPE_REPORT_DESCRIPTION = {
    '101': 'Register New Unit',
    'CONV': 'Register New Unit',
    'DEFAULT': ''
}


class MhrRegistration(db.Model):  # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """This class manages all MHR registration model information."""

    __tablename__ = 'mhr_registrations'

    # Always use get_generated_values() to generate PK.
    id = db.Column('id', db.Integer, primary_key=True)
    registration_ts = db.Column('registration_ts', db.DateTime, nullable=False, index=True)
    mhr_number = db.Column('mhr_number', db.String(7), nullable=False, index=True,
                           default=db.func.get_mhr_number())
    account_id = db.Column('account_id', db.String(20), nullable=True, index=True)
    client_reference_id = db.Column('client_reference_id', db.String(50), nullable=True)
    pay_invoice_id = db.Column('pay_invoice_id', db.Integer, nullable=True)
    pay_path = db.Column('pay_path', db.String(256), nullable=True)
    user_id = db.Column('user_id', db.String(1000), nullable=True)

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

    draft_number: str = None
    doc_reg_number: str = None
    manuhome: Db2Manuhome = None
    mail_version: bool = False

    @property
    def json(self) -> dict:
        """Return the registration as a json object."""
        registration = {
            'mhrNumber': self.mhr_number,
            'createDateTime': model_utils.format_ts(self.registration_ts)
        }
        if self.client_reference_id:
            registration['clientReferenceId'] = self.client_reference_id

        # registration_id = self.id
        return self.__set_payment_json(registration)

    @property
    def registration_json(self) -> dict:
        """Return the search version of the registration as a json object."""
        if self.manuhome:
            reg_json = self.manuhome.registration_json
            # Inject note document type descriptions here.
            if reg_json and reg_json.get('notes'):
                for note in reg_json.get('notes'):
                    doc_desc = ''
                    doc_type = note.get('documentType', '')
                    if FROM_LEGACY_DOC_TYPE.get(doc_type):
                        doc_type = FROM_LEGACY_DOC_TYPE.get(doc_type)
                    doc_type_info: MhrDocumentType = MhrDocumentType.find_by_doc_type(doc_type)
                    if doc_type_info:
                        doc_desc = doc_type_info.document_type_desc
                    note['documentDescription'] = doc_desc
            return reg_json
        return self.json

    @property
    def new_registration_json(self) -> dict:
        """Return the new registration version of the registration as a json object."""
        if self.manuhome:
            reg_json = self.manuhome.new_registration_json
            if self.mail_version and self.manuhome.reg_documents:
                reg_doc = None
                for doc in self.manuhome.reg_documents:
                    if self.manuhome.reg_document_id and self.manuhome.reg_document_id == doc.id:
                        reg_doc = doc
                if reg_doc:
                    reg_json['documentRegistrationId'] = reg_doc.document_reg_id
                    doc_type = reg_doc.document_type
                    if doc_type in DOC_TYPE_REPORT_DESCRIPTION:
                        reg_json['documentDescription'] = DOC_TYPE_REPORT_DESCRIPTION[doc_type]
                    else:
                        reg_json['documentDescription'] = ''
            return reg_json
        return self.json

    def __set_payment_json(self, registration):
        """Add registration payment info json if payment exists."""
        if self.pay_invoice_id and self.pay_path:
            payment = {
                'invoiceId': str(self.pay_invoice_id),
                'receipt': self.pay_path
            }
            registration['payment'] = payment
        return registration

    def save(self):
        """Render a registration to the local cache."""
        # Save draft first
        draft = self.draft
        db.session.add(draft)
        db.session.commit()

        self.draft_id = draft.id
        db.session.add(self)
        db.session.commit()

    def get_registration_type(self):
        """Lookup registration type record if it has not already been fetched."""
        if self.reg_type is None and self.registration_type:
            self.reg_type = db.session.query(MhrRegistrationType).\
                            filter(MhrRegistrationType.registration_type == self.registration_type).\
                            one_or_none()

    @classmethod
    def find_by_id(cls, registration_id: int, legacy: bool = False):
        """Return the registration matching the id."""
        registration = None
        if registration_id:
            if legacy:
                registration = MhrRegistration()
                registration.manuhome = legacy_utils.find_by_id(registration_id)
            else:
                registration = cls.query.get(registration_id)
        return registration

    @classmethod
    def find_summary_by_mhr_number(cls, account_id: str, mhr_number: str, staff: bool = False):
        """Return the MHR registration summary information matching the registration number."""
        formatted_mhr = model_utils.format_mhr_number(mhr_number)
        current_app.logger.debug(f'Account_id={account_id}, mhr_number={formatted_mhr}')
        if model_utils.is_legacy():
            return legacy_utils.find_summary_by_mhr_number(account_id, formatted_mhr, staff)

        raise DatabaseException('MhrRegistration.find_summary_by_mhr_number PosgreSQL not yet implemented.')

    @classmethod
    def find_all_by_account_id(cls, account_id: str, staff: bool = False):
        """Return a summary list of recent MHR registrations belonging to an account."""
        current_app.logger.debug(f'Account_id={account_id}')
        if model_utils.is_legacy():
            return legacy_utils.find_all_by_account_id(account_id, staff)

        raise DatabaseException('MhrRegistration.find_all_by_account_id PosgreSQL not yet implemented.')

    @classmethod
    def get_doc_id_count(cls, doc_id):
        """Execute a query to count existing document id (must not exist check)."""
        current_app.logger.debug(f'document id={doc_id}')
        if model_utils.is_legacy():
            return legacy_utils.get_doc_id_count(doc_id)

        raise DatabaseException('MhrRegistration.get_doc_id_count PosgreSQL not yet implemented.')

    @classmethod
    def find_by_mhr_number(cls, mhr_number: str, account_id: str, staff: bool = False):
        """Return the registration matching the MHR number."""
        current_app.logger.debug(f'Account={account_id}, mhr_number={mhr_number}')
        registration = None
        formatted_mhr = model_utils.format_mhr_number(mhr_number)
        if formatted_mhr:
            try:
                registration = cls.query.filter(MhrRegistration.mhr_number == formatted_mhr).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB find_by_mhr_number exception: ' + str(db_exception))
                raise DatabaseException(db_exception)

        if not registration:
            raise BusinessException(
                error=model_utils.ERR_MHR_REGISTRATION_NOT_FOUND.format(code=ResourceErrorCodes.NOT_FOUND_ERR,
                                                                        mhr_number=formatted_mhr),
                status_code=HTTPStatus.NOT_FOUND
            )

        if not staff and account_id and registration.account_id != account_id:
            # Check extra registrations
            extra_reg = MhrExtraRegistration.find_by_mhr_number(formatted_mhr, account_id)
            if not extra_reg:
                raise BusinessException(
                    error=model_utils.ERR_REGISTRATION_ACCOUNT.format(code=ResourceErrorCodes.UNAUTHORIZED_ERR,
                                                                      account_id=account_id,
                                                                      mhr_number=formatted_mhr),
                    status_code=HTTPStatus.UNAUTHORIZED
                )
        # Authorized, exists. If legacy transition load legacy data.
        if model_utils.is_legacy():
            registration.manuhome = legacy_utils.find_by_mhr_number(formatted_mhr)
        return registration

    @staticmethod
    def create_new_from_json(json_data, account_id: str = None, user_id: str = None):
        """Create a new registration object from dict/json."""
        # Create or update draft.
        draft = MhrRegistration.find_draft(json_data)
        reg_vals: MhrRegistration = MhrRegistration.get_generated_values(draft)
        registration: MhrRegistration = MhrRegistration()
        registration.id = reg_vals.id  # pylint: disable=invalid-name; allow name of id.
        registration.mhr_number = reg_vals.mhr_number
        registration.doc_reg_number = reg_vals.doc_reg_number
        registration.registration_ts = model_utils.now_ts()
        registration.registration_type = MhrRegistrationTypes.MHREG
        registration.status_type = MhrRegistrationStatusTypes.ACTIVE
        registration.account_id = account_id
        registration.user_id = user_id
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
        return registration

    @staticmethod
    def find_draft(json_data, registration_type: str = None):
        """Try to find an existing draft if a draftNumber is in json_data.).

        Return None if not found or no documentId.
        """
        draft = None
        if json_data.get('draftNumber'):
            try:
                draft_number = json_data['draftNumber'].strip()
                if draft_number != '':
                    draft: MhrDraft = MhrDraft.find_by_draft_number(draft_number, False)
                    if draft:
                        draft.draft = json.dumps(json_data)
                        if registration_type:
                            draft.registration_type = registration_type
            except BusinessException:
                draft = None
        return draft

    @staticmethod
    def get_generated_values(draft):
        """Get db generated identifiers that are in more than one table.

        Get registration_id, mhr_number, and optionally draft_number.
        """
        registration = MhrRegistration()
        # generate reg id, MHR number. If not existing draft also generate draft number
        query = QUERY_PKEYS
        if draft:
            query = QUERY_PKEYS_NO_DRAFT
        result = db.session.execute(query)
        row = result.first()
        registration.id = int(row[0])
        registration.mhr_number = str(row[1])
        registration.doc_reg_number = str(row[2])
        if not draft:
            registration.draft_number = str(row[3])
            registration.draft_id = int(row[4])
        return registration
