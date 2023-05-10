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
"""This module holds data for legacy DB2 MHR description information."""
from flask import current_app

from mhr_api.exceptions import DatabaseException
from mhr_api.models import db, utils as model_utils, Db2Cmpserno
from mhr_api.utils.base import BaseEnum


LEGACY_STATUS_NEW = {
    'A': 'ACTIVE',
    'D': 'DRAFT',
    'C': 'HISTORICAL'
}


class Db2Descript(db.Model):
    """This class manages all of the legacy DB2 MHR description information."""

    class StatusTypes(BaseEnum):
        """Render an Enum of the legacy document types."""

        ACTIVE = 'A'
        DRAFT = 'D'
        HISTORICAL = 'H'

    __bind_key__ = 'db2'
    __tablename__ = 'descript'

    # manuhome_id = db.Column('MANHOMID', db.Integer, primary_key=True)
    manuhome_id = db.Column('MANHOMID', db.Integer, db.ForeignKey('manuhome.manhomid'), primary_key=True)
    description_id = db.Column('DESCRNID', db.Integer, primary_key=True)
    status = db.Column('status', db.String(1), nullable=False)
    reg_document_id = db.Column('REGDOCID', db.String(8), nullable=False)
    can_document_id = db.Column('CANDOCID', db.String(8), nullable=False)
    csa_number = db.Column('CSANUMBR', db.String(10), nullable=False)
    csa_standard = db.Column('CSASTAND', db.String(4), nullable=False)
    section_count = db.Column('NUMBSECT', db.Integer, nullable=False)
    square_feet = db.Column('SQARFEET', db.Integer, nullable=False)
    year_made = db.Column('YEARMADE', db.String(4), nullable=False)
    circa = db.Column('CIRCA', db.String(1), nullable=False)
    serial_number_1 = db.Column('SERNUMB1', db.String(20), nullable=False)
    serial_number_2 = db.Column('SERNUMB2', db.String(20), nullable=False)
    serial_number_3 = db.Column('SERNUMB3', db.String(20), nullable=False)
    serial_number_4 = db.Column('SERNUMB4', db.String(20), nullable=False)
    length_feet_1 = db.Column('LENGTH1', db.Integer, nullable=False)
    length_feet_2 = db.Column('LENGTH2', db.Integer, nullable=False)
    length_feet_3 = db.Column('LENGTH3', db.Integer, nullable=False)
    length_feet_4 = db.Column('LENGTH4', db.Integer, nullable=False)
    length_inches_1 = db.Column('LENGIN1', db.Integer, nullable=False)
    length_inches_2 = db.Column('LENGIN2', db.Integer, nullable=False)
    length_inches_3 = db.Column('LENGIN3', db.Integer, nullable=False)
    length_inches_4 = db.Column('LENGIN4', db.Integer, nullable=False)
    width_feet_1 = db.Column('WIDTH1', db.Integer, nullable=False)
    width_feet_2 = db.Column('WIDTH2', db.Integer, nullable=False)
    width_feet_3 = db.Column('WIDTH3', db.Integer, nullable=False)
    width_feet_4 = db.Column('WIDTH4', db.Integer, nullable=False)
    width_inches_1 = db.Column('WIDIN1', db.Integer, nullable=False)
    width_inches_2 = db.Column('WIDIN2', db.Integer, nullable=False)
    width_inches_3 = db.Column('WIDIN3', db.Integer, nullable=False)
    width_inches_4 = db.Column('WIDIN4', db.Integer, nullable=False)
    engineer_date = db.Column('ENGIDATE', db.Date, nullable=False)
    engineer_name = db.Column('ENGINAME', db.String(30), nullable=False)
    manufacturer_name = db.Column('MANUNAME', db.String(65), nullable=False)
    make_model = db.Column('MAKEMODL', db.String(65), nullable=False)
    rebuilt_remarks = db.Column('REBUILTR', db.String(280), nullable=False)
    other_remarks = db.Column('OTHERREM', db.String(140), nullable=False)

    # parent keys

    # Relationships
    registration = db.relationship('Db2Manuhome', foreign_keys=[manuhome_id],
                                   back_populates='descriptions', cascade='all, delete', uselist=False)

    compressed_keys = []

    def save(self):
        """Save the object to the database immediately."""
        try:
            db.session.add(self)
            if self.compressed_keys:
                for key in self.compressed_keys:
                    key.save()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB2 descript.save exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    def strip(self):
        """Strip all string properties."""
        self.reg_document_id = self.reg_document_id.strip()
        self.can_document_id = self.can_document_id.strip()
        self.csa_number = self.csa_number.strip()
        self.csa_standard = self.csa_standard.strip()
        self.serial_number_1 = self.serial_number_1.strip()
        self.serial_number_2 = self.serial_number_2.strip()
        self.serial_number_3 = self.serial_number_3.strip()
        self.serial_number_4 = self.serial_number_4.strip()
        self.engineer_name = self.engineer_name.strip()
        self.manufacturer_name = self.manufacturer_name.strip()
        self.make_model = self.make_model.strip()
        self.rebuilt_remarks = self.rebuilt_remarks.strip()
        self.other_remarks = self.other_remarks.strip()

    @classmethod
    def find_by_manuhome_id(cls, manuhome_id: int):
        """Return the all descriptions matching the manuhome id."""
        descriptions = None
        if manuhome_id and manuhome_id > 0:
            try:
                descriptions = cls.query.filter(Db2Descript.manuhome_id == manuhome_id).all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2 descript.find_by_manuhome_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)

        if descriptions:
            for descript in descriptions:
                descript.strip()
        return descriptions

    @classmethod
    def find_by_manuhome_id_active(cls, manuhome_id: int):
        """Return the active description matching the manuhome id."""
        descript = None
        if manuhome_id and manuhome_id > 0:
            try:
                descript = cls.query.filter(Db2Descript.manuhome_id == manuhome_id,
                                            Db2Descript.status == 'A').one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2 descript.find_by_manuhome_id_active exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if descript:
            descript.strip()
        return descript

    @classmethod
    def find_by_doc_id(cls, reg_document_id: str):
        """Return the description matching the document id."""
        descript = None
        if reg_document_id:
            try:
                descript = cls.query.filter(Db2Descript.reg_document_id == reg_document_id).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2 descript.find_by_doc_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if descript:
            descript.strip()
        return descript

    @property
    def json(self):
        """Return a dict of this object, with keys in JSON format."""
        description = {
            'descriptionId': self.description_id,
            'status': self.status,
            'registrationDocumentId': self.reg_document_id,
            'canDocumentId': self.can_document_id,
            'csaNumber': self.csa_number,
            'csaStandard': self.csa_standard,
            'sectionCount': self.section_count,
            'squareFeet': self.square_feet,
            'year': self.year_made,
            'circa': self.circa,
            'serialNumber1': self.serial_number_1,
            'lengthFeet1': self.length_feet_1,
            'lengthInches1': self.length_inches_1,
            'widthFeet1': self.width_feet_1,
            'widthInches1': self.width_inches_1,
            'manufacturer': self.manufacturer_name,
            'makeModel': self.make_model,
            'engineerName': self.engineer_name,
            'rebuiltRemarks': self.rebuilt_remarks,
            'otherRemarks': self.other_remarks
        }
        if self.section_count > 1:
            description['serialNumber2'] = self.serial_number_2
            description['lengthFeet2'] = self.length_feet_2
            description['lengthInches2'] = self.length_inches_2
            description['widthFeet2'] = self.width_feet_2
            description['widthInches2'] = self.width_inches_2
        if self.section_count > 2:
            description['serialNumber3'] = self.serial_number_3
            description['lengthFeet3'] = self.length_feet_3
            description['lengthInches3'] = self.length_inches_3
            description['widthFeet3'] = self.width_feet_3
            description['widthInches3'] = self.width_inches_3
        if self.section_count > 3:
            description['serialNumber4'] = self.serial_number_4
            description['lengthFeet4'] = self.length_feet_4
            description['lengthInches4'] = self.length_inches_4
            description['widthFeet4'] = self.width_feet_4
            description['widthInches4'] = self.width_inches_4
        if self.engineer_date and self.engineer_date.year > 1900:
            description['engineerDate'] = model_utils.format_local_date(self.engineer_date)
        return description

    @property
    def registration_json(self):
        """Return a search registration dict of this object, with keys in JSON format."""
        self.strip()
        sections = [
            {
                'serialNumber': self.serial_number_1,
                'lengthFeet': self.length_feet_1,
                'lengthInches': self.length_inches_1,
                'widthFeet': self.width_feet_1,
                'widthInches': self.width_inches_1
            }
        ]
        if self.section_count > 1 and self.serial_number_2:
            section = {
                'serialNumber': self.serial_number_2,
                'lengthFeet': self.length_feet_2,
                'lengthInches': self.length_inches_2,
                'widthFeet': self.width_feet_2,
                'widthInches': self.width_inches_2
            }
            sections.append(section)
        if self.section_count > 2 and self.serial_number_3:
            section = {
                'serialNumber': self.serial_number_3,
                'lengthFeet': self.length_feet_3,
                'lengthInches': self.length_inches_3,
                'widthFeet': self.width_feet_3,
                'widthInches': self.width_inches_3
            }
            sections.append(section)
        if self.section_count > 3 and self.serial_number_4:
            section = {
                'serialNumber': self.serial_number_4,
                'lengthFeet': self.length_feet_4,
                'lengthInches': self.length_inches_4,
                'widthFeet': self.width_feet_4,
                'widthInches': self.width_inches_4
            }
            sections.append(section)

        description = {
            'manufacturer': self.manufacturer_name,
            'baseInformation': {
                'year': self.year_made,
                'make': self.make_model,
                'model': ''
            },
            'sectionCount': self.section_count,
            'sections': sections,
            'csaNumber': self.csa_number,
            'csaStandard': self.csa_standard,
            'engineerName': self.engineer_name,
            'rebuiltRemarks': self.rebuilt_remarks,
            'otherRemarks': self.other_remarks
        }
        if self.engineer_date and self.engineer_date.year > 1900:
            description['engineerDate'] = model_utils.format_local_date(self.engineer_date)
        if self.circa == '?':
            description['baseInformation']['circa'] = True
        return description

    @staticmethod
    def create_from_dict(new_info: dict):
        """Create a description object from dict/json."""
        descript = Db2Descript(status=new_info.get('status', ''),
                               reg_document_id=new_info.get('registrationDocumentId', ''),
                               can_document_id=new_info.get('canDocumentId', ''),
                               csa_number=new_info.get('csaNumber', ''),
                               csa_standard=new_info.get('csaStandard', ''),
                               section_count=new_info.get('sectionCount', 0),
                               square_feet=new_info.get('squareFeet', 0),
                               year_made=new_info.get('year', ''),
                               circa=new_info.get('circa', ''),
                               manufacturer_name=new_info.get('manufacturer', ''),
                               make_model=new_info.get('make', ''),
                               engineer_name=new_info.get('engineerName', ''),
                               rebuilt_remarks=new_info.get('rebuiltRemarks', ''),
                               other_remarks=new_info.get('otherRemarks', ''))

        if descript.section_count > 0:
            descript.serial_number_1 = new_info['serialNumber1']
            descript.length_feet_1 = new_info['lengthFeet1']
            descript.length_inches_1 = new_info.get('lengthInches1', 0)
            descript.width_feet_1 = new_info['widthFeet1']
            descript.width_inches_1 = new_info.get('widthInches1', 0)
        if descript.section_count > 1:
            descript.serial_number_2 = new_info['serialNumber2']
            descript.length_feet_2 = new_info['lengthFeet2']
            descript.length_inches_2 = new_info.get('lengthInches2', 0)
            descript.width_feet_2 = new_info['widthFeet2']
            descript.width_inches_2 = new_info.get('widthInches2', 0)
        if descript.section_count > 2:
            descript.serial_number_3 = new_info['serialNumber3']
            descript.length_feet_3 = new_info['lengthFeet3']
            descript.length_inches_3 = new_info.get('lengthInches3', 0)
            descript.width_feet_3 = new_info['widthFeet3']
            descript.width_inches_3 = new_info.get('widthInches3', 0)
        if descript.section_count > 3:
            descript.serial_number_4 = new_info['serialNumber4']
            descript.length_feet_4 = new_info['lengthFeet4']
            descript.length_inches_4 = new_info.get('lengthInches4', 0)
            descript.width_feet_4 = new_info['widthFeet4']
            descript.width_inches_4 = new_info.get('widthInches4', 0)
        if new_info.get('engineerDate', None):
            date_val: str = str(new_info.get('engineerDate'))[0:10]
            descript.engineer_date = model_utils.date_from_iso_format(date_val)

        return descript

    @staticmethod
    def create_from_registration(registration, reg_json):
        """Create a new description object from a new MH registration."""
        new_info = reg_json['description']
        base_info = new_info['baseInformation']
        sections = new_info['sections']
        make_model: str = base_info.get('make', '') + ' ' + base_info.get('model', ' ')
        descript = Db2Descript(manuhome_id=registration.id,
                               description_id=1,
                               status=Db2Descript.StatusTypes.ACTIVE,
                               reg_document_id=reg_json.get('documentId', ''),
                               can_document_id='',
                               csa_number=new_info.get('csaNumber', ''),
                               csa_standard=new_info.get('csaStandard', ''),
                               section_count=new_info.get('sectionCount', 0),
                               square_feet=new_info.get('squareFeet', 0),
                               year_made=str(base_info.get('year', '')),
                               circa=' ',
                               manufacturer_name=new_info.get('manufacturer', ''),
                               make_model=make_model[0:64],
                               engineer_name=new_info.get('engineerName', ''),
                               rebuilt_remarks=new_info.get('rebuiltRemarks', ''),
                               other_remarks=new_info.get('otherRemarks', ''))
        descript.compressed_keys = []
        if base_info.get('circa'):
            descript.circa = '?'
        if descript.section_count > 0 and sections:
            section = sections[0]
            descript.serial_number_1 = section['serialNumber']
            descript.length_feet_1 = section['lengthFeet']
            descript.length_inches_1 = section.get('lengthInches', 0)
            descript.width_feet_1 = section['widthFeet']
            descript.width_inches_1 = section.get('widthInches', 0)
            key = Db2Cmpserno.create_from_registration(registration.id,
                                                       1,
                                                       model_utils.get_serial_number_key(descript.serial_number_1))
            descript.compressed_keys.append(key)
        if descript.section_count > 1 and len(sections) > 1:
            section = sections[1]
            descript.serial_number_2 = section['serialNumber']
            descript.length_feet_2 = section['lengthFeet']
            descript.length_inches_2 = section.get('lengthInches', 0)
            descript.width_feet_2 = section['widthFeet']
            descript.width_inches_2 = section.get('widthInches', 0)
            key = Db2Cmpserno.create_from_registration(registration.id,
                                                       2,
                                                       model_utils.get_serial_number_key(descript.serial_number_2))
            descript.compressed_keys.append(key)
        else:
            descript.serial_number_2 = ''
            descript.length_feet_2 = 0
            descript.length_inches_2 = 0
            descript.width_feet_2 = 0
            descript.width_inches_2 = 0
        if descript.section_count > 2 and len(sections) > 2:
            section = sections[2]
            descript.serial_number_3 = section['serialNumber']
            descript.length_feet_3 = section['lengthFeet']
            descript.length_inches_3 = section.get('lengthInches', 0)
            descript.width_feet_3 = section['widthFeet']
            descript.width_inches_3 = section.get('widthInches', 0)
            key = Db2Cmpserno.create_from_registration(registration.id,
                                                       3,
                                                       model_utils.get_serial_number_key(descript.serial_number_3))
            descript.compressed_keys.append(key)
        else:
            descript.serial_number_3 = ''
            descript.length_feet_3 = 0
            descript.length_inches_3 = 0
            descript.width_feet_3 = 0
            descript.width_inches_3 = 0
        if descript.section_count > 3 and len(sections) > 3:
            section = sections[3]
            descript.serial_number_4 = section['serialNumber']
            descript.length_feet_4 = section['lengthFeet']
            descript.length_inches_4 = section.get('lengthInches', 0)
            descript.width_feet_4 = section['widthFeet']
            descript.width_inches_4 = section.get('widthInches', 0)
            key = Db2Cmpserno.create_from_registration(registration.id,
                                                       4,
                                                       model_utils.get_serial_number_key(descript.serial_number_4))
            descript.compressed_keys.append(key)
        else:
            descript.serial_number_4 = ''
            descript.length_feet_4 = 0
            descript.length_inches_4 = 0
            descript.width_feet_4 = 0
            descript.width_inches_4 = 0
        if new_info.get('engineerDate', None):
            date_val: str = str(new_info.get('engineerDate'))[0:10]
            descript.engineer_date = model_utils.date_from_iso_format(date_val)
        else:
            descript.engineer_date = model_utils.date_from_iso_format('0001-01-01')
        return descript

    @staticmethod
    def create_from_json(json_data):
        """Create a description object from a json description schema object: map json to db."""
        descript = Db2Descript.create_from_dict(json_data)

        return descript
