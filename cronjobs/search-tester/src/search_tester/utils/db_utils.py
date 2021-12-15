# Copyright © 2021 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Db helper."""

QUERY_LEGACY_RESULTS_MOST_RECENT = """
SELECT date, time, criteria, search_type, match_type, result, document_id, id
FROM ssa_search_records
WHERE date = (SELECT MAX(date) FROM ssa_search_records)
"""

QUERY_LEGACY_RESULTS_DATE = """
SELECT date, time, criteria, search_type, match_type, result, document_id, id
FROM ssa_search_records
WHERE date = :date
"""

QUERY_LEGACY_RESULTS_DATE_TIME = """
SELECT date, time, criteria, search_type, match_type, result, document_id, id
FROM ssa_search_records
WHERE date = :date AND time = :time
"""
