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
"""This module containes the signature of the StorageService."""
from abc import ABC, abstractmethod
from typing import Optional, Union

from ...common.enum import BaseEnum, auto


class StorageServiceError(Exception):
    """Storage Service Exception."""

    def __init__(self, message: str, e: Exception = None):
        """Initialize Storage Service Exception."""
        super().__init__(message)
        self.e = e


class StorageDocumentTypes(BaseEnum):
    """Document Types."""

    BINARY = auto()
    TEXT = auto()


class AbstractStorageService(ABC):
    """Storage Service abstract class for all implementations."""

    @abstractmethod
    def connect(self):
        """Connect to the storage service."""
        raise StorageServiceError('Not Implemented.')

    @abstractmethod
    def get_document(self, bucket_name: str, filename: str, doc_type: str = None) -> Optional[bytes]:
        """Fetch the uniquely named document from storage as binary data."""

    @abstractmethod
    def save_document(self,
                      bucket_name: str,
                      filename: str,
                      raw_data: Union[str, bytes],
                      doc_type: str = StorageDocumentTypes.BINARY.value) -> None:
        """Save or replace the named document in storage with the binary data as the file contents."""

    @abstractmethod
    def generate_download_signed_url(self,
                                     bucket_name: str,
                                     blob_name: str,
                                     available_days: int = 1,
                                     available_hours: int = 0,
                                     available_minutes: int = 0
                                     ):
        """Generates a signed URL for downloading a blob."""