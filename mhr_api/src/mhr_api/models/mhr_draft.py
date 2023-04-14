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

from http import HTTPStatus

from flask import current_app
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from mhr_api.exceptions import BusinessException, ResourceErrorCodes, DatabaseException
from mhr_api.models import utils as model_utils
from mhr_api.models.type_tables import MhrRegistrationTypes

from .db import db


QUERY_ACCOUNT_DRAFTS_LIMIT = ' FETCH FIRST :max_results_size ROWS ONLY'
QUERY_ACCOUNT_DRAFTS_DEFAULT_ORDER = ' ORDER BY create_ts DESC'
QUERY_ACCOUNT_DRAFTS_BASE = """
SELECT d.draft_number, d.create_ts, d.registration_type, rt.registration_type_desc,
       d.draft ->> 'clientReferenceId' AS clientReferenceId,
       CASE WHEN d.update_ts IS NOT NULL THEN d.update_ts ELSE d.create_ts END last_update_ts,
       CASE WHEN d.draft -> 'submittingParty' IS NOT NULL THEN
            CASE WHEN d.draft -> 'submittingParty' -> 'businessName' IS NOT NULL THEN
                      d.draft -> 'submittingParty' ->> 'businessName'
                 WHEN d.draft -> 'submittingParty' ->> 'personName' IS NOT NULL THEN
                    concat(d.draft -> 'submittingParty' -> 'personName' ->> 'first', ' ',
                           d.draft -> 'submittingParty' -> 'personName' ->> 'last')
                 END
            ELSE '' END submitting_party,
       (SELECT CASE WHEN d.user_id IS NULL THEN ''
                    ELSE (SELECT u.firstname || ' ' || u.lastname
                            FROM users u
                           WHERE u.username = d.user_id FETCH FIRST 1 ROWS ONLY) END) AS registering_name,
       d.mhr_number,
       CASE WHEN d.registration_type = 'MHREG' or d.mhr_number IS NULL THEN 0
            ELSE (SELECT COUNT(r.id)
                    FROM mhr_registrations r
                   WHERE r.mhr_number = d.mhr_number
                     AND r.registration_ts > d.create_ts)
            END stale_count
  FROM mhr_drafts d, mhr_registration_types rt
 WHERE d.account_id = :query_account
   AND d.registration_type = rt.registration_type
   AND NOT EXISTS (SELECT r.draft_id FROM mhr_registrations r WHERE r.draft_id = d.id)
   AND NOT EXISTS (SELECT mer.id
                     FROM mhr_extra_registrations mer
                    WHERE mer.mhr_number = d.mhr_number
                      AND mer.account_id = d.account_id
                      AND mer.removed_ind IS NOT NULL AND mer.removed_ind = 'Y')
"""
QUERY_DRAFT_STALE_COUNT = """
SELECT COUNT(r.id)
  FROM mhr_registrations r
 WHERE r.mhr_number = :query_value1
   AND r.registration_ts > :query_value2
"""

QUERY_ACCOUNT_DRAFTS = QUERY_ACCOUNT_DRAFTS_BASE + QUERY_ACCOUNT_DRAFTS_DEFAULT_ORDER + QUERY_ACCOUNT_DRAFTS_LIMIT

PARAM_TO_ORDER_BY = {
    'draftNumber': 'draft_number',
    'registrationType': 'registration_type',
    'registeringName': 'registering_name',
    'clientReferenceId': 'client_reference_id',
    'startDateTime': 'create_ts',
    'endDateTime': 'create_ts'
}


class MhrDraft(db.Model):
    """This class maintains draft statement information."""

    __tablename__ = 'mhr_drafts'

    id = db.Column('id', db.Integer, db.Sequence('mhr_draft_id_seq'), primary_key=True)
    draft_number = db.Column('draft_number', db.String(10), nullable=False, unique=True,
                             default=db.func.get_mhr_draft_number())
    account_id = db.Column('account_id', db.String(20), nullable=False, index=True)
    create_ts = db.Column('create_ts', db.DateTime, nullable=False, index=True)
    draft = db.Column('draft', db.JSON, nullable=False)
    mhr_number = db.Column('mhr_number', db.String(7), nullable=True)
    update_ts = db.Column('update_ts', db.DateTime, nullable=True)
    user_id = db.Column('user_id', db.String(1000), nullable=True)

    # parent keys
    registration_type = db.Column('registration_type', PG_ENUM(MhrRegistrationTypes),
                                  db.ForeignKey('mhr_registration_types.registration_type'), nullable=False)

    # Relationships - Registration
    registration = db.relationship('MhrRegistration', back_populates='draft', uselist=False)

    stale_count: int = 0

    @property
    def json(self) -> dict:
        """Return the draft as a json object."""
        draft = {
            'createDateTime': model_utils.format_ts(self.create_ts),
            'type': self.registration_type,
            'draftNumber': self.draft_number,
            'registration': self.draft
        }
        if self.mhr_number:
            draft['outOfDate'] = (self.stale_count > 0)
        if self.update_ts:
            draft['lastUpdateDateTime'] = model_utils.format_ts(self.update_ts)
        else:
            draft['lastUpdateDateTime'] = model_utils.format_ts(self.create_ts)
        return draft

    @classmethod
    def find_all_by_account_id(cls, account_id: str):
        """Return a summary list of drafts belonging to an account."""
        drafts_json = []
        if not account_id:
            return drafts_json
        try:
            max_results_size = int(current_app.config.get('ACCOUNT_DRAFTS_MAX_RESULTS', 1000))
            results = db.session.execute(QUERY_ACCOUNT_DRAFTS,
                                         {'query_account': account_id, 'max_results_size': max_results_size})
            rows = results.fetchall()
            if rows is not None:
                for row in rows:
                    drafts_json.append(MhrDraft.__build_account_draft_result(row))
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB find_all_by_account_id exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

        return drafts_json

    @staticmethod
    def __build_account_draft_result(row) -> dict:
        """Build a draft result from a query result set row."""
        registering_name = str(row[7])
        if not registering_name or registering_name == 'None':
            registering_name = ''
        ref_id = str(row[4])
        if not ref_id or ref_id == 'None':
            ref_id = ''
        mhr_num = str(row[8])
        stale_count: int = int(row[9])
        if not mhr_num or mhr_num == 'None':
            mhr_num = ''
        draft_json = {
            'draftNumber': str(row[0]),
            'createDateTime': model_utils.format_ts(row[1]),
            'registrationType': str(str(row[2])),
            'registrationDescription': str(row[3]),
            'lastUpdateDateTime': model_utils.format_ts(row[5]),
            'path': '/mhr/api/v1/drafts/' + str(row[0]),
            'submittingParty': str(row[6]),
            'registeringName': registering_name,
            'clientReferenceId': ref_id,
            'mhrNumber': mhr_num
        }
        if draft_json.get('mhrNumber'):
            draft_json['outOfDate'] = (stale_count > 0)
        return draft_json

    @classmethod
    def find_by_draft_number(cls, draft_number: str = None, allow_used: bool = False):
        """Return a draft statement by document ID."""
        draft = None
        if draft_number:
            try:
                draft = cls.query.filter(MhrDraft.draft_number == draft_number).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB find_by_draft_number exception: ' + str(db_exception))
                raise DatabaseException(db_exception)

        if not draft:
            code = ResourceErrorCodes.NOT_FOUND_ERR
            message = model_utils.ERR_DRAFT_NOT_FOUND.format(code=code, draft_number=draft_number)
            raise BusinessException(
                error=message,
                status_code=HTTPStatus.NOT_FOUND
            )

        if draft.registration and not allow_used:
            code = ResourceErrorCodes.UNAUTHORIZED_ERR
            message = model_utils.ERR_DRAFT_USED.format(code=code, draft_number=draft_number)
            raise BusinessException(
                error=message,
                status_code=HTTPStatus.BAD_REQUEST
            )
        if draft.mhr_number:
            current_app.logger.debug(f'Checking if draftId={draft.id} on mhr {draft.mhr_number} is out of date.')
            draft.get_stale_count()
            current_app.logger.debug(f'DraftId={draft.id} out of date count={draft.stale_count}.')
        return draft

    @classmethod
    def delete(cls, draft_number: str = None):
        """Delete a draft statement by document ID."""
        draft = None
        if draft_number:
            draft = cls.find_by_draft_number(draft_number, False)
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
    def update(cls, request_json, draft_number: str = None):
        """Update an existing draft statement by document number."""
        draft = None
        if request_json and request_json.get('registration') and draft_number:
            draft = cls.find_by_draft_number(draft_number, False)
        if draft:
            draft.update_ts = model_utils.now_ts()
            draft.draft = request_json.get('registration')
        return draft

    @staticmethod
    def create_from_json(json_data, account_id: str, user_id: str = None):
        """Create a draft object from a json Draft schema object: map json to db."""
        draft: MhrDraft = MhrDraft()
        draft.account_id = account_id
        draft.registration_type = json_data.get('type', MhrRegistrationTypes.MHREG)
        draft.draft = json_data.get('registration')
        if user_id:
            draft.user_id = user_id
        if json_data.get('registration') and 'mhrNumber' in json_data['registration']:
            draft.mhr_number = json_data['registration']['mhrNumber']
        # Not null constraint: should be removed if staff can submit requests without an account id.
        if not account_id:
            draft.account_id = 'NA'
        return draft

    @staticmethod
    def create_from_registration(registration, json_data, user_id: str = None):
        """Create a draft object from a registration."""
        draft: MhrDraft = MhrDraft()
        if registration.draft_id:
            draft.id = registration.draft_id  # pylint: disable=invalid-name; allow name of id.
        draft.account_id = registration.account_id
        draft.create_ts = registration.registration_ts
        draft.mhr_number = registration.mhr_number
        draft.draft_number = registration.draft_number
        draft.registration_type = registration.registration_type
        draft.draft = json_data
        if user_id:
            draft.user_id = user_id
        # Not null constraint: should be removed.
        if not draft.account_id:
            draft.account_id = 'NA'
        return draft

    def get_stale_count(self):
        """Determine if the draft is out of date."""
        self.stale_count = 0
        if self.mhr_number and self.create_ts:
            try:
                result = db.session.execute(QUERY_DRAFT_STALE_COUNT,
                                            {'query_value1': self.mhr_number, 'query_value2': self.create_ts})
                row = result.first()
                self.stale_count = int(row[0])
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB get_stale_count exception: ' + str(db_exception))
