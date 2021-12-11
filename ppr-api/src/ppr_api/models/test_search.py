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
"""This module holds model data and database operations for test searches."""

from __future__ import annotations

from typing import List

from .db import db
from .test_search_result import TestSearchResult


class TestSearch(db.Model):
    """This class maintains test searches detail information (for automated testing)."""

    __tablename__ = 'test_searches'

    id = db.Column('id', db.Integer, db.Sequence('test_searches_id_seq'), primary_key=True)
    search_criteria = db.Column('search_criteria', db.Text, nullable=False)
    run_time = db.Column('run_time', db.Float, nullable=False)

    # parent keys
    batch_id = db.Column('batch_id', db.Integer, db.ForeignKey('test_search_batches.id'), nullable=False, index=True)

    # relationships - test_search_batch
    search_batch = db.relationship('TestSearchBatch', foreign_keys=[batch_id],
                                   back_populates='searches', cascade='all, delete', uselist=False)

    # relationships - test_search_results
    results = db.relationship('TestSearchResult', back_populates='search')

    @property
    def json(self) -> dict:
        """Return the search as a json object."""
        search = {
            'criteria': self.search_criteria,
            'matchesExact': {
                'avgIndexDiff': self.avg_index_diff(TestSearchResult.MatchType.EXACT.value),
                'firstFailIndex': self.fail_index(TestSearchResult.MatchType.EXACT.value),
                'missedMatches': self.missed_matches(TestSearchResult.MatchType.EXACT.value),
                'resultsApi': self.get_results(
                    TestSearchResult.MatchType.EXACT.value, TestSearchResult.Source.API.value),
                'resultsLegacy': self.get_results(
                    TestSearchResult.MatchType.EXACT.value, TestSearchResult.Source.LEGACY.value)
            },
            'matchesSimilar': {
                'avgIndexDiff': self.avg_index_diff(TestSearchResult.MatchType.SIMILAR.value),
                'firstFailIndex': self.fail_index(TestSearchResult.MatchType.SIMILAR.value),
                'missedMatches': self.missed_matches(TestSearchResult.MatchType.SIMILAR.value),
                'resultsApi': self.get_results(
                    TestSearchResult.MatchType.SIMILAR.value, TestSearchResult.Source.API.value),
                'resultsLegacy': self.get_results(
                    TestSearchResult.MatchType.SIMILAR.value, TestSearchResult.Source.LEGACY.value)
            },
            'runTime': self.run_time,
        }

        search['matchesExact']['passed'] = (
            len(search['matchesExact']['missedMatches']) == 0 and
            search['matchesExact']['firstFailIndex'] == -1
        )
        search['matchesSimilar']['passed'] = (
            len(search['matchesSimilar']['missedMatches']) == 0 and
            search['matchesSimilar']['firstFailIndex'] == -1
        )

        return search

    def avg_index_diff(self, match_type) -> float:
        """Return the average index diff between api/legacy results. Excludes missed results."""
        api_results = self.get_results(match_type, TestSearchResult.Source.API.value)
        total_diff = 0
        total_paired_results = 0
        for result in api_results:
            if result['pairedIndex'] != -1:
                total_diff += abs(result['index'] - result['pairedIndex'])
                total_paired_results += 1
        return total_diff / total_paired_results

    def fail_index(self, match_type) -> int:
        """Return the first index that diffs between api/legacy results. Includes missed results."""
        api_results = self.get_results(match_type, TestSearchResult.Source.API.value)
        for result in api_results:
            if result['pairedIndex'] != result['index']:
                return result['index']
        return -1

    def get_results(self, match_type, source) -> list[dict]:
        """Return results list of this search with given match type and source."""
        results = db.session.query(TestSearchResult).filter(
            TestSearchResult.search_id == self.id,
            TestSearchResult.match_type == match_type,
            TestSearchResult.source == source
        ).order_by(TestSearchResult.index.asc())

        results_json = []
        for result in results:
            results_json.append(result.json)
        return results_json

    def missed_matches(self, match_type) -> list:
        """Return the missed matches for the given match type."""
        missed = []
        for result in self.get_results(match_type, TestSearchResult.Source.LEGACY.value):
            if result['pairedIndex'] == -1:
                missed.append(result)
        return missed

    def save(self):
        """Render a search to the local cache."""
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, search_id: int = None) -> TestSearch:
        """Return a search object by search ID."""
        search = None
        if search_id:
            search = db.session.query(TestSearch).\
                        filter(TestSearch.id == search_id).one_or_none()

        return search

    @classmethod
    def find_all_by_batch_id(cls, batch_id: int = None) -> List[TestSearch]:
        """Return a list of search objects by batch ID."""
        searches = []
        if batch_id:
            searches = db.session.query(TestSearch).\
                        filter(TestSearch.batch_id == batch_id).all()

        return searches
