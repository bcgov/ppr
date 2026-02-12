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
from sqlalchemy.sql import text

import mhr_api.models.registration_utils as reg_utils
from mhr_api.exceptions import DatabaseException
from mhr_api.models import utils as model_utils
from mhr_api.models.mhr_registration import REG_TO_DOC_TYPE
from mhr_api.models.registration_utils import AccountRegistrationParams
from mhr_api.utils.logging import logger

from .db import db
from .mhr_draft import MhrDraft
from .mhr_review_step import MhrReviewStep
from .type_tables import MhrDocumentTypes, MhrRegistrationTypes, MhrReviewStatusTypes

# from .mhr_review_step import MhrReviewStep


QUERY_REVIEW_DEFAULT = """select rr.id as review_id, rr.create_ts, rr.mhr_number, rr.status_type, rr.document_id,
       rr.priority, rr.registration_type, rr.submitting_name, rr.assignee_name, dt.document_type_desc
  from mhr_review_registrations rr, mhr_document_types dt
 where rr.document_type = dt.document_type """
DEFAULT_SORT_ORDER = " order by rr.priority desc, rr.create_ts asc"


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
    drs_id = db.mapped_column("drs_id", db.String(20), nullable=True)

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
        result = copy.deepcopy(self.registration_data)
        result["status"] = self.status_type
        result["assigneeName"] = self.assignee_name
        if self.document_id:
            result["documentId"] = self.document_id
        steps = []
        if self.review_steps:
            for step in self.review_steps:
                steps.append(step.json)
        result["reviewSteps"] = steps
        return result

    def save(self):
        """Render a record of mhr review registration information to the local cache."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:  # noqa: B902; just logging
            logger.error(f"DB mhr review registration save exception: {db_exception}")
            raise DatabaseException(db_exception) from db_exception

    def save_update(self, request_json: dict, username: str):
        """Render an updated record of mhr review registration information to the local cache."""
        try:
            new_status: str = request_json.get("statusType")
            change_msg: str = f"Current status={self.status_type.value}, new status={new_status}."
            if request_json.get("payRefundInfo"):
                change_msg += request_json.get("payRefundInfo")
            if not self.document_id and request_json.get("documentId"):
                change_msg += f" Adding document ID {self.document_id}"
                self.document_id = request_json.get("documentId")
            if self.status_type != MhrReviewStatusTypes.NEW.value and new_status == MhrReviewStatusTypes.NEW.value:
                change_msg += f" Removing assignee {self.assignee_name}."
                self.assignee_name = None
            if new_status == MhrReviewStatusTypes.IN_REVIEW.value and self.status_type.value != new_status:
                if request_json.get("assigneeName"):
                    self.assignee_name = request_json.get("assigneeName")
                else:
                    self.assignee_name = username
                change_msg += f" Setting assignee {self.assignee_name}."
            step: MhrReviewStep = MhrReviewStep(
                review_registration_id=self.id,
                create_ts=model_utils.now_ts(),
                status_type=new_status,
                username=username,
                change_note=change_msg,
                staff_note=request_json.get("staffNote", None),
                client_note=request_json.get("clientNote", None),
            )
            if self.is_declined(new_status):
                step.declined_reason_type = request_json.get("declinedReasonType")
                change_msg += f" Declined reason type: {step.declined_reason_type}."
            if self.status_type.value != new_status:
                self.status_type = new_status
            db.session.add(step)
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:  # noqa: B902; just logging
            logger.error(f"DB mhr review registration save update exception: {db_exception}")
            raise DatabaseException(db_exception) from db_exception

    def is_approved(self, new_status: str) -> bool:
        """Is a review update transitioning from IN_REVIEW to APPROVED."""
        return self.status_type == MhrReviewStatusTypes.IN_REVIEW and new_status == MhrReviewStatusTypes.APPROVED.value

    def is_declined(self, new_status: str) -> bool:
        """Is a review update transitioning from IN_REVIEW to DECLINED."""
        return self.status_type == MhrReviewStatusTypes.IN_REVIEW and new_status == MhrReviewStatusTypes.DECLINED.value

    @classmethod
    def find_by_id(cls, reg_id: int):
        """Return the mhr review registration record matching the id."""
        reg = None
        if reg_id:
            try:
                reg = db.session.query(MhrReviewRegistration).filter(MhrReviewRegistration.id == reg_id).one_or_none()
            except Exception as db_exception:  # noqa: B902; return nicer error
                logger.error(f"MhrReviewRegistration.find_by_id exception: {db_exception}")
                raise DatabaseException(db_exception) from db_exception
        return reg

    @classmethod
    def find_by_invoice_id(cls, invoice_id: int):
        """Return the mhr review registration record matching the payment invoice id."""
        reg = None
        if invoice_id:
            try:
                reg = (
                    db.session.query(MhrReviewRegistration)
                    .filter(MhrReviewRegistration.pay_invoice_id == invoice_id)
                    .one_or_none()
                )
            except Exception as db_exception:  # noqa: B902; return nicer error
                logger.error(f"MhrReviewRegistration.find_by_invoice_id exception: {db_exception}")
                raise DatabaseException(db_exception) from db_exception
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

    @classmethod
    def find_all(cls, params: AccountRegistrationParams):
        """Return a summary list of staff review registrations."""
        registrations = []
        try:
            query = text(MhrReviewRegistration.build_review_query(params))
            if params.has_filter() and params.filter_reg_start_date and params.filter_reg_end_date:
                start_ts = model_utils.search_ts(params.filter_reg_start_date, True)
                end_ts = model_utils.search_ts(params.filter_reg_end_date, False)
                logger.info(f"Coming soon start_ts={start_ts} end_ts={end_ts}")
                # result = db.session.execute(
                #    query, {"query_value1": params.account_id, "query_start": start_ts, "query_end": end_ts}
                # )
                result = db.session.execute(query)
            else:
                result = db.session.execute(query)
            rows = result.fetchall()
            if rows is not None:
                for row in rows:
                    registrations.append(MhrReviewRegistration.__build_summary(row))
            return registrations
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error(f"find_all exception: {db_exception}.")
            raise DatabaseException(db_exception) from db_exception

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
        json_data["documentDescription"] = reg_utils.get_document_description(review_reg.document_type)
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

    @classmethod
    def build_review_query(cls, params: AccountRegistrationParams) -> str:
        """Build the staff review registration summary query."""
        query_text: str = QUERY_REVIEW_DEFAULT
        if not params.has_filter() and not params.has_sort():
            query_text += DEFAULT_SORT_ORDER
            return query_text
        # order_clause: str = ""
        if params.has_filter():
            logger.debug("filter coming")
            # query_text = build_account_query_filter(query_text, params)
        if params.has_sort():
            logger.debug("sort coming")
            # order_clause = QUERY_ACCOUNT_ORDER_BY.get(params.sort_criteria)
            # if params.sort_criteria == REG_TS_PARAM:
            # if params.sort_direction and params.sort_direction == SORT_ASCENDING:
            #    order_clause = order_clause.replace(ACCOUNT_SORT_DESCENDING, ACCOUNT_SORT_ASCENDING)
            # elif params.sort_direction and params.sort_direction == SORT_ASCENDING:
            # order_clause += ACCOUNT_SORT_ASCENDING
            # else:
            # order_clause += ACCOUNT_SORT_DESCENDING
            # query_text += order_clause
        else:  # Default sort order if filter but no sorting specified.
            query_text += DEFAULT_SORT_ORDER
        # logger.info(query_text)
        return query_text

    @classmethod
    def __build_summary(cls, row):
        """Build a single registration summary from query result."""
        summary = {
            "reviewId": str(row[0]),
            "createDateTime": model_utils.format_ts(row[1]),
            "mhrNumber": str(row[2]),
            "statusType": str(row[3]),
            "documentId": str(row[4]) if row[4] else "",
            "priority": bool(row[5]),
            "registrationType": str(row[6]),
            "submittingName": str(row[7]) if row[7] else "",
            "assigneeName": str(row[8]) if row[8] else "",
            "registrationDescription": str(row[9]),
        }
        return summary
