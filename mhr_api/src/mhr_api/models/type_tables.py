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
"""This module holds model definitions for the PPR type tables."""

from __future__ import annotations

from .db import db


class SearchType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the search_type table."""

    __tablename__ = 'search_types'

    search_type = db.Column('search_type', db.String(2), primary_key=True)
    search_type_desc = db.Column('search_type_desc', db.String(60), nullable=False)

    # parent keys

    # Relationships - SearchRequest
    search_request = db.relationship('SearchRequest', back_populates='search_request_type')
