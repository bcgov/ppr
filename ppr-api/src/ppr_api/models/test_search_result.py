# Copyright © 2021 Province of British Columbia
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
"""This module holds model data and database operations for test search results."""

from __future__ import annotations
from typing import List

from enum import Enum

from .db import db


class TestSearchResult(db.Model):
    """This class maintains test search results detail information (for automated testing)."""

    class MatchType(Enum):
        """Render an enum of the search result match types."""

        EXACT = 'E'
        SIMILAR = 'S'

    class Source(Enum):
        """Render an enum of the search result sources."""

        API = 'api'
        LEGACY = 'legacy'

    __tablename__ = 'test_search_results'

    id = db.Column('id', db.Integer, db.Sequence('test_search_results_id_seq'), primary_key=True)
    doc_id = db.Column('doc_id', db.String(20), nullable=False)
    details = db.Column('details', db.Text, nullable=False)
    index = db.Column('index', db.Integer, nullable=False)
    match_type = db.Column('match_type', db.String(1), nullable=False)
    source = db.Column('source', db.String(10), nullable=False)

    # parent keys
    search_id = db.Column('search_id', db.Integer, db.ForeignKey('test_searches.id'), nullable=False, index=True)

    # relationships - test_search
    search = db.relationship('TestSearch', foreign_keys=[search_id],
                             back_populates='results', cascade='all, delete', uselist=False)

    @property
    def json(self) -> dict:
        """Return the result as a json object."""
        result = {
            'details': self.details,
            'documentId': self.doc_id,
            'id': self.id,
            'index': self.index,
            'matchType': self.match_type,
            'pairedIndex': self.paired_index,
            'source': self.source
        }

        return result

    @property
    def paired_index(self) -> int:
        """Return the index of the result from the other alg."""
        paired_match = db.session.query(TestSearchResult).filter(
            TestSearchResult.search_id == self.search_id,
            TestSearchResult.match_type == self.match_type,
            TestSearchResult.doc_id == self.doc_id,
            TestSearchResult.source != self.source
        ).one_or_none()

        if paired_match:
            return paired_match.index
        return -1

    @classmethod
    def find_by_id(cls, result_id: int = None) -> TestSearchResult:
        """Return a search result object by search result ID."""
        result = None
        if result_id:
            result = db.session.query(TestSearchResult).\
                        filter(TestSearchResult.id == result_id).one_or_none()

        return result

    @classmethod
    def find_all_by_search_id(cls, search_id: int = None) -> List[TestSearchResult]:
        """Return a list of search result objects by search ID."""
        results = []
        if search_id:
            results = db.session.query(TestSearchResult).\
                        filter(TestSearchResult.search_id == search_id).all()

        return results
