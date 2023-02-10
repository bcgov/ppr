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
"""This module holds model data for registration surface mail verification report generation and tracking."""
from datetime import datetime

from flask import current_app
from sqlalchemy.sql import text

from ppr_api.exceptions import DatabaseException
from ppr_api.models import utils as model_utils

from .db import db


QUERY_FILTER_DATE_START = """
SELECT id, create_ts, doc_storage_url
  FROM mail_reports
 WHERE create_ts > :query_start
   AND doc_storage_url IS NOT NULL
"""
QUERY_FILTER_DATE_RANGE = """
SELECT id, create_ts, doc_storage_url
  FROM mail_reports
 WHERE create_ts BETWEEN :query_start AND :query_end
   AND doc_storage_url IS NOT NULL
"""


class MailReport(db.Model):
    """This class maintains registration BCMail+ verification report information."""

    __tablename__ = 'mail_reports'

    id = db.Column('id', db.Integer, db.Sequence('mail_report_id_seq'), primary_key=True)
    create_ts = db.Column('create_ts', db.DateTime, nullable=False, index=True)
    report_data = db.Column('report_data', db.JSON, nullable=False)
    doc_storage_url = db.Column('doc_storage_url', db.String(1000), nullable=True)
    retry_count = db.Column('retry_count', db.Integer, nullable=True)
    status = db.Column('status', db.Integer, nullable=True)
    message = db.Column('message', db.String(2000), nullable=True)

    # parent keys
    registration_id = db.Column('registration_id', db.Integer, db.ForeignKey('registrations.id'), nullable=False,
                                index=True)
    party_id = db.Column('party_id', db.Integer, db.ForeignKey('parties.id'), nullable=False, index=True)

    # Relationships - Don't need

    @property
    def json(self) -> dict:
        """Return the verification report information as a json object."""
        result = {
            'id': self.id,
            'createDateTime': model_utils.format_ts(self.create_ts),
            'registrationId': self.registration_id,
            'partyId': self.party_id,
            'reportData': self.report_data,
            'documentStorageURL': self.doc_storage_url if self.doc_storage_url else '',
            'retryCount': self.retry_count if self.retry_count else 0,
            'status': self.status if self.status else 0,
            'message': self.message if self.message else ''
        }
        return result

    def save(self):
        """Persist mail report information."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:  # noqa: B902; just logging
            current_app.logger.error('DB mail report save exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    def update_storage_url(self, doc_storage_url: str, status: int):
        """Update the mail report doc storage URL after the document is generated and stored."""
        self.doc_storage_url = doc_storage_url
        self.status = status
        self.create_ts = model_utils.now_ts()
        self.save()

    def update_retry_count(self, status: int = None, message: str = None):
        """Update the mail report retry count if document generation or storage failed."""
        if not self.retry_count:
            self.retry_count = 1
        else:
            self.retry_count += 1
        if status:
            self.status = status
        if message:
            self.message = message[0:2000]
        self.create_ts = model_utils.now_ts()
        self.save()

    @classmethod
    def find_by_id(cls, report_id: int):
        """Return the mail report record matching the id."""
        mail_report = None
        if report_id:
            mail_report = cls.query.get(report_id)

        return mail_report

    @classmethod
    def find_by_registration_party_id(cls, registration_id: int, party_id: int):
        """Return the mail report that matches the registration id - party id pair."""
        mail_report = None
        if registration_id and party_id:
            mail_report = cls.query.filter(MailReport.registration_id == registration_id,
                                           MailReport.party_id == party_id).one_or_none()
        return mail_report

    @classmethod
    def find_list_by_timestamp(cls, start: datetime, end: datetime):
        """Return a list of mail reports that matches the start and optional end timestamps."""
        try:
            results = []
            if not start:
                return results
            result_set = None
            if not end:
                query = text(QUERY_FILTER_DATE_START)
                result_set = db.session.execute(query, {'query_start': start})
            else:
                query = text(QUERY_FILTER_DATE_RANGE)
                result_set = db.session.execute(query, {'query_start': start, 'query_end': end})
            rows = result_set.fetchall()
            if rows is not None:
                for row in rows:
                    result = {
                        'id': int(row[0]),
                        'dateTime': model_utils.format_ts(row[1]),
                        'docStorageRef': str(row[2])
                    }
                    results.append(result)
            return results
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB find_list_by_timestamp exception: ' + str(db_exception))
            raise DatabaseException(db_exception)
