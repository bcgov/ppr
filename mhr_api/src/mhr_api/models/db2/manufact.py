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
"""This module holds data for legacy DB2 MHR manufacturer information."""
from flask import current_app

from mhr_api.exceptions import DatabaseException
from mhr_api.models import db, utils as model_utils


class Db2Manufact(db.Model):
    """This class manages all of the legacy DB2 MHR location information."""

    __bind_key__ = 'db2'
    __tablename__ = 'manufact'

    id = db.Column('MANUFAID', db.Integer, primary_key=True)
    bcol_account_number = db.Column('BCOLACCT', db.String(6), nullable=False)
    dealer_name = db.Column('MHDEALER', db.String(60), nullable=False)
    submitting_party_name = db.Column('SUBPNAME', db.String(40), nullable=False)
    submitting_party_phone = db.Column('SUBPFONE', db.String(10), nullable=False)
    submitting_party_address = db.Column('SUBPADDR', db.String(160), nullable=False)
    owner_name = db.Column('OWNRNAME', db.String(70), nullable=False)
    owner_phone_number = db.Column('OWNRFONE', db.String(10), nullable=False)
    owner_address = db.Column('OWNRADDR', db.String(160), nullable=False)
    owner_postal_code = db.Column('OWNRPOCO', db.String(10), nullable=False)
    street_number = db.Column('STNUMBER', db.String(6), nullable=False)
    street_name = db.Column('STNAME', db.String(25), nullable=False)
    town_city = db.Column('TOWNCITY', db.String(20), nullable=False)
    province = db.Column('PROVINCE', db.String(2), nullable=False)
    manufacturer_name = db.Column('MANUNAME', db.String(65), nullable=False)

    # parent keys

    # Relationships

    def save(self):
        """Save the object to the database immediately. Only used for unit testing."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB2 manufact.save exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    def strip(self):
        """Strip all string properties."""
        self.bcol_account_number = self.bcol_account_number.strip()
        self.dealer_name = self.dealer_name.strip()
        self.submitting_party_name = self.submitting_party_name.strip()
        self.submitting_party_phone = self.submitting_party_phone.strip()
        self.submitting_party_address = self.submitting_party_address.strip()
        self.owner_name = self.owner_name.strip()
        self.owner_phone_number = self.owner_phone_number.strip()
        self.owner_address = self.owner_address.strip()
        self.owner_postal_code = self.owner_postal_code.strip()
        self.street_number = self.street_number.strip()
        self.street_name = self.street_name.strip()
        self.town_city = self.town_city.strip()
        self.manufacturer_name = self.manufacturer_name.strip()

    @classmethod
    def find_by_id(cls, id: int):
        """Return the manufacturer matching the manufacturer id."""
        manfacturer = None
        if id and id > 0:
            try:
                manfacturer = cls.query.get(id)
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2 manufact.find_by_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if manfacturer:
            manfacturer.strip()
        return manfacturer

    @classmethod
    def find_by_bcol_account(cls, bcol_account_num: str):
        """Return the manufacturers matching the BCOL account number."""
        manufacturers = None
        if bcol_account_num:
            try:
                manufacturers = cls.query.filter(Db2Manufact.bcol_account_number == bcol_account_num).all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2 manufact.find_by_bcol_account exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if manufacturers:
            for manufacturer in manufacturers:
                manufacturer.strip()
        return manufacturers

    @property
    def json(self):
        """Return a dict of this object, with keys in JSON format."""
        manufacturer = {
            'bcolAccountNumber': self.bcol_account_number,
            'dealerName': self.dealer_name,
            'submittingParty': {
                'businessName': self.submitting_party_name,
                'phoneNumber': self.submitting_party_phone,
                'address': model_utils.get_address_from_db2_manufact(self.submitting_party_address)
            },
            'owner': {
                'businessName': self.owner_name,
                'phoneNumber': self.owner_phone_number,
                'address': {
                    'street': self.street_number + ' ' + self.street_name,
                    'city': self.town_city,
                    'region': self.province,
                    'country': model_utils.get_country_from_province(self.province),
                    'postalCode': self.owner_postal_code
                }
            },
            'manufacturerName': self.manufacturer_name
        }
        if not self.owner_postal_code:
            pos = len(self.owner_address) - 9
            p_code = self.owner_address[pos:].strip()
            if p_code[1:2] == ' ':
                p_code = p_code[2:]
            manufacturer['owner']['address']['postalCode'] = p_code
        return manufacturer

    @staticmethod
    def create_from_dict(new_info: dict):
        """Create a manufacturer object from dict/json."""
        manufacturer = Db2Manufact(bcol_account_number=new_info.get('bcolAccountNumber', ''),
                                   dealer_name=new_info.get('dealerName', ''),
                                   submitting_party_name=new_info.get('submittingPartyName', ''),
                                   submitting_party_phone=new_info.get('submittingPartyPhone', ''),
                                   submitting_party_address=new_info.get('submittingPartyAddress', ''),
                                   owner_name=new_info.get('ownerName', ''),
                                   owner_phone_number=new_info.get('ownerPhoneNumber', ''),
                                   owner_address=new_info.get('ownerAddress', ''),
                                   owner_postal_code=new_info.get('ownerPostalCode', ''),
                                   street_number=new_info.get('streetNumber', ''),
                                   street_name=new_info.get('streetName', ''),
                                   town_city=new_info.get('townCity', ''),
                                   province=new_info.get('province', ''),
                                   manufacturer_name=new_info.get('manufacturerName', ''))
        return manufacturer

    @staticmethod
    def create_from_json(json_data):
        """Create a manufacturer object from a json manufacturer schema object: map json to db."""
        manufacturer = Db2Manufact.create_from_dict(json_data)
        return manufacturer
