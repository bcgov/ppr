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
"""This module holds model data for MHR registration report tracking."""

from flask import current_app

from mhr_api.exceptions import DatabaseException
from mhr_api.models import utils as model_utils

from .db import db


class MhrRegistrationReport(db.Model):
    """This class maintains MHR registration report information."""

    __tablename__ = 'mhr_registration_reports'

    id = db.Column('id', db.Integer, db.Sequence('mhr_registration_report_id_seq'), primary_key=True)
    create_ts = db.Column('create_ts', db.DateTime, nullable=False, index=True)
    report_data = db.Column('report_data', db.JSON, nullable=False)
    report_type = db.Column('report_type', db.String(30), nullable=False)
    doc_storage_url = db.Column('doc_storage_url', db.String(1000), nullable=True)

    # parent keys
    registration_id = db.Column('registration_id', db.Integer, db.ForeignKey('mhr_registrations.id'), nullable=False,
                                index=True)

    # Relationships - MhrRegistration
    registration = db.relationship('MhrRegistration', foreign_keys=[registration_id],
                                   cascade='all, delete', uselist=False)

    @property
    def json(self) -> dict:
        """Return the verification report information as a json object."""
        result = {
            'id': self.id,
            'createDateTime': model_utils.format_ts(self.create_ts),
            'registrationId': self.registration_id,
            'reportData': self.report_data,
            'reportType': self.report_type
        }
        if self.doc_storage_url:
            result['documentStorageURL'] = self.doc_storage_url
        return result

    def save(self):
        """Render a record of mhr registration report information to the local cache."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:  # noqa: B902; just logging
            current_app.logger.error('DB mhr registration report save exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    def update_storage_url(self, doc_storage_url: str = None):
        """Update the report doc storage URL after the document is generated and stored."""
        self.doc_storage_url = doc_storage_url
        self.create_ts = model_utils.now_ts()
        self.save()

    @classmethod
    def find_by_id(cls, report_id: int):
        """Return the mhr registration report metadata record matching the id."""
        report = None
        if report_id:
            report = cls.query.get(report_id)

        return report

    @classmethod
    def find_by_registration_id(cls, registration_id: int = None):
        """Return the mhr registration report metadata record that matches the registration ID."""
        report = None
        if registration_id:
            report = cls.query.filter(MhrRegistrationReport.registration_id == registration_id).one_or_none()

        return report
