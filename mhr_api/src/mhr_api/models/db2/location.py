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
"""This module holds data for legacy DB2 MHR location information."""
from flask import current_app
from mhr_api.exceptions import DatabaseException
from mhr_api.models import db, utils as model_utils
from mhr_api.models.db2 import address_utils
from mhr_api.models.type_tables import MhrLocationTypes
from mhr_api.models.ltsa_description import LtsaDescription
from mhr_api.utils.base import BaseEnum


LEGACY_STATUS_NEW = {
    'A': 'ACTIVE',
    'D': 'DRAFT',
    'H': 'HISTORICAL'
}


class Db2Location(db.Model):
    """This class manages all of the legacy DB2 MHR location information."""

    class StatusTypes(BaseEnum):
        """Render an Enum of the legacy document types."""

        ACTIVE = 'A'
        DRAFT = 'D'
        HISTORICAL = 'H'

    __bind_key__ = 'db2'
    __tablename__ = 'location'
    __allow_unmapped__ = True

    manuhome_id = db.mapped_column('MANHOMID', db.Integer, db.ForeignKey('manuhome.manhomid'), primary_key=True)
    location_id = db.mapped_column('LOCATNID', db.Integer, primary_key=True)
    status = db.mapped_column('status', db.String(1), nullable=False)
    reg_document_id = db.mapped_column('REGDOCID', db.String(8), nullable=False)
    can_document_id = db.mapped_column('CANDOCID', db.String(8), nullable=False)
    street_number = db.mapped_column('STNUMBER', db.String(6), nullable=False)
    street_name = db.mapped_column('STNAME', db.String(25), nullable=False)
    town_city = db.mapped_column('TOWNCITY', db.String(20), nullable=False)
    province = db.mapped_column('PROVINCE', db.String(2), nullable=False)
    area = db.mapped_column('BCAAAREA', db.String(2), nullable=False)
    jurisdiction = db.mapped_column('BCAAJURI', db.String(3), nullable=False)
    roll_number = db.mapped_column('BCAAROLL', db.String(20), nullable=False)
    park_name = db.mapped_column('MAHPNAME', db.String(40), nullable=False)
    park_pad = db.mapped_column('MAHPPAD', db.String(6), nullable=False)
    pid_number = db.mapped_column('PIDNUMB', db.String(9), nullable=False)
    lot = db.mapped_column('LOT', db.String(10), nullable=False)
    parcel = db.mapped_column('PARCEL', db.String(10), nullable=False)
    block = db.mapped_column('BLOCK', db.String(10), nullable=False)
    district_lot = db.mapped_column('DISTLOT', db.String(17), nullable=False)
    part_of = db.mapped_column('PARTOF', db.String(10), nullable=False)
    section = db.mapped_column('SECTION', db.String(10), nullable=False)
    township = db.mapped_column('TOWNSHIP', db.String(2), nullable=False)
    range = db.mapped_column('RANGE', db.String(2), nullable=False)
    meridian = db.mapped_column('MERIDIAN', db.String(3), nullable=False)
    land_district = db.mapped_column('LANDDIST', db.String(20), nullable=False)
    plan = db.mapped_column('PLAN', db.String(12), nullable=False)
    tax_certificate = db.mapped_column('TAXCERT', db.String(1), nullable=False)
    tax_certificate_date = db.mapped_column('TAXDATE', db.Date, nullable=False)
    leave_bc = db.mapped_column('LEAVEBC', db.String(1), nullable=False)
    except_plan = db.mapped_column('EXCPLAN', db.String(80), nullable=False)
    dealer_name = db.mapped_column('MHDEALER', db.String(60), nullable=False)
    additional_description = db.mapped_column('ADDDESC', db.String(80), nullable=False)

    # parent keys

    # Relationships
    registration = db.relationship('Db2Manuhome', foreign_keys=[manuhome_id],
                                   back_populates='locations', cascade='all, delete', uselist=False)
    ltsa: LtsaDescription = None

    def save(self):
        """Save the object to the database immediately."""
        try:
            db.session.add(self)
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB2 location.save exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    def strip(self):
        """Strip all string properties."""
        self.reg_document_id = self.reg_document_id.strip()
        self.can_document_id = self.can_document_id.strip()
        self.street_number = self.street_number.strip()
        self.street_name = self.street_name.strip()
        self.town_city = self.town_city.strip()
        self.area = self.area.strip()
        self.jurisdiction = self.jurisdiction.strip()
        self.roll_number = self.roll_number.strip()
        self.park_name = self.park_name.strip()
        self.pid_number = self.pid_number.strip()
        self.park_pad = self.park_pad.strip()
        self.lot = self.lot.strip()
        self.parcel = self.parcel.strip()
        self.block = self.block.strip()
        self.district_lot = self.district_lot.strip()
        self.part_of = self.part_of.strip()
        self.section = self.section.strip()
        self.meridian = self.meridian.strip()
        self.land_district = self.land_district.strip()
        self.plan = self.plan.strip()
        self.except_plan = self.except_plan.strip()
        self.dealer_name = self.dealer_name.strip()
        self.additional_description = self.additional_description.strip()
        self.range = self.range.strip()
        self.township = self.township.strip()

    @classmethod
    def find_by_manuhome_id(cls, manuhome_id: int):
        """Return the all locations matching the manuhome id."""
        locations = None
        if manuhome_id and manuhome_id > 0:
            try:
                locations = db.session.query(Db2Location).filter(Db2Location.manuhome_id == manuhome_id).all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2 location.find_by_manuhome_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if locations:
            for location in locations:
                location.strip()
                location.get_ltsa_description()
        return locations

    @classmethod
    def find_by_manuhome_id_active(cls, manuhome_id: int):
        """Return the active location matching the manuhome id."""
        location = None
        if manuhome_id and manuhome_id > 0:
            try:
                location = db.session.query(Db2Location) \
                    .filter(Db2Location.manuhome_id == manuhome_id, Db2Location.status == 'A').one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2 location.find_by_manuhome_id_active exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if location:
            location.strip()
            location.get_ltsa_description()
        return location

    @classmethod
    def find_by_doc_id(cls, reg_document_id: str):
        """Return the location matching the document id."""
        location = None
        if reg_document_id:
            try:
                location = db.session.query(Db2Location) \
                    .filter(Db2Location.reg_document_id == reg_document_id).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2 location.find_by_doc_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if location:
            location.strip()
            location.get_ltsa_description()
        return location

    def get_ltsa_description(self):
        """Try to get the ltsa legal description if a location pid exists."""
        if self.pid_number and len(self.pid_number) >= 9:
            self.ltsa = LtsaDescription.find_by_pid_number(self.pid_number)

    @property
    def json(self):
        """Return a dict of this object, with keys in JSON format."""
        location = {
            'locationId': self.location_id,
            'status': self.status,
            'registrationDocumentId': self.reg_document_id,
            'canDocumentId': self.can_document_id,
            'streetNumber': self.street_number,
            'streetName': self.street_name,
            'townCity': self.town_city,
            'province': self.province,
            'area': self.area,
            'jurisdiction': self.jurisdiction,
            'rollNumber': self.roll_number,
            'parkName': self.park_name,
            'pad': self.park_pad,
            'pidNumber': self.pid_number,
            'lot': self.lot,
            'parcel': self.parcel,
            'block': self.block,
            'districtLot': self.district_lot,
            'partOf': self.part_of,
            'section': self.section,
            'township': self.township,
            'range': self.range,
            'meridian': self.meridian,
            'landDistrict': self.land_district,
            'plan': self.plan,
            'taxCertificate': self.tax_certificate,
            'leaveProvince': self.leave_bc,
            'exceptionPlan': self.except_plan,
            'dealerName': self.dealer_name,
            'additionalDescription': self.additional_description
        }
        if self.tax_certificate_date:
            location['taxExpiryDate'] = model_utils.format_local_date(self.tax_certificate_date)
        if self.ltsa:
            location['legalDescription'] = self.ltsa.ltsa_description
        return location

    @property
    def registration_json(self):
        """Return a search registration dict of this object, with keys in JSON format."""
        street = self.street_number + ' ' + self.street_name
        if len(self.street_number) == 6:
            street = self.street_number + self.street_name
        location = {
            'parkName': self.park_name,
            'pad': self.park_pad,
            'status': LEGACY_STATUS_NEW.get(self.status),
            'address': {
                'street': street,
                'city': self.town_city,
                'region': self.province,
                'country': Db2Location.get_country(self.province),
                'postalCode': ''
            },
            'pidNumber': self.pid_number,
            'lot': self.lot,
            'parcel': self.parcel,
            'block': self.block,
            'districtLot': self.district_lot,
            'partOf': self.part_of,
            'section': self.section,
            'township': self.township,
            'range': self.range,
            'meridian': self.meridian,
            'landDistrict': self.land_district,
            'plan': self.plan,
            'taxCertificate': False,
            'leaveProvince': False,
            'exceptionPlan': self.except_plan,
            'dealerName': self.dealer_name,
            'additionalDescription': self.additional_description
        }
        # 1 location with an invalid province code:
        if self.province and self.province == 'XX' and self.town_city and self.town_city.find('WA USA') != -1:
            location['address']['region'] = 'WA'
            location['address']['country'] = 'US'
            location['address']['city'] = self.town_city.replace('WA USA', '').strip()
        if self.leave_bc == 'Y':
            location['leaveProvince'] = True
        if self.tax_certificate == 'Y':
            location['taxCertificate'] = True
        if self.tax_certificate_date:
            tax_date = model_utils.format_local_date(self.tax_certificate_date)
            if tax_date:
                location['taxExpiryDate'] = tax_date
        if self.ltsa:
            location['legalDescription'] = self.ltsa.ltsa_description
        return self.derive_location_type(location)

    @property
    def new_registration_json(self):
        """Return a dict of this object, with keys in JSON format."""
        self.strip()
        street = self.street_number + ' ' + self.street_name
        if len(self.street_number) == 6:
            street = self.street_number + self.street_name
        location = {
            'parkName': self.park_name,
            'pad': self.park_pad,
            'status': LEGACY_STATUS_NEW.get(self.status),
            'address': {
                'street': street,
                'city': self.town_city,
                'region': self.province,
                'country': Db2Location.get_country(self.province),
                'postalCode': ''
            },
            'pidNumber': self.pid_number,
            'lot': self.lot,
            'parcel': self.parcel,
            'block': self.block,
            'districtLot': self.district_lot,
            'partOf': self.part_of,
            'section': self.section,
            'township': self.township,
            'range': self.range,
            'meridian': self.meridian,
            'landDistrict': self.land_district,
            'plan': self.plan,
            'taxCertificate': False,
            'leaveProvince': False,
            'exceptionPlan': self.except_plan,
            'dealerName': self.dealer_name,
            'additionalDescription': self.additional_description
        }
        if self.leave_bc == 'Y':
            location['leaveProvince'] = True
        if self.tax_certificate == 'Y':
            location['taxCertificate'] = True
        if self.tax_certificate_date:
            tax_date = model_utils.format_local_date(self.tax_certificate_date)
            if tax_date:
                location['taxExpiryDate'] = tax_date
        return self.derive_location_type(location)

    def derive_location_type(self, location: dict) -> dict:
        """Add the locationType using the same logic as data migration."""
        if self.dealer_name:
            location['locationType'] = MhrLocationTypes.MANUFACTURER
        elif self.park_name:
            location['locationType'] = MhrLocationTypes.MH_PARK
        elif self.additional_description and \
                (self.additional_description.find('BAND') > -1 or
                 self.additional_description.find('RESERVE') > -1 or
                 self.additional_description.find('INDIAN') > -1):
            location['locationType'] = MhrLocationTypes.RESERVE
        else:
            location['locationType'] = MhrLocationTypes.OTHER
        return location

    @staticmethod
    def create_from_dict(new_info: dict):
        """Create a location object from dict/json."""
        location = Db2Location(status=new_info.get('status', ''),
                               reg_document_id=new_info.get('registrationDocumentId', ''),
                               can_document_id=new_info.get('canDocumentId', ''),
                               street_number=new_info.get('streetNumber', ''),
                               street_name=new_info.get('streetName', ''),
                               town_city=new_info.get('townCity', ''),
                               province=new_info.get('province', ''),
                               area=new_info.get('area', ''),
                               jurisdiction=new_info.get('jurisdiction', ''),
                               roll_number=new_info.get('rollNumber', ''),
                               park_name=new_info.get('parkName', ''),
                               park_pad=new_info.get('pad', ''),
                               pid_number=new_info.get('pidNumber', ''),
                               lot=new_info.get('lot', ''),
                               parcel=new_info.get('parcel', ''),
                               block=new_info.get('block', ''),
                               district_lot=new_info.get('districtLot', ''),
                               part_of=new_info.get('partOf', ''),
                               section=new_info.get('section', ''),
                               township=new_info.get('township', ''),
                               range=new_info.get('range', ''),
                               meridian=new_info.get('meridian', ''),
                               land_district=new_info.get('landDistrict', ''),
                               plan=new_info.get('plan', ''),
                               tax_certificate=new_info.get('taxCertificate', ''),
                               leave_bc=new_info.get('leaveProvince', ''),
                               except_plan=new_info.get('exceptionPlan', ''),
                               dealer_name=new_info.get('dealerName', ''),
                               additional_description=new_info.get('additionalDescription', ''))

        if new_info.get('taxExpiryDate', None):
            tax_date: str = new_info.get('taxExpiryDate')
            location.tax_certificate_date = model_utils.date_from_iso_format(tax_date[0:10])
        return location

    @staticmethod
    def create_from_registration(registration, reg_json, update: bool = False):
        """Create a new location object from a new MH registration."""
        new_info = reg_json.get('location') if not update else reg_json.get('newLocation')
        address = new_info['address']
        street = str(address['street'])
        street_info = street.split(' ')
        street_num = street_info[0]
        if len(street_num) < 7:
            street_name = street[len(street_num):].strip()
        else:  # Adjust; db table column length is 6.
            street_num = street[0:6]
            street_name = street[6:]
        additional_desc = ''
        if new_info.get('locationType') and new_info.get('locationType') == MhrLocationTypes.RESERVE:
            if new_info.get('bandName'):
                additional_desc += str(new_info.get('bandName')).strip().upper() + ' '
            if new_info.get('reserveNumber'):
                additional_desc += str(new_info.get('reserveNumber')).strip() + ' '
        if new_info.get('additionalDescription'):
            additional_desc += new_info.get('additionalDescription')
        if additional_desc:
            additional_desc = additional_desc[0:80]
        location = Db2Location(manuhome_id=registration.id,
                               location_id=1,
                               status=Db2Location.StatusTypes.ACTIVE,
                               reg_document_id=reg_json.get('documentId', ''),
                               can_document_id='',
                               street_number=street_num,
                               street_name=street_name[0:25],
                               town_city=str(address['city'])[0:20],
                               province=address.get('region', ''),
                               area='',
                               jurisdiction='',
                               roll_number='',
                               park_name=new_info.get('parkName', ''),
                               park_pad=new_info.get('pad', ''),
                               pid_number=new_info.get('pidNumber', ''),
                               lot=new_info.get('lot', ''),
                               parcel=new_info.get('parcel', ''),
                               block=new_info.get('block', ''),
                               district_lot=new_info.get('districtLot', ''),
                               part_of=new_info.get('partOf', ''),
                               section=new_info.get('section', ''),
                               township=new_info.get('township', ''),
                               range=new_info.get('range', ''),
                               meridian=new_info.get('meridian', ''),
                               land_district=new_info.get('landDistrict', ''),
                               plan=new_info.get('plan', ''),
                               except_plan=new_info.get('exceptionPlan', ''),
                               dealer_name=str(new_info.get('dealerName', ''))[0:60],
                               additional_description=additional_desc,
                               leave_bc='N',
                               tax_certificate='N')
        if new_info.get('leaveProvince'):
            location.leave_bc = 'Y'
        if new_info.get('taxCertificate'):
            location.tax_certificate = 'Y'
        if new_info.get('taxExpiryDate', None):
            tax_date: str = new_info.get('taxExpiryDate')
            location.tax_certificate_date = model_utils.date_from_iso_format(tax_date[0:10])
        else:
            location.tax_certificate_date = model_utils.date_from_iso_format('0001-01-01')
        return location

    @staticmethod
    def create_from_json(json_data):
        """Create a location object from a json location schema object: map json to db."""
        location = Db2Location.create_from_dict(json_data)

        return location

    @staticmethod
    def get_country(region: str) -> str:
        """Try to derive a country code from a region code."""
        if not region:
            return ''
        if address_utils.PROVINCE_CODES.find(region) > 0:
            return address_utils.COUNTRY_CA
        if address_utils.STATE_CODES.find(region) > 0 or region == address_utils.COUNTRY_US:
            return address_utils.COUNTRY_US
        return ''
