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
"""This module holds data for general collateral."""
from __future__ import annotations

#from http import HTTPStatus

#from sqlalchemy import event

#from ppr_api.exceptions import BusinessException

from .db import db


class GeneralCollateral(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the general collateral information."""

    __versioned__ = {}
    __tablename__ = 'general_collateral'

    collateral_id = db.Column('general_collateral_id', db.Integer, primary_key=True, server_default=db.FetchedValue())
    description = db.Column('description', db.String(4000), nullable=False)

    # parent keys
    registration_id = db.Column('registration_id', db.Integer, 
                                db.ForeignKey('registration.registration_id'), nullable=False)
    financing_id = db.Column('financing_id', db.Integer, 
                             db.ForeignKey('financing_statement.financing_id'), nullable=False)
    registration_id_end = db.Column('registration_id_end', db.Integer, nullable=True)
#                                db.ForeignKey('registration.registration_id'), nullable=True)

    # Relationships - Registration
    registration = db.relationship("Registration", foreign_keys=[registration_id], 
                               back_populates="general_collateral", cascade='all, delete', uselist=False)
#    registration_end = db.relationship("Registration", foreign_keys=[registration_id_end])

    # Relationships - FinancingStatement
    financing_statement = db.relationship("FinancingStatement", foreign_keys=[financing_id], 
                               back_populates="general_collateral", cascade='all, delete', uselist=False)


    def save(self):
        """Save the object to the database immediately."""
#        db.session.add(self)
#        db.session.commit()

    @property
    def json(self) -> dict:
        """Return the genreal collateral as a json object."""
        return {
            'collateralId': self.collateral_id,
            'description': self.description
        }

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
            collateral = cls.query.filter(GeneralCollateral.registration_id == registration_id) \
                               .order_by(GeneralCollateral.collateral_id).all()

        return collateral


    @classmethod
    def find_by_financing_id(cls, financing_id: int = None):
        """Return a list of general collateral objects by financing statement ID."""
        collateral = None
        if financing_id:
            collateral = cls.query.filter(GeneralCollateral.financing_id == financing_id) \
                                  .order_by(GeneralCollateral.collateral_id).all()

        return collateral


    @staticmethod
    def create_from_json(json_data, registration_id: int = None):
        """Create a general collateral object from a json schema object: map json to db."""
        collateral = GeneralCollateral()
        collateral.registration_id = registration_id
        collateral.description = json_data['description']

        return collateral

    @staticmethod
    def create_from_financing_json(json_data, registration_id: int = None):
        """Create a list of general collateral objects from a financing statement json schema object: map json to db."""
        collateral_list = []
        if 'generalCollateral' in json_data and len(json_data['generalCollateral']) > 0:
            for collateral in json_data['generalCollateral']:
                collateral_list.append(GeneralCollateral.create_from_json(collateral, registration_id))

        return collateral_list


    @staticmethod
    def create_from_statement_json(json_data, registration_id: int, financing_id: int):
        """Create a list of general collateral objects from an amendment/change statement json schema object: map json to db."""
        collateral_list = []
        if json_data and registration_id and financing_id and \
                'addGeneralCollateral' in json_data and len(json_data['addGeneralCollateral']) > 0:
            for collateral in json_data['addGeneralCollateral']:
                gc = GeneralCollateral.create_from_json(collateral, registration_id)
                gc.financing_id = financing_id
                collateral_list.append(gc)

        return collateral_list
