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
"""This module wraps the calls to external payment service used by the API."""

from enum import Enum


class TransactionTypes(str, Enum):
    """Derive payment request filing type from transaction type."""

    SEARCH = 'SEARCH'
    SEARCH_COMBO = 'SEARCH_COMBO'
    SEARCH_STAFF = 'SEARCH_STAFF'
    SEARCH_STAFF_COMBO = 'SEARCH_STAFF_COMBO'
    CERTIFIED = 'CERTIFIED'
    REGISTRATION = 'REGISTRATION'
    TRANSFER = 'TRANSFER'
    EXEMPTION_RES = 'EXEMPTION_RES'
    EXEMPTION_NON_RES = 'EXEMPTION_NON_RES'
    TRANSPORT_PERMIT = 'TRANSPORT_PERMIT'
    TRANSPORT_PERMIT_EXT = 'TRANSPORT_PERMIT_EXT'
    UNIT_NOTE = 'UNIT_NOTE'
