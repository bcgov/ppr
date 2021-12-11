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
"""This module holds model data and database operations for test search batches."""

from __future__ import annotations

from datetime import datetime
from typing import List

from ppr_api.models import utils as model_utils
from ppr_api.models.search_request import SearchRequest

from .db import db


class TestSearchBatch(db.Model):
    """This class maintains test search batches detail information (for automated testing)."""

    __tablename__ = 'test_search_batches'

    id = db.Column('id', db.Integer, db.Sequence('test_search_batches_id_seq'), primary_key=True)
    search_type = db.Column('search_type', db.String(2), db.ForeignKey('search_types.search_type'), nullable=False)
    test_date = db.Column('test_date', db.DateTime, nullable=False)
    sim_val_business = db.Column('sim_val_business', db.Float, nullable=True)
    sim_val_first_name = db.Column('sim_val_first_name', db.Float, nullable=True)
    sim_val_last_name = db.Column('sim_val_last_name', db.Float, nullable=True)

    # parent keys

    # relationships - test_search
    searches = db.relationship('TestSearch', back_populates='search_batch')

    @property
    def json(self) -> dict:
        """Return the search batch as a json object."""
        batch = {
            'searchType': self.search_type,
            'date': model_utils.format_ts(self.test_date)
        }
        if self.search_type == SearchRequest.SearchTypes.BUSINESS_DEBTOR.value:
            batch['similarityValue'] = self.sim_val_business
        elif self.search_type == SearchRequest.SearchTypes.INDIVIDUAL_DEBTOR.value:
            batch['similarityValueFirst'] = self.sim_val_first_name
            batch['similarityValueLast'] = self.sim_val_last_name

        searches = []
        for search in self.searches:
            searches.append(search.json)

        batch['searches'] = searches

        return batch

    def save(self):
        """Render a search batch to the local cache."""
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, batch_id: int = None) -> TestSearchBatch:
        """Return a search batch object by batch ID."""
        batch = None
        if batch_id:
            batch = db.session.query(TestSearchBatch).\
                        filter(TestSearchBatch.id == batch_id).one_or_none()

        return batch

    @classmethod
    def find_search_batches(
        cls,
        type: SearchRequest.SearchTypes = None,
        after_date: datetime = None,
        before_date: datetime = None
    ) -> List[TestSearchBatch]:
        """Return a list of search batch objects by type and/or date."""
        batch = db.session.query(TestSearchBatch)
        if type:
            batch = batch.filter(TestSearchBatch.search_type == type)
        if after_date:
            batch = batch.filter(TestSearchBatch.test_date >= after_date)
        if before_date:
            batch = batch.filter(TestSearchBatch.test_date <= before_date)

        return batch.all()
