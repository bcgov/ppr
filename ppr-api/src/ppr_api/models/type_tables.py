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
"""This module holds model definitions for the PPR type tables."""

from __future__ import annotations

from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from ppr_api.utils.base import BaseEnum

from .db import db


class SecuritiesActTypes(BaseEnum):
    """Render an Enum of the Securities Act types."""

    LIEN = "LIEN"
    PROCEEDINGS = "PROCEEDINGS"
    PRESERVATION = "PRESERVATION"


class CountryType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the country_type table."""

    __tablename__ = "country_types"

    country_type = db.mapped_column("country_type", db.String(2), primary_key=True)
    country_desc = db.mapped_column("country_desc", db.String(75), nullable=False)

    # parent keys

    # Relationships - Address
    address = db.relationship("Address", back_populates="country_type")


class ProvinceType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the province_type table."""

    __tablename__ = "province_types"

    province_type = db.mapped_column("province_type", db.String(2), primary_key=True)
    country_type = db.mapped_column(
        "country_type", db.String(2), db.ForeignKey("country_types.country_type"), nullable=False
    )
    province_desc = db.mapped_column("province_desc", db.String(75), nullable=False)

    # parent keys

    # Relationships - Address
    address = db.relationship("Address", back_populates="province_type")


class PartyType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the party_type table."""

    __tablename__ = "party_types"

    party_type = db.mapped_column("party_type", db.String(2), primary_key=True)
    party_type_desc = db.mapped_column("party_type_desc", db.String(30), nullable=False)

    # parent keys

    # Relationships - Party
    party = db.relationship("Party", back_populates="party_types")


class RegistrationTypeClass(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the registration_type_class table."""

    __tablename__ = "registration_type_classes"

    registration_type_cl = db.mapped_column("registration_type_cl", db.String(10), primary_key=True)
    registration_desc = db.mapped_column("registration_desc", db.String(100), nullable=False)

    # parent keys

    # Relationships


class RegistrationType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the registration_type table."""

    __tablename__ = "registration_types"

    registration_type = db.mapped_column("registration_type", db.String(2), primary_key=True)
    registration_type_cl = db.mapped_column(
        "registration_type_cl",
        db.String(10),
        db.ForeignKey("registration_type_classes.registration_type_cl"),
        nullable=False,
    )
    registration_desc = db.mapped_column("registration_desc", db.String(100), nullable=False)
    registration_act = db.mapped_column("registration_act", db.String(60), nullable=False)

    # parent keys

    # Relationships - Registration
    registration = db.relationship("Registration", back_populates="reg_type")


class SearchType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the search_type table."""

    __tablename__ = "search_types"

    search_type = db.mapped_column("search_type", db.String(2), primary_key=True)
    search_type_desc = db.mapped_column("search_type_desc", db.String(60), nullable=False)

    # parent keys

    # Relationships - SearchRequest
    search_request = db.relationship("SearchRequest", back_populates="search_request_type")


class StateType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the state_type table."""

    __tablename__ = "state_types"

    state_type = db.mapped_column("state_type", db.String(3), primary_key=True)
    state_type_desc = db.mapped_column("state_type_desc", db.String(30), nullable=False)

    # parent keys

    # Relationships - FinancingStatement
    financing_statement = db.relationship("FinancingStatement", back_populates="fin_state_type")


class SerialType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the serial_type table."""

    __tablename__ = "serial_types"

    serial_type = db.mapped_column("serial_type", db.String(2), primary_key=True)
    serial_type_desc = db.mapped_column("serial_type_desc", db.String(30), nullable=False)

    # parent keys

    # Relationships - VehicleCollateral
    vehicle_collateral = db.relationship("VehicleCollateral", back_populates="serial_type")


class EventTrackingType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the event_tracking_types table."""

    __tablename__ = "event_tracking_types"

    event_tracking_type = db.mapped_column("event_tracking_type", db.String(20), primary_key=True)
    event_tracking_desc = db.mapped_column("event_tracking_desc", db.String(100), nullable=False)

    # parent keys

    # Relationships - EventTracking
    event_tracking = db.relationship("EventTracking", back_populates="tracking_type")


class SecuritiesActType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the securities_act_types table."""

    __tablename__ = "securities_act_types"

    securities_act_type = db.mapped_column(
        "securities_act_type", PG_ENUM(SecuritiesActTypes, name="securities_act_type"), primary_key=True
    )
    securities_act_type_desc = db.mapped_column("securities_act_type_desc", db.String(100), nullable=False)

    # Relationships -
    securities_act_notice = db.relationship("SecuritiesActNotice", back_populates="sec_act_type")

    @classmethod
    def find_all(cls):
        """Return all the type records."""
        return db.session.query(SecuritiesActType).all()
