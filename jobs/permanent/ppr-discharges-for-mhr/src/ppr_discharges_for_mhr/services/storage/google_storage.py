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
"""This is the concrete implementation of the StorageService, using Google Cloud Storage."""
import base64
import datetime
import json
from typing import Callable, Optional, Union

from google.cloud import storage

from ..logging import logging

from .abstract_storage import AbstractStorageService  # noqa: I001
from .abstract_storage import StorageDocumentTypes  # noqa: I001
from .abstract_storage import StorageServiceError  # noqa: I001


class GoogleCloudStorage(AbstractStorageService):
    """Google Cloud Storage implmentation.

    Maintain document storage with Google Cloud Storage API calls.
    """

    def __init__(self, config: dict):
        """Initialize Google Cloud Storage."""
        super().__init__()
        self.config = config
        self.client = None

    def connect(self) -> Callable:
        """Connect to the storage service."""
        if self.client is None:
            try:
                # If service account credentials are specified in the environment,
                if self.config and hasattr(self.config, 'GOOGLE_STORAGE_SERVICE_ACCOUNT'):
                    auth_json = json.loads(base64.b64decode(self.config.GOOGLE_STORAGE_SERVICE_ACCOUNT).decode('utf-8'))
                    self.client = storage.Client.from_service_account_info(auth_json)

                # if not, try to use the default credentials attached to the environment
                else:
                    self.client = storage.Client()
            except Exception as err:  # noqa: B902
                logging.error('GoogleCloudStorage.connect() failed: {}'.format(err))
                raise StorageServiceError('GoogleCloudStorage.connect() failed: {}'.format(err), e=err)

        return self.client

    def get_document(self, bucket_name: str, filename: str, doc_type: str = None) -> Optional[bytes]:
        """Fetch the uniquely named document from cloud storage as binary data."""
        raise StorageServiceError('Not Implemented.')

    def save_document(self,
                      bucket_name: str,
                      filename: str,
                      raw_data: Union[bytes, str],
                      doc_type: str = StorageDocumentTypes.BINARY.value) -> None:
        """Save or replace the named document in storage with the binary data as the file contents."""
        try:
            gcs = self.connect()
            bucket = gcs.bucket(bucket_name)
            blob = bucket.blob(filename)
            if doc_type == StorageDocumentTypes.BINARY:
                gcs_file = blob.open(mode='wb')
            elif doc_type == StorageDocumentTypes.TEXT:
                gcs_file = blob.open(mode='w')
            else:
                raise StorageServiceError('Unsupported document type: {}'.format(doc_type))

            gcs_file.write(raw_data)
            gcs_file.close()
        except Exception as err:  # noqa: B902
            logging.error('GoogleCloudStorage.save_document() failed: {}'.format(err))
            raise StorageServiceError('GoogleCloudStorage.save_document() failed: {}'.format(err), e=err)

    def generate_download_signed_url(self,
                                     bucket_name: str,
                                     blob_name: str,
                                     available_days: int = 1,
                                     available_hours: int = 0,
                                     available_minutes: int = 0
                                     ):
        """Generates a v4 signed URL for downloading a blob.

        Note that this method requires a service account key file. You can not use
        this if you are using Application Default Credentials from Google Compute
        Engine or from the Google Cloud SDK.
        """
        gcs = self.connect()
        bucket = gcs.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(days=available_days, hours=available_hours, minutes=available_minutes),
            method="GET",
        )
        return url
