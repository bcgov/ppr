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
from .registration import Registration  # noqa: F401 pylint: disable=unused-import


class TrustIndenture(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the financing statement trust indenture information."""

    __versioned__ = {}
    __tablename__ = 'trust_indenture'

#    trust_id = db.Column('trust_id', db.Integer, primary_key=True, server_default=db.FetchedValue())
    trust_id = db.Column('trust_id', db.Integer, db.Sequence('trust_id_seq'), primary_key=True)
    trust_indenture = db.Column('trust_indenture', db.String(1), nullable=False)

    # parent keys
    registration_id = db.Column('registration_id', db.Integer,
                                db.ForeignKey('registration.registration_id'), nullable=False)
    financing_id = db.Column('financing_id', db.Integer,
                             db.ForeignKey('financing_statement.financing_id'), nullable=False)
    registration_id_end = db.Column('registration_id_end', db.Integer, nullable=True)
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
    def find_by_registration_number(cls, registration_num: str = None):
        """Return a list of trust indenture objects by registration number."""
        trust_indenture = None
        if registration_num:
            trust_indenture = cls.query.filter(TrustIndenture.registration_id == Registration.registration_id,
                                               Registration.registration_num == registration_num) \
                                        .order_by(TrustIndenture.trust_id).all()

        return trust_indenture

    @classmethod
    def find_by_financing_id(cls, financing_id: int = None):
        """Return a list of trust indenture objects by financing statement ID."""
        trust_indenture = None
        if financing_id:
            trust_indenture = cls.query.filter(TrustIndenture.financing_id == financing_id) \
                                        .order_by(TrustIndenture.trust_id).all()

        return trust_indenture

    @staticmethod
    def create_from_json(json_data, registration_id: int = None):
        """Create a trust indenture object from a json schema object: map json to db."""
        trust_indenture = TrustIndenture()
        if registration_id:
            trust_indenture.registration_id = registration_id
        if 'trustIndenture' in json_data and json_data['trustIndenture']:
            trust_indenture.trust_indenture = 'Y'
        else:
            trust_indenture.trust_indenture = 'N'

        return [trust_indenture]
