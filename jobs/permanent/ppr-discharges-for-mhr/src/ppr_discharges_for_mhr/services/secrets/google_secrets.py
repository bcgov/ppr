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
"""This module containes the signature of the StorageService."""
from typing import Optional, Union

from .abstract_secrets import AbstractSecretService, SecretServiceError

import google_crc32c
from google.cloud import secretmanager

class GoogleSecretService(AbstractSecretService):
    """Storage Service abstract class for all implementations."""

    def __init__(self):
        """Create a secret manager client."""
        self.connection = None
        self.project_id = None

    def connect(self, **kwargs):
        """Connect to the secret service."""
        self.project_id = kwargs.get('project_id')
        self.connection = secretmanager.SecretManagerServiceClient()
    
    def _get_connection(self):
        """Helper function to get current connection client."""
        if not self.connection:
            self.connection = secretmanager.SecretManagerServiceClient()
        return self.connection


    def create_secret(self, secret_id: str, project_id: Optional[str] = None) -> str:
        """Create a new secret with the given secret_id.
        
        A secret is a logical wrappercaround a collection of secret versions.
        Secret versions hold the actual secret material.
        """
        if not(_project_id := project_id or self.project_id):
            raise SecretServiceError('No project_id provided or available.')

        conn = self._get_connection()

        # Build the resource name of the parent project.
        parent = f'projects/{_project_id}'

        # Create the secret.
        response = conn.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": {"replication": {"automatic": {}}},
            }
        )
        return response.name
 
    def add_secret_version(self, secret_id: str, payload: str, project_id: Optional[str] = None) -> str:
        """Add a value as the latest version of a secret."""

        if not(_project_id := project_id or self.project_id):
            raise SecretServiceError('No project_id provided or available.')

        conn = self._get_connection()

        # Build the resource name of the parent secret.
        parent = conn.secret_path(_project_id, secret_id)

        # Convert the string payload into a bytes. This step can be omitted if you
        # pass in bytes instead of a str for the payload argument.
        payload = payload.encode("UTF-8")

        # Calculate payload checksum. Passing a checksum in add-version request
        # is optional.
        crc32c = google_crc32c.Checksum()
        crc32c.update(payload)

        # Add the secret version.
        response = conn.add_secret_version(
            request={
                "parent": parent,
                "payload": {"data": payload, "data_crc32c": int(crc32c.hexdigest(), 16)},
            }
        )
        return response.name

    def get_secret_version(self, secret_id: str, version_id: str = "latest", project_id: Optional[str] = None) -> str:
        """Get a secret container """

        if not(_project_id := project_id or self.project_id):
            raise SecretServiceError('No project_id provided or available.')

        conn = self._get_connection()
        
        # Build the resource name of the secret version.
        name = f"projects/{_project_id}/secrets/{secret_id}/versions/{version_id}"

        # Access the secret version.
        response = conn.access_secret_version(request={"name": name})

        # Verify payload checksum.
        crc32c = google_crc32c.Checksum()
        crc32c.update(response.payload.data)
        if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
            raise SecretServiceError("Data corruption detected.")
        
        # unpack to the secret value.
        return response.payload.data.decode('UTF-8')

    def delete_secret(self, secret_id, project_id: Optional[str] = None):
        """Delete a secret container."""

        if not(_project_id := project_id or self.project_id):
            raise SecretServiceError('No project_id provided or available.')

        conn = self._get_connection()

        # Build the resource name of the secret.
        name = conn.secret_path(_project_id, secret_id)

        # Delete the secret.
        conn.delete_secret(request={"name": name})
