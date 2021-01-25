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
"""This module holds data for vehicle collateral."""
from __future__ import annotations

from enum import Enum
#from http import HTTPStatus

#from sqlalchemy import event

#from ppr_api.exceptions import BusinessException

from .db import db


class VehicleCollateral(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the vehicle collateral information."""

    class VehicleTypes(Enum):
        """Render an Enum of the vehicle types."""
        AIRCRAFT = 'AC'
        AIRCRAFT_AIRFRAME = 'AF'
        BOAT = 'BO'
        ELECTRIC_VEHICLE = 'EV'
        MANUFACTURED_HOME = 'MH'
        MOTOR_VEHICLE = 'MV'
        OUTBOARD_MOTOR = 'OB'
        TRAILER = 'TR'

    __versioned__ = {}
    __tablename__ = 'vehicle_collateral'

    vehicle_id = db.Column('vehicle_collateral_id', db.Integer, primary_key=True, server_default=db.FetchedValue())
    vehicle_type_cd = db.Column('vehicle_type_cd', db.String(3), nullable=False) #, db.ForeignKey('vehicle_type.vehicle_type_cd'))
    year = db.Column('year', db.Integer, nullable=True)
    make = db.Column('make', db.String(60), nullable=True)
    model = db.Column('model', db.String(60), nullable=True)
    serial_number = db.Column('serial_number', db.String(30), nullable=True)
    mhr_number = db.Column('mhr_number', db.String(20), nullable=True)

    # parent keys
    registration_id = db.Column('registration_id', db.Integer, 
                                db.ForeignKey('registration.registration_id'), nullable=False)
    financing_id = db.Column('financing_id', db.Integer, 
                             db.ForeignKey('financing_statement.financing_id'), nullable=False)
    registration_id_end = db.Column('registration_id_end', db.Integer, nullable=True)
#                                db.ForeignKey('registration.registration_id'), nullable=True)

    # Relationships - Registration
    registration = db.relationship("Registration", foreign_keys=[registration_id], 
                               back_populates="vehicle_collateral", cascade='all, delete', uselist=False)
#    registration_end = db.relationship("Registration", foreign_keys=[registration_id_end])

    # Relationships - FinancingStatement
    financing_statement = db.relationship("FinancingStatement", foreign_keys=[financing_id], 
                               back_populates="vehicle_collateral", cascade='all, delete', uselist=False)

    def save(self):
        """Save the object to the database immediately."""
#        db.session.add(self)
#        db.session.commit()

    @property
    def json(self) -> dict:
        """Return the genreal collateral as a json object."""
        collateral = {
            'vehicleId': self.vehicle_id,
            'type': self.vehicle_type_cd
        }
        if self.year:
            collateral['year'] = self.year
        if self.make:
            collateral['make'] = self.make
        if self.model:
            collateral['model'] = self.model
        if self.serial_number:
            collateral['serialNumber'] = self.serial_number
        if self.mhr_number:
            collateral['manufacturedHomeRegistrationNumber'] = self.mhr_number

        return collateral


    @classmethod
    def find_by_id(cls, vehicle_id: int = None):
        """Return a vehicle collateral object by collateral ID."""
        collateral = None
        if vehicle_id:
            collateral = cls.query.get(vehicle_id)

        return collateral


    @classmethod
    def find_by_registration_id(cls, registration_id: int = None):
        """Return a list of vehicle collateral objects by registration id."""
        collateral = None
        if registration_id:
            collateral = cls.query.filter(VehicleCollateral.registration_id == registration_id) \
                               .order_by(VehicleCollateral.vehicle_id).all()

        return collateral


    @classmethod
    def find_by_financing_id(cls, financing_id: int = None):
        """Return a list of vehicle collateral objects by financing statement ID."""
        collateral = None
        if financing_id:
            collateral = cls.query.filter(VehicleCollateral.financing_id == financing_id) \
                                  .order_by(VehicleCollateral.vehicle_id).all()

        return collateral


    @staticmethod
    def create_from_json(json_data, registration_id: int = None):
        """Create a vehicle collateral object from a json schema object: map json to db."""
        collateral = VehicleCollateral()
        collateral.registration_id = registration_id
        collateral.vehicle_type_cd = json_data['type']
        collateral.serial_number = json_data['serialNumber']
        if 'year' in json_data:
            collateral.year = json_data['year']
        if 'make' in json_data:
            collateral.make = json_data['make']
        if 'model' in json_data:
            collateral.model = json_data['model']
        if 'manufacturedHomeRegistrationNumber' in json_data:
            collateral.mhr_number = json_data['manufacturedHomeRegistrationNumber']

        return collateral

    @staticmethod
    def create_from_financing_json(json_data, registration_id: int = None):
        """Create a list of vehicle collateral objects from a financing statement json schema object: map json to db."""
        collateral_list = []
        if 'vehicleCollateral' in json_data and len(json_data['vehicleCollateral']) > 0:
            for collateral in json_data['vehicleCollateral']:
                collateral_list.append(VehicleCollateral.create_from_json(collateral, registration_id))

        return collateral_list


    @staticmethod
    def create_from_statement_json(json_data, registration_id: int, financing_id: int):
        """Create a list of vehicle collateral objects from an amendment/change statement json schema object: map json to db."""
        collateral_list = []
        if json_data and registration_id and financing_id and \
                'addVehicleCollateral' in json_data and len(json_data['addVehicleCollateral']) > 0:
            for collateral in json_data['addVehicleCollateral']:
                vc = VehicleCollateral.create_from_json(collateral, registration_id)
                vc.financing_id = financing_id
                collateral_list.append(vc)

        return collateral_list
