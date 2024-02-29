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

from sqlalchemy.sql import text
from mhr_api.utils.base import BaseEnum

from .db import db


SEARCH_VIN_STATEMENT = "SELECT searchkey_vehicle(:serial_number) AS search_key"  # noqa: Q000
SEARCH_VIN_STATEMENT_AC = "SELECT searchkey_aircraft(:serial_number) AS search_key"  # noqa: Q000
SEARCH_STATEMENT_MH = "SELECT searchkey_mhr(:mhr_number) AS search_key"  # noqa: Q000


class VehicleCollateral(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the vehicle collateral information."""

    class SerialTypes(BaseEnum):
        """Render an Enum of the vehicle types."""

        AIRCRAFT = 'AC'
        AIRCRAFT_AIRFRAME = 'AF'
        AIRPLANE = 'AP'
        BOAT = 'BO'
        MANUFACTURED_HOME = 'MH'
        MOTOR_VEHICLE = 'MV'
        OUTBOARD_MOTOR = 'OB'
        TRAILER = 'TR'

    __tablename__ = 'serial_collateral'

    id = db.mapped_column('id', db.Integer, db.Sequence('vehicle_id_seq'), primary_key=True)
    vehicle_type = db.mapped_column('serial_type', db.String(2),
                                    db.ForeignKey('serial_types.serial_type'), nullable=False)
    year = db.mapped_column('year', db.Integer, nullable=True)
    make = db.mapped_column('make', db.String(60), nullable=True)
    model = db.mapped_column('model', db.String(60), nullable=True)
    serial_number = db.mapped_column('serial_number', db.String(30), nullable=True)
    mhr_number = db.mapped_column('mhr_number', db.String(6), nullable=True, index=True)
    search_vin = db.mapped_column('srch_vin', db.String(6), nullable=True, index=True)

    # parent keys
    registration_id = db.mapped_column('registration_id', db.Integer,
                                       db.ForeignKey('registrations.id'), nullable=False, index=True)
    financing_id = db.mapped_column('financing_id', db.Integer,
                                    db.ForeignKey('financing_statements.id'), nullable=False, index=True)
    registration_id_end = db.mapped_column('registration_id_end', db.Integer, nullable=True, index=True)

    # Relationships - Registration
    registration = db.relationship('Registration', foreign_keys=[registration_id],
                                   back_populates='vehicle_collateral', cascade='all, delete',
                                   uselist=False)
#    registration_end = db.relationship("Registration", foreign_keys=[registration_id_end])

    # Relationships - FinancingStatement
    financing_statement = db.relationship('FinancingStatement', foreign_keys=[financing_id],
                                          back_populates='vehicle_collateral', cascade='all, delete',
                                          uselist=False)
    # Relationships - SerialType
    serial_type = db.relationship('SerialType', foreign_keys=[vehicle_type],
                                  back_populates='vehicle_collateral', cascade='all, delete', uselist=False)

    @property
    def json(self) -> dict:
        """Return the genreal collateral as a json object."""
        collateral = {
            'vehicleId': self.id,
            'type': self.vehicle_type
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
            collateral = db.session.query(VehicleCollateral).filter(VehicleCollateral.id == vehicle_id).one_or_none()

        return collateral

    @classmethod
    def find_by_registration_id(cls, registration_id: int = None):
        """Return a list of vehicle collateral objects by registration id."""
        collateral = None
        if registration_id:
            collateral = db.session.query(VehicleCollateral) \
                .filter(VehicleCollateral.registration_id == registration_id) \
                .order_by(VehicleCollateral.id).all()

        return collateral

    @classmethod
    def find_by_financing_id(cls, financing_id: int = None):
        """Return a list of vehicle collateral objects by financing statement ID."""
        collateral = None
        if financing_id:
            collateral = db.session.query(VehicleCollateral) \
                .filter(VehicleCollateral.financing_id == financing_id) \
                .order_by(VehicleCollateral.id).all()

        return collateral

    @staticmethod
    def create_from_json(json_data, registration_id: int = None):
        """Create a vehicle collateral object from a json schema object: map json to db."""
        collateral = VehicleCollateral()
        collateral.registration_id = registration_id
        collateral.vehicle_type = json_data['type']
        collateral.serial_number = json_data['serialNumber']
        if 'year' in json_data:
            collateral.year = json_data['year']
        if 'make' in json_data:
            collateral.make = json_data['make']
        if 'model' in json_data:
            collateral.model = json_data['model']
        if collateral.serial_number:
            collateral.serial_number = collateral.serial_number.strip().upper()
            collateral.search_vin = VehicleCollateral.get_search_vin(collateral.vehicle_type,
                                                                     collateral.serial_number)
        if collateral.vehicle_type == VehicleCollateral.SerialTypes.MANUFACTURED_HOME:
            if 'manufacturedHomeRegistrationNumber' in json_data:
                collateral.mhr_number = \
                    VehicleCollateral.get_formatted_mhr_number(json_data['manufacturedHomeRegistrationNumber'])
            else:  # From Bob
                collateral.mhr_number = 'NR'

        return collateral

    @staticmethod
    def create_from_financing_json(json_data, registration_id: int = None):
        """Create a list of vehicle collateral objects from a financing statement json schema object: map json to db."""
        collateral_list = []
        if 'vehicleCollateral' in json_data and json_data['vehicleCollateral']:
            for collateral in json_data['vehicleCollateral']:
                collateral_list.append(VehicleCollateral.create_from_json(collateral, registration_id))

        return collateral_list

    @staticmethod
    def create_from_statement_json(json_data, registration_id: int, financing_id: int):
        """Create a list of vehicle collateral objects from an amendment/change statement json schema object.

        Map json to db.
        """
        collateral_list = []
        if json_data and registration_id and financing_id and \
                'addVehicleCollateral' in json_data and json_data['addVehicleCollateral']:
            for collateral in json_data['addVehicleCollateral']:
                v_collateral = VehicleCollateral.create_from_json(collateral, registration_id)
                v_collateral.financing_id = financing_id
                collateral_list.append(v_collateral)

        return collateral_list

    @staticmethod
    def get_search_vin(vehicle_type: str, serial_number: str):
        """Conditionally generate the search_vin value from a database function."""
        if not vehicle_type or not serial_number:
            return None

        statement = SEARCH_VIN_STATEMENT
        if vehicle_type in (VehicleCollateral.SerialTypes.AIRCRAFT,
                            VehicleCollateral.SerialTypes.AIRPLANE,
                            VehicleCollateral.SerialTypes.AIRCRAFT_AIRFRAME):
            statement = SEARCH_VIN_STATEMENT_AC
        query = text(statement)
        result = db.session.execute(query, {'serial_number': serial_number})
        row = result.first()
        return str(row._mapping['search_key'])  # pylint: disable=protected-access; follows documentation

    @staticmethod
    def get_formatted_mhr_number(mhr_number: str):
        """Conditionally format the MHR number value from a database function."""
        if not mhr_number:  # From Bob
            return 'NR'
        query = text(SEARCH_STATEMENT_MH)
        result = db.session.execute(query, {'mhr_number': mhr_number})
        row = result.first()
        return str(row._mapping['search_key'])  # pylint: disable=protected-access; follows documentation
