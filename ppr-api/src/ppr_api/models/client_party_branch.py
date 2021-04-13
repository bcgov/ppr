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
"""This module holds data for client party branck (reusable registering parties, secured parties).

Currently the API only selects client parties. There are no create, update, delete requests.
"""
from __future__ import annotations

# Needed by the SQLAlchemy relationship
from .address import Address  # noqa: F401 pylint: disable=unused-import
from .db import db


class ClientPartyBranch(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains client party information (registering and secured parties)."""

    __tablename__ = 'client_party_branch'

    client_party_branch_id = db.Column('client_party_branch_id', db.Integer, primary_key=True, nullable=False)
    bconline_account = db.Column('bconline_account', db.Integer, nullable=True)
    # contact info
    contact_name = db.Column('contact_name', db.String(100), nullable=False)
    contact_area_cd = db.Column('contact_area_cd', db.String(3), nullable=True)
    contact_phone_number = db.Column('contact_phone_number', db.String(15), nullable=False)
    email_id = db.Column('email_id', db.String(250), nullable=True)
    user_id = db.Column('user_id', db.String(7), nullable=True)
    update_ts = db.Column('update_ts', db.DateTime, nullable=True)

    # parent keys
    client_party_id = db.Column('client_party_id', db.Integer,
                                db.ForeignKey('client_party.client_party_id'), primary_key=True, nullable=False)
    address_id = db.Column('address_id', db.Integer, db.ForeignKey('address_ppr.address_id'), nullable=False)
    id = db.Column('id', db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    address = db.relationship('Address', foreign_keys=[address_id], uselist=False,
                              back_populates='client_party_branch', cascade='all, delete')
    client_party = db.relationship('ClientParty', foreign_keys=[client_party_id],
                                   uselist=False, back_populates='client_party_branch')
    party = db.relationship('Party', uselist=True, back_populates='client_party_branch')

    @property
    def json(self) -> dict:
        """Return the client party branch as a json object."""
        party = {
            'code': str(self.client_party_branch_id),
            'contact': {
                'name': self.contact_name,
                'phoneNumber': self.contact_phone_number
            }
        }
        if self.contact_area_cd:
            party['contact']['areaCode'] = self.contact_area_cd
        if self.email_id:
            party['emailAddress'] = self.email_id
        if self.client_party and self.client_party.business_name:
            party['businessName'] = self.client_party.business_name
        if self.address:
            cp_address = self.address.json
            party['address'] = cp_address

        return party

    @classmethod
    def find_by_code(cls, code: str = None):
        """Return a client party branch json object by client code."""
        party = None
        if code:
            party = cls.query.filter(ClientPartyBranch.client_party_branch_id == int(code)).one_or_none()

        if party:
            return party.json

        return party
