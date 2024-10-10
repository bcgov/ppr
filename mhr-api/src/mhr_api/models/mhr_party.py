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
"""This module holds data for parties and client parties (debtors, registering parties, secured parties)."""
from __future__ import annotations

from sqlalchemy import event, text
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from .address import Address  # noqa: F401 pylint: disable=unused-import
from .db import db
from .type_tables import MhrOwnerStatusTypes, MhrPartyTypes

NAME_KEY_QUERY = """
    SELECT mhr_name_compressed_key(:actual_name)
"""


class MhrParty(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the MHR parties (people and organizations)."""

    __tablename__ = "mhr_parties"

    id = db.mapped_column("id", db.Integer, db.Sequence("mhr_party_id_seq"), primary_key=True)
    # party person
    first_name = db.mapped_column("first_name", db.String(50), nullable=True)
    middle_name = db.mapped_column("middle_name", db.String(50), nullable=True, index=True)
    last_name = db.mapped_column("last_name", db.String(50), nullable=True)
    # or party business
    business_name = db.mapped_column("business_name", db.String(150), index=True, nullable=True)
    # Search key
    compressed_name = db.mapped_column("compressed_name", db.String(30), nullable=False, index=True)
    email_id = db.mapped_column("email_address", db.String(250), nullable=True)
    phone_number = db.mapped_column("phone_number", db.String(20), nullable=True)
    phone_extension = db.mapped_column("phone_extension", db.String(10), nullable=True)
    suffix = db.mapped_column("suffix", db.String(100), nullable=True)
    description = db.mapped_column("description", db.String(150), nullable=True)
    death_cert_number = db.mapped_column("death_cert_number", db.String(20), nullable=True)
    death_ts = db.mapped_column("death_ts", db.DateTime, nullable=True)
    corp_number = db.mapped_column("corp_number", db.String(20), nullable=True)
    death_corp_number = db.mapped_column("death_corp_number", db.String(20), nullable=True)

    # parent keys
    address_id = db.mapped_column("address_id", db.Integer, db.ForeignKey("addresses.id"), nullable=True, index=True)
    registration_id = db.mapped_column(
        "registration_id", db.Integer, db.ForeignKey("mhr_registrations.id"), nullable=False, index=True
    )
    change_registration_id = db.mapped_column("change_registration_id", db.Integer, nullable=False, index=True)
    party_type = db.mapped_column(
        "party_type",
        PG_ENUM(MhrPartyTypes, name="mhr_party_type"),
        db.ForeignKey("mhr_party_types.party_type"),
        nullable=False,
    )
    status_type = db.mapped_column(
        "status_type",
        PG_ENUM(MhrOwnerStatusTypes, name="mhr_owner_status_type"),
        db.ForeignKey("mhr_owner_status_types.status_type"),
        nullable=False,
    )
    owner_group_id = db.mapped_column("owner_group_id", db.Integer, db.ForeignKey("mhr_owner_groups.id"), nullable=True)

    # Relationships - Address
    address = db.relationship(
        "Address", foreign_keys=[address_id], uselist=False, back_populates="mhr_party", cascade="all, delete"
    )
    # Relationships - MhrRegistration
    registration = db.relationship(
        "MhrRegistration",
        foreign_keys=[registration_id],
        back_populates="parties",
        cascade="all, delete",
        uselist=False,
    )
    # Relationships - MhrOwnerGroup
    owner_group = db.relationship(
        "MhrOwnerGroup", foreign_keys=[owner_group_id], back_populates="owners", cascade="all, delete", uselist=False
    )
    # Relationships - PartyType Don't need for now.
    # party_types = db.relationship('MhrPartyType', foreign_keys=[party_type],
    #                               back_populates='party', cascade='all, delete', uselist=False)

    @property
    def json(self) -> dict:  # pylint: disable=too-many-branches
        """Return the party as a json object."""
        party = {}
        if self.party_type not in (MhrPartyTypes.SUBMITTING, MhrPartyTypes.CONTACT):
            party["ownerId"] = self.id
            party["status"] = self.status_type
            party["partyType"] = self.party_type

        if self.business_name:
            if self.party_type in (MhrPartyTypes.SUBMITTING, MhrPartyTypes.CONTACT):
                party["businessName"] = self.business_name
            else:
                party["organizationName"] = self.business_name
        elif self.last_name:
            person_name = {"first": self.first_name, "last": self.last_name}
            if self.middle_name:
                person_name["middle"] = self.middle_name
            if self.party_type in (MhrPartyTypes.SUBMITTING, MhrPartyTypes.CONTACT):
                party["personName"] = person_name
            else:
                party["individualName"] = person_name

        if self.address:
            cp_address = self.address.json
            party["address"] = cp_address
        if self.email_id:
            party["emailAddress"] = self.email_id
        if self.phone_number:
            party["phoneNumber"] = self.phone_number
        if self.phone_extension:
            party["phoneExtension"] = self.phone_extension
        if self.description:
            party["description"] = self.description
        if self.suffix:
            party["suffix"] = self.suffix
        if self.corp_number:
            party["corpNumber"] = self.corp_number
        return party

    @classmethod
    def find_by_id(cls, party_id: int = None):
        """Return a party object by party ID."""
        party = None
        if party_id:
            party = db.session.query(MhrParty).filter(MhrParty.id == party_id).one_or_none()

        return party

    @classmethod
    def find_by_registration_id(cls, registration_id: int = None):
        """Return a list of party objects by registration id."""
        parties = None
        if registration_id:
            parties = (
                db.session.query(MhrParty)
                .filter(MhrParty.registration_id == registration_id)
                .order_by(MhrParty.id)
                .all()
            )

        return parties

    @classmethod
    def find_by_change_registration_id(cls, registration_id: int = None):
        """Return a list of party objects by change registration id."""
        parties = None
        if registration_id:
            parties = (
                db.session.query(MhrParty)
                .filter(MhrParty.change_registration_id == registration_id)
                .order_by(MhrParty.id)
                .all()
            )

        return parties

    @staticmethod
    def create_from_json(  # pylint: disable=too-many-branches
        json_data,
        party_type: str,
        registration_id: int = None,
        change_registration_id: int = None,
    ):
        """Create a party object from a json schema object: map json to db."""
        # current_app.logger.info(json_data)
        party: MhrParty = MhrParty()
        party.party_type = party_type
        party.status_type = MhrOwnerStatusTypes.ACTIVE
        if json_data.get("businessName"):
            party.business_name = json_data["businessName"].strip().upper()
        elif json_data.get("organizationName"):
            party.business_name = json_data["organizationName"].strip().upper()
        elif json_data.get("individualName"):
            party.last_name = json_data["individualName"]["last"].strip().upper()
            party.first_name = json_data["individualName"]["first"].strip().upper()
            name = party.last_name + " " + party.first_name
            if json_data["individualName"].get("middle"):
                party.middle_name = json_data["individualName"]["middle"].strip().upper()
                name += " " + party.middle_name
        else:
            party.last_name = json_data["personName"]["last"].strip().upper()
            party.first_name = json_data["personName"]["first"].strip().upper()
            name = party.last_name + " " + party.first_name
            if json_data["personName"].get("middle"):
                party.middle_name = json_data["personName"]["middle"].strip().upper()
                name += " " + party.middle_name

        if json_data.get("emailAddress"):
            party.email_id = json_data["emailAddress"].strip()
        if json_data.get("phoneNumber"):
            party.phone_number = json_data["phoneNumber"].strip()
        if json_data.get("phoneExtension"):
            party.phone_extension = json_data["phoneExtension"].strip()
        if json_data.get("description"):
            party.description = json_data["description"].strip().upper()
        if json_data.get("suffix"):
            party.suffix = json_data["suffix"].strip().upper()
        if json_data.get("corpNumber"):
            party.corp_number = json_data["corpNumber"].strip()

        party.address = Address.create_from_json(json_data["address"])

        if registration_id:
            party.registration_id = registration_id
            if not change_registration_id:
                party.change_registration_id = registration_id
        if change_registration_id:
            party.change_registration_id = change_registration_id
        return party

    @staticmethod
    def create_from_registration_json(json_data, registration_id: int = None):
        """Create a list of party objects from a financing statement json schema object: map json to db."""
        parties = []
        party = json_data.get("submittingParty")
        if party:
            parties.append(MhrParty.create_from_json(party, MhrPartyTypes.SUBMITTING, registration_id))
        # owners and owner groups here.
        return parties


@event.listens_for(MhrParty, "before_insert")
def party_before_insert_listener(
    mapper, connection, target: MhrParty  # pylint: disable=unused-argument; don't use mapper
):
    """Set party compressed key value for searching."""
    stmt = text(NAME_KEY_QUERY)
    if target.business_name:
        stmt = stmt.bindparams(actual_name=target.business_name)
    else:
        search_name: str = target.last_name + " " + target.first_name
        if target.middle_name:
            search_name += " " + target.middle_name
        stmt = stmt.bindparams(actual_name=search_name)
    result = connection.execute(stmt)
    row = result.first()
    target.compressed_name = str(row[0])
