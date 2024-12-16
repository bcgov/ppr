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
"""This module holds data for amendment, renewal statement court order information."""
from __future__ import annotations

from .db import db
from .utils import format_ts, ts_from_date_iso_format


class CourtOrder(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the amendment, renewal statement court order information."""

    __tablename__ = "court_orders"

    id = db.mapped_column("id", db.Integer, db.Sequence("court_order_id_seq"), primary_key=True)
    order_date = db.mapped_column("order_date", db.DateTime, nullable=False)
    court_name = db.mapped_column("court_name", db.String(256), nullable=False)
    court_registry = db.mapped_column("court_registry", db.String(64), nullable=False)
    file_number = db.mapped_column("file_number", db.String(20), nullable=False)
    effect_of_order = db.mapped_column("effect_of_order", db.String(512), nullable=True)

    # parent keys
    registration_id = db.mapped_column(
        "registration_id", db.Integer, db.ForeignKey("registrations.id"), nullable=False, index=True
    )

    # Relationships - Registration
    registration = db.relationship("Registration", foreign_keys=[registration_id], cascade="all, delete", uselist=False)

    @property
    def json(self) -> dict:
        """Return the court_order as a json object."""
        court_order = {
            "courtName": self.court_name,
            "courtRegistry": self.court_registry,
            "fileNumber": self.file_number,
            "orderDate": format_ts(self.order_date),
        }
        if self.effect_of_order:
            court_order["effectOfOrder"] = self.effect_of_order

        return court_order

    @classmethod
    def find_by_id(cls, court_order_id: int = None):
        """Return an expiry object by expiry ID."""
        expiry = None
        if court_order_id:
            expiry = db.session.query(CourtOrder).filter(CourtOrder.id == court_order_id).one_or_none()

        return expiry

    @classmethod
    def find_by_registration_id(cls, registration_id: int = None):
        """Return a list of expiry objects by registration number."""
        expiry = None
        if registration_id:
            expiry = db.session.query(CourtOrder).filter(CourtOrder.registration_id == registration_id).one_or_none()

        return expiry

    @staticmethod
    def create_from_json(json_data, registration_id: int = None):
        """Create a court order object from a json schema object: map json to db."""
        court_order = CourtOrder()
        if registration_id:
            court_order.registration_id = registration_id

        court_order.court_name = json_data["courtName"]
        court_order.court_registry = json_data["courtRegistry"]
        court_order.file_number = json_data["fileNumber"]
        court_order.order_date = ts_from_date_iso_format(json_data["orderDate"])
        if "effectOfOrder" in json_data:
            court_order.effect_of_order = json_data["effectOfOrder"]

        return court_order
