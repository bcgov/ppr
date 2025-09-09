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
"""This module holds model data and database operations for draft statements."""
# pylint: disable=singleton-comparison
import json
from http import HTTPStatus

from flask import current_app
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.sql import text

from mhr_api.exceptions import BusinessException, DatabaseException, ResourceErrorCodes
from mhr_api.models import registration_utils as reg_utils
from mhr_api.models import utils as model_utils
from mhr_api.models.type_tables import MhrRegistrationTypes
from mhr_api.utils.logging import logger

from .db import db

QUERY_PKEYS = """
select get_mhr_draft_number() AS draft_num,
       nextval('mhr_draft_id_seq') AS draft_id
"""
QUERY_NEXT_MHR_NUMBER = """
select get_mhr_number() AS mhr_number
"""
QUERY_REUSE_MHR_NUMBER = """
select min(d.mhr_number), 'X'
  from mhr_drafts d
 where d.registration_type = 'MHREG'
   and d.create_ts > now() - interval '30 days'
   and d.mhr_number is not null
   and left(d.draft_number, 1) != 'P'
   and not exists (select r.id
                     from mhr_registrations r
                    where r.registration_type = 'MHREG'
                      and r.mhr_number = d.mhr_number)
   and not exists (select d2.id
                     from mhr_drafts d2
                    where d2.registration_type = 'MHREG'
                      and left(d2.draft_number, 1) = 'P'
                      and d2.mhr_number = d.mhr_number)
"""
QUERY_ACCOUNT_DRAFTS_LIMIT = " FETCH FIRST :max_results_size ROWS ONLY"
QUERY_ACCOUNT_DRAFTS_BASE = """
SELECT d.draft_number, d.create_ts, d.registration_type,
       CASE WHEN d.draft ->> 'documentType' IS NOT NULL
            THEN (SELECT document_type_desc
                    FROM mhr_document_types
                   WHERE document_type::text = d.draft ->> 'documentType')
            ELSE rt.registration_type_desc
            END registration_type_desc,
       d.draft ->> 'clientReferenceId' AS clientReferenceId,
       CASE WHEN d.update_ts IS NOT NULL THEN d.update_ts ELSE d.create_ts END last_update_ts,
       CASE WHEN d.draft -> 'submittingParty' IS NOT NULL THEN
            CASE WHEN d.draft -> 'submittingParty' -> 'businessName' IS NOT NULL THEN
                      d.draft -> 'submittingParty' ->> 'businessName'
                 WHEN d.draft -> 'submittingParty' ->> 'personName' IS NOT NULL THEN
                    concat(d.draft -> 'submittingParty' -> 'personName' ->> 'first', ' ',
                           d.draft -> 'submittingParty' -> 'personName' ->> 'last')
                 END
            ELSE '' END submitting_party,
       (SELECT CASE WHEN d.user_id IS NULL THEN ''
                    ELSE (SELECT CASE WHEN u.lastname = '' or u.lastname IS NULL THEN u.firstname
                                 ELSE u.firstname || ' ' || u.lastname END
                            FROM users u
                           WHERE u.username = d.user_id FETCH FIRST 1 ROWS ONLY) END) AS registering_name,
       d.mhr_number,
       CASE WHEN d.registration_type = 'MHREG' or d.mhr_number IS NULL THEN 0
            ELSE (SELECT COUNT(r.id)
                    FROM mhr_registrations r
                   WHERE r.mhr_number = d.mhr_number
                     AND r.registration_ts > d.create_ts)
            END stale_count,
        d.account_id,
        d.user_id,
       CASE WHEN d.draft -> 'description' IS NOT NULL AND d.draft -> 'description' -> 'manufacturer' IS NOT NULL THEN
                 d.draft -> 'description' ->> 'manufacturer'
            ELSE '' END manufacturer_name,
       CASE WHEN d.draft -> 'location' IS NOT NULL AND d.draft -> 'location' -> 'address' IS NOT NULL THEN
            CASE WHEN d.draft -> 'location' -> 'address' -> 'streetAdditional' IS NOT NULL THEN
                      concat(d.draft -> 'location' -> 'address' ->> 'street', '\n',
                             d.draft -> 'location' -> 'address' ->> 'streetAdditional', '\n',
                             d.draft -> 'location' -> 'address' ->> 'city', ' ',
                             d.draft -> 'location' -> 'address' ->> 'region', '\n',
                             d.draft -> 'location' -> 'address' ->> 'country')
                 ELSE concat(d.draft -> 'location' -> 'address' ->> 'street', '\n',
                             d.draft -> 'location' -> 'address' ->> 'city', ' ',
                             d.draft -> 'location' -> 'address' ->> 'region', '\n',
                             d.draft -> 'location' -> 'address' ->> 'country')
                 END
            ELSE '' END civic_address
  FROM mhr_drafts d, mhr_registration_types rt
 WHERE d.account_id = :query_account
   AND d.registration_type = rt.registration_type
   AND LEFT(d.draft_number, 2) != 'PR'
   AND NOT EXISTS (SELECT r.draft_id FROM mhr_registrations r WHERE r.draft_id = d.id)
   AND NOT EXISTS (SELECT mer.id
                     FROM mhr_extra_registrations mer
                    WHERE mer.mhr_number = d.mhr_number
                      AND mer.account_id = d.account_id
                      AND mer.removed_ind IS NOT NULL AND mer.removed_ind = 'Y')
"""
QUERY_DRAFT_STALE_COUNT = """
SELECT COUNT(r.id)
  FROM mhr_registrations r
 WHERE r.mhr_number = :query_value1
   AND r.registration_ts > :query_value2
"""
FILTER_MHR_NUMBER = " AND mhr_number = '?'"
FILTER_REG_TYPE = " AND registration_type_desc = '?'"
FILTER_SUBMITTING_NAME = " AND submitting_party LIKE '%?%'"
FILTER_CLIENT_REF = " AND UPPER(TRIM(clientReferenceId)) LIKE '%?%'"
FILTER_USERNAME = " AND TRIM(UPPER(registering_name)) LIKE '%?%'"
FILTER_MANUFACTURER = " AND TRIM(UPPER(manufacturer_name)) LIKE '%?%'"
FILTER_DATE = " AND create_ts BETWEEN :query_start AND :query_end"

ORDER_BY_DATE = " ORDER BY create_ts"
ORDER_BY_MHR_NUMBER = " ORDER BY mhr_number"
ORDER_BY_REG_TYPE = " ORDER BY registration_type_desc"
ORDER_BY_SUBMITTING_NAME = " ORDER BY submitting_party"
ORDER_BY_CLIENT_REF = " ORDER BY clientReferenceId"
ORDER_BY_USERNAME = " ORDER BY registering_name"
ORDER_BY_MANUFACTURER_NAME = " ORDER BY manufacturer_name"
ORDER_BY_CIVIC_ADDRESS = " ORDER BY civic_address"
SORT_DESCENDING = " DESC"
SORT_ASCENDING = " ASC"
QUERY_ACCOUNT_DRAFTS_DEFAULT_ORDER = ORDER_BY_DATE + SORT_DESCENDING

QUERY_ACCOUNT_DRAFTS = QUERY_ACCOUNT_DRAFTS_BASE + QUERY_ACCOUNT_DRAFTS_DEFAULT_ORDER + QUERY_ACCOUNT_DRAFTS_LIMIT
QUERY_ACCOUNT_DRAFTS_FILTER = "SELECT * FROM (" + QUERY_ACCOUNT_DRAFTS_BASE + ") AS q WHERE account_id = :query_account"
QUERY_ACCOUNT_ORDER_BY = {
    reg_utils.REG_TS_PARAM: ORDER_BY_DATE,
    reg_utils.MHR_NUMBER_PARAM: ORDER_BY_MHR_NUMBER,
    reg_utils.REG_TYPE_PARAM: ORDER_BY_REG_TYPE,
    reg_utils.SUBMITTING_NAME_PARAM: ORDER_BY_SUBMITTING_NAME,
    reg_utils.CLIENT_REF_PARAM: ORDER_BY_CLIENT_REF,
    reg_utils.USER_NAME_PARAM: ORDER_BY_USERNAME,
    reg_utils.MANUFACTURER_NAME_PARAM: ORDER_BY_MANUFACTURER_NAME,
    reg_utils.CIVIC_ADDRESS_PARAM: ORDER_BY_CIVIC_ADDRESS,
}
QUERY_ACCOUNT_FILTER_BY = {
    reg_utils.MHR_NUMBER_PARAM: FILTER_MHR_NUMBER,
    reg_utils.REG_TYPE_PARAM: FILTER_REG_TYPE,
    reg_utils.SUBMITTING_NAME_PARAM: FILTER_SUBMITTING_NAME,
    reg_utils.CLIENT_REF_PARAM: FILTER_CLIENT_REF,
    reg_utils.USER_NAME_PARAM: FILTER_USERNAME,
    reg_utils.START_TS_PARAM: FILTER_DATE,
    reg_utils.MANUFACTURER_NAME_PARAM: FILTER_MANUFACTURER,
}
DRAFT_PAY_PENDING_PREFIX = "P"  # Special draft number when payment pending.
DRAFT_STAFF_REVIEW_PREFIX = "PR"  # Special draft number when staff review in incomplete.


class MhrDraft(db.Model):
    """This class maintains draft statement information."""

    __tablename__ = "mhr_drafts"
    __allow_unmapped__ = True

    id = db.mapped_column("id", db.Integer, db.Sequence("mhr_draft_id_seq"), primary_key=True)
    draft_number = db.mapped_column(
        "draft_number", db.String(10), nullable=False, unique=True, default=db.func.get_mhr_draft_number()
    )
    account_id = db.mapped_column("account_id", db.String(20), nullable=False, index=True)
    create_ts = db.mapped_column("create_ts", db.DateTime, nullable=False, index=True)
    draft = db.mapped_column("draft", db.JSON, nullable=False)
    mhr_number = db.mapped_column("mhr_number", db.String(7), nullable=True)
    update_ts = db.mapped_column("update_ts", db.DateTime, nullable=True)
    user_id = db.mapped_column("user_id", db.String(1000), nullable=True)

    # parent keys
    registration_type = db.mapped_column(
        "registration_type",
        PG_ENUM(MhrRegistrationTypes, name="mhr_registration_type"),
        db.ForeignKey("mhr_registration_types.registration_type"),
        nullable=False,
    )

    # Relationships - Registration
    registration = db.relationship("MhrRegistration", back_populates="draft", uselist=False)

    stale_count: int = 0

    @property
    def json(self) -> dict:
        """Return the draft as a json object."""
        draft = {
            "createDateTime": model_utils.format_ts(self.create_ts),
            "type": self.registration_type,
            "draftNumber": self.draft_number,
            "registration": self.draft,
        }
        if self.mhr_number:
            draft["outOfDate"] = self.stale_count > 0
        if self.update_ts:
            draft["lastUpdateDateTime"] = model_utils.format_ts(self.update_ts)
        else:
            draft["lastUpdateDateTime"] = model_utils.format_ts(self.create_ts)
        return draft

    @classmethod
    def find_all_by_account_id(cls, params: reg_utils.AccountRegistrationParams):
        """Return a summary list of drafts belonging to an account."""
        drafts_json = []
        if not params or not params.account_id:
            return drafts_json
        try:
            query = text(MhrDraft.build_account_query(params))
            results = None
            max_results_size = int(current_app.config.get("ACCOUNT_DRAFTS_MAX_RESULTS", 1000))
            if params.has_filter() and params.filter_reg_start_date and params.filter_reg_end_date:
                start_ts = model_utils.ts_from_iso_format(params.filter_reg_start_date)
                end_ts = model_utils.ts_from_iso_format(params.filter_reg_end_date)
                results = db.session.execute(
                    query,
                    {
                        "query_account": params.account_id,
                        "query_start": start_ts,
                        "query_end": end_ts,
                        "max_results_size": max_results_size,
                    },
                )
            else:
                results = db.session.execute(
                    query, {"query_account": params.account_id, "max_results_size": max_results_size}
                )
            rows = results.fetchall()
            if rows is not None:
                for row in rows:
                    drafts_json.append(MhrDraft.__build_account_draft_result(row))
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error("DB find_all_by_account_id exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception
        return drafts_json

    @staticmethod
    def build_account_query(params: reg_utils.AccountRegistrationParams) -> str:
        """Build the account draft summary query."""
        if not params.has_filter() and not params.has_sort():
            return QUERY_ACCOUNT_DRAFTS
        query_text: str = QUERY_ACCOUNT_DRAFTS_FILTER
        if params.has_filter():
            query_text = MhrDraft.build_account_query_filter(query_text, params)
        if params.has_sort():
            order_clause: str = QUERY_ACCOUNT_ORDER_BY.get(params.sort_criteria)
            if params.sort_direction and params.sort_direction == reg_utils.SORT_DESCENDING:
                order_clause += SORT_DESCENDING
            elif params.sort_direction and params.sort_direction == reg_utils.SORT_ASCENDING:
                order_clause += SORT_ASCENDING
            else:
                order_clause += SORT_DESCENDING
            query_text += order_clause
        else:  # Default sort order if filter but no sorting specified.
            query_text += QUERY_ACCOUNT_DRAFTS_DEFAULT_ORDER
        return query_text + QUERY_ACCOUNT_DRAFTS_LIMIT

    @staticmethod
    def get_multiple_filters(params: reg_utils.AccountRegistrationParams) -> dict:
        """Build the list of all applied filters as a key/value dictionary."""
        filters = []
        if params.filter_mhr_number:
            filters.append((reg_utils.MHR_NUMBER_PARAM, params.filter_mhr_number))
        if params.filter_registration_type:
            filters.append((reg_utils.REG_TYPE_PARAM, params.filter_registration_type))
        if params.filter_reg_start_date and params.filter_reg_end_date:
            filters.append((reg_utils.START_TS_PARAM, params.filter_reg_start_date))
        if params.filter_client_reference_id:
            filters.append((reg_utils.CLIENT_REF_PARAM, params.filter_client_reference_id))
        if params.filter_submitting_name:
            filters.append((reg_utils.SUBMITTING_NAME_PARAM, params.filter_submitting_name))
        if params.filter_username:
            filters.append((reg_utils.USER_NAME_PARAM, params.filter_username))
        if params.filter_manufacturer:
            filters.append((reg_utils.MANUFACTURER_NAME_PARAM, params.filter_manufacturer))
        if filters:
            return filters
        return None

    @staticmethod
    def build_account_query_filter(query_text: str, params: reg_utils.AccountRegistrationParams) -> str:
        """Build the account draft summary query filter clause."""
        # Get all selected filters and loop through, applying them
        filters = MhrDraft.get_multiple_filters(params)
        if not filters:
            return query_text
        for q_filter in filters:
            filter_type = q_filter[0]
            filter_value = q_filter[1]
            if filter_type and filter_value:
                filter_clause: str = QUERY_ACCOUNT_FILTER_BY.get(filter_type)
                if filter_clause and filter_type != reg_utils.START_TS_PARAM:  # timestamp range added elsewhere
                    filter_clause = filter_clause.replace("?", filter_value)
                query_text += filter_clause
        return query_text

    @staticmethod
    def __build_account_draft_result(row) -> dict:
        """Build a draft result from a query result set row."""
        registering_name = str(row[7])
        if not registering_name or registering_name == "None":
            registering_name = ""
        ref_id = str(row[4])
        if not ref_id or ref_id == "None":
            ref_id = ""
        mhr_num = str(row[8])
        stale_count: int = int(row[9])
        if not mhr_num or mhr_num == "None":
            mhr_num = ""
        draft_number: str = str(row[0])
        draft_json = {
            "draftNumber": draft_number,
            "createDateTime": model_utils.format_ts(row[1]),
            "registrationType": str(str(row[2])),
            "registrationDescription": str(row[3]),
            "lastUpdateDateTime": model_utils.format_ts(row[5]),
            "path": "/mhr/api/v1/drafts/" + str(row[0]),
            "submittingParty": str(row[6]),
            "registeringName": registering_name,
            "clientReferenceId": ref_id,
            "mhrNumber": mhr_num,
            "manufacturerName": str(row[12]),
            "civicAddress": str(row[13]),
        }
        if draft_json.get("mhrNumber"):
            draft_json["outOfDate"] = stale_count > 0
        if draft_number.startswith(DRAFT_PAY_PENDING_PREFIX):
            draft_json["paymentPending"] = True
            draft_json["invoiceId"] = str(row[11])
        return draft_json

    @classmethod
    def find_by_draft_number(cls, draft_number: str = None, allow_used: bool = False):
        """Return a draft statement by document ID."""
        draft = None
        if draft_number:
            try:
                draft = db.session.query(MhrDraft).filter(MhrDraft.draft_number == draft_number).one_or_none()
            except Exception as db_exception:  # noqa: B902; return nicer error
                logger.error("DB find_by_draft_number exception: " + str(db_exception))
                raise DatabaseException(db_exception) from db_exception

        if not draft:
            code = ResourceErrorCodes.NOT_FOUND_ERR.value
            message = model_utils.ERR_DRAFT_NOT_FOUND.format(code=code, draft_number=draft_number)
            raise BusinessException(error=message, status_code=HTTPStatus.NOT_FOUND)

        if draft.registration and not allow_used:
            code = ResourceErrorCodes.UNAUTHORIZED_ERR.value
            message = model_utils.ERR_DRAFT_USED.format(code=code, draft_number=draft_number)
            raise BusinessException(error=message, status_code=HTTPStatus.BAD_REQUEST)
        if draft.mhr_number:
            logger.debug(f"Checking if draftId={draft.id} on mhr {draft.mhr_number} is out of date.")
            draft.get_stale_count()
            logger.debug(f"DraftId={draft.id} out of date count={draft.stale_count}.")
        return draft

    @classmethod
    def find_by_invoice_id(cls, invoice_id: str):
        """Return a draft statement by payment invoice id (payment pending state)."""
        draft = None
        if invoice_id:
            try:
                draft = db.session.query(MhrDraft).filter(MhrDraft.user_id == invoice_id).one_or_none()
            except Exception as db_exception:  # noqa: B902; return nicer error
                logger.error("DB find_by_draft_number exception: " + str(db_exception))
                raise DatabaseException(db_exception) from db_exception
        return draft

    @classmethod
    def delete(cls, draft_number: str = None):
        """Delete a draft statement by document ID."""
        draft = None
        if draft_number:
            draft = cls.find_by_draft_number(draft_number, False)
        # Preserve to track reused mhr numbers.
        if draft and draft.mhr_number and draft.registration_type == MhrRegistrationTypes.MHREG:
            draft.account_id = "SYSTEM"
            db.session.add(draft)
            db.session.commit()
        elif draft:
            db.session.delete(draft)
            db.session.commit()
        return draft

    def save(self):
        """Save the object to the database immediately."""
        if not self.create_ts:
            self.create_ts = model_utils.now_ts()
        db.session.add(self)
        db.session.commit()
        return self.json

    @classmethod
    def update(cls, request_json, draft_number: str = None):
        """Update an existing draft statement by document number."""
        draft = None
        if request_json and request_json.get("registration") and draft_number:
            draft = cls.find_by_draft_number(draft_number, False)
        if draft:
            draft.update_ts = model_utils.now_ts()
            draft.draft = request_json.get("registration")
            if request_json.get("type"):
                reg_type: str = request_json.get("type")
                if reg_type != draft.registration_type:
                    logger.debug(f"Updating draft reg type from {draft.registration_type} to {reg_type}")
                    draft.registration_type = reg_type
        return draft

    @staticmethod
    def create_from_json(json_data, account_id: str, user_id: str = None):
        """Create a draft object from a json Draft schema object: map json to db."""
        draft: MhrDraft = MhrDraft()
        draft.account_id = account_id
        draft.registration_type = json_data.get("type", MhrRegistrationTypes.MHREG)
        draft.draft = json_data.get("registration")
        if user_id:
            draft.user_id = user_id
        if json_data.get("registration") and "mhrNumber" in json_data["registration"]:
            draft.mhr_number = json_data["registration"]["mhrNumber"]
        # Not null constraint: should be removed if staff can submit requests without an account id.
        if not account_id:
            draft.account_id = "NA"
        return draft

    @staticmethod
    def create_from_mhreg_json(json_data, account_id: str, user_id: str = None):
        """Create a draft object from a new home registration json object: map json to db."""
        draft: MhrDraft = MhrDraft.find_draft(json_data)
        if not draft:
            draft: MhrDraft = MhrDraft(
                account_id=account_id, user_id=user_id, registration_type=MhrRegistrationTypes.MHREG, draft=json_data
            )
            result = db.session.execute(text(QUERY_PKEYS))
            row = result.first()
            draft.draft_number = str(row[0])
            draft.id = int(row[1])
            draft.create_ts = model_utils.now_ts()
        else:
            draft.account_id = account_id
            draft.user_id = user_id
            draft.registration_type = MhrRegistrationTypes.MHREG
            draft.draft = json_data
        if not draft.mhr_number:
            mhr_result = db.session.execute(text(QUERY_REUSE_MHR_NUMBER))
            mhr_row = mhr_result.first()
            if mhr_row[0]:
                draft.mhr_number = str(mhr_row[0])
        if not draft.mhr_number:
            mhr_result2 = db.session.execute(text(QUERY_NEXT_MHR_NUMBER))
            mhr_row2 = mhr_result2.first()
            draft.mhr_number = str(mhr_row2[0])
        # Not null constraint: should be removed if staff can submit requests without an account id.
        if not account_id:
            draft.account_id = "NA"
        return draft

    @staticmethod
    def create_from_registration(registration, json_data, user_id: str = None):
        """Create a draft object from a registration."""
        draft: MhrDraft = MhrDraft()
        if registration.draft_id:
            draft.id = registration.draft_id  # pylint: disable=invalid-name; allow name of id.
        draft.account_id = registration.account_id
        draft.create_ts = registration.registration_ts
        draft.mhr_number = registration.mhr_number
        draft.draft_number = registration.draft_number
        draft.registration_type = registration.registration_type
        draft.draft = json_data
        if user_id:
            draft.user_id = user_id
        # Not null constraint: should be removed.
        if not draft.account_id:
            draft.account_id = "NA"
        return draft

    def get_stale_count(self):
        """Determine if the draft is out of date."""
        self.stale_count = 0
        if self.mhr_number and self.create_ts:
            try:
                query = text(QUERY_DRAFT_STALE_COUNT)
                result = db.session.execute(query, {"query_value1": self.mhr_number, "query_value2": self.create_ts})
                row = result.first()
                self.stale_count = int(row[0])
            except Exception as db_exception:  # noqa: B902; return nicer error
                logger.error("DB get_stale_count exception: " + str(db_exception))

    @staticmethod
    def find_draft(json_data, registration_type: str = None):
        """Try to find an existing draft if a draftNumber is in json_data.).

        Return None if not found or no documentId.
        """
        draft = None
        if json_data.get("draftNumber"):
            try:
                draft_number = json_data["draftNumber"].strip()
                if draft_number != "":
                    draft: MhrDraft = MhrDraft.find_by_draft_number(draft_number, False)
                    if draft:
                        draft.draft = json.dumps(json_data)
                        if registration_type:
                            draft.registration_type = registration_type
            except BusinessException:
                draft = None
        return draft
