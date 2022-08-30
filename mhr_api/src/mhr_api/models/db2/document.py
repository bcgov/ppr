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
"""This module holds data for legacy DB2 MHR document information."""

from flask import current_app

from mhr_api.exceptions import DatabaseException
from mhr_api.models import utils as model_utils
from mhr_api.models import db
from mhr_api.utils.base import BaseEnum


class Db2Document(db.Model):
    """This class manages all of the legacy DB2 MHR manufauctured home document information."""

    class DocumentTypes(BaseEnum):
        """Render an Enum of the legacy document types."""

        MHREG = '101 '

    __bind_key__ = 'db2'
    __tablename__ = 'document'

    id = db.Column('documtid', db.String(8), primary_key=True)
    mhr_number = db.Column('mhregnum', db.String(6), nullable=False)
    draft_ts = db.Column('drafdate', db.DateTime, nullable=False)
    registration_ts = db.Column('regidate', db.DateTime, nullable=False)
    document_type = db.Column('docutype', db.String(4), nullable=False)
    document_reg_id = db.Column('docuregi', db.String(8), nullable=False)
    interimed = db.Column('interimd', db.String(1), nullable=False)
    owner_cross_reference = db.Column('OWNRXREF', db.String(5), nullable=False)
    interest_denominator = db.Column('INTDENOM', db.Integer, nullable=False)
    declared_value = db.Column('DECVALUE', db.Integer, nullable=False)
    own_land = db.Column('ownland', db.String(1), nullable=False)
    routing_slip_number = db.Column('rslipnum', db.String(9), nullable=False)
    last_service = db.Column('lastserv', db.String(1), nullable=False)
    bcol_account = db.Column('BCOLACCT', db.String(6), nullable=False)
    dat_number = db.Column('DATNUMBR', db.String(8), nullable=False)
    examiner_id = db.Column('examinid', db.String(8), nullable=False)
    update_id = db.Column('updateid', db.String(8), nullable=False)
    phone_number = db.Column('phone', db.String(10), nullable=False)
    attention_reference = db.Column('ATTNREF', db.String(40), nullable=False)
    name = db.Column('name', db.String(40), nullable=False)
    legacy_address = db.Column('address', db.String(160), nullable=False)
    number_of_pages = db.Column('NUMPAGES', db.Integer, nullable=False)
    transfer_execution_date = db.Column('DATEOFEX', db.Date, nullable=False)
    consideration_value = db.Column('CONVALUE', db.String(80), nullable=False)
    affirm_by_name = db.Column('AFFIRMBY', db.String(40), nullable=False)
    liens_with_consent = db.Column('CONSENT', db.String(60), nullable=False)
    client_reference_id = db.Column('OLBCFOLI', db.String(30), nullable=False)

    # parent keys

    # Relationships

    def save(self):
        """Save the object to the database immediately."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('Db2Document.save exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    def strip(self):
        """Strip all string properties."""
        self.document_type = self.document_type.strip()
        self.document_reg_id = self.document_reg_id.strip()
        self.owner_cross_reference = self.owner_cross_reference.strip()
        self.routing_slip_number = self.routing_slip_number.strip()
        self.bcol_account = self.bcol_account.strip()
        self.dat_number = self.dat_number.strip()
        self.examiner_id = self.examiner_id.strip()
        self.update_id = self.update_id.strip()
        self.phone_number = self.phone_number.strip()
        self.attention_reference = self.attention_reference.strip()
        self.name = self.name.strip()
        self.legacy_address = self.legacy_address.strip()
        self.consideration_value = self.consideration_value.strip()
        self.affirm_by_name = self.affirm_by_name.strip()
        self.liens_with_consent = self.liens_with_consent.strip()
        self.client_reference_id = self.client_reference_id.strip()

    @classmethod
    def find_by_id(cls, doc_id: str):
        """Return the document matching the id."""
        document = None
        if doc_id:
            try:
                document = cls.query.get(doc_id)
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('Db2Document.find_by_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if document:
            document.strip()
        return document

    @classmethod
    def find_by_mhr_number(cls, mhr_number: str):
        """Return the document matching the MHR number."""
        documents = None
        if mhr_number:
            try:
                documents = cls.query.filter(Db2Document.mhr_number == mhr_number).all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('Db2Document.find_by_mhr_number exception: ' + str(db_exception))
                raise DatabaseException(db_exception)

        return documents

    @classmethod
    def find_by_doc_id(cls, document_id: str):
        """Return the document matching the document id."""
        document = None
        if document_id:
            try:
                document = cls.query.filter(Db2Document.id == document_id).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('Db2Document.find_by_doc_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)

        return document

    @property
    def json(self):
        """Return a dict of this object, with keys in JSON format."""
        # Response legacy data: allow for any column to be null.
        document = {
            'mhrNumber': self.mhr_number,
            'documentType': self.document_type,
            'documentRegistrationId': self.document_reg_id,
            'interimed': self.interimed,
            'ownerCrossReference': self.owner_cross_reference,
            'interestDenominator': self.interest_denominator,
            'declaredValue': self.declared_value,
            'ownLand': self.own_land,
            'routingSlipNumber': self.routing_slip_number,
            'lastService': self.last_service,
            'bcolAccount': self.bcol_account,
            'datNumber': self.dat_number,
            'examinerId': self.examiner_id,
            'updateId': self.update_id,
            'phoneNumber': self.phone_number,
            'attentionReference': self.attention_reference,
            'name': self.name,
            'legacyAddress': self.legacy_address,
            'numberOfPages': self.number_of_pages,
            'considerationValue': self.consideration_value,
            'affirmByName': self.affirm_by_name,
            'liensWithConsent': self.liens_with_consent,
            'clientReferenceId': self.client_reference_id
        }
        if self.draft_ts:
            document['draftDateTime'] = model_utils.format_ts(self.draft_ts)
        if self.registration_ts:
            document['createDateTime'] = model_utils.format_ts(self.registration_ts)
        if self.transfer_execution_date:
            document['transferExecutionDate'] = self.transfer_execution_date.isoformat()
        return document

    @property
    def registration_json(self):
        """Return a search registration dict of this object, with keys in JSON format."""
        # Response legacy data: allow for any column to be null.
        document = {
            'documentId': self.id,
            'documentRegistrationId': self.document_reg_id,
            'documentType': self.document_type,
            'mhrNumber': self.mhr_number,
            'declaredValue': self.declared_value,
            'attentionReference': self.attention_reference,
            'clientReferenceId': self.client_reference_id
        }
        if self.registration_ts:
            document['createDateTime'] = model_utils.format_ts(self.registration_ts)
        return document

    @staticmethod
    def create_from_dict(new_info: dict):
        """Create a document object from dict/json."""
        doc = Db2Document(mhr_number=new_info.get('mhrNumber'),
                          document_type=new_info.get('documentType'),
                          document_reg_id=new_info.get('documentRegistrationId'),
                          interimed=new_info.get('interimed', ''),
                          owner_cross_reference=new_info.get('ownerCrossReference', ''),
                          interest_denominator=new_info.get('interestDenominator', 0),
                          declared_value=new_info.get('declaredValue', 0),
                          own_land=new_info.get('ownLand', ''),
                          routing_slip_number=new_info.get('routingSlipNumber', ''))
        doc.last_service = new_info.get('lastService', '')
        doc.bcol_account = new_info.get('bcolAccount', '')
        doc.dat_number = new_info.get('datNumber', '')
        doc.examiner_id = new_info.get('examinerId', '')
        doc.update_id = new_info.get('updateId', '')
        doc.phone_number = new_info.get('phoneNumber', '')
        doc.attention_reference = new_info.get('attentionReference', '')
        doc.name = new_info.get('name', '')
        doc.legacy_address = new_info.get('legacyAddress', '')
        doc.number_of_pages = new_info.get('numberOfPages', 0)
        doc.consideration_value = new_info.get('considerationValue', '')
        doc.affirm_by_name = new_info.get('affirmByName', '')
        doc.liens_with_consent = new_info.get('liensWithConsent', '')
        doc.client_reference_id = new_info.get('clientReferenceId', '')
        if new_info.get('createDateTime', None):
            doc.registration_ts = model_utils.ts_from_iso_format(new_info.get('createDateTime'))
        if new_info.get('draftDateTime', None):
            doc.draft_ts = model_utils.ts_from_iso_format(new_info.get('draftDateTime'))
        if new_info.get('transferExecutionDate', None):
            doc.transfer_execution_date = model_utils.date_from_date_iso_format(new_info.get('transferExecutionDate'))
        return doc

    @staticmethod
    def create_from_json(json_data):
        """Create a document object from a json Document schema object: map json to db."""
        document = Db2Document.create_from_dict(json_data)
        if document.update_id:
            document.update_id = document.update_id.strip()

        return document

    @staticmethod
    def create_from_registration(registration, reg_json, doc_type: str, local_ts):
        """Create a new document object from a new MH registration."""
        doc_id = reg_json.get('documentId', '')
        doc = Db2Document(id=doc_id,
                          mhr_number=registration.mhr_number,
                          document_type=doc_type,
                          document_reg_id=registration.doc_reg_number,
                          registration_ts=local_ts,
                          draft_ts=local_ts,
                          interimed='',
                          owner_cross_reference='',
                          interest_denominator=0,
                          declared_value=0,
                          own_land='',
                          routing_slip_number='')
        doc.last_service = ''
        doc.bcol_account = ''
        doc.dat_number = ''
        doc.examiner_id = ''
        doc.update_id = ''
        doc.number_of_pages = 0
        doc.consideration_value = ''
        doc.affirm_by_name = ''
        doc.liens_with_consent = ''
        if reg_json.get('submittingParty'):
            submitting = reg_json.get('submittingParty')
            if submitting.get('phoneNumber'):
                doc.phone_number = str(submitting.get('phoneNumber'))[0:9]
            else:
                doc.phone_number = ''
            if submitting.get('businessName'):
                doc.name = str(submitting.get('businessName'))[0:39]
            else:
                ind_name: str = model_utils.to_db2_ind_name(submitting.get('personName'))
                doc.name = ind_name[0:39]
            doc.legacy_address = model_utils.to_db2_address(submitting.get('address'))
        else:
            doc.phone_number = ''
            doc.name = ''
            doc.legacy_address = ''
        if reg_json.get('attentionReference'):
            doc.attention_reference = str(reg_json['attentionReference'])[0:39]
        else:
            doc.attention_reference = ''
        if registration.client_reference_id:
            doc.client_reference_id = registration.client_reference_id[0:29]
        else:
            doc.client_reference_id = ''
        doc.transfer_execution_date = model_utils.date_from_iso_format('0001-01-01')
        return doc
