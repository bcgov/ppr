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
import datetime

from google.cloud import storage

from secured_party_notification.config import Config
from secured_party_notification.services.gcp_auth.auth_service import GoogleAuthService
from secured_party_notification.services.utils.exceptions import StorageException
from secured_party_notification.utils.logging import logger

HTTP_GET = "get"
HTTP_POST = "post"
CONTENT_TYPE_PDF = "application/pdf"


class GoogleStorageService:  # pylint: disable=too-few-public-methods
    """Google Cloud Storage implmentation.

    Maintain document storage with Google Cloud Storage API calls.
    """

    # Google cloud storage configuration.
    GCP_BUCKET_ID_MAIL = None
    GCP_CREDENTIALS = None
    GCP_STORAGE_CLIENT = None
    GCP_BUCKET = None

    @staticmethod
    def init_app(config: Config):
        """Set up the service"""
        bucket_id = config.GCP_CS_BUCKET_ID_MAIL
        credentials = GoogleAuthService.get_credentials()
        storage_client = storage.Client(credentials=credentials)
        GoogleStorageService.GCP_BUCKET = storage_client.bucket(bucket_id)
        GoogleStorageService.GCP_BUCKET_ID_MAIL = bucket_id
        GoogleStorageService.GCP_CREDENTIALS = credentials
        GoogleStorageService.GCP_STORAGE_CLIENT = storage_client

    @classmethod
    def get_document(cls, name: str):
        """Fetch the uniquely named document from cloud storage as binary data."""
        try:
            logger.debug(f"Fetching document name={name}.")
            return cls.__call_cs_api(HTTP_GET, name, None)
        except StorageException as storage_err:
            raise storage_err
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            logger.error(f"get_document failed for doc name={name}: {err}.")
            raise StorageException(f"GET document failed for doc name={name}.") from err

    @classmethod
    def get_document_link(cls, name: str, available_days: int = 1):
        """Fetch the uniquely named document from cloud storage as a time-limited download link."""
        try:
            logger.debug(f"Fetching document name={name}.")
            return cls.__call_cs_api_link(name, None, available_days)
        except StorageException as storage_err:
            raise storage_err
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            logger.error(f"get_document_link failed for doc name={name}: {err}.")
            raise StorageException(f"GET document failed for doc name={name}.") from err

    @classmethod
    def save_document(cls, name: str, raw_data, content_type: str):
        """Save or replace the named document in cloud storage with the binary data as the file contents."""
        try:
            logger.info(f"Saving document name={name}.")
            return cls.__call_cs_api(HTTP_POST, name, raw_data, content_type)
        except StorageException as storage_err:
            raise storage_err
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            logger.error(f"save_document failed for doc name={name}: {err}")
            raise StorageException(f"POST document failed for doc name={name}.") from err

    @classmethod
    def save_document_link(cls, name: str, raw_data, available_days: int = 1, content_type: str = None):
        """Save a document to a cloud storage bucket with the binary data as the file contents. Return a link."""
        try:
            logger.info(f"Saving document name={name}.")
            return cls.__call_cs_api_link(name, raw_data, available_days, content_type)
        except StorageException as storage_err:
            raise storage_err
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            logger.error(f"save_document_link failed for doc name={name}: {err}")
            raise StorageException(f"POST document failed for doc name={name}.") from err

    @classmethod
    def __call_cs_api(cls, method: str, name: str, data=None, content_type: str = CONTENT_TYPE_PDF):
        """Call the Cloud Storage API."""
        blob = GoogleStorageService.GCP_BUCKET.blob(name)
        if method == HTTP_POST:
            blob.upload_from_string(data=data, content_type=content_type)
            return blob.time_created
        if method == HTTP_GET:
            contents = blob.download_as_bytes()
            return contents
        return None

    @classmethod
    def __call_cs_api_link(cls, name: str, data=None, available_days: int = 1, content_type: str = CONTENT_TYPE_PDF):
        """Call the Cloud Storage API, returning a time-limited download link."""
        blob = GoogleStorageService.GCP_BUCKET.blob(name)
        if data:
            blob.upload_from_string(data=data, content_type=content_type)
        url = blob.generate_signed_url(
            version="v4", expiration=datetime.timedelta(days=available_days, hours=0, minutes=0), method="GET"
        )
        return url
