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
"""This module holds model data for MHR staff review registration information."""
import copy

from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from mhr_api.exceptions import DatabaseException
from mhr_api.models import utils as model_utils
from mhr_api.models.mhr_registration import REG_TO_DOC_TYPE
from mhr_api.utils.logging import logger

from .db import db
from .mhr_draft import MhrDraft
from .type_tables import MhrDocumentTypes, MhrRegistrationTypes, MhrReviewStatusTypes

# from .mhr_review_step import MhrReviewStep


class MhrReviewRegistration(db.Model):
    """This class maintains MHR staff review of registrations information."""

    __tablename__ = "mhr_review_registrations"

    id = db.mapped_column("id", db.Integer, db.Sequence("mhr_review_registration_id_seq"), primary_key=True)
    create_ts = db.mapped_column("create_ts", db.DateTime, nullable=False, index=True)
    registration_data = db.mapped_column("registration_data", db.JSON, nullable=False)
    mhr_number = db.mapped_column("mhr_number", db.String(7), nullable=False, index=True)
    draft_id = db.mapped_column("draft_id", db.Integer, nullable=False)
    account_id = db.mapped_column("account_id", db.String(20), nullable=True, index=True)
    submitting_name = db.mapped_column("submitting_name", db.String(320), nullable=True, index=True)
    assignee_name = db.mapped_column("assignee_name", db.String(320), nullable=True, index=True)
    client_reference_id = db.mapped_column("client_reference_id", db.String(50), nullable=True)
    pay_invoice_id = db.mapped_column("pay_invoice_id", db.Integer, nullable=True)
    pay_path = db.mapped_column("pay_path", db.String(256), nullable=True)
    user_id = db.mapped_column("user_id", db.String(1000), nullable=True)
    document_id = db.mapped_column("document_id", db.String(20), nullable=True)
    priority = db.mapped_column("priority", db.Boolean, nullable=False, index=True)

    # parent keys
    registration_type = db.mapped_column(
        "registration_type",
        PG_ENUM(MhrRegistrationTypes, name="mhr_registration_type"),
        db.ForeignKey("mhr_registration_types.registration_type"),
        nullable=False,
        index=True,
    )
    document_type = db.mapped_column(
        "document_type",
        PG_ENUM(MhrDocumentTypes, name="mhr_document_type"),
        db.ForeignKey("mhr_document_types.document_type"),
        nullable=False,
        index=True,
    )
    status_type = db.mapped_column(
        "status_type",
        PG_ENUM(MhrReviewStatusTypes, name="mhr_review_status_type"),
        db.ForeignKey("mhr_review_status_types.status_type"),
        nullable=False,
        index=True,
    )

    # relationships
    review_steps = db.relationship(
        "MhrReviewStep", order_by="asc(MhrReviewStep.id)", back_populates="review_registration"
    )

    @property
    def json(self) -> dict:
        """Return the registration information as a json object."""
        result = {
            "mhrNumber": self.mhr_number,
            "createDateTime": model_utils.format_ts(self.registration_ts),
            "registrationType": self.registration_type,
            "status": self.status_type,
            "priority": self.priority,
            "documentDescription": self.document_type.document_type_desc,
        }
        return result

    def save(self):
        """Render a record of mhr review registration information to the local cache."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:  # noqa: B902; just logging
            logger.error(f"DB mhr review registration save exception: {db_exception}")
            raise DatabaseException(db_exception) from db_exception

    @classmethod
    def find_by_id(cls, reg_id: int):
        """Return the mhr review registration record matching the id."""
        reg = None
        if reg_id:
            reg = db.session.query(MhrReviewRegistration).filter(MhrReviewRegistration.id == reg_id).one_or_none()

        return reg

    @classmethod
    def find_by_mhr_number(cls, mhr_number: str):
        """Return a list of review registrations by MHR number."""
        regs = None
        if mhr_number:
            try:
                regs = (
                    db.session.query(MhrReviewRegistration)
                    .filter(MhrReviewRegistration.mhr_number == mhr_number)
                    .order_by(MhrReviewRegistration.id)
                    .all()
                )
            except Exception as db_exception:  # noqa: B902; return nicer error
                logger.error(f"MhrReviewRegistration.find_by_mhr_number exception: {db_exception}")
                raise DatabaseException(db_exception) from db_exception
        return regs

    @staticmethod
    def create_from_json(json_data: dict, draft: MhrDraft):
        """Create a staff review registration objects from the request json and the previously created draft."""
        review_reg = MhrReviewRegistration(
            create_ts=draft.update_ts,
            draft_id=draft.id,
            mhr_number=draft.mhr_number,
            account_id=draft.account_id,
            user_id=draft.user_id,
            registration_type=draft.registration_type,
        )
        if json_data.get("documentId"):
            review_reg.document_id = json_data.get("documentId")
        review_reg.document_type = REG_TO_DOC_TYPE[review_reg.registration_type]
        if json_data.get("paymentPending"):
            review_reg.status_type = MhrReviewStatusTypes.PAY_PENDING
        else:
            review_reg.status_type = MhrReviewStatusTypes.NEW
        if json_data.get("clientReferenceId"):
            review_reg.client_reference_id = json_data.get("clientReferenceId")
        review_reg.pay_invoice_id = int(json_data["payment"].get("invoiceId"))
        review_reg.pay_path = json_data["payment"].get("receipt")
        review_reg.priority = json_data["payment"].get("priority", False)
        if json_data["submittingParty"].get("businessName"):
            review_reg.submitting_name = json_data["submittingParty"].get("businessName")
        else:
            sub_name: str = json_data["submittingParty"]["personName"].get("first")
            if json_data["submittingParty"]["personName"].get("middle"):
                sub_name += " " + json_data["submittingParty"]["personName"].get("middle")
                sub_name += " " + json_data["submittingParty"]["personName"].get("last")
            review_reg.submitting_name = sub_name
        review_reg.registration_data = copy.deepcopy(json_data)
        return review_reg
