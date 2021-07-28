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
"""This module holds data for legacy previous financing statement information only used in reports."""
from __future__ import annotations

from .utils import format_ts
from .db import db


class PreviousFinancingStatement(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the previous financing statement information (legacy only)."""

    __tablename__ = 'previous_financing_statements'

    financing_id = db.Column('financing_id', db.Integer, db.ForeignKey('financing_statements.id'),
                             primary_key=True, nullable=False)
    # Free text description
    registration_type = db.Column('registration_type', db.String(30), nullable=False)
    # cb is companies branch
    cb_date = db.Column('cb_date', db.DateTime, nullable=True)
    cb_number = db.Column('cb_number', db.String(10), nullable=True)
    # cr is central registry
    cr_date = db.Column('cr_date', db.DateTime, nullable=True)
    cr_number = db.Column('cr_number', db.String(10), nullable=True)
    # mhr is manufactured homes registry
    mhr_date = db.Column('mhr_date', db.DateTime, nullable=True)
    mhr_number = db.Column('mhr_number', db.String(10), nullable=True)

    # parent keys

    # Relationships - Registration
    financing_statement = db.relationship('FinancingStatement', foreign_keys=[financing_id],
                                          back_populates='previous_statement', cascade='all, delete', uselist=False)

    @property
    def json(self) -> dict:
        """Return the court_order as a json object."""
        previous_financing = {
            'registrationType': self.registration_type
        }
        if self.mhr_number:
            previous_financing['mhrNumber'] = self.mhr_number
            previous_financing['mhrDateTime'] = format_ts(self.mhr_date)
        if self.cr_number:
            previous_financing['crNumber'] = self.cr_number
            previous_financing['crDateTime'] = format_ts(self.cr_date)
        if self.cb_number:
            previous_financing['cbNumber'] = self.cb_number
            previous_financing['cbDateTime'] = format_ts(self.cb_date)

        return previous_financing

    @classmethod
    def find_by_id(cls, financing_id: int = None):
        """Return a previous financing statement object by ID."""
        previous_financing = None
        if financing_id:
            previous_financing = cls.query.get(financing_id)

        return previous_financing
