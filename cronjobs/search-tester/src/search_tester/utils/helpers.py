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
"""Model helper utilities for processing requests.

Common constants used across models and utilities for mapping type codes
between the API and the database in both directions.
"""

TO_API_SEARCH_TYPE = {
    'AC': 'AIRCRAFT_DOT',
    'BS': 'BUSINESS_DEBTOR',
    'IS': 'INDIVIDUAL_DEBTOR',
    'MH': 'MHR_NUMBER',
    'RG': 'REGISTRATION_NUMBER',
    'SS': 'SERIAL_NUMBER'
}
