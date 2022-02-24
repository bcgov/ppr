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
"""This module holds model data for registration verification report tracking."""

from __future__ import annotations

from flask import current_app

from ppr_api.exceptions import DatabaseException
from ppr_api.models import utils as model_utils

from .db import db


class VerificationReport(db.Model):
    """This class maintains registration verification report information."""

    __tablename__ = 'verification_reports'

    id = db.Column('id', db.Integer, db.Sequence('verification_report_id_seq'), primary_key=True)
    create_ts = db.Column('create_ts', db.DateTime, nullable=False, index=True)
    report_data = db.Column('report_data', db.JSON, nullable=False)
    report_type = db.Column('report_type', db.String(30), nullable=False)
    doc_storage_url = db.Column('doc_storage_url', db.String(1000), nullable=True)

    # parent keys
    registration_id = db.Column('registration_id', db.Integer, db.ForeignKey('registrations.id'), nullable=False,
                                index=True)

    # Relationships - Registration
    registration = db.relationship('Registration', foreign_keys=[registration_id],
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
        """Render a search results detail information to the local cache."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:  # noqa: B902; just logging
            current_app.logger.error('DB verification report save exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    def update_storage_url(self, doc_storage_url: str = None):
        """Update the verfication report doc storage URL after the document is generated and stored."""
        self.doc_storage_url = doc_storage_url
        self.create_ts = model_utils.now_ts()
        self.save()

    @classmethod
    def find_by_id(cls, vr_id: int):
        """Return the verification report record matching the id."""
        verification_report = None
        if vr_id:
            verification_report = cls.query.get(vr_id)

        return verification_report

    @classmethod
    def find_by_registration_id(cls, registration_id: int = None):
        """Return the verification report that matches the registration ID."""
        verification_report = None
        if registration_id:
            verification_report = cls.query.filter(VerificationReport.registration_id == registration_id).one_or_none()

        return verification_report
