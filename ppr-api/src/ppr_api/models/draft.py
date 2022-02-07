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

from flask import current_app

from ppr_api.exceptions import BusinessException, ResourceErrorCodes, DatabaseException
from ppr_api.models import utils as model_utils
from ppr_api.models.registration_utils import AccountRegistrationParams

from .db import db


ACCOUNT_QUERY = """
SELECT d.create_ts, d.registration_type_cl, d.registration_type, d.document_number, d.registration_number
  FROM drafts d
 WHERE d.account_id = '?'
   AND NOT EXISTS (SELECT r.draft_id FROM registrations r WHERE r.draft_id = d.id)
"""

PARAM_TO_ORDER_BY = {
    'registrationNumber': 'document_number',
    'registrationType': 'registration_type',
    'registeringName': 'registering_name',
    'clientReferenceId': 'client_reference_id',
    'startDateTime': 'create_ts',
    'endDateTime': 'create_ts'
}


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

    __tablename__ = 'drafts'

    id = db.Column('id', db.Integer, db.Sequence('draft_id_seq'), primary_key=True)
    document_number = db.Column('document_number', db.String(10), nullable=False, unique=True,
                                default=db.func.get_draft_document_number())
    account_id = db.Column('account_id', db.String(20), nullable=False, index=True)
    create_ts = db.Column('create_ts', db.DateTime, nullable=False, index=True)
    draft = db.Column('draft', db.JSON, nullable=False)
    registration_number = db.Column('registration_number', db.String(10), nullable=True)
    update_ts = db.Column('update_ts', db.DateTime, nullable=True)
    user_id = db.Column('user_id', db.String(1000), nullable=True)

    # parent keys
    registration_type = db.Column('registration_type', db.String(2),
                                  db.ForeignKey('registration_types.registration_type'), nullable=False)
    registration_type_cl = db.Column('registration_type_cl', db.String(10),
                                     db.ForeignKey('registration_type_classes.registration_type_cl'), nullable=False)

    # Relationships - Registration
    registration = db.relationship('Registration', back_populates='draft', uselist=False)

    @property
    def json(self) -> dict:
        """Return the draft as a json object."""
        draft = self.draft

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
    def find_all_by_account_id(cls, account_id: str, params: AccountRegistrationParams):
        """Return a summary list of drafts belonging to an account."""
        drafts_json = []
        if not account_id:
            return drafts_json
        try:
            if params and params.from_ui:
                return Draft.find_all_by_account_id_filter(params)

            max_results_size = int(current_app.config.get('ACCOUNT_DRAFTS_MAX_RESULTS'))
            results = db.session.execute(model_utils.QUERY_ACCOUNT_DRAFTS,
                                         {'query_account': account_id, 'max_results_size': max_results_size})
            rows = results.fetchall()
            if rows is not None:
                for row in rows:
                    mapping = row._mapping  # pylint: disable=protected-access; follows documentation
                    drafts_json.append(Draft.__build_account_draft_result(mapping))
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB find_all_by_account_id exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

        return drafts_json

    @classmethod
    def find_all_by_account_id_filter(cls, params: AccountRegistrationParams):
        """Return a summary list of drafts belonging to an account applying filters."""
        drafts_json = []
        query = Draft.build_account_draft_query(params)
        # current_app.logger.info(query)
        query_params = Draft.build_account_draft_query_params(params)
        # current_app.logger.info(query_params)
        results = db.session.execute(query, query_params)
        rows = results.fetchall()
        if rows is not None:
            for row in rows:
                mapping = row._mapping  # pylint: disable=protected-access; follows documentation
                drafts_json.append(Draft.__build_account_draft_result(mapping))
        return drafts_json

    @staticmethod
    def __build_account_draft_result(mapping) -> dict:
        """Build a draft result from a query result set row."""
        registering_name = str(mapping['registering_name'])
        if not registering_name or registering_name == 'None':
            registering_name = ''
        ref_id = str(mapping['client_reference_id'])
        if not ref_id or ref_id == 'None':
            ref_id = ''
        draft_json = {
            'createDateTime': model_utils.format_ts(mapping['create_ts']),
            'documentId': str(mapping['document_number']),
            'baseRegistrationNumber': str(mapping['base_reg_num']),
            'registrationType': str(mapping['registration_type']),
            'registrationDescription': str(mapping['registration_desc']),
            'type': str(mapping['draft_type']),
            'lastUpdateDateTime': model_utils.format_ts(mapping['last_update_ts']),
            'path': '/ppr/api/v1/drafts/' + str(mapping['document_number']),
            'registeringParty': str(mapping['registering_party']),
            'securedParties': str(mapping['secured_party']),
            'registeringName': registering_name,
            'clientReferenceId': ref_id
        }
        return draft_json

    @classmethod
    def find_by_document_number(cls, document_number: str = None, allow_used: bool = False):
        """Return a draft statement by document ID."""
        draft = None
        if document_number:
            try:
                draft = cls.query.filter(Draft.document_number == document_number).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB find_by_document_number exception: ' + str(db_exception))
                raise DatabaseException(db_exception)

        if not draft:
            code = ResourceErrorCodes.NOT_FOUND_ERR
            message = model_utils.ERR_DRAFT_NOT_FOUND.format(code=code, document_number=document_number)
            raise BusinessException(
                error=message,
                status_code=HTTPStatus.NOT_FOUND
            )

        if draft.registration and not allow_used:
            code = ResourceErrorCodes.UNAUTHORIZED_ERR
            message = model_utils.ERR_DRAFT_USED.format(code=code, document_number=document_number)
            raise BusinessException(
                error=message,
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
            draft.draft = request_json
            if request_json['type'] == 'AMENDMENT_STATEMENT':
                if 'courtOrderInformation' in request_json:
                    draft.registration_type_cl = 'COURTORDER'
                else:
                    draft.registration_type_cl = 'AMENDMENT'

                draft.registration_type = request_json['amendmentStatement']['changeType']
                draft.registration_number = request_json['amendmentStatement']['baseRegistrationNumber']
            elif request_json['type'] == 'CHANGE_STATEMENT':
                draft.registration_type_cl = 'CHANGE'
                draft.registration_type = request_json['changeStatement']['changeType']
                draft.registration_number = request_json['changeStatement']['baseRegistrationNumber']
            else:
                draft.registration_type_cl = 'PPSALIEN'
                draft.registration_type = request_json['financingStatement']['type']

        return draft

    @staticmethod
    def create_from_json(json_data, account_id: str, user_id: str = None):
        """Create a draft object from a json Draft schema object: map json to db."""
        draft = Draft()
        draft.account_id = account_id
        draft.user_id = user_id
        draft_type = json_data['type']
        draft.registration_type_cl = model_utils.DRAFT_TYPE_TO_REG_CLASS[draft_type]
        if 'amendmentStatement' in json_data and 'courtOrderInformation' in json_data['amendmentStatement']:
            draft.registration_type_cl = model_utils.REG_CLASS_AMEND_COURT
        if draft_type == model_utils.DRAFT_TYPE_AMENDMENT:
            draft.registration_type = json_data['amendmentStatement']['changeType']
            draft.registration_number = json_data['amendmentStatement']['baseRegistrationNumber']
        elif draft_type == model_utils.DRAFT_TYPE_CHANGE:
            draft.registration_type = json_data['changeStatement']['changeType']
            draft.registration_number = json_data['changeStatement']['baseRegistrationNumber']
        else:
            draft.registration_type = json_data['financingStatement']['type']

        # Not null constraint: should be removed if staff can submit requests without an account id.
        if not account_id:
            draft.account_id = 'NA'

        draft.draft = json_data

        return draft

    @staticmethod
    def create_from_registration(registration, json_data, user_id: str = None):
        """Create a draft object from a registration."""
        draft = Draft()
        draft.account_id = registration.account_id
        draft.create_ts = registration.registration_ts
        draft.registration_number = registration.registration_num
        draft.document_number = registration.document_number
        draft.registration_type_cl = registration.registration_type_cl
        draft.registration_type = registration.registration_type
        draft.user_id = user_id
        draft.draft = json_data
        # Not null constraint: should be removed.
        if not draft.account_id:
            draft.account_id = 'NA'

        return draft

    @staticmethod
    def get_account_draft_query_order(params: AccountRegistrationParams) -> str:
        """Get the account drafts query order by clause from the provided parameters."""
        order_by: str = model_utils.QUERY_ACCOUNT_DRAFTS_DEFAULT_ORDER
        if not params.sort_criteria:
            return order_by
        if param_order_by := PARAM_TO_ORDER_BY.get(params.sort_criteria, None):
            sort_order = 'DESC'
            if params.sort_direction and params.sort_direction in ('asc', 'ascending', 'desc', 'descending'):
                sort_order = params.sort_direction
            order_by = ' ORDER BY ' + param_order_by + ' ' + sort_order
        return order_by

    @staticmethod
    def build_account_draft_query(params: AccountRegistrationParams) -> str:
        """Build the account drafts query from the provided parameters."""
        query: str = model_utils.QUERY_ACCOUNT_DRAFTS_FILTER
        if params.registration_number:
            query += model_utils.QUERY_ACCOUNT_DRAFTS_DOC_NUM_CLAUSE
        if params.registration_type:
            query += model_utils.QUERY_ACCOUNT_DRAFTS_REG_TYPE_CLAUSE
        if params.client_reference_id:
            query += model_utils.QUERY_ACCOUNT_DRAFTS_CLIENT_REF_CLAUSE
        if params.registering_name:
            query += model_utils.QUERY_ACCOUNT_DRAFTS_REG_NAME_CLAUSE
        if params.start_date_time and params.end_date_time:
            query += model_utils.QUERY_ACCOUNT_DRAFTS_DATE_CLAUSE
        query += Draft.get_account_draft_query_order(params)
        query += model_utils.QUERY_ACCOUNT_DRAFTS_LIMIT
        return query

    @staticmethod
    def build_account_draft_query_params(params: AccountRegistrationParams) -> dict:
        """Build the account drafts query runtime parameter set from the provided parameters."""
        max_results_size = int(model_utils.MAX_ACCOUNT_REGISTRATIONS_DEFAULT)
        query_params = {
            'query_account': params.account_id,
            'max_results_size': max_results_size
        }
        if params.registration_number:
            query_params['doc_num'] = params.registration_number
        if params.registration_type:
            query_params['registration_type'] = params.registration_type
        if params.client_reference_id:
            query_params['client_reference_id'] = params.client_reference_id
        if params.registering_name:
            query_params['registering_name'] = params.registering_name
        if params.start_date_time and params.end_date_time:
            start_ts: str = params.start_date_time.replace('T', ' ')
            end_ts: str = params.end_date_time.replace('T', ' ')
            query_params['start_date_time'] = start_ts
            query_params['end_date_time'] = end_ts
        return query_params
