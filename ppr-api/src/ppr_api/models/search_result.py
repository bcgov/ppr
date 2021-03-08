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
"""This module holds model data and database operations for search results detail requests."""

from __future__ import annotations

from http import HTTPStatus
import json

# from sqlalchemy import event
from flask import current_app

from ppr_api.exceptions import BusinessException
from ppr_api.models.utils import REG_CLASS_TO_STATEMENT_TYPE  # , format_ts

from .db import db
# from .search_client import SearchClient
from .financing_statement import FinancingStatement


class SearchResult(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains search results detail (search step 2) information."""

    __versioned__ = {}
    __tablename__ = 'search_result'

    search_id = db.Column('search_id', db.Integer, db.ForeignKey('search_client.search_id'),
                          primary_key=True, nullable=False)
    search_select = db.Column('api_result', db.Text, nullable=False)
    search_response = db.Column('registrations', db.Text, nullable=False)
    jaro = db.Column('jaro', db.Integer, nullable=True)
    match = db.Column('match', db.String(1), nullable=True)
    result_id = db.Column('result_id', db.Integer, nullable=True)
    result = db.Column('result', db.String(150), nullable=True)

    # parent keys

    # Relationships - Search
    search = db.relationship('SearchClient', foreign_keys=[search_id],
                             back_populates='search_result', cascade='all, delete', uselist=False)

    @property
    def json(self) -> dict:
        """Return the search query results as a json object."""
        result = None
        if self.search_response:
            result = json.loads(self.search_response)

        return result

    def save(self):
        """Render a search results detail information to the local cache."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:
            current_app.logger.error('DB search_result save exception: ' + repr(db_exception))
            raise BusinessException(
                error='Database search_result save failed: ' + repr(db_exception),
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR
            )

    def update_selection(self):
        """Update the set of search details from the search query selection.

        Remove financing statements that are not in the search query selection.
        """
        results = json.loads(self.search_response)
        selected = self.search_select
        new_results = []
        exact_count = 0
        similar_count = 0
        for result in results:
            found = False
            reg_num = result['financingStatement']['baseRegistrationNumber']
            for select in selected:
                if select['baseRegistrationNumber'] == reg_num:
                    found = True
                    if select['matchType'] == 'EXACT':
                        exact_count += 1
                    else:
                        similar_count += 1
            if found:
                new_results.append(result)

        # current_app.logger.debug('exact_count=' + str(exact_count) + ' similar_count=' + str(similar_count))
        self.search_response = json.dumps(new_results)
        self.search_select = json.dumps(selected)
        # current_app.logger.debug('saving updates')
        self.save()

    @classmethod
    def find_by_search_id(cls, search_id: int):
        """Return the search detail record matching the search_id."""
        search_detail = None
        if search_id:
            search_detail = cls.query.filter(SearchResult.search_id == search_id).one_or_none()

        return search_detail

    @staticmethod
    def create_from_search_query(search_query):
        """Create a search detail object from the inital search query with no search selection criteria."""
        search_result = SearchResult()
        search_result.search_id = search_query.search_id
        query_results = json.loads(search_query.search_response)
        detail_results = []
        for result in query_results:
            reg_num = result['baseRegistrationNumber']
            found = False
            # Check for duplicates
            if detail_results:
                for statement in detail_results:
                    if statement['financingStatement']['baseRegistrationNumber'] == reg_num:
                        found = True
            if not found:
                financing = FinancingStatement.find_by_registration_number(reg_num, staff=False, allow_historical=True)
                # Special business rule: if search is by serial number, only include
                # serial_collateral records where the serial number is an exact match.
                # Do not include general_collateral records.
                financing_json = {
                    'financingStatement': financing.json
                }
                # Build an array of changes
                changes = []
                if financing.registration:
                    for reg in financing.registration:
                        if reg.registration_num != financing.registration_num:
                            statement_json = reg.json
                            statement_json['statementType'] = REG_CLASS_TO_STATEMENT_TYPE[reg.registration_type_cl]
                            changes.append(statement_json)
                if changes:
                    financing_json['financingStatement']['changes'] = changes
                detail_results.append(financing_json)

        search_result.search_response = json.dumps(detail_results)
        return search_result

    @staticmethod
    def create_from_json(search_json, search_id: int):
        """Create a search detail object from dict/json specifying the search selection."""
        search = SearchResult()
        search.search_id = search_id
        search.search_select = json.dumps(search_json)
        detail_results = []
        for result in search_json:
            reg_num = result['baseRegistrationNumber']
            financing = FinancingStatement.find_by_registration_number(reg_num, staff=False, allow_historical=True)
            # Special business rule: if search is by serial number, only include
            # serial_collateral records where the serial number is an exact match.
            # Do not include general_collateral records.
            financing_json = {
                'financingStatement': financing.json
            }
            # Build an array of changes
            changes = []
            if financing.registration:
                for reg in financing.registration:
                    if reg.registration_num != financing.registration_num:
                        statement_json = reg.json
                        statement_json['statementType'] = REG_CLASS_TO_STATEMENT_TYPE[reg.registration_type_cl]
                        changes.append(statement_json)
            if changes:
                financing_json['financingStatement']['changes'] = changes
            detail_results.append(financing_json)
        search.search_response = json.dumps(detail_results)

        return search

    @staticmethod
    def validate_search_select(select_json, search_id: int):  # pylint: disable=unused-argument
        """Perform any extra data validation here.

        Either because it is too complicated for the schema, or because it requires existing data.
        Also fetch the existing search_detail record and verify a previous search detail request on
        the same search ID has not been submitted.
        """
        error_msg = ''

        search_result = SearchResult.find_by_search_id(search_id)
        if not search_result:
            error_msg = f'Search select results failed: invalid search ID {search_id}.'
        elif search_result.search_select:
            # Search detail request already submitted.
            error_msg = f'Search select results failed: results already provided for search ID {search_id}.'

        if error_msg != '':
            raise BusinessException(
                error=error_msg,
                status_code=HTTPStatus.BAD_REQUEST
            )

        search_result.search_select = select_json
        return search_result
