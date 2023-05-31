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
import os
import json
import urllib.parse

import requests
from flask import current_app
from google.cloud import storage

from mhr_api.services.gcp_auth.auth_service import GoogleAuthService
from mhr_api.services.utils.exceptions import StorageException
from mhr_api.services.abstract_storage_service import DocumentTypes, StorageService


HTTP_DELETE = 'delete'
HTTP_GET = 'get'
HTTP_POST = 'post'


class GoogleStorageService(StorageService):  # pylint: disable=too-few-public-methods
    """Google Cloud Storage implmentation.

    Maintain document storage with Google Cloud Storage API calls.
    """

    # Google cloud storage configuration.
    GCP_BUCKET_ID = str(os.getenv('GCP_CS_BUCKET_ID'))
    GCP_BUCKET_ID_REGISTRATION = str(os.getenv('GCP_CS_BUCKET_ID_REGISTRATION'))
    GCP_BUCKET_ID_BATCH = str(os.getenv('GCP_CS_BUCKET_ID_BATCH'))
    GCP_URL = str(os.getenv('GCP_CS_URL', 'https://storage.googleapis.com'))
    DOC_URL = GCP_URL + '/storage/v1/b/{bucket_id}/o/{name}'
    GET_DOC_URL = DOC_URL + '?alt=media'
    DELETE_DOC_URL = GCP_URL + '/storage/v1/b/{bucket_id}/o/{name}'
    UPLOAD_DOC_URL = GCP_URL + '/upload/storage/v1/b/{bucket_id}/o?uploadType=media&name={name}'

    @classmethod
    def get_document_http(cls, name: str, doc_type: str = None):
        """Fetch the uniquely named document from cloud storage as binary data."""
        try:
            bucket_id = cls.__get_bucket_id(doc_type)
            url = cls.GET_DOC_URL.format(bucket_id=bucket_id, name=urllib.parse.quote(name, safe=''))
            token = GoogleAuthService.get_token()
            current_app.logger.info('Fetching doc with GET ' + url)
            return cls.__call_api(HTTP_GET, url, token)
        except StorageException as storage_err:
            raise storage_err
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            current_app.logger.error(f'get_document failed for url={url}.')
            current_app.logger.error(str(err))
            raise StorageException(f'GET document failed for url={url}.')

    @classmethod
    def get_document(cls, name: str, doc_type: str = None):
        """Fetch the uniquely named document from cloud storage as binary data."""
        try:
            current_app.logger.info(f'Fetching doc type={doc_type}, name={name}.')
            return cls.__call_cs_api(HTTP_GET, name, None, doc_type)
        except StorageException as storage_err:
            raise storage_err
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            current_app.logger.error(f'get_document failed for doc type={doc_type}, name={name}.')
            current_app.logger.error(str(err))
            raise StorageException('GET document failed for doc type={doc_type}, name={name}.')

    @classmethod
    def delete_document_http(cls, name: str, doc_type: str = None):
        """Delete the uniquely named document from cloud storage (unit testing only)."""
        try:
            bucket_id = cls.__get_bucket_id(doc_type)
            url = cls.DOC_URL.format(bucket_id=bucket_id, name=urllib.parse.quote(name, safe=''))
            token = GoogleAuthService.get_token()
            current_app.logger.info(f'Deleting doc with DELETE {url}.')
            return cls.__call_api(HTTP_DELETE, url, token)
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            current_app.logger.error(f'get_document failed for url={url}.')
            current_app.logger.error(str(err))

    @classmethod
    def delete_document(cls, name: str, doc_type: str = None):
        """Delete the uniquely named document from cloud storage (unit testing only)."""
        try:
            current_app.logger.info(f'Deleting doc type={doc_type}, name={name}.')
            return cls.__call_cs_api(HTTP_DELETE, name, None, doc_type)
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            current_app.logger.error(f'get_document failed for doc type {doc_type}, name {name}.')
            current_app.logger.error(str(err))

    @classmethod
    def save_document_http(cls, name: str, raw_data, doc_type: str = None):
        """Save or replace the named document in cloud storage with the binary data as the file contents."""
        try:
            bucket_id = cls.__get_bucket_id(doc_type)
            url = cls.UPLOAD_DOC_URL.format(bucket_id=bucket_id, name=urllib.parse.quote(name, safe=''))
            token = GoogleAuthService.get_token()
            current_app.logger.info('Saving doc with POST ' + url)
            return cls.__call_api(HTTP_POST, url, token, raw_data)
        except StorageException as storage_err:
            raise storage_err
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            current_app.logger.error('save_document failed for url=' + url)
            current_app.logger.error(repr(err))
            raise StorageException('POST document failed for url=' + url)

    @classmethod
    def save_document(cls, name: str, raw_data, doc_type: str = None):
        """Save or replace the named document in cloud storage with the binary data as the file contents."""
        try:
            # bucket_id = cls.__get_bucket_id(doc_type)
            # url = cls.UPLOAD_DOC_URL.format(bucket_id=bucket_id, name=urllib.parse.quote(name, safe=""))
            current_app.logger.info(f'Saving doc type={doc_type}, name={name}.')
            return cls.__call_cs_api(HTTP_POST, name, raw_data, doc_type)
        except StorageException as storage_err:
            raise storage_err
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            current_app.logger.error(f'save_document failed for doc type={doc_type}, name={name}.')
            current_app.logger.error(str(err))
            raise StorageException('POST document failed for doc type={doc_type}, name={name}.')

    @classmethod
    def __get_bucket_id(cls, doc_type: str = None):
        """Map the document type to a bucket ID. The default is GCP_BUCKET_ID."""
        if not doc_type or doc_type == DocumentTypes.SEARCH_RESULTS:
            return cls.GCP_BUCKET_ID
        if doc_type == DocumentTypes.REGISTRATION:
            return cls.GCP_BUCKET_ID_REGISTRATION
        if doc_type == DocumentTypes.BATCH_REGISTRATION:
            return cls.GCP_BUCKET_ID_BATCH
        return cls.GCP_BUCKET_ID

    @classmethod
    def __call_api(cls, method, url, token, data=None):
        """Call the Cloud Storage API."""
        headers = {
            'Authorization': 'Bearer ' + token
        }
        if data:
            response = requests.request(
                method,
                url,
                params=None,
                data=data,
                headers=headers
            )
        else:
            response = requests.request(
                method,
                url,
                params=None,
                headers=headers
            )

        if not response.ok:
            current_app.logger.error(f'{method} {url}  failed: ' + str(response.status_code))
            raise StorageException(str(response.status_code) + ': ' + method + ' ' + url + ' failed. ' + response.text)

        current_app.logger.info(f'{method} {url} successful.')
        if method == HTTP_GET:
            return response.content
        if method != HTTP_DELETE:
            return json.loads(response.text)
        return {}

    @classmethod
    def __call_cs_api(cls, method: str, name: str, data=None, doc_type: str = None):
        """Call the Cloud Storage API."""
        credentials = GoogleAuthService.get_credentials()
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(cls.__get_bucket_id(doc_type))
        blob = bucket.blob(name)
        if method == HTTP_POST:
            blob.upload_from_string(data=data, content_type='application/pdf')
            return blob.time_created
        if method == HTTP_GET:
            contents = blob.download_as_bytes()
            return contents
        if method == HTTP_DELETE:
            blob.delete()
            return None
        return None
