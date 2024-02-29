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
"""This module holds data for maintaining client party name, address, and contact info.

Client parties are reusable registering parties and secured parties.
"""
from __future__ import annotations

from flask import current_app
from mhr_api.exceptions import DatabaseException

# Needed by the SQLAlchemy relationship
from .address import Address  # noqa: F401 pylint: disable=unused-import
from .db import db


class ClientCode(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains client party information (registering and secured parties)."""

    __tablename__ = 'client_codes'
    # key value is generated from a db function tbd. ,default=db.func.get_code_branch_id()
    id = db.mapped_column('id', db.Integer, primary_key=True, nullable=False)
    head_id = db.mapped_column('head_id', db.Integer, index=True, nullable=False)
    name = db.mapped_column('name', db.String(150), index=True, nullable=False)
    bconline_account = db.mapped_column('bconline_account', db.Integer, nullable=True)
    # contact info
    contact_name = db.mapped_column('contact_name', db.String(100), nullable=False)
    contact_area_cd = db.mapped_column('contact_area_cd', db.String(3), nullable=True)
    contact_phone_number = db.mapped_column('contact_phone_number', db.String(15), nullable=False)
    email_id = db.mapped_column('email_address', db.String(250), nullable=True)
    user_id = db.mapped_column('user_id', db.String(7), nullable=True)
    date_ts = db.mapped_column('date_ts', db.DateTime, nullable=True)

    # parent keys
    address_id = db.mapped_column('address_id', db.Integer, db.ForeignKey('addresses.id'), nullable=False, index=True)

    # Relationships
    address = db.relationship('Address', foreign_keys=[address_id], uselist=False,
                              back_populates='client_code', cascade='all, delete')
    party = db.relationship('Party', uselist=True, back_populates='client_code')

    @property
    def json(self) -> dict:
        """Return the client party branch as a json object."""
        party = {
            'code': str(self.id),
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
    def find_by_code(cls, code: str = None):
        """Return a client party branch json object by client code."""
        party = None
        if code:
            try:
                party = db.session.query(ClientCode).filter(ClientCode.id == int(code)).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB find_by_code exception: ' + repr(db_exception))
                raise DatabaseException(db_exception)

        if party:
            return party.json

        return party

    @classmethod
    def find_by_head_office_code(cls, head_office_id: str):
        """Return a list of client parties belonging to a head office searching by code."""
        party_codes = []
        if head_office_id and len(head_office_id) <= 4 and head_office_id.strip().isdigit():
            party_list = None
            try:
                party_list = db.session.query(ClientCode).\
                                filter(ClientCode.head_id == int(head_office_id.strip())).all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB find_by_head_office_code exception: ' + repr(db_exception))
                raise DatabaseException(db_exception)

            if not party_list:
                return party_codes
            for party in party_list:
                party_codes.append(party.json)

        return party_codes

    @classmethod
    def find_by_branch_start(cls, branch_code: str):
        """Return a list of client parties matching on branch ids that start with a query number."""
        party_codes = []
        if not branch_code or not branch_code.strip().isdigit():
            return party_codes
        try:
            query_num = branch_code.strip()
            if int(query_num) < 100:  # Exact match
                party = cls.find_by_code(query_num)
                if party:
                    party_codes.append(party)
                return party_codes

            query_num += '%'
            party_list = db.session.query(ClientCode).filter(db.cast(ClientCode.id, db.String).like(query_num)).all()
            if not party_list:
                return party_codes
            for party in party_list:
                party_codes.append(party.json)
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB find_by_branch_start exception: ' + repr(db_exception))
            raise DatabaseException(db_exception)

        return party_codes

    @classmethod
    def find_by_head_office_name(cls, head_office_name: str = None, is_fuzzy_search: bool = False):
        """Return a list of client parties belonging to a head office searching by name."""
        party_codes = []
        if head_office_name and head_office_name.strip() != '':
            try:
                name = head_office_name.strip().upper()
                party_list = None
                if is_fuzzy_search:
                    name += '%'
                    party_list = db.session.query(ClientCode).filter(ClientCode.name.like(name)).all()
                else:
                    party_list = db.session.query(ClientCode).filter(ClientCode.name == name).all()

                if not party_list:
                    return party_codes
                for party in party_list:
                    party_codes.append(party.json)
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB find_by_head_office_name exception: ' + repr(db_exception))
                raise DatabaseException(db_exception)
        return party_codes

    @classmethod
    def find_by_head_office(cls, name_or_id: str = None, is_fuzzy_search: bool = False):
        """Return a list of client parties belonging to a head office searching by either ID or name."""
        if is_fuzzy_search:
            return cls.find_by_head_office_name(name_or_id, is_fuzzy_search)

        if name_or_id and name_or_id.strip().isdigit():
            return cls.find_by_branch_start(name_or_id)

        return cls.find_by_head_office_name(name_or_id)
