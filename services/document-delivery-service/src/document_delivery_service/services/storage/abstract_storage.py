from abc import ABC, abstractmethod
from typing import Optional

from document_delivery_service.common.enum import BaseEnum, auto


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

    def __init__(self) -> None:
        super().__init__()
    
    @abstractmethod
    def connect(self):
        """Connect to the storage service."""
        raise StorageServiceError('Not Implemented.')

    @abstractmethod
    def get_document(self, bucket_name: str, filename: str, doc_type: str = None) -> Optional[bytes]:
        """Fetch the uniquely named document from storage as binary data."""

    @abstractmethod
    def save_document(self, bucket_name: str, filename: str, raw_data, doc_type: str = StorageDocumentTypes.BINARY.value):
        """Save or replace the named document in storage with the binary data as the file contents."""