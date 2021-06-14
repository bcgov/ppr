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
"""This module holds data for registry addresses."""
# import pycountry

from .db import db


class Address(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the registry addresses."""

    __tablename__ = 'addresses'

    id = db.Column('id', db.Integer, db.Sequence('address_id_seq'), primary_key=True)
    street = db.Column('street', db.String(50), nullable=False)  # index=True)
    street_additional = db.Column('street_additional', db.String(50), nullable=True)
    city = db.Column('city', db.String(40), nullable=False)
    region = db.Column('region', db.String(2),
                       db.ForeignKey('province_types.province_type'), nullable=True)
    postal_code = db.Column('postal_code', db.String(15), nullable=False)
    country = db.Column('country', db.String(2),
                        db.ForeignKey('country_types.country_type'), nullable=True)

    # parent keys

    # relationships
    party = db.relationship('Party', uselist=False, back_populates='address')
    client_code = db.relationship('ClientCode', uselist=False, back_populates='address')
    client_code_historical = db.relationship('ClientCodeHistorical', uselist=False, back_populates='address')
    # Relationships - ProvinceType
    province_type = db.relationship('ProvinceType', foreign_keys=[region],
                                    back_populates='address', cascade='all, delete', uselist=False)
    # Relationships - CountryType
    country_type = db.relationship('CountryType', foreign_keys=[country],
                                   back_populates='address', cascade='all, delete', uselist=False)

    def save(self):
        """Save the object to the database immediately. Only used for unit testing."""
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, address_id: int):  # -> Address:
        """Return the address matching the id."""
        address = None
        if address_id:
            address = cls.query.get(address_id)
        return address

    @property
    def json(self):
        """Return a dict of this object, with keys in JSON format."""
        address = {
            'street': self.street,
            'city': self.city,
            'region': self.region,
            'country': self.country,
            'postalCode': self.postal_code
        }
        if self.street_additional:
            address['streetAdditional'] = self.street_additional

        return address

    @staticmethod
    def create_from_dict(new_info: dict):
        """Create an address object from dict/json."""
        address = Address()

        address.street = new_info.get('street')
        address.street_additional = new_info.get('streetAdditional')
        address.city = new_info.get('city')
        address.region = new_info.get('region')
#        address.country = pycountry.countries.search_fuzzy(new_info.get('addressCountry'))[0].alpha_2
        address.country = new_info.get('country')
        address.postal_code = new_info.get('postalCode')

        return address

    @staticmethod
    def create_from_json(json_data):
        """Create an address object from a json Address schema object: map json to db."""
        address = Address()

        address.street = json_data['street'].strip().upper()
        if 'streetAdditional' in json_data:
            address.street_additional = json_data['streetAdditional'].strip().upper()
        address.city = json_data['city'].strip().upper()
        address.region = json_data['region'].strip().upper()
        address.country = json_data['country'].strip().upper()
        address.postal_code = json_data['postalCode'].strip().upper()

        return address
