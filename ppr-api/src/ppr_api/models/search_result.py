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
"""This module holds model data and database operations for search results detail
    requests."""

from __future__ import annotations

from http import HTTPStatus
import json
import copy

#from sqlalchemy import event

from registry_schemas.example_data.ppr import FINANCING_STATEMENT_HISTORY
from ppr_api.exceptions import BusinessException

from .db import db
from .search_client import SearchClient  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship


class SearchResult(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains search results detail (search step 2) information."""

    __versioned__ = {}
    __tablename__ = 'search_result'


    search_id = db.Column('search_id', db.Integer, db.ForeignKey('search_client.search_id'),
                          primary_key=True, nullable=False)
    search_select = db.Column('results', db.Text, nullable=False)
    search_response = db.Column('registrations', db.Text, nullable=False)

    # parent keys

    # Relationships - Search
    search = db.relationship("SearchClient", foreign_keys=[search_id],
                             back_populates="search_result", cascade='all, delete', uselist=False)



    @property
    def json(self) -> dict:
        """Return the search query results as a json object."""
        result = None
        if self.search_response:
            result = json.loads(self.search_response)

        return result


    def save(self):
        """Render a search results detail information to the local cache."""

        db.session.add(self)
        db.session.commit()


    @classmethod
    def find_by_search_id(cls, search_id: int):
        """Return the search detail record matching the search_id."""
        search_detail = None
        if search_id:
            search_detail = cls.query.filter(SearchResult.search_id == search_id).one_or_none()

        return search_detail


    @staticmethod
    def create_from_json(search_json, search_id: int):
        """Create a search detail object from dict/json."""
        search = SearchResult()
        search.search_id = search_id
        # TODO: replace with actual results build.
        search.search_response = json.dumps(copy.deepcopy(FINANCING_STATEMENT_HISTORY))
        search.search_select = json.dumps(search_json)

        return search


    @staticmethod
    def validate_search_select(json_data, search_id: int):  # pylint: disable=unused-argument
        """Perform any extra data validation here, either because it is too

        complicated for the schema, or because it requires existing data.
        """
        error_msg = ''

        search = SearchClient.find_by_id(search_id)
        if not search:
            error_msg = f'Search select results failed: invalid search ID {search_id}.'
        else:
            # Check if search detail request already submitted.
            search_detail = SearchResult.find_by_search_id(search_id)
            if search_detail:
                error_msg = f'Search select results failed: results already provided for search ID {search_id}.'

        if error_msg != '':
            raise BusinessException(
                error=error_msg,
                status_code=HTTPStatus.BAD_REQUEST
            )
