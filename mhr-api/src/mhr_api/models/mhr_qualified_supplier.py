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
"""This module holds data for qualifid supplier party information."""
from __future__ import annotations

from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from .address import Address  # noqa: F401 pylint: disable=unused-import
from .db import db
from .type_tables import MhrPartyTypes


class MhrQualifiedSupplier(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the MHR qualiifed supplier parties (people and businesses)."""

    __tablename__ = "mhr_qualified_suppliers"

    id = db.mapped_column("id", db.Integer, db.Sequence("mhr_supplier_id_seq"), primary_key=True)
    # party person
    first_name = db.mapped_column("first_name", db.String(50), nullable=True)
    middle_name = db.mapped_column("middle_name", db.String(50), nullable=True)
    last_name = db.mapped_column("last_name", db.String(50), nullable=True)
    # or party business
    business_name = db.mapped_column("business_name", db.String(150), nullable=True)
    dba_name = db.mapped_column("dba_name", db.String(150), nullable=True)
    authorization_name = db.mapped_column("authorization_name", db.String(150), nullable=True)
    account_id = db.mapped_column("account_id", db.String(20), nullable=False)
    email_id = db.mapped_column("email_address", db.String(250), nullable=True)
    phone_number = db.mapped_column("phone_number", db.String(20), nullable=True)
    phone_extension = db.mapped_column("phone_extension", db.String(10), nullable=True)
    terms_accepted = db.mapped_column("terms_accepted", db.String(1), nullable=True)
    confirm_requirements = db.mapped_column("confirm_requirements", db.String(1), nullable=True)

    # parent keys
    address_id = db.mapped_column("address_id", db.Integer, db.ForeignKey("addresses.id"), nullable=True, index=True)
    location_address_id = db.mapped_column(
        "location_address_id", db.Integer, db.ForeignKey("addresses.id"), nullable=True, index=True
    )
    party_type = db.mapped_column(
        "party_type",
        PG_ENUM(MhrPartyTypes, name="mhr_party_type"),
        db.ForeignKey("mhr_party_types.party_type"),
        nullable=False,
    )
    # Relationships - Addressess
    address = db.relationship("Address", foreign_keys=[address_id], uselist=False)
    location_address = db.relationship("Address", foreign_keys=[location_address_id], uselist=False)

    @property
    def json(self) -> dict:
        """Return the party as a json object."""
        party = {
            "confirmRequirements": bool(self.confirm_requirements and self.confirm_requirements == "Y"),
            "termsAccepted": bool(self.terms_accepted and self.terms_accepted == "Y"),
            "partyType": self.party_type,
            "address": self.address.json,
        }
        if self.business_name:
            party["businessName"] = self.business_name
        elif self.last_name:
            person_name = {"first": self.first_name, "last": self.last_name}
            if self.middle_name:
                person_name["middle"] = self.middle_name
            party["personName"] = person_name
        if self.dba_name:
            party["dbaName"] = self.dba_name
        if self.email_id:
            party["emailAddress"] = self.email_id
        if self.phone_number:
            party["phoneNumber"] = self.phone_number
        if self.phone_extension:
            party["phoneExtension"] = self.phone_extension
        if self.authorization_name:
            party["authorizationName"] = self.authorization_name
        if self.location_address_id and self.location_address:
            party["locationAddress"] = self.location_address.json
        return party

    def save(self):
        """Render a qualified supplier to the local cache."""
        db.session.add(self)
        db.session.commit()

    def update(self, json_data: dict):
        """Update the qualified supplier information."""
        if not json_data:
            return
        if json_data.get("businessName"):
            self.business_name = json_data["businessName"].strip().upper()
            self.last_name = None
            self.first_name = None
            self.middle_name = None
        else:
            self.business_name = None
            self.last_name = json_data["personName"]["last"].strip().upper()
            self.first_name = json_data["personName"]["first"].strip().upper()
            if json_data["personName"].get("middle"):
                self.middle_name = json_data["personName"]["middle"].strip().upper()
        if json_data.get("dbaName"):
            self.dba_name = json_data["dbaName"].strip().upper()
        else:
            self.dba_name = None
        if json_data.get("authorizationName"):
            self.authorization_name = json_data["authorizationName"].strip()
        else:
            self.authorization_name = None
        self.email_id = json_data["emailAddress"].strip() if json_data.get("emailAddress") else None
        self.phone_number = json_data["phoneNumber"].strip() if json_data.get("phoneNumber") else None
        self.phone_extension = json_data["phoneExtension"].strip() if json_data.get("phoneExtension") else None
        self.terms_accepted = "Y" if json_data.get("termsAccepted") else None
        if json_data.get("address") and json_data.get("address") != self.address.json:
            self.address = Address.create_from_json(json_data["address"])
        if json_data.get("confirmRequirements"):
            self.confirm_requirements = "Y"
        if json_data.get("locationAddress") and (
            not self.location_address
            or (self.location_address and self.location_address.json != json_data.get("locationAddress"))
        ):
            self.location_address = Address.create_from_json(json_data["locationAddress"])
        db.session.add(self)
        db.session.commit()

    @classmethod
    def delete(cls, account_id: str):
        """Delete a qualified supplier by account ID."""
        supplier = None
        if account_id:
            supplier = cls.find_by_account_id(account_id)
        if supplier:
            db.session.delete(supplier)
            db.session.commit()
        return supplier

    @classmethod
    def find_by_id(cls, supplier_id: int = None):
        """Return a qualified supplier party object by primary key ID."""
        supplier = None
        if supplier_id:
            supplier = (
                db.session.query(MhrQualifiedSupplier).filter(MhrQualifiedSupplier.id == supplier_id).one_or_none()
            )
        return supplier

    @classmethod
    def find_by_account_id(cls, account_id: str = None):
        """Return a qualified supplier party object by account ID."""
        supplier = None
        if account_id:
            supplier = (
                db.session.query(MhrQualifiedSupplier)
                .filter(MhrQualifiedSupplier.account_id == account_id)
                .one_or_none()
            )
        return supplier

    @staticmethod
    def create_from_json(json_data, account_id: str, party_type: str):
        """Create a qualified supplier object from a json schema object: map json to db."""
        # logger.info(json_data)
        supplier: MhrQualifiedSupplier = MhrQualifiedSupplier(account_id=account_id, party_type=party_type)
        if json_data.get("businessName"):
            supplier.business_name = json_data["businessName"].strip().upper()
        else:
            supplier.last_name = json_data["personName"]["last"].strip().upper()
            supplier.first_name = json_data["personName"]["first"].strip().upper()
            if json_data["personName"].get("middle"):
                supplier.middle_name = json_data["personName"]["middle"].strip().upper()
        if json_data.get("dbaName"):
            supplier.dba_name = json_data["dbaName"].strip().upper()
        if json_data.get("authorizationName"):
            supplier.authorization_name = json_data["authorizationName"].strip()
        if json_data.get("emailAddress"):
            supplier.email_id = json_data["emailAddress"].strip()
        if json_data.get("phoneNumber"):
            supplier.phone_number = json_data["phoneNumber"].strip()
        if json_data.get("phoneExtension"):
            supplier.phone_extension = json_data["phoneExtension"].strip()
        if json_data.get("termsAccepted"):
            supplier.terms_accepted = "Y"
        supplier.address = Address.create_from_json(json_data["address"])
        if json_data.get("confirmRequirements"):
            supplier.confirm_requirements = "Y"
        if json_data.get("locationAddress"):
            supplier.location_address = Address.create_from_json(json_data["locationAddress"])
        return supplier
