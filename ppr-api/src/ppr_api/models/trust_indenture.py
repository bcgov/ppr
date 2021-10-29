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
"""This module holds data for financing statement trust indenture information."""
from __future__ import annotations

from .db import db


class TrustIndenture(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the financing statement trust indenture information."""

    TRUST_INDENTURE_YES = 'Y'
    TRUST_INDENTURE_NO = 'N'
    __tablename__ = 'trust_indentures'

    id = db.Column('id', db.Integer, db.Sequence('trust_id_seq'), primary_key=True)
    trust_indenture = db.Column('trust_indenture', db.String(1), nullable=False)

    # parent keys
    registration_id = db.Column('registration_id', db.Integer, db.ForeignKey('registrations.id'), nullable=False,
                                index=True)
    financing_id = db.Column('financing_id', db.Integer, db.ForeignKey('financing_statements.id'), nullable=False,
                             index=True)
    registration_id_end = db.Column('registration_id_end', db.Integer, nullable=True,
                                    index=True)
#                                db.ForeignKey('registration.registration_id'), nullable=True)

    # Relationships - Registration
    registration = db.relationship('Registration', foreign_keys=[registration_id],
                                   back_populates='trust_indenture', cascade='all, delete', uselist=False)
#    registration_end = db.relationship("Registration", foreign_keys=[registration_id_end])

    # Relationships - FinancingStatement
    financing_statement = db.relationship('FinancingStatement', foreign_keys=[financing_id],
                                          back_populates='trust_indenture', cascade='all, delete', uselist=False)

    @classmethod
    def find_by_id(cls, trust_id: int = None):
        """Return a trust indenture object by expiry ID."""
        trust_indenture = None
        if trust_id:
            trust_indenture = cls.query.get(trust_id)

        return trust_indenture

    @classmethod
    def find_by_registration_id(cls, registration_id: int):
        """Return a list of trust indenture objects by registration number."""
        trust_indenture = None
        if registration_id:
            trust_indenture = cls.query.filter(TrustIndenture.registration_id == registration_id) \
                                        .order_by(TrustIndenture.id).one_or_none()

        return trust_indenture

    @classmethod
    def find_by_financing_id(cls, financing_id: int):
        """Return a list of trust indenture objects by financing statement ID."""
        trust_indenture = None
        if financing_id:
            trust_indenture = cls.query.filter(TrustIndenture.financing_id == financing_id) \
                                        .order_by(TrustIndenture.id).all()

        return trust_indenture

    @staticmethod
    def create_from_json(json_data, registration_id: int = None):
        """Create a trust indenture object from a json schema object: map json to db."""
        trust_indenture = TrustIndenture()
        if registration_id:
            trust_indenture.registration_id = registration_id
        if 'trustIndenture' in json_data and json_data['trustIndenture']:
            trust_indenture.trust_indenture = TrustIndenture.TRUST_INDENTURE_YES
        else:
            trust_indenture.trust_indenture = TrustIndenture.TRUST_INDENTURE_NO

        return [trust_indenture]

    @staticmethod
    def create_from_amendment_json(financing_id: int, registration_id: int):
        """Create a trust indenture object as part of an amendment registration: map json to db."""
        trust_indenture = TrustIndenture()
        trust_indenture.registration_id = registration_id
        trust_indenture.financing_id = financing_id
        trust_indenture.trust_indenture = TrustIndenture.TRUST_INDENTURE_YES

        return trust_indenture
