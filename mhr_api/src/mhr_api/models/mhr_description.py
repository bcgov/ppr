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
"""This module holds data for MHR descriptions."""

# from flask import current_app
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from mhr_api.models import utils as model_utils

from .db import db
from .type_tables import MhrStatusTypes


class MhrDescription(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the MHR description information."""

    __tablename__ = 'mhr_descriptions'

    id = db.Column('id', db.Integer, db.Sequence('mhr_description_id_seq'), primary_key=True)
    csa_number = db.Column('csa_number', db.String(10), nullable=True)
    csa_standard = db.Column('csa_standard', db.String(4), nullable=True)
    number_of_sections = db.Column('number_of_sections', db.Integer, nullable=False)
    square_feet = db.Column('square_feet', db.Integer, nullable=True)
    year_made = db.Column('year_made', db.Integer, nullable=True)
    circa = db.Column('circa', db.String(1), nullable=True)
    engineer_date = db.Column('engineer_date', db.DateTime, nullable=True)
    engineer_name = db.Column('engineer_name', db.String(150), nullable=True)
    manufacturer_name = db.Column('manufacturer_name', db.String(150), nullable=True)
    make = db.Column('make', db.String(60), nullable=True)
    model = db.Column('model', db.String(60), nullable=True)
    rebuilt_remarks = db.Column('rebuilt_remarks', db.String(300), nullable=True)
    other_remarks = db.Column('other_remarks', db.String(150), nullable=True)

    # parent keys
    registration_id = db.Column('registration_id', db.Integer, db.ForeignKey('mhr_registrations.id'), nullable=False,
                                index=True)
    change_registration_id = db.Column('change_registration_id', db.Integer, nullable=False, index=True)
    status_type = db.Column('status_type', PG_ENUM(MhrStatusTypes),
                            db.ForeignKey('mhr_status_types.status_type'), nullable=False)

    # Relationships - MhrRegistration
    registration = db.relationship('MhrRegistration', foreign_keys=[registration_id],
                                   back_populates='descriptions', cascade='all, delete', uselist=False)

    @property
    def json(self) -> dict:  # pylint: disable=too-many-branches
        """Return the description as a json object."""
        description = {
            'status': self.status_type,
            'sectionCount': self.number_of_sections,
            'baseInformation': {
                'make': '',
                'model': '',
                'circa': False
            }
        }
        if self.csa_number:
            description['csaNumber'] = self.csa_number
        if self.csa_standard:
            description['csaStandard'] = self.csa_standard
        if self.square_feet:
            description['squareFeet'] = self.square_feet
        if self.year_made:
            description['baseInformation']['year'] = self.year_made
        if self.circa and self.circa == 'Y':
            description['baseInformation']['circa'] = True
        if self.manufacturer_name:
            description['manufacturer'] = self.manufacturer_name
        if self.make:
            description['baseInformation']['make'] = self.make
        if self.model:
            description['baseInformation']['model'] = self.model
        if self.engineer_name:
            description['engineerName'] = self.engineer_name
        if self.engineer_date:
            description['engineerDate'] = model_utils.format_ts(self.engineer_date)
        if self.rebuilt_remarks:
            description['rebuiltRemarks'] = self.rebuilt_remarks
        if self.other_remarks:
            description['otherRemarks'] = self.other_remarks
        return description

    @classmethod
    def find_by_id(cls, description_id: int = None):
        """Return a description object by location ID."""
        description = None
        if description_id:
            description = cls.query.get(description_id)

        return description

    @classmethod
    def find_by_registration_id(cls, registration_id: int = None):
        """Return a list of description objects by registration id."""
        descriptions = None
        if registration_id:
            descriptions = cls.query.filter(MhrDescription.registration_id == registration_id) \
                                    .order_by(MhrDescription.id).all()

        return descriptions

    @classmethod
    def find_by_change_registration_id(cls, registration_id: int = None):
        """Return a description object by change registration id."""
        description = None
        if registration_id:
            description = cls.query.filter(MhrDescription.change_registration_id == registration_id).one_or_none()
        return description

    @staticmethod
    def create_from_json(json_data, registration_id: int = None):
        """Create a description object from a json schema object: map json to db."""
        # current_app.logger.info(json_data)
        base_info = json_data['baseInformation']
        # sections = new_info['sections']
        description: MhrDescription = MhrDescription(status_type=MhrStatusTypes.ACTIVE,
                                                     csa_number=json_data.get('csaNumber', None),
                                                     csa_standard=json_data.get('csaStandard', None),
                                                     number_of_sections=json_data.get('sectionCount', 0),
                                                     square_feet=json_data.get('squareFeet', None),
                                                     year_made=base_info.get('year', None),
                                                     circa='N',
                                                     manufacturer_name=json_data.get('manufacturer', ''),
                                                     make=base_info.get('make', None),
                                                     model=base_info.get('model', None),
                                                     engineer_name=json_data.get('engineerName', None),
                                                     rebuilt_remarks=json_data.get('rebuiltRemarks', None),
                                                     other_remarks=json_data.get('otherRemarks', None))
        if registration_id:
            description.registration_id = registration_id
            description.change_registration_id = registration_id
        if base_info.get('circa'):
            description.circa = 'Y'
        if json_data.get('engineerDate', None):
            description.engineer_date = model_utils.ts_from_iso_format(json_data.get('engineerDate'))

        return description
