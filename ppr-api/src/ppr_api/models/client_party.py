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
"""This module holds data for client parties (reusable registering parties, secured parties).

Currently the API only selects client parties. There are no create, update, delete requests.
"""
from __future__ import annotations

from .db import db
from .address import Address  # noqa: F401 pylint: disable=unused-import


class ClientParty(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains client party information (registering and secured parties)."""

    __versioned__ = {}
    __tablename__ = 'client_party'

    client_party_id = db.Column('client_party_id', db.Integer,
                                db.Sequence('client_party_id_seq'), primary_key=True)
    party_type_cd = db.Column('party_type_cd', db.String(3))
    # , db.ForeignKey('party_type.party_type_cd'), nullable=False)
    account_id = db.Column('account_id', db.String(20), nullable=False)
    # contact info
    contact_name = db.Column('contact_name', db.String(100), nullable=False)
    contact_area_cd = db.Column('contact_area_cd', db.String(3), nullable=True)
    contact_phone_number = db.Column('contact_phone_number', db.String(15), nullable=False)
#    contact_email_id = db.Column('contact_email_id', db.String(250), nullable=True)
    # party business name
    business_name = db.Column('party_name', db.String(150), index=True, nullable=True)
    email_id = db.Column('email_id', db.String(250), nullable=True)

    user_id = db.Column('user_id', db.String(7), nullable=True)
    last_update = db.Column('last_update', db.String(8), nullable=True)
    last_update_time = db.Column('last_update_time', db.String(8), nullable=True)
    bcol_account_number = db.Column('bcol_account_nbr', db.String(6), nullable=True)
    history_count = db.Column('history_count', db.Integer, nullable=True)
    branch_count = db.Column('branch_count', db.Integer, nullable=True)

    # parent keys
    address_id = db.Column('address_id', db.Integer, db.ForeignKey('address_ppr.address_id'), nullable=False)

    # Relationships - Address
    address = db.relationship('Address', foreign_keys=[address_id], uselist=False,
                              back_populates='client_party', cascade='all, delete')
    party = db.relationship('Party', uselist=False, back_populates='client_party')

    @property
    def json(self) -> dict:
        """Return the client party as a json object."""
        party = {
            'code': str(self.client_party_id),
            'contact': {
                'name': self.contact_name,
                'phoneNumber': self.contact_phone_number
            }
        }

        if self.contact_area_cd:
            party['contact']['areaCode'] = self.contact_area_cd
#        if self.contact_email_id:
#            party['contact']['emailAddress'] = self.contact_email_id
        if self.email_id:
            party['emailAddress'] = self.email_id
        if self.business_name:
            party['businessName'] = self.business_name

        if self.address:
            cp_address = self.address.json
            party['address'] = cp_address

        return party

    @classmethod
    def find_by_code(cls, code: str = None):
        """Return a client party json object by client code."""
        party = None
        if code:
            party = cls.query.get(int(code))

        if party:
            return party.json

        return party
