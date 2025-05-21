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
"""This module holds model data and database operations for search queries."""
# flake8: noqa Q000,E122,E131
# Disable Q000: Allow query strings to be in double quotation marks that contain single quotation marks.
# Disable E122: allow query strings to be more human readable.
# Disable E131: allow query strings to be more human readable.
from __future__ import annotations

from enum import Enum
from http import HTTPStatus

from sqlalchemy.sql import text

from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.models import search_utils
from mhr_api.models import utils as model_utils
from mhr_api.utils.logging import logger

from .db import db

# Async search report status pending.
REPORT_STATUS_PENDING = "PENDING"
CHARACTER_SET_UNSUPPORTED = "The search name {} charcter set is not supported.\n"
PAY_PENDING: int = 1000


class SearchRequest(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains search query (search step 1) information."""

    class SearchTypes(str, Enum):
        """Render an Enum of the distinct MHR search types."""

        OWNER_NAME = "MI"
        ORGANIZATION_NAME = "MO"
        SERIAL_NUM = "MS"
        MANUFACTURED_HOME_NUM = "MM"

    __tablename__ = "search_requests"
    __allow_unmapped__ = True

    id = db.mapped_column("id", db.Integer, db.Sequence("search_id_seq"), primary_key=True)
    search_ts = db.mapped_column("search_ts", db.DateTime, nullable=False, index=True)
    search_type = db.mapped_column(
        "search_type", db.String(2), db.ForeignKey("search_types.search_type"), nullable=False
    )
    search_criteria = db.mapped_column("api_criteria", db.JSON, nullable=False)
    search_response = db.mapped_column("search_response", db.JSON, nullable=True)
    account_id = db.mapped_column("account_id", db.String(20), nullable=True, index=True)
    client_reference_id = db.mapped_column("client_reference_id", db.String(50), nullable=True)
    total_results_size = db.mapped_column("total_results_size", db.Integer, nullable=True)
    returned_results_size = db.mapped_column("returned_results_size", db.Integer, nullable=True)
    user_id = db.mapped_column("user_id", db.String(1000), nullable=True)
    updated_selection = db.mapped_column("updated_selection", db.JSON, nullable=True)

    pay_invoice_id = db.mapped_column("pay_invoice_id", db.Integer, nullable=True)
    pay_path = db.mapped_column("pay_path", db.String(256), nullable=True)

    # parent keys

    # Relationships - SearchResult
    search_result = db.relationship("SearchResult", back_populates="search", uselist=False)
    # Relationships - SearchType
    search_request_type = db.relationship(
        "SearchType", foreign_keys=[search_type], back_populates="search_request", cascade="all, delete", uselist=False
    )

    request_json = {}

    @property
    def json(self) -> dict:
        """Return the search query results as a json object."""
        result = {
            "searchId": str(self.id),
            "searchDateTime": model_utils.format_ts(self.search_ts),
            "totalResultsSize": self.total_results_size,
            "returnedResultsSize": self.returned_results_size,
            "maxResultsSize": search_utils.SEARCH_RESULTS_MAX_SIZE,
            "searchQuery": self.search_criteria,
        }
        if self.updated_selection:
            result["results"] = self.updated_selection
        elif self.search_response:
            result["results"] = self.search_response

        if self.pay_invoice_id and self.pay_path:
            payment = {"invoiceId": str(self.pay_invoice_id), "receipt": self.pay_path}
            result["payment"] = payment

        return result

    def save(self):
        """Render a search query to the local cache."""
        try:
            db.session.add(self)
            db.session.commit()
            logger.debug("DB search_request.save completed")
        except Exception as db_exception:
            logger.error("DB search_request save exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception

    def update_search_selection(self, search_json):
        """Support UI search selection autosave: replace search response."""
        # Audit requirement: save original search summary results (before consumer selects registrations to include).
        # API consumers could remove results.
        self.updated_selection = search_json
        self.save()

    def search_by_mhr_number(self):
        """Execute a search by mhr number query."""
        result = search_utils.search_by_mhr_number(self.request_json)
        row = None
        try:
            row = result.first()
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error("DB search_by_mhr_number exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception

        result_json = []
        if row is not None:
            result_json.append(search_utils.build_search_result_mhr(row))
            self.returned_results_size = 1
            self.total_results_size = 1
            self.search_response = result_json
        else:
            self.returned_results_size = 0
            self.total_results_size = 0

    def search_by_serial_number(self):
        """Execute a search query for a serial number search type."""
        result = search_utils.search_by_serial_number(self.request_json)
        rows = None
        try:
            rows = result.fetchall()
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error("DB search_by_serial_number exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception

        if rows is not None:
            results_json = []
            for row in rows:
                match = search_utils.build_search_result_serial(row)
                SearchRequest.update_result_matches(results_json, match, SearchRequest.SearchTypes.SERIAL_NUM)
            self.returned_results_size = len(results_json)
            self.total_results_size = self.returned_results_size
            self.search_response = results_json
        else:
            self.returned_results_size = 0
            self.total_results_size = 0

    def search_by_organization_name(self):
        """Execute a owner organization/business name search query."""
        result = search_utils.search_by_owner_business(self.request_json)
        rows = None
        try:
            rows = result.fetchall()
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error("DB search_by_owner_business exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception

        if rows is not None:
            results_json = []
            for row in rows:
                match = search_utils.build_search_result_owner_bus(row)
                SearchRequest.update_result_matches(results_json, match, SearchRequest.SearchTypes.ORGANIZATION_NAME)
            self.returned_results_size = len(results_json)
            self.total_results_size = self.returned_results_size
            self.search_response = results_json
        else:
            self.returned_results_size = 0
            self.total_results_size = 0

    def search_by_owner_name(self):
        """Execute a owner individual name search query."""
        result = search_utils.search_by_owner_individual(self.request_json)
        rows = None
        try:
            rows = result.fetchall()
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error("DB search_by_owner_individual exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception

        if rows is not None:
            results_json = []
            for row in rows:
                match = search_utils.build_search_result_owner_ind(row)
                SearchRequest.update_result_matches(results_json, match, SearchRequest.SearchTypes.OWNER_NAME)
            self.returned_results_size = len(results_json)
            self.total_results_size = self.returned_results_size
            self.search_response = results_json
        else:
            self.returned_results_size = 0
            self.total_results_size = 0

    def search(self):
        """Execute a search with the previously set search type and criteria."""
        if self.search_type == self.SearchTypes.MANUFACTURED_HOME_NUM:
            # Format before searching
            search_utils.format_mhr_number(self.request_json)

        if self.search_type == self.SearchTypes.MANUFACTURED_HOME_NUM:
            self.search_by_mhr_number()
        elif self.search_type == self.SearchTypes.SERIAL_NUM:
            self.search_by_serial_number()
        elif self.search_type == self.SearchTypes.ORGANIZATION_NAME:
            self.search_by_organization_name()
        elif self.search_type == self.SearchTypes.OWNER_NAME:
            self.search_by_owner_name()
        else:
            raise DatabaseException("SearchRequest.search PosgreSQL not yet implemented.")
        self.save()

    @classmethod
    def update_result_matches(cls, results, result, search_type: str) -> bool:
        """If identical mhr number and result criteria exists update the count instead of adding a result."""
        updated: bool = False
        for existing in results:
            if existing.get("mhrNumber") == result.get("mhrNumber"):
                if search_type == cls.SearchTypes.ORGANIZATION_NAME and existing.get("organizationName") == result.get(
                    "organizationName"
                ):
                    updated = True
                elif search_type == cls.SearchTypes.OWNER_NAME and existing.get("ownerName") == result.get("ownerName"):
                    updated = True
                elif search_type == cls.SearchTypes.SERIAL_NUM:
                    updated = True
                    existing["serialNumber"] = existing["serialNumber"] + ", " + result.get("serialNumber")
                if updated:
                    if result.get("activeCount") == 1:
                        existing["activeCount"] = existing["activeCount"] + 1
                    elif search_type != cls.SearchTypes.SERIAL_NUM and result.get("exemptCount") == 1:
                        existing["exemptCount"] = existing["exemptCount"] + 1
                    elif search_type != cls.SearchTypes.SERIAL_NUM and result.get("historicalCount") == 1:
                        existing["historicalCount"] = existing["historicalCount"] + 1
        if not updated:
            results.append(result)
        return updated

    @classmethod
    def find_by_id(cls, search_id: int):
        """Return the search query matching the id."""
        search = None
        if search_id:
            search = db.session.query(SearchRequest).filter(SearchRequest.id == search_id).one_or_none()
        return search

    @classmethod
    def find_all_by_account_id(
        cls, account_id: str = None, from_ui: bool = False
    ):  # pylint: disable=too-many-branches, too-many-locals
        """Return a search history summary list of searches executed by an account."""
        history_list = []
        if account_id:
            query = search_utils.ACCOUNT_SEARCH_HISTORY_DATE_QUERY.replace("?", account_id)
            if from_ui:
                query = search_utils.ACCOUNT_SEARCH_HISTORY_DATE_QUERY_NEW.replace("?", account_id)
            if search_utils.GET_HISTORY_DAYS_LIMIT <= 0:
                query = search_utils.ACCOUNT_SEARCH_HISTORY_QUERY.replace("?", account_id)
                if from_ui:
                    query = search_utils.ACCOUNT_SEARCH_HISTORY_QUERY_NEW.replace("?", account_id)
            rows = None
            try:
                result = db.session.execute(text(query))
                rows = result.fetchall()
            except Exception as db_exception:  # noqa: B902; return nicer error
                logger.error("DB find_all_by_account_id exception: " + str(db_exception))
                raise DatabaseException(db_exception) from db_exception
            if rows is not None:
                for row in rows:
                    search_id = str(row[0])
                    # Set to pending if async report is not yet available.
                    callback_url = str(row[6])
                    search_ts = row[1]
                    doc_storage_url = str(row[7])
                    if (
                        callback_url is not None
                        and callback_url.lower() != "none"
                        and (doc_storage_url is None or doc_storage_url.lower() == "none")
                    ):
                        search_id += "_" + REPORT_STATUS_PENDING
                    search = {
                        "searchId": search_id,
                        "searchDateTime": model_utils.format_ts(search_ts),
                        "searchQuery": row[2],
                        "totalResultsSize": int(row[3]),
                        "returnedResultsSize": int(row[4]),
                        "username": str(row[10]),
                    }
                    if from_ui:
                        # if api_result is null then the selection has not been saved.
                        search["inProgress"] = not row[8] and row[8] != [] and search["totalResultsSize"] > 0
                        search["userId"] = str(row[5])
                        if row[11] and int(row[11]) == PAY_PENDING:
                            search["paymentPending"] = True
                            search["invoiceId"] = str(row[12]) if row[12] else ""
                            search["reportAvailable"] = False
                        elif not search.get("inProgress") and (
                            (doc_storage_url and doc_storage_url.lower() != "none")
                            or model_utils.report_retry_elapsed(search_ts)
                        ):
                            search["reportAvailable"] = True
                        else:
                            search["reportAvailable"] = False
                    history_list.append(search)
        return history_list

    @staticmethod
    def create_from_json(search_json, account_id: str = None, user_id: str = None):
        """Create a search object from dict/json."""
        new_search = SearchRequest()
        new_search.request_json = search_json
        search_type = search_json["type"]
        new_search.search_type = model_utils.TO_DB_SEARCH_TYPE[search_type]
        new_search.search_criteria = search_json
        new_search.search_ts = model_utils.now_ts()
        if account_id:
            new_search.account_id = account_id
        if "clientReferenceId" in search_json and search_json["clientReferenceId"].strip() != "":
            new_search.client_reference_id = search_json["clientReferenceId"]
        new_search.user_id = user_id
        return new_search

    @staticmethod
    def validate_query(json_data):  # pylint: disable=too-many-branches
        """Perform any extra data validation here, either because it is too complicated for the schema.

        Or because it requires existing data.
        """
        error_msg = ""
        # validate search type - criteria combinations
        search_type: str = json_data["type"]
        if len(search_type) != 2:
            search_type = model_utils.TO_DB_SEARCH_TYPE[search_type]
        if search_type == SearchRequest.SearchTypes.OWNER_NAME:
            if "ownerName" not in json_data["criteria"]:
                error_msg += f"Search criteria ownerName is required for search type {search_type}. "
            elif "last" not in json_data["criteria"]["ownerName"]:
                error_msg += f"Search criteria ownerName last is required for search type {search_type}. "
            elif "first" not in json_data["criteria"]["ownerName"]:
                error_msg += f"Search criteria ownerName first is required for search type {search_type}. "
        elif "value" not in json_data["criteria"]:
            error_msg += f"Search criteria value is required for search type {search_type}. "

        if error_msg != "":
            raise BusinessException(error=error_msg, status_code=HTTPStatus.BAD_REQUEST)
