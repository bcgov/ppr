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

# pylint: disable=too-few-public-methods

"""This module holds methods to support registration model updates - mostly account registration summary."""
from flask import current_app
from sqlalchemy.sql import text

from mhr_api.exceptions import DatabaseException
from mhr_api.models import utils as model_utils
from mhr_api.models.db import db


# Account registration request parameters to support sorting and filtering.
CLIENT_REF_PARAM = 'clientReferenceId'
PAGE_NUM_PARAM = 'pageNumber'
SORT_DIRECTION_PARAM = 'sortDirection'
SORT_CRITERIA_PARAM = 'sortCriteriaName'
MHR_NUMBER_PARAM = 'mhrNumber'
DOC_REG_NUMBER_PARAM = 'documentRegistrationNumber'
REG_TYPE_PARAM = 'registrationType'
REG_TS_PARAM = 'createDateTime'
START_TS_PARAM = 'startDateTime'
END_TS_PARAM = 'endDateTime'
STATUS_PARAM = 'statusType'
SUBMITTING_NAME_PARAM = 'submittingName'
OWNER_NAME_PARAM = 'ownerName'
USER_NAME_PARAM = 'username'
EXPIRY_DAYS_PARAM = 'expiryDays'
SORT_ASCENDING = 'ascending'
SORT_DESCENDING = 'descending'

QUERY_PPR_LIEN_COUNT = """
SELECT COUNT(base_registration_num)
  FROM mhr_lien_check_vw
 WHERE mhr_number = :query_value
"""


class AccountRegistrationParams():
    """Contains parameter values to use when sorting and filtering account summary registration information."""

    account_id: str
    collapse: bool = False
    sbc_staff: bool = False
    from_ui: bool = False
    sort_direction: str = SORT_DESCENDING
    page_number: int = 1
    sort_criteria: str = None
    filter_mhr_number: str = None
    filter_registration_type: str = None
    filter_registration_date: str = None
    # start_date_time: str = None
    # end_date_time: str = None
    filter_status_type: str = None
    filter_client_reference_id: str = None
    filter_submitting_name: str = None
    filter_username: str = None

    def __init__(self, account_id, collapse: bool = False, sbc_staff: bool = False):
        """Set common base initialization."""
        self.account_id = account_id
        self.collapse = collapse
        self.sbc_staff = sbc_staff

    def has_sort(self) -> bool:
        """Check if sort criteria provided."""
        if self.sort_criteria:
            if self.sort_criteria == MHR_NUMBER_PARAM or self.sort_criteria == REG_TYPE_PARAM or \
                    self.sort_criteria == REG_TS_PARAM or self.sort_criteria == CLIENT_REF_PARAM:
                return True
            if self.sort_criteria == SUBMITTING_NAME_PARAM or self.sort_criteria == OWNER_NAME_PARAM or \
                    self.sort_criteria == USER_NAME_PARAM or self.sort_criteria == STATUS_PARAM or \
                    self.sort_criteria == EXPIRY_DAYS_PARAM:
                return True
        return False

    def has_filter(self) -> bool:
        """Check if filter criteria provided."""
        return self.filter_client_reference_id or self.filter_mhr_number or self.filter_registration_type or \
            self.filter_registration_date or self.filter_status_type or self.filter_submitting_name or \
            self.filter_username

    def get_filter_values(self):  # pylint: disable=too-many-return-statements
        """Provide optional filter name and value if available."""
        if self.filter_mhr_number:
            return MHR_NUMBER_PARAM, self.filter_mhr_number
        if self.filter_registration_type:
            return REG_TYPE_PARAM, self.filter_registration_type
        if self.filter_registration_date:
            return REG_TS_PARAM, self.filter_registration_date
        if self.filter_status_type:
            return STATUS_PARAM, self.filter_status_type
        if self.filter_client_reference_id:
            return CLIENT_REF_PARAM, self.filter_client_reference_id
        if self.filter_submitting_name:
            return SUBMITTING_NAME_PARAM, self.filter_submitting_name
        if self.filter_username:
            return USER_NAME_PARAM, self.filter_username
        return None, None

    def get_page_size(self) -> int:
        """Provide account registrations query page size."""
        if self.has_filter():
            return model_utils.MAX_ACCOUNT_REGISTRATIONS_DEFAULT
        return model_utils.get_max_registrations_size()

    def get_page_offset(self) -> int:
        """Provide account registrations query page offset."""
        page_offset: int = self.page_number
        if page_offset <= 1:
            return 0
        return (page_offset - 1) * self.get_page_size()


def get_ppr_lien_count(mhr_number: str) -> int:
    """Execute a query to count existing PPR liens on the MH (must not exist check)."""
    try:
        query = text(QUERY_PPR_LIEN_COUNT)
        result = db.session.execute(query, {'query_value': mhr_number})
        row = result.first()
        lien_count = int(row[0])
        return lien_count
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('get_ppr_lien_count exception: ' + str(db_exception))
        raise DatabaseException(db_exception)
