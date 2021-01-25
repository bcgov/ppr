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

from enum import Enum
from http import HTTPStatus
import json

#from sqlalchemy import event

from .db import db

from ppr_api.utils.datetime import format_ts, now_ts, ts_from_iso_format
from ppr_api.exceptions import BusinessException

from .search import Search  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship

# temporary mock responses
import copy
from registry_schemas.example_data.ppr import FINANCING_STATEMENT_HISTORY



class SearchDetail(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains search results detail (search step 2) information."""

    __versioned__ = {}
    __tablename__ = 'search_audit_detail'


    search_detail_id = db.Column('search_detail_id', db.Integer, primary_key=True, 
                                 server_default=db.FetchedValue())
    search_select = db.Column('search_select', db.Text, nullable=False)
    search_response = db.Column('search_response', db.Text, nullable=False)

    # parent keys
    search_id = db.Column('search_id', db.Integer, 
                             db.ForeignKey('search_audit.search_id'), nullable=False)

    # Relationships - Search
    search = db.relationship("Search", foreign_keys=[search_id], 
                              back_populates="search_detail", cascade='all, delete', uselist=False)



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
    def find_by_id(cls, search_detail_id: int):
        """Return the search results detail matching the id."""
        search_detail = None
        if search_detail_id:
            search_detail = cls.query.get(search_detail_id)
        return search_detail


    @classmethod
    def find_by_search_id(cls, search_id: int):
        """Return the search detail record matching the search_id."""
        search_detail = None
        if search_id:
            search_detail = cls.query.filter(SearchDetail.search_id == search_id).one_or_none()

        return search_detail


    @staticmethod
    def create_from_json(search_json, search_id: int):
        """Create a search detail object from dict/json."""
        search = SearchDetail()
        search.search_id = search_id
        # TODO: replace with actual results build.
        search.search_response = json.dumps(copy.deepcopy(FINANCING_STATEMENT_HISTORY))
        search.search_select = json.dumps(search_json)

        return search


    @staticmethod
    def validate_search_select(json_data, search_id: int):
        """Perform any extra data validation here, either because it is too

        complicated for the schema, or because it requires existing data.
        """
        error_msg = ''

        search = Search.find_by_id(search_id)
        if not search:
            error_msg = f'Search select results failed: invalid search ID {search_id}.'
        else:
            # Check if search detail request already submitted.
            search_detail = SearchDetail.find_by_search_id(search_id)
            if search_detail:
                error_msg = f'Search select results failed: results already provided for search ID {search_id}.'

        if error_msg != '':
            raise BusinessException(
                error=error_msg,
                status_code=HTTPStatus.BAD_REQUEST
            )
