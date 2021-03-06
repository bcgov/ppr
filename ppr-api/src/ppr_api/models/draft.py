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
# pylint: disable=singleton-comparison


from __future__ import annotations

from enum import Enum
from http import HTTPStatus
import json

from ppr_api.exceptions import BusinessException
from ppr_api.models import utils as model_utils

from .db import db


class Draft(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains draft statement information."""

    class DraftTypes(Enum):
        """Render an Enum of the draft types."""

        REG_CLASS_AMEND = 'AMENDMENT'
        REG_CLASS_AMEND_COURT = 'COURTORDER'
        REG_CLASS_CHANGE = 'CHANGE'
        REG_CLASS_FINANCING = 'PPSALIEN'
        REG_CLASS_DISCHARGE = 'DISCHARGE'
        REG_CLASS_RENEWAL = 'RENEWAL'

    __tablename__ = 'draft'

#    draft_id = db.Column('draft_id', db.Integer, primary_key=True, server_default=db.FetchedValue())
    draft_id = db.Column('draft_id', db.Integer, db.Sequence('draft_id_seq'), primary_key=True)
    document_number = db.Column('document_number', db.String(10), nullable=False,
                                default=db.func.get_draft_document_number())
    account_id = db.Column('account_id', db.String(20), nullable=False)
    create_ts = db.Column('create_ts', db.DateTime, nullable=False)
    registration_type_cl = db.Column('registration_type_cl', db.String(10), nullable=False)
    registration_type_cd = db.Column('registration_type_cd', db.String(2), nullable=False)
    draft = db.Column('draft', db.Text, nullable=False)
    registration_number = db.Column('registration_number', db.String(10), nullable=False)
    update_ts = db.Column('update_ts', db.DateTime, nullable=True)

    # parent keys
    registration_id = db.Column('registration_id', db.Integer,
                                db.ForeignKey('registration.registration_id'), nullable=True)

    # Relationships - Registration
    registration = db.relationship('Registration', foreign_keys=[registration_id],
                                   back_populates='draft', uselist=False)

    @property
    def json(self) -> dict:
        """Return the draft as a json object."""
        draft = json.loads(self.draft)

        draft['createDateTime'] = model_utils.format_ts(self.create_ts)
        if self.update_ts:
            draft['lastUpdateDateTime'] = model_utils.format_ts(self.update_ts)
        if self.document_number:
            if self.registration_type_cl in (model_utils.REG_CLASS_AMEND, model_utils.REG_CLASS_AMEND_COURT):
                draft['amendmentStatement']['documentId'] = self.document_number
            elif self.registration_type_cl == model_utils.REG_CLASS_CHANGE:
                draft['changeStatement']['documentId'] = self.document_number
            elif self.registration_type_cl in (model_utils.REG_CLASS_FINANCING, model_utils.REG_CLASS_MISC):
                draft['financingStatement']['documentId'] = self.document_number

        return draft

    @classmethod
    def find_all_by_account_id(cls, account_id: str = None):
        """Return a summary list of drafts belonging to an account."""
        draft_list = None
        if account_id:
            draft_list = db.session.query(Draft.create_ts, Draft.registration_type_cl,
                                          Draft.registration_type_cd, Draft.document_number,
                                          Draft.registration_number). \
                            filter(Draft.account_id == account_id,
                                   Draft.registration_id == None).order_by(Draft.draft_id).all()  # noqa: E711

        drafts_json = []
        if not draft_list:
            return drafts_json
        #    raise BusinessException(
        #        error=f'No Draft Statements found for Account ID {account_id}.',
        #        status_code=HTTPStatus.NOT_FOUND
        #    )

        for draft in draft_list:
            draft_json = {
                'createDateTime': model_utils.format_ts(draft.create_ts),
                'documentId': draft.document_number,
                'registrationType': draft.registration_type_cd,
                'path': '/api/v1/drafts/' + draft.document_number
            }
            draft_json['type'] = model_utils.REG_CLASS_TO_DRAFT_TYPE[draft.registration_type_cl]
            if draft.registration_type_cl in (model_utils.REG_CLASS_AMEND,
                                              model_utils.REG_CLASS_AMEND_COURT,
                                              model_utils.REG_CLASS_CHANGE):
                draft_json['baseRegistrationNumber'] = draft.registration_number

            drafts_json.append(draft_json)

        return drafts_json

    @classmethod
    def find_by_document_number(cls, document_number: str = None, allow_used: bool = False):
        """Return a draft statement by document ID."""
        draft = None
        if document_number:
            draft = cls.query.filter(Draft.document_number == document_number).one_or_none()

        if not draft:
            raise BusinessException(
                error=f'No Draft Statement found for Document ID {document_number}.',
                status_code=HTTPStatus.NOT_FOUND
            )

        if draft.registration and not allow_used:
            raise BusinessException(
                error=f'Draft Statement for Document ID {document_number} has been used.',
                status_code=HTTPStatus.BAD_REQUEST
            )

        return draft

    @classmethod
    def delete(cls, document_number: str = None):
        """Delete a draft statement by document ID."""
        draft = None
        if document_number:
            draft = cls.find_by_document_number(document_number, True)

        if draft:
            db.session.delete(draft)
            db.session.commit()

        return draft

    def save(self):
        """Save the object to the database immediately."""
        if not self.create_ts:
            self.create_ts = model_utils.now_ts()

        db.session.add(self)
        db.session.commit()

        return self.json

    @classmethod
    def update(cls, request_json, document_number: str = None):
        """Update an existing draft statement by document number."""
        draft = None
        if request_json and document_number:
            draft = cls.find_by_document_number(document_number, False)

        if draft:
            draft.update_ts = model_utils.now_ts()
            draft.draft = json.dumps(request_json)
            if request_json['type'] == 'AMENDMENT_STATEMENT':
                if 'courtOrderInformation' in request_json:
                    draft.registration_type_cl = 'COURTORDER'
                else:
                    draft.registration_type_cl = 'AMENDMENT'

                draft.registration_type_cd = request_json['amendmentStatement']['changeType']
                draft.registration_number = request_json['amendmentStatement']['baseRegistrationNumber']
            elif request_json['type'] == 'CHANGE_STATEMENT':
                draft.registration_type_cl = 'CHANGE'
                draft.registration_type_cd = request_json['changeStatement']['changeType']
                draft.registration_number = request_json['changeStatement']['baseRegistrationNumber']
            else:
                draft.registration_type_cl = 'PPSALIEN'
                draft.registration_type_cd = request_json['financingStatement']['type']

        return draft

    @staticmethod
    def create_from_json(json_data, account_id: str):
        """Create a draft object from a json Draft schema object: map json to db."""
        draft = Draft()
        draft.account_id = account_id
        draft_type = json_data['type']
        draft.registration_type_cl = model_utils.DRAFT_TYPE_TO_REG_CLASS[draft_type]
        if 'amendmentStatement' in json_data and 'courtOrderInformation' in json_data['amendmentStatement']:
            draft.registration_type_cl = model_utils.REG_CLASS_AMEND_COURT
        if draft_type == model_utils.DRAFT_TYPE_AMENDMENT:
            draft.registration_type_cd = json_data['amendmentStatement']['changeType']
            draft.registration_number = json_data['amendmentStatement']['baseRegistrationNumber']
        elif draft_type == model_utils.DRAFT_TYPE_CHANGE:
            draft.registration_type_cd = json_data['changeStatement']['changeType']
            draft.registration_number = json_data['changeStatement']['baseRegistrationNumber']
        else:
            draft.registration_type_cd = json_data['financingStatement']['type']

        # Not null constraint: should be removed if staff can submit requests without an account id.
        if not account_id:
            draft.account_id = 'NA'

        draft.draft = json.dumps(json_data)

        return draft

    @staticmethod
    def create_from_registration(registration, json_data):
        """Create a draft object from a registration."""
        draft = Draft()
        draft.account_id = registration.account_id
        draft.create_ts = registration.registration_ts
        draft.registration_number = registration.registration_num
        draft.document_number = registration.document_number
        draft.registration_type_cl = registration.registration_type_cl
        draft.registration_type_cd = registration.registration_type_cd
        draft.draft = json.dumps(json_data)
        # Not null constraint: should be removed.
        if not draft.account_id:
            draft.account_id = 'NA'

        return draft
