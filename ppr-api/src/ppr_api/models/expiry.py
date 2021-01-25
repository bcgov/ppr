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
"""This module holds data for financing statement expiry information."""
from __future__ import annotations

from http import HTTPStatus
from datetime import date

#from sqlalchemy import event

#from ppr_api.exceptions import BusinessException

from .db import db

from ppr_api.utils.datetime import now_ts_offset, expiry_dt_from_years


class Expiry(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the financing statement expiry information."""

    __versioned__ = {}
    __tablename__ = 'expiry'

    expiry_id = db.Column('expiry_id', db.Integer, primary_key=True, server_default=db.FetchedValue())
    expiry_dt = db.Column('expiry_dt', db.Date, nullable=True)
    life_years = db.Column('life_years', db.Integer)
    life_infinite = db.Column('life_infinite', db.String(1), nullable=True)

    # parent keys
    registration_id = db.Column('registration_id', db.Integer, 
                                db.ForeignKey('registration.registration_id'), nullable=False)
    financing_id = db.Column('financing_id', db.Integer, 
                             db.ForeignKey('financing_statement.financing_id'), nullable=False)
    registration_id_end = db.Column('registration_id_end', db.Integer, nullable=True)
#                                db.ForeignKey('registration.registration_id'), nullable=True)

    # Relationships - Registration
    registration = db.relationship("Registration", foreign_keys=[registration_id], 
                               cascade='all, delete', uselist=False)
#    registration_end = db.relationship("Registration", foreign_keys=[registration_id_end])

    # Relationships - FinancingStatement
    financing_statement = db.relationship("FinancingStatement", foreign_keys=[financing_id], 
                               back_populates="expiry", cascade='all, delete', uselist=False)


    def save(self):
        """Save the object to the database immediately."""
#        db.session.add(self)
#        db.session.commit()


    @classmethod
    def find_by_id(cls, expiry_id: int = None):
        """Return an expiry object by expiry ID."""
        expiry = None
        if expiry_id:
            expiry = cls.query.get(expiry_id)

        return expiry


    @classmethod
    def find_by_registration_id(cls, registration_id: int = None):
        """Return a list of expiry objects by registration number."""
        expiry = None
        if registration_id:
            expiry = cls.query.filter(Expiry.registration_id == registration_id).one_or_none()

        return expiry


    @classmethod
    def find_by_financing_id(cls, financing_id: int = None):
        """Return a list of expiry objects by financing statement ID."""
        expiry = None
        if financing_id:
            expiry = cls.query.filter(Expiry.financing_id == financing_id) \
                               .order_by(Expiry.expiry_id).all()

        return expiry


    @staticmethod
    def create_from_json(json_data, financing_type:str = None, registration_id: int = None):
        """Create a expiry object from a json schema object: map json to db."""
        expiry = Expiry()
        if registration_id:
            expiry.registration_id = registration_id
        if financing_type and financing_type == 'RL':
            expiry.life_infinite = 'N'
            expiry.life_years = 0
            expiry.expiry_dt = now_ts_offset(180, True)
        elif 'lifeInfinite' in json_data and json_data['lifeInfinite'] == True:
            expiry.life_infinite = 'Y'
            expiry.life_years = 0
        else:
            expiry.life_infinite = 'N'
            if 'lifeYears' in json_data:
                expiry.life_years = json_data['lifeYears']
                if expiry.life_years > 0:
                    expiry.expiry_dt = expiry_dt_from_years(expiry.life_years)
            if 'expiryDate' in json_data and not expiry.expiry_dt:
                expiry.expiry_dt = date.fromisoformat(json_data['expiryDate'])

        return [expiry]


    @staticmethod
    def create_from_renewal_json(json_data, 
                                 financing_id: int, 
                                 financing_type: str, 
                                 registration_id: int = None):
        """Create a expiry object from a json schema object: map json to db."""
        expiry = Expiry()
        expiry.financing_id = financing_id
        if registration_id:
            expiry.registration_id = registration_id
        expiry.life_years = 0
        expiry.life_infinite = 'N'
        if financing_type == 'RL':
            expiry.expiry_dt = now_ts_offset(180, True)
        elif 'expiryDate' in json_data:
            expiry.expiry_dt = date.fromisoformat(json_data['expiryDate'])

        return expiry
