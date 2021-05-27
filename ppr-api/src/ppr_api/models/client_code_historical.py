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
"""This module holds data for maintaining client party address and name change history.

Client parties are reusable registering parties and secured parties.
"""
from __future__ import annotations

from enum import Enum

# Needed by the SQLAlchemy relationship
from .address import Address  # noqa: F401 pylint: disable=unused-import
from .db import db


class ClientCodeHistorical(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains client party information: history of name and address changes."""

    class HistoricalTypes(Enum):
        """Render an Enum of the historical types."""

        ADDRESS = 'A'
        BOTH = 'B'
        NAME = 'N'

    __tablename__ = 'client_codes_historical'
    id = db.Column('id', db.Integer, db.Sequence('historical_head_id_seq'), primary_key=True)
    head_id = db.Column('head_id', db.Integer, index=True, nullable=False)
    name = db.Column('name', db.String(150), index=True, nullable=False)
    historical_type_cd = db.Column('historical_type_cd', db.String(1), nullable=False)
    bconline_account = db.Column('bconline_account', db.Integer, nullable=True)
    # contact info
    contact_name = db.Column('contact_name', db.String(100), nullable=False)
    contact_area_cd = db.Column('contact_area_cd', db.String(3), nullable=True)
    contact_phone_number = db.Column('contact_phone_number', db.String(15), nullable=False)
    email_id = db.Column('email_addresss', db.String(250), nullable=True)
    user_id = db.Column('user_id', db.String(7), nullable=True)
    date_ts = db.Column('date_ts', db.DateTime, nullable=True)

    # parent keys
    branch_id = db.Column('branch_id', db.Integer, db.ForeignKey('client_codes.id'), nullable=False)
    address_id = db.Column('address_id', db.Integer, db.ForeignKey('addresses.id'), nullable=False)
    users_id = db.Column('users_id', db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    address = db.relationship('Address', foreign_keys=[address_id], uselist=False,
                              back_populates='client_code_historical', cascade='all, delete')
    client_code = db.relationship('ClientCode', foreign_keys=[branch_id], uselist=False,
                                  back_populates='client_code_historical')

    @property
    def json(self) -> dict:
        """Return the client party branch as a json object."""
        party = {
            'code': str(self.branch_id),
            'businessName': self.name,
            'contact': {
                'name': self.contact_name,
                'phoneNumber': self.contact_phone_number
            }
        }
        if self.contact_area_cd:
            party['contact']['areaCode'] = self.contact_area_cd
        if self.email_id:
            party['emailAddress'] = self.email_id
        if self.address:
            cp_address = self.address.json
            party['address'] = cp_address

        return party

    @classmethod
    def find_by_id(cls, historical_id: int = None):
        """Return a code historical json object by primary key."""
        party = None
        if historical_id:
            party = db.session.query(ClientCodeHistorical).\
                                     filter(ClientCodeHistorical.id == historical_id).\
                                     one_or_none()

        if party:
            return party.json

        return party
