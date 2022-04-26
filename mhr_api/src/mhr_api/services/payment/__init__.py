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


class TransactionTypes(Enum):
    """Derive payment request filing type from transaction type."""

    AMENDMENT = 'AMENDMENT'
    AMENDMENT_NO_FEE = 'AMENDMENT_NO_FEE'
    CHANGE = 'CHANGE'
    CHANGE_STAFF_PROCESS_FEE = 'CHANGE_STAFF_PROCESS_FEE'
    DISCHARGE = 'DISCHARGE'
    FINANCING_FR = 'FINANCING_FR'  # Special flat rate fee for FR registration type.
    FINANCING_INFINITE = 'FINANCING_INFINITE'
    FINANCING_LIFE_YEAR = 'FINANCING_LIFE_YEAR'
    FINANCING_NO_FEE = 'FINANCING_NO_FEE'  # No Charge fee for LT, MH, MISCLIEN class, CROWNLIEN class.
    FINANCING_STAFF_PROCESS_FEE = 'FINANCING_STAFF_PROCESS_FEE'
    RENEWAL_INFINITE = 'RENEWAL_INFINITE'
    RENEWAL_LIFE_YEAR = 'RENEWAL_LIFE_YEAR'
    SEARCH = 'SEARCH'
    SEARCH_STAFF = 'SEARCH_STAFF'
    SEARCH_STAFF_NO_FEE = 'SEARCH_STAFF_NO_FEE'
    SEARCH_STAFF_CERTIFIED = 'SEARCH_STAFF_CERTIFIED'
    SEARCH_STAFF_CERTIFIED_NO_FEE = 'SEARCH_STAFF_CERTIFIED_NO_FEE'
