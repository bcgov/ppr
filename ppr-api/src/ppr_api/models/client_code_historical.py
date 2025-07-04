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

from ppr_api.exceptions import DatabaseException
from ppr_api.utils.base import BaseEnum
from ppr_api.utils.logging import logger

# Needed by the SQLAlchemy relationship
from .address import Address  # noqa: F401 pylint: disable=unused-import
from .client_code import ClientCode
from .db import db


class ClientCodeHistorical(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains client party information: history of name and address changes."""

    class HistoricalTypes(BaseEnum):
        """Render an Enum of the historical types."""

        ADDRESS = "A"
        BOTH = "B"
        NAME = "N"

    __tablename__ = "client_codes_historical"

    id = db.mapped_column("id", db.Integer, db.Sequence("historical_head_id_seq"), primary_key=True)
    head_id = db.mapped_column("head_id", db.Integer, index=True, nullable=False)
    name = db.mapped_column("name", db.String(150), index=True, nullable=False)
    historical_type = db.mapped_column("historical_type", db.String(1), nullable=False)
    bconline_account = db.mapped_column("bconline_account", db.Integer, nullable=True)
    # contact info
    contact_name = db.mapped_column("contact_name", db.String(100), nullable=False)
    contact_area_cd = db.mapped_column("contact_area_cd", db.String(3), nullable=True)
    contact_phone_number = db.mapped_column("contact_phone_number", db.String(15), nullable=False)
    email_id = db.mapped_column("email_addresss", db.String(250), nullable=True)
    user_id = db.mapped_column("user_id", db.String(7), nullable=True)
    date_ts = db.mapped_column("date_ts", db.DateTime, nullable=True)

    # parent keys
    branch_id = db.mapped_column("branch_id", db.Integer, db.ForeignKey("client_codes.id"), nullable=False, index=True)
    address_id = db.mapped_column("address_id", db.Integer, db.ForeignKey("addresses.id"), nullable=False, index=True)
    users_id = db.mapped_column("users_id", db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)

    # Relationships
    address = db.relationship(
        "Address",
        foreign_keys=[address_id],
        uselist=False,
        back_populates="client_code_historical",
        cascade="all, delete",
    )
    client_code = db.relationship(
        "ClientCode", foreign_keys=[branch_id], uselist=False, back_populates="client_code_historical"
    )

    @property
    def json(self) -> dict:
        """Return the client party branch as a json object."""
        party = {
            "code": str(self.branch_id),
            "businessName": self.name,
            "contact": {"name": self.contact_name, "phoneNumber": self.contact_phone_number},
        }
        if self.contact_area_cd:
            party["contact"]["areaCode"] = self.contact_area_cd
        if self.email_id:
            party["emailAddress"] = self.email_id
        if self.address:
            cp_address = self.address.json
            party["address"] = cp_address

        return party

    def save(self):
        """Render a client code historical record to the local cache."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:  # noqa: B902; just logging
            logger.error(f"DB client_code_historical save exception: {db_exception}")
            raise DatabaseException(db_exception) from db_exception

    @classmethod
    def find_by_id(cls, historical_id: int = None):
        """Return a code historical json object by primary key."""
        party = None
        if historical_id:
            party = (
                db.session.query(ClientCodeHistorical).filter(ClientCodeHistorical.id == historical_id).one_or_none()
            )

        if party:
            return party.json

        return party

    @staticmethod
    def create_from_client_code(code: ClientCode, hist_type: str):
        """Creae a code historical object from a client code object."""
        hist_code: ClientCodeHistorical = ClientCodeHistorical(
            head_id=code.head_id,
            name=code.name,
            historical_type=hist_type,
            bconline_account=code.bconline_account,
            contact_name=code.contact_name,
            contact_area_cd=code.contact_area_cd,
            contact_phone_number=code.contact_phone_number,
            email_id=code.email_id,
            date_ts=code.date_ts,
            branch_id=code.id,
            address_id=code.address_id,
        )
        return hist_code
