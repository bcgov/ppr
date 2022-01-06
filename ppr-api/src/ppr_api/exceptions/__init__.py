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
"""Application Specific Exceptions, to manage the business errors.

@log_error - a decorator to automatically log the exception to the logger provided

BusinessException - error, status_code - Business rules error
error - a description of the error {code / description: classname / full text}
status_code - where possible use HTTP Error Codes
"""
import functools
from enum import Enum


class ResourceErrorCodes(str, Enum):
    """Render an Enum of error codes as message prefixes to facilitate identifying the source of the exception."""

    ACCOUNT_REQUIRED_ERR = '001'
    UNAUTHORIZED_ERR = '002'
    VALIDATION_ERR = '003'
    PAY_ERR = '004'
    DATABASE_ERR = '005'
    NOT_FOUND_ERR = '006'
    DUPLICATE_ERR = '007'
    PATH_PARAM_ERR = '008'
    DATA_MISMATCH_ERR = '009'
    HISTORICAL_ERR = '010'
    DEBTOR_NAME_ERR = '011'
    REPORT_ERR = '012'
    DEFAULT_ERR = '013'
    TOO_OLD_ERR = '014'


class BusinessException(Exception):
    """Exception that adds error code and error name, that can be used for i18n support."""

    def __init__(self, error, status_code, *args, **kwargs):
        """Return a valid BusinessException."""
        super(BusinessException, self).__init__(*args, **kwargs)
        self.error = error
        self.status_code = status_code


class DatabaseException(Exception):
    """Database insert/update exception."""
