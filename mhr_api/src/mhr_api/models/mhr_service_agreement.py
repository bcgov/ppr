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
"""This module holds model data for MHR service agreement document information."""
import copy
import json

from flask import current_app
from sqlalchemy.sql import text

from mhr_api.models import utils as model_utils

from .db import db


DEFAULT_AGREEMENT_TYPE: str = 'DEFAULT'
VERSION_1: str = 'v1'
VERSION_CURRENT = 'current'
VERSION_LATEST = 'latest'
UPDATE_USER_PROFILE = """
UPDATE user_profiles
   SET service_agreements = '{agreement}'
 WHERE id = (SELECT id
               FROM users
              WHERE account_id = '{account_id}'
                AND username = '{username}')
"""
SELECT_USER_PROFILE = """
SELECT up.service_agreements
  FROM user_profiles up, users u
 WHERE u.id = up.id
   AND u.account_id = :query_value1
   AND u.username = :query_value2
"""


class MhrServiceAgreement(db.Model):
    """This class maintains information about MHR service agreement documents."""

    __tablename__ = 'mhr_service_agreements'

    id = db.Column('id', db.Integer, db.Sequence('mhr_agreements_id_seq'), primary_key=True)
    agreement_type = db.Column('agreement_type', db.String(20), nullable=False)
    version = db.Column('version', db.String(10), nullable=False)
    create_ts = db.Column('create_ts', db.DateTime, nullable=False)
    doc_storage_url = db.Column('doc_storage_url', db.String(1000), nullable=False)
    current_version = db.Column('current_version', db.String(1), nullable=False)

    @property
    def json(self) -> dict:
        """Return the service agreement information as a json object."""
        result = {
            'agreementType': self.agreement_type,
            'version': self.version,
            'latestVersion': bool(self.current_version and self.current_version == 'Y'),
            'createDateTime': model_utils.format_ts(self.create_ts)
        }
        return result

    @classmethod
    def find_by_id(cls, agreement_id: int):
        """Return the mhr service agreement information record matching the id."""
        agreement = None
        if agreement_id:
            agreement = cls.query.get(agreement_id)

        return agreement

    @classmethod
    def find_by_version(cls, version: str = None):
        """Return the mhr service agreement information record matching the version."""
        agreement = None
        if version and version.lower() in (VERSION_CURRENT, VERSION_LATEST):
            return cls.find_by_current()
        if version:
            agreement = cls.query.filter(MhrServiceAgreement.version == version).one_or_none()
        return agreement

    @classmethod
    def find_by_current(cls):
        """Return the mhr service agreement information record that is current."""
        return cls.query.filter(MhrServiceAgreement.current_version == 'Y').one_or_none()

    @classmethod
    def find_all(cls):
        """Return all the service agreement document information."""
        return db.session.query(MhrServiceAgreement).all()

    @classmethod
    def find_all_json(cls):
        """Return all the service agreement document information as JSON."""
        agreement_json = []
        agreements = MhrServiceAgreement.find_all()
        for agreement in agreements:
            agreement_json.append(agreement.json)
        return agreement_json

    @staticmethod
    def update_user_profile(json_data: dict, account_id: str, username: str) -> int:
        """Add the service agreement info to the user profile."""
        update_count: int = 0
        if not json_data or not account_id or not username:
            return update_count
        agreement_json: dict = copy.deepcopy(json_data)
        agreement_json['acceptAgreementRequired'] = False
        agreement = json.dumps(agreement_json)
        query_s = UPDATE_USER_PROFILE
        query_s = query_s.format(agreement=agreement, account_id=account_id, username=username)
        current_app.logger.debug(f'Executing update query {query_s}')
        query = text(query_s)
        result = db.session.execute(query)
        update_count = result.rowcount
        db.session.commit()
        if result:
            current_app.logger.debug(f'Updated {update_count} user_profiles.service_agreements to {agreement}.')
        return update_count

    @staticmethod
    def get_agreement_profile(account_id: str, username: str) -> dict:
        """Retrieve the service agreement info from the user profile."""
        agreement_json: dict = {}
        if not account_id or not username:
            return agreement_json
        try:
            query = text(SELECT_USER_PROFILE)
            result = db.session.execute(query, {'query_value1': account_id, 'query_value2': username})
            if result:
                current_app.logger.info('11111111')
                row = result.first()
                if row:
                    current_app.logger.info('22222222')
                    agreement_json = row[0]
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('get_agreement_profile exception: ' + str(db_exception))
        return agreement_json
