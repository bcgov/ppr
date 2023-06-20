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
"""This module holds data for MH home section information."""

# from flask import current_app
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from .db import db
from .type_tables import MhrStatusTypes


KEY_STATEMENT = "SELECT mhr_serial_compressed_key(:serial_number) AS search_key"  # noqa: Q000


class MhrSection(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the MH section information."""

    __tablename__ = 'mhr_sections'

    id = db.Column('id', db.Integer, db.Sequence('mhr_section_id_seq'), primary_key=True)
    compressed_key = db.Column('compressed_key', db.String(6), nullable=False, index=True)
    serial_number = db.Column('serial_number', db.String(20), nullable=False)
    length_feet = db.Column('length_feet', db.Integer, nullable=False)
    width_feet = db.Column('width_feet', db.Integer, nullable=False)
    length_inches = db.Column('length_inches', db.Integer, nullable=True)
    width_inches = db.Column('width_inches', db.Integer, nullable=True)

    # parent keys
    registration_id = db.Column('registration_id', db.Integer, db.ForeignKey('mhr_registrations.id'), nullable=False,
                                index=True)
    change_registration_id = db.Column('change_registration_id', db.Integer, nullable=False, index=True)
    status_type = db.Column('status_type', PG_ENUM(MhrStatusTypes),
                            db.ForeignKey('mhr_status_types.status_type'), nullable=False)

    # Relationships - MhrRegistration
    registration = db.relationship('MhrRegistration', foreign_keys=[registration_id],
                                   back_populates='sections', cascade='all, delete', uselist=False)

    @property
    def json(self) -> dict:  # pylint: disable=too-many-branches
        """Return the section as a json object."""
        section = {
            'serialNumber': self.serial_number,
            'lengthFeet': self.length_feet,
            'widthFeet': self.width_feet
        }
        if self.length_inches:
            section['lengthInches'] = self.length_inches
        if self.width_inches:
            section['widthInches'] = self.width_inches
        return section

    @classmethod
    def find_by_id(cls, section_id: int = None):
        """Return a section object by section ID."""
        section = None
        if section_id:
            section = cls.query.get(section_id)

        return section

    @classmethod
    def find_by_registration_id(cls, registration_id: int = None):
        """Return a list of section objects by registration id."""
        sections = None
        if registration_id:
            sections = cls.query.filter(MhrSection.registration_id == registration_id) \
                                    .order_by(MhrSection.id).all()

        return sections

    @classmethod
    def find_by_change_registration_id(cls, registration_id: int = None):
        """Return a list of section objects by change registration id."""
        sections = None
        if registration_id:
            sections = cls.query.filter(MhrSection.change_registration_id == registration_id) \
                                    .order_by(MhrSection.id).all()

        return sections

    @staticmethod
    def create_from_json(json_data, registration_id: int = None):
        """Create a description object from a json schema object: map json to db."""
        # current_app.logger.info(json_data)
        # sections = new_info['sections']
        section: MhrSection = MhrSection(status_type=MhrStatusTypes.ACTIVE,
                                         serial_number=json_data.get('serialNumber'),
                                         length_feet=json_data.get('lengthFeet'),
                                         width_feet=json_data.get('widthFeet'),
                                         length_inches=json_data.get('lengthInches', None),
                                         width_inches=json_data.get('widthInches', None))
        if registration_id:
            section.registration_id = registration_id
            section.change_registration_id = registration_id
        section.compressed_key = MhrSection.get_compressed_key(section.serial_number)
        return section

    @staticmethod
    def get_compressed_key(serial_number: str):
        """Generate the serial number compressed key value from a database function."""
        result = db.session.execute(KEY_STATEMENT, {'serial_number': serial_number})
        row = result.first()
        return str(row[0])
