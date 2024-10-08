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
"""This module holds data for MHR locations."""

from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from mhr_api.models import utils as model_utils

from .address import Address  # noqa: F401 pylint: disable=unused-import
from .db import db
from .type_tables import MhrLocationTypes, MhrStatusTypes

# from mhr_api.utils.logging import logger


class MhrLocation(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the MHR location information."""

    __tablename__ = "mhr_locations"

    id = db.mapped_column("id", db.Integer, db.Sequence("mhr_location_id_seq"), primary_key=True)
    ltsa_description = db.mapped_column("ltsa_description", db.String(1000), nullable=True)
    additional_description = db.mapped_column("additional_description", db.String(250), nullable=True)
    dealer_name = db.mapped_column("dealer_name", db.String(310), nullable=True)
    exception_plan = db.mapped_column("exception_plan", db.String(150), index=True, nullable=True)
    leave_province = db.mapped_column("leave_province", db.String(1), nullable=True)
    tax_certification = db.mapped_column("tax_certification", db.String(1), nullable=True)
    tax_certification_date = db.mapped_column("tax_certification_date", db.DateTime, nullable=True)
    # LTSA specific properties.
    park_name = db.mapped_column("park_name", db.String(100), nullable=True)
    park_pad = db.mapped_column("park_pad", db.String(10), nullable=True)
    pid_number = db.mapped_column("pid_number", db.String(9), nullable=True)
    lot = db.mapped_column("lot", db.String(10), nullable=True)
    parcel = db.mapped_column("parcel", db.String(10), nullable=True)
    block = db.mapped_column("block", db.String(10), nullable=True)
    district_lot = db.mapped_column("district_lot", db.String(20), nullable=True)
    part_of = db.mapped_column("part_of", db.String(10), nullable=True)
    section = db.mapped_column("section", db.String(10), nullable=True)
    township = db.mapped_column("township", db.String(10), nullable=True)
    range = db.mapped_column("range", db.String(10), nullable=True)
    meridian = db.mapped_column("meridian", db.String(10), nullable=True)
    land_district = db.mapped_column("land_district", db.String(30), nullable=True)
    plan = db.mapped_column("plan", db.String(20), nullable=True)
    band_name = db.mapped_column("band_name", db.String(150), nullable=True)
    reserve_number = db.mapped_column("reserve_number", db.String(20), nullable=True)

    # parent keys
    address_id = db.mapped_column("address_id", db.Integer, db.ForeignKey("addresses.id"), nullable=True, index=True)
    registration_id = db.mapped_column(
        "registration_id", db.Integer, db.ForeignKey("mhr_registrations.id"), nullable=False, index=True
    )
    change_registration_id = db.mapped_column("change_registration_id", db.Integer, nullable=False, index=True)
    location_type = db.mapped_column(
        "location_type",
        PG_ENUM(MhrLocationTypes, name="mhr_location_type"),
        db.ForeignKey("mhr_location_types.location_type"),
        nullable=False,
    )
    status_type = db.mapped_column(
        "status_type",
        PG_ENUM(MhrStatusTypes, name="mhr_status_type"),
        db.ForeignKey("mhr_status_types.status_type"),
        nullable=False,
    )

    # Relationships - Address
    address = db.relationship(
        "Address", foreign_keys=[address_id], uselist=False, back_populates="mhr_location", cascade="all, delete"
    )
    # Relationships - MhrRegistration
    registration = db.relationship(
        "MhrRegistration",
        foreign_keys=[registration_id],
        back_populates="locations",
        cascade="all, delete",
        uselist=False,
    )

    @property
    def json(self) -> dict:  # pylint: disable=too-many-branches, too-many-statements
        """Return the location as a json object."""
        location = {"locationId": self.id, "status": self.status_type, "locationType": self.location_type}
        if self.ltsa_description:
            location["legalDescription"] = self.ltsa_description
        if self.address:
            location["address"] = self.address.json
            if not location["address"].get("postalCode"):
                location["address"]["postalCode"] = ""
        if self.park_name:
            location["parkName"] = self.park_name
        if self.park_pad:
            location["pad"] = self.park_pad
        if self.pid_number:
            location["pidNumber"] = self.pid_number
        if self.lot:
            location["lot"] = self.lot
        if self.parcel:
            location["parcel"] = self.parcel
        if self.block:
            location["block"] = self.block
        if self.district_lot:
            location["districtLot"] = self.district_lot
        if self.part_of:
            location["partOf"] = self.part_of
        if self.section:
            location["section"] = self.section
        if self.township:
            location["township"] = self.township
        if self.range:
            location["range"] = self.range
        if self.meridian:
            location["meridian"] = self.meridian
        if self.land_district:
            location["landDistrict"] = self.land_district
        if self.plan:
            location["plan"] = self.plan
        if self.leave_province and self.leave_province == "Y":
            location["leaveProvince"] = True
        else:
            location["leaveProvince"] = False
        if self.tax_certification and self.tax_certification == "Y":
            location["taxCertificate"] = True
        else:
            location["taxCertificate"] = False
        if self.tax_certification_date:
            location["taxExpiryDate"] = model_utils.format_ts(self.tax_certification_date)
        if self.exception_plan:
            location["exceptionPlan"] = self.exception_plan
        if self.dealer_name:
            location["dealerName"] = self.dealer_name
        if self.additional_description:
            location["additionalDescription"] = self.additional_description
        if self.location_type == MhrLocationTypes.RESERVE:
            if self.band_name:
                location["bandName"] = self.band_name
            if self.reserve_number:
                location["reserveNumber"] = self.reserve_number
        return location

    @classmethod
    def find_by_id(cls, location_id: int = None):
        """Return a location object by location ID."""
        location = None
        if location_id:
            location = db.session.query(MhrLocation).filter(MhrLocation.id == location_id).one_or_none()

        return location

    @classmethod
    def find_by_registration_id(cls, registration_id: int = None):
        """Return a list of location objects by registration id."""
        locations = None
        if registration_id:
            locations = (
                db.session.query(MhrLocation)
                .filter(MhrLocation.registration_id == registration_id)
                .order_by(MhrLocation.id)
                .all()
            )

        return locations

    @classmethod
    def find_by_change_registration_id(cls, registration_id: int = None):
        """Return a list of location objects by change registration id."""
        locations = None
        if registration_id:
            locations = (
                db.session.query(MhrLocation)
                .filter(MhrLocation.change_registration_id == registration_id)
                .order_by(MhrLocation.id)
                .all()
            )

        return locations

    @staticmethod
    def create_from_json(  # pylint: disable=too-many-statements, too-many-branches
        json_data, registration_id: int = None
    ):
        """Create a location object from a json schema object: map json to db."""
        # logger.info(json_data)
        location: MhrLocation = MhrLocation()
        location.location_type = json_data.get("locationType", MhrLocationTypes.OTHER)
        location.status_type = MhrStatusTypes.ACTIVE
        location.address = Address.create_from_json(json_data["address"])
        if registration_id:
            location.registration_id = registration_id
            location.change_registration_id = registration_id
        if json_data.get("legalDescription"):
            location.ltsa_description = json_data["legalDescription"].strip()
        if json_data.get("parkName"):
            location.park_name = json_data["parkName"].strip()
        if json_data.get("pad"):
            location.park_pad = json_data["pad"].strip()
        if json_data.get("pidNumber"):
            location.pid_number = json_data["pidNumber"].strip()
        if json_data.get("parcel"):
            location.parcel = json_data["parcel"].strip()
        if json_data.get("block"):
            location.block = json_data["block"].strip()
        if json_data.get("lot"):
            location.lot = json_data["lot"].strip()
        if json_data.get("districtLot"):
            location.district_lot = json_data["districtLot"].strip()
        if json_data.get("partOf"):
            location.part_of = json_data["partOf"].strip()
        if json_data.get("section"):
            location.section = json_data["section"].strip()
        if json_data.get("township"):
            location.township = json_data["township"].strip()
        if json_data.get("range"):
            location.range = json_data["range"].strip()
        if json_data.get("meridian"):
            location.meridian = json_data["meridian"].strip()
        if json_data.get("landDistrict"):
            location.land_district = json_data["landDistrict"].strip()
        if json_data.get("plan"):
            location.plan = json_data["plan"].strip()
        if json_data.get("exceptionPlan"):
            location.exception_plan = json_data["exceptionPlan"].strip()
        if json_data.get("dealerName"):
            location.dealer_name = json_data["dealerName"].strip()
        if json_data.get("additionalDescription"):
            location.additional_description = json_data["additionalDescription"].strip()
        if location.location_type == MhrLocationTypes.RESERVE:
            if json_data.get("bandName"):
                location.band_name = json_data["bandName"].strip().upper()
            if json_data.get("reserveNumber"):
                location.reserve_number = json_data["reserveNumber"].strip()
        if json_data.get("leaveProvince"):
            location.leave_province = "Y"
        else:
            location.leave_province = "N"
        if json_data.get("taxCertificate"):
            location.tax_certification = "Y"
        else:
            location.tax_certification = "N"

        if json_data.get("taxExpiryDate", None):
            location.tax_certification_date = model_utils.ts_from_iso_format(json_data.get("taxExpiryDate"))

        return location
