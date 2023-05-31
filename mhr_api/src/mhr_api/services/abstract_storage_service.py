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
"""This class is a wrapper for document storage API calls."""
from abc import ABC, abstractmethod

from mhr_api.utils.base import BaseEnum


class DocumentTypes(BaseEnum):
    """Render an Enum of storage document types."""

    SEARCH_RESULTS = 'SEARCH_RESULTS'
    REGISTRATION = 'REGISTRATION'
    BATCH_REGISTRATION = 'BATCH_REGISTRATION'


class StorageService(ABC):  # pylint: disable=too-few-public-methods
    """Storage Service abstract class for all implementations."""

    @classmethod
    @abstractmethod
    def get_document(cls, name: str, doc_type: str = None):
        """Fetch the uniquely named document from storage as binary data."""

    @classmethod
    @abstractmethod
    def save_document(cls, name: str, raw_data, doc_type: str = None):
        """Save or replace the named document in storage with the binary data as the file contents."""
