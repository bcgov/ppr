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
"""This module holds data for the legacy application general collateral."""
from __future__ import annotations

from enum import Enum

from ppr_api.models import utils as model_utils

from .db import db


STATUS_ADDED = 'A'
STATUS_DELETED = 'D'


class GeneralCollateralLegacy(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the legacy application general collateral information."""

    class StatusTypes(str, Enum):
        """Render an Enum of the status types."""

        ADDED = STATUS_ADDED
        DELETED = STATUS_DELETED

    __tablename__ = 'general_collateral_legacy'

    id = db.Column('id', db.Integer, db.Sequence('general_id_seq'), primary_key=True)
    description = db.Column('description', db.Text, nullable=False)
    # A - added, D - removed/deleted, or null if neither
    status = db.Column('status', db.String(1), nullable=True)

    # parent keys
    registration_id = db.Column('registration_id', db.Integer,
                                db.ForeignKey('registrations.id'), nullable=False, index=True)
    financing_id = db.Column('financing_id', db.Integer,
                             db.ForeignKey('financing_statements.id'), nullable=False, index=True)
    registration_id_end = db.Column('registration_id_end', db.Integer, nullable=True, index=True)

    # Relationships - Registration
    registration = db.relationship('Registration', foreign_keys=[registration_id],
                                   back_populates='general_collateral_legacy', cascade='all, delete', uselist=False)

    # Relationships - FinancingStatement
    financing_statement = db.relationship('FinancingStatement', foreign_keys=[financing_id],
                                          back_populates='general_collateral_legacy',
                                          cascade='all, delete', uselist=False)

    @property
    def current_json(self) -> dict:
        """Generate a Financing Statement current view of the general collateral as json/dict."""
        collateral = {
            'collateralId': self.id,
            'addedDateTime': ''
        }
        if self.status and self.status == STATUS_ADDED:
            collateral['descriptionAdd'] = self.description
        elif self.status and self.status == STATUS_DELETED:
            collateral['descriptionDelete'] = self.description
        else:
            collateral['description'] = self.description
        if self.registration:
            collateral['addedDateTime'] = model_utils.format_ts(self.registration.registration_ts)
        return collateral

    @property
    def json(self) -> dict:
        """Generate the default view of the general collateral as json/a dict."""
        collateral = {
            'collateralId': self.id,
            'description': self.description,
            'addedDateTime': ''
        }
        if self.registration:
            collateral['addedDateTime'] = model_utils.format_ts(self.registration.registration_ts)
        return collateral

    @classmethod
    def find_by_id(cls, collateral_id: int = None):
        """Return a general collateral object by collateral ID."""
        collateral = None
        if collateral_id:
            collateral = cls.query.get(collateral_id)

        return collateral

    @classmethod
    def find_by_registration_id(cls, registration_id: int = None):
        """Return a list of general collateral objects by registration ID."""
        collateral = None
        if registration_id:
            collateral = cls.query.filter(GeneralCollateralLegacy.registration_id == registration_id) \
                                  .order_by(GeneralCollateralLegacy.id).all()

        return collateral

    @classmethod
    def find_by_financing_id(cls, financing_id: int = None):
        """Return a list of general collateral objects by financing statement ID."""
        collateral = None
        if financing_id:
            collateral = cls.query.filter(GeneralCollateralLegacy.financing_id == financing_id) \
                                  .order_by(GeneralCollateralLegacy.id).all()

        return collateral
