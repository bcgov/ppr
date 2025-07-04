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
"""This module holds model data for client party code registration tracking."""
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from ppr_api.exceptions import DatabaseException
from ppr_api.models import ClientCode
from ppr_api.models import utils as model_utils
from ppr_api.models.type_tables import ClientCodeTypes
from ppr_api.utils.logging import logger

from .db import db


class ClientCodeRegistration(db.Model):
    """This class maintains client party code registration information."""

    __tablename__ = "client_code_registrations"

    id = db.mapped_column("id", db.Integer, db.Sequence("client_code_registration_id_seq"), primary_key=True)
    create_ts = db.mapped_column("create_ts", db.DateTime, nullable=False, index=True)
    request_data = db.mapped_column("request_data", db.JSON, nullable=False)
    pay_invoice_id = db.mapped_column("pay_invoice_id", db.Integer, nullable=True)
    pay_path = db.mapped_column("pay_path", db.String(256), nullable=True)
    user_id = db.mapped_column("user_id", db.String(1000), nullable=True)
    # For name/address changes.
    previous_registration_id = db.mapped_column("previous_registration_id", db.Integer, nullable=True)

    # parent keys
    client_code_type = db.mapped_column(
        "client_code_type",
        PG_ENUM(ClientCodeTypes, name="client_code_type"),
        db.ForeignKey("client_code_types.client_code_type"),
        nullable=False,
    )

    # Relationships - Registration
    client_code = db.relationship("ClientCode", back_populates="client_code_registration", uselist=False)
    registration_code_type = db.relationship(
        "ClientCodeType",
        foreign_keys=[client_code_type],
        back_populates="client_code_registration",
        cascade="all, delete",
        uselist=False,
    )

    @property
    def json(self) -> dict:
        """Return the client party code registration information as a json object."""
        result = {
            "createDateTime": model_utils.format_ts(self.create_ts),
            "clientCodeRegistrationType": self.client_code_type.value,
        }
        if self.client_code:
            result["clientCode"] = self.client_code.json
        if self.pay_invoice_id and self.pay_path:
            payment = {"invoiceId": str(self.pay_invoice_id), "receipt": self.pay_path}
            result["payment"] = payment
        return result

    def save(self):
        """Render a search results detail information to the local cache."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:  # noqa: B902; just logging
            logger.error(f"DB client_code_registrations save exception: {db_exception}")
            raise DatabaseException(db_exception) from db_exception

    @classmethod
    def find_by_id(cls, reg_id: int):
        """Return the client_code_registrations record matching the id."""
        registration = None
        if reg_id:
            registration = (
                db.session.query(ClientCodeRegistration).filter(ClientCodeRegistration.id == reg_id).one_or_none()
            )
        return registration

    @staticmethod
    def create_new_from_json(json_data: dict, account_id: str, user_id: str):
        """Create a client party code registration from dict/json."""
        code = None
        if not json_data.get("headOfficeCode"):
            code: ClientCode = ClientCode.create_new_from_json(json_data, account_id)
        else:
            code: ClientCode = ClientCode.create_new_branch_from_json(json_data, account_id)
        reg: ClientCodeRegistration = ClientCodeRegistration(
            create_ts=code.date_ts,
            request_data=json_data,
            user_id=user_id,
            client_code_type=ClientCodeTypes.CREATE_CODE,
        )
        reg.client_code = code
        return reg

    @staticmethod
    def create_name_change_from_json(json_data: dict, user_id: str, code: ClientCode):
        """Create a client party code name change registration from dict/json."""
        reg: ClientCodeRegistration = ClientCodeRegistration(
            create_ts=model_utils.now_ts(),
            request_data=json_data,
            user_id=user_id,
            client_code_type=ClientCodeTypes.CHANGE_NAME,
        )
        reg.client_code = code
        return reg
