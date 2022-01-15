import base64
import json
from typing import Callable, Optional

from google.cloud import storage

from document_delivery_service.services.logging import logging
from .abstract_storage import AbstractStorageService
from .abstract_storage import StorageServiceError
from .abstract_storage import StorageDocumentTypes


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
            except Exception as err:
                logging.error('GoogleCloudStorage.connect() failed: {}'.format(err))
                raise StorageServiceError('GoogleCloudStorage.connect() failed: {}'.format(err), e=err)

        return self.client

    def get_document(self, bucket: str, name: str, doc_type: str = None) -> Optional[bytes]:
        """Fetch the uniquely named document from cloud storage as binary data."""
        raise StorageServiceError('Not Implemented.')

    def save_document(self, bucket_name: str, filename: str, raw_data, doc_type: str = StorageDocumentTypes.BINARY.value):
        """Save or replace the named document in storage with the binary data as the file contents."""
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
