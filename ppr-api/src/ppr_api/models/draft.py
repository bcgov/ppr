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
"""This module holds model data and database operations for draft statements."""
from __future__ import annotations

from enum import Enum
from http import HTTPStatus

#from sqlalchemy import event

from .db import db
#from .registration import Registration  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship

from ppr_api.exceptions import BusinessException
from ppr_api.utils.datetime import format_ts, now_ts

import json
import datetime


class Draft(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains draft statement information."""

    class DraftTypes(Enum):
        """Render an Enum of the draft types."""

        AMENDMENT_DRAFT = 'AMD'
        CHANGE_DRAFT = 'CHD'
        FINANCING_DRAFT = 'FSD'

    __versioned__ = {}
    __tablename__ = 'draft'

    draft_id = db.Column('draft_id', db.Integer, primary_key=True, server_default=db.FetchedValue())
    draft_type_cd = db.Column('draft_type_cd', db.String(3), nullable=False) #, db.ForeignKey('draft_type.draft_type_cd'))
    document_id = db.Column('document_id', db.String(20), nullable=False, default=db.func.get_draft_document_id())
    account_id = db.Column('account_id', db.String(20), nullable=False)
    create_ts = db.Column('create_ts', db.DateTime, nullable=False)
    # Included for convenience when querying account drafts
    type_cd = db.Column('type_cd', db.String(3), nullable=False)
    draft = db.Column('draft', db.Text, nullable=False)
    # Included for convenience when querying account change and amendment drafts
    registration_num = db.Column('registration_num', db.String(3), nullable=True)
    update_ts = db.Column('update_ts', db.DateTime, nullable=True)

    # parent keys
    registration_id = db.Column('registration_id', db.Integer, 
                                db.ForeignKey('registration.registration_id'), nullable=True)

    # Relationships - Registration
    registration = db.relationship("Registration", foreign_keys=[registration_id], 
                               back_populates="draft", cascade='all, delete', uselist=False)



    @property
    def json(self) -> dict:
        """Return the financing statement as a json object."""

        draft = json.loads(self.draft)

        draft['createDateTime'] = format_ts(self.create_ts)

        if self.update_ts:
            draft['lastUpdateDateTime'] = format_ts(self.update_ts)

        if 'amendmentStatement' in draft and self.document_id:
            draft['amendmentStatement']['documentId'] = self.document_id
        elif 'changeStatement' in draft and self.document_id:
            draft['changeStatement']['documentId'] = self.document_id
        elif 'financingStatement' in draft and self.document_id:
            draft['financingStatement']['documentId'] = self.document_id

        return draft


    @classmethod
    def find_all_by_account_id(cls, account_id: str = None):
        """Return a summary list of drafts belonging to an account."""
        draft_list = None
        if account_id:
            draft_list = db.session.query(Draft.create_ts, Draft.draft_type_cd, Draft.document_id, 
                                   Draft.type_cd, Draft.registration_num). \
                            filter(Draft.account_id == account_id).order_by(Draft.draft_id).all()

        if not draft_list:
            raise BusinessException(
                error=f'No Draft Statements found for Account ID {account_id}.',
                status_code=HTTPStatus.NOT_FOUND
            )

        drafts_json = []
        for draft in draft_list:
            draft_json = {
                'createDateTime': format_ts(draft.create_ts),
                'documentId': draft.document_id,
                'registrationType': draft.type_cd,
                'path': '/api/v1/drafts/' + draft.document_id
            }            
            if draft.draft_type_cd == 'FSD':
                draft_json['type'] = 'FINANCING_STATEMENT'
            elif draft.draft_type_cd == 'AMD':
                draft_json['type'] = 'AMENDMENT_STATEMENT'
                draft_json['registrationType'] = draft.type_cd
                draft_json['baseRegistrationNumber'] = draft.registration_num
            else:
                draft_json['type'] = 'CHANGE_STATEMENT'
                draft_json['registrationType'] = draft.type_cd
                draft_json['baseRegistrationNumber'] = draft.registration_num

            drafts_json.append(draft_json)

        return drafts_json


    @classmethod
    def find_by_document_id(cls, document_id: str = None, allow_used: bool = False):
        """Return a draft statement by document ID."""
        draft = None
        if document_id:
            draft = cls.query.filter(Draft.document_id == document_id).one_or_none()

        if not draft:
            raise BusinessException(
                error=f'No Draft Statement found for Document ID {document_id}.',
                status_code=HTTPStatus.NOT_FOUND
            )

        if draft.registration_id and not allow_used:
            raise BusinessException(
                error=f'Draft Statement for Document ID {document_id} has been used.',
                status_code=HTTPStatus.BAD_REQUEST
            )

        return draft


    @classmethod
    def delete(cls, document_id: str = None):
        """Delete a draft statement by document ID."""
        draft = None
        if document_id:
            draft = cls.find_by_document_id(document_id, True)

        if draft:
            db.session.delete(draft)
            db.session.commit()

        return draft


    def save(self):
        """Save the object to the database immediately."""

        if not self.create_ts:
            self.create_ts = now_ts()

        db.session.add(self)
        db.session.commit()

        return self.json


#    @classmethod
#    def _save(cls, request_json, account_id: str = None):
#        """Save the object to the database immediately."""

#        draft = None
#        if request_json:
#            draft = copy.deepcopy(DRAFT_CHANGE_STATEMENT)

#        return draft


    @classmethod
    def update(cls, request_json, document_id: str = None, account_id: str = None):
        """Update an existing draft statement by document ID."""
        draft = None
        if request_json and document_id:
            draft = cls.find_by_document_id(document_id, False)

        if draft:
            draft.update_ts = now_ts()
            draft.draft = json.dumps(request_json)
            if request_json['type'] == 'AMENDMENT_STATEMENT':
                draft.type_cd = request_json['amendmentStatement']['changeType']
                draft.registration_num = request_json['amendmentStatement']['baseRegistrationNumber']
            elif request_json['type'] == 'CHANGE_STATEMENT':
                draft.type_cd = request_json['changeStatement']['changeType']
                draft.registration_num = request_json['changeStatement']['baseRegistrationNumber']
            else:
                draft.type_cd = request_json['financingStatement']['type']

        return draft


    @staticmethod
    def create_from_json(json_data, account_id:str):
        """Create a draft object from a json Draft schema object: map json to db."""
        draft = Draft()
        draft.account_id = account_id
        if json_data['type'] == 'AMENDMENT_STATEMENT':
            draft.draft_type_cd = 'AMD'
            draft.type_cd = json_data['amendmentStatement']['changeType']
            draft.registration_num = json_data['amendmentStatement']['baseRegistrationNumber']
        elif json_data['type'] == 'CHANGE_STATEMENT':
            draft.draft_type_cd = 'CHD'
            draft.type_cd = json_data['changeStatement']['changeType']
            draft.registration_num = json_data['changeStatement']['baseRegistrationNumber']
        else:
            draft.draft_type_cd = 'FSD'
            draft.type_cd = json_data['financingStatement']['type']

        draft.draft = json.dumps(json_data)

        return draft
