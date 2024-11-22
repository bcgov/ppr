# Copyright © 2019 Province of British Columbia
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
"""Enum definitions."""
from enum import auto

from ppr_api.utils.base import BaseEnum


class Role(BaseEnum):
    """User Role."""

    SYSTEM = auto()
    STAFF = auto()
    PUBLIC_USER = auto()
    SMS = auto()
    JOB = auto()
    INVALID = auto()
    GC_NOTIFY_CALLBACK = auto()


class MillionverifierResult(BaseEnum):
    """The result of email verification."""

    OK = auto()
    CATCH_ALL = auto()
    UNKNOWN = auto()
    ERROR = auto()
    DISPOSABLE = auto()
    INVALID = auto()
