# Copyright © 2022 Province of British Columbia
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
"""This module containes the signature of the SecretService."""
from abc import ABC, abstractmethod
from typing import Optional, Union

from ...common.enum import BaseEnum, auto


class SecretServiceError(Exception):
    """Secret Service Exception."""

    def __init__(self, message: str, e: Exception = None):
        """Initialize Secret Service Exception."""
        super().__init__(message)
        self.e = e


class AbstractSecretService(ABC):
    """Storage Service abstract class for all implementations."""

    @abstractmethod
    def connect(self, **kwargs):
        """Connect to the storage service."""
        raise SecretServiceError('Not Implemented.')

    @abstractmethod
    def create_secret(self, secret_id: str, project_id: Optional[str] = None) -> str:
        """Create a secret container."""
 
    @abstractmethod
    def add_secret_version(self, secret_id: str, payload: str, project_id: Optional[str] = None) -> str:
        """Add a value as the latest version of a secret."""

    @abstractmethod
    def get_secret_version(self, secret_id: str, version_id: str = "latest", project_id: Optional[str] = None):
        """Get a secret container and return the value stored inside.
        
        All secret stores use a slightly different schema, so we'll return the value stored in the
        secret, rather than the secret container.
        We may decide to return a container class of our making in the future.
        """

    @abstractmethod
    def delete_secret(self, secret_id: str, project_id: Optional[str] = None):
        """Delete a secret container."""
