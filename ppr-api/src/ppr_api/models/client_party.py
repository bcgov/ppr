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


class ClientParty(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains client party information (registering and secured parties)."""

    __tablename__ = 'client_party'

    client_party_id = db.Column('client_party_id', db.Integer,
                                db.Sequence('client_party_id_seq'), primary_key=True)
    account_id = db.Column('account_id', db.String(20), nullable=False)
    # party business name
    business_name = db.Column('name', db.String(150), index=True, nullable=True)
    user_id = db.Column('user_id', db.String(7), nullable=True)
    update_ts = db.Column('update_ts', db.DateTime, nullable=True)
    id = db.Column('id', db.Integer, nullable=True)

    # parent keys

    # Relationships
    # party = db.relationship('Party', uselist=True, back_populates='client_party')
    client_party_branch = db.relationship('ClientPartyBranch', uselist=True, back_populates='client_party')

    @property
    def json(self) -> dict:
        """Return the client party as a json object."""
        party = {
            'code': str(self.client_party_id),
        }

        if self.business_name:
            party['businessName'] = self.business_name

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
