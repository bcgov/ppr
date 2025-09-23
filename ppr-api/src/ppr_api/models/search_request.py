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

from http import HTTPStatus

from flask import current_app
from sqlalchemy.sql import text

from ppr_api.exceptions import BusinessException, DatabaseException
from ppr_api.models import search_utils
from ppr_api.models import utils as model_utils
from ppr_api.models.search_utils import AccountSearchParams
from ppr_api.utils.base import BaseEnum
from ppr_api.utils.logging import logger
from ppr_api.utils.validators import valid_charset

from .db import db

# Async search report status pending.
REPORT_STATUS_PENDING = "PENDING"
CHARACTER_SET_UNSUPPORTED = "The search name {} charcter set is not supported.\n"
PAY_PENDING: int = 1000


class SearchRequest(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains search query (search step 1) information."""

    class SearchTypes(BaseEnum):
        """Render an Enum of the search types."""

        AIRCRAFT_AIRFRAME_DOT = "AC"
        BUSINESS_DEBTOR = "BS"
        INDIVIDUAL_DEBTOR = "IS"
        REGISTRATION_NUM = "RG"
        SERIAL_NUM = "SS"
        MANUFACTURED_HOME_NUM = "MH"

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
    search_value = db.mapped_column("search_value", db.String(320), nullable=True, index=True)

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
        if self.search_result and self.search_result.is_payment_pending():
            result["paymentPending"] = True
            result["results"] = []
        elif self.updated_selection:
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
        except Exception as db_exception:
            logger.error("DB search_client save exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception

    def update_search_selection(self, search_json):
        """Support UI search selection autosave: replace search response."""
        # Audit requirement: save original search summary results (before consumer selects registrations to include).
        # API consumers could remove results.
        self.updated_selection = search_json
        self.save()

    def search_by_registration_number(self):
        """Execute a search by registration number query."""
        reg_num = self.request_json["criteria"]["value"]
        row = None
        try:
            result = db.session.execute(text(search_utils.REG_NUM_QUERY), {"query_value": reg_num.strip().upper()})
            row = result.first()
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error("DB search_by_registration_number exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception

        if row is not None:
            registration_type = str(row[0])
            # Remove state check for now - let the DB view take care of it.
            timestamp = row[1]
            result_json = [
                {
                    "baseRegistrationNumber": str(row[2]),
                    "matchType": str(row[3]),
                    "createDateTime": model_utils.format_ts(timestamp),
                    "registrationType": registration_type,
                }
            ]
            if reg_num != str(row[2]):
                result_json[0]["registrationNumber"] = reg_num

            self.returned_results_size = 1
            self.total_results_size = 1
            self.search_response = result_json
        else:
            self.returned_results_size = 0
            self.total_results_size = 0

    def search_by_serial_type(self):
        """Execute a search query for either an aircraft DOT, MHR number, or serial number search type."""
        search_value = self.request_json["criteria"]["value"]
        query = search_utils.SERIAL_NUM_QUERY
        if self.search_type == "MH":
            query = search_utils.MHR_NUM_QUERY
            query = query.replace("CASE WHEN serial_number", "CASE WHEN mhr_number")
        elif self.search_type == "AC":
            query = search_utils.AIRCRAFT_DOT_QUERY
        rows = None
        try:
            result = db.session.execute(text(query), {"query_value": search_value.strip().upper()})
            rows = result.fetchall()
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error("DB search_by_serial_type exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception
        if rows is not None:
            results_json = []
            for row in rows:
                registration_type = str(row[0])
                timestamp = row[1]
                collateral = {"type": str(row[2]), "serialNumber": str(row[3])}
                value = row[4]
                if value is not None:
                    collateral["year"] = int(value)
                value = row[5]
                if value is not None:
                    collateral["make"] = str(value)
                value = row[6]
                if value is not None:
                    collateral["model"] = str(value)
                match_type = str(row[8])
                if self.search_type == "MH":
                    collateral["manufacturedHomeRegistrationNumber"] = str(row[12])
                result_json = {
                    "baseRegistrationNumber": str(row[7]),
                    "matchType": match_type,
                    "createDateTime": model_utils.format_ts(timestamp),
                    "registrationType": registration_type,
                    "vehicleCollateral": collateral,
                }
                results_json.append(result_json)

            self.returned_results_size = len(results_json)
            self.total_results_size = self.returned_results_size
            if self.returned_results_size > 0:
                self.search_response = results_json
        else:
            self.returned_results_size = 0
            self.total_results_size = 0

    def search_by_business_name(self):
        """Execute a debtor business name search query."""
        search_value = self.request_json["criteria"]["debtorName"]["business"]
        rows = None
        try:
            result = db.session.execute(
                text(search_utils.BUSINESS_NAME_QUERY),
                {
                    "query_bus_name": search_value.strip().upper(),
                    "query_bus_quotient": current_app.config.get("SIMILARITY_QUOTIENT_BUSINESS_NAME"),
                },
            )
            rows = result.fetchall()
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error("DB search_by_business_name exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception
        if rows is not None:
            results_json = []
            for row in rows:
                registration_type = str(row[0])
                timestamp = row[1]
                debtor = {"businessName": str(row[2]), "partyId": int(row[7])}
                result_json = {
                    "baseRegistrationNumber": str(row[3]),
                    "matchType": str(row[4]),
                    "createDateTime": model_utils.format_ts(timestamp),
                    "registrationType": registration_type,
                    "debtor": debtor,
                }
                results_json.append(result_json)

            self.returned_results_size = len(results_json)
            self.total_results_size = self.returned_results_size
            if self.returned_results_size > 0:
                self.search_response = results_json
        else:
            self.returned_results_size = 0
            self.total_results_size = 0

    def search_by_individual_name(self):  # pylint: disable=too-many-locals; easier to follow
        """Execute a debtor individual name search query."""
        result = None
        middle_name = None
        last_name = self.request_json["criteria"]["debtorName"]["last"]
        first_name = self.request_json["criteria"]["debtorName"]["first"]
        quotient_first = current_app.config.get("SIMILARITY_QUOTIENT_FIRST_NAME")
        quotient_last = current_app.config.get("SIMILARITY_QUOTIENT_LAST_NAME")
        quotient_default = current_app.config.get("SIMILARITY_QUOTIENT_DEFAULT")
        if "second" in self.request_json["criteria"]["debtorName"]:
            middle_name = self.request_json["criteria"]["debtorName"]["second"]
        rows = None
        try:
            if middle_name is not None and middle_name.strip() != "" and middle_name.strip().upper() != "NONE":
                result = db.session.execute(
                    text(search_utils.INDIVIDUAL_NAME_MIDDLE_QUERY),
                    {
                        "query_last": last_name.strip().upper(),
                        "query_first": first_name.strip().upper(),
                        "query_middle": middle_name.strip().upper(),
                        "query_last_quotient": quotient_last,
                        "query_first_quotient": quotient_first,
                        "query_default_quotient": quotient_default,
                    },
                )
            else:
                result = db.session.execute(
                    text(search_utils.INDIVIDUAL_NAME_QUERY),
                    {
                        "query_last": last_name.strip().upper(),
                        "query_first": first_name.strip().upper(),
                        "query_last_quotient": quotient_last,
                        "query_first_quotient": quotient_first,
                        "query_default_quotient": quotient_default,
                    },
                )
            rows = result.fetchall()
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error("DB search_by_individual_name exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception
        if rows is not None:
            results_json = []
            for row in rows:
                registration_type = str(row[0])
                timestamp = row[1]
                person = {"last": str(row[2]), "first": str(row[3])}
                if row[4]:
                    person["middle"] = str(row[4])
                debtor = {"personName": person, "partyId": int(row[5])}
                if row[10]:
                    debtor["birthDate"] = model_utils.format_ts(row[10])
                result_json = {
                    "baseRegistrationNumber": str(row[6]),
                    "matchType": str(row[7]),
                    "createDateTime": model_utils.format_ts(timestamp),
                    "registrationType": registration_type,
                    "debtor": debtor,
                }
                results_json.append(result_json)

            self.returned_results_size = len(results_json)
            self.total_results_size = self.returned_results_size
            if self.returned_results_size > 0:
                self.search_response = results_json
        else:
            self.returned_results_size = 0
            self.total_results_size = 0

    def get_total_count(self):
        """Execute a search to get the total match count for the search criteria. Only call if limit reached."""
        query_text = search_utils.COUNT_QUERY_FROM_SEARCH_TYPE[self.search_type]
        if query_text:
            count_query = text(query_text)
            result = None
            if self.search_type == self.SearchTypes.BUSINESS_DEBTOR.value:
                search_value = self.request_json["criteria"]["debtorName"]["business"]
                quotient = current_app.config.get("SIMILARITY_QUOTIENT_BUSINESS_NAME")
                result = db.session.execute(
                    count_query, {"query_bus_name": search_value, "query_bus_quotient": quotient}
                )
            elif self.search_type == self.SearchTypes.INDIVIDUAL_DEBTOR.value:
                last_name = self.request_json["criteria"]["debtorName"]["last"]
                first_name = self.request_json["criteria"]["debtorName"]["first"]
                quotient_first = current_app.config.get("SIMILARITY_QUOTIENT_FIRST_NAME")
                quotient_last = current_app.config.get("SIMILARITY_QUOTIENT_LAST_NAME")
                quotient_default = current_app.config.get("SIMILARITY_QUOTIENT_DEFAULT")
                result = db.session.execute(
                    count_query,
                    {
                        "query_last": last_name.strip().upper(),
                        "query_first": first_name.strip().upper(),
                        "query_first_quotient": quotient_first,
                        "query_last_quotient": quotient_last,
                        "query_default_quotient": quotient_default,
                    },
                )
            else:
                search_value = self.request_json["criteria"]["value"]
                result = db.session.execute(count_query, {"query_value": search_value})

            if result:
                row = result.first()
                self.total_results_size = int(row[0])

    def search(self):
        """Execute a search with the previously set search type and criteria."""
        if self.search_type == self.SearchTypes.REGISTRATION_NUM.value:
            self.search_by_registration_number()
        elif self.search_type == self.SearchTypes.MANUFACTURED_HOME_NUM.value:
            # Format before searching
            search_utils.format_mhr_number(self.request_json)
            self.search_by_serial_type()
        elif self.search_type in (self.SearchTypes.SERIAL_NUM.value, self.SearchTypes.AIRCRAFT_AIRFRAME_DOT.value):
            self.search_by_serial_type()
        elif self.search_type == self.SearchTypes.BUSINESS_DEBTOR.value:
            self.search_by_business_name()
        else:
            self.search_by_individual_name()
        self.save()

    @classmethod
    def find_by_id(cls, search_id: int):
        """Return the search query matching the id."""
        search = None
        if search_id:
            search = db.session.query(SearchRequest).filter(SearchRequest.id == search_id).one_or_none()
        return search

    @classmethod
    def find_all_by_account_id(cls, params: AccountSearchParams):
        """Return a search history summary list of searches executed by an account."""
        history_list = []
        query: str = search_utils.build_search_history_query(params)
        logger.info(query)
        query_params = search_utils.build_account_query_params(params)
        logger.info(query_params)
        rows = None
        from_ui: bool = params.from_ui is not None and params.from_ui
        count = SearchRequest.get_account_history_count(params.account_id)
        # logger.info(f"count={count}")
        if count < 1:
            return history_list
        try:
            result = db.session.execute(text(query), query_params)
            rows = result.fetchall()
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error("DB find_all_by_account_id exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception
        if rows is not None:
            for row in rows:
                history_list.append(build_search_history_json(row, from_ui))
        if history_list:
            history_list[0]["searchHistoryTotal"] = count
        return history_list

    @classmethod
    def get_account_history_count(cls, account_id: str) -> int:
        """Get the total number of available search results for an account."""
        count: int = 0
        result = db.session.execute(text(search_utils.QUERY_ACCOUNT_HISTORY_TOTAL), {"query_account": account_id})
        row = result.first()
        count = int(row[0])
        return count

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
        if search_json["criteria"].get("value"):
            new_search.search_value = str(search_json["criteria"]["value"]).upper().strip()
        elif search_json["criteria"].get("debtorName"):
            if search_json["criteria"]["debtorName"].get("business"):
                new_search.search_value = str(search_json["criteria"]["debtorName"].get("business")).upper().strip()
            elif search_json["criteria"]["debtorName"].get("last"):
                ind_name: str = str(search_json["criteria"]["debtorName"].get("first")).strip()
                if search_json["criteria"]["debtorName"].get("middle"):
                    ind_name += " " + str(search_json["criteria"]["debtorName"].get("middle")).strip()
                ind_name += " " + str(search_json["criteria"]["debtorName"].get("last")).strip()
                new_search.search_value = ind_name.upper()
        return new_search

    @staticmethod
    def validate_query(json_data):  # pylint: disable=too-many-branches
        """Perform any extra data validation here, either because it is too complicated for the schema.

        Or because it requires existing data.
        """
        error_msg = ""
        # validate search type - criteria combinations
        search_type = json_data["type"]
        if search_type not in ("INDIVIDUAL_DEBTOR", "BUSINESS_DEBTOR"):
            if "value" not in json_data["criteria"]:
                error_msg += f"Search criteria value is required for search type {search_type}. "
        else:
            if "debtorName" not in json_data["criteria"]:
                error_msg += f"Search criteria debtorName is required for search type {search_type}. "
            elif search_type == "INDIVIDUAL_DEBTOR" and "last" not in json_data["criteria"]["debtorName"]:
                error_msg += f"Search criteria debtorName last is required for search type {search_type}. "
            elif search_type == "BUSINESS_DEBTOR" and "business" not in json_data["criteria"]["debtorName"]:
                error_msg += f"Search criteria debtorName businessName is required for search type {search_type}. "
            error_msg += SearchRequest.validate_debtor_name(json_data)

        # Verify the start and end dates.
        if "startDateTime" in json_data or "startDateTime" in json_data:
            now = model_utils.now_ts()
            ts_start = None
            ts_end = None
            if "startDateTime" in json_data:
                ts_start = model_utils.ts_from_iso_format(json_data["startDateTime"])
                if ts_start > now:
                    error_msg = error_msg + "Search startDateTime invalid: it cannot be in the future. "
            if "endDateTime" in json_data:
                ts_end = model_utils.ts_from_iso_format(json_data["endDateTime"])
                if ts_end > now:
                    error_msg = error_msg + "Search endDateTime invalid: it cannot be in the future. "

            if ts_start and ts_end and ts_start > ts_end:
                error_msg = error_msg + "Search date range invalid: startDateTime cannot be after endDateTime. "

        if error_msg != "":
            raise BusinessException(error=error_msg, status_code=HTTPStatus.BAD_REQUEST)

    @staticmethod
    def validate_debtor_name(json_data):
        """Verify search debtor name is valid."""
        error_msg = ""
        if "criteria" in json_data and "debtorName" in json_data["criteria"]:
            debtor_json = json_data["criteria"]["debtorName"]
            name = debtor_json.get("business", None)
            if name and not valid_charset(name):
                error_msg += CHARACTER_SET_UNSUPPORTED.format(name)
            name = debtor_json.get("first", None)
            if name and not valid_charset(name):
                error_msg += CHARACTER_SET_UNSUPPORTED.format(name)
            name = debtor_json.get("middle", None)
            if name and not valid_charset(name):
                error_msg += CHARACTER_SET_UNSUPPORTED.format(name)
            name = debtor_json.get("last", None)
            if name and not valid_charset(name):
                error_msg += CHARACTER_SET_UNSUPPORTED.format(name)
        return error_msg


@staticmethod
def build_search_history_query(account_id: str, history_params) -> str:
    """Build the account search history query based on the request parameters."""
    from_ui: bool = history_params.get("from_ui")
    query: str = search_utils.ACCOUNT_SEARCH_HISTORY_DATE_QUERY
    if search_utils.GET_HISTORY_DAYS_LIMIT <= 0 and from_ui:
        query = search_utils.ACCOUNT_SEARCH_HISTORY_QUERY_NEW
    elif search_utils.GET_HISTORY_DAYS_LIMIT <= 0:
        query = search_utils.ACCOUNT_SEARCH_HISTORY_QUERY
    elif from_ui:
        query = search_utils.ACCOUNT_SEARCH_HISTORY_DATE_QUERY_NEW
    query += search_utils.QUERY_ACCOUNT_HISTORY_LIMIT
    return query


@staticmethod
def build_search_history_json(row, from_ui: bool) -> dict:
    """Build the account search history query based on the request parameters."""
    search_id: str = str(row[0])
    search_ts = row[1]
    # Signal UI report pending if async report is not yet available.
    if row[7] is not None and row[8] is None:
        search_id += "_" + REPORT_STATUS_PENDING
    search = {
        "searchId": search_id,
        "searchDateTime": model_utils.format_ts(search_ts),
        "searchQuery": row[2],
        "totalResultsSize": int(row[3]),
        "returnedResultsSize": int(row[4]),
        "exactResultsSize": int(row[5]) if row[5] else 0,
        "selectedResultsSize": int(row[9]) if row[9] else 0,
        "username": str(row[10]),
    }
    if from_ui:
        # if api_result is null then the selections have not been finished
        search["inProgress"] = not row[11] and row[11] != [] and search["totalResultsSize"] > 0
        search["userId"] = str(row[12])
        if row[13] and int(row[13]) == PAY_PENDING:
            search["paymentPending"] = True
            search["invoiceId"] = str(row[14]) if row[14] else ""
            search["reportAvailable"] = False
        elif not search.get("inProgress") and (row[8] or model_utils.report_retry_elapsed(search_ts)):
            search["reportAvailable"] = True
        else:
            search["reportAvailable"] = False
    return search
