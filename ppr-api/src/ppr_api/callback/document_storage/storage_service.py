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
from abc import ABC, abstractmethod

import requests
from flask import current_app

from ppr_api.callback.auth.token_service import GoogleStorageTokenService
from ppr_api.callback.utils.exceptions import StorageException


HTTP_GET = 'get'
HTTP_POST = 'post'


class StorageService(ABC):  # pylint: disable=too-few-public-methods
    """Storage Service abstract class for all implementations."""

    @classmethod
    @abstractmethod
    def get_document(cls, name: str):
        """Fetch the uniquely named document from storage as binary data."""

    @classmethod
    @abstractmethod
    def save_document(cls, name: str, raw_data):
        """Save or replace the named document in storage with the binary data as the file contents."""


class GoogleStorageService(StorageService):  # pylint: disable=too-few-public-methods
    """Google Cloud Storage implmentation.

    Maintain document storage with Google Cloud Storage API calls.
    """

    # Google cloud storage configuration.
    GCP_BUCKET_ID = str(os.getenv('GCP_CS_BUCKET_ID'))
    GCP_URL = str(os.getenv('GCP_CS_URL', 'https://storage.googleapis.com'))
    GET_DOC_URL = GCP_URL + '/storage/v1/b/' + GCP_BUCKET_ID + '/o/{name}?alt=media'
    UPLOAD_DOC_URL = GCP_URL + '/upload/storage/v1/b/' + GCP_BUCKET_ID + '/o?uploadType=media&name='

    @classmethod
    def get_document(cls, name: str):
        """Fetch the uniquely named document from cloud storage as binary data."""
        try:
            url = cls.GET_DOC_URL.format(name=name)
            token = GoogleStorageTokenService.get_token()
            current_app.logger.info('Fetching doc with GET ' + url)
            return cls.__call_api(HTTP_GET, url, token)
        except StorageException as storage_err:
            raise storage_err
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            current_app.logger.error('get_document failed for url=' + url)
            current_app.logger.error(repr(err))
            raise StorageException('GET document failed for url=' + url)

    @classmethod
    def save_document(cls, name: str, raw_data):
        """Save or replace the named document in cloud storage with the binary data as the file contents."""
        try:
            url = cls.UPLOAD_DOC_URL + name
            token = GoogleStorageTokenService.get_token()
            current_app.logger.info('Saving doc with POST ' + url)
            return cls.__call_api(HTTP_POST, url, token, raw_data)
        except StorageException as storage_err:
            raise storage_err
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            current_app.logger.error('save_document failed for url=' + url)
            current_app.logger.error(repr(err))
            raise StorageException('POST document failed for url=' + url)

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
            current_app.logger.error(method + ' ' + url + ' failed: ' + str(response.status_code))
            raise StorageException(str(response.status_code) + ': ' + method + ' ' + url + ' failed. ' + response.text)

        current_app.logger.info(method + ' ' + url + ' successful.')
        if method == HTTP_GET:
            return response.content
        return json.loads(response.text)
